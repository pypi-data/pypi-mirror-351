"""
Chat components for Kritrima AI CLI terminal interface.

This module provides specialized widgets for chat interaction including
message rendering, streaming responses, code blocks, and tool calls.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.message import Message
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Static

logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Message role types."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageStatus(Enum):
    """Message status types."""

    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ChatMessage:
    """Represents a chat message with metadata."""

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: MessageStatus = MessageStatus.COMPLETE
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)

    @property
    def is_user(self) -> bool:
        """Check if message is from user."""
        return self.role == MessageRole.USER

    @property
    def is_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == MessageRole.ASSISTANT

    @property
    def is_system(self) -> bool:
        """Check if message is from system."""
        return self.role == MessageRole.SYSTEM

    @property
    def is_tool(self) -> bool:
        """Check if message is from tool."""
        return self.role == MessageRole.TOOL


class ChatMessageRenderer(Static):
    """Widget for rendering individual chat messages."""

    DEFAULT_CSS = """
    ChatMessageRenderer {
        margin: 1 0;
        padding: 1;
    }
    
    ChatMessageRenderer.user {
        background: $primary-background;
        border-left: thick $primary;
    }
    
    ChatMessageRenderer.assistant {
        background: $secondary-background;
        border-left: thick $secondary;
    }
    
    ChatMessageRenderer.system {
        background: $warning-background;
        border-left: thick $warning;
    }
    
    ChatMessageRenderer.tool {
        background: $success-background;
        border-left: thick $success;
    }
    
    ChatMessageRenderer.error {
        background: $error-background;
        border-left: thick $error;
    }
    
    ChatMessageRenderer .timestamp {
        color: $text-muted;
        text-style: italic;
    }
    
    ChatMessageRenderer .role {
        color: $text-primary;
        text-style: bold;
    }
    """

    def __init__(
        self,
        message: ChatMessage,
        show_timestamp: bool = True,
        show_role: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.message = message
        self.show_timestamp = show_timestamp
        self.show_role = show_role
        self._setup_styling()

    def _setup_styling(self) -> None:
        """Setup widget styling based on message role and status."""
        # Add role-based class
        self.add_class(self.message.role.value)

        # Add status-based class
        if self.message.status == MessageStatus.ERROR:
            self.add_class("error")

    def render(self) -> Text:
        """Render the chat message."""
        text = Text()

        # Add header with role and timestamp
        if self.show_role or self.show_timestamp:
            header_parts = []

            if self.show_role:
                role_text = Text(self.message.role.value.title(), style="bold")
                header_parts.append(role_text)

            if self.show_timestamp:
                timestamp_str = self.message.timestamp.strftime("%H:%M:%S")
                timestamp_text = Text(f"[{timestamp_str}]", style="dim")
                header_parts.append(timestamp_text)

            if header_parts:
                header = Text(" • ").join(header_parts)
                text.append(header)
                text.append("\n")

        # Add message content
        if self.message.content:
            # Try to render as markdown if it looks like markdown
            if self._looks_like_markdown(self.message.content):
                try:
                    console = Console(width=self.size.width or 80)
                    with console.capture() as capture:
                        console.print(Markdown(self.message.content))
                    text.append(capture.get())
                except Exception:
                    # Fallback to plain text
                    text.append(self.message.content)
            else:
                text.append(self.message.content)

        # Add tool calls if present
        if self.message.tool_calls:
            text.append("\n\n")
            text.append("🔧 Tool Calls:", style="bold cyan")
            for i, tool_call in enumerate(self.message.tool_calls, 1):
                text.append(
                    f"\n{i}. {tool_call.get('function', {}).get('name', 'Unknown')}"
                )

        # Add attachments if present
        if self.message.attachments:
            text.append("\n\n")
            text.append("📎 Attachments:", style="bold magenta")
            for attachment in self.message.attachments:
                text.append(f"\n• {attachment}")

        return text

    def _looks_like_markdown(self, content: str) -> bool:
        """Check if content looks like markdown."""
        markdown_indicators = ["```", "##", "**", "*", "`", "[", "](", "- ", "1. "]
        return any(indicator in content for indicator in markdown_indicators)


class StreamingResponseWidget(ScrollableContainer):
    """Widget for displaying streaming AI responses."""

    DEFAULT_CSS = """
    StreamingResponseWidget {
        border: solid $primary;
        height: auto;
        max-height: 20;
    }
    
    StreamingResponseWidget .content {
        padding: 1;
    }
    
    StreamingResponseWidget .cursor {
        background: $primary;
        color: $primary-background;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_widget = Static("", classes="content")
        self.current_content = ""
        self.is_streaming = False
        self.cursor_timer: Optional[Timer] = None
        self.show_cursor = True

    def compose(self) -> ComposeResult:
        """Compose the streaming widget."""
        yield self.content_widget

    def start_streaming(self) -> None:
        """Start streaming mode."""
        self.is_streaming = True
        self.current_content = ""
        self._start_cursor_animation()
        self._update_display()

    def append_content(self, content: str) -> None:
        """Append content to the streaming response."""
        if not self.is_streaming:
            return

        self.current_content += content
        self._update_display()

        # Auto-scroll to bottom
        self.scroll_end(animate=False)

    def finish_streaming(self) -> None:
        """Finish streaming mode."""
        self.is_streaming = False
        self._stop_cursor_animation()
        self._update_display()

    def clear_content(self) -> None:
        """Clear all content."""
        self.current_content = ""
        self.is_streaming = False
        self._stop_cursor_animation()
        self._update_display()

    def _start_cursor_animation(self) -> None:
        """Start cursor blinking animation."""
        if self.cursor_timer:
            self.cursor_timer.stop()

        self.cursor_timer = self.set_interval(0.5, self._toggle_cursor)

    def _stop_cursor_animation(self) -> None:
        """Stop cursor blinking animation."""
        if self.cursor_timer:
            self.cursor_timer.stop()
            self.cursor_timer = None
        self.show_cursor = False

    def _toggle_cursor(self) -> None:
        """Toggle cursor visibility."""
        self.show_cursor = not self.show_cursor
        self._update_display()

    def _update_display(self) -> None:
        """Update the display content."""
        display_content = self.current_content

        if self.is_streaming and self.show_cursor:
            display_content += "█"

        # Try to render as markdown
        try:
            console = Console(width=self.size.width or 80)
            with console.capture() as capture:
                console.print(Markdown(display_content))
            rendered = capture.get()
        except Exception:
            rendered = display_content

        self.content_widget.update(rendered)


class CodeBlockWidget(Static):
    """Widget for displaying code blocks with syntax highlighting."""

    DEFAULT_CSS = """
    CodeBlockWidget {
        border: solid $accent;
        margin: 1 0;
    }
    
    CodeBlockWidget .header {
        background: $accent;
        color: $accent-background;
        padding: 0 1;
        text-style: bold;
    }
    
    CodeBlockWidget .content {
        padding: 1;
        background: $surface;
    }
    """

    def __init__(
        self,
        code: str,
        language: str = "text",
        filename: Optional[str] = None,
        show_line_numbers: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.code = code
        self.language = language
        self.filename = filename
        self.show_line_numbers = show_line_numbers

    def compose(self) -> ComposeResult:
        """Compose the code block widget."""
        # Header with language and filename
        header_text = self.language.upper()
        if self.filename:
            header_text += f" • {self.filename}"

        yield Static(header_text, classes="header")

        # Code content with syntax highlighting
        try:
            syntax = Syntax(
                self.code,
                self.language,
                line_numbers=self.show_line_numbers,
                theme="monokai",
            )
            yield Static(syntax, classes="content")
        except Exception:
            # Fallback to plain text
            yield Static(self.code, classes="content")


class DiffWidget(Static):
    """Widget for displaying code diffs."""

    DEFAULT_CSS = """
    DiffWidget {
        border: solid $warning;
        margin: 1 0;
    }
    
    DiffWidget .header {
        background: $warning;
        color: $warning-background;
        padding: 0 1;
        text-style: bold;
    }
    
    DiffWidget .content {
        padding: 1;
        background: $surface;
    }
    
    DiffWidget .added {
        background: $success-background;
        color: $success;
    }
    
    DiffWidget .removed {
        background: $error-background;
        color: $error;
    }
    
    DiffWidget .context {
        color: $text-muted;
    }
    """

    def __init__(
        self,
        old_content: str,
        new_content: str,
        filename: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.old_content = old_content
        self.new_content = new_content
        self.filename = filename

    def compose(self) -> ComposeResult:
        """Compose the diff widget."""
        # Header
        header_text = "DIFF"
        if self.filename:
            header_text += f" • {self.filename}"

        yield Static(header_text, classes="header")

        # Diff content
        diff_text = self._generate_diff()
        yield Static(diff_text, classes="content")

    def _generate_diff(self) -> Text:
        """Generate diff text with styling."""
        import difflib

        old_lines = self.old_content.splitlines(keepends=True)
        new_lines = self.new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines, new_lines, fromfile="old", tofile="new", lineterm=""
        )

        text = Text()
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                text.append(line, style="green")
            elif line.startswith("-") and not line.startswith("---"):
                text.append(line, style="red")
            elif line.startswith("@@"):
                text.append(line, style="cyan")
            else:
                text.append(line, style="dim")
            text.append("\n")

        return text


class ToolCallWidget(Container):
    """Widget for displaying tool calls and their results."""

    DEFAULT_CSS = """
    ToolCallWidget {
        border: solid $accent;
        margin: 1 0;
        height: auto;
    }
    
    ToolCallWidget .header {
        background: $accent;
        color: $accent-background;
        padding: 0 1;
        text-style: bold;
    }
    
    ToolCallWidget .tool-name {
        color: $primary;
        text-style: bold;
    }
    
    ToolCallWidget .parameters {
        background: $surface;
        padding: 1;
        margin: 1 0;
    }
    
    ToolCallWidget .result {
        background: $success-background;
        padding: 1;
        margin: 1 0;
    }
    
    ToolCallWidget .error {
        background: $error-background;
        color: $error;
        padding: 1;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.parameters = parameters
        self.result = result
        self.error = error

    def compose(self) -> ComposeResult:
        """Compose the tool call widget."""
        # Header
        yield Static(f"🔧 Tool Call: {self.tool_name}", classes="header")

        # Parameters
        if self.parameters:
            params_text = self._format_parameters()
            yield Static(params_text, classes="parameters")

        # Result or error
        if self.error:
            yield Static(f"❌ Error: {self.error}", classes="error")
        elif self.result:
            yield Static(f"✅ Result:\n{self.result}", classes="result")

    def _format_parameters(self) -> str:
        """Format parameters for display."""
        lines = ["Parameters:"]
        for key, value in self.parameters.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:97] + "..."
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


class ChatContainer(ScrollableContainer):
    """Main container for chat messages."""

    DEFAULT_CSS = """
    ChatContainer {
        height: 1fr;
        padding: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages: List[ChatMessage] = []
        self.message_widgets: List[Widget] = []

    def add_message(self, message: ChatMessage) -> None:
        """Add a new message to the chat."""
        self.messages.append(message)

        # Create appropriate widget based on message content
        if message.tool_calls:
            for tool_call in message.tool_calls:
                widget = ToolCallWidget(
                    tool_name=tool_call.get("function", {}).get("name", "Unknown"),
                    parameters=tool_call.get("function", {}).get("arguments", {}),
                )
                self.mount(widget)
                self.message_widgets.append(widget)

        # Regular message widget
        message_widget = ChatMessageRenderer(message)
        self.mount(message_widget)
        self.message_widgets.append(message_widget)

        # Auto-scroll to bottom
        self.call_after_refresh(self.scroll_end)

    def clear_messages(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        for widget in self.message_widgets:
            widget.remove()
        self.message_widgets.clear()

    def get_messages(self) -> List[ChatMessage]:
        """Get all messages."""
        return self.messages.copy()


# Message events
class MessageAdded(Message):
    """Message added to chat."""

    def __init__(self, message: ChatMessage) -> None:
        super().__init__()
        self.message = message


class StreamingStarted(Message):
    """Streaming response started."""


class StreamingContent(Message):
    """Streaming content received."""

    def __init__(self, content: str) -> None:
        super().__init__()
        self.content = content


class StreamingFinished(Message):
    """Streaming response finished."""
