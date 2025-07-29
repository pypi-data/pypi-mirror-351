"""
Termitty exception hierarchy.

This module defines all custom exceptions used throughout Termitty. Having a
well-organized exception hierarchy helps users handle errors appropriately
and provides clear information about what went wrong.

The exception hierarchy mirrors Selenium's approach where possible, making it
familiar to developers who have used Selenium WebDriver.
"""

class TermittyException(Exception):
    """
    Base exception for all Termitty-related errors.
    
    This is the root of our exception hierarchy. Users can catch this
    to handle any Termitty error, though catching more specific exceptions
    is usually better.
    """
    pass


class ConnectionException(TermittyException):
    """
    Raised when there are issues establishing or maintaining SSH connections.
    
    This could be due to network issues, authentication failures, or the
    remote host being unavailable.
    """
    pass


class AuthenticationException(ConnectionException):
    """
    Raised when SSH authentication fails.
    
    This is a specific type of ConnectionException that occurs when
    credentials are invalid or authentication methods fail.
    """
    
    def __init__(self, message: str, tried_methods: list = None):
        super().__init__(message)
        self.tried_methods = tried_methods or []
    
    def __str__(self):
        base_msg = super().__str__()
        if self.tried_methods:
            return f"{base_msg} (tried methods: {', '.join(self.tried_methods)})"
        return base_msg


class TimeoutException(TermittyException):
    """
    Raised when operations exceed their allowed time.
    
    Similar to Selenium's TimeoutException, this occurs when waiting for
    conditions, command execution, or connection attempts take too long.
    """
    
    def __init__(self, message: str, timeout: float = None):
        super().__init__(message)
        self.timeout = timeout
    
    def __str__(self):
        base_msg = super().__str__()
        if self.timeout:
            return f"{base_msg} (timeout: {self.timeout}s)"
        return base_msg


class CommandExecutionException(TermittyException):
    """
    Raised when command execution fails.
    
    This doesn't mean the command returned a non-zero exit code (that's
    normal and expected). This is for actual execution failures.
    """
    
    def __init__(self, message: str, command: str = None, exit_code: int = None):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code
    
    def __str__(self):
        parts = [super().__str__()]
        if self.command:
            parts.append(f"Command: {self.command}")
        if self.exit_code is not None:
            parts.append(f"Exit code: {self.exit_code}")
        return " | ".join(parts)


class ElementNotFoundException(TermittyException):
    """
    Raised when a terminal element (prompt, pattern, etc.) cannot be found.
    
    This mirrors Selenium's NoSuchElementException and occurs when searching
    for specific patterns or prompts in terminal output fails.
    """
    
    def __init__(self, message: str, pattern: str = None):
        super().__init__(message)
        self.pattern = pattern
    
    def __str__(self):
        base_msg = super().__str__()
        if self.pattern:
            return f"{base_msg} (pattern: {self.pattern})"
        return base_msg


class SessionStateException(TermittyException):
    """
    Raised when operations are attempted on sessions in invalid states.
    
    For example, trying to execute commands on a disconnected session
    or attempting to connect an already connected session.
    """
    pass


class TerminalParsingException(TermittyException):
    """
    Raised when terminal output cannot be parsed correctly.
    
    This might occur with malformed ANSI escape sequences or
    unexpected terminal behavior.
    """
    pass


class UnsupportedOperationException(TermittyException):
    """
    Raised when an operation is not supported in the current context.
    
    For example, certain terminal operations might not be available
    on all systems or terminal types.
    """
    pass