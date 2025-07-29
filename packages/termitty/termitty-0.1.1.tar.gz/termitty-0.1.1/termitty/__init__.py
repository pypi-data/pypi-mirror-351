"""
Termitty - A Selenium-inspired Python framework for terminal and SSH automation.

This package provides a high-level interface for automating terminal interactions,
similar to how Selenium WebDriver automates web browsers. It handles SSH connections,
command execution, output parsing, and interactive terminal sessions.

Basic usage:
    from termitty import TermittySession
    
    with TermittySession() as session:
        session.connect('example.com', username='user')
        result = session.execute('ls -la')
        print(result.output)
"""

__version__ = "0.1.1"
__author__ = "Termitty Contributors"
__email__ = "your.email@example.com"
__license__ = "MIT"

# Import main classes for easier access
# This allows: from termitty import TermittySession
# Instead of: from termitty.session.session import TermittySession

from .session.session import TermittySession, OutputContains, OutputMatches, PromptReady
from .transport.base import CommandResult
from .core.exceptions import (
    TermittyException,
    ConnectionException,
    AuthenticationException,
    TimeoutException,
    CommandExecutionException,
    ElementNotFoundException,
    SessionStateException,
)
from .core.config import config
from .terminal.virtual_terminal import VirtualTerminal
from .terminal.screen_buffer import ScreenBuffer
from .interactive.shell import InteractiveShell
from .interactive.key_codes import KeyCodes, SpecialKeys
from .recording.recorder import SessionRecorder
from .recording.player import SessionPlayer, PlaybackSpeed
from .recording.storage import RecordingStorage

# Define what should be imported with "from termitty import *"
__all__ = [
    # Main session class
    'TermittySession',
    
    # Interactive shell
    'InteractiveShell',
    'KeyCodes',
    'SpecialKeys',
    
    # Recording
    'SessionRecorder',
    'SessionPlayer',
    'PlaybackSpeed',
    'RecordingStorage',
    
    # Wait conditions
    'OutputContains',
    'OutputMatches', 
    'PromptReady',
    
    # Result types
    'CommandResult',
    
    # Exceptions
    'TermittyException',
    'ConnectionException',
    'AuthenticationException',
    'TimeoutException',
    'CommandExecutionException',
    'ElementNotFoundException',
    'SessionStateException',
    
    # Configuration
    'config',
    
    # Terminal emulation
    'VirtualTerminal',
    'ScreenBuffer',
]

# Logging setup
import logging

# Create a logger for the entire termitty package
logger = logging.getLogger(__name__)

# By default, we'll only show warnings and above
logger.setLevel(logging.WARNING)

# Create a null handler to prevent "No handlers found" warnings
logger.addHandler(logging.NullHandler())

# Version check
import sys
if sys.version_info < (3, 8):
    raise ImportError("Termitty requires Python 3.8 or higher")