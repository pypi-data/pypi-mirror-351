"""
Pattern matching for interactive shell sessions.

This module provides pattern matching capabilities for detecting prompts,
command completion, and other interactive elements in shell sessions.
"""

import re
import time
from typing import List, Pattern, Union, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns to match."""
    PROMPT = "prompt"
    PASSWORD = "password"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    SUCCESS = "success"
    CUSTOM = "custom"


@dataclass
class PatternMatch:
    """Result of a pattern match."""
    pattern_type: PatternType
    matched_text: str
    pattern: Union[str, Pattern]
    position: int
    line: Optional[str] = None
    
    def __str__(self):
        return f"{self.pattern_type.value}: {self.matched_text}"


class ShellPatterns:
    """Common patterns for shell interaction."""
    
    # Common shell prompts
    BASH_PROMPT = re.compile(r'[\$#]\s*$')
    ZSH_PROMPT = re.compile(r'[%#]\s*$')
    GENERAL_PROMPT = re.compile(r'[$#>%]\s*$')
    
    # Password prompts
    PASSWORD_PROMPTS = [
        re.compile(r'password[:\s]*$', re.IGNORECASE),
        re.compile(r'pass[:\s]*$', re.IGNORECASE),
        re.compile(r'passphrase[:\s]*$', re.IGNORECASE),
        re.compile(r'\[sudo\]\s+password', re.IGNORECASE),
        re.compile(r'enter\s+password', re.IGNORECASE),
    ]
    
    # Confirmation prompts
    CONFIRMATION_PROMPTS = [
        re.compile(r'\(y/n\)[:\s]*$', re.IGNORECASE),
        re.compile(r'\(yes/no\)[:\s]*$', re.IGNORECASE),
        re.compile(r'continue\s*\?[:\s]*$', re.IGNORECASE),
        re.compile(r'proceed\s*\?[:\s]*$', re.IGNORECASE),
        re.compile(r'are\s+you\s+sure', re.IGNORECASE),
    ]
    
    # Error patterns
    ERROR_PATTERNS = [
        re.compile(r'error:', re.IGNORECASE),
        re.compile(r'failed:', re.IGNORECASE),
        re.compile(r'command not found'),
        re.compile(r'permission denied', re.IGNORECASE),
        re.compile(r'no such file or directory', re.IGNORECASE),
    ]
    
    # Success patterns
    SUCCESS_PATTERNS = [
        re.compile(r'success', re.IGNORECASE),
        re.compile(r'completed?', re.IGNORECASE),
        re.compile(r'done\.?$', re.IGNORECASE),
        re.compile(r'finished', re.IGNORECASE),
    ]
    
    # Program-specific patterns
    VIM_PATTERNS = {
        'normal_mode': re.compile(r'^\s*$'),  # Empty line in vim
        'insert_mode': re.compile(r'-- INSERT --'),
        'visual_mode': re.compile(r'-- VISUAL --'),
        'command_mode': re.compile(r'^:'),
    }
    
    LESS_PATTERNS = {
        'prompt': re.compile(r'^:$'),
        'end': re.compile(r'\(END\)'),
    }
    
    TOP_PATTERNS = {
        'header': re.compile(r'top\s+-\s+\d+:\d+:\d+'),
        'prompt': re.compile(r'^$'),  # Empty line for commands
    }


class PatternMatcher:
    """
    Matches patterns in shell output.
    
    This class provides flexible pattern matching for interactive shells,
    allowing detection of prompts, errors, and other significant patterns.
    """
    
    def __init__(self):
        """Initialize the pattern matcher."""
        self.custom_patterns: List[Tuple[PatternType, Union[str, Pattern]]] = []
        self._last_match_time = 0.0
        self._match_cache = {}
    
    def add_pattern(self, 
                    pattern: Union[str, Pattern],
                    pattern_type: PatternType = PatternType.CUSTOM):
        """
        Add a custom pattern to match.
        
        Args:
            pattern: Regular expression pattern
            pattern_type: Type of pattern
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.custom_patterns.append((pattern_type, pattern))
    
    def find_prompt(self, 
                    text: str,
                    custom_prompts: Optional[List[Union[str, Pattern]]] = None) -> Optional[PatternMatch]:
        """
        Find a shell prompt in text.
        
        Args:
            text: Text to search
            custom_prompts: Additional prompt patterns to check
        
        Returns:
            PatternMatch if found, None otherwise
        """
        # Check custom prompts first
        if custom_prompts:
            for prompt in custom_prompts:
                if isinstance(prompt, str):
                    prompt = re.compile(prompt)
                match = prompt.search(text)
                if match:
                    return PatternMatch(
                        pattern_type=PatternType.PROMPT,
                        matched_text=match.group(0),
                        pattern=prompt,
                        position=match.start()
                    )
        
        # Check standard prompts
        for prompt in [ShellPatterns.BASH_PROMPT, 
                      ShellPatterns.ZSH_PROMPT,
                      ShellPatterns.GENERAL_PROMPT]:
            match = prompt.search(text)
            if match:
                return PatternMatch(
                    pattern_type=PatternType.PROMPT,
                    matched_text=match.group(0),
                    pattern=prompt,
                    position=match.start()
                )
        
        return None
    
    def find_password_prompt(self, text: str) -> Optional[PatternMatch]:
        """
        Find a password prompt in text.
        
        Args:
            text: Text to search
        
        Returns:
            PatternMatch if found, None otherwise
        """
        for pattern in ShellPatterns.PASSWORD_PROMPTS:
            match = pattern.search(text)
            if match:
                return PatternMatch(
                    pattern_type=PatternType.PASSWORD,
                    matched_text=match.group(0),
                    pattern=pattern,
                    position=match.start()
                )
        return None
    
    def find_confirmation(self, text: str) -> Optional[PatternMatch]:
        """
        Find a confirmation prompt in text.
        
        Args:
            text: Text to search
        
        Returns:
            PatternMatch if found, None otherwise
        """
        for pattern in ShellPatterns.CONFIRMATION_PROMPTS:
            match = pattern.search(text)
            if match:
                return PatternMatch(
                    pattern_type=PatternType.CONFIRMATION,
                    matched_text=match.group(0),
                    pattern=pattern,
                    position=match.start()
                )
        return None
    
    def find_error(self, text: str) -> Optional[PatternMatch]:
        """
        Find an error message in text.
        
        Args:
            text: Text to search
        
        Returns:
            PatternMatch if found, None otherwise
        """
        for pattern in ShellPatterns.ERROR_PATTERNS:
            match = pattern.search(text)
            if match:
                return PatternMatch(
                    pattern_type=PatternType.ERROR,
                    matched_text=match.group(0),
                    pattern=pattern,
                    position=match.start()
                )
        return None
    
    def find_all_patterns(self, text: str) -> List[PatternMatch]:
        """
        Find all matching patterns in text.
        
        Args:
            text: Text to search
        
        Returns:
            List of all pattern matches
        """
        matches = []
        
        # Check for prompts
        prompt = self.find_prompt(text)
        if prompt:
            matches.append(prompt)
        
        # Check for password prompts
        password = self.find_password_prompt(text)
        if password:
            matches.append(password)
        
        # Check for confirmations
        confirmation = self.find_confirmation(text)
        if confirmation:
            matches.append(confirmation)
        
        # Check for errors
        error = self.find_error(text)
        if error:
            matches.append(error)
        
        # Check custom patterns
        for pattern_type, pattern in self.custom_patterns:
            match = pattern.search(text)
            if match:
                matches.append(PatternMatch(
                    pattern_type=pattern_type,
                    matched_text=match.group(0),
                    pattern=pattern,
                    position=match.start()
                ))
        
        return matches
    
    def wait_for_pattern(self,
                        get_text_func: Callable[[], str],
                        patterns: List[Union[str, Pattern]],
                        timeout: float = 30.0,
                        poll_interval: float = 0.1) -> Optional[PatternMatch]:
        """
        Wait for any of the given patterns to appear.
        
        Args:
            get_text_func: Function that returns current text
            patterns: List of patterns to wait for
            timeout: Maximum time to wait
            poll_interval: How often to check
        
        Returns:
            First matching pattern, or None if timeout
        """
        # Compile string patterns
        compiled_patterns = []
        for p in patterns:
            if isinstance(p, str):
                compiled_patterns.append(re.compile(p))
            else:
                compiled_patterns.append(p)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            text = get_text_func()
            
            for pattern in compiled_patterns:
                match = pattern.search(text)
                if match:
                    return PatternMatch(
                        pattern_type=PatternType.CUSTOM,
                        matched_text=match.group(0),
                        pattern=pattern,
                        position=match.start()
                    )
            
            time.sleep(poll_interval)
        
        return None
    
    def extract_prompt_line(self, text: str) -> Optional[str]:
        """
        Extract the line containing the prompt.
        
        Args:
            text: Text to search
        
        Returns:
            The line containing the prompt, or None
        """
        lines = text.split('\n')
        
        # Search from bottom up (prompts usually at the end)
        for line in reversed(lines):
            if self.find_prompt(line):
                return line
        
        return None