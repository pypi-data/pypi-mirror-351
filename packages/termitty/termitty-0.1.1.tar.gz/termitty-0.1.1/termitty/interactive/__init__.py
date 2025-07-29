"""
Interactive shell components for Termitty.

This package provides interactive shell session capabilities, allowing
real-time interaction with terminal programs like vim, top, interactive
installers, and maintaining persistent shell sessions.

Phase 3 additions that enable:
- Persistent shell sessions with state
- Real-time I/O with running programs
- Special key support (Ctrl+C, ESC, Tab, etc.)
- PTY (pseudo-terminal) for full terminal emulation
- Interactive program automation (vim, nano, top, etc.)
"""

from .shell import InteractiveShell
from .key_codes import KeyCodes, SpecialKeys
from .io_handler import IOHandler
from .patterns import ShellPatterns, PatternMatcher

__all__ = [
    'InteractiveShell',
    'KeyCodes',
    'SpecialKeys',
    'IOHandler',
    'ShellPatterns',
    'PatternMatcher',
]