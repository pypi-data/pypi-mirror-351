"""
Advanced text buffer implementation for multi-line text editing.

This module provides a sophisticated text buffer with full Unicode support,
undo/redo functionality, cursor management, and advanced text operations.
"""

import logging
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, NamedTuple, Optional

logger = logging.getLogger(__name__)


class CursorMovement(Enum):
    """Cursor movement types."""

    CHAR_LEFT = "char_left"
    CHAR_RIGHT = "char_right"
    WORD_LEFT = "word_left"
    WORD_RIGHT = "word_right"
    LINE_START = "line_start"
    LINE_END = "line_end"
    LINE_UP = "line_up"
    LINE_DOWN = "line_down"
    BUFFER_START = "buffer_start"
    BUFFER_END = "buffer_end"


@dataclass
class CursorPosition:
    """Represents a cursor position in the text buffer."""

    row: int
    col: int

    def __post_init__(self):
        """Ensure valid cursor position."""
        self.row = max(0, self.row)
        self.col = max(0, self.col)


@dataclass
class UndoState:
    """Represents a state for undo/redo operations."""

    lines: List[str]
    cursor: CursorPosition
    description: str
    timestamp: float


class TextOperation(NamedTuple):
    """Represents a text operation."""

    type: str  # 'insert', 'delete', 'replace'
    start: CursorPosition
    end: CursorPosition
    old_text: str
    new_text: str


class TextBuffer:
    """
    Advanced text buffer with Unicode support and editing capabilities.

    Features:
    - Multi-line text editing
    - Full Unicode support with proper character width handling
    - Undo/redo system with operation merging
    - Advanced cursor movement (word-wise, line-wise)
    - Text selection and manipulation
    - Viewport management for scrolling
    - Performance optimization for large texts
    """

    def __init__(self, initial_text: str = "", max_undo_levels: int = 100):
        """
        Initialize the text buffer.

        Args:
            initial_text: Initial text content
            max_undo_levels: Maximum number of undo levels
        """
        self.lines: List[str] = initial_text.split("\n") if initial_text else [""]
        self.cursor = CursorPosition(0, 0)
        self.scroll_row = 0
        self.scroll_col = 0
        self.version = 0

        # Undo/Redo system
        self.undo_stack: List[UndoState] = []
        self.redo_stack: List[UndoState] = []
        self.max_undo_levels = max_undo_levels

        # Selection state
        self.selection_start: Optional[CursorPosition] = None
        self.selection_end: Optional[CursorPosition] = None

        # Operation merging for undo
        self.last_operation_time = 0.0
        self.last_operation_type = ""

        # Performance optimization
        self._line_cache: Dict[int, Dict[str, Any]] = {}

        logger.debug(f"Initialized text buffer with {len(self.lines)} lines")

    def get_text(self) -> str:
        """Get the complete text content."""
        return "\n".join(self.lines)

    def get_line(self, row: int) -> str:
        """
        Get a specific line by row number.

        Args:
            row: Row number (0-based)

        Returns:
            Line content or empty string if row is invalid
        """
        if 0 <= row < len(self.lines):
            return self.lines[row]
        return ""

    def get_line_count(self) -> int:
        """Get the total number of lines."""
        return len(self.lines)

    def get_char_at(self, position: CursorPosition) -> str:
        """
        Get character at specific position.

        Args:
            position: Cursor position

        Returns:
            Character at position or empty string
        """
        line = self.get_line(position.row)
        if 0 <= position.col < len(line):
            return line[position.col]
        return ""

    def is_valid_position(self, position: CursorPosition) -> bool:
        """
        Check if a cursor position is valid.

        Args:
            position: Position to validate

        Returns:
            True if position is valid
        """
        if position.row < 0 or position.row >= len(self.lines):
            return False

        line_length = len(self.lines[position.row])
        return 0 <= position.col <= line_length

    def clamp_position(self, position: CursorPosition) -> CursorPosition:
        """
        Clamp position to valid bounds.

        Args:
            position: Position to clamp

        Returns:
            Valid position within bounds
        """
        row = max(0, min(position.row, len(self.lines) - 1))
        line_length = len(self.lines[row])
        col = max(0, min(position.col, line_length))
        return CursorPosition(row, col)

    def move_cursor(
        self, movement: CursorMovement, extend_selection: bool = False
    ) -> bool:
        """
        Move cursor according to movement type.

        Args:
            movement: Type of cursor movement
            extend_selection: Whether to extend current selection

        Returns:
            True if cursor was moved
        """
        old_cursor = CursorPosition(self.cursor.row, self.cursor.col)
        new_cursor = self._calculate_cursor_movement(movement)

        if new_cursor != old_cursor:
            if extend_selection:
                if self.selection_start is None:
                    self.selection_start = old_cursor
                self.selection_end = new_cursor
            elif not extend_selection:
                self.clear_selection()

            self.cursor = new_cursor
            self._update_scroll()
            return True

        return False

    def _calculate_cursor_movement(self, movement: CursorMovement) -> CursorPosition:
        """Calculate new cursor position for movement."""
        current_line = self.get_line(self.cursor.row)

        if movement == CursorMovement.CHAR_LEFT:
            if self.cursor.col > 0:
                return CursorPosition(self.cursor.row, self.cursor.col - 1)
            elif self.cursor.row > 0:
                prev_line = self.get_line(self.cursor.row - 1)
                return CursorPosition(self.cursor.row - 1, len(prev_line))

        elif movement == CursorMovement.CHAR_RIGHT:
            if self.cursor.col < len(current_line):
                return CursorPosition(self.cursor.row, self.cursor.col + 1)
            elif self.cursor.row < len(self.lines) - 1:
                return CursorPosition(self.cursor.row + 1, 0)

        elif movement == CursorMovement.WORD_LEFT:
            return self._find_word_boundary(self.cursor, -1)

        elif movement == CursorMovement.WORD_RIGHT:
            return self._find_word_boundary(self.cursor, 1)

        elif movement == CursorMovement.LINE_START:
            return CursorPosition(self.cursor.row, 0)

        elif movement == CursorMovement.LINE_END:
            return CursorPosition(self.cursor.row, len(current_line))

        elif movement == CursorMovement.LINE_UP:
            if self.cursor.row > 0:
                new_row = self.cursor.row - 1
                new_col = min(self.cursor.col, len(self.get_line(new_row)))
                return CursorPosition(new_row, new_col)

        elif movement == CursorMovement.LINE_DOWN:
            if self.cursor.row < len(self.lines) - 1:
                new_row = self.cursor.row + 1
                new_col = min(self.cursor.col, len(self.get_line(new_row)))
                return CursorPosition(new_row, new_col)

        elif movement == CursorMovement.BUFFER_START:
            return CursorPosition(0, 0)

        elif movement == CursorMovement.BUFFER_END:
            last_row = len(self.lines) - 1
            last_col = len(self.get_line(last_row))
            return CursorPosition(last_row, last_col)

        return self.cursor

    def _find_word_boundary(
        self, position: CursorPosition, direction: int
    ) -> CursorPosition:
        """Find word boundary in given direction."""
        line = self.get_line(position.row)
        col = position.col

        if direction < 0:  # Moving left
            # Skip current whitespace
            while col > 0 and line[col - 1].isspace():
                col -= 1

            # Skip current word
            while col > 0 and not line[col - 1].isspace():
                col -= 1

        else:  # Moving right
            # Skip current word
            while col < len(line) and not line[col].isspace():
                col += 1

            # Skip whitespace
            while col < len(line) and line[col].isspace():
                col += 1

        return CursorPosition(position.row, col)

    def insert_text(self, text: str, position: Optional[CursorPosition] = None) -> bool:
        """
        Insert text at specified position.

        Args:
            text: Text to insert
            position: Position to insert at (defaults to cursor)

        Returns:
            True if text was inserted
        """
        if position is None:
            position = self.cursor

        position = self.clamp_position(position)

        # Save state for undo
        self._save_undo_state("insert")

        # Handle multi-line text
        if "\n" in text:
            lines_to_insert = text.split("\n")
            current_line = self.get_line(position.row)

            # Split current line at insertion point
            before = current_line[: position.col]
            after = current_line[position.col :]

            # Replace current line with first part + first inserted line
            self.lines[position.row] = before + lines_to_insert[0]

            # Insert middle lines
            insert_point = position.row + 1
            for i, line in enumerate(lines_to_insert[1:-1], 1):
                self.lines.insert(insert_point, line)
                insert_point += 1

            # Insert last line + remaining part
            if len(lines_to_insert) > 1:
                self.lines.insert(insert_point, lines_to_insert[-1] + after)

                # Update cursor position
                final_row = position.row + len(lines_to_insert) - 1
                final_col = len(lines_to_insert[-1])
                self.cursor = CursorPosition(final_row, final_col)
            else:
                self.cursor = CursorPosition(position.row, position.col + len(text))

        else:
            # Single line insertion
            line = self.get_line(position.row)
            new_line = line[: position.col] + text + line[position.col :]
            self.lines[position.row] = new_line

            # Update cursor
            self.cursor = CursorPosition(position.row, position.col + len(text))

        self.version += 1
        self._clear_cache()
        self._update_scroll()

        return True

    def delete_text(self, start: CursorPosition, end: CursorPosition) -> str:
        """
        Delete text between start and end positions.

        Args:
            start: Start position
            end: End position

        Returns:
            Deleted text
        """
        start = self.clamp_position(start)
        end = self.clamp_position(end)

        # Ensure start comes before end
        if start.row > end.row or (start.row == end.row and start.col > end.col):
            start, end = end, start

        # Save state for undo
        self._save_undo_state("delete")

        # Get deleted text for return value
        deleted_text = self.get_text_range(start, end)

        if start.row == end.row:
            # Single line deletion
            line = self.get_line(start.row)
            new_line = line[: start.col] + line[end.col :]
            self.lines[start.row] = new_line
        else:
            # Multi-line deletion
            start_line = self.get_line(start.row)
            end_line = self.get_line(end.row)

            # Combine parts of first and last lines
            new_line = start_line[: start.col] + end_line[end.col :]
            self.lines[start.row] = new_line

            # Remove lines in between (including end line)
            del self.lines[start.row + 1 : end.row + 1]

        # Update cursor
        self.cursor = start
        self.version += 1
        self._clear_cache()
        self._update_scroll()

        return deleted_text

    def get_text_range(self, start: CursorPosition, end: CursorPosition) -> str:
        """
        Get text between start and end positions.

        Args:
            start: Start position
            end: End position

        Returns:
            Text in range
        """
        start = self.clamp_position(start)
        end = self.clamp_position(end)

        # Ensure start comes before end
        if start.row > end.row or (start.row == end.row and start.col > end.col):
            start, end = end, start

        if start.row == end.row:
            # Single line
            line = self.get_line(start.row)
            return line[start.col : end.col]
        else:
            # Multi-line
            result = []

            # First line
            start_line = self.get_line(start.row)
            result.append(start_line[start.col :])

            # Middle lines
            for row in range(start.row + 1, end.row):
                result.append(self.get_line(row))

            # Last line
            end_line = self.get_line(end.row)
            result.append(end_line[: end.col])

            return "\n".join(result)

    def replace_text(
        self, start: CursorPosition, end: CursorPosition, text: str
    ) -> str:
        """
        Replace text in range with new text.

        Args:
            start: Start position
            end: End position
            text: Replacement text

        Returns:
            Original text that was replaced
        """
        old_text = self.get_text_range(start, end)
        self.delete_text(start, end)
        self.insert_text(text, start)
        return old_text

    def delete_line(self, row: int) -> str:
        """
        Delete entire line.

        Args:
            row: Row number to delete

        Returns:
            Deleted line content
        """
        if 0 <= row < len(self.lines):
            self._save_undo_state("delete_line")
            deleted_line = self.lines.pop(row)

            # Ensure at least one line exists
            if not self.lines:
                self.lines = [""]

            # Adjust cursor if necessary
            if self.cursor.row >= len(self.lines):
                self.cursor.row = len(self.lines) - 1

            self.cursor.col = min(self.cursor.col, len(self.get_line(self.cursor.row)))
            self.version += 1
            self._clear_cache()

            return deleted_line

        return ""

    def insert_line(self, row: int, content: str = "") -> bool:
        """
        Insert new line at specified row.

        Args:
            row: Row number to insert at
            content: Line content

        Returns:
            True if line was inserted
        """
        if 0 <= row <= len(self.lines):
            self._save_undo_state("insert_line")
            self.lines.insert(row, content)
            self.version += 1
            self._clear_cache()
            return True

        return False

    def clear_selection(self) -> None:
        """Clear current text selection."""
        self.selection_start = None
        self.selection_end = None

    def select_all(self) -> None:
        """Select all text in buffer."""
        self.selection_start = CursorPosition(0, 0)
        last_row = len(self.lines) - 1
        last_col = len(self.get_line(last_row))
        self.selection_end = CursorPosition(last_row, last_col)

    def get_selected_text(self) -> str:
        """
        Get currently selected text.

        Returns:
            Selected text or empty string
        """
        if self.selection_start and self.selection_end:
            return self.get_text_range(self.selection_start, self.selection_end)
        return ""

    def delete_selected(self) -> str:
        """
        Delete currently selected text.

        Returns:
            Deleted text
        """
        if self.selection_start and self.selection_end:
            deleted = self.delete_text(self.selection_start, self.selection_end)
            self.clear_selection()
            return deleted
        return ""

    def _save_undo_state(self, description: str) -> None:
        """Save current state for undo."""
        import time

        current_time = time.time()

        # Create undo state
        undo_state = UndoState(
            lines=self.lines.copy(),
            cursor=CursorPosition(self.cursor.row, self.cursor.col),
            description=description,
            timestamp=current_time,
        )

        # Check if we should merge with previous operation
        should_merge = (
            self.undo_stack
            and current_time - self.last_operation_time < 1.0  # Within 1 second
            and self.last_operation_type == description
            and description in ["insert", "delete"]  # Only merge simple operations
        )

        if should_merge:
            # Update the last undo state instead of adding new one
            self.undo_stack[-1] = undo_state
        else:
            # Add new undo state
            self.undo_stack.append(undo_state)

            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_levels:
                self.undo_stack.pop(0)

        # Clear redo stack on new operation
        self.redo_stack.clear()

        self.last_operation_time = current_time
        self.last_operation_type = description

    def undo(self) -> bool:
        """
        Undo last operation.

        Returns:
            True if undo was performed
        """
        if not self.undo_stack:
            return False

        # Save current state for redo
        current_state = UndoState(
            lines=self.lines.copy(),
            cursor=CursorPosition(self.cursor.row, self.cursor.col),
            description="redo_point",
            timestamp=self.last_operation_time,
        )
        self.redo_stack.append(current_state)

        # Restore previous state
        undo_state = self.undo_stack.pop()
        self.lines = undo_state.lines.copy()
        self.cursor = CursorPosition(undo_state.cursor.row, undo_state.cursor.col)

        self.version += 1
        self._clear_cache()
        self._update_scroll()

        return True

    def redo(self) -> bool:
        """
        Redo last undone operation.

        Returns:
            True if redo was performed
        """
        if not self.redo_stack:
            return False

        # Save current state for undo
        current_state = UndoState(
            lines=self.lines.copy(),
            cursor=CursorPosition(self.cursor.row, self.cursor.col),
            description="undo_point",
            timestamp=self.last_operation_time,
        )
        self.undo_stack.append(current_state)

        # Restore redo state
        redo_state = self.redo_stack.pop()
        self.lines = redo_state.lines.copy()
        self.cursor = CursorPosition(redo_state.cursor.row, redo_state.cursor.col)

        self.version += 1
        self._clear_cache()
        self._update_scroll()

        return True

    def _update_scroll(self) -> None:
        """Update scroll position to keep cursor visible."""
        # This would be implemented based on viewport size
        # For now, just ensure cursor is valid
        self.cursor = self.clamp_position(self.cursor)

    def _clear_cache(self) -> None:
        """Clear internal caches."""
        self._line_cache.clear()

    def get_char_width(self, char: str) -> int:
        """
        Get display width of a character.

        Args:
            char: Character to measure

        Returns:
            Display width (0, 1, or 2)
        """
        if not char:
            return 0

        # Handle control characters
        if ord(char) < 32:
            return 0

        # Use Unicode East Asian Width property
        width = unicodedata.east_asian_width(char)
        if width in ("F", "W"):  # Full-width or Wide
            return 2
        elif width in ("H", "Na", "N"):  # Half-width, Narrow, or Neutral
            return 1
        else:  # Ambiguous
            return 1

    def get_line_width(self, row: int) -> int:
        """
        Get display width of a line.

        Args:
            row: Row number

        Returns:
            Total display width
        """
        line = self.get_line(row)
        return sum(self.get_char_width(char) for char in line)

    def get_cursor_visual_col(self) -> int:
        """
        Get visual column position of cursor (accounting for character widths).

        Returns:
            Visual column position
        """
        line = self.get_line(self.cursor.row)
        visual_col = 0

        for i in range(min(self.cursor.col, len(line))):
            visual_col += self.get_char_width(line[i])

        return visual_col

    def find_cursor_from_visual_col(self, row: int, visual_col: int) -> int:
        """
        Find cursor column from visual column position.

        Args:
            row: Row number
            visual_col: Target visual column

        Returns:
            Cursor column position
        """
        line = self.get_line(row)
        current_visual = 0

        for col, char in enumerate(line):
            char_width = self.get_char_width(char)
            if current_visual + char_width > visual_col:
                return col
            current_visual += char_width

        return len(line)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get buffer statistics.

        Returns:
            Dictionary with buffer statistics
        """
        text = self.get_text()
        return {
            "lines": len(self.lines),
            "characters": len(text),
            "words": len(text.split()),
            "cursor_position": (self.cursor.row, self.cursor.col),
            "version": self.version,
            "undo_levels": len(self.undo_stack),
            "redo_levels": len(self.redo_stack),
            "has_selection": bool(self.selection_start and self.selection_end),
        }
