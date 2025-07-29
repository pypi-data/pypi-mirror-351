"""
Key codes and special key handling for interactive shells.

This module defines the special key sequences needed for terminal interaction,
including control characters, escape sequences, and function keys.
"""

from enum import Enum
from typing import Dict, Union


class SpecialKeys(Enum):
    """Common special keys used in terminal interaction."""
    
    # Control keys (Ctrl+letter)
    CTRL_A = '\x01'  # Start of line
    CTRL_B = '\x02'  # Back one character
    CTRL_C = '\x03'  # Interrupt (SIGINT)
    CTRL_D = '\x04'  # EOF/logout
    CTRL_E = '\x05'  # End of line
    CTRL_F = '\x06'  # Forward one character
    CTRL_G = '\x07'  # Bell
    CTRL_H = '\x08'  # Backspace
    CTRL_I = '\x09'  # Tab
    CTRL_J = '\x0a'  # Line feed (Enter)
    CTRL_K = '\x0b'  # Kill line
    CTRL_L = '\x0c'  # Clear screen
    CTRL_M = '\x0d'  # Carriage return
    CTRL_N = '\x0e'  # Next history
    CTRL_O = '\x0f'  # Execute command
    CTRL_P = '\x10'  # Previous history
    CTRL_Q = '\x11'  # Resume transmission (XON)
    CTRL_R = '\x12'  # Reverse search
    CTRL_S = '\x13'  # Pause transmission (XOFF)
    CTRL_T = '\x14'  # Transpose characters
    CTRL_U = '\x15'  # Kill line backward
    CTRL_V = '\x16'  # Literal next
    CTRL_W = '\x17'  # Kill word backward
    CTRL_X = '\x18'  # Command prefix
    CTRL_Y = '\x19'  # Yank
    CTRL_Z = '\x1a'  # Suspend (SIGTSTP)
    
    # Other special characters
    ESCAPE = '\x1b'  # ESC key
    DELETE = '\x7f'  # Delete key
    
    # Common key combinations
    TAB = CTRL_I
    ENTER = CTRL_J
    RETURN = CTRL_M
    BACKSPACE = CTRL_H
    
    # Arrow keys (ANSI escape sequences)
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    RIGHT = '\x1b[C'
    LEFT = '\x1b[D'
    
    # Function keys
    F1 = '\x1bOP'
    F2 = '\x1bOQ'
    F3 = '\x1bOR'
    F4 = '\x1bOS'
    F5 = '\x1b[15~'
    F6 = '\x1b[17~'
    F7 = '\x1b[18~'
    F8 = '\x1b[19~'
    F9 = '\x1b[20~'
    F10 = '\x1b[21~'
    F11 = '\x1b[23~'
    F12 = '\x1b[24~'
    
    # Navigation keys
    HOME = '\x1b[H'
    END = '\x1b[F'
    PAGE_UP = '\x1b[5~'
    PAGE_DOWN = '\x1b[6~'
    INSERT = '\x1b[2~'
    DELETE_FORWARD = '\x1b[3~'


class KeyCodes:
    """Utility class for working with key codes and sequences."""
    
    # Mapping of common key names to their codes
    KEY_NAMES: Dict[str, str] = {
        # Control keys
        'ctrl+a': SpecialKeys.CTRL_A.value,
        'ctrl+b': SpecialKeys.CTRL_B.value,
        'ctrl+c': SpecialKeys.CTRL_C.value,
        'ctrl+d': SpecialKeys.CTRL_D.value,
        'ctrl+e': SpecialKeys.CTRL_E.value,
        'ctrl+f': SpecialKeys.CTRL_F.value,
        'ctrl+g': SpecialKeys.CTRL_G.value,
        'ctrl+h': SpecialKeys.CTRL_H.value,
        'ctrl+i': SpecialKeys.CTRL_I.value,
        'ctrl+j': SpecialKeys.CTRL_J.value,
        'ctrl+k': SpecialKeys.CTRL_K.value,
        'ctrl+l': SpecialKeys.CTRL_L.value,
        'ctrl+m': SpecialKeys.CTRL_M.value,
        'ctrl+n': SpecialKeys.CTRL_N.value,
        'ctrl+o': SpecialKeys.CTRL_O.value,
        'ctrl+p': SpecialKeys.CTRL_P.value,
        'ctrl+q': SpecialKeys.CTRL_Q.value,
        'ctrl+r': SpecialKeys.CTRL_R.value,
        'ctrl+s': SpecialKeys.CTRL_S.value,
        'ctrl+t': SpecialKeys.CTRL_T.value,
        'ctrl+u': SpecialKeys.CTRL_U.value,
        'ctrl+v': SpecialKeys.CTRL_V.value,
        'ctrl+w': SpecialKeys.CTRL_W.value,
        'ctrl+x': SpecialKeys.CTRL_X.value,
        'ctrl+y': SpecialKeys.CTRL_Y.value,
        'ctrl+z': SpecialKeys.CTRL_Z.value,
        
        # Common names
        'esc': SpecialKeys.ESCAPE.value,
        'escape': SpecialKeys.ESCAPE.value,
        'tab': SpecialKeys.TAB.value,
        'enter': SpecialKeys.ENTER.value,
        'return': SpecialKeys.RETURN.value,
        'backspace': SpecialKeys.BACKSPACE.value,
        'delete': SpecialKeys.DELETE.value,
        'del': SpecialKeys.DELETE.value,
        
        # Arrow keys
        'up': SpecialKeys.UP.value,
        'down': SpecialKeys.DOWN.value,
        'left': SpecialKeys.LEFT.value,
        'right': SpecialKeys.RIGHT.value,
        
        # Navigation
        'home': SpecialKeys.HOME.value,
        'end': SpecialKeys.END.value,
        'pageup': SpecialKeys.PAGE_UP.value,
        'pagedown': SpecialKeys.PAGE_DOWN.value,
        'insert': SpecialKeys.INSERT.value,
        
        # Function keys
        'f1': SpecialKeys.F1.value,
        'f2': SpecialKeys.F2.value,
        'f3': SpecialKeys.F3.value,
        'f4': SpecialKeys.F4.value,
        'f5': SpecialKeys.F5.value,
        'f6': SpecialKeys.F6.value,
        'f7': SpecialKeys.F7.value,
        'f8': SpecialKeys.F8.value,
        'f9': SpecialKeys.F9.value,
        'f10': SpecialKeys.F10.value,
        'f11': SpecialKeys.F11.value,
        'f12': SpecialKeys.F12.value,
    }
    
    @classmethod
    def get_key_code(cls, key_name: str) -> str:
        """
        Get the key code for a given key name.
        
        Args:
            key_name: Name of the key (e.g., 'ctrl+c', 'escape', 'enter')
        
        Returns:
            The key code sequence
        
        Raises:
            ValueError: If key name is not recognized
        
        Example:
            >>> KeyCodes.get_key_code('ctrl+c')
            '\\x03'
            >>> KeyCodes.get_key_code('escape')
            '\\x1b'
        """
        normalized = key_name.lower().replace(' ', '').replace('-', '+')
        if normalized in cls.KEY_NAMES:
            return cls.KEY_NAMES[normalized]
        else:
            raise ValueError(f"Unknown key name: {key_name}")
    
    @classmethod
    def create_ctrl_key(cls, letter: str) -> str:
        """
        Create a control key sequence for a given letter.
        
        Args:
            letter: Single letter (a-z)
        
        Returns:
            Control key sequence
        
        Example:
            >>> KeyCodes.create_ctrl_key('c')
            '\\x03'
        """
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError("Must provide a single letter")
        
        # Convert to uppercase and get ASCII value
        ascii_val = ord(letter.upper())
        # Control keys are ASCII value - 64
        ctrl_val = ascii_val - 64
        return chr(ctrl_val)
    
    @classmethod
    def is_printable(cls, char: str) -> bool:
        """
        Check if a character is printable (not a control character).
        
        Args:
            char: Character to check
        
        Returns:
            True if printable, False otherwise
        """
        if not char:
            return False
        
        code = ord(char[0])
        # Printable ASCII range is 32-126
        return 32 <= code <= 126
    
    @classmethod
    def format_key_sequence(cls, sequence: Union[str, bytes]) -> str:
        """
        Format a key sequence for display.
        
        Args:
            sequence: Key sequence to format
        
        Returns:
            Human-readable representation
        
        Example:
            >>> KeyCodes.format_key_sequence('\\x03')
            '^C'
            >>> KeyCodes.format_key_sequence('\\x1b[A')
            '<Up>'
        """
        if isinstance(sequence, bytes):
            sequence = sequence.decode('utf-8', errors='replace')
        
        # Check for known sequences
        for name, code in cls.KEY_NAMES.items():
            if code == sequence:
                if name.startswith('ctrl+'):
                    return f"^{name[5:].upper()}"
                else:
                    return f"<{name.capitalize()}>"
        
        # Format unknown control characters
        if sequence and ord(sequence[0]) < 32:
            return f"^{chr(ord(sequence[0]) + 64)}"
        
        return repr(sequence)