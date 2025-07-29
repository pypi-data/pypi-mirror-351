"""
Interactive shell implementation for Termitty.

This module provides the InteractiveShell class, which enables real-time
interaction with remote shells, supporting features like command execution,
program interaction, and special key handling.
"""

import time
import logging
from typing import Optional, Union, List, Callable, Pattern, Tuple
from dataclasses import dataclass
import re

from .io_handler import IOHandler, IOEvent, IOEventType
from .key_codes import KeyCodes, SpecialKeys
from .patterns import PatternMatcher, PatternMatch, PatternType
from ..terminal.virtual_terminal import VirtualTerminal
from ..core.exceptions import TimeoutException, SessionStateException
from ..core.config import config

logger = logging.getLogger(__name__)


@dataclass
class ShellState:
    """Tracks the state of an interactive shell."""
    connected: bool = False
    current_prompt: Optional[str] = None
    last_command: Optional[str] = None
    command_running: bool = False
    terminal: Optional[VirtualTerminal] = None
    start_time: float = 0.0
    
    def __post_init__(self):
        if self.start_time == 0.0:
            self.start_time = time.time()


class InteractiveShell:
    """
    Interactive shell session for real-time terminal interaction.
    
    This class provides a high-level interface for interacting with remote
    shells in real-time, supporting features like:
    - Persistent shell sessions
    - Real-time I/O with programs
    - Special key support (Ctrl+C, ESC, etc.)
    - Pattern-based waiting
    - Terminal state tracking
    
    Example:
        shell = session.create_shell()
        shell.send("vim test.txt\\n")
        shell.wait_for_pattern("~")  # Wait for vim to open
        shell.send("i")  # Insert mode
        shell.send("Hello from Termitty!")
        shell.send_key("escape")
        shell.send(":wq\\n")
    """
    
    def __init__(self,
                 channel,
                 encoding: str = 'utf-8',
                 terminal_width: int = 80,
                 terminal_height: int = 24):
        """
        Initialize an interactive shell.
        
        Args:
            channel: SSH channel for the shell
            encoding: Character encoding to use
            terminal_width: Terminal width in columns
            terminal_height: Terminal height in rows
        """
        self.channel = channel
        self.encoding = encoding
        
        # Initialize components
        self.io_handler = IOHandler(channel, encoding=encoding)
        self.pattern_matcher = PatternMatcher()
        
        # Initialize state
        self.state = ShellState()
        
        # Initialize virtual terminal if enabled
        if config.terminal.ansi_colors:
            self.state.terminal = VirtualTerminal(
                width=terminal_width,
                height=terminal_height
            )
        
        # Set up callbacks
        self.io_handler.set_data_callback(self._on_data_received)
        self.io_handler.set_event_callback(self._on_io_event)
        
        # Buffer for received data
        self._receive_buffer = b''
        self._line_buffer = []
        
        # Start I/O handling
        self.io_handler.start()
        self.state.connected = True
        
        logger.info("Interactive shell initialized")
    
    def send(self, data: Union[str, bytes]):
        """
        Send data to the shell.
        
        Args:
            data: Data to send (string or bytes)
        
        Example:
            shell.send("ls -la\\n")
            shell.send("cd /var/log\\n")
        """
        if not self.state.connected:
            raise SessionStateException("Shell is not connected")
        
        self.io_handler.send(data)
        
        # Track commands
        if isinstance(data, str) and data.endswith('\n'):
            self.state.last_command = data.strip()
            self.state.command_running = True
    
    def send_line(self, line: str):
        """
        Send a line of text with newline.
        
        Args:
            line: Line to send (newline will be added)
        
        Example:
            shell.send_line("echo 'Hello, World!'")
        """
        self.send(line + '\n')
    
    def send_key(self, key_name: str):
        """
        Send a special key.
        
        Args:
            key_name: Name of the key (e.g., 'ctrl+c', 'escape', 'tab')
        
        Example:
            shell.send_key('ctrl+c')  # Interrupt
            shell.send_key('tab')     # Tab completion
            shell.send_key('escape')  # ESC key
        """
        key_code = KeyCodes.get_key_code(key_name)
        self.send(key_code)
    
    def send_control(self, letter: str):
        """
        Send a control key combination.
        
        Args:
            letter: Letter for the control combination (a-z)
        
        Example:
            shell.send_control('c')  # Ctrl+C
            shell.send_control('d')  # Ctrl+D (EOF)
            shell.send_control('z')  # Ctrl+Z (suspend)
        """
        key_code = KeyCodes.create_ctrl_key(letter)
        self.send(key_code)
    
    def send_escape(self):
        """Send the ESC key."""
        self.send(SpecialKeys.ESCAPE.value)
    
    def read(self, timeout: Optional[float] = None) -> str:
        """
        Read available output.
        
        Args:
            timeout: Maximum time to wait for data
        
        Returns:
            Available output as string
        """
        data = self.io_handler.read(timeout=timeout)
        if data:
            return data.decode(self.encoding, errors='replace')
        return ""
    
    def read_until(self,
                   pattern: Union[str, Pattern],
                   timeout: float = 30.0) -> Optional[str]:
        """
        Read output until a pattern is found.
        
        Args:
            pattern: Pattern to search for
            timeout: Maximum time to wait
        
        Returns:
            All output up to and including the pattern, or None if timeout
        
        Example:
            output = shell.read_until("$ ")  # Read until prompt
            output = shell.read_until(r"Process completed")
        """
        if isinstance(pattern, str):
            pattern_bytes = pattern.encode(self.encoding)
        else:
            # Convert regex pattern to work with bytes
            pattern_bytes = pattern.pattern.encode(self.encoding)
        
        data = self.io_handler.read_until(pattern_bytes, timeout=timeout)
        if data:
            return data.decode(self.encoding, errors='replace')
        return None
    
    def wait_for_prompt(self,
                        prompt_patterns: Optional[List[Union[str, Pattern]]] = None,
                        timeout: float = 10.0) -> bool:
        """
        Wait for a shell prompt to appear.
        
        Args:
            prompt_patterns: Custom prompt patterns (uses defaults if None)
            timeout: Maximum time to wait
        
        Returns:
            True if prompt found, False if timeout
        
        Example:
            shell.send_line("ls -la")
            shell.wait_for_prompt()  # Wait for command to complete
        """
        def get_text():
            return self._receive_buffer.decode(self.encoding, errors='replace')
        
        # Use default patterns if none provided
        if prompt_patterns is None:
            prompt_patterns = [r'[$#>%]\s*$']
        
        match = self.pattern_matcher.wait_for_pattern(
            get_text,
            prompt_patterns,
            timeout=timeout
        )
        
        if match:
            self.state.current_prompt = match.matched_text
            self.state.command_running = False
            return True
        
        return False
    
    def wait_for_pattern(self,
                        patterns: Union[str, Pattern, List[Union[str, Pattern]]],
                        timeout: float = 30.0) -> Optional[PatternMatch]:
        """
        Wait for one or more patterns to appear.
        
        Args:
            patterns: Pattern(s) to wait for
            timeout: Maximum time to wait
        
        Returns:
            First matching pattern, or None if timeout
        
        Example:
            # Wait for success or error
            match = shell.wait_for_pattern(["Success", "Error"])
            if match and match.pattern_type == PatternType.ERROR:
                print("Command failed!")
        """
        if isinstance(patterns, (str, Pattern)):
            patterns = [patterns]
        
        def get_text():
            return self._receive_buffer.decode(self.encoding, errors='replace')
        
        return self.pattern_matcher.wait_for_pattern(
            get_text,
            patterns,
            timeout=timeout
        )
    
    def expect(self,
               patterns: List[Union[str, Pattern]],
               timeout: float = 30.0) -> Tuple[int, Optional[str]]:
        """
        Wait for one of several patterns (like pexpect).
        
        Args:
            patterns: List of patterns to wait for
            timeout: Maximum time to wait
        
        Returns:
            Tuple of (index of matched pattern, matched text)
            Returns (-1, None) if timeout
        
        Example:
            patterns = ["Password:", "Login:", "Error"]
            index, match = shell.expect(patterns)
            if index == 0:
                shell.send_line("mypassword")
            elif index == 1:
                shell.send_line("myusername")
        """
        match = self.wait_for_pattern(patterns, timeout=timeout)
        
        if match:
            # Find which pattern matched
            for i, pattern in enumerate(patterns):
                if isinstance(pattern, str):
                    if pattern in match.matched_text:
                        return (i, match.matched_text)
                else:
                    if pattern.search(match.matched_text):
                        return (i, match.matched_text)
        
        return (-1, None)
    
    def get_screen_text(self) -> str:
        """
        Get the current terminal screen content.
        
        Returns:
            Current screen content
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.get_screen_text()
    
    def get_visible_text(self) -> str:
        """
        Get only the visible portion of the screen.
        
        Returns:
            Visible screen content
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.get_visible_text()
    
    def find_on_screen(self,
                      pattern: Union[str, Pattern]) -> List[Tuple[int, int]]:
        """
        Find pattern on the terminal screen.
        
        Args:
            pattern: Pattern to search for
        
        Returns:
            List of (row, column) positions
        
        Raises:
            SessionStateException: If terminal emulation is not enabled
        """
        if not self.state.terminal:
            raise SessionStateException("Terminal emulation is not enabled")
        
        return self.state.terminal.screen.find_text(pattern, regex=isinstance(pattern, Pattern))
    
    def clear_screen(self):
        """Send clear screen command (Ctrl+L)."""
        self.send_control('l')
    
    def interrupt(self):
        """Send interrupt signal (Ctrl+C)."""
        self.send_control('c')
        self.state.command_running = False
    
    def send_eof(self):
        """Send EOF (Ctrl+D)."""
        self.send_control('d')
    
    def close(self):
        """Close the interactive shell."""
        if self.state.connected:
            logger.info("Closing interactive shell")
            
            # Stop I/O handler
            self.io_handler.stop()
            
            # Close channel
            if self.channel and not self.channel.closed:
                self.channel.close()
            
            self.state.connected = False
    
    def _on_data_received(self, data: bytes):
        """Handle received data."""
        # Add to buffer
        self._receive_buffer += data
        
        # Keep buffer size reasonable
        if len(self._receive_buffer) > 1024 * 1024:  # 1MB limit
            self._receive_buffer = self._receive_buffer[-512 * 1024:]  # Keep last 512KB
        
        # Update terminal if enabled
        if self.state.terminal:
            self.state.terminal.process_output(data)
        
        # Update line buffer
        text = data.decode(self.encoding, errors='replace')
        lines = text.split('\n')
        if lines:
            self._line_buffer.extend(lines)
            # Keep line buffer reasonable
            if len(self._line_buffer) > 1000:
                self._line_buffer = self._line_buffer[-500:]
    
    def _on_io_event(self, event: IOEvent):
        """Handle I/O events."""
        if event.event_type == IOEventType.EOF:
            logger.info("Shell received EOF")
            self.state.connected = False
        elif event.event_type == IOEventType.ERROR:
            logger.error(f"Shell I/O error: {event.error}")
    
    def get_statistics(self) -> dict:
        """
        Get shell session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        stats = self.io_handler.get_statistics()
        stats['session_duration'] = time.time() - self.state.start_time
        stats['connected'] = self.state.connected
        stats['last_command'] = self.state.last_command
        return stats
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    def __repr__(self):
        """String representation."""
        status = "connected" if self.state.connected else "disconnected"
        return f"InteractiveShell({status})"