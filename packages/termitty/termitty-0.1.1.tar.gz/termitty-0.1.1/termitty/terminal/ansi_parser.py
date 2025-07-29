"""
ANSI escape code parser for terminal emulation.

This module handles parsing and interpretation of ANSI escape sequences,
which are used to control formatting, color, cursor position, and other
terminal features. Understanding these codes is essential for accurate
terminal emulation.

ANSI escape sequences typically start with ESC[ (or \033[ in octal) and
are followed by parameters and a command letter.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class AnsiCommandType(Enum):
    """Types of ANSI commands we handle."""

    # Cursor movement
    CURSOR_UP = auto()
    CURSOR_DOWN = auto()
    CURSOR_FORWARD = auto()
    CURSOR_BACK = auto()
    CURSOR_POSITION = auto()
    CURSOR_SAVE = auto()
    CURSOR_RESTORE = auto()

    # Screen manipulation
    ERASE_DISPLAY = auto()
    ERASE_LINE = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()

    # Text formatting
    SGR = auto()  # Select Graphic Rendition (colors, bold, etc.)

    # Other
    UNKNOWN = auto()


class SgrAttribute(Enum):
    """SGR (Select Graphic Rendition) attributes for text formatting."""

    # Reset
    RESET = 0

    # Intensity
    BOLD = 1
    DIM = 2
    NORMAL_INTENSITY = 22

    # Italic
    ITALIC = 3
    NOT_ITALIC = 23

    # Underline
    UNDERLINE = 4
    NOT_UNDERLINED = 24

    # Blink
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    NOT_BLINKING = 25

    # Reverse video
    REVERSE = 7
    NOT_REVERSED = 27

    # Conceal
    CONCEAL = 8
    NOT_CONCEALED = 28

    # Strikethrough
    STRIKETHROUGH = 9
    NOT_STRIKETHROUGH = 29

    # Foreground colors (30-37, 90-97)
    FG_BLACK = 30
    FG_RED = 31
    FG_GREEN = 32
    FG_YELLOW = 33
    FG_BLUE = 34
    FG_MAGENTA = 35
    FG_CYAN = 36
    FG_WHITE = 37
    FG_DEFAULT = 39

    # Bright foreground colors
    FG_BRIGHT_BLACK = 90
    FG_BRIGHT_RED = 91
    FG_BRIGHT_GREEN = 92
    FG_BRIGHT_YELLOW = 93
    FG_BRIGHT_BLUE = 94
    FG_BRIGHT_MAGENTA = 95
    FG_BRIGHT_CYAN = 96
    FG_BRIGHT_WHITE = 97

    # Background colors (40-47, 100-107)
    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47
    BG_DEFAULT = 49

    # Bright background colors
    BG_BRIGHT_BLACK = 100
    BG_BRIGHT_RED = 101
    BG_BRIGHT_GREEN = 102
    BG_BRIGHT_YELLOW = 103
    BG_BRIGHT_BLUE = 104
    BG_BRIGHT_MAGENTA = 105
    BG_BRIGHT_CYAN = 106
    BG_BRIGHT_WHITE = 107


@dataclass
class AnsiCode:
    """Represents a parsed ANSI escape code."""

    command_type: AnsiCommandType
    parameters: List[int]
    raw_sequence: str

    def __str__(self):
        return f"AnsiCode({self.command_type.name}, params={self.parameters})"


class AnsiParser:
    """
    Parser for ANSI escape sequences.

    This class takes terminal output containing ANSI codes and breaks it
    down into text and control sequences. It handles the most common ANSI
    codes used in terminal applications.
    """

    # Main pattern for CSI (Control Sequence Introducer) sequences
    # Matches: ESC [ parameters command
    CSI_PATTERN = re.compile(
        rb"\x1b\["  # ESC[ or \033[
        rb"([0-9;]*)"  # Optional parameters (digits and semicolons)
        rb"([A-Za-z])"  # Command letter
    )

    # Pattern for OSC (Operating System Command) sequences
    OSC_PATTERN = re.compile(
        rb"\x1b\]"  # ESC]
        rb"([0-9]+);"  # Command number
        rb"([^\x07\x1b]*)"  # Parameters
        rb"(?:\x07|\x1b\\)"  # Terminator (BEL or ESC\)
    )

    # Simple escape sequences (like ESC 7 for save cursor)
    SIMPLE_ESCAPE_PATTERN = re.compile(rb"\x1b([78DMc])")

    # Map of command letters to command types
    COMMAND_MAP = {
        b"A": AnsiCommandType.CURSOR_UP,
        b"B": AnsiCommandType.CURSOR_DOWN,
        b"C": AnsiCommandType.CURSOR_FORWARD,
        b"D": AnsiCommandType.CURSOR_BACK,
        b"H": AnsiCommandType.CURSOR_POSITION,
        b"f": AnsiCommandType.CURSOR_POSITION,  # Same as H
        b"J": AnsiCommandType.ERASE_DISPLAY,
        b"K": AnsiCommandType.ERASE_LINE,
        b"S": AnsiCommandType.SCROLL_UP,
        b"T": AnsiCommandType.SCROLL_DOWN,
        b"m": AnsiCommandType.SGR,
    }

    def __init__(self):
        """Initialize the ANSI parser."""
        self._buffer = bytearray()
        self._in_escape_sequence = False

    def parse(self, data: bytes) -> List[Tuple[bool, Any]]:
        """
        Parse terminal output containing ANSI escape codes.

        Args:
            data: Raw terminal output as bytes

        Returns:
            List of tuples (is_text, content) where:
            - If is_text is True, content is decoded text
            - If is_text is False, content is an AnsiCode object

        Example:
            >>> parser = AnsiParser()
            >>> results = parser.parse(b'Hello \x1b[31mred\x1b[0m world')
            >>> # Results: [(True, 'Hello '), (False, AnsiCode(SGR, [31])),
            >>> #          (True, 'red'), (False, AnsiCode(SGR, [0])),
            >>> #          (True, ' world')]
        """
        results = []
        self._buffer.extend(data)

        while self._buffer:
            # Try to find an escape sequence
            match = self.CSI_PATTERN.search(self._buffer)

            if match:
                # Add any text before the escape sequence
                if match.start() > 0:
                    text = self._buffer[: match.start()].decode(
                        "utf-8", errors="replace"
                    )
                    if text:
                        results.append((True, text))

                # Parse the escape sequence
                params_str = match.group(1)
                command = match.group(2)
                raw_sequence = match.group(0)

                # Parse parameters
                parameters = self._parse_parameters(params_str)

                # Create AnsiCode object
                command_type = self.COMMAND_MAP.get(command, AnsiCommandType.UNKNOWN)
                code = AnsiCode(
                    command_type=command_type,
                    parameters=parameters,
                    raw_sequence=raw_sequence.decode("utf-8", errors="replace"),
                )
                results.append((False, code))

                # Remove processed data from buffer
                self._buffer = self._buffer[match.end() :]

            else:
                # Check for simple escape sequences
                simple_match = self.SIMPLE_ESCAPE_PATTERN.search(self._buffer)
                if simple_match:
                    # Process text before escape
                    if simple_match.start() > 0:
                        text = self._buffer[: simple_match.start()].decode(
                            "utf-8", errors="replace"
                        )
                        if text:
                            results.append((True, text))

                    # Handle simple escape
                    command = simple_match.group(1)
                    if command == b"7":
                        code = AnsiCode(
                            AnsiCommandType.CURSOR_SAVE,
                            [],
                            simple_match.group(0).decode(),
                        )
                    elif command == b"8":
                        code = AnsiCode(
                            AnsiCommandType.CURSOR_RESTORE,
                            [],
                            simple_match.group(0).decode(),
                        )
                    else:
                        code = AnsiCode(
                            AnsiCommandType.UNKNOWN, [], simple_match.group(0).decode()
                        )

                    results.append((False, code))
                    self._buffer = self._buffer[simple_match.end() :]

                else:
                    # No escape sequence found
                    # Check if we might be in the middle of an incomplete sequence
                    if b"\x1b" in self._buffer:
                        # Find the escape character
                        esc_index = self._buffer.index(b"\x1b")

                        # Process text before escape
                        if esc_index > 0:
                            text = self._buffer[:esc_index].decode(
                                "utf-8", errors="replace"
                            )
                            if text:
                                results.append((True, text))
                            self._buffer = self._buffer[esc_index:]

                        # If the buffer is very short, we might have an incomplete sequence
                        if len(self._buffer) < 10:
                            # Wait for more data
                            break
                        else:
                            # Likely a lone escape character, treat as text
                            results.append((True, "\x1b"))
                            self._buffer = self._buffer[1:]
                    else:
                        # All remaining data is text
                        text = self._buffer.decode("utf-8", errors="replace")
                        if text:
                            results.append((True, text))
                        self._buffer.clear()

        return results

    def _parse_parameters(self, params_bytes: bytes) -> List[int]:
        """
        Parse parameter string into list of integers.

        Args:
            params_bytes: Parameter bytes (e.g., b'1;31' or b'')

        Returns:
            List of parameter values
        """
        if not params_bytes:
            return []

        params_str = params_bytes.decode("ascii", errors="ignore")
        parameters = []

        for param in params_str.split(";"):
            if param:
                try:
                    parameters.append(int(param))
                except ValueError:
                    # Invalid parameter, skip
                    logger.debug(f"Invalid ANSI parameter: {param}")

        return parameters

    def format_attributes_to_sgr(self, attributes: Dict[str, Any]) -> bytes:
        """
        Convert text attributes to SGR escape sequence.

        Args:
            attributes: Dictionary of text attributes (bold, color, etc.)

        Returns:
            ANSI escape sequence as bytes

        Example:
            >>> parser = AnsiParser()
            >>> seq = parser.format_attributes_to_sgr({'bold': True, 'fg_color': 31})
            >>> # Returns: b'\x1b[1;31m'
        """
        params = []

        if attributes.get("reset"):
            params.append(0)

        if attributes.get("bold"):
            params.append(1)
        elif attributes.get("bold") is False:
            params.append(22)

        if attributes.get("italic"):
            params.append(3)
        elif attributes.get("italic") is False:
            params.append(23)

        if attributes.get("underline"):
            params.append(4)
        elif attributes.get("underline") is False:
            params.append(24)

        if "fg_color" in attributes:
            params.append(attributes["fg_color"])

        if "bg_color" in attributes:
            params.append(attributes["bg_color"])

        if not params:
            return b""

        param_str = ";".join(str(p) for p in params)
        return f"\x1b[{param_str}m".encode("ascii")

    def strip_ansi_codes(self, text: str) -> str:
        """
        Remove all ANSI escape codes from text.

        Args:
            text: Text possibly containing ANSI codes

        Returns:
            Plain text with all ANSI codes removed

        Example:
            >>> parser = AnsiParser()
            >>> plain = parser.strip_ansi_codes('\x1b[31mRed text\x1b[0m')
            >>> # Returns: 'Red text'
        """
        # Remove CSI sequences
        text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
        # Remove OSC sequences
        text = re.sub(r"\x1b\][0-9]+;[^\x07\x1b]*(?:\x07|\x1b\\)", "", text)
        # Remove simple escape sequences
        text = re.sub(r"\x1b[78DMc]", "", text)

        return text
