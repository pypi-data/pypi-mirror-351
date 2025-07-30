"""
Overlay widgets for Kritrima AI CLI terminal interface.

This module provides modal overlay widgets for various functionality:
- Help overlays with command information
- Diff overlays for git changes
- Approval mode configuration
- Configuration viewing and editing
- File suggestions popup
- Debug information displays
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Header,
    Label,
    ListItem,
    ListView,
    RadioButton,
    RadioSet,
    Static,
)

from kritrima_ai.config.app_config import AppConfig, ApprovalMode
from kritrima_ai.utils.logger import get_logger
from kritrima_ai.utils.slash_commands import SLASH_COMMANDS

logger = get_logger(__name__)


class HelpOverlay(ModalScreen[None]):
    """
    Help overlay showing commands, shortcuts, and usage information.

    Provides comprehensive help with tabbed interface for different categories.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Previous Tab"),
    ]

    def __init__(self, **kwargs):
        """Initialize help overlay."""
        super().__init__(**kwargs)
        self.current_tab = 0
        self.tabs = ["Commands", "Shortcuts", "File Tags", "Configuration", "Examples"]

    def compose(self):
        """Compose the help overlay."""
        with Container(id="help_container", classes="modal_container"):
            yield Header()
            with Container(id="help_content"):
                yield Static(id="help_display")
            with Horizontal(id="help_navigation"):
                for i, tab in enumerate(self.tabs):
                    yield Button(
                        tab, id=f"tab_{i}", variant="primary" if i == 0 else "default"
                    )
            with Horizontal(id="help_actions"):
                yield Button("Close", variant="error", id="close_help")

    async def on_mount(self) -> None:
        """Setup help overlay after mounting."""
        await self._show_tab_content(0)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close_help":
            self.dismiss()
        elif event.button.id.startswith("tab_"):
            tab_index = int(event.button.id.split("_")[1])
            await self._switch_tab(tab_index)

    async def _switch_tab(self, tab_index: int) -> None:
        """Switch to a different tab."""
        if 0 <= tab_index < len(self.tabs):
            # Update button states
            for i, tab in enumerate(self.tabs):
                button = self.query_one(f"#tab_{i}", Button)
                button.variant = "primary" if i == tab_index else "default"

            self.current_tab = tab_index
            await self._show_tab_content(tab_index)

    async def _show_tab_content(self, tab_index: int) -> None:
        """Show content for the specified tab."""
        display = self.query_one("#help_display", Static)

        if tab_index == 0:  # Commands
            content = self._get_commands_help()
        elif tab_index == 1:  # Shortcuts
            content = self._get_shortcuts_help()
        elif tab_index == 2:  # File Tags
            content = self._get_file_tags_help()
        elif tab_index == 3:  # Configuration
            content = self._get_configuration_help()
        elif tab_index == 4:  # Examples
            content = self._get_examples_help()
        else:
            content = Text("Help content not available")

        display.update(content)

    def _get_commands_help(self) -> Panel:
        """Get help content for slash commands."""
        table = Table(
            title="Available Slash Commands",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Usage", style="dim")

        for cmd in SLASH_COMMANDS:
            usage = f"{cmd.command}"
            if hasattr(cmd, "args") and cmd.args:
                usage += f" {cmd.args}"

            table.add_row(cmd.command, cmd.description, usage)

        return Panel(
            table, title="[bold cyan]Slash Commands[/bold cyan]", border_style="cyan"
        )

    def _get_shortcuts_help(self) -> Panel:
        """Get help content for keyboard shortcuts."""
        table = Table(
            title="Keyboard Shortcuts", show_header=True, header_style="bold magenta"
        )
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Action", style="white")
        table.add_column("Context", style="dim")

        shortcuts = [
            ("Ctrl+C", "Quit application", "Global"),
            ("Ctrl+M", "Model selection", "Global"),
            ("Ctrl+H", "Command history", "Global"),
            ("Ctrl+S", "Session browser", "Global"),
            ("Ctrl+L", "Clear chat", "Global"),
            ("F1", "Show help", "Global"),
            ("Tab", "Auto-complete", "Input"),
            ("Ctrl+Space", "Show completions", "Input"),
            ("Ctrl+P", "Previous history", "Input"),
            ("Ctrl+N", "Next history", "Input"),
            ("Ctrl+A", "Go to start", "Input"),
            ("Ctrl+E", "Go to end", "Input"),
            ("Ctrl+K", "Delete to end", "Input"),
            ("Ctrl+U", "Delete to start", "Input"),
            ("Ctrl+W", "Delete word", "Input"),
            ("Escape", "Close overlay", "Overlay"),
        ]

        for key, action, context in shortcuts:
            table.add_row(key, action, context)

        return Panel(
            table,
            title="[bold cyan]Keyboard Shortcuts[/bold cyan]",
            border_style="cyan",
        )

    def _get_file_tags_help(self) -> Panel:
        """Get help content for file tags."""
        content = Text()
        content.append("File Tags Usage\n\n", style="bold cyan")

        content.append(
            "File tags allow you to include file contents in your messages:\n\n",
            style="white",
        )

        examples = [
            ("@filename.py", "Include a specific file"),
            ("@*.py", "Include all Python files in current directory"),
            ("@src/", "Include all files in src directory"),
            ("@**/*.js", "Include all JavaScript files recursively"),
            ("@README.md @src/main.py", "Include multiple files"),
        ]

        for tag, description in examples:
            content.append(f"  {tag}", style="cyan bold")
            content.append(f" - {description}\n", style="white")

        content.append("\nTips:\n", style="bold yellow")
        content.append("• Use Tab for auto-completion of file paths\n", style="white")
        content.append("• File contents are included as XML blocks\n", style="white")
        content.append("• Large files may be truncated\n", style="white")
        content.append("• Binary files are skipped automatically\n", style="white")

        return Panel(
            content, title="[bold cyan]File Tags[/bold cyan]", border_style="cyan"
        )

    def _get_configuration_help(self) -> Panel:
        """Get help content for configuration."""
        content = Text()
        content.append("Configuration Options\n\n", style="bold cyan")

        content.append("Configuration files (in order of precedence):\n", style="white")
        config_files = [
            "Command line arguments",
            "Environment variables",
            "Project config: .kritrima-ai/config.json",
            "User config: ~/.kritrima-ai/config.json",
            "Default values",
        ]

        for config_file in config_files:
            content.append(f"  • {config_file}\n", style="white")

        content.append("\nKey Settings:\n", style="bold yellow")
        settings = [
            ("model", "AI model to use (e.g., gpt-4, claude-3-sonnet)"),
            ("provider", "AI provider (openai, anthropic, gemini, etc.)"),
            ("approval_mode", "Command approval: suggest, auto-edit, full-auto"),
            ("debug", "Enable debug logging"),
            ("verbose", "Enable verbose output"),
        ]

        for setting, description in settings:
            content.append(f"  {setting}", style="cyan bold")
            content.append(f" - {description}\n", style="white")

        content.append("\nEnvironment Variables:\n", style="bold yellow")
        env_vars = [
            ("OPENAI_API_KEY", "OpenAI API key"),
            ("ANTHROPIC_API_KEY", "Anthropic API key"),
            ("GOOGLE_AI_KEY", "Google AI API key"),
            ("PROVIDER_API_KEY", "Generic provider API key"),
        ]

        for var, description in env_vars:
            content.append(f"  {var}", style="green bold")
            content.append(f" - {description}\n", style="white")

        return Panel(
            content, title="[bold cyan]Configuration[/bold cyan]", border_style="cyan"
        )

    def _get_examples_help(self) -> Panel:
        """Get help content with usage examples."""
        content = Text()
        content.append("Usage Examples\n\n", style="bold cyan")

        content.append("Basic Usage:\n", style="bold yellow")
        basic_examples = [
            "kritrima-ai",
            'kritrima-ai "Explain this code" --file main.py',
            "kritrima-ai --model gpt-4 --provider openai",
            'kritrima-ai --full-context "Refactor this project"',
        ]

        for example in basic_examples:
            content.append(f"  $ {example}\n", style="green")

        content.append("\nInteractive Commands:\n", style="bold yellow")
        interactive_examples = [
            ("/help", "Show this help"),
            ("/model", "Change AI model"),
            ("/history", "View command history"),
            ("/sessions", "Browse saved sessions"),
            ("/clear", "Clear conversation"),
            ("/diff", "Show git changes"),
            ("/compact", "Compress context"),
        ]

        for cmd, desc in interactive_examples:
            content.append(f"  {cmd}", style="cyan bold")
            content.append(f" - {desc}\n", style="white")

        content.append("\nFile Tag Examples:\n", style="bold yellow")
        file_examples = [
            '"Review this code: @src/main.py"',
            '"Compare these files: @old.py @new.py"',
            '"Analyze all Python files: @*.py"',
            '"Include documentation: @README.md @docs/"',
        ]

        for example in file_examples:
            content.append(f"  {example}\n", style="cyan")

        return Panel(
            content, title="[bold cyan]Examples[/bold cyan]", border_style="cyan"
        )

    def action_next_tab(self) -> None:
        """Switch to next tab."""
        next_tab = (self.current_tab + 1) % len(self.tabs)
        asyncio.create_task(self._switch_tab(next_tab))

    def action_prev_tab(self) -> None:
        """Switch to previous tab."""
        prev_tab = (self.current_tab - 1) % len(self.tabs)
        asyncio.create_task(self._switch_tab(prev_tab))

    def action_dismiss(self) -> None:
        """Close the help overlay."""
        self.dismiss()


class DiffOverlay(ModalScreen[None]):
    """
    Diff overlay showing git changes with syntax highlighting.

    Displays git diff with proper formatting and navigation.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, **kwargs):
        """Initialize diff overlay."""
        super().__init__(**kwargs)
        self.diff_content = ""
        self.git_status = ""

    def compose(self):
        """Compose the diff overlay."""
        with Container(id="diff_container", classes="modal_container"):
            yield Header()
            with Container(id="diff_content"):
                yield Static(id="git_status", classes="status_section")
                yield ScrollableContainer(Static(id="diff_display"))
            with Horizontal(id="diff_actions"):
                yield Button("Refresh", variant="primary", id="refresh_diff")
                yield Button("Close", variant="error", id="close_diff")

    async def on_mount(self) -> None:
        """Load git diff after mounting."""
        await self._load_git_diff()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close_diff":
            self.dismiss()
        elif event.button.id == "refresh_diff":
            await self.action_refresh()

    async def _load_git_diff(self) -> None:
        """Load git diff and status."""
        try:
            # Get git status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            if status_result.returncode == 0:
                self.git_status = status_result.stdout.strip()
            else:
                self.git_status = "Not a git repository or git not available"

            # Get git diff
            diff_result = subprocess.run(
                ["git", "diff", "--color=never"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            if diff_result.returncode == 0:
                self.diff_content = diff_result.stdout
            else:
                self.diff_content = "No git changes found or error getting diff"

            await self._update_display()

        except Exception as e:
            logger.error(f"Error loading git diff: {e}")
            self.git_status = f"Error: {e}"
            self.diff_content = "Could not load git diff"
            await self._update_display()

    async def _update_display(self) -> None:
        """Update the diff display."""
        # Update status
        status_widget = self.query_one("#git_status", Static)
        if self.git_status:
            status_lines = self.git_status.split("\n")
            status_text = Text()
            status_text.append("Git Status:\n", style="bold cyan")

            for line in status_lines:
                if line.strip():
                    # Color code git status
                    if line.startswith(" M"):
                        status_text.append(f"  Modified: {line[3:]}\n", style="yellow")
                    elif line.startswith("M "):
                        status_text.append(f"  Staged: {line[3:]}\n", style="green")
                    elif line.startswith("??"):
                        status_text.append(f"  Untracked: {line[3:]}\n", style="red")
                    elif line.startswith(" D"):
                        status_text.append(f"  Deleted: {line[3:]}\n", style="red")
                    elif line.startswith("A "):
                        status_text.append(f"  Added: {line[3:]}\n", style="green")
                    else:
                        status_text.append(f"  {line}\n", style="white")

            status_widget.update(status_text)
        else:
            status_widget.update("No git status available")

        # Update diff display
        diff_widget = self.query_one("#diff_display", Static)
        if self.diff_content:
            # Use syntax highlighting for diff
            try:
                highlighted_diff = Syntax(
                    self.diff_content, "diff", theme="monokai", line_numbers=False
                )
                diff_widget.update(highlighted_diff)
            except Exception:
                # Fallback to plain text with basic coloring
                diff_text = Text()
                for line in self.diff_content.split("\n"):
                    if line.startswith("+++") or line.startswith("---"):
                        diff_text.append(line + "\n", style="bold white")
                    elif line.startswith("@@"):
                        diff_text.append(line + "\n", style="cyan")
                    elif line.startswith("+"):
                        diff_text.append(line + "\n", style="green")
                    elif line.startswith("-"):
                        diff_text.append(line + "\n", style="red")
                    else:
                        diff_text.append(line + "\n", style="white")

                diff_widget.update(diff_text)
        else:
            diff_widget.update("No git diff available")

    async def action_refresh(self) -> None:
        """Refresh git diff."""
        await self._load_git_diff()

    def action_dismiss(self) -> None:
        """Close the diff overlay."""
        self.dismiss()


class ApprovalModeOverlay(ModalScreen[Optional[str]]):
    """
    Approval mode configuration overlay.

    Allows user to configure command approval behavior.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("enter", "apply", "Apply"),
    ]

    def __init__(self, current_mode: ApprovalMode, **kwargs):
        """Initialize approval mode overlay."""
        super().__init__(**kwargs)
        self.current_mode = current_mode
        self.selected_mode = current_mode

    def compose(self):
        """Compose the approval mode overlay."""
        with Container(id="approval_container", classes="modal_container"):
            yield Header()
            with Container(id="approval_content"):
                yield Label("Select Approval Mode:", classes="section_title")
                yield RadioSet(
                    RadioButton(
                        "Suggest - Manual approval for all commands",
                        value=True if self.current_mode == "suggest" else False,
                        id="suggest",
                    ),
                    RadioButton(
                        "Auto-edit - Auto approve file edits, manual for commands",
                        value=True if self.current_mode == "auto-edit" else False,
                        id="auto_edit",
                    ),
                    RadioButton(
                        "Full-auto - Auto approve everything (use with caution)",
                        value=True if self.current_mode == "full-auto" else False,
                        id="full_auto",
                    ),
                    id="approval_radio_set",
                )
                yield Static(id="mode_description")
            with Horizontal(id="approval_actions"):
                yield Button("Apply", variant="primary", id="apply_approval")
                yield Button("Cancel", variant="default", id="cancel_approval")

    async def on_mount(self) -> None:
        """Setup approval mode overlay after mounting."""
        await self._update_description()

    async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle approval mode selection."""
        if event.pressed.id == "suggest":
            self.selected_mode = "suggest"
        elif event.pressed.id == "auto_edit":
            self.selected_mode = "auto-edit"
        elif event.pressed.id == "full_auto":
            self.selected_mode = "full-auto"

        await self._update_description()

    async def _update_description(self) -> None:
        """Update mode description."""
        description_widget = self.query_one("#mode_description", Static)

        descriptions = {
            "suggest": "Manual approval required for all AI actions. Safest option for production use.",
            "auto-edit": "Automatically approve file edits and patches, but require manual approval for shell commands. Balanced safety and productivity.",
            "full-auto": "Automatically approve all AI actions. Fastest but requires careful monitoring. Use only in safe environments.",
        }

        description = descriptions.get(self.selected_mode, "")
        description_widget.update(Text(description, style="dim"))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "apply_approval":
            self.dismiss(self.selected_mode)
        elif event.button.id == "cancel_approval":
            self.dismiss(None)

    def action_apply(self) -> None:
        """Apply selected approval mode."""
        self.dismiss(self.selected_mode)

    def action_dismiss(self) -> None:
        """Cancel approval mode selection."""
        self.dismiss(None)


class ConfigOverlay(ModalScreen[None]):
    """
    Configuration overlay showing current settings.

    Displays comprehensive configuration information in a tabbed interface.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, config: AppConfig, **kwargs):
        """Initialize config overlay."""
        super().__init__(**kwargs)
        self.config = config
        self.current_tab = 0
        self.tabs = ["General", "Providers", "Security", "UI", "Advanced"]

    def compose(self):
        """Compose the config overlay."""
        with Container(id="config_container", classes="modal_container"):
            yield Header()
            with Container(id="config_content"):
                yield Static(id="config_display")
            with Horizontal(id="config_navigation"):
                for i, tab in enumerate(self.tabs):
                    yield Button(
                        tab,
                        id=f"config_tab_{i}",
                        variant="primary" if i == 0 else "default",
                    )
            with Horizontal(id="config_actions"):
                yield Button("Refresh", variant="primary", id="refresh_config")
                yield Button("Close", variant="error", id="close_config")

    async def on_mount(self) -> None:
        """Setup config overlay after mounting."""
        await self._show_tab_content(0)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close_config":
            self.dismiss()
        elif event.button.id == "refresh_config":
            await self.action_refresh()
        elif event.button.id.startswith("config_tab_"):
            tab_index = int(event.button.id.split("_")[2])
            await self._switch_tab(tab_index)

    async def _switch_tab(self, tab_index: int) -> None:
        """Switch to a different tab."""
        if 0 <= tab_index < len(self.tabs):
            # Update button states
            for i, tab in enumerate(self.tabs):
                button = self.query_one(f"#config_tab_{i}", Button)
                button.variant = "primary" if i == tab_index else "default"

            self.current_tab = tab_index
            await self._show_tab_content(tab_index)

    async def _show_tab_content(self, tab_index: int) -> None:
        """Show content for the specified tab."""
        display = self.query_one("#config_display", Static)

        if tab_index == 0:  # General
            content = self._get_general_config()
        elif tab_index == 1:  # Providers
            content = self._get_providers_config()
        elif tab_index == 2:  # Security
            content = self._get_security_config()
        elif tab_index == 3:  # UI
            content = self._get_ui_config()
        elif tab_index == 4:  # Advanced
            content = self._get_advanced_config()
        else:
            content = Text("Configuration section not available")

        display.update(content)

    def _get_general_config(self) -> Panel:
        """Get general configuration display."""
        table = Table(
            title="General Configuration", show_header=True, header_style="bold magenta"
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Description", style="dim")

        general_settings = [
            ("Model", self.config.model, "Current AI model"),
            ("Provider", self.config.provider, "AI provider"),
            ("Approval Mode", self.config.approval_mode, "Command approval behavior"),
            ("Debug", str(self.config.debug), "Debug logging enabled"),
            ("Verbose", str(self.config.verbose), "Verbose output enabled"),
            ("Temperature", str(self.config.temperature), "AI response randomness"),
            (
                "Max Tokens",
                str(self.config.max_tokens or "Auto"),
                "Maximum response tokens",
            ),
            ("Timeout", f"{self.config.timeout}s", "Request timeout"),
        ]

        for setting, value, desc in general_settings:
            table.add_row(setting, value, desc)

        return Panel(
            table, title="[bold cyan]General Settings[/bold cyan]", border_style="cyan"
        )

    def _get_providers_config(self) -> Panel:
        """Get providers configuration display."""
        content = Text()
        content.append("AI Providers Configuration\n\n", style="bold cyan")

        # Current provider details
        content.append(f"Active Provider: {self.config.provider}\n", style="bold white")
        content.append(f"Active Model: {self.config.model}\n\n", style="bold white")

        # Environment variables status
        content.append("API Keys Status:\n", style="bold yellow")

        env_vars = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("GOOGLE_AI_KEY", "Google AI"),
            ("MISTRAL_API_KEY", "Mistral"),
            ("DEEPSEEK_API_KEY", "DeepSeek"),
            ("XAI_API_KEY", "xAI"),
            ("GROQ_API_KEY", "Groq"),
        ]

        for env_var, provider_name in env_vars:
            import os

            status = "✓ Set" if os.getenv(env_var) else "✗ Not set"
            style = "green" if os.getenv(env_var) else "red"
            content.append(f"  {provider_name}: ", style="white")
            content.append(f"{status}\n", style=style)

        # Custom providers
        if self.config.custom_providers:
            content.append("\nCustom Providers:\n", style="bold yellow")
            for provider_id, provider_config in self.config.custom_providers.items():
                content.append(
                    f"  {provider_id}: {provider_config.get('name', 'Unknown')}\n",
                    style="cyan",
                )

        return Panel(
            content, title="[bold cyan]Providers[/bold cyan]", border_style="cyan"
        )

    def _get_security_config(self) -> Panel:
        """Get security configuration display."""
        table = Table(
            title="Security Configuration",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Description", style="dim")

        security_settings = [
            ("Approval Mode", self.config.approval_mode, "Command approval behavior"),
            (
                "Safe Commands",
                str(len(self.config.security.safe_commands)),
                "Number of pre-approved commands",
            ),
            (
                "Dangerous Commands",
                str(len(self.config.security.dangerous_commands)),
                "Number of restricted commands",
            ),
            (
                "Auto Approve Edits",
                str(self.config.security.auto_approve_edits),
                "Auto-approve file edits",
            ),
            (
                "Require Confirmation",
                str(self.config.security.require_confirmation),
                "Require confirmation for actions",
            ),
            (
                "Sandbox Mode",
                str(self.config.security.sandbox_mode),
                "Execute commands in sandbox",
            ),
            (
                "Max File Size",
                f"{self.config.security.max_file_size_mb}MB",
                "Maximum file size for processing",
            ),
        ]

        for setting, value, desc in security_settings:
            table.add_row(setting, value, desc)

        return Panel(
            table, title="[bold cyan]Security Settings[/bold cyan]", border_style="cyan"
        )

    def _get_ui_config(self) -> Panel:
        """Get UI configuration display."""
        table = Table(
            title="UI Configuration", show_header=True, header_style="bold magenta"
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Description", style="dim")

        ui_settings = [
            ("Theme", self.config.ui.theme, "UI color theme"),
            (
                "Show Timestamps",
                str(self.config.ui.show_timestamps),
                "Show message timestamps",
            ),
            (
                "Show Performance",
                str(self.config.ui.show_performance),
                "Show performance indicators",
            ),
            ("Auto Scroll", str(self.config.ui.auto_scroll), "Auto-scroll chat"),
            (
                "Syntax Highlighting",
                str(self.config.ui.syntax_highlighting),
                "Enable syntax highlighting",
            ),
            (
                "Line Numbers",
                str(self.config.ui.show_line_numbers),
                "Show line numbers in code",
            ),
            (
                "Animations",
                str(self.config.ui.enable_animations),
                "Enable UI animations",
            ),
            (
                "Notifications",
                str(self.config.ui.enable_notifications),
                "Enable desktop notifications",
            ),
        ]

        for setting, value, desc in ui_settings:
            table.add_row(setting, value, desc)

        return Panel(
            table, title="[bold cyan]UI Settings[/bold cyan]", border_style="cyan"
        )

    def _get_advanced_config(self) -> Panel:
        """Get advanced configuration display."""
        content = Text()
        content.append("Advanced Configuration\n\n", style="bold cyan")

        # Session settings
        content.append("Session Management:\n", style="bold yellow")
        content.append(f"  Auto Save: {self.config.session.auto_save}\n", style="white")
        content.append(
            f"  Max Sessions: {self.config.session.max_sessions}\n", style="white"
        )
        content.append(
            f"  Session Timeout: {self.config.session.session_timeout_minutes} minutes\n",
            style="white",
        )
        content.append(
            f"  Compression: {self.config.session.enable_compression}\n", style="white"
        )

        # Logging settings
        content.append("\nLogging Configuration:\n", style="bold yellow")
        content.append(
            f"  File Logging: {self.config.logging.file_logging}\n", style="white"
        )
        content.append(
            f"  Console Logging: {self.config.logging.console_logging}\n", style="white"
        )
        content.append(f"  Log Level: {self.config.logging.level}\n", style="white")
        content.append(
            f"  Max Size: {self.config.logging.max_size_mb}MB\n", style="white"
        )
        content.append(
            f"  Backup Count: {self.config.logging.backup_count}\n", style="white"
        )

        # Git integration
        content.append("\nGit Integration:\n", style="bold yellow")
        content.append(
            f"  Suppress Warnings: {self.config.suppress_git_warnings}\n", style="white"
        )
        content.append(f"  Auto Commit: {self.config.auto_commit}\n", style="white")

        # Performance settings
        content.append("\nPerformance:\n", style="bold yellow")
        content.append(f"  Max Retries: {self.config.max_retries}\n", style="white")
        content.append(
            f"  Context Window: {self.config.context_window or 'Auto'}\n", style="white"
        )

        return Panel(
            content,
            title="[bold cyan]Advanced Settings[/bold cyan]",
            border_style="cyan",
        )

    async def action_refresh(self) -> None:
        """Refresh configuration display."""
        await self._show_tab_content(self.current_tab)

    def action_dismiss(self) -> None:
        """Close the config overlay."""
        self.dismiss()


class FileSuggestionsOverlay(ModalScreen[Optional[str]]):
    """
    File suggestions overlay for file path completion.

    Shows available files and directories for selection.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("up", "prev_item", "Previous"),
        Binding("down", "next_item", "Next"),
    ]

    def __init__(self, suggestions: List[str], current_path: str = "", **kwargs):
        """Initialize file suggestions overlay."""
        super().__init__(**kwargs)
        self.suggestions = suggestions
        self.current_path = current_path
        self.selected_index = 0

    def compose(self):
        """Compose the file suggestions overlay."""
        with Container(id="suggestions_container", classes="modal_container"):
            yield Label(f"File suggestions for: {self.current_path}")
            yield ListView(id="suggestions_list")
            with Horizontal(id="suggestions_actions"):
                yield Button("Select", variant="primary", id="select_file")
                yield Button("Cancel", variant="default", id="cancel_suggestions")

    async def on_mount(self) -> None:
        """Setup file suggestions after mounting."""
        suggestions_list = self.query_one("#suggestions_list", ListView)

        for i, suggestion in enumerate(self.suggestions):
            path_obj = Path(suggestion)

            # Determine display text and icon
            if path_obj.is_dir():
                display_text = f"📁 {suggestion}/"
            else:
                # Add file icon based on extension
                suffix = path_obj.suffix.lower()
                if suffix in [".py"]:
                    icon = "🐍"
                elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
                    icon = "📜"
                elif suffix in [".md", ".txt"]:
                    icon = "📝"
                elif suffix in [".json", ".yaml", ".yml"]:
                    icon = "⚙️"
                else:
                    icon = "📄"

                display_text = f"{icon} {suggestion}"

            suggestions_list.append(ListItem(Label(display_text), id=str(i)))

        # Select first item
        if self.suggestions:
            suggestions_list.highlighted = 0

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "select_file":
            await self.action_select()
        elif event.button.id == "cancel_suggestions":
            self.dismiss(None)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection."""
        await self.action_select()

    def action_select(self) -> None:
        """Select current file."""
        suggestions_list = self.query_one("#suggestions_list", ListView)
        if 0 <= suggestions_list.highlighted < len(self.suggestions):
            selected_file = self.suggestions[suggestions_list.highlighted]
            self.dismiss(selected_file)
        else:
            self.dismiss(None)

    def action_prev_item(self) -> None:
        """Select previous item."""
        suggestions_list = self.query_one("#suggestions_list", ListView)
        if suggestions_list.highlighted > 0:
            suggestions_list.highlighted -= 1

    def action_next_item(self) -> None:
        """Select next item."""
        suggestions_list = self.query_one("#suggestions_list", ListView)
        if suggestions_list.highlighted < len(self.suggestions) - 1:
            suggestions_list.highlighted += 1

    def action_dismiss(self) -> None:
        """Cancel file selection."""
        self.dismiss(None)


class DebugOverlay(ModalScreen[None]):
    """
    Debug overlay showing system information and performance metrics.

    Provides comprehensive debugging information for troubleshooting.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, debug_info: Dict[str, Any], **kwargs):
        """Initialize debug overlay."""
        super().__init__(**kwargs)
        self.debug_info = debug_info

    def compose(self):
        """Compose the debug overlay."""
        with Container(id="debug_container", classes="modal_container"):
            yield Header()
            with ScrollableContainer(id="debug_content"):
                yield Static(id="debug_display")
            with Horizontal(id="debug_actions"):
                yield Button("Refresh", variant="primary", id="refresh_debug")
                yield Button("Close", variant="error", id="close_debug")

    async def on_mount(self) -> None:
        """Setup debug overlay after mounting."""
        await self._update_debug_info()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close_debug":
            self.dismiss()
        elif event.button.id == "refresh_debug":
            await self.action_refresh()

    async def _update_debug_info(self) -> None:
        """Update debug information display."""
        debug_widget = self.query_one("#debug_display", Static)

        content = Text()
        content.append("Debug Information\n\n", style="bold cyan")

        # System information
        import platform
        import sys

        import psutil

        content.append("System Information:\n", style="bold yellow")
        content.append(f"  Platform: {platform.platform()}\n", style="white")
        content.append(f"  Python: {sys.version}\n", style="white")
        content.append(f"  CPU: {psutil.cpu_percent()}%\n", style="white")
        content.append(f"  Memory: {psutil.virtual_memory().percent}%\n", style="white")
        content.append(f"  Disk: {psutil.disk_usage('/').percent}%\n", style="white")

        # Application information
        content.append("\nApplication Information:\n", style="bold yellow")
        for key, value in self.debug_info.items():
            content.append(f"  {key}: {value}\n", style="white")

        # Performance metrics
        if "performance" in self.debug_info:
            perf_data = self.debug_info["performance"]
            content.append("\nPerformance Metrics:\n", style="bold yellow")
            for metric, value in perf_data.items():
                content.append(f"  {metric}: {value}\n", style="white")

        debug_widget.update(content)

    async def action_refresh(self) -> None:
        """Refresh debug information."""
        await self._update_debug_info()

    def action_dismiss(self) -> None:
        """Close the debug overlay."""
        self.dismiss()


# Convenience functions for creating overlays
def create_help_overlay() -> HelpOverlay:
    """Create a help overlay."""
    return HelpOverlay()


def create_diff_overlay() -> DiffOverlay:
    """Create a diff overlay."""
    return DiffOverlay()


def create_approval_mode_overlay(current_mode: ApprovalMode) -> ApprovalModeOverlay:
    """Create an approval mode overlay."""
    return ApprovalModeOverlay(current_mode)


def create_config_overlay(config: AppConfig) -> ConfigOverlay:
    """Create a config overlay."""
    return ConfigOverlay(config)


def create_file_suggestions_overlay(
    suggestions: List[str], current_path: str = ""
) -> FileSuggestionsOverlay:
    """Create a file suggestions overlay."""
    return FileSuggestionsOverlay(suggestions, current_path)


def create_debug_overlay(debug_info: Dict[str, Any]) -> DebugOverlay:
    """Create a debug overlay."""
    return DebugOverlay(debug_info)
