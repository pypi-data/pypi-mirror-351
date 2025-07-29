"""
Terminal emulation components for Termitty.

This package provides terminal emulation capabilities, including:
- Virtual terminal that maintains screen state
- ANSI escape code parsing and interpretation
- Cursor tracking and screen buffer management
- Color and formatting support

The terminal emulator allows Termitty to understand not just what text
was output, but how it would appear on screen, enabling intelligent
interaction with terminal-based user interfaces.
"""

from .ansi_parser import AnsiCode, AnsiParser
from .screen_buffer import Cell, ScreenBuffer
from .virtual_terminal import VirtualTerminal

__all__ = [
    "VirtualTerminal",
    "AnsiParser",
    "AnsiCode",
    "ScreenBuffer",
    "Cell",
]
