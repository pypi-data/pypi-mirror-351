"""
Parallel command executor for Termitty.

This module provides the main interface for executing commands across
multiple hosts in parallel, with support for various execution strategies
and result handling.
"""

import concurrent.futures
import threading
import time
import logging
from typing import List, Dict, Optional, Union, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .pool import ConnectionPool
from .results import ParallelResults, HostResult, ResultStatus, ResultsCollector
from ..core.exceptions import TermittyException
from ..core.config import config

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Strategy for parallel execution."""
    PARALLEL = "parallel"      # Execute on all hosts simultaneously
    ROLLING = "rolling"        # Execute on hosts in batches
    SEQUENTIAL = "sequential"  # Execute on hosts one by one


@dataclass
class ExecutionConfig:
    """Configuration for parallel execution."""
    strategy: ExecutionStrategy = ExecutionStrategy.PARALLEL
    max_workers: int = 10
    batch_size: int = 5  # For rolling strategy
    timeout: float = 300.0  # Command timeout
    connection_timeout: float = 30.0
    fail_fast: bool = False  # Stop on first failure
    retry_failed: int = 0  # Number of retries for failed hosts
    progress_callback: Optional[Callable[[str, HostResult], None]] = None


@dataclass
class HostConfig:
    """Configuration for a single host."""
    host: str
    username: str
    password: Optional[str] = None
    key_file: Optional[str] = None
    port: int = 22
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ParallelExecutor:
    """
    Executes commands on multiple hosts in parallel.
    
    This class provides high-level methods for parallel command execution
    with support for different strategies, connection pooling, and
    comprehensive result handling.
    
    Example:
        executor = ParallelExecutor()
        
        hosts = [
            HostConfig("server1.example.com", "admin", password="pass"),
            HostConfig("server2.example.com", "admin", key_file="~/.ssh/id_rsa"),
        ]
        
        results = executor.execute("uptime", hosts)
        print(results.summary())
    """
    
    def __init__(self, 
                 config: Optional[ExecutionConfig] = None,
                 connection_pool: Optional[ConnectionPool] = None):
        """
        Initialize the parallel executor.
        
        Args:
            config: Execution configuration
            connection_pool: Connection pool to use (creates one if None)
        """
        self.config = config or ExecutionConfig()
        self.pool = connection_pool or ConnectionPool(
            max_connections=self.config.max_workers,
            connection_timeout=self.config.connection_timeout
        )
        self.results_collector = ResultsCollector()
        
        # Thread pool for parallel execution
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_workers,
            thread_name_prefix="ParallelExecutor"
        )
        
        # Tracking
        self._stop_event = threading.Event()
        self._current_execution: Optional[ParallelResults] = None
        
        # Start connection pool
        self.pool.start()
        
        logger.info(f"Parallel executor initialized with {self.config.max_workers} workers")
    
    def execute(self,
                command: str,
                hosts: List[Union[HostConfig, Dict[str, Any]]],
                config: Optional[ExecutionConfig] = None) -> ParallelResults:
        """
        Execute a command on multiple hosts.
        
        Args:
            command: Command to execute
            hosts: List of hosts to execute on
            config: Override default configuration
        
        Returns:
            ParallelResults with execution results
        
        Example:
            results = executor.execute("df -h", hosts)
            for host, result in results.results.items():
                print(f"{host}: {result.output}")
        """
        # Use provided config or default
        exec_config = config or self.config
        
        # Convert dict hosts to HostConfig
        host_configs = []
        for host in hosts:
            if isinstance(host, dict):
                host_configs.append(HostConfig(**host))
            else:
                host_configs.append(host)
        
        # Start tracking execution
        self._current_execution = self.results_collector.start_execution(
            command, [h.host for h in host_configs]
        )
        
        logger.info(f"Starting execution of '{command}' on {len(host_configs)} hosts")
        
        try:
            # Execute based on strategy
            if exec_config.strategy == ExecutionStrategy.PARALLEL:
                self._execute_parallel(command, host_configs, exec_config)
            elif exec_config.strategy == ExecutionStrategy.ROLLING:
                self._execute_rolling(command, host_configs, exec_config)
            elif exec_config.strategy == ExecutionStrategy.SEQUENTIAL:
                self._execute_sequential(command, host_configs, exec_config)
            
            # Complete execution
            results = self.results_collector.complete_execution()
            logger.info(f"Execution completed: {results.summary()}")
            
            return results
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            # Still return partial results
            results = self.results_collector.complete_execution()
            if results:
                return results
            raise
    
    def execute_script(self,
                      script_path: str,
                      hosts: List[Union[HostConfig, Dict[str, Any]]],
                      config: Optional[ExecutionConfig] = None) -> ParallelResults:
        """
        Execute a script file on multiple hosts.
        
        Args:
            script_path: Path to script file
            hosts: List of hosts to execute on
            config: Override default configuration
        
        Returns:
            ParallelResults with execution results
        """
        # Read script content
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Create temporary script and execute
        command = f"""
cat > /tmp/termitty_script.$$ << 'EOF'
{script_content}
EOF
chmod +x /tmp/termitty_script.$$
/tmp/termitty_script.$$
rm -f /tmp/termitty_script.$$
"""
        
        return self.execute(command, hosts, config)
    
    def _execute_parallel(self,
                         command: str,
                         hosts: List[HostConfig],
                         config: ExecutionConfig):
        """Execute command on all hosts in parallel."""
        futures = {}
        
        for host_config in hosts:
            if self._stop_event.is_set():
                break
            
            future = self._executor.submit(
                self._execute_on_host,
                command,
                host_config,
                config
            )
            futures[future] = host_config
        
        # Wait for completion
        for future in concurrent.futures.as_completed(futures):
            host_config = futures[future]
            
            try:
                result = future.result()
                self._handle_result(host_config.host, result, config)
                
            except Exception as e:
                logger.error(f"Execution failed on {host_config.host}: {e}")
                error_result = HostResult(
                    host=host_config.host,
                    status=ResultStatus.ERROR,
                    error=e,
                    start_time=time.time(),
                    end_time=time.time()
                )
                self._handle_result(host_config.host, error_result, config)
    
    def _execute_rolling(self,
                        command: str,
                        hosts: List[HostConfig],
                        config: ExecutionConfig):
        """Execute command on hosts in rolling batches."""
        batch_size = config.batch_size
        
        for i in range(0, len(hosts), batch_size):
            if self._stop_event.is_set():
                break
            
            batch = hosts[i:i + batch_size]
            logger.info(f"Executing on batch {i//batch_size + 1}: {[h.host for h in batch]}")
            
            # Execute batch in parallel
            self._execute_parallel(command, batch, config)
            
            # Check for failures if fail_fast is enabled
            if config.fail_fast and self._current_execution.any_failed:
                logger.warning("Stopping rolling execution due to failures")
                break
    
    def _execute_sequential(self,
                           command: str,
                           hosts: List[HostConfig],
                           config: ExecutionConfig):
        """Execute command on hosts one by one."""
        for host_config in hosts:
            if self._stop_event.is_set():
                break
            
            try:
                result = self._execute_on_host(command, host_config, config)
                self._handle_result(host_config.host, result, config)
                
                # Check for failure if fail_fast is enabled
                if config.fail_fast and result.status != ResultStatus.SUCCESS:
                    logger.warning(f"Stopping sequential execution due to failure on {host_config.host}")
                    break
                    
            except Exception as e:
                logger.error(f"Execution failed on {host_config.host}: {e}")
                error_result = HostResult(
                    host=host_config.host,
                    status=ResultStatus.ERROR,
                    error=e,
                    start_time=time.time(),
                    end_time=time.time()
                )
                self._handle_result(host_config.host, error_result, config)
                
                if config.fail_fast:
                    break
    
    def _execute_on_host(self,
                        command: str,
                        host_config: HostConfig,
                        config: ExecutionConfig) -> HostResult:
        """Execute command on a single host."""
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= config.retry_failed:
            try:
                with self.pool.get_connection(
                    host=host_config.host,
                    username=host_config.username,
                    password=host_config.password,
                    key_file=host_config.key_file,
                    port=host_config.port
                ) as session:
                    
                    # Execute command
                    logger.debug(f"Executing on {host_config.host}: {command[:50]}...")
                    result = session.execute(command, timeout=config.timeout)
                    
                    # Create host result
                    return HostResult(
                        host=host_config.host,
                        status=ResultStatus.SUCCESS if result.success else ResultStatus.FAILED,
                        command_result=result,
                        start_time=start_time,
                        end_time=time.time(),
                        metadata=host_config.metadata
                    )
                    
            except Exception as e:
                retry_count += 1
                if retry_count <= config.retry_failed:
                    logger.warning(f"Retrying {host_config.host} (attempt {retry_count})")
                    time.sleep(1)  # Brief delay before retry
                else:
                    # Final failure
                    return HostResult(
                        host=host_config.host,
                        status=ResultStatus.ERROR,
                        error=e,
                        start_time=start_time,
                        end_time=time.time(),
                        metadata=host_config.metadata
                    )
    
    def _handle_result(self,
                      host: str,
                      result: HostResult,
                      config: ExecutionConfig):
        """Handle a host result."""
        # Add to results
        self.results_collector.add_host_result(host, result)
        
        # Call progress callback if provided
        if config.progress_callback:
            try:
                config.progress_callback(host, result)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
        
        # Check fail_fast
        if config.fail_fast and result.status != ResultStatus.SUCCESS:
            logger.warning(f"Fail-fast triggered by {host}")
            self._stop_event.set()
    
    def stop(self):
        """Stop the executor and clean up resources."""
        logger.info("Stopping parallel executor")
        self._stop_event.set()
        
        # Shutdown thread pool
        self._executor.shutdown(wait=True)
        
        # Stop connection pool
        self.pool.stop()
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return self.pool.get_statistics()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


def execute_parallel(command: str,
                    hosts: List[Dict[str, Any]],
                    max_workers: int = 10,
                    timeout: float = 300.0,
                    fail_fast: bool = False) -> ParallelResults:
    """
    Convenience function for simple parallel execution.
    
    Args:
        command: Command to execute
        hosts: List of host configurations
        max_workers: Maximum parallel workers
        timeout: Command timeout
        fail_fast: Stop on first failure
    
    Returns:
        ParallelResults
    
    Example:
        hosts = [
            {"host": "server1", "username": "admin", "password": "pass"},
            {"host": "server2", "username": "admin", "key_file": "~/.ssh/id_rsa"},
        ]
        
        results = execute_parallel("uptime", hosts)
        print(results.summary())
    """
    config = ExecutionConfig(
        max_workers=max_workers,
        timeout=timeout,
        fail_fast=fail_fast
    )
    
    with ParallelExecutor(config) as executor:
        return executor.execute(command, hosts)