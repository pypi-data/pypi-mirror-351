"""
Advanced input widgets for Kritrima AI CLI.

This module provides sophisticated input widgets with features like:
- Multiline text editing with syntax highlighting
- File tag expansion and auto-completion
- Command input with slash command support
- File path suggestions and completion
- Input history and navigation
- Emacs-style keyboard shortcuts
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Input, Static

from kritrima_ai.ui.widgets.text_buffer import TextBufferWidget
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class InputMode(Enum):
    """Input modes for different types of input handling."""

    NORMAL = "normal"
    COMMAND = "command"
    FILE_TAG = "file_tag"
    SEARCH = "search"


@dataclass
class CompletionItem:
    """A completion suggestion item."""

    text: str
    description: str = ""
    type: str = "text"  # text, file, command, etc.
    icon: str = ""


class AdvancedInput(Input):
    """
    Advanced input widget with completion and enhanced features.

    Provides auto-completion, input history, and enhanced keyboard shortcuts.
    """

    BINDINGS = [
        Binding("ctrl+space", "show_completions", "Show Completions"),
        Binding("tab", "complete", "Complete"),
        Binding("ctrl+p", "history_prev", "Previous History"),
        Binding("ctrl+n", "history_next", "Next History"),
        Binding("ctrl+a", "cursor_start", "Go to Start"),
        Binding("ctrl+e", "cursor_end", "Go to End"),
        Binding("ctrl+k", "delete_to_end", "Delete to End"),
        Binding("ctrl+u", "delete_to_start", "Delete to Start"),
        Binding("ctrl+w", "delete_word", "Delete Word"),
        Binding("alt+f", "word_forward", "Word Forward"),
        Binding("alt+b", "word_backward", "Word Backward"),
    ]

    def __init__(
        self,
        completion_provider: Optional[Callable[[str], List[CompletionItem]]] = None,
        history_size: int = 100,
        **kwargs,
    ):
        """
        Initialize advanced input.

        Args:
            completion_provider: Function to provide completions
            history_size: Maximum history size
        """
        super().__init__(**kwargs)
        self.completion_provider = completion_provider
        self.history_size = history_size

        # Input state
        self.input_mode = InputMode.NORMAL
        self.completion_prefix = ""
        self.completion_start_pos = 0

        # History management
        self.history: List[str] = []
        self.history_index = -1
        self.current_input = ""

        # Word boundaries for navigation
        self.word_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        )

    def add_to_history(self, text: str) -> None:
        """Add text to input history."""
        if text and (not self.history or self.history[-1] != text):
            self.history.append(text)

            # Limit history size
            if len(self.history) > self.history_size:
                self.history = self.history[-self.history_size :]

        # Reset history navigation
        self.history_index = -1
        self.current_input = ""


class FileTagInput(AdvancedInput):
    """Specialized input for file tag expansion."""

    def __init__(self, **kwargs):
        """Initialize file tag input."""
        super().__init__(
            placeholder="Enter message (use @filename for files, /help for commands)...",
            **kwargs,
        )


class CommandInput(AdvancedInput):
    """Specialized input for command entry."""

    def __init__(self, **kwargs):
        """Initialize command input."""
        super().__init__(
            placeholder="Enter command or type /help for available commands...",
            **kwargs,
        )


class MultilineEditor(Container):
    """Multiline text editor with advanced features."""

    def __init__(
        self,
        initial_text: str = "",
        syntax: Optional[str] = None,
        show_line_numbers: bool = True,
        **kwargs,
    ):
        """Initialize multiline editor."""
        super().__init__(**kwargs)
        self.syntax = syntax
        self.show_line_numbers = show_line_numbers

        # Create text buffer widget
        self.text_buffer = TextBufferWidget(initial_text=initial_text, syntax=syntax)

        # Status information
        self.status_bar = Static("")

    def compose(self):
        """Compose the editor layout."""
        yield self.text_buffer
        yield self.status_bar

    def get_text(self) -> str:
        """Get the current text content."""
        return self.text_buffer.get_text()

    def set_text(self, text: str) -> None:
        """Set the text content."""
        self.text_buffer.set_text(text)


# Convenience functions
def create_file_tag_input(**kwargs) -> FileTagInput:
    """Create a file tag input widget."""
    return FileTagInput(**kwargs)


def create_command_input(**kwargs) -> CommandInput:
    """Create a command input widget."""
    return CommandInput(**kwargs)


def create_multiline_editor(
    text: str = "", language: str = "python", **kwargs
) -> MultilineEditor:
    """Create a multiline editor widget."""
    return MultilineEditor(
        initial_text=text, syntax=language, show_line_numbers=True, **kwargs
    )
