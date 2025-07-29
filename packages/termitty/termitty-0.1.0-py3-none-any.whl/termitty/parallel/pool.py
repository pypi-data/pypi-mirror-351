"""
Connection pool for parallel execution.

This module manages a pool of SSH connections for efficient parallel
command execution across multiple hosts.
"""

import threading
import queue
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from contextlib import contextmanager

from ..session.session import TermittySession
from ..core.exceptions import ConnectionException, TermittyException
from ..core.config import config

logger = logging.getLogger(__name__)


@dataclass
class PooledConnection:
    """Represents a pooled connection."""
    session: TermittySession
    host: str
    created_at: float
    last_used: float
    use_count: int = 0
    is_healthy: bool = True
    
    def update_usage(self):
        """Update usage statistics."""
        self.last_used = time.time()
        self.use_count += 1


class ConnectionPool:
    """
    Manages a pool of SSH connections for parallel execution.
    
    This class provides efficient connection reuse, health checking,
    and automatic connection management for parallel operations.
    """
    
    def __init__(self,
                 max_connections: int = 10,
                 connection_timeout: float = 30.0,
                 idle_timeout: float = 300.0,
                 health_check_interval: float = 60.0):
        """
        Initialize the connection pool.
        
        Args:
            max_connections: Maximum number of concurrent connections
            connection_timeout: Timeout for establishing connections
            idle_timeout: Time before idle connections are closed
            health_check_interval: Interval between health checks
        """
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval
        
        # Connection storage
        self._connections: Dict[str, queue.Queue] = {}  # host -> queue of connections
        self._all_connections: List[PooledConnection] = []
        self._lock = threading.Lock()
        
        # Statistics
        self._stats = {
            'connections_created': 0,
            'connections_reused': 0,
            'connections_failed': 0,
            'health_checks_passed': 0,
            'health_checks_failed': 0,
        }
        
        # Health check thread
        self._stop_event = threading.Event()
        self._health_check_thread = None
    
    def start(self):
        """Start the connection pool (begins health checking)."""
        if not self._health_check_thread:
            self._health_check_thread = threading.Thread(
                target=self._health_check_loop,
                daemon=True,
                name="ConnectionPool-HealthCheck"
            )
            self._health_check_thread.start()
            logger.info("Connection pool started")
    
    def stop(self, timeout: float = 10.0):
        """Stop the connection pool and close all connections."""
        logger.info("Stopping connection pool")
        self._stop_event.set()
        
        if self._health_check_thread:
            self._health_check_thread.join(timeout)
        
        # Close all connections
        with self._lock:
            for conn in self._all_connections:
                try:
                    conn.session.disconnect()
                except Exception as e:
                    logger.error(f"Error closing connection to {conn.host}: {e}")
            
            self._connections.clear()
            self._all_connections.clear()
    
    @contextmanager
    def get_connection(self, 
                      host: str,
                      username: str,
                      password: Optional[str] = None,
                      key_file: Optional[str] = None,
                      port: int = 22,
                      **kwargs):
        """
        Get a connection from the pool.
        
        This is a context manager that automatically returns the connection
        to the pool when done.
        
        Args:
            host: Target host
            username: SSH username
            password: SSH password
            key_file: SSH key file path
            port: SSH port
            **kwargs: Additional connection arguments
        
        Yields:
            TermittySession: Connected session
        
        Example:
            with pool.get_connection(host, username, password) as session:
                result = session.execute("ls -la")
        """
        connection = None
        try:
            connection = self._acquire_connection(
                host, username, password, key_file, port, **kwargs
            )
            yield connection.session
        finally:
            if connection:
                self._release_connection(connection)
    
    def _acquire_connection(self,
                           host: str,
                           username: str,
                           password: Optional[str] = None,
                           key_file: Optional[str] = None,
                           port: int = 22,
                           **kwargs) -> PooledConnection:
        """Acquire a connection from the pool or create a new one."""
        with self._lock:
            # Check if we have a connection queue for this host
            if host not in self._connections:
                self._connections[host] = queue.Queue()
            
            conn_queue = self._connections[host]
        
        # Try to get an existing connection
        try:
            while not conn_queue.empty():
                conn = conn_queue.get_nowait()
                
                # Check if connection is still valid
                if self._is_connection_valid(conn):
                    conn.update_usage()
                    self._stats['connections_reused'] += 1
                    logger.debug(f"Reusing connection to {host}")
                    return conn
                else:
                    # Remove invalid connection
                    with self._lock:
                        self._all_connections.remove(conn)
                    try:
                        conn.session.disconnect()
                    except:
                        pass
        except queue.Empty:
            pass
        
        # Need to create a new connection
        with self._lock:
            if len(self._all_connections) >= self.max_connections:
                # Try to close an idle connection
                self._close_idle_connection()
                
                if len(self._all_connections) >= self.max_connections:
                    raise TermittyException(
                        f"Connection pool limit reached ({self.max_connections})"
                    )
        
        # Create new connection
        return self._create_connection(host, username, password, key_file, port, **kwargs)
    
    def _create_connection(self,
                          host: str,
                          username: str,
                          password: Optional[str] = None,
                          key_file: Optional[str] = None,
                          port: int = 22,
                          **kwargs) -> PooledConnection:
        """Create a new connection."""
        logger.debug(f"Creating new connection to {host}")
        
        try:
            session = TermittySession()
            session.connect(
                host=host,
                username=username,
                password=password,
                key_file=key_file,
                port=port,
                timeout=self.connection_timeout,
                **kwargs
            )
            
            conn = PooledConnection(
                session=session,
                host=host,
                created_at=time.time(),
                last_used=time.time()
            )
            
            with self._lock:
                self._all_connections.append(conn)
                self._stats['connections_created'] += 1
            
            logger.info(f"Created connection to {host}")
            return conn
            
        except Exception as e:
            self._stats['connections_failed'] += 1
            logger.error(f"Failed to create connection to {host}: {e}")
            raise
    
    def _release_connection(self, connection: PooledConnection):
        """Return a connection to the pool."""
        if not self._is_connection_valid(connection):
            # Don't return invalid connections
            with self._lock:
                if connection in self._all_connections:
                    self._all_connections.remove(connection)
            try:
                connection.session.disconnect()
            except:
                pass
            return
        
        # Return to pool
        with self._lock:
            if connection.host in self._connections:
                self._connections[connection.host].put(connection)
                logger.debug(f"Returned connection to pool for {connection.host}")
    
    def _is_connection_valid(self, connection: PooledConnection) -> bool:
        """Check if a connection is still valid."""
        # Check if connection is too old
        age = time.time() - connection.created_at
        if age > self.idle_timeout:
            logger.debug(f"Connection to {connection.host} exceeded idle timeout")
            return False
        
        # Check if connection is healthy
        if not connection.is_healthy:
            return False
        
        # Check if session is still connected
        if not connection.session.connected:
            return False
        
        return True
    
    def _health_check_loop(self):
        """Background thread for health checking connections."""
        logger.debug("Health check thread started")
        
        while not self._stop_event.is_set():
            try:
                self._perform_health_checks()
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            
            # Wait for next check
            self._stop_event.wait(self.health_check_interval)
        
        logger.debug("Health check thread stopped")
    
    def _perform_health_checks(self):
        """Perform health checks on all connections."""
        with self._lock:
            connections_to_check = list(self._all_connections)
        
        for conn in connections_to_check:
            try:
                # Simple health check - execute echo command
                result = conn.session.execute("echo 'health_check'", timeout=5.0)
                if result.success:
                    conn.is_healthy = True
                    self._stats['health_checks_passed'] += 1
                else:
                    conn.is_healthy = False
                    self._stats['health_checks_failed'] += 1
                    logger.warning(f"Health check failed for {conn.host}")
            except Exception as e:
                conn.is_healthy = False
                self._stats['health_checks_failed'] += 1
                logger.warning(f"Health check error for {conn.host}: {e}")
    
    def _close_idle_connection(self):
        """Close the most idle connection."""
        with self._lock:
            if not self._all_connections:
                return
            
            # Find the connection that's been idle longest
            oldest = min(self._all_connections, key=lambda c: c.last_used)
            
            # Remove from pool
            self._all_connections.remove(oldest)
            if oldest.host in self._connections:
                # Remove from queue if present
                try:
                    temp_queue = queue.Queue()
                    while not self._connections[oldest.host].empty():
                        conn = self._connections[oldest.host].get_nowait()
                        if conn != oldest:
                            temp_queue.put(conn)
                    self._connections[oldest.host] = temp_queue
                except:
                    pass
        
        # Close connection
        try:
            oldest.session.disconnect()
            logger.info(f"Closed idle connection to {oldest.host}")
        except Exception as e:
            logger.error(f"Error closing idle connection: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self._lock:
            active_connections = len(self._all_connections)
            hosts_connected = len(set(c.host for c in self._all_connections))
        
        return {
            'active_connections': active_connections,
            'max_connections': self.max_connections,
            'hosts_connected': hosts_connected,
            'connections_created': self._stats['connections_created'],
            'connections_reused': self._stats['connections_reused'],
            'connections_failed': self._stats['connections_failed'],
            'health_checks_passed': self._stats['health_checks_passed'],
            'health_checks_failed': self._stats['health_checks_failed'],
            'reuse_rate': (self._stats['connections_reused'] / 
                          max(1, self._stats['connections_created'] + self._stats['connections_reused']) * 100)
        }
    
    def close_host_connections(self, host: str):
        """Close all connections to a specific host."""
        with self._lock:
            connections = [c for c in self._all_connections if c.host == host]
            
            for conn in connections:
                self._all_connections.remove(conn)
                try:
                    conn.session.disconnect()
                except:
                    pass
            
            if host in self._connections:
                self._connections[host] = queue.Queue()
        
        logger.info(f"Closed {len(connections)} connections to {host}")