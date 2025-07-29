"""
Main session class for Termitty.

This module provides the primary interface that users interact with. The
TermittySession class is designed to feel familiar to Selenium users while
providing powerful terminal automation capabilities.

The session manages:
- Connection lifecycle
- Command execution with intelligent waiting
- State tracking (working directory, environment)
- Pattern matching and element finding
- Context managers for temporary state changes
- Terminal emulation (Phase 2)
- Interactive shell sessions (Phase 3)
"""

import contextlib
import logging
import re
import time
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Pattern, Callable, Tuple
from dataclasses import dataclass, field

from ..core.config import config
from ..core.exceptions import (
    ConnectionException,
    TimeoutException,
    ElementNotFoundException,
    SessionStateException,
    CommandExecutionException
)
from ..transport.base import TransportBase, CommandResult
from ..transport.paramiko_transport import ParamikoTransport
from ..terminal.virtual_terminal import VirtualTerminal
from ..interactive.shell import InteractiveShell

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Tracks the current state of a terminal session."""
    working_directory: Optional[str] = None
    environment_variables: Dict[str, str] = field(default_factory=dict)
    last_command: Optional[str] = None
    last_result: Optional[CommandResult] = None
    command_history: List[str] = field(default_factory=list)
    terminal: Optional[VirtualTerminal] = None
    terminal_emulation_enabled: bool = True
    
    def add_command(self, command: str):
        """Add a command to history."""
        self.command_history.append(command)
        self.last_command = command
        # Keep history reasonable size
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]


class WaitCondition:
    """
    Represents a condition to wait for in terminal output.
    
    This is similar to Selenium's expected_conditions, providing
    reusable conditions for common waiting scenarios.
    """
    
    def __init__(self, description: str):
        self.description = description
    
    def __call__(self, session: 'TermittySession') -> bool:
        """Check if condition is met. Override in subclasses."""
        raise NotImplementedError
    
    def __str__(self):
        return self.description


class OutputContains(WaitCondition):
    """Wait for specific text to appear in command output."""
    
    def __init__(self, text: str, case_sensitive: bool = True):
        super().__init__(f"output contains '{text}'")
        self.text = text
        self.case_sensitive = case_sensitive
    
    def __call__(self, session: 'TermittySession') -> bool:
        if not session.state.last_result:
            return False
        
        output = session.state.last_result.output
        if not self.case_sensitive:
            output = output.lower()
            text = self.text.lower()
        else:
            text = self.text
        
        return text in output


class OutputMatches(WaitCondition):
    """Wait for output to match a regular expression."""
    
    def __init__(self, pattern: Union[str, Pattern], flags: int = 0):
        super().__init__(f"output matches pattern")
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern, flags)
        else:
            self.pattern = pattern
    
    def __call__(self, session: 'TermittySession') -> bool:
        if not session.state.last_result:
            return False
        
        return bool(self.pattern.search(session.state.last_result.output))


class PromptReady(WaitCondition):
    """Wait for a command prompt to appear."""
    
    def __init__(self, prompt_pattern: Optional[str] = None):
        super().__init__("prompt is ready")
        self.prompt_pattern = prompt_pattern or config.execution.shell_prompt_pattern
        self.pattern = re.compile(self.prompt_pattern)
    
    def __call__(self, session: 'TermittySession') -> bool:
        if not session.state.last_result:
            return False
        
        # Check if the output ends with a prompt
        # Don't strip the output as it might remove important trailing spaces
        lines = session.state.last_result.output.rstrip('\n').split('\n')
        if not lines:
            return False
        
        last_line = lines[-1]
        return bool(self.pattern.search(last_line))


class TermittySession:
    """
    Main session class for terminal automation.
    
    This class provides the primary interface for Termitty users. It manages
    SSH connections, executes commands, and provides intelligent waiting and
    interaction capabilities similar to Selenium WebDriver.
    
    Example:
        with TermittySession() as session:
            session.connect('example.com', username='user')
            session.execute('ls -la')
            session.wait_until(OutputContains('important_file.txt'))
    """
    
    def __init__(self, transport: Optional[TransportBase] = None, enable_terminal_emulation: bool = True):
        """
        Initialize a new Termitty session.
        
        Args:
            transport: Optional transport instance. If not provided,
                      a ParamikoTransport will be created.
            enable_terminal_emulation: Whether to enable virtual terminal emulation
        """
        self.transport = transport or ParamikoTransport()
        self.state = SessionState()
        self._default_timeout = config.execution.default_timeout
        
        # Create virtual terminal if emulation is enabled
        if enable_terminal_emulation:
            self.state.terminal = VirtualTerminal(
                width=config.terminal.width,
                height=config.terminal.height
            )
            self.state.terminal_emulation_enabled = True
        
        # Track if we're in a context manager
        self._in_context = False
    
    @property
    def connected(self) -> bool:
        """Check if session is connected."""
        return self.transport.connected
    
    @property
    def last_result(self) -> Optional[CommandResult]:
        """Get the result of the last executed command."""
        return self.state.last_result
    
    def connect(self, 
                host: str,
                username: Optional[str] = None,
                password: Optional[str] = None,
                port: int = 22,
                key_file: Optional[Union[str, Path]] = None,
                timeout: float = 30.0,
                **kwargs) -> 'TermittySession':
        """
        Connect to a remote host via SSH.
        
        This method establishes an SSH connection and initializes the session
        state. It supports various authentication methods including password
        and public key authentication.
        
        Args:
            host: Hostname or IP address
            username: SSH username
            password: SSH password (if using password auth)
            port: SSH port (default: 22)
            key_file: Path to private key file (if using key auth)
            timeout: Connection timeout in seconds
            **kwargs: Additional transport-specific options
        
        Returns:
            Self for method chaining
        
        Raises:
            ConnectionException: If connection fails
            AuthenticationException: If authentication fails
        
        Example:
            session = TermittySession()
            session.connect('example.com', username='admin', key_file='~/.ssh/id_rsa')
        """
        logger.info(f"Connecting to {host}:{port} as {username}")
        
        result = self.transport.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            key_filename=key_file,
            timeout=timeout,
            **kwargs
        )
        
        if result.success:
            # Initialize session state
            self._initialize_session_state()
            logger.info("Session connected and initialized")
        
        return self
    
    def disconnect(self) -> None:
        """
        Disconnect from the remote host.
        
        This method closes the SSH connection and resets the session state.
        It's safe to call multiple times.
        """
        if self.connected:
            logger.info("Disconnecting session")
            self.transport.disconnect()
            self.state = SessionState()
    
    def execute(self,
                command: str,
                timeout: Optional[float] = None,
                check: bool = None,
                input_data: Optional[str] = None,
                environment: Optional[Dict[str, str]] = None,
                capture_output: bool = True) -> CommandResult:
        """
        Execute a command on the remote host.
        
        This is the primary method for running commands. It executes the command
        and returns the result, including output and exit code.
        
        Args:
            command: Command to execute
            timeout: Maximum execution time (uses default if None)
            check: Whether to raise exception on non-zero exit code
            input_data: Data to send to stdin
            environment: Additional environment variables
            capture_output: Whether to capture stdout/stderr
        
        Returns:
            CommandResult with output and exit code
        
        Raises:
            SessionStateException: If not connected
            CommandExecutionException: If command fails and check=True
            TimeoutException: If command exceeds timeout
        
        Example:
            result = session.execute('grep "error" /var/log/syslog')
            if result.success:
                print(f"Found {len(result.output.splitlines())} errors")
        """
        if not self.connected:
            raise SessionStateException("Not connected to any host")
        
        # Use defaults from config if not specified
        if timeout is None:
            timeout = self._default_timeout
        
        if check is None:
            check = config.execution.check_return_code
        
        # Add command to history
        self.state.add_command(command)
        
        # Merge environment with session environment
        if environment:
            merged_env = self.state.environment_variables.copy()
            merged_env.update(environment)
        else:
            merged_env = self.state.environment_variables
        
        # Execute with current working directory
        result = self.transport.execute_command(
            command=command,
            timeout=timeout,
            input_data=input_data,
            environment=merged_env if merged_env else None,
            working_directory=self.state.working_directory
        )
        
        # Update state
        self.state.last_result = result
        
        # Feed output to virtual terminal if enabled
        if self.state.terminal_emulation_enabled and self.state.terminal:
            # Combine stdout and stderr as they would appear in terminal
            combined_output = result.stdout
            if result.stderr:
                combined_output += result.stderr
            
            # Process the output through the terminal emulator
            self.state.terminal.process_output(combined_output.encode(config.terminal.encoding))
        
        # Check exit code if requested
        if check and result.exit_code != 0:
            raise CommandExecutionException(
                f"Command '{command}' failed with exit code {result.exit_code}",
                command=command,
                exit_code=result.exit_code
            )
        
        return result
    
    def wait_until(self,
                   condition: Union[WaitCondition, Callable],
                   timeout: float = 10.0,
                   poll_frequency: float = 0.5,
                   message: str = "") -> bool:
        """
        Wait until a condition is met.
        
        This method provides Selenium-style waiting functionality. It repeatedly
        checks a condition until it's met or the timeout is reached.
        
        Args:
            condition: WaitCondition object or callable that returns bool
            timeout: Maximum time to wait
            poll_frequency: How often to check the condition
            message: Custom timeout message
        
        Returns:
            True when condition is met
        
        Raises:
            TimeoutException: If condition is not met within timeout
        
        Example:
            session.execute('long_running_job.sh &')
            session.wait_until(OutputContains('Job completed'), timeout=300)
        """
        end_time = time.time() + timeout
        last_exception = None
        
        while time.time() < end_time:
            try:
                if callable(condition):
                    if condition(self):
                        return True
                else:
                    # Assume it's a callable object with __call__
                    if condition(self):
                        return True
            except Exception as e:
                last_exception = e
            
            time.sleep(poll_frequency)
        
        # Timeout reached
        timeout_message = message or f"Timed out waiting for {condition}"
        if last_exception:
            timeout_message += f" (last error: {last_exception})"
        
        raise TimeoutException(timeout_message, timeout=timeout)
    
    def wait_for_prompt(self, 
                        prompt_pattern: Optional[str] = None,
                        timeout: float = 10.0) -> str:
        """
        Wait for a command prompt to appear.
        
        This is useful after running commands that might take time to complete
        or when waiting for interactive programs to be ready for input.
        
        Args:
            prompt_pattern: Regex pattern for prompt (uses default if None)
            timeout: Maximum time to wait
        
        Returns:
            The matched prompt string
        
        Raises:
            TimeoutException: If prompt doesn't appear within timeout
        """
        condition = PromptReady(prompt_pattern)
        self.wait_until(condition, timeout=timeout)
        
        # Extract the actual prompt from the output
        if self.state.last_result:
            lines = self.state.last_result.output.strip().split('\n')
            if lines:
                return lines[-1]
        
        return ""
    
    def wait_until_output_contains(self,
                                   text: str,
                                   timeout: float = 10.0,
                                   case_sensitive: bool = True) -> None:
        """
        Wait for specific text to appear in command output.
        
        This is a convenience method that waits for text to appear in the
        output of the last executed command.
        
        Args:
            text: Text to search for
            timeout: Maximum time to wait
            case_sensitive: Whether search is case-sensitive
        
        Raises:
            TimeoutException: If text doesn't appear within timeout
        """
        condition = OutputContains(text, case_sensitive)
        self.wait_until(condition, timeout=timeout)
    
    @contextlib.contextmanager
    def cd(self, directory: str):
        """
        Context manager for temporarily changing directories.
        
        This provides a Pythonic way to run commands in a different directory
        and automatically return to the original directory afterwards.
        
        Example:
            with session.cd('/var/log'):
                result = session.execute('ls -la')  # Runs in /var/log
            # Automatically returns to original directory
        """
        if not self.connected:
            raise SessionStateException("Not connected to any host")
        
        # Get current directory
        original_dir = self.state.working_directory
        
        try:
            # Expand tilde to home directory
            if directory.startswith('~'):
                # Get home directory
                home_result = self.execute('echo $HOME', capture_output=True)
                if home_result.success:
                    home_dir = home_result.output.strip()
                    directory = directory.replace('~', home_dir, 1)
            
            # Change to new directory
            logger.debug(f"Changing directory to: {directory}")
            self.state.working_directory = directory
            
            # Verify the directory exists by trying to cd to it
            result = self.execute(f'cd "{directory}" && pwd', capture_output=True)
            if not result.success:
                raise CommandExecutionException(f"Failed to change directory to: {directory}")
            
            # Update working directory to the actual path (handles symlinks, ~, etc.)
            actual_path = result.output.strip()
            self.state.working_directory = actual_path
            
            yield self
            
        finally:
            # Restore original directory
            logger.debug(f"Restoring directory to: {original_dir}")
            self.state.working_directory = original_dir
    
    @contextlib.contextmanager
    def env(self, **variables):
        """
        Context manager for temporarily setting environment variables.
        
        This allows you to run commands with specific environment variables
        that are automatically cleaned up afterwards.
        
        Example:
            with session.env(JAVA_HOME='/usr/lib/jvm/java-11', PATH='/custom/bin:$PATH'):
                result = session.execute('java -version')
            # Environment variables are restored
        """
        if not self.connected:
            raise SessionStateException("Not connected to any host")
        
        # Save original environment
        original_env = self.state.environment_variables.copy()
        
        try:
            # Update environment
            self.state.environment_variables.update(variables)
            logger.debug(f"Set environment variables: {list(variables.keys())}")
            
            yield self
            
        finally:
            # Restore original environment
            self.state.environment_variables = original_env
            logger.debug("Restored original environment variables")
    
    def send(self, text: str, add_newline: bool = True) -> None:
        """
        Send text to an interactive command.
        
        This method is used for interacting with commands that expect input,
        such as password prompts or interactive installers.
        
        Args:
            text: Text to send
            add_newline: Whether to add a newline character
        
        Note:
            This is a placeholder for future interactive shell support.
            Currently, use the input_data parameter of execute() instead.
        """
        # TODO: Implement interactive shell support
        raise NotImplementedError("Interactive shell support coming in Phase 3")
    
    def find_in_output(self,
                       pattern: Union[str, Pattern],
                       flags: int = 0) -> Optional[re.Match]:
        """
        Find a pattern in the last command's output.
        
        This searches the output of the last executed command for a pattern
        and returns the match object if found.
        
        Args:
            pattern: Regex pattern to search for
            flags: Regex flags (e.g., re.IGNORECASE)
        
        Returns:
            Match object if found, None otherwise
        
        Example:
            session.execute('ip addr show')
            match = session.find_in_output(r'inet (\d+\.\d+\.\d+\.\d+)')
            if match:
                ip_address = match.group(1)
        """
        if not self.state.last_result:
            return None
        
        if isinstance(pattern, str):
            pattern = re.compile(pattern, flags)
        
        return pattern.search(self.state.last_result.output)
    
    # ========== Phase 2: Terminal Emulation Methods ==========
    
    def get_screen_text(self) -> str:
        """
        Get the current terminal screen content.
        
        This returns what would be visible on the terminal screen right now,
        which may be different from the raw command output if the command
        used terminal control sequences.
        
        Returns:
            Current screen content
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal_emulation_enabled or not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.get_visible_text()
    
    def find_on_screen(self, 
                       pattern: Union[str, Pattern],
                       regex: bool = False,
                       case_sensitive: bool = True) -> List[Tuple[int, int]]:
        """
        Find text on the current terminal screen.
        
        This searches the virtual terminal screen for patterns, which is useful
        for locating UI elements in terminal applications. It handles various
        corner cases like text split across lines, extra spaces, and different
        text positions.
        
        Args:
            pattern: Text or regex pattern to find
            regex: Whether pattern is a regular expression (default: False for simple string search)
            case_sensitive: Whether search is case-sensitive (only for non-regex searches)
        
        Returns:
            List of (row, column) positions where pattern starts
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        
        Example:
            # Simple string search
            positions = session.find_on_screen("Menu")
            
            # Case-insensitive search
            positions = session.find_on_screen("menu", case_sensitive=False)
            
            # Regex search
            positions = session.find_on_screen(r"\[\d+\].*Option", regex=True)
        """
        if not self.state.terminal_emulation_enabled or not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        # Handle case-insensitive searches for non-regex patterns
        if not regex and not case_sensitive and isinstance(pattern, str):
            # Convert to case-insensitive regex
            import re
            escaped_pattern = re.escape(pattern)
            pattern = re.compile(escaped_pattern, re.IGNORECASE)
            regex = True
        
        return self.state.terminal.screen.find_text(pattern, regex=regex)
    
    def wait_for_screen_text(self,
                            text: str,
                            timeout: float = 10.0,
                            poll_frequency: float = 0.5,
                            case_sensitive: bool = True) -> bool:
        """
        Wait for specific text to appear on the terminal screen.
        
        This is more accurate than waiting for output when dealing with
        terminal applications that update the screen dynamically. It handles
        text that might be split across lines or have extra spaces.
        
        Args:
            text: Text to wait for on screen
            timeout: Maximum time to wait
            poll_frequency: How often to check
            case_sensitive: Whether search is case-sensitive
        
        Returns:
            True if text appeared, False if timeout
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal_emulation_enabled or not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check multiple places where text might appear
            screen_text = self.state.terminal.get_screen_text()
            visible_text = self.state.terminal.get_visible_text()
            
            # Normalize search if not case sensitive
            if not case_sensitive:
                search_text = text.lower()
                screen_text = screen_text.lower()
                visible_text = visible_text.lower()
            else:
                search_text = text
            
            # Check if text appears anywhere
            if search_text in screen_text or search_text in visible_text:
                return True
            
            # Also check with normalized spaces
            normalized_screen = ' '.join(screen_text.split())
            normalized_visible = ' '.join(visible_text.split())
            normalized_search = ' '.join(search_text.split())
            
            if normalized_search in normalized_screen or normalized_search in normalized_visible:
                return True
            
            time.sleep(poll_frequency)
        
        return False
    
    def find_menu_items(self) -> List[Tuple[int, str]]:
        """
        Find menu items on the current terminal screen.
        
        This looks for common menu patterns and returns their positions,
        useful for automating terminal-based menu systems.
        
        Returns:
            List of (line_number, menu_text) tuples
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal_emulation_enabled or not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.find_menu_items()
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """
        Get the current cursor position on the terminal screen.
        
        Returns:
            Tuple of (column, row) coordinates
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal_emulation_enabled or not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.get_cursor_position()
    
    def take_terminal_snapshot(self):
        """
        Take a snapshot of the current terminal state.
        
        This is useful for debugging or recording terminal sessions.
        
        Returns:
            TerminalSnapshot object
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal_emulation_enabled or not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.take_snapshot()
    
    def find_all_text(self,
                      pattern: Union[str, Pattern],
                      include_screen: bool = True,
                      include_last_output: bool = True,
                      case_sensitive: bool = True) -> Dict[str, List[Union[Tuple[int, int], int]]]:
        """
        Find text in all available sources (screen, command output).
        
        This comprehensive search method looks for text in multiple places
        and returns all occurrences. Useful for debugging or when you're
        not sure where text might appear.
        
        Args:
            pattern: Text or regex pattern to find
            include_screen: Whether to search the terminal screen
            include_last_output: Whether to search the last command output
            case_sensitive: Whether search is case-sensitive
        
        Returns:
            Dictionary with keys 'screen' and 'output' containing found positions
        
        Example:
            results = session.find_all_text("error")
            if results['screen']:
                print(f"Found on screen at: {results['screen']}")
            if results['output']:
                print(f"Found in output at positions: {results['output']}")
        """
        results = {'screen': [], 'output': []}
        
        # Search screen if requested and available
        if include_screen and self.state.terminal_emulation_enabled and self.state.terminal:
            try:
                positions = self.find_on_screen(pattern, regex=isinstance(pattern, Pattern), case_sensitive=case_sensitive)
                results['screen'] = positions
            except Exception as e:
                logger.debug(f"Error searching screen: {e}")
        
        # Search last command output if requested
        if include_last_output and self.state.last_result:
            output = self.state.last_result.output
            
            if isinstance(pattern, Pattern):
                # Regex search
                for match in pattern.finditer(output):
                    results['output'].append(match.start())
            else:
                # String search
                search_text = str(pattern)
                if not case_sensitive:
                    search_text = search_text.lower()
                    output = output.lower()
                
                # Find all occurrences
                start = 0
                while True:
                    pos = output.find(search_text, start)
                    if pos == -1:
                        break
                    results['output'].append(pos)
                    start = pos + 1
        
        return results
    
    # ========== Phase 3: Interactive Shell Methods ==========
    
    def create_shell(self,
                     term_type: str = 'xterm-256color',
                     width: int = 80,
                     height: int = 24) -> InteractiveShell:
        """
        Create an interactive shell session.
        
        This opens a persistent shell that can be used for real-time
        interaction with programs, maintaining state between commands.
        
        Args:
            term_type: Terminal type to emulate
            width: Terminal width in columns
            height: Terminal height in rows
        
        Returns:
            InteractiveShell instance
        
        Raises:
            SessionStateException: If not connected
        
        Example:
            with session.create_shell() as shell:
                shell.send_line("cd /var/log")
                shell.wait_for_prompt()
                
                shell.send_line("tail -f syslog")
                # Watch output in real-time...
                shell.interrupt()  # Send Ctrl+C
                
                shell.send_line("vim config.txt")
                shell.wait_for_pattern("~")
                shell.send("i")
                shell.send("New config value")
                shell.send_escape()
                shell.send(":wq\\n")
        """
        if not self.connected:
            raise SessionStateException("Not connected to any host")
        
        logger.info(f"Creating interactive shell: {term_type} ({width}x{height})")
        
        # Create interactive shell channel
        channel = self.transport.create_interactive_shell(
            term_type=term_type,
            width=width,
            height=height
        )
        
        # Create and return interactive shell
        shell = InteractiveShell(
            channel=channel,
            encoding=config.terminal.encoding,
            terminal_width=width,
            terminal_height=height
        )
        
        # Wait for initial prompt
        shell.wait_for_prompt(timeout=5.0)
        
        return shell
    
    def _initialize_session_state(self) -> None:
        """Initialize session state after connection."""
        try:
            # Get initial working directory
            result = self.execute('pwd', capture_output=True)
            if result.success:
                self.state.working_directory = result.output.strip()
                logger.debug(f"Initial working directory: {self.state.working_directory}")
            
            # Get initial environment (selected variables)
            # We don't want all variables as that would be too much
            important_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'LANG']
            for var in important_vars:
                result = self.execute(f'echo "${var}"', capture_output=True)
                if result.success and result.output.strip():
                    self.state.environment_variables[var] = result.output.strip()
            
        except Exception as e:
            logger.warning(f"Failed to initialize session state: {e}")
    
    def __enter__(self) -> 'TermittySession':
        """Context manager entry."""
        self._in_context = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure disconnection."""
        self._in_context = False
        self.disconnect()
        return False
    
    def __repr__(self) -> str:
        """String representation of the session."""
        if self.connected:
            info = self.transport.connection_info
            return f"TermittySession(connected={info.get('host')}:{info.get('port')})"
        else:
            return "TermittySession(disconnected)"