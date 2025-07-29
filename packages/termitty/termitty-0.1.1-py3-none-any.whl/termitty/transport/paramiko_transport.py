"""
Paramiko-based transport implementation.

This module provides a concrete implementation of the TransportBase using
the Paramiko SSH library. Paramiko is a pure-Python implementation of SSHv2,
making it portable and easy to install, though potentially slower than
native SSH implementations.

This transport handles the complexities of SSH connections, including:
- Multiple authentication methods
- Key management and validation
- Connection persistence and error recovery
- Proper resource cleanup
"""

import logging
import socket
import time
from pathlib import Path
from typing import Optional, Union, Dict, Any
import io

import paramiko
from paramiko.ssh_exception import (
    SSHException, 
    AuthenticationException as ParamikoAuthException,
    NoValidConnectionsError
)

from .base import TransportBase, ConnectionResult, CommandResult
from ..core.exceptions import (
    ConnectionException,
    AuthenticationException,
    TimeoutException,
    CommandExecutionException
)
from ..core.config import config

logger = logging.getLogger(__name__)


class ParamikoTransport(TransportBase):
    """
    Paramiko-based SSH transport implementation.
    
    This class provides a production-ready SSH transport using the Paramiko library.
    It handles various authentication methods, connection management, and command
    execution with proper error handling and resource cleanup.
    """
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        Initialize the Paramiko transport.
        
        Args:
            config_override: Optional configuration overrides
        """
        super().__init__(config_override)
        
        # Paramiko-specific attributes
        self._client: Optional[paramiko.SSHClient] = None
        self._transport: Optional[paramiko.Transport] = None
        
        # Configure Paramiko logging based on our config
        if config.logging.debug_ssh_transport:
            paramiko_logger = logging.getLogger('paramiko')
            paramiko_logger.setLevel(logging.DEBUG)
    
    def connect(self,
                host: str,
                port: int = 22,
                username: Optional[str] = None,
                password: Optional[str] = None,
                key_filename: Optional[Union[str, Path]] = None,
                key_password: Optional[str] = None,
                timeout: float = 30.0,
                **kwargs) -> ConnectionResult:
        """
        Establish an SSH connection using Paramiko.
        
        This method implements the abstract connect method from TransportBase.
        It tries multiple authentication methods in order of preference and
        handles various connection failures gracefully.
        """
        # If already connected, disconnect first
        if self._connected:
            logger.warning(f"Already connected to {self._host}:{self._port}. Disconnecting.")
            self.disconnect()
        
        # Store connection parameters
        self._host = host
        self._port = port or config.connection.default_port
        self._username = username
        
        # Initialize SSH client
        self._client = paramiko.SSHClient()
        
        # Configure host key policy based on configuration
        self._setup_host_key_policy()
        
        # Prepare authentication arguments
        connect_kwargs = {
            'hostname': host,
            'port': self._port,
            'username': username,
            'timeout': timeout,
            'compress': config.connection.compression,
            'allow_agent': True,  # Allow SSH agent authentication
            'look_for_keys': True,  # Look for keys in ~/.ssh/
        }
        
        # Add authentication credentials if provided
        if password:
            connect_kwargs['password'] = password
        
        if key_filename:
            # Convert to Path and ensure it exists
            key_path = Path(key_filename).expanduser()
            if not key_path.exists():
                raise AuthenticationException(f"Key file not found: {key_path}")
            
            connect_kwargs['key_filename'] = str(key_path)
            if key_password:
                connect_kwargs['passphrase'] = key_password
        
        # Attempt connection with retries
        last_error = None
        for attempt in range(config.connection.connection_retries):
            try:
                if attempt > 0:
                    logger.info(f"Connection attempt {attempt + 1} to {host}:{self._port}")
                    time.sleep(config.connection.retry_delay)
                
                # Attempt to connect
                self._client.connect(**connect_kwargs)
                
                # Get the underlying transport for advanced operations
                self._transport = self._client.get_transport()
                
                # Enable keepalive to prevent connection timeouts
                if self._transport and config.connection.keepalive_interval > 0:
                    self._transport.set_keepalive(int(config.connection.keepalive_interval))
                
                self._connected = True
                
                # Gather server information
                server_info = self._get_server_info()
                
                logger.info(f"Successfully connected to {host}:{self._port}")
                return ConnectionResult(
                    success=True,
                    server_info=server_info
                )
                
            except ParamikoAuthException as e:
                # Authentication failed - don't retry
                error_msg = f"Authentication failed for {username}@{host}: {str(e)}"
                logger.error(error_msg)
                
                # Try to determine which auth methods were attempted
                tried_methods = []
                if password:
                    tried_methods.append('password')
                if key_filename:
                    tried_methods.append('publickey')
                
                raise AuthenticationException(error_msg, tried_methods=tried_methods)
                
            except NoValidConnectionsError as e:
                # Network-level connection failure
                last_error = ConnectionException(f"Unable to connect to {host}:{self._port}: {str(e)}")
                
            except socket.timeout:
                # Connection timeout
                last_error = TimeoutException(f"Connection to {host}:{self._port} timed out", timeout=timeout)
                
            except Exception as e:
                # Other connection errors
                last_error = ConnectionException(f"Connection failed: {str(e)}")
        
        # All retries exhausted
        if last_error:
            raise last_error
        else:
            raise ConnectionException(f"Failed to connect after {config.connection.connection_retries} attempts")
    
    def disconnect(self) -> None:
        """Close the SSH connection and clean up resources."""
        if self._client:
            try:
                self._client.close()
                logger.info(f"Disconnected from {self._host}:{self._port}")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self._client = None
                self._transport = None
                self._connected = False
                self._host = None
                self._port = None
                self._username = None
    
    def execute_command(self,
                       command: str,
                       timeout: Optional[float] = None,
                       input_data: Optional[str] = None,
                       environment: Optional[Dict[str, str]] = None,
                       working_directory: Optional[str] = None,
                       **kwargs) -> CommandResult:
        """
        Execute a command on the remote host.
        
        This implementation properly handles:
        - Command execution with timeout
        - Input/output streams
        - Environment variables
        - Working directory changes
        - Proper encoding/decoding
        """
        if not self._connected:
            raise ConnectionException("Not connected to any host")
        
        # Use configured timeout if not specified
        if timeout is None:
            timeout = config.execution.default_timeout
        
        # Build the actual command to execute
        actual_command = self._build_command(command, environment, working_directory)
        
        # Log the command if configured
        if config.logging.log_commands:
            # Be careful not to log sensitive data
            safe_command = self._sanitize_command_for_logging(actual_command)
            logger.debug(f"Executing command: {safe_command}")
        
        start_time = time.time()
        
        try:
            # Execute the command
            stdin, stdout, stderr = self._client.exec_command(
                actual_command,
                timeout=timeout,
                environment=environment
            )
            
            # Send input data if provided
            if input_data:
                stdin.write(input_data)
                if not input_data.endswith('\n'):
                    stdin.write('\n')
                stdin.flush()
                stdin.channel.shutdown_write()
            
            # Read output - this blocks until command completes or timeout
            stdout_data = stdout.read().decode(config.terminal.encoding, errors='replace')
            stderr_data = stderr.read().decode(config.terminal.encoding, errors='replace')
            
            # Get exit code
            exit_code = stdout.channel.recv_exit_status()
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log output if configured
            if config.logging.log_output:
                logger.debug(f"Command stdout: {stdout_data[:500]}...")  # Truncate for logs
                if stderr_data:
                    logger.debug(f"Command stderr: {stderr_data[:500]}...")
            
            result = CommandResult(
                stdout=stdout_data,
                stderr=stderr_data,
                exit_code=exit_code,
                duration=duration,
                encoding=config.terminal.encoding
            )
            
            # Check if we should raise on non-zero exit codes
            if config.execution.check_return_code and exit_code != 0:
                raise CommandExecutionException(
                    f"Command failed with exit code {exit_code}",
                    command=actual_command,
                    exit_code=exit_code
                )
            
            return result
            
        except socket.timeout:
            raise TimeoutException(f"Command execution timed out after {timeout}s", timeout=timeout)
        except Exception as e:
            raise CommandExecutionException(f"Command execution failed: {str(e)}", command=actual_command)
    
    def create_sftp_client(self):
        """Create an SFTP client for file transfers."""
        if not self._connected:
            raise ConnectionException("Not connected to any host")
        
        try:
            sftp = self._client.open_sftp()
            logger.debug("Created SFTP client")
            return sftp
        except Exception as e:
            raise ConnectionException(f"Failed to create SFTP client: {str(e)}")
    
    def create_interactive_shell(self,
                               term_type: str = 'xterm-256color',
                               width: int = 80,
                               height: int = 24,
                               **kwargs):
        """Create an interactive shell session with PTY."""
        if not self._connected:
            raise ConnectionException("Not connected to any host")
        
        try:
            # Request a pseudo-terminal
            channel = self._client.invoke_shell(
                term=term_type,
                width=width,
                height=height
            )
            
            logger.debug(f"Created interactive shell: {term_type} ({width}x{height})")
            return channel
            
        except Exception as e:
            raise ConnectionException(f"Failed to create interactive shell: {str(e)}")
    
    def _setup_host_key_policy(self):
        """Configure how to handle host key verification."""
        policy_map = {
            'strict': paramiko.RejectPolicy(),
            'warning': paramiko.WarningPolicy(),
            'auto-add': paramiko.AutoAddPolicy()
        }
        
        policy_name = config.connection.known_hosts_policy
        policy = policy_map.get(policy_name, paramiko.WarningPolicy())
        
        self._client.set_missing_host_key_policy(policy)
        
        # Load known hosts if using strict policy
        if policy_name == 'strict':
            known_hosts_file = Path.home() / '.ssh' / 'known_hosts'
            if known_hosts_file.exists():
                self._client.load_host_keys(str(known_hosts_file))
    
    def _get_server_info(self) -> Dict[str, Any]:
        """Gather information about the connected server."""
        info = {}
        
        if self._transport:
            try:
                info['server_version'] = self._transport.remote_version
                # Check if method exists before calling
                if hasattr(self._transport, 'get_cipher_name'):
                    info['cipher'] = self._transport.get_cipher_name()
                elif hasattr(self._transport, 'cipher_name'):
                    info['cipher'] = self._transport.cipher_name
                
                if hasattr(self._transport, 'get_username'):
                    info['username'] = self._transport.get_username()
                elif hasattr(self._transport, 'username'):
                    info['username'] = self._transport.username
                
                # Get server host key info
                host_key = self._transport.get_remote_server_key()
                if host_key:
                    info['host_key_type'] = host_key.get_name()
                    # Handle different versions of paramiko
                    if hasattr(host_key, 'get_fingerprint'):
                        info['host_key_fingerprint'] = host_key.get_fingerprint().hex()
            except Exception as e:
                logger.debug(f"Error getting server info: {e}")
        
        return info
    
    def _build_command(self, 
                      command: str, 
                      environment: Optional[Dict[str, str]], 
                      working_directory: Optional[str]) -> str:
        """Build the actual command to execute with environment and directory."""
        parts = []
        
        # Add environment variables
        if environment:
            for key, value in environment.items():
                # Properly escape values for shell
                escaped_value = value.replace("'", "'\"'\"'")
                parts.append(f"export {key}='{escaped_value}'")
        
        # Change directory if specified
        if working_directory:
            parts.append(f"cd '{working_directory}'")
        
        # Add the actual command
        parts.append(command)
        
        # Join with && to ensure each part succeeds
        return " && ".join(parts) if len(parts) > 1 else command
    
    def _sanitize_command_for_logging(self, command: str) -> str:
        """Remove sensitive information from commands before logging."""
        if not config.logging.mask_passwords:
            return command
        
        # Simple password masking - in production, this would be more sophisticated
        import re
        
        # Common password patterns
        patterns = [
            (r'password[=:]\S+', 'password=***'),
            (r'pass[=:]\S+', 'pass=***'),
            (r'pwd[=:]\S+', 'pwd=***'),
            (r'--password\s+\S+', '--password ***'),
            (r'-p\s+\S+', '-p ***'),
        ]
        
        sanitized = command
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized