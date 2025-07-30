"""
Advanced terminal interface for Kritrima AI CLI.

This module implements a sophisticated terminal-based user interface using
Rich and Textual, providing:
- Interactive chat interface with streaming responses
- Advanced UI widgets (spinners, overlays, status components)
- Enhanced input handling with file suggestions and slash commands
- Real-time response rendering with syntax highlighting
- Session management and command history
- Advanced text editing capabilities
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.screen import ModalScreen
from textual.validation import ValidationResult, Validator
from textual.widgets import (
    Button,
    Checkbox,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Static,
    TabbedContent,
    TabPane,
)

from kritrima_ai.agent.agent_loop import AgentLoop, AgentResponse, ResponseType
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.providers.model_manager import ModelManager
from kritrima_ai.security.approval import ApprovalDecision
from kritrima_ai.storage.command_history import CommandHistory
from kritrima_ai.storage.session_manager import SessionManager

# Import new UI components
from kritrima_ai.ui.widgets import (
    ApprovalModeOverlay,
    ChatContainer,
)
from kritrima_ai.ui.widgets import (
    ChatMessage as NewChatMessage,  # Text Buffer; Overlays; Spinners; Advanced Input; Chat Components; Status Components; Selection Components
)
from kritrima_ai.ui.widgets import (
    CodeBlockWidget,
    ConfigOverlay,
    ConnectionIndicator,
    ConnectionStatus,
    ContextIndicator,
    ContextInfo,
    DebugOverlay,
    DiffOverlay,
    DiffWidget,
    FileSuggestionsOverlay,
    FileTagInput,
    HelpOverlay,
    HistoryBrowser,
    HistoryEntry,
    ModelInfo,
    ModelSelector,
    PerformanceIndicator,
    ProviderInfo,
    ProviderSelector,
    SessionBrowser,
    SessionInfo,
    StatusBar,
    StreamingResponseWidget,
    ThinkingSpinner,
    ToolCallWidget,
)
from kritrima_ai.utils.file_utils import get_file_suggestions
from kritrima_ai.utils.input_utils import expand_file_tags
from kritrima_ai.utils.logger import get_logger
from kritrima_ai.utils.slash_commands import (
    get_command_processor,
)

logger = get_logger(__name__)


class ChatMessage:
    """Represents a chat message with metadata."""

    def __init__(
        self,
        content: str,
        role: str = "user",
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.role = role
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}


class SlashCommandValidator(Validator):
    """Validator for slash commands using the command processor."""

    def __init__(self):
        super().__init__()
        self.command_processor = get_command_processor()

    def validate(self, value: str) -> ValidationResult:
        """Validate slash command input."""
        if value.startswith("/"):
            if self.command_processor.is_command(value):
                return self.success()
            else:
                command = value.split()[0]
                suggestions = self.command_processor.get_completions(command)
                if suggestions:
                    return self.failure(
                        f"Unknown command: {command}. Did you mean: {', '.join(suggestions[:3])}?"
                    )
                else:
                    return self.failure(f"Unknown command: {command}")
        return self.success()


class EnhancedFileTagInput(FileTagInput):
    """Enhanced input widget with file tag expansion and slash command support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_processor = get_command_processor()
        self.file_suggestions: List[str] = []
        self.current_suggestion_index = 0
        self.validator = SlashCommandValidator()

    async def on_key(self, event: events.Key) -> None:
        """Handle key events for file suggestions and command completion."""
        if event.key == "tab":
            if self.value.startswith("/"):
                await self._handle_command_completion()
            elif "@" in self.value:
                await self._handle_file_completion()
        elif event.key == "ctrl+space":
            if self.value.startswith("/"):
                await self._show_command_suggestions()
            elif "@" in self.value:
                await self._show_file_suggestions()
        else:
            await super().on_key(event)

    async def _handle_command_completion(self) -> None:
        """Handle slash command completion."""
        current_value = self.value
        if current_value.startswith("/"):
            completions = self.command_processor.get_completions(current_value)
            if completions:
                # Replace with first completion
                self.value = completions[0]
                if not self.value.endswith(" "):
                    self.value += " "
                self.cursor_position = len(self.value)

    async def _handle_file_completion(self) -> None:
        """Handle file path completion."""
        current_value = self.value
        if "@" in current_value:
            prefix = current_value.split("@")[-1]
            suggestions = get_file_suggestions(prefix, limit=10)
            if suggestions:
                # Replace the current partial path with the first suggestion
                parts = current_value.rsplit("@", 1)
                self.value = parts[0] + "@" + suggestions[0]
                self.cursor_position = len(self.value)

    async def _show_command_suggestions(self) -> None:
        """Show command suggestions overlay."""
        if self.value.startswith("/"):
            completions = self.command_processor.get_completions(self.value)
            if completions:
                # Post message to parent to show suggestions overlay
                self.post_message(ShowSuggestions(completions, "commands"))

    async def _show_file_suggestions(self) -> None:
        """Show file suggestions overlay."""
        if "@" in self.value:
            prefix = self.value.split("@")[-1]
            suggestions = get_file_suggestions(prefix, limit=20)
            if suggestions:
                # Post message to parent to show suggestions overlay
                self.post_message(ShowSuggestions(suggestions, "files"))


class ShowSuggestions(Message):
    """Message to show suggestions overlay."""

    def __init__(self, suggestions: List[str], suggestion_type: str):
        super().__init__()
        self.suggestions = suggestions
        self.suggestion_type = suggestion_type


class ModelSelectionScreen(ModalScreen[str]):
    """Enhanced modal screen for model and provider selection using new widgets."""

    def __init__(self, config: AppConfig, model_manager: ModelManager):
        super().__init__()
        self.config = config
        self.model_manager = model_manager
        self.selected_provider = config.provider
        self.selected_model = config.model

        # Prepare model and provider data
        self.models_data = []
        self.providers_data = []

    def compose(self) -> ComposeResult:
        """Compose the enhanced model selection interface."""
        with Container(id="model_selection_container", classes="modal_container"):
            yield Header()

            with TabbedContent("Providers", "Models", "Settings"):
                with TabPane("Providers", id="providers_tab"):
                    # Use new ProviderSelector widget
                    yield ProviderSelector(
                        providers=self.providers_data, id="provider_selector"
                    )

                with TabPane("Models", id="models_tab"):
                    # Use new ModelSelector widget
                    yield ModelSelector(models=self.models_data, id="model_selector")

                with TabPane("Settings", id="settings_tab"):
                    yield Label("Model Settings")
                    yield Checkbox("Stream responses", value=True, id="stream_checkbox")
                    yield Checkbox(
                        "Enable function calling",
                        value=True,
                        id="function_calling_checkbox",
                    )
                    yield Checkbox(
                        "Show thinking process", value=False, id="thinking_checkbox"
                    )

                    # Performance indicator
                    yield PerformanceIndicator(id="performance_indicator")

            with Horizontal(id="model_buttons"):
                yield Button("Apply", variant="primary", id="apply_model")
                yield Button("Test Connection", variant="outline", id="test_model")
                yield Button("Cancel", variant="default", id="cancel_model")

    async def on_mount(self) -> None:
        """Initialize the model selection screen with data."""
        await self._load_providers_and_models()

    async def _load_providers_and_models(self) -> None:
        """Load providers and models data for the selectors."""
        try:
            # Load providers
            available_providers = self.model_manager.get_available_providers()
            self.providers_data = []

            for provider_name in available_providers:
                provider_info = ProviderInfo(
                    name=provider_name,
                    display_name=provider_name.title(),
                    description=f"{provider_name.title()} AI provider",
                    is_configured=await self._check_provider_configured(provider_name),
                    is_connected=await self._check_provider_connected(provider_name),
                    api_key_set=self._check_api_key_set(provider_name),
                )

                # Get models for this provider
                try:
                    models = await self.model_manager.get_models_for_provider(
                        provider_name
                    )
                    provider_info.models = models
                except Exception as e:
                    logger.warning(f"Could not load models for {provider_name}: {e}")
                    provider_info.last_error = str(e)

                self.providers_data.append(provider_info)

            # Load models for current provider
            await self._load_models_for_current_provider()

            # Update the selector widgets
            provider_selector = self.query_one("#provider_selector", ProviderSelector)
            provider_selector.providers = self.providers_data
            provider_selector.update_provider_list()

            model_selector = self.query_one("#model_selector", ModelSelector)
            model_selector.models = self.models_data
            model_selector.update_model_list()

        except Exception as e:
            logger.error(f"Error loading providers and models: {e}")

    async def _load_models_for_current_provider(self) -> None:
        """Load models data for the current provider."""
        try:
            models = await self.model_manager.get_models_for_provider(
                self.selected_provider
            )
            self.models_data = []

            for model_name in models:
                model_info = ModelInfo(
                    name=model_name,
                    provider=self.selected_provider,
                    description=f"{model_name} model from {self.selected_provider}",
                    is_available=True,
                    last_used=(
                        datetime.now() if model_name == self.selected_model else None
                    ),
                )

                # Add model capabilities and cost info if available
                model_details = await self._get_model_details(
                    model_name, self.selected_provider
                )
                if model_details:
                    model_info.context_length = model_details.get("context_length", 0)
                    model_info.input_cost = model_details.get("input_cost", 0.0)
                    model_info.output_cost = model_details.get("output_cost", 0.0)
                    model_info.capabilities = model_details.get("capabilities", [])

                self.models_data.append(model_info)

        except Exception as e:
            logger.error(f"Error loading models for {self.selected_provider}: {e}")

    async def _check_provider_configured(self, provider: str) -> bool:
        """Check if provider is properly configured."""
        try:
            return self.model_manager.is_provider_configured(provider)
        except Exception:
            return False

    async def _check_provider_connected(self, provider: str) -> bool:
        """Check if provider is currently connected."""
        try:
            return await self.model_manager.test_provider_connection(provider)
        except Exception:
            return False

    def _check_api_key_set(self, provider: str) -> bool:
        """Check if API key is set for provider."""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_AI_KEY",
            "mistral": "MISTRAL_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "xai": "XAI_API_KEY",
            "groq": "GROQ_API_KEY",
        }

        env_var = key_map.get(provider.lower())
        if env_var:
            return bool(os.environ.get(env_var))
        return False

    async def _get_model_details(
        self, model: str, provider: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model."""
        try:
            return await self.model_manager.get_model_info(model, provider)
        except Exception:
            return None

    async def on_message(self, message: Message) -> None:
        """Handle messages from child widgets."""
        from kritrima_ai.ui.widgets.selection_components import (
            ConfigureProvider,
            ModelSelected,
            ProviderSelected,
            TestProvider,
        )

        if isinstance(message, ProviderSelected):
            self.selected_provider = message.provider.name
            await self._load_models_for_current_provider()

            # Update model selector
            model_selector = self.query_one("#model_selector", ModelSelector)
            model_selector.models = self.models_data
            model_selector.update_model_list()

        elif isinstance(message, ModelSelected):
            self.selected_model = message.model.name

        elif isinstance(message, ConfigureProvider):
            # Handle provider configuration
            await self._configure_provider(message.provider)

        elif isinstance(message, TestProvider):
            # Handle provider testing
            await self._test_provider(message.provider)

    async def _configure_provider(self, provider: ProviderInfo) -> None:
        """Configure a provider."""
        # This could open a configuration dialog or show instructions
        logger.info(f"Configure provider: {provider.name}")

    async def _test_provider(self, provider: ProviderInfo) -> None:
        """Test a provider connection."""
        try:
            success = await self.model_manager.test_provider_connection(provider.name)
            if success:
                self.notify(f"✅ {provider.display_name} connection successful")
            else:
                self.notify(f"❌ {provider.display_name} connection failed")
        except Exception as e:
            self.notify(f"❌ Error testing {provider.display_name}: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "apply_model":
            # Apply the selected model and provider
            result = f"{self.selected_provider}:{self.selected_model}"
            self.dismiss(result)
        elif event.button.id == "test_model":
            await self._test_current_selection()
        elif event.button.id == "cancel_model":
            self.dismiss(None)

    async def _test_current_selection(self) -> None:
        """Test the currently selected model and provider."""
        try:
            success = await self.model_manager.test_model(
                self.selected_model, self.selected_provider
            )
            if success:
                self.notify(f"✅ {self.selected_model} test successful")
            else:
                self.notify(f"❌ {self.selected_model} test failed")
        except Exception as e:
            self.notify(f"❌ Error testing model: {e}")

    async def _refresh_providers(self) -> None:
        """Refresh provider information."""
        await self._load_providers_and_models()


class SessionHistoryScreen(ModalScreen[str]):
    """Enhanced modal screen for session and history browsing using new widgets."""

    def __init__(
        self, session_manager: SessionManager, command_history: CommandHistory
    ):
        super().__init__()
        self.session_manager = session_manager
        self.command_history = command_history
        self.sessions_data = []
        self.history_data = []

    def compose(self) -> ComposeResult:
        """Compose the enhanced session history interface."""
        with Container(id="session_history_container", classes="modal_container"):
            yield Header()

            with TabbedContent("Sessions", "History", "Statistics"):
                with TabPane("Sessions", id="sessions_tab"):
                    # Use new SessionBrowser widget
                    yield SessionBrowser(
                        sessions=self.sessions_data, id="session_browser"
                    )

                with TabPane("History", id="history_tab"):
                    # Use new HistoryBrowser widget
                    yield HistoryBrowser(
                        history=self.history_data, id="history_browser"
                    )

                with TabPane("Statistics", id="stats_tab"):
                    yield Label("Session Statistics")
                    yield Static("", id="session_stats")

                    # Performance metrics
                    yield PerformanceIndicator(
                        update_interval=5.0, id="session_performance"
                    )

            with Horizontal(id="session_buttons"):
                yield Button("Load Session", variant="primary", id="load_session")
                yield Button("Export", variant="outline", id="export_session")
                yield Button("Close", variant="default", id="close_session")

    async def on_mount(self) -> None:
        """Initialize the session history screen with data."""
        await self._load_sessions_and_history()

    async def _load_sessions_and_history(self) -> None:
        """Load sessions and history data for the browsers."""
        try:
            # Load sessions
            sessions = await self.session_manager.get_all_sessions()
            self.sessions_data = []

            for session_data in sessions:
                session_info = SessionInfo(
                    id=session_data.get("id", ""),
                    name=session_data.get("name", "Unnamed Session"),
                    created_at=datetime.fromisoformat(
                        session_data.get("created_at", datetime.now().isoformat())
                    ),
                    last_used=datetime.fromisoformat(
                        session_data.get("last_used", datetime.now().isoformat())
                    ),
                    message_count=session_data.get("message_count", 0),
                    token_count=session_data.get("token_count", 0),
                    model_used=session_data.get("model_used", ""),
                    provider_used=session_data.get("provider_used", ""),
                    workspace_path=session_data.get("workspace_path", ""),
                    tags=session_data.get("tags", []),
                )
                self.sessions_data.append(session_info)

            # Load command history
            history_entries = await self.command_history.get_recent_commands(limit=100)
            self.history_data = []

            for entry in history_entries:
                history_entry = HistoryEntry(
                    id=entry.get("id", ""),
                    timestamp=datetime.fromisoformat(
                        entry.get("timestamp", datetime.now().isoformat())
                    ),
                    command=entry.get("command", ""),
                    result=entry.get("result", ""),
                    success=entry.get("success", True),
                    duration=entry.get("duration", 0.0),
                    session_id=entry.get("session_id", ""),
                    model_used=entry.get("model_used", ""),
                )
                self.history_data.append(history_entry)

            # Update browser widgets
            session_browser = self.query_one("#session_browser", SessionBrowser)
            session_browser.sessions = self.sessions_data
            session_browser.update_session_list()

            history_browser = self.query_one("#history_browser", HistoryBrowser)
            history_browser.history = self.history_data
            history_browser.update_history_list()

            # Update statistics
            await self._update_statistics()

        except Exception as e:
            logger.error(f"Error loading sessions and history: {e}")

    async def _update_statistics(self) -> None:
        """Update session statistics display."""
        try:
            stats_widget = self.query_one("#session_stats", Static)

            # Calculate statistics
            total_sessions = len(self.sessions_data)
            total_commands = len(self.history_data)
            total_messages = sum(s.message_count for s in self.sessions_data)
            total_tokens = sum(s.token_count for s in self.sessions_data)

            successful_commands = sum(1 for h in self.history_data if h.success)
            success_rate = (
                (successful_commands / total_commands * 100)
                if total_commands > 0
                else 0
            )

            avg_session_duration = (
                sum(
                    (s.last_used - s.created_at).total_seconds()
                    for s in self.sessions_data
                )
                / len(self.sessions_data)
                if self.sessions_data
                else 0
            )

            # Format statistics
            stats_text = [
                f"Total Sessions: {total_sessions}",
                f"Total Commands: {total_commands}",
                f"Total Messages: {total_messages:,}",
                f"Total Tokens: {total_tokens:,}",
                f"Command Success Rate: {success_rate:.1f}%",
                f"Average Session Duration: {timedelta(seconds=int(avg_session_duration))}",
            ]

            # Most used models
            model_usage = {}
            for session in self.sessions_data:
                if session.model_used:
                    model_usage[session.model_used] = (
                        model_usage.get(session.model_used, 0) + 1
                    )

            if model_usage:
                most_used_model = max(model_usage.items(), key=lambda x: x[1])
                stats_text.append(
                    f"Most Used Model: {most_used_model[0]} ({most_used_model[1]} sessions)"
                )

            stats_widget.update("\n".join(stats_text))

        except Exception as e:
            logger.error(f"Error updating statistics: {e}")

    async def on_message(self, message: Message) -> None:
        """Handle messages from child widgets."""
        from kritrima_ai.ui.widgets.selection_components import (
            ClearHistory,
            CopyCommand,
            DeleteSession,
            ExportHistory,
            LoadSession,
            NewSession,
            RenameSession,
            RerunCommand,
        )

        if isinstance(message, LoadSession):
            self.dismiss(f"load:{message.session.id}")

        elif isinstance(message, NewSession):
            self.dismiss("new_session")

        elif isinstance(message, RenameSession):
            await self._rename_session(message.session)

        elif isinstance(message, DeleteSession):
            await self._delete_session(message.session)

        elif isinstance(message, RerunCommand):
            self.dismiss(f"rerun:{message.entry.command}")

        elif isinstance(message, CopyCommand):
            await self._copy_command(message.entry)

        elif isinstance(message, ExportHistory):
            await self._export_history(message.history)

        elif isinstance(message, ClearHistory):
            await self._clear_history()

    async def _rename_session(self, session: SessionInfo) -> None:
        """Rename a session."""
        try:
            # This would typically open a text input dialog
            # For now, just log the action
            logger.info(f"Rename session: {session.name}")
            self.notify(f"Rename session feature coming soon")
        except Exception as e:
            logger.error(f"Error renaming session: {e}")

    async def _delete_session(self, session: SessionInfo) -> None:
        """Delete a session."""
        try:
            await self.session_manager.delete_session(session.id)
            await self._load_sessions_and_history()  # Refresh
            self.notify(f"Session '{session.name}' deleted")
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            self.notify(f"Error deleting session: {e}")

    async def _copy_command(self, entry: HistoryEntry) -> None:
        """Copy command to clipboard."""
        try:
            # Copy to system clipboard if available
            import pyperclip

            pyperclip.copy(entry.command)
            self.notify("Command copied to clipboard")
        except ImportError:
            # Fallback - just show the command
            self.notify(f"Command: {entry.command}")
        except Exception as e:
            logger.error(f"Error copying command: {e}")

    async def _export_history(self, history: List[HistoryEntry]) -> None:
        """Export history to file."""
        try:
            # This would typically open a file save dialog
            logger.info(f"Export {len(history)} history entries")
            self.notify(f"Export history feature coming soon")
        except Exception as e:
            logger.error(f"Error exporting history: {e}")

    async def _clear_history(self) -> None:
        """Clear command history."""
        try:
            await self.command_history.clear_history()
            await self._load_sessions_and_history()  # Refresh
            self.notify("Command history cleared")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            self.notify(f"Error clearing history: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "load_session":
            # Get selected session from browser
            session_browser = self.query_one("#session_browser", SessionBrowser)
            if session_browser.selected_session:
                self.dismiss(f"load:{session_browser.selected_session.id}")
            else:
                self.notify("No session selected")
        elif event.button.id == "export_session":
            # Export selected session
            session_browser = self.query_one("#session_browser", SessionBrowser)
            if session_browser.selected_session:
                await self._export_selected_session(session_browser.selected_session)
            else:
                self.notify("No session selected")
        elif event.button.id == "close_session":
            self.dismiss(None)

    async def _export_selected_session(self, session: SessionInfo) -> None:
        """Export the selected session."""
        try:
            # This would typically open a file save dialog
            logger.info(f"Export session: {session.name}")
            self.notify(f"Export session feature coming soon")
        except Exception as e:
            logger.error(f"Error exporting session: {e}")
            self.notify(f"Error exporting session: {e}")


class ApprovalScreen(ModalScreen[str]):
    """Enhanced approval screen with detailed command information and approval mode settings."""

    def __init__(
        self,
        command: str,
        explanation: str = "",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.command = command
        self.explanation = explanation
        self.context = context or {}
        self.command_processor = get_command_processor()

    def compose(self) -> ComposeResult:
        """Compose the enhanced approval interface."""
        with Container(id="approval_container", classes="modal_container"):
            yield Header()

            with TabbedContent("Command", "Context", "Settings"):
                with TabPane("Command", id="command_tab"):
                    yield Label("Command Approval Required", classes="section_title")

                    # Command details
                    with Container(id="command_details"):
                        yield Static(f"Command: {self.command}", id="command_text")
                        if self.explanation:
                            yield Static(
                                f"Explanation: {self.explanation}",
                                id="explanation_text",
                            )

                        # Code highlighting for commands that look like code
                        if self._looks_like_code(self.command):
                            yield CodeBlockWidget(
                                code=self.command,
                                language=self._detect_language(self.command),
                                filename="command.sh",
                            )

                    # Risk assessment
                    yield Static("", id="risk_assessment")

                    # Approval options
                    yield RadioSet(
                        RadioButton("Approve this command", value=True, id="approve"),
                        RadioButton(
                            "Approve and remember for similar commands",
                            value=False,
                            id="approve_remember",
                        ),
                        RadioButton("Deny this command", value=False, id="deny"),
                        RadioButton(
                            "Modify command before execution", value=False, id="modify"
                        ),
                        id="approval_radio_set",
                    )

                with TabPane("Context", id="context_tab"):
                    yield Label("Execution Context", classes="section_title")
                    yield Static("", id="context_display")

                    # Show related files if any
                    if self.context.get("files"):
                        yield Label("Related Files:")
                        for file_path in self.context["files"]:
                            yield Static(f"📄 {file_path}")

                with TabPane("Settings", id="settings_tab"):
                    yield Label("Approval Settings", classes="section_title")
                    yield Checkbox(
                        "Auto-approve safe commands",
                        value=False,
                        id="auto_approve_safe",
                    )
                    yield Checkbox(
                        "Show detailed explanations", value=True, id="show_explanations"
                    )
                    yield Checkbox(
                        "Remember approval decisions",
                        value=True,
                        id="remember_decisions",
                    )

                    yield Button(
                        "Configure Approval Mode",
                        id="config_approval_mode",
                        variant="outline",
                    )

            with Horizontal(id="approval_buttons"):
                yield Button("Approve", variant="success", id="approve_command")
                yield Button("Deny", variant="error", id="deny_command")
                yield Button("Modify", variant="warning", id="modify_command")
                yield Button("Cancel", variant="default", id="cancel_approval")

    async def on_mount(self) -> None:
        """Initialize the approval screen."""
        await self._analyze_command()
        await self._update_context_display()

    async def _analyze_command(self) -> None:
        """Analyze the command for security risks."""
        risk_widget = self.query_one("#risk_assessment", Static)

        # Basic risk assessment
        risk_level = "LOW"
        risk_factors = []

        dangerous_patterns = [
            "rm -rf",
            "del /",
            "format",
            "sudo",
            "chmod 777",
            "wget http://",
            "curl http://",
            "bash <(",
            "eval",
            "exec",
            ">",
            ">>",
            "|",
            "&",
        ]

        for pattern in dangerous_patterns:
            if pattern in self.command.lower():
                risk_level = "HIGH"
                risk_factors.append(f"Contains dangerous pattern: {pattern}")

        # Check if it's a slash command
        if self.command.startswith("/"):
            if self.command_processor.is_command(self.command):
                risk_level = "LOW"
                risk_factors = ["Safe slash command"]
            else:
                risk_level = "MEDIUM"
                risk_factors.append("Unknown slash command")

        # Format risk assessment
        risk_color = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}.get(
            risk_level, "white"
        )

        risk_text = f"Risk Level: [{risk_color}]{risk_level}[/{risk_color}]"
        if risk_factors:
            risk_text += "\n" + "\n".join(f"• {factor}" for factor in risk_factors)

        risk_widget.update(risk_text)

    async def _update_context_display(self) -> None:
        """Update the context display."""
        context_widget = self.query_one("#context_display", Static)

        context_lines = []
        context_lines.append(f"Working Directory: {os.getcwd()}")
        context_lines.append(f"User: {os.environ.get('USER', 'Unknown')}")

        if self.context.get("session_id"):
            context_lines.append(f"Session: {self.context['session_id']}")

        if self.context.get("model"):
            context_lines.append(f"AI Model: {self.context['model']}")

        if self.context.get("provider"):
            context_lines.append(f"Provider: {self.context['provider']}")

        # Environment variables that might be relevant
        env_vars = ["PATH", "HOME", "SHELL"]
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                # Truncate long paths
                display_value = value if len(value) < 50 else value[:47] + "..."
                context_lines.append(f"{var}: {display_value}")

        context_widget.update("\n".join(context_lines))

    def _looks_like_code(self, text: str) -> bool:
        """Check if text looks like code."""
        code_indicators = [
            "#!/",
            "python",
            "pip",
            "npm",
            "git",
            "docker",
            "mkdir",
            "cd",
            "ls",
            "cat",
            "echo",
            "export",
        ]
        return any(indicator in text.lower() for indicator in code_indicators)

    def _detect_language(self, text: str) -> str:
        """Detect the language of the command."""
        if text.startswith("#!/usr/bin/env python") or "python" in text.lower():
            return "python"
        elif text.startswith("#!/bin/bash") or any(
            cmd in text for cmd in ["cd", "ls", "mkdir", "rm"]
        ):
            return "bash"
        elif "npm" in text or "node" in text:
            return "javascript"
        elif "docker" in text:
            return "dockerfile"
        else:
            return "bash"  # Default

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "approve_command":
            self.dismiss("approve")
        elif event.button.id == "deny_command":
            self.dismiss("deny")
        elif event.button.id == "modify_command":
            self.dismiss("modify")
        elif event.button.id == "cancel_approval":
            self.dismiss("cancel")
        elif event.button.id == "config_approval_mode":
            await self._show_approval_mode_config()

    async def _show_approval_mode_config(self) -> None:
        """Show approval mode configuration overlay."""

        # Get current approval mode from context or default
        current_mode = self.context.get("approval_mode", "suggest")

        approval_overlay = ApprovalModeOverlay(current_mode)
        result = await self.push_screen(approval_overlay)

        if result:
            # Update the approval mode in context
            self.context["approval_mode"] = result
            self.notify(f"Approval mode set to: {result}")

    async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle approval option selection."""
        if event.pressed.id == "approve":
            # Auto-approve
            pass
        elif event.pressed.id == "approve_remember":
            # Approve and remember
            pass
        elif event.pressed.id == "deny":
            # Deny
            pass
        elif event.pressed.id == "modify":
            # Modify command
            pass


class MainChatInterface(Container):
    """Enhanced main chat interface using new chat components."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_container = None
        self.streaming_widget = None
        self.current_thinking_spinner = None

    def compose(self) -> ComposeResult:
        """Compose the enhanced chat interface."""
        # Use new ChatContainer for message display
        self.chat_container = ChatContainer(id="chat_log")
        yield self.chat_container

        # Streaming response widget for AI responses
        self.streaming_widget = StreamingResponseWidget(id="streaming_response")
        yield self.streaming_widget

        # Enhanced input with file tag and command support
        yield EnhancedFileTagInput(
            placeholder="Type your message, @file to include files, /command for slash commands...",
            id="chat_input",
        )

    async def add_message(self, message: ChatMessage) -> None:
        """Add a message to the chat using new chat components."""
        # Convert old ChatMessage to new format
        new_message = NewChatMessage(
            role=message.role,
            content=message.content,
            timestamp=message.timestamp,
            metadata=message.metadata,
        )

        # Add to chat container
        self.chat_container.add_message(new_message)

    async def _render_message(self, message: ChatMessage) -> None:
        """Render a message with appropriate formatting."""
        # This is now handled by ChatContainer and ChatMessageRenderer

    async def start_streaming_response(self) -> None:
        """Start streaming response mode with thinking spinner."""
        # Show thinking spinner
        self.current_thinking_spinner = ThinkingSpinner(
            message="AI is thinking...", show_elapsed=True, show_interrupt=True
        )

        # Start the spinner
        self.current_thinking_spinner.start()

        # Mount the spinner temporarily
        await self.mount(self.current_thinking_spinner)

        # Clear and prepare streaming widget
        self.streaming_widget.clear_content()
        self.streaming_widget.start_streaming()

    async def update_streaming_response(self, delta: str) -> None:
        """Update streaming response with new content."""
        if self.streaming_widget and self.streaming_widget.is_streaming:
            self.streaming_widget.append_content(delta)

    async def finish_streaming_response(self) -> None:
        """Finish streaming response and add to chat history."""
        # Stop thinking spinner
        if self.current_thinking_spinner:
            self.current_thinking_spinner.stop()
            self.current_thinking_spinner.remove()
            self.current_thinking_spinner = None

        # Finish streaming
        if self.streaming_widget:
            self.streaming_widget.finish_streaming()

            # Get the complete response content
            complete_response = self.streaming_widget.current_content

            # Create assistant message and add to chat
            if complete_response.strip():
                assistant_message = NewChatMessage(
                    role="assistant",
                    content=complete_response,
                    timestamp=datetime.now(),
                )
                self.chat_container.add_message(assistant_message)

            # Clear streaming widget for next response
            self.streaming_widget.clear_content()

    async def show_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Show a tool call with results using ToolCallWidget."""
        tool_widget = ToolCallWidget(
            tool_name=tool_name, parameters=parameters, result=result, error=error
        )

        # Mount the tool widget temporarily or add to chat
        await self.mount(tool_widget)

    async def show_code_block(
        self, code: str, language: str = "text", filename: Optional[str] = None
    ) -> None:
        """Show a code block using CodeBlockWidget."""
        code_widget = CodeBlockWidget(code=code, language=language, filename=filename)

        await self.mount(code_widget)

    async def show_diff(
        self, old_content: str, new_content: str, filename: Optional[str] = None
    ) -> None:
        """Show a diff using DiffWidget."""
        diff_widget = DiffWidget(
            old_content=old_content, new_content=new_content, filename=filename
        )

        await self.mount(diff_widget)

    async def show_thinking_process(self, message: str = "Processing...") -> None:
        """Show thinking process with spinner."""
        if not self.current_thinking_spinner:
            self.current_thinking_spinner = ThinkingSpinner(
                message=message, show_elapsed=True, show_interrupt=True
            )
            self.current_thinking_spinner.start()
            await self.mount(self.current_thinking_spinner)

    async def hide_thinking_process(self) -> None:
        """Hide thinking process spinner."""
        if self.current_thinking_spinner:
            self.current_thinking_spinner.stop()
            self.current_thinking_spinner.remove()
            self.current_thinking_spinner = None

    def clear_messages(self) -> None:
        """Clear all messages from chat."""
        if self.chat_container:
            self.chat_container.clear_messages()

        if self.streaming_widget:
            self.streaming_widget.clear_content()

        if self.current_thinking_spinner:
            self.current_thinking_spinner.stop()
            self.current_thinking_spinner.remove()
            self.current_thinking_spinner = None


class TerminalInterface(App):
    """
    Enhanced terminal interface for Kritrima AI CLI.

    Provides a comprehensive, interactive terminal-based user interface with:
    - Real-time chat with AI streaming responses and thinking indicators
    - Advanced UI widgets (spinners, overlays, status components)
    - Enhanced file tag expansion and auto-completion
    - Comprehensive slash command support with validation
    - Modal overlays for configuration and management
    - Session management and command history with advanced browsing
    - Command approval workflow with risk assessment
    - Performance monitoring and context tracking
    """

    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 4;
        grid-rows: auto 1fr auto auto;
    }
    
    #header_container {
        height: 3;
        background: $primary;
        color: $primary-background;
    }
    
    #main_container {
        row-span: 1;
        layout: horizontal;
    }
    
    #chat_container {
        width: 3fr;
        border: solid $primary;
    }
    
    #side_panel {
        width: 1fr;
        border: solid $accent;
        background: $surface;
    }
    
    #status_container {
        height: auto;
        background: $surface;
        border-top: solid $border;
    }
    
    #footer_container {
        height: 1;
        background: $primary;
        color: $primary-background;
    }
    
    #chat_log {
        height: 1fr;
        scrollbar-gutter: stable;
    }
    
    #chat_input {
        height: 3;
        border: solid $accent;
    }
    
    .modal_container {
        align: center middle;
        width: 80%;
        height: 80%;
        background: $background;
        border: solid $primary;
        border-radius: 4;
    }
    
    .section_title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+m", "toggle_model", "Model Selection"),
        Binding("ctrl+h", "toggle_history", "History"),
        Binding("ctrl+s", "toggle_sessions", "Sessions"),
        Binding("ctrl+l", "clear_chat", "Clear Chat"),
        Binding("ctrl+d", "toggle_diff", "Git Diff"),
        Binding("ctrl+g", "toggle_debug", "Debug Info"),
        Binding("ctrl+p", "toggle_performance", "Performance"),
        Binding("ctrl+r", "refresh_status", "Refresh"),
        Binding("f1", "show_help", "Help"),
        Binding("f2", "config_overlay", "Configuration"),
        Binding("f3", "approval_settings", "Approval Mode"),
    ]

    def __init__(
        self,
        config: AppConfig,
        agent_loop: AgentLoop,
        session_manager: SessionManager,
        command_history: CommandHistory,
    ):
        super().__init__()
        self.config = config
        self.agent_loop = agent_loop
        self.session_manager = session_manager
        self.command_history = command_history
        self.model_manager = ModelManager(config)
        self.command_processor = get_command_processor()

        # UI State
        self.current_session_id: Optional[str] = None
        self.approval_callback: Optional[Callable] = None
        self.show_side_panel = False

        # Context tracking
        self.context_info = ContextInfo(
            current_model=config.model,
            provider=config.provider,
            workspace_path=str(Path.cwd()),
            session_duration=timedelta(),
        )

        # Performance tracking
        self._message_count = 0
        self._session_start_time = time.time()
        self._total_tokens = 0

        # Connection status
        self.connection_status = ConnectionStatus.DISCONNECTED

        logger.info("Enhanced terminal interface initialized")

    def compose(self) -> ComposeResult:
        """Compose the enhanced application layout."""
        # Header with title and quick info
        with Container(id="header_container"):
            yield Label(
                f"🤖 Kritrima AI CLI - {self.config.model} ({self.config.provider})",
                id="header_label",
            )

        # Main content area
        with Container(id="main_container"):
            # Chat area
            with Container(id="chat_container"):
                yield MainChatInterface(id="main_chat")

            # Side panel for status and tools (initially hidden)
            with Container(
                id="side_panel", classes="hidden" if not self.show_side_panel else ""
            ):
                # Context indicator
                yield ContextIndicator(id="context_indicator")

                # Performance indicator
                yield PerformanceIndicator(id="performance_indicator")

                # Connection indicator
                yield ConnectionIndicator(id="connection_indicator")

        # Status bar with enhanced information
        with Container(id="status_container"):
            yield StatusBar(id="status_bar")

        # Footer with key bindings
        with Container(id="footer_container"):
            yield Label(
                "F1:Help F2:Config F3:Approval | Ctrl+M:Model Ctrl+H:History Ctrl+S:Sessions Ctrl+L:Clear | Ctrl+C:Quit",
                id="footer_label",
            )

    async def on_mount(self) -> None:
        """Initialize the enhanced interface when mounted."""
        # Create new session
        self.current_session_id = await self.session_manager.create_session()

        # Update context info
        self.context_info.session_id = self.current_session_id
        self.context_info.workspace_path = str(Path.cwd())

        # Update status components
        await self._update_all_status()

        # Set up agent loop approval callback
        self.agent_loop.approval_callback = self._handle_approval_request

        # Focus input
        chat_input = self.query_one("#chat_input")
        chat_input.focus()

        # Test initial connection
        await self._test_connection()

        logger.info(
            f"Enhanced interface mounted with session: {self.current_session_id}"
        )

    async def on_message(self, message: Message) -> None:
        """Handle messages from child widgets."""
        if isinstance(message, ShowSuggestions):
            await self._show_suggestions_overlay(
                message.suggestions, message.suggestion_type
            )
        else:
            await super().on_message(message)

    async def _show_suggestions_overlay(
        self, suggestions: List[str], suggestion_type: str
    ) -> None:
        """Show suggestions overlay for file or command completion."""
        if suggestion_type == "files":
            overlay = FileSuggestionsOverlay(suggestions, "@")
        else:  # commands
            overlay = FileSuggestionsOverlay(suggestions, "/")

        result = await self.push_screen(overlay)
        if result:
            # Replace current input with selected suggestion
            chat_input = self.query_one("#chat_input")
            if suggestion_type == "files":
                parts = chat_input.value.rsplit("@", 1)
                chat_input.value = parts[0] + "@" + result
            else:  # commands
                chat_input.value = result
            chat_input.cursor_position = len(chat_input.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission with enhanced processing."""
        if event.input.id == "chat_input":
            message = event.value.strip()
            if message:
                await self._process_user_input(message)
                event.input.value = ""

    async def _process_user_input(self, message: str) -> None:
        """Enhanced user input processing with better error handling and features."""
        try:
            # Update context
            self._message_count += 1

            # Expand file tags
            expanded_message = await expand_file_tags(message)

            # Check for slash commands
            if message.startswith("/"):
                await self._handle_slash_command(message)
                return

            # Add user message to chat
            chat_interface = self.query_one("#main_chat", MainChatInterface)
            user_message = ChatMessage(content=message, role="user")
            await chat_interface.add_message(user_message)

            # Add to command history
            await self.command_history.add_command(message)

            # Start streaming response with thinking indicator
            await chat_interface.start_streaming_response()

            # Send to agent loop and stream response
            response_complete = False
            try:
                async for response in self.agent_loop.send_message_stream(
                    expanded_message
                ):
                    await self._handle_agent_response(response)

                response_complete = True

            except Exception as e:
                logger.error(f"Error during agent response: {e}")
                await chat_interface.finish_streaming_response()
                await self._show_error(f"Error: {str(e)}")
                return

            # Finish streaming if not already finished
            if response_complete:
                await chat_interface.finish_streaming_response()

            # Update context and performance stats
            await self._update_context_after_message()
            await self._update_performance_stats()

        except Exception as e:
            logger.error(f"Error processing user input: {e}", exc_info=True)
            await self._show_error(f"Error: {str(e)}")

    async def _handle_agent_response(self, response: AgentResponse) -> None:
        """Enhanced agent response handling with tool call visualization."""
        chat_interface = self.query_one("#main_chat", MainChatInterface)

        if response.type == ResponseType.TEXT:
            await chat_interface.update_streaming_response(response.content)

        elif response.type == ResponseType.TOOL_CALL:
            # Show tool call with enhanced visualization
            await chat_interface.show_tool_call(
                tool_name=response.tool_name,
                parameters=response.tool_args or {},
                result=getattr(response, "tool_result", None),
                error=getattr(response, "tool_error", None),
            )

        elif response.type == ResponseType.CODE:
            # Show code block with syntax highlighting
            await chat_interface.show_code_block(
                code=response.content,
                language=getattr(response, "language", "text"),
                filename=getattr(response, "filename", None),
            )

        elif response.type == ResponseType.DIFF:
            # Show diff with proper formatting
            await chat_interface.show_diff(
                old_content=getattr(response, "old_content", ""),
                new_content=response.content,
                filename=getattr(response, "filename", None),
            )

        elif response.type == ResponseType.ERROR:
            await self._show_error(response.content)

        elif response.type == ResponseType.THINKING:
            # Update thinking spinner message
            await chat_interface.show_thinking_process(response.content)

        elif response.type == ResponseType.APPROVAL_REQUIRED:
            # This is handled by the approval callback
            pass

    async def _handle_slash_command(self, command: str) -> None:
        """Enhanced slash command handling using the command processor."""
        try:
            # Parse and execute command using the processor
            context = {
                "session_id": self.current_session_id,
                "model": self.config.model,
                "provider": self.config.provider,
                "workspace": str(Path.cwd()),
                "interface": self,  # Pass interface reference for UI operations
            }

            result = await self.command_processor.execute_command(command, context)

            if result:
                # Show command result
                chat_interface = self.query_one("#main_chat", MainChatInterface)
                result_message = ChatMessage(
                    content=str(result),
                    role="system",
                    metadata={"type": "command_result"},
                )
                await chat_interface.add_message(result_message)

        except Exception as e:
            logger.error(f"Error executing slash command '{command}': {e}")
            await self._show_error(f"Command error: {e}")

    async def _show_help(self) -> None:
        """Show enhanced help overlay."""
        help_overlay = HelpOverlay()
        await self.push_screen(help_overlay)

    async def _clear_chat(self) -> None:
        """Clear chat with confirmation."""
        if self._message_count > 0:
            # Could add a confirmation dialog here
            pass

        chat_interface = self.query_one("#main_chat", MainChatInterface)
        chat_interface.clear_messages()
        self._message_count = 0

        # Reset context
        await self._update_context_after_message()

    async def _show_git_diff(self) -> None:
        """Show enhanced git diff overlay."""
        diff_overlay = DiffOverlay()
        await self.push_screen(diff_overlay)

    async def _compact_conversation(self) -> None:
        """Compact conversation context to save tokens."""
        try:
            await self.agent_loop.compact_context()
            self.notify("Conversation context compacted")
        except Exception as e:
            logger.error(f"Error compacting conversation: {e}")
            await self._show_error(f"Error compacting context: {e}")

    async def _export_session(self, filename: Optional[str] = None) -> None:
        """Export current session to file."""
        try:
            if not filename:
                # Generate default filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"session_{timestamp}.json"

            export_path = Path(filename)
            await self.session_manager.export_session(
                self.current_session_id, export_path
            )
            self.notify(f"Session exported to {export_path}")

        except Exception as e:
            logger.error(f"Error exporting session: {e}")
            await self._show_error(f"Export error: {e}")

    async def _import_session(self, filename: Optional[str] = None) -> None:
        """Import session from file."""
        try:
            if not filename:
                # Could open file dialog here
                self.notify("Import session feature: specify filename")
                return

            import_path = Path(filename)
            session_id = await self.session_manager.import_session(import_path)

            if session_id:
                await self._load_session(session_id)
                self.notify(f"Session imported from {import_path}")
            else:
                await self._show_error("Failed to import session")

        except Exception as e:
            logger.error(f"Error importing session: {e}")
            await self._show_error(f"Import error: {e}")

    async def _show_error(self, error_message: str) -> None:
        """Show error message with enhanced formatting."""
        chat_interface = self.query_one("#main_chat", MainChatInterface)
        error_msg = ChatMessage(
            content=f"❌ {error_message}", role="system", metadata={"type": "error"}
        )
        await chat_interface.add_message(error_msg)

    async def _handle_approval_request(
        self, command: str, explanation: str = ""
    ) -> ApprovalDecision:
        """Enhanced approval request handling with context."""
        context = {
            "session_id": self.current_session_id,
            "model": self.config.model,
            "provider": self.config.provider,
            "approval_mode": self.config.approval_mode,
            "workspace": str(Path.cwd()),
        }

        approval_screen = ApprovalScreen(command, explanation, context)
        result = await self.push_screen(approval_screen)

        if result == "approve":
            return ApprovalDecision.APPROVED
        elif result == "approve_remember":
            return ApprovalDecision.ALWAYS_ALLOW
        elif result == "deny":
            return ApprovalDecision.DENIED
        elif result == "modify":
            # Return PENDING to indicate modification needed
            return ApprovalDecision.PENDING
        else:
            return ApprovalDecision.DENIED

    async def _test_connection(self) -> None:
        """Test AI provider connection and update status."""
        try:
            success = await self.model_manager.test_provider_connection(
                self.config.provider
            )
            if success:
                self.connection_status = ConnectionStatus.CONNECTED
            else:
                self.connection_status = ConnectionStatus.DISCONNECTED
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self.connection_status = ConnectionStatus.ERROR

        await self._update_connection_status()

    async def _update_all_status(self) -> None:
        """Update all status components."""
        # Update status bar
        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.update_context(self.context_info)
        status_bar.update_connection(self.connection_status)

        # Update context indicator if visible
        if self.show_side_panel:
            context_indicator = self.query_one("#context_indicator", ContextIndicator)
            context_indicator.update_context(self.context_info)

            # Update connection indicator
            connection_indicator = self.query_one(
                "#connection_indicator", ConnectionIndicator
            )
            connection_indicator.update_connection(
                self.config.provider,
                self.connection_status,
                {"model": self.config.model},
            )

    async def _update_context_after_message(self) -> None:
        """Update context information after a message."""
        self.context_info.message_count = self._message_count
        self.context_info.session_duration = timedelta(
            seconds=time.time() - self._session_start_time
        )

        await self._update_all_status()

    async def _update_connection_status(self) -> None:
        """Update connection status across UI."""
        await self._update_all_status()

    async def _update_performance_stats(self) -> None:
        """Update performance statistics."""
        if self.show_side_panel:
            perf_indicator = self.query_one(
                "#performance_indicator", PerformanceIndicator
            )
            # Performance indicator updates automatically

    # Enhanced action methods
    async def action_toggle_model(self) -> None:
        """Enhanced model selection with new widget."""
        model_screen = ModelSelectionScreen(self.config, self.model_manager)
        result = await self.push_screen(model_screen)

        if result:
            # Parse provider:model format
            if ":" in result:
                provider, model = result.split(":", 1)
                self.config.provider = provider
                self.config.model = model

                # Update context
                self.context_info.provider = provider
                self.context_info.current_model = model

                # Test new connection
                await self._test_connection()

                # Update status
                await self._update_all_status()

                self.notify(f"Switched to {model} ({provider})")

    async def action_toggle_history(self) -> None:
        """Enhanced history browser."""
        history_screen = SessionHistoryScreen(
            self.session_manager, self.command_history
        )
        result = await self.push_screen(history_screen)

        if result:
            if result.startswith("load:"):
                session_id = result[5:]
                await self._load_session(session_id)
            elif result.startswith("rerun:"):
                command = result[6:]
                await self._process_user_input(command)
            elif result == "new_session":
                await self._create_new_session()

    async def action_toggle_sessions(self) -> None:
        """Open enhanced session browser."""
        await self.action_toggle_history()  # Same enhanced interface

    async def _load_session(self, session_id: str) -> None:
        """Load a session with enhanced feedback."""
        try:
            session_data = await self.session_manager.load_session(session_id)
            if session_data:
                self.current_session_id = session_id
                self.context_info.session_id = session_id

                # Clear current chat and load session messages
                chat_interface = self.query_one("#main_chat", MainChatInterface)
                chat_interface.clear_messages()

                # Load messages if available
                messages = session_data.get("messages", [])
                for msg_data in messages:
                    message = ChatMessage(
                        content=msg_data.get("content", ""),
                        role=msg_data.get("role", "user"),
                        timestamp=datetime.fromisoformat(
                            msg_data.get("timestamp", datetime.now().isoformat())
                        ),
                    )
                    await chat_interface.add_message(message)

                await self._update_all_status()
                self.notify(f"Loaded session: {session_id[:8]}...")

        except Exception as e:
            logger.error(f"Error loading session: {e}")
            await self._show_error(f"Error loading session: {e}")

    async def _create_new_session(self) -> None:
        """Create a new session."""
        try:
            self.current_session_id = await self.session_manager.create_session()
            self.context_info.session_id = self.current_session_id

            # Clear chat
            chat_interface = self.query_one("#main_chat", MainChatInterface)
            chat_interface.clear_messages()

            self._message_count = 0
            self._session_start_time = time.time()

            await self._update_all_status()
            self.notify(f"New session created: {self.current_session_id[:8]}...")

        except Exception as e:
            logger.error(f"Error creating new session: {e}")
            await self._show_error(f"Error creating session: {e}")

    async def action_clear_chat(self) -> None:
        """Clear chat with confirmation."""
        await self._clear_chat()

    async def action_show_help(self) -> None:
        """Show comprehensive help."""
        await self._show_help()

    async def action_toggle_diff(self) -> None:
        """Show git diff overlay."""
        await self._show_git_diff()

    async def action_toggle_debug(self) -> None:
        """Show debug information overlay."""
        debug_info = {
            "session_id": self.current_session_id,
            "message_count": self._message_count,
            "total_tokens": self._total_tokens,
            "connection_status": self.connection_status.value,
            "performance": self.get_performance_stats(),
        }

        debug_overlay = DebugOverlay(debug_info)
        await self.push_screen(debug_overlay)

    async def action_toggle_performance(self) -> None:
        """Toggle side panel visibility."""
        self.show_side_panel = not self.show_side_panel
        side_panel = self.query_one("#side_panel")

        if self.show_side_panel:
            side_panel.remove_class("hidden")
            await self._update_all_status()
        else:
            side_panel.add_class("hidden")

    async def action_refresh_status(self) -> None:
        """Refresh all status information."""
        await self._test_connection()
        await self._update_all_status()
        self.notify("Status refreshed")

    async def action_config_overlay(self) -> None:
        """Show configuration overlay."""
        config_overlay = ConfigOverlay(self.config)
        await self.push_screen(config_overlay)

    async def action_approval_settings(self) -> None:
        """Show approval mode settings."""
        approval_overlay = ApprovalModeOverlay(self.config.approval_mode)
        result = await self.push_screen(approval_overlay)

        if result:
            self.config.approval_mode = result
            self.notify(f"Approval mode set to: {result}")

    async def action_quit(self) -> None:
        """Enhanced quit with cleanup."""
        try:
            # Save current session if needed
            if self.current_session_id and self._message_count > 0:
                await self.session_manager.save_session(self.current_session_id)

            logger.info("Terminal interface shutting down")
            self.exit()

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.exit()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get enhanced performance statistics."""
        session_duration = time.time() - self._session_start_time

        return {
            "session_duration": session_duration,
            "messages_sent": self._message_count,
            "total_tokens": self._total_tokens,
            "messages_per_minute": (
                (self._message_count / (session_duration / 60))
                if session_duration > 0
                else 0
            ),
            "connection_status": self.connection_status.value,
            "current_model": self.config.model,
            "current_provider": self.config.provider,
            "session_id": self.current_session_id,
        }


# Convenience function for running the interface
async def run_terminal_interface(
    config: AppConfig,
    agent_loop: AgentLoop,
    session_manager: SessionManager,
    command_history: CommandHistory,
) -> None:
    """
    Run the terminal interface.

    Args:
        config: Application configuration
        agent_loop: Agent loop instance
        session_manager: Session manager instance
        command_history: Command history instance
    """
    app = TerminalInterface(config, agent_loop, session_manager, command_history)

    try:
        await app.run_async()
    except Exception as e:
        logger.error(f"Terminal interface error: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        try:
            await agent_loop.cleanup()
            await session_manager.cleanup()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
