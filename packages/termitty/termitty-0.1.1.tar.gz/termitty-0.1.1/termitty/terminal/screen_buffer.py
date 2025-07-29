"""
Screen buffer implementation for terminal emulation.

The screen buffer maintains a 2D grid of cells representing the terminal
display. Each cell contains a character and its attributes (color, bold, etc.).
This allows us to track exactly what the terminal screen looks like at any
point in time.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union, Pattern

logger = logging.getLogger(__name__)


@dataclass
class CellAttributes:
    """Attributes for a single terminal cell."""

    # Foreground color (ANSI color code or RGB)
    fg_color: Optional[int] = None
    # Background color (ANSI color code or RGB)
    bg_color: Optional[int] = None
    # Text styling
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    dim: bool = False
    reverse: bool = False
    hidden: bool = False

    def copy(self) -> "CellAttributes":
        """Create a copy of these attributes."""
        return CellAttributes(
            fg_color=self.fg_color,
            bg_color=self.bg_color,
            bold=self.bold,
            italic=self.italic,
            underline=self.underline,
            strikethrough=self.strikethrough,
            dim=self.dim,
            reverse=self.reverse,
            hidden=self.hidden,
        )

    def reset(self):
        """Reset all attributes to defaults."""
        self.fg_color = None
        self.bg_color = None
        self.bold = False
        self.italic = False
        self.underline = False
        self.strikethrough = False
        self.dim = False
        self.reverse = False
        self.hidden = False

    def apply_sgr(self, params: List[int]):
        """
        Apply SGR (Select Graphic Rendition) parameters.

        Args:
            params: List of SGR parameter codes
        """
        i = 0
        while i < len(params):
            param = params[i]

            if param == 0:  # Reset all
                self.reset()
            elif param == 1:  # Bold
                self.bold = True
            elif param == 2:  # Dim
                self.dim = True
            elif param == 3:  # Italic
                self.italic = True
            elif param == 4:  # Underline
                self.underline = True
            elif param == 7:  # Reverse
                self.reverse = True
            elif param == 8:  # Hidden
                self.hidden = True
            elif param == 9:  # Strikethrough
                self.strikethrough = True
            elif param == 22:  # Normal intensity (not bold/dim)
                self.bold = False
                self.dim = False
            elif param == 23:  # Not italic
                self.italic = False
            elif param == 24:  # Not underlined
                self.underline = False
            elif param == 27:  # Not reversed
                self.reverse = False
            elif param == 28:  # Not hidden
                self.hidden = False
            elif param == 29:  # Not strikethrough
                self.strikethrough = False
            elif 30 <= param <= 37:  # Foreground color
                self.fg_color = param
            elif param == 39:  # Default foreground
                self.fg_color = None
            elif 40 <= param <= 47:  # Background color
                self.bg_color = param
            elif param == 49:  # Default background
                self.bg_color = None
            elif 90 <= param <= 97:  # Bright foreground color
                self.fg_color = param
            elif 100 <= param <= 107:  # Bright background color
                self.bg_color = param
            elif param == 38 and i + 2 < len(params):
                # Extended foreground color
                if params[i + 1] == 5 and i + 2 < len(params):
                    # 256-color mode
                    self.fg_color = 256 + params[i + 2]
                    i += 2
                elif params[i + 1] == 2 and i + 4 < len(params):
                    # RGB mode (store as negative to distinguish)
                    r, g, b = params[i + 2], params[i + 3], params[i + 4]
                    self.fg_color = -(r * 65536 + g * 256 + b)
                    i += 4
            elif param == 48 and i + 2 < len(params):
                # Extended background color
                if params[i + 1] == 5 and i + 2 < len(params):
                    # 256-color mode
                    self.bg_color = 256 + params[i + 2]
                    i += 2
                elif params[i + 1] == 2 and i + 4 < len(params):
                    # RGB mode (store as negative to distinguish)
                    r, g, b = params[i + 2], params[i + 3], params[i + 4]
                    self.bg_color = -(r * 65536 + g * 256 + b)
                    i += 4

            i += 1


@dataclass
class Cell:
    """A single cell in the terminal screen buffer."""

    char: str = " "
    attributes: CellAttributes = field(default_factory=CellAttributes)

    def copy(self) -> "Cell":
        """Create a copy of this cell."""
        return Cell(char=self.char, attributes=self.attributes.copy())

    def clear(self):
        """Clear this cell to default state."""
        self.char = " "
        self.attributes.reset()


class ScreenBuffer:
    """
    Terminal screen buffer that maintains the display state.

    This class represents the visible terminal as a 2D grid of cells.
    It handles cursor movement, text insertion, scrolling, and all the
    operations needed to maintain an accurate representation of the
    terminal display.
    """

    def __init__(self, width: int = 80, height: int = 24):
        """
        Initialize screen buffer with given dimensions.

        Args:
            width: Number of columns
            height: Number of rows
        """
        self.width = width
        self.height = height

        # Initialize the screen buffer
        self._buffer: List[List[Cell]] = []
        for _ in range(height):
            row = [Cell() for _ in range(width)]
            self._buffer.append(row)

        # Cursor position (0-indexed)
        self.cursor_x = 0
        self.cursor_y = 0

        # Saved cursor position (for save/restore operations)
        self._saved_cursor_x = 0
        self._saved_cursor_y = 0

        # Current text attributes for new characters
        self.current_attributes = CellAttributes()

        # Scrolling region (default is entire screen)
        self.scroll_top = 0
        self.scroll_bottom = height - 1

        # Line wrap mode
        self.wrap_mode = True
        
        # Pending wrap state - cursor is at end of line but hasn't wrapped yet
        self._pending_wrap = False

        # Keep track of dirty regions for optimization
        self._dirty_lines = set()

    def write_char(self, char: str):
        """
        Write a single character at the cursor position.

        Args:
            char: Character to write
        """
        # Handle pending wrap from previous character
        if self._pending_wrap and char not in ["\n", "\r"]:
            if self.wrap_mode:
                self.cursor_x = 0
                self._line_feed()
            self._pending_wrap = False
            
        if char == "\n":
            self.cursor_x = 0
            self._line_feed()
            self._pending_wrap = False
        elif char == "\r":
            self.cursor_x = 0
            self._pending_wrap = False
        elif char == "\b":  # Backspace
            if self.cursor_x > 0:
                self.cursor_x -= 1
            self._pending_wrap = False
        elif char == "\t":  # Tab
            # Move to next tab stop (every 8 columns)
            self.cursor_x = min((self.cursor_x // 8 + 1) * 8, self.width - 1)
            self._pending_wrap = False
        else:
            # Normal character
            if 0 <= self.cursor_y < self.height and 0 <= self.cursor_x < self.width:
                cell = self._buffer[self.cursor_y][self.cursor_x]
                cell.char = char
                cell.attributes = self.current_attributes.copy()
                self._dirty_lines.add(self.cursor_y)

                # Advance cursor
                self.cursor_x += 1

                # Check if we need to set pending wrap
                if self.cursor_x >= self.width:
                    if self.wrap_mode:
                        # Cursor can be at width (one past last column) when at line end
                        self._pending_wrap = True
                    else:
                        self.cursor_x = self.width - 1
                        self._pending_wrap = False
                else:
                    self._pending_wrap = False

    def write_string(self, text: str):
        """
        Write a string of characters.

        Args:
            text: String to write
        """
        for char in text:
            self.write_char(char)

    def move_cursor(self, x: int, y: int):
        """
        Move cursor to absolute position.

        Args:
            x: Column (0-indexed)
            y: Row (0-indexed)
        """
        self.cursor_x = max(0, min(x, self.width - 1))
        self.cursor_y = max(0, min(y, self.height - 1))

    def move_cursor_relative(self, dx: int, dy: int):
        """
        Move cursor relative to current position.

        Args:
            dx: Columns to move (negative for left)
            dy: Rows to move (negative for up)
        """
        self.move_cursor(self.cursor_x + dx, self.cursor_y + dy)

    def save_cursor(self):
        """Save current cursor position."""
        self._saved_cursor_x = self.cursor_x
        self._saved_cursor_y = self.cursor_y

    def restore_cursor(self):
        """Restore saved cursor position."""
        self.cursor_x = self._saved_cursor_x
        self.cursor_y = self._saved_cursor_y

    def erase_line(self, mode: int = 0):
        """
        Erase line based on mode.

        Args:
            mode: 0 = cursor to end, 1 = start to cursor, 2 = entire line
        """
        if 0 <= self.cursor_y < self.height:
            if mode == 0:  # Cursor to end of line
                for x in range(self.cursor_x, self.width):
                    self._buffer[self.cursor_y][x].clear()
            elif mode == 1:  # Start of line to cursor
                for x in range(0, self.cursor_x + 1):
                    self._buffer[self.cursor_y][x].clear()
            elif mode == 2:  # Entire line
                for x in range(self.width):
                    self._buffer[self.cursor_y][x].clear()

            self._dirty_lines.add(self.cursor_y)

    def erase_display(self, mode: int = 0):
        """
        Erase display based on mode.

        Args:
            mode: 0 = cursor to end, 1 = start to cursor, 2 = entire display
        """
        if mode == 0:  # Cursor to end of display
            # Erase from cursor to end of current line
            self.erase_line(0)
            # Erase all lines below
            for y in range(self.cursor_y + 1, self.height):
                for x in range(self.width):
                    self._buffer[y][x].clear()
                self._dirty_lines.add(y)

        elif mode == 1:  # Start to cursor
            # Erase all lines above
            for y in range(0, self.cursor_y):
                for x in range(self.width):
                    self._buffer[y][x].clear()
                self._dirty_lines.add(y)
            # Erase from start of line to cursor
            self.erase_line(1)

        elif mode == 2:  # Entire display
            self.clear()

    def clear(self):
        """Clear entire screen and reset cursor."""
        for y in range(self.height):
            for x in range(self.width):
                self._buffer[y][x].clear()
            self._dirty_lines.add(y)

        self.cursor_x = 0
        self.cursor_y = 0

    def scroll_up(self, lines: int = 1):
        """
        Scroll content up by specified lines.

        Args:
            lines: Number of lines to scroll
        """
        if lines <= 0:
            return

        # Remove lines from top of scrolling region
        for _ in range(min(lines, self.scroll_bottom - self.scroll_top + 1)):
            self._buffer.pop(self.scroll_top)
            # Add new line at bottom of scrolling region
            new_line = [Cell() for _ in range(self.width)]
            self._buffer.insert(self.scroll_bottom, new_line)

        # Mark all lines in scrolling region as dirty
        for y in range(self.scroll_top, self.scroll_bottom + 1):
            self._dirty_lines.add(y)

    def get_line(self, y: int) -> str:
        """
        Get text content of a specific line.

        Args:
            y: Line number (0-indexed)

        Returns:
            Text content of the line
        """
        if 0 <= y < self.height:
            return "".join(cell.char for cell in self._buffer[y])
        return ""

    def get_line_with_attributes(self, y: int) -> List[Tuple[str, CellAttributes]]:
        """
        Get line content with attributes.

        Args:
            y: Line number (0-indexed)

        Returns:
            List of (char, attributes) tuples
        """
        if 0 <= y < self.height:
            return [(cell.char, cell.attributes.copy()) for cell in self._buffer[y]]
        return []

    def get_text(
        self,
        start_y: int = 0,
        start_x: int = 0,
        end_y: Optional[int] = None,
        end_x: Optional[int] = None,
    ) -> str:
        """
        Get text content from buffer region.

        Args:
            start_y: Starting row
            start_x: Starting column
            end_y: Ending row (inclusive, None for last row)
            end_x: Ending column (inclusive, None for last column)

        Returns:
            Text content of the region
        """
        if end_y is None:
            end_y = self.height - 1
        if end_x is None:
            end_x = self.width - 1

        lines = []
        for y in range(start_y, min(end_y + 1, self.height)):
            if y == start_y and y == end_y:
                # Single line
                line = "".join(
                    self._buffer[y][x].char
                    for x in range(start_x, min(end_x + 1, self.width))
                )
            elif y == start_y:
                # First line
                line = "".join(
                    self._buffer[y][x].char for x in range(start_x, self.width)
                )
            elif y == end_y:
                # Last line
                line = "".join(
                    self._buffer[y][x].char
                    for x in range(0, min(end_x + 1, self.width))
                )
            else:
                # Middle lines
                line = self.get_line(y)

            lines.append(line.rstrip())

        return "\n".join(lines)

    def find_text(self, pattern: Union[str, Pattern], regex: bool = False) -> List[Tuple[int, int]]:
        """
        Find text in the buffer with improved matching.

        This method handles various corner cases:
        - Text split across multiple lines
        - Text with extra spaces
        - Text at any position on the screen
        - Case-sensitive and case-insensitive searches

        Args:
            pattern: Text or regex pattern to find
            regex: Whether pattern is a regular expression

        Returns:
            List of (y, x) positions where pattern starts
        """
        positions = []
        
        # First, try to find in individual lines
        for y in range(self.height):
            line = self.get_line(y)
            
            if regex:
                if isinstance(pattern, str):
                    pattern_obj = re.compile(pattern)
                else:
                    pattern_obj = pattern
                    
                for match in pattern_obj.finditer(line):
                    positions.append((y, match.start()))
            else:
                # Simple string search
                search_text = str(pattern)
                
                # Try exact match first
                start = 0
                while True:
                    pos = line.find(search_text, start)
                    if pos == -1:
                        break
                    positions.append((y, pos))
                    start = pos + 1
                
                # Try with normalized spaces
                normalized_line = ' '.join(line.split())
                normalized_search = ' '.join(search_text.split())
                if normalized_search in normalized_line and not positions:
                    # Find the approximate position
                    pos = normalized_line.find(normalized_search)
                    if pos != -1:
                        positions.append((y, pos))
        
        # If not found in single lines, try searching across lines
        if not positions and not regex:
            search_text = str(pattern)
            
            # Get all screen text
            full_text = self.get_text()
            
            # Try to find the text anywhere
            if search_text in full_text:
                # Find all occurrences in the full text
                start = 0
                while True:
                    pos = full_text.find(search_text, start)
                    if pos == -1:
                        break
                    
                    # Convert position in full text to (y, x) coordinates
                    lines_before = full_text[:pos].count('\n')
                    if lines_before == 0:
                        x_pos = pos
                    else:
                        last_newline = full_text[:pos].rfind('\n')
                        x_pos = pos - last_newline - 1
                    
                    positions.append((lines_before, x_pos))
                    start = pos + 1
            
            # Also try with normalized spaces across the entire screen
            if not positions:
                normalized_full = ' '.join(full_text.split())
                normalized_search = ' '.join(search_text.split())
                
                if normalized_search in normalized_full:
                    # This is harder to map back to exact positions,
                    # so we'll do a line-by-line search with fuzzy matching
                    search_words = search_text.split()
                    
                    for y in range(self.height):
                        line = self.get_line(y)
                        line_words = line.split()
                        
                        # Try to find the start of the word sequence
                        for i in range(len(line_words) - len(search_words) + 1):
                            if line_words[i:i+len(search_words)] == search_words:
                                # Found a match, estimate position
                                x_pos = line.find(line_words[i])
                                if x_pos != -1:
                                    positions.append((y, x_pos))
                                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_positions = []
        for pos in positions:
            if pos not in seen:
                seen.add(pos)
                unique_positions.append(pos)
        
        return unique_positions

    def _line_feed(self):
        """Handle line feed (move cursor down, possibly scroll)."""
        self.cursor_y += 1

        # Check if we need to scroll
        if self.cursor_y > self.scroll_bottom:
            self.cursor_y = self.scroll_bottom
            self.scroll_up(1)

    def resize(self, width: int, height: int):
        """
        Resize the terminal buffer.

        Args:
            width: New width
            height: New height
        """
        old_width = self.width
        old_height = self.height

        self.width = width
        self.height = height

        # Resize existing lines
        for y in range(min(old_height, height)):
            row = self._buffer[y]
            if width > old_width:
                # Extend line
                row.extend([Cell() for _ in range(width - old_width)])
            elif width < old_width:
                # Truncate line
                self._buffer[y] = row[:width]

        # Add or remove rows
        if height > old_height:
            # Add new rows
            for _ in range(height - old_height):
                self._buffer.append([Cell() for _ in range(width)])
        elif height < old_height:
            # Remove extra rows
            self._buffer = self._buffer[:height]

        # Adjust cursor position
        self.cursor_x = min(self.cursor_x, width - 1)
        self.cursor_y = min(self.cursor_y, height - 1)

        # Adjust scrolling region
        self.scroll_bottom = min(self.scroll_bottom, height - 1)

        # Mark everything as dirty
        self._dirty_lines = set(range(height))

    def __str__(self) -> str:
        """Get string representation of the entire buffer."""
        return self.get_text()