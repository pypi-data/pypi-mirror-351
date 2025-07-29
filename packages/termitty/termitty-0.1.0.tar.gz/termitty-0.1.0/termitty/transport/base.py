"""
Abstract base class for transport implementations.

This module defines the interface that all transport backends must implement.
By using an abstract base class, we ensure that different SSH implementations
(Paramiko, AsyncSSH, etc.) provide a consistent interface to the rest of Termitty.

This abstraction pattern is similar to how Selenium WebDriver works - you can
switch between Chrome, Firefox, or Safari drivers without changing your test code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple, Union, Dict, Any, Callable
import io
from pathlib import Path

from ..core.exceptions import ConnectionException, AuthenticationException


@dataclass
class ConnectionResult:
    """Result of a connection attempt."""
    success: bool
    error: Optional[Exception] = None
    server_info: Optional[Dict[str, Any]] = None  # Server version, capabilities, etc.


@dataclass
class CommandResult:
    """Result of executing a command."""
    stdout: str
    stderr: str
    exit_code: int
    duration: float  # Time taken to execute in seconds
    encoding: str = 'utf-8'
    
    @property
    def success(self) -> bool:
        """Command succeeded if exit code is 0."""
        return self.exit_code == 0
    
    @property
    def output(self) -> str:
        """Combined stdout and stderr."""
        # This mimics how terminal output actually appears - stderr mixed with stdout
        return self.stdout + self.stderr if self.stderr else self.stdout


class TransportBase(ABC):
    """
    Abstract base class for all transport implementations.
    
    This defines the interface that concrete transport classes must implement.
    The design allows for both synchronous and asynchronous implementations,
    though the initial version focuses on synchronous operations.
    
    The transport layer is responsible for:
    1. Establishing and managing SSH connections
    2. Authenticating with remote servers
    3. Executing commands and capturing output
    4. Managing the lifecycle of connections
    5. Handling low-level SSH protocol details
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the transport with optional configuration.
        
        Args:
            config: Transport-specific configuration options
        """
        self.config = config or {}
        self._connected = False
        self._connection = None
        self._host = None
        self._port = None
        self._username = None
    
    @property
    def connected(self) -> bool:
        """Check if transport is currently connected."""
        return self._connected
    
    @property
    def connection_info(self) -> Dict[str, Any]:
        """Get information about the current connection."""
        if not self._connected:
            return {}
        
        return {
            'host': self._host,
            'port': self._port,
            'username': self._username,
            'transport_type': self.__class__.__name__,
            'connected': self._connected
        }
    
    @abstractmethod
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
        Establish an SSH connection to a remote host.
        
        This method must handle various authentication methods including:
        - Password authentication
        - Public key authentication
        - Keyboard-interactive authentication
        - Multi-factor authentication (if supported)
        
        Args:
            host: Hostname or IP address to connect to
            port: SSH port (default: 22)
            username: Username for authentication
            password: Password for authentication
            key_filename: Path to private key file
            key_password: Password for encrypted private key
            timeout: Connection timeout in seconds
            **kwargs: Additional transport-specific options
        
        Returns:
            ConnectionResult object indicating success/failure
        
        Raises:
            ConnectionException: If connection cannot be established
            AuthenticationException: If authentication fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the SSH connection and clean up resources.
        
        This method should be idempotent - calling it multiple times
        should not cause errors.
        """
        pass
    
    @abstractmethod
    def execute_command(self,
                       command: str,
                       timeout: Optional[float] = None,
                       input_data: Optional[str] = None,
                       environment: Optional[Dict[str, str]] = None,
                       working_directory: Optional[str] = None,
                       **kwargs) -> CommandResult:
        """
        Execute a command on the remote host.
        
        This is the core method for running commands. It should handle:
        - Command execution with proper shell escaping
        - Capturing stdout and stderr
        - Handling command timeouts
        - Providing input to commands that read from stdin
        - Setting environment variables
        - Changing working directory before execution
        
        Args:
            command: Command to execute
            timeout: Maximum time to wait for command completion
            input_data: Data to send to command's stdin
            environment: Environment variables to set
            working_directory: Directory to execute command in
            **kwargs: Additional transport-specific options
        
        Returns:
            CommandResult object with output and exit code
        
        Raises:
            CommandExecutionException: If command execution fails
            TimeoutException: If command exceeds timeout
        """
        pass
    
    @abstractmethod
    def create_sftp_client(self):
        """
        Create an SFTP client for file transfer operations.
        
        Returns:
            SFTP client object (implementation-specific)
        
        Raises:
            ConnectionException: If not connected
            UnsupportedOperationException: If SFTP is not available
        """
        pass
    
    @abstractmethod
    def create_interactive_shell(self,
                               term_type: str = 'xterm-256color',
                               width: int = 80,
                               height: int = 24,
                               **kwargs):
        """
        Create an interactive shell session.
        
        This creates a PTY (pseudo-terminal) session that can be used
        for interactive commands, terminal applications, and real-time
        interaction.
        
        Args:
            term_type: Terminal type to emulate
            width: Terminal width in columns
            height: Terminal height in rows
            **kwargs: Additional terminal options
        
        Returns:
            Shell channel object (implementation-specific)
        
        Raises:
            ConnectionException: If not connected
        """
        pass
    
    def validate_connection(self) -> bool:
        """
        Check if the current connection is still valid.
        
        This method can be overridden by subclasses to provide
        transport-specific validation logic.
        
        Returns:
            True if connection is valid, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            # Try a simple command to test the connection
            result = self.execute_command('echo "test"', timeout=5.0)
            return result.success
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry - returns self."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.disconnect()
        return False  # Don't suppress exceptions
    
    def __del__(self):
        """Destructor - attempt to close connection if still open."""
        try:
            if self._connected:
                self.disconnect()
        except Exception:
            # Ignore errors during cleanup
            pass