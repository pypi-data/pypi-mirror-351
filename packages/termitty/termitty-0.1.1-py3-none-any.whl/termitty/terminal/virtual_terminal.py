"""
Virtual terminal implementation that combines ANSI parsing and screen buffer.

This module provides the VirtualTerminal class, which emulates a complete
terminal. It processes input containing ANSI escape codes and maintains
an accurate representation of what would be displayed on screen.
"""

import logging
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from .ansi_parser import AnsiCode, AnsiCommandType, AnsiParser
from .screen_buffer import ScreenBuffer

logger = logging.getLogger(__name__)


@dataclass
class TerminalSnapshot:
    """A snapshot of the terminal state at a point in time."""

    screen_text: str
    cursor_position: Tuple[int, int]
    width: int
    height: int
    timestamp: float

    def __str__(self):
        return f"TerminalSnapshot({self.width}x{self.height}, cursor={self.cursor_position})"


class VirtualTerminal:
    """
    A complete virtual terminal emulator.

    This class combines ANSI escape code parsing with screen buffer management
    to provide accurate terminal emulation. It can process terminal output and
    maintain the exact state of what would be displayed on screen.

    The virtual terminal is essential for:
    - Understanding terminal-based user interfaces
    - Detecting prompts and UI elements
    - Waiting for specific screen states
    - Recording and replaying terminal sessions
    """

    def __init__(self, width: int = 80, height: int = 24):
        """
        Initialize virtual terminal.

        Args:
            width: Terminal width in columns
            height: Terminal height in rows
        """
        self.parser = AnsiParser()
        self.screen = ScreenBuffer(width, height)

        # Callback for screen updates
        self._update_callback: Optional[Callable[[ScreenBuffer], None]] = None

        # History of snapshots for replay/debugging
        self._snapshot_history: List[TerminalSnapshot] = []
        self._max_snapshots = 100

        # Track if we should automatically take snapshots
        self._auto_snapshot = False

        logger.debug(f"Created virtual terminal: {width}x{height}")

    def process_output(self, data: bytes):
        """
        Process terminal output containing text and ANSI codes.

        This is the main method for feeding terminal output into the emulator.
        It parses ANSI codes and updates the screen buffer accordingly.

        Args:
            data: Raw terminal output as bytes
        """
        # Parse the data into text and ANSI codes
        elements = self.parser.parse(data)

        for is_text, content in elements:
            if is_text:
                # Regular text - write to screen buffer
                self.screen.write_string(content)
            else:
                # ANSI code - process it
                self._process_ansi_code(content)

        # Notify callback if set
        if self._update_callback:
            self._update_callback(self.screen)

        # Take snapshot if enabled
        if self._auto_snapshot:
            self.take_snapshot()

    def _process_ansi_code(self, code: AnsiCode):
        """
        Process a single ANSI escape code.

        Args:
            code: Parsed ANSI code
        """
        logger.debug(f"Processing ANSI code: {code}")

        if code.command_type == AnsiCommandType.CURSOR_UP:
            lines = code.parameters[0] if code.parameters else 1
            self.screen.move_cursor_relative(0, -lines)

        elif code.command_type == AnsiCommandType.CURSOR_DOWN:
            lines = code.parameters[0] if code.parameters else 1
            self.screen.move_cursor_relative(0, lines)

        elif code.command_type == AnsiCommandType.CURSOR_FORWARD:
            cols = code.parameters[0] if code.parameters else 1
            self.screen.move_cursor_relative(cols, 0)

        elif code.command_type == AnsiCommandType.CURSOR_BACK:
            cols = code.parameters[0] if code.parameters else 1
            self.screen.move_cursor_relative(-cols, 0)

        elif code.command_type == AnsiCommandType.CURSOR_POSITION:
            # Parameters are 1-indexed, convert to 0-indexed
            row = (code.parameters[0] - 1) if code.parameters else 0
            col = (code.parameters[1] - 1) if len(code.parameters) > 1 else 0
            self.screen.move_cursor(col, row)

        elif code.command_type == AnsiCommandType.CURSOR_SAVE:
            self.screen.save_cursor()

        elif code.command_type == AnsiCommandType.CURSOR_RESTORE:
            self.screen.restore_cursor()

        elif code.command_type == AnsiCommandType.ERASE_DISPLAY:
            mode = code.parameters[0] if code.parameters else 0
            self.screen.erase_display(mode)

        elif code.command_type == AnsiCommandType.ERASE_LINE:
            mode = code.parameters[0] if code.parameters else 0
            self.screen.erase_line(mode)

        elif code.command_type == AnsiCommandType.SCROLL_UP:
            lines = code.parameters[0] if code.parameters else 1
            self.screen.scroll_up(lines)

        elif code.command_type == AnsiCommandType.SGR:
            # Apply text formatting attributes
            self.screen.current_attributes.apply_sgr(code.parameters)

    def get_screen_text(self) -> str:
        """
        Get the current screen content as plain text.

        Returns:
            Screen content with newlines between rows
        """
        return str(self.screen)

    def get_visible_text(self) -> str:
        """
        Get only the visible (non-empty) portion of the screen.

        This is useful for comparing screen states without worrying about
        trailing blank lines.

        Returns:
            Visible screen content
        """
        lines = []
        last_non_empty = -1

        # Find last non-empty line
        for y in range(self.screen.height):
            line = self.screen.get_line(y).rstrip()
            if line:
                last_non_empty = y

        # Get all lines up to last non-empty
        for y in range(last_non_empty + 1):
            lines.append(self.screen.get_line(y).rstrip())

        return "\n".join(lines)

    def find_prompt(
        self, patterns: Optional[List[str]] = None, default_pattern: str = r"[\$#>] "
    ) -> Optional[Tuple[int, str]]:
        """
        Find a command prompt on the screen.

        Args:
            patterns: List of regex patterns to search for
            default_pattern: Default pattern if none provided

        Returns:
            Tuple of (line_number, prompt_text) if found, None otherwise
        """
        import re

        if patterns is None:
            patterns = [default_pattern]

        # Search from bottom up (prompts are usually at the bottom)
        for y in range(self.screen.height - 1, -1, -1):
            line = self.screen.get_line(y)
            if not line.strip():  # Skip truly empty lines
                continue

            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return (y, match.group(0))

        return None

    def find_menu_items(self) -> List[Tuple[int, str]]:
        """
        Find potential menu items on screen.

        This looks for common menu patterns like:
        - [1] Option One
        - 1. Option One
        - 1) Option One

        Returns:
            List of (line_number, menu_text) tuples
        """
        import re

        menu_patterns = [
            r"\[(\d+)\]\s+(.+)",  # [1] Option
            r"(\d+)\.\s+(.+)",  # 1. Option
            r"(\d+)\)\s+(.+)",  # 1) Option
        ]

        items = []

        for y in range(self.screen.height):
            line = self.screen.get_line(y).strip()
            if not line:
                continue

            for pattern in menu_patterns:
                match = re.match(pattern, line)
                if match:
                    items.append((y, line))
                    break

        return items

    def wait_for_text(
        self, text: str, timeout: float = 10.0, poll_interval: float = 0.1
    ) -> bool:
        """
        Wait for specific text to appear on screen.

        Args:
            text: Text to wait for
            timeout: Maximum time to wait
            poll_interval: How often to check

        Returns:
            True if text appeared, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if text in self.get_screen_text():
                return True
            time.sleep(poll_interval)

        return False

    def wait_for_prompt(
        self,
        patterns: Optional[List[str]] = None,
        timeout: float = 10.0,
        poll_interval: float = 0.1,
    ) -> Optional[Tuple[int, str]]:
        """
        Wait for a command prompt to appear.

        Args:
            patterns: Prompt patterns to search for
            timeout: Maximum time to wait
            poll_interval: How often to check

        Returns:
            Tuple of (line_number, prompt_text) if found, None if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            prompt = self.find_prompt(patterns)
            if prompt:
                return prompt
            time.sleep(poll_interval)

        return None

    def clear(self):
        """Clear the terminal screen."""
        self.screen.clear()

    def resize(self, width: int, height: int):
        """
        Resize the terminal.

        Args:
            width: New width in columns
            height: New height in rows
        """
        self.screen.resize(width, height)
        logger.debug(f"Resized terminal to {width}x{height}")

    def set_update_callback(self, callback: Optional[Callable[[ScreenBuffer], None]]):
        """
        Set a callback to be called when screen updates.

        Args:
            callback: Function to call with screen buffer on updates
        """
        self._update_callback = callback

    def take_snapshot(self) -> TerminalSnapshot:
        """
        Take a snapshot of the current terminal state.

        Returns:
            TerminalSnapshot object
        """
        snapshot = TerminalSnapshot(
            screen_text=self.get_screen_text(),
            cursor_position=(self.screen.cursor_x, self.screen.cursor_y),
            width=self.screen.width,
            height=self.screen.height,
            timestamp=time.time(),
        )

        # Add to history
        self._snapshot_history.append(snapshot)

        # Limit history size
        if len(self._snapshot_history) > self._max_snapshots:
            self._snapshot_history = self._snapshot_history[-self._max_snapshots :]

        return snapshot

    def enable_auto_snapshot(self, enabled: bool = True):
        """
        Enable or disable automatic snapshots on updates.

        Args:
            enabled: Whether to enable auto snapshots
        """
        self._auto_snapshot = enabled

    def get_snapshot_history(self) -> List[TerminalSnapshot]:
        """Get the history of terminal snapshots."""
        return self._snapshot_history.copy()

    def replay_to_snapshot(self, snapshot: TerminalSnapshot):
        """
        Restore terminal to a previous snapshot state.

        Args:
            snapshot: Snapshot to restore to

        Note:
            This is mainly useful for debugging and testing.
        """
        # Clear and resize to match snapshot
        self.resize(snapshot.width, snapshot.height)
        self.clear()

        # Restore screen content
        lines = snapshot.screen_text.split("\n")
        for y, line in enumerate(lines[: snapshot.height]):
            self.screen.cursor_y = y
            self.screen.cursor_x = 0
            self.screen.write_string(line)

        # Restore cursor position
        self.screen.cursor_x, self.screen.cursor_y = snapshot.cursor_position

    def get_cursor_position(self) -> Tuple[int, int]:
        """
        Get current cursor position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.screen.cursor_x, self.screen.cursor_y)

    def get_line_at_cursor(self) -> str:
        """Get the line where the cursor is currently positioned."""
        return self.screen.get_line(self.screen.cursor_y)

    def __str__(self) -> str:
        """String representation shows current screen content."""
        return self.get_screen_text()

    def __repr__(self) -> str:
        """Representation includes terminal dimensions."""
        return (
            f"VirtualTerminal({self.screen.width}x{self.screen.height}, "
            f"cursor=({self.screen.cursor_x}, {self.screen.cursor_y}))"
        )
