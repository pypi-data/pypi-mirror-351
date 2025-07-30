"""
Selection components for Kritrima AI CLI terminal interface.

This module provides selection widgets for models, providers, sessions,
and history browsing with search and filtering capabilities.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import (
    Button,
    Input,
    ListItem,
    ListView,
    Static,
)

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about an AI model."""

    name: str
    provider: str
    description: str = ""
    context_length: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    is_available: bool = True
    last_used: Optional[datetime] = None
    usage_count: int = 0

    @property
    def display_name(self) -> str:
        """Get display name for the model."""
        return f"{self.provider}/{self.name}"

    @property
    def cost_info(self) -> str:
        """Get cost information string."""
        if self.input_cost > 0 or self.output_cost > 0:
            return f"${self.input_cost:.4f}/${self.output_cost:.4f} per 1K tokens"
        return "Cost unknown"


@dataclass
class ProviderInfo:
    """Information about an AI provider."""

    name: str
    display_name: str
    description: str = ""
    models: List[str] = field(default_factory=list)
    is_configured: bool = False
    is_connected: bool = False
    api_key_set: bool = False
    rate_limit: Optional[int] = None
    last_error: Optional[str] = None

    @property
    def status_icon(self) -> str:
        """Get status icon for the provider."""
        if not self.is_configured:
            return "⚙️"
        elif not self.is_connected:
            return "🔴"
        elif self.last_error:
            return "⚠️"
        else:
            return "🟢"


@dataclass
class SessionInfo:
    """Information about a chat session."""

    id: str
    name: str
    created_at: datetime
    last_used: datetime
    message_count: int = 0
    token_count: int = 0
    model_used: str = ""
    provider_used: str = ""
    workspace_path: str = ""
    tags: List[str] = field(default_factory=list)

    @property
    def duration(self) -> timedelta:
        """Get session duration."""
        return self.last_used - self.created_at

    @property
    def display_name(self) -> str:
        """Get display name for the session."""
        return f"{self.name} ({self.message_count} msgs)"


@dataclass
class HistoryEntry:
    """History entry for commands or interactions."""

    id: str
    timestamp: datetime
    command: str
    result: str = ""
    success: bool = True
    duration: float = 0.0
    session_id: str = ""
    model_used: str = ""

    @property
    def display_text(self) -> str:
        """Get display text for the entry."""
        time_str = self.timestamp.strftime("%H:%M:%S")
        status = "✅" if self.success else "❌"
        return f"{time_str} {status} {self.command[:50]}..."


class ModelSelector(Container):
    """Widget for selecting AI models with search and filtering."""

    DEFAULT_CSS = """
    ModelSelector {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    ModelSelector .header {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    ModelSelector .search {
        margin-bottom: 1;
    }
    
    ModelSelector .model-list {
        height: 15;
        border: solid $border;
    }
    
    ModelSelector .model-item {
        padding: 1;
        margin: 0 0 1 0;
    }
    
    ModelSelector .model-item.selected {
        background: $primary;
        color: $primary-background;
    }
    
    ModelSelector .model-item.available {
        color: $success;
    }
    
    ModelSelector .model-item.unavailable {
        color: $error;
        text-style: dim;
    }
    
    ModelSelector .model-name {
        text-style: bold;
    }
    
    ModelSelector .model-details {
        color: $text-muted;
        text-style: italic;
    }
    """

    def __init__(self, models: List[ModelInfo], **kwargs):
        super().__init__(**kwargs)
        self.models = models
        self.filtered_models = models.copy()
        self.selected_model: Optional[ModelInfo] = None
        self.search_query = ""
        self.filter_provider = ""
        self.sort_by = "name"  # name, provider, last_used, usage_count

    def compose(self) -> ComposeResult:
        """Compose the model selector."""
        yield Static("🤖 Select Model", classes="header")

        # Search and filter controls
        with Horizontal(classes="search"):
            yield Input(placeholder="Search models...", id="search-input")
            yield Button("Filter", id="filter-btn", variant="outline")
            yield Button("Sort", id="sort-btn", variant="outline")

        # Model list
        yield ListView(id="model-list", classes="model-list")

        # Selected model info
        yield Static("", id="selected-info")

    def on_mount(self) -> None:
        """Initialize the model list when mounted."""
        self.update_model_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value.lower()
            self.filter_models()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "filter-btn":
            self.show_filter_options()
        elif event.button.id == "sort-btn":
            self.show_sort_options()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle model selection."""
        if event.list_view.id == "model-list" and event.item:
            model_index = event.item.index
            if 0 <= model_index < len(self.filtered_models):
                self.selected_model = self.filtered_models[model_index]
                self.update_selected_info()
                self.post_message(ModelSelected(self.selected_model))

    def filter_models(self) -> None:
        """Filter models based on search query and filters."""
        self.filtered_models = []

        for model in self.models:
            # Search filter
            if self.search_query:
                searchable = (
                    f"{model.name} {model.provider} {model.description}".lower()
                )
                if self.search_query not in searchable:
                    continue

            # Provider filter
            if self.filter_provider and model.provider != self.filter_provider:
                continue

            self.filtered_models.append(model)

        # Sort models
        self.sort_models()
        self.update_model_list()

    def sort_models(self) -> None:
        """Sort filtered models."""
        if self.sort_by == "name":
            self.filtered_models.sort(key=lambda m: m.name)
        elif self.sort_by == "provider":
            self.filtered_models.sort(key=lambda m: (m.provider, m.name))
        elif self.sort_by == "last_used":
            self.filtered_models.sort(
                key=lambda m: m.last_used or datetime.min, reverse=True
            )
        elif self.sort_by == "usage_count":
            self.filtered_models.sort(key=lambda m: m.usage_count, reverse=True)

    def update_model_list(self) -> None:
        """Update the model list display."""
        model_list = self.query_one("#model-list", ListView)
        model_list.clear()

        for model in self.filtered_models:
            # Create model item
            item_text = self._format_model_item(model)
            list_item = ListItem(Static(item_text), classes="model-item")

            if model.is_available:
                list_item.add_class("available")
            else:
                list_item.add_class("unavailable")

            model_list.append(list_item)

    def update_selected_info(self) -> None:
        """Update selected model information display."""
        info_widget = self.query_one("#selected-info", Static)

        if self.selected_model:
            info_text = self._format_model_details(self.selected_model)
            info_widget.update(info_text)
        else:
            info_widget.update("No model selected")

    def _format_model_item(self, model: ModelInfo) -> Text:
        """Format a model item for display."""
        text = Text()

        # Model name and provider
        text.append(f"{model.display_name}", style="bold")

        # Availability indicator
        if model.is_available:
            text.append(" ✅", style="green")
        else:
            text.append(" ❌", style="red")

        # Usage info
        if model.usage_count > 0:
            text.append(f" ({model.usage_count} uses)", style="dim")

        # Description
        if model.description:
            text.append(f"\n  {model.description[:60]}...", style="italic dim")

        return text

    def _format_model_details(self, model: ModelInfo) -> str:
        """Format detailed model information."""
        lines = [
            f"Selected: {model.display_name}",
            f"Description: {model.description or 'No description'}",
            (
                f"Context Length: {model.context_length:,} tokens"
                if model.context_length > 0
                else "Context Length: Unknown"
            ),
            f"Cost: {model.cost_info}",
            f"Capabilities: {', '.join(model.capabilities) if model.capabilities else 'Unknown'}",
            f"Usage: {model.usage_count} times",
            f"Last Used: {model.last_used.strftime('%Y-%m-%d %H:%M') if model.last_used else 'Never'}",
        ]
        return "\n".join(lines)

    def show_filter_options(self) -> None:
        """Show filter options dialog."""
        # This would typically open a modal dialog
        # For now, cycle through provider filters
        providers = list(set(model.provider for model in self.models))
        if not self.filter_provider:
            self.filter_provider = providers[0] if providers else ""
        else:
            try:
                current_index = providers.index(self.filter_provider)
                next_index = (current_index + 1) % (len(providers) + 1)
                self.filter_provider = (
                    providers[next_index] if next_index < len(providers) else ""
                )
            except ValueError:
                self.filter_provider = ""

        self.filter_models()

    def show_sort_options(self) -> None:
        """Show sort options dialog."""
        sort_options = ["name", "provider", "last_used", "usage_count"]
        try:
            current_index = sort_options.index(self.sort_by)
            next_index = (current_index + 1) % len(sort_options)
            self.sort_by = sort_options[next_index]
        except ValueError:
            self.sort_by = "name"

        self.filter_models()


class ProviderSelector(Container):
    """Widget for selecting AI providers with configuration status."""

    DEFAULT_CSS = """
    ProviderSelector {
        height: auto;
        border: solid $secondary;
        padding: 1;
    }
    
    ProviderSelector .header {
        text-style: bold;
        color: $secondary;
        margin-bottom: 1;
    }
    
    ProviderSelector .provider-list {
        height: 10;
        border: solid $border;
    }
    
    ProviderSelector .provider-item {
        padding: 1;
        margin: 0 0 1 0;
    }
    
    ProviderSelector .provider-item.selected {
        background: $secondary;
        color: $secondary-background;
    }
    
    ProviderSelector .provider-item.configured {
        border-left: thick $success;
    }
    
    ProviderSelector .provider-item.unconfigured {
        border-left: thick $warning;
    }
    
    ProviderSelector .provider-item.error {
        border-left: thick $error;
    }
    """

    def __init__(self, providers: List[ProviderInfo], **kwargs):
        super().__init__(**kwargs)
        self.providers = providers
        self.selected_provider: Optional[ProviderInfo] = None

    def compose(self) -> ComposeResult:
        """Compose the provider selector."""
        yield Static("🌐 Select Provider", classes="header")

        # Provider list
        yield ListView(id="provider-list", classes="provider-list")

        # Selected provider info
        yield Static("", id="provider-info")

        # Action buttons
        with Horizontal():
            yield Button("Configure", id="configure-btn", variant="primary")
            yield Button("Test", id="test-btn", variant="outline")
            yield Button("Refresh", id="refresh-btn", variant="outline")

    def on_mount(self) -> None:
        """Initialize the provider list when mounted."""
        self.update_provider_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle provider selection."""
        if event.list_view.id == "provider-list" and event.item:
            provider_index = event.item.index
            if 0 <= provider_index < len(self.providers):
                self.selected_provider = self.providers[provider_index]
                self.update_provider_info()
                self.post_message(ProviderSelected(self.selected_provider))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if not self.selected_provider:
            return

        if event.button.id == "configure-btn":
            self.post_message(ConfigureProvider(self.selected_provider))
        elif event.button.id == "test-btn":
            self.post_message(TestProvider(self.selected_provider))
        elif event.button.id == "refresh-btn":
            self.post_message(RefreshProviders())

    def update_provider_list(self) -> None:
        """Update the provider list display."""
        provider_list = self.query_one("#provider-list", ListView)
        provider_list.clear()

        for provider in self.providers:
            # Create provider item
            item_text = self._format_provider_item(provider)
            list_item = ListItem(Static(item_text), classes="provider-item")

            # Add status class
            if provider.last_error:
                list_item.add_class("error")
            elif provider.is_configured:
                list_item.add_class("configured")
            else:
                list_item.add_class("unconfigured")

            provider_list.append(list_item)

    def update_provider_info(self) -> None:
        """Update selected provider information display."""
        info_widget = self.query_one("#provider-info", Static)

        if self.selected_provider:
            info_text = self._format_provider_details(self.selected_provider)
            info_widget.update(info_text)
        else:
            info_widget.update("No provider selected")

    def _format_provider_item(self, provider: ProviderInfo) -> Text:
        """Format a provider item for display."""
        text = Text()

        # Status icon and name
        text.append(f"{provider.status_icon} {provider.display_name}", style="bold")

        # Model count
        if provider.models:
            text.append(f" ({len(provider.models)} models)", style="dim")

        # Description
        if provider.description:
            text.append(f"\n  {provider.description}", style="italic dim")

        return text

    def _format_provider_details(self, provider: ProviderInfo) -> str:
        """Format detailed provider information."""
        lines = [
            f"Provider: {provider.display_name}",
            f"Description: {provider.description or 'No description'}",
            f"Models: {len(provider.models)} available",
            f"Configured: {'Yes' if provider.is_configured else 'No'}",
            f"Connected: {'Yes' if provider.is_connected else 'No'}",
            f"API Key: {'Set' if provider.api_key_set else 'Not set'}",
        ]

        if provider.rate_limit:
            lines.append(f"Rate Limit: {provider.rate_limit} requests/minute")

        if provider.last_error:
            lines.append(f"Last Error: {provider.last_error}")

        return "\n".join(lines)


class SessionBrowser(Container):
    """Widget for browsing and managing chat sessions."""

    DEFAULT_CSS = """
    SessionBrowser {
        height: auto;
        border: solid $accent;
        padding: 1;
    }
    
    SessionBrowser .header {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    SessionBrowser .search {
        margin-bottom: 1;
    }
    
    SessionBrowser .session-list {
        height: 12;
        border: solid $border;
    }
    
    SessionBrowser .session-item {
        padding: 1;
        margin: 0 0 1 0;
    }
    
    SessionBrowser .session-item.selected {
        background: $accent;
        color: $accent-background;
    }
    
    SessionBrowser .session-name {
        text-style: bold;
    }
    
    SessionBrowser .session-details {
        color: $text-muted;
        text-style: italic;
    }
    """

    def __init__(self, sessions: List[SessionInfo], **kwargs):
        super().__init__(**kwargs)
        self.sessions = sessions
        self.filtered_sessions = sessions.copy()
        self.selected_session: Optional[SessionInfo] = None
        self.search_query = ""
        self.sort_by = "last_used"  # last_used, created_at, name, message_count

    def compose(self) -> ComposeResult:
        """Compose the session browser."""
        yield Static("💬 Browse Sessions", classes="header")

        # Search and controls
        with Horizontal(classes="search"):
            yield Input(placeholder="Search sessions...", id="search-input")
            yield Button("Sort", id="sort-btn", variant="outline")
            yield Button("New", id="new-btn", variant="primary")

        # Session list
        yield ListView(id="session-list", classes="session-list")

        # Session info
        yield Static("", id="session-info")

        # Action buttons
        with Horizontal():
            yield Button("Load", id="load-btn", variant="primary")
            yield Button("Rename", id="rename-btn", variant="outline")
            yield Button("Delete", id="delete-btn", variant="error")

    def on_mount(self) -> None:
        """Initialize the session list when mounted."""
        self.update_session_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value.lower()
            self.filter_sessions()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "sort-btn":
            self.cycle_sort()
        elif event.button.id == "new-btn":
            self.post_message(NewSession())
        elif event.button.id == "load-btn" and self.selected_session:
            self.post_message(LoadSession(self.selected_session))
        elif event.button.id == "rename-btn" and self.selected_session:
            self.post_message(RenameSession(self.selected_session))
        elif event.button.id == "delete-btn" and self.selected_session:
            self.post_message(DeleteSession(self.selected_session))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle session selection."""
        if event.list_view.id == "session-list" and event.item:
            session_index = event.item.index
            if 0 <= session_index < len(self.filtered_sessions):
                self.selected_session = self.filtered_sessions[session_index]
                self.update_session_info()

    def filter_sessions(self) -> None:
        """Filter sessions based on search query."""
        self.filtered_sessions = []

        for session in self.sessions:
            if self.search_query:
                searchable = f"{session.name} {session.model_used} {session.workspace_path}".lower()
                if self.search_query not in searchable:
                    continue

            self.filtered_sessions.append(session)

        self.sort_sessions()
        self.update_session_list()

    def sort_sessions(self) -> None:
        """Sort filtered sessions."""
        if self.sort_by == "last_used":
            self.filtered_sessions.sort(key=lambda s: s.last_used, reverse=True)
        elif self.sort_by == "created_at":
            self.filtered_sessions.sort(key=lambda s: s.created_at, reverse=True)
        elif self.sort_by == "name":
            self.filtered_sessions.sort(key=lambda s: s.name)
        elif self.sort_by == "message_count":
            self.filtered_sessions.sort(key=lambda s: s.message_count, reverse=True)

    def cycle_sort(self) -> None:
        """Cycle through sort options."""
        sort_options = ["last_used", "created_at", "name", "message_count"]
        try:
            current_index = sort_options.index(self.sort_by)
            next_index = (current_index + 1) % len(sort_options)
            self.sort_by = sort_options[next_index]
        except ValueError:
            self.sort_by = "last_used"

        self.filter_sessions()

    def update_session_list(self) -> None:
        """Update the session list display."""
        session_list = self.query_one("#session-list", ListView)
        session_list.clear()

        for session in self.filtered_sessions:
            # Create session item
            item_text = self._format_session_item(session)
            list_item = ListItem(Static(item_text), classes="session-item")
            session_list.append(list_item)

    def update_session_info(self) -> None:
        """Update selected session information display."""
        info_widget = self.query_one("#session-info", Static)

        if self.selected_session:
            info_text = self._format_session_details(self.selected_session)
            info_widget.update(info_text)
        else:
            info_widget.update("No session selected")

    def _format_session_item(self, session: SessionInfo) -> Text:
        """Format a session item for display."""
        text = Text()

        # Session name
        text.append(session.name, style="bold")

        # Message count and model
        text.append(
            f" ({session.message_count} msgs, {session.model_used})", style="dim"
        )

        # Last used time
        time_ago = datetime.now() - session.last_used
        if time_ago.days > 0:
            time_str = f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600}h ago"
        else:
            time_str = f"{time_ago.seconds // 60}m ago"

        text.append(f"\n  Last used: {time_str}", style="italic dim")

        return text

    def _format_session_details(self, session: SessionInfo) -> str:
        """Format detailed session information."""
        lines = [
            f"Session: {session.name}",
            f"ID: {session.id}",
            f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Last Used: {session.last_used.strftime('%Y-%m-%d %H:%M')}",
            f"Duration: {session.duration}",
            f"Messages: {session.message_count}",
            f"Tokens: {session.token_count:,}",
            f"Model: {session.model_used} ({session.provider_used})",
            f"Workspace: {session.workspace_path or 'None'}",
        ]

        if session.tags:
            lines.append(f"Tags: {', '.join(session.tags)}")

        return "\n".join(lines)


class HistoryBrowser(Container):
    """Widget for browsing command and interaction history."""

    DEFAULT_CSS = """
    HistoryBrowser {
        height: auto;
        border: solid $warning;
        padding: 1;
    }
    
    HistoryBrowser .header {
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    
    HistoryBrowser .search {
        margin-bottom: 1;
    }
    
    HistoryBrowser .history-list {
        height: 10;
        border: solid $border;
    }
    
    HistoryBrowser .history-item {
        padding: 1;
        margin: 0 0 1 0;
    }
    
    HistoryBrowser .history-item.selected {
        background: $warning;
        color: $warning-background;
    }
    
    HistoryBrowser .history-item.success {
        border-left: thick $success;
    }
    
    HistoryBrowser .history-item.error {
        border-left: thick $error;
    }
    """

    def __init__(self, history: List[HistoryEntry], **kwargs):
        super().__init__(**kwargs)
        self.history = history
        self.filtered_history = history.copy()
        self.selected_entry: Optional[HistoryEntry] = None
        self.search_query = ""
        self.filter_success = None  # None, True, False

    def compose(self) -> ComposeResult:
        """Compose the history browser."""
        yield Static("📜 Command History", classes="header")

        # Search and filter controls
        with Horizontal(classes="search"):
            yield Input(placeholder="Search history...", id="search-input")
            yield Button("Filter", id="filter-btn", variant="outline")
            yield Button("Clear", id="clear-btn", variant="error")

        # History list
        yield ListView(id="history-list", classes="history-list")

        # Entry details
        yield Static("", id="entry-details")

        # Action buttons
        with Horizontal():
            yield Button("Rerun", id="rerun-btn", variant="primary")
            yield Button("Copy", id="copy-btn", variant="outline")
            yield Button("Export", id="export-btn", variant="outline")

    def on_mount(self) -> None:
        """Initialize the history list when mounted."""
        self.update_history_list()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value.lower()
            self.filter_history()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "filter-btn":
            self.cycle_filter()
        elif event.button.id == "clear-btn":
            self.post_message(ClearHistory())
        elif event.button.id == "rerun-btn" and self.selected_entry:
            self.post_message(RerunCommand(self.selected_entry))
        elif event.button.id == "copy-btn" and self.selected_entry:
            self.post_message(CopyCommand(self.selected_entry))
        elif event.button.id == "export-btn":
            self.post_message(ExportHistory(self.filtered_history))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle history entry selection."""
        if event.list_view.id == "history-list" and event.item:
            entry_index = event.item.index
            if 0 <= entry_index < len(self.filtered_history):
                self.selected_entry = self.filtered_history[entry_index]
                self.update_entry_details()

    def filter_history(self) -> None:
        """Filter history based on search query and filters."""
        self.filtered_history = []

        for entry in self.history:
            # Search filter
            if self.search_query:
                searchable = f"{entry.command} {entry.result}".lower()
                if self.search_query not in searchable:
                    continue

            # Success filter
            if self.filter_success is not None and entry.success != self.filter_success:
                continue

            self.filtered_history.append(entry)

        # Sort by timestamp (newest first)
        self.filtered_history.sort(key=lambda e: e.timestamp, reverse=True)
        self.update_history_list()

    def cycle_filter(self) -> None:
        """Cycle through success filter options."""
        if self.filter_success is None:
            self.filter_success = True  # Show only successful
        elif self.filter_success is True:
            self.filter_success = False  # Show only failed
        else:
            self.filter_success = None  # Show all

        self.filter_history()

    def update_history_list(self) -> None:
        """Update the history list display."""
        history_list = self.query_one("#history-list", ListView)
        history_list.clear()

        for entry in self.filtered_history:
            # Create history item
            item_text = self._format_history_item(entry)
            list_item = ListItem(Static(item_text), classes="history-item")

            # Add status class
            if entry.success:
                list_item.add_class("success")
            else:
                list_item.add_class("error")

            history_list.append(list_item)

    def update_entry_details(self) -> None:
        """Update selected entry details display."""
        details_widget = self.query_one("#entry-details", Static)

        if self.selected_entry:
            details_text = self._format_entry_details(self.selected_entry)
            details_widget.update(details_text)
        else:
            details_widget.update("No entry selected")

    def _format_history_item(self, entry: HistoryEntry) -> Text:
        """Format a history item for display."""
        text = Text()

        # Timestamp and status
        time_str = entry.timestamp.strftime("%H:%M:%S")
        status = "✅" if entry.success else "❌"
        text.append(f"{time_str} {status}", style="bold")

        # Command (truncated)
        command = (
            entry.command[:50] + "..." if len(entry.command) > 50 else entry.command
        )
        text.append(f" {command}", style="")

        # Duration
        if entry.duration > 0:
            text.append(f" ({entry.duration:.2f}s)", style="dim")

        return text

    def _format_entry_details(self, entry: HistoryEntry) -> str:
        """Format detailed entry information."""
        lines = [
            f"Timestamp: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Command: {entry.command}",
            f"Success: {'Yes' if entry.success else 'No'}",
            f"Duration: {entry.duration:.3f} seconds",
        ]

        if entry.session_id:
            lines.append(f"Session: {entry.session_id}")

        if entry.model_used:
            lines.append(f"Model: {entry.model_used}")

        if entry.result:
            lines.append(f"Result: {entry.result[:200]}...")

        return "\n".join(lines)


# Selection messages
class ModelSelected(Message):
    """Model selected message."""

    def __init__(self, model: ModelInfo) -> None:
        super().__init__()
        self.model = model


class ProviderSelected(Message):
    """Provider selected message."""

    def __init__(self, provider: ProviderInfo) -> None:
        super().__init__()
        self.provider = provider


class ConfigureProvider(Message):
    """Configure provider message."""

    def __init__(self, provider: ProviderInfo) -> None:
        super().__init__()
        self.provider = provider


class TestProvider(Message):
    """Test provider message."""

    def __init__(self, provider: ProviderInfo) -> None:
        super().__init__()
        self.provider = provider


class RefreshProviders(Message):
    """Refresh providers message."""


class NewSession(Message):
    """New session message."""


class LoadSession(Message):
    """Load session message."""

    def __init__(self, session: SessionInfo) -> None:
        super().__init__()
        self.session = session


class RenameSession(Message):
    """Rename session message."""

    def __init__(self, session: SessionInfo) -> None:
        super().__init__()
        self.session = session


class DeleteSession(Message):
    """Delete session message."""

    def __init__(self, session: SessionInfo) -> None:
        super().__init__()
        self.session = session


class ClearHistory(Message):
    """Clear history message."""


class RerunCommand(Message):
    """Rerun command message."""

    def __init__(self, entry: HistoryEntry) -> None:
        super().__init__()
        self.entry = entry


class CopyCommand(Message):
    """Copy command message."""

    def __init__(self, entry: HistoryEntry) -> None:
        super().__init__()
        self.entry = entry


class ExportHistory(Message):
    """Export history message."""

    def __init__(self, history: List[HistoryEntry]) -> None:
        super().__init__()
        self.history = history
