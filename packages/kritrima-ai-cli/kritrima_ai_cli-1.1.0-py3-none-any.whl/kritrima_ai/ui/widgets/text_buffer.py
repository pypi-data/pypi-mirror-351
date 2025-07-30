"""
Advanced text buffer implementation for multi-line text editing.

This module provides a sophisticated text buffer with:
- Multi-line text editing capabilities
- Undo/redo system with stack management
- Viewport management and scrolling
- Unicode character support
- Cursor positioning and movement
- Text manipulation operations
- Emacs-style keyboard shortcuts
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from rich.syntax import Syntax
from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.widget import Widget

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class CursorMovement(Enum):
    """Cursor movement directions."""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    HOME = "home"
    END = "end"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"
    WORD_LEFT = "word_left"
    WORD_RIGHT = "word_right"


@dataclass
class UndoState:
    """State for undo/redo operations."""

    lines: List[str]
    cursor_row: int
    cursor_col: int
    description: str = ""
    timestamp: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class Selection:
    """Text selection state."""

    start_row: int
    start_col: int
    end_row: int
    end_col: int

    def normalize(self) -> "Selection":
        """Normalize selection so start is before end."""
        if self.start_row > self.end_row or (
            self.start_row == self.end_row and self.start_col > self.end_col
        ):
            return Selection(
                start_row=self.end_row,
                start_col=self.end_col,
                end_row=self.start_row,
                end_col=self.start_col,
            )
        return self

    def is_empty(self) -> bool:
        """Check if selection is empty."""
        return self.start_row == self.end_row and self.start_col == self.end_col


class TextBuffer:
    """
    Advanced text buffer for multi-line editing.

    Provides comprehensive text editing capabilities with undo/redo,
    Unicode support, and sophisticated cursor management.
    """

    def __init__(self, initial_text: str = "", max_undo_levels: int = 100):
        """
        Initialize text buffer.

        Args:
            initial_text: Initial text content
            max_undo_levels: Maximum undo history levels
        """
        self.lines: List[str] = initial_text.split("\n") if initial_text else [""]
        self.cursor_row = 0
        self.cursor_col = 0
        self.scroll_row = 0
        self.scroll_col = 0
        self.version = 0
        self.max_undo_levels = max_undo_levels

        # Undo/redo system
        self.undo_stack: List[UndoState] = []
        self.redo_stack: List[UndoState] = []

        # Selection state
        self.selection: Optional[Selection] = None
        self.selecting = False

        # Viewport dimensions
        self.viewport_width = 80
        self.viewport_height = 24

        # Text properties
        self.tab_width = 4
        self.auto_indent = True
        self.word_wrap = False

        logger.debug("Text buffer initialized")

    def get_text(self) -> str:
        """Get the complete text content."""
        return "\n".join(self.lines)

    def set_text(self, text: str, description: str = "Set text") -> None:
        """
        Set the entire text content.

        Args:
            text: New text content
            description: Description for undo operation
        """
        self._save_state(description)
        self.lines = text.split("\n") if text else [""]
        self.cursor_row = 0
        self.cursor_col = 0
        self._clamp_cursor()
        self.version += 1

    def insert_text(self, text: str, description: str = "Insert text") -> None:
        """
        Insert text at cursor position.

        Args:
            text: Text to insert
            description: Description for undo operation
        """
        if not text:
            return

        self._save_state(description)

        # Handle newlines in inserted text
        if "\n" in text:
            lines_to_insert = text.split("\n")
            current_line = self.lines[self.cursor_row]

            # Split current line at cursor
            before = current_line[: self.cursor_col]
            after = current_line[self.cursor_col :]

            # Update current line with before + first insert line
            self.lines[self.cursor_row] = before + lines_to_insert[0]

            # Insert middle lines
            for i, line in enumerate(lines_to_insert[1:-1], 1):
                self.lines.insert(self.cursor_row + i, line)

            # Insert last line + after
            if len(lines_to_insert) > 1:
                self.lines.insert(
                    self.cursor_row + len(lines_to_insert) - 1,
                    lines_to_insert[-1] + after,
                )
                self.cursor_row += len(lines_to_insert) - 1
                self.cursor_col = len(lines_to_insert[-1])
            else:
                self.cursor_col += len(text)
        else:
            # Simple text insertion
            current_line = self.lines[self.cursor_row]
            self.lines[self.cursor_row] = (
                current_line[: self.cursor_col] + text + current_line[self.cursor_col :]
            )
            self.cursor_col += len(text)

        self._clamp_cursor()
        self.version += 1

    def delete_char(
        self, direction: int = 1, description: str = "Delete character"
    ) -> None:
        """
        Delete character(s) at cursor.

        Args:
            direction: 1 for forward delete, -1 for backward delete
            description: Description for undo operation
        """
        if self.is_empty():
            return

        self._save_state(description)

        if direction == 1:  # Delete forward
            current_line = self.lines[self.cursor_row]
            if self.cursor_col < len(current_line):
                # Delete character in current line
                self.lines[self.cursor_row] = (
                    current_line[: self.cursor_col]
                    + current_line[self.cursor_col + 1 :]
                )
            elif self.cursor_row < len(self.lines) - 1:
                # Join with next line
                next_line = self.lines[self.cursor_row + 1]
                self.lines[self.cursor_row] = current_line + next_line
                del self.lines[self.cursor_row + 1]
        else:  # Delete backward
            if self.cursor_col > 0:
                # Delete character before cursor
                current_line = self.lines[self.cursor_row]
                self.lines[self.cursor_row] = (
                    current_line[: self.cursor_col - 1]
                    + current_line[self.cursor_col :]
                )
                self.cursor_col -= 1
            elif self.cursor_row > 0:
                # Join with previous line
                prev_line = self.lines[self.cursor_row - 1]
                current_line = self.lines[self.cursor_row]
                self.cursor_col = len(prev_line)
                self.lines[self.cursor_row - 1] = prev_line + current_line
                del self.lines[self.cursor_row]
                self.cursor_row -= 1

        self._clamp_cursor()
        self.version += 1

    def delete_word(self, direction: int = 1, description: str = "Delete word") -> None:
        """
        Delete word at cursor.

        Args:
            direction: 1 for forward, -1 for backward
            description: Description for undo operation
        """
        if direction == 1:
            # Delete forward word
            start_pos = (self.cursor_row, self.cursor_col)
            self.move_cursor_word(direction)
            end_pos = (self.cursor_row, self.cursor_col)
            self._delete_range(start_pos, end_pos, description)
        else:
            # Delete backward word
            end_pos = (self.cursor_row, self.cursor_col)
            self.move_cursor_word(direction)
            start_pos = (self.cursor_row, self.cursor_col)
            self._delete_range(start_pos, end_pos, description)

    def delete_line(self, description: str = "Delete line") -> None:
        """Delete current line."""
        if len(self.lines) <= 1:
            self.set_text("", description)
            return

        self._save_state(description)
        del self.lines[self.cursor_row]

        if self.cursor_row >= len(self.lines):
            self.cursor_row = len(self.lines) - 1

        self.cursor_col = 0
        self._clamp_cursor()
        self.version += 1

    def move_cursor(
        self, movement: CursorMovement, extend_selection: bool = False
    ) -> None:
        """
        Move cursor with optional selection extension.

        Args:
            movement: Type of cursor movement
            extend_selection: Whether to extend current selection
        """
        if extend_selection and not self.selecting:
            self.start_selection()
        elif not extend_selection and self.selecting:
            self.clear_selection()

        old_row, old_col = self.cursor_row, self.cursor_col

        if movement == CursorMovement.LEFT:
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_row > 0:
                self.cursor_row -= 1
                self.cursor_col = len(self.lines[self.cursor_row])

        elif movement == CursorMovement.RIGHT:
            current_line = self.lines[self.cursor_row]
            if self.cursor_col < len(current_line):
                self.cursor_col += 1
            elif self.cursor_row < len(self.lines) - 1:
                self.cursor_row += 1
                self.cursor_col = 0

        elif movement == CursorMovement.UP:
            if self.cursor_row > 0:
                self.cursor_row -= 1
                self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

        elif movement == CursorMovement.DOWN:
            if self.cursor_row < len(self.lines) - 1:
                self.cursor_row += 1
                self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

        elif movement == CursorMovement.HOME:
            self.cursor_col = 0

        elif movement == CursorMovement.END:
            self.cursor_col = len(self.lines[self.cursor_row])

        elif movement == CursorMovement.WORD_LEFT:
            self.move_cursor_word(-1)

        elif movement == CursorMovement.WORD_RIGHT:
            self.move_cursor_word(1)

        elif movement == CursorMovement.PAGE_UP:
            self.cursor_row = max(0, self.cursor_row - self.viewport_height)
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

        elif movement == CursorMovement.PAGE_DOWN:
            self.cursor_row = min(
                len(self.lines) - 1, self.cursor_row + self.viewport_height
            )
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

        self._clamp_cursor()
        self._update_viewport()

        if extend_selection and self.selecting:
            self.selection.end_row = self.cursor_row
            self.selection.end_col = self.cursor_col

    def move_cursor_word(self, direction: int) -> None:
        """
        Move cursor by word boundaries.

        Args:
            direction: 1 for forward, -1 for backward
        """
        if direction == 1:  # Forward
            current_line = self.lines[self.cursor_row]
            pos = self.cursor_col

            # Skip current word
            while pos < len(current_line) and current_line[pos].isalnum():
                pos += 1

            # Skip whitespace
            while pos < len(current_line) and current_line[pos].isspace():
                pos += 1

            if pos < len(current_line):
                self.cursor_col = pos
            elif self.cursor_row < len(self.lines) - 1:
                self.cursor_row += 1
                self.cursor_col = 0

        else:  # Backward
            if self.cursor_col > 0:
                current_line = self.lines[self.cursor_row]
                pos = self.cursor_col - 1

                # Skip whitespace
                while pos >= 0 and current_line[pos].isspace():
                    pos -= 1

                # Skip word
                while pos >= 0 and current_line[pos].isalnum():
                    pos -= 1

                self.cursor_col = max(0, pos + 1)
            elif self.cursor_row > 0:
                self.cursor_row -= 1
                self.cursor_col = len(self.lines[self.cursor_row])

    def start_selection(self) -> None:
        """Start text selection at current cursor position."""
        self.selection = Selection(
            start_row=self.cursor_row,
            start_col=self.cursor_col,
            end_row=self.cursor_row,
            end_col=self.cursor_col,
        )
        self.selecting = True

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selection = None
        self.selecting = False

    def get_selected_text(self) -> str:
        """Get currently selected text."""
        if not self.selection or self.selection.is_empty():
            return ""

        selection = self.selection.normalize()

        if selection.start_row == selection.end_row:
            # Single line selection
            line = self.lines[selection.start_row]
            return line[selection.start_col : selection.end_col]
        else:
            # Multi-line selection
            result = []

            # First line
            first_line = self.lines[selection.start_row]
            result.append(first_line[selection.start_col :])

            # Middle lines
            for row in range(selection.start_row + 1, selection.end_row):
                result.append(self.lines[row])

            # Last line
            last_line = self.lines[selection.end_row]
            result.append(last_line[: selection.end_col])

            return "\n".join(result)

    def delete_selection(self, description: str = "Delete selection") -> None:
        """Delete currently selected text."""
        if not self.selection or self.selection.is_empty():
            return

        selection = self.selection.normalize()

        self._save_state(description)

        if selection.start_row == selection.end_row:
            # Single line deletion
            line = self.lines[selection.start_row]
            self.lines[selection.start_row] = (
                line[: selection.start_col] + line[selection.end_col :]
            )
            self.cursor_row = selection.start_row
            self.cursor_col = selection.start_col
        else:
            # Multi-line deletion
            first_line = self.lines[selection.start_row][: selection.start_col]
            last_line = self.lines[selection.end_row][selection.end_col :]

            # Remove lines in between
            del self.lines[selection.start_row : selection.end_row + 1]

            # Insert combined line
            self.lines.insert(selection.start_row, first_line + last_line)

            self.cursor_row = selection.start_row
            self.cursor_col = len(first_line)

        self.clear_selection()
        self._clamp_cursor()
        self.version += 1

    def undo(self) -> bool:
        """
        Undo last operation.

        Returns:
            True if undo was performed, False if no undo available
        """
        if not self.undo_stack:
            return False

        # Save current state to redo stack
        current_state = UndoState(
            lines=self.lines.copy(),
            cursor_row=self.cursor_row,
            cursor_col=self.cursor_col,
            description="Current state",
        )
        self.redo_stack.append(current_state)

        # Restore previous state
        state = self.undo_stack.pop()
        self.lines = state.lines
        self.cursor_row = state.cursor_row
        self.cursor_col = state.cursor_col

        self._clamp_cursor()
        self.version += 1

        logger.debug(f"Undo: {state.description}")
        return True

    def redo(self) -> bool:
        """
        Redo last undone operation.

        Returns:
            True if redo was performed, False if no redo available
        """
        if not self.redo_stack:
            return False

        # Save current state to undo stack
        self._save_state("Redo operation")

        # Restore redo state
        state = self.redo_stack.pop()
        self.lines = state.lines
        self.cursor_row = state.cursor_row
        self.cursor_col = state.cursor_col

        self._clamp_cursor()
        self.version += 1

        logger.debug(f"Redo: {state.description}")
        return True

    def find_text(
        self,
        search_text: str,
        start_row: int = 0,
        start_col: int = 0,
        case_sensitive: bool = False,
    ) -> Optional[Tuple[int, int]]:
        """
        Find text in buffer.

        Args:
            search_text: Text to search for
            start_row: Starting row for search
            start_col: Starting column for search
            case_sensitive: Whether search is case sensitive

        Returns:
            Tuple of (row, col) if found, None otherwise
        """
        if not search_text:
            return None

        search_func = (
            str.find if case_sensitive else lambda s, t: s.lower().find(t.lower())
        )
        search_target = search_text if case_sensitive else search_text.lower()

        # Search from start position
        for row in range(start_row, len(self.lines)):
            line = self.lines[row]
            search_line = line if case_sensitive else line.lower()

            start_pos = start_col if row == start_row else 0
            pos = search_func(search_line[start_pos:], search_target)

            if pos != -1:
                return (row, start_pos + pos)

        return None

    def replace_text(
        self,
        search_text: str,
        replace_text: str,
        all_occurrences: bool = False,
        case_sensitive: bool = False,
    ) -> int:
        """
        Replace text in buffer.

        Args:
            search_text: Text to search for
            replace_text: Replacement text
            all_occurrences: Whether to replace all occurrences
            case_sensitive: Whether search is case sensitive

        Returns:
            Number of replacements made
        """
        if not search_text:
            return 0

        replacements = 0
        self._save_state(f"Replace '{search_text}' with '{replace_text}'")

        for row in range(len(self.lines)):
            line = self.lines[row]

            if case_sensitive:
                new_line = line.replace(
                    search_text, replace_text, -1 if all_occurrences else 1
                )
            else:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(search_text), re.IGNORECASE)
                if all_occurrences:
                    new_line = pattern.sub(replace_text, line)
                else:
                    new_line = pattern.sub(replace_text, line, count=1)

            if new_line != line:
                self.lines[row] = new_line
                replacements += 1
                if not all_occurrences:
                    break

        if replacements > 0:
            self.version += 1

        return replacements

    def get_line_count(self) -> int:
        """Get total number of lines."""
        return len(self.lines)

    def get_char_count(self) -> int:
        """Get total number of characters."""
        return sum(len(line) for line in self.lines) + len(self.lines) - 1

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self.lines) == 1 and len(self.lines[0]) == 0

    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position."""
        return (self.cursor_row, self.cursor_col)

    def set_cursor_position(self, row: int, col: int) -> None:
        """Set cursor position."""
        self.cursor_row = row
        self.cursor_col = col
        self._clamp_cursor()
        self._update_viewport()

    def get_viewport_text(self) -> List[str]:
        """Get text visible in current viewport."""
        end_row = min(len(self.lines), self.scroll_row + self.viewport_height)
        viewport_lines = []

        for row in range(self.scroll_row, end_row):
            line = self.lines[row]
            if self.word_wrap:
                # Handle word wrapping
                wrapped_lines = self._wrap_line(line)
                viewport_lines.extend(wrapped_lines)
            else:
                # Handle horizontal scrolling
                if self.scroll_col < len(line):
                    end_col = min(len(line), self.scroll_col + self.viewport_width)
                    viewport_lines.append(line[self.scroll_col : end_col])
                else:
                    viewport_lines.append("")

        return viewport_lines

    def set_viewport_size(self, width: int, height: int) -> None:
        """Set viewport dimensions."""
        self.viewport_width = width
        self.viewport_height = height
        self._update_viewport()

    def _save_state(self, description: str) -> None:
        """Save current state for undo."""
        state = UndoState(
            lines=self.lines.copy(),
            cursor_row=self.cursor_row,
            cursor_col=self.cursor_col,
            description=description,
        )

        self.undo_stack.append(state)

        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)

        # Clear redo stack when new action is performed
        self.redo_stack.clear()

    def _clamp_cursor(self) -> None:
        """Ensure cursor is within valid bounds."""
        self.cursor_row = max(0, min(self.cursor_row, len(self.lines) - 1))

        if self.cursor_row < len(self.lines):
            max_col = len(self.lines[self.cursor_row])
            self.cursor_col = max(0, min(self.cursor_col, max_col))

    def _update_viewport(self) -> None:
        """Update viewport scroll position to keep cursor visible."""
        # Vertical scrolling
        if self.cursor_row < self.scroll_row:
            self.scroll_row = self.cursor_row
        elif self.cursor_row >= self.scroll_row + self.viewport_height:
            self.scroll_row = self.cursor_row - self.viewport_height + 1

        # Horizontal scrolling (if word wrap is disabled)
        if not self.word_wrap:
            if self.cursor_col < self.scroll_col:
                self.scroll_col = self.cursor_col
            elif self.cursor_col >= self.scroll_col + self.viewport_width:
                self.scroll_col = self.cursor_col - self.viewport_width + 1

    def _wrap_line(self, line: str) -> List[str]:
        """Wrap line to viewport width."""
        if len(line) <= self.viewport_width:
            return [line]

        wrapped = []
        for i in range(0, len(line), self.viewport_width):
            wrapped.append(line[i : i + self.viewport_width])

        return wrapped

    def _delete_range(
        self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], description: str
    ) -> None:
        """Delete text between two positions."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Ensure start is before end
        if start_row > end_row or (start_row == end_row and start_col > end_col):
            start_pos, end_pos = end_pos, start_pos
            start_row, start_col = start_pos
            end_row, end_col = end_pos

        self._save_state(description)

        if start_row == end_row:
            # Single line deletion
            line = self.lines[start_row]
            self.lines[start_row] = line[:start_col] + line[end_col:]
        else:
            # Multi-line deletion
            first_line = self.lines[start_row][:start_col]
            last_line = self.lines[end_row][end_col:]

            # Remove lines in between
            del self.lines[start_row : end_row + 1]

            # Insert combined line
            self.lines.insert(start_row, first_line + last_line)

        self.cursor_row = start_row
        self.cursor_col = start_col
        self._clamp_cursor()
        self.version += 1


class TextBufferWidget(Widget):
    """
    Textual widget wrapper for TextBuffer.

    Provides a Textual widget interface for the TextBuffer class,
    handling events and rendering.
    """

    BINDINGS = [
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+y", "redo", "Redo"),
        Binding("ctrl+a", "select_all", "Select All"),
        Binding("ctrl+c", "copy", "Copy"),
        Binding("ctrl+x", "cut", "Cut"),
        Binding("ctrl+v", "paste", "Paste"),
        Binding("ctrl+f", "find", "Find"),
        Binding("ctrl+h", "replace", "Replace"),
    ]

    def __init__(self, initial_text: str = "", syntax: Optional[str] = None, **kwargs):
        """
        Initialize TextBuffer widget.

        Args:
            initial_text: Initial text content
            syntax: Syntax highlighting language
        """
        super().__init__(**kwargs)
        self.buffer = TextBuffer(initial_text)
        self.syntax = syntax
        self.cursor_visible = True
        self.cursor_blink_time = 0.5

        # Clipboard for copy/paste
        self.clipboard = ""

    def render(self) -> Text:
        """Render the text buffer."""
        viewport_lines = self.buffer.get_viewport_text()

        if self.syntax:
            # Use syntax highlighting
            full_text = "\n".join(viewport_lines)
            syntax_text = Syntax(
                full_text, self.syntax, theme="monokai", line_numbers=True
            )
            return syntax_text
        else:
            # Plain text rendering
            result = Text()
            cursor_row, cursor_col = self.buffer.get_cursor_position()

            for i, line in enumerate(viewport_lines):
                row = self.buffer.scroll_row + i

                if row == cursor_row and self.cursor_visible:
                    # Add cursor
                    if cursor_col <= len(line):
                        line_text = Text(line[:cursor_col])
                        line_text.append("|", style="reverse")
                        line_text.append(line[cursor_col:])
                    else:
                        line_text = Text(line)
                        line_text.append("|", style="reverse")
                else:
                    line_text = Text(line)

                # Highlight selection if present
                if self.buffer.selection:
                    selection = self.buffer.selection.normalize()
                    if selection.start_row <= row <= selection.end_row:
                        start_col = (
                            selection.start_col if row == selection.start_row else 0
                        )
                        end_col = (
                            selection.end_col if row == selection.end_row else len(line)
                        )

                        if start_col < len(line):
                            line_text.stylize(
                                "reverse", start_col, min(end_col, len(line))
                            )

                result.append(line_text)
                if i < len(viewport_lines) - 1:
                    result.append("\n")

            return result

    async def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        key = event.key

        # Movement keys
        if key == "left":
            self.buffer.move_cursor(CursorMovement.LEFT, event.shift)
        elif key == "right":
            self.buffer.move_cursor(CursorMovement.RIGHT, event.shift)
        elif key == "up":
            self.buffer.move_cursor(CursorMovement.UP, event.shift)
        elif key == "down":
            self.buffer.move_cursor(CursorMovement.DOWN, event.shift)
        elif key == "home":
            self.buffer.move_cursor(CursorMovement.HOME, event.shift)
        elif key == "end":
            self.buffer.move_cursor(CursorMovement.END, event.shift)
        elif key == "pageup":
            self.buffer.move_cursor(CursorMovement.PAGE_UP, event.shift)
        elif key == "pagedown":
            self.buffer.move_cursor(CursorMovement.PAGE_DOWN, event.shift)
        elif key == "ctrl+left":
            self.buffer.move_cursor(CursorMovement.WORD_LEFT, event.shift)
        elif key == "ctrl+right":
            self.buffer.move_cursor(CursorMovement.WORD_RIGHT, event.shift)

        # Editing keys
        elif key == "backspace":
            if self.buffer.selection and not self.buffer.selection.is_empty():
                self.buffer.delete_selection()
            else:
                self.buffer.delete_char(-1)
        elif key == "delete":
            if self.buffer.selection and not self.buffer.selection.is_empty():
                self.buffer.delete_selection()
            else:
                self.buffer.delete_char(1)
        elif key == "enter":
            if self.buffer.selection and not self.buffer.selection.is_empty():
                self.buffer.delete_selection()
            self.buffer.insert_text("\n")
        elif key == "tab":
            if self.buffer.selection and not self.buffer.selection.is_empty():
                self.buffer.delete_selection()
            self.buffer.insert_text(" " * self.buffer.tab_width)

        # Ctrl+key combinations
        elif key == "ctrl+k":
            # Delete to end of line
            cursor_row, cursor_col = self.buffer.get_cursor_position()
            line = self.buffer.lines[cursor_row]
            if cursor_col < len(line):
                self.buffer.lines[cursor_row] = line[:cursor_col]
            elif cursor_row < len(self.buffer.lines) - 1:
                self.buffer.delete_char(1)
        elif key == "ctrl+u":
            # Delete to beginning of line
            cursor_row, cursor_col = self.buffer.get_cursor_position()
            line = self.buffer.lines[cursor_row]
            self.buffer.lines[cursor_row] = line[cursor_col:]
            self.buffer.cursor_col = 0
        elif key == "ctrl+w":
            # Delete word backward
            self.buffer.delete_word(-1)
        elif key == "ctrl+d":
            # Delete word forward
            self.buffer.delete_word(1)

        # Printable characters
        elif len(key) == 1 and key.isprintable():
            if self.buffer.selection and not self.buffer.selection.is_empty():
                self.buffer.delete_selection()
            self.buffer.insert_text(key)

        self.refresh()

    async def on_resize(self, event: events.Resize) -> None:
        """Handle resize events."""
        self.buffer.set_viewport_size(event.size.width, event.size.height)
        self.refresh()

    def action_undo(self) -> None:
        """Undo action."""
        self.buffer.undo()
        self.refresh()

    def action_redo(self) -> None:
        """Redo action."""
        self.buffer.redo()
        self.refresh()

    def action_select_all(self) -> None:
        """Select all text."""
        self.buffer.start_selection()
        self.buffer.cursor_row = 0
        self.buffer.cursor_col = 0
        self.buffer.selection.start_row = 0
        self.buffer.selection.start_col = 0
        self.buffer.cursor_row = len(self.buffer.lines) - 1
        self.buffer.cursor_col = len(self.buffer.lines[-1])
        self.buffer.selection.end_row = self.buffer.cursor_row
        self.buffer.selection.end_col = self.buffer.cursor_col
        self.refresh()

    def action_copy(self) -> None:
        """Copy selected text."""
        if self.buffer.selection and not self.buffer.selection.is_empty():
            self.clipboard = self.buffer.get_selected_text()

    def action_cut(self) -> None:
        """Cut selected text."""
        if self.buffer.selection and not self.buffer.selection.is_empty():
            self.clipboard = self.buffer.get_selected_text()
            self.buffer.delete_selection()
            self.refresh()

    def action_paste(self) -> None:
        """Paste text from clipboard."""
        if self.clipboard:
            if self.buffer.selection and not self.buffer.selection.is_empty():
                self.buffer.delete_selection()
            self.buffer.insert_text(self.clipboard)
            self.refresh()

    def action_find(self) -> None:
        """Find text (to be implemented by parent)."""

    def action_replace(self) -> None:
        """Replace text (to be implemented by parent)."""

    def get_text(self) -> str:
        """Get complete text content."""
        return self.buffer.get_text()

    def set_text(self, text: str) -> None:
        """Set text content."""
        self.buffer.set_text(text)
        self.refresh()

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        return {
            "line_count": self.buffer.get_line_count(),
            "char_count": self.buffer.get_char_count(),
            "cursor_position": self.buffer.get_cursor_position(),
            "has_selection": self.buffer.selection is not None
            and not self.buffer.selection.is_empty(),
            "undo_levels": len(self.buffer.undo_stack),
            "redo_levels": len(self.buffer.redo_stack),
            "version": self.buffer.version,
        }
