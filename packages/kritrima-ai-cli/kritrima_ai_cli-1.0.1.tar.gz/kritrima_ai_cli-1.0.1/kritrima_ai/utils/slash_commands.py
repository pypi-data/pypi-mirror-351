"""
Slash command system for Kritrima AI CLI.

This module provides a comprehensive slash command system with auto-completion,
help information, and command processing capabilities.
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from kritrima_ai.utils.git_utils import get_git_diff
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SlashCommand:
    """Represents a slash command with metadata."""

    command: str
    description: str
    aliases: List[str] = None
    parameters: List[str] = None
    examples: List[str] = None
    category: str = "general"

    def __post_init__(self):
        """Initialize default values."""
        if self.aliases is None:
            self.aliases = []
        if self.parameters is None:
            self.parameters = []
        if self.examples is None:
            self.examples = []


class SlashCommandProcessor:
    """
    Processes slash commands and provides auto-completion.

    Features:
    - Command registration and execution
    - Auto-completion with fuzzy matching
    - Help system with categorized commands
    - Parameter validation and suggestions
    - Command history and usage tracking
    """

    def __init__(self):
        """Initialize the slash command processor."""
        self.commands: Dict[str, SlashCommand] = {}
        self.handlers: Dict[str, Callable] = {}
        self.command_history: List[str] = []
        self.usage_stats: Dict[str, int] = {}

        # Register built-in commands
        self._register_builtin_commands()

        logger.debug("Slash command processor initialized")

    def _register_builtin_commands(self) -> None:
        """Register built-in slash commands."""

        # Core commands
        self.register_command(
            SlashCommand(
                command="/help",
                description="Show help information and available commands",
                examples=["/help", "/help model"],
                category="core",
            )
        )

        self.register_command(
            SlashCommand(
                command="/clear",
                description="Clear conversation history",
                aliases=["/cls"],
                examples=["/clear"],
                category="core",
            )
        )

        self.register_command(
            SlashCommand(
                command="/quit",
                description="Exit the application",
                aliases=["/exit", "/q"],
                examples=["/quit"],
                category="core",
            )
        )

        # Model and provider commands
        self.register_command(
            SlashCommand(
                command="/model",
                description="Open model selection panel",
                aliases=["/m"],
                parameters=["[model_name]"],
                examples=["/model", "/model gpt-4"],
                category="ai",
            )
        )

        self.register_command(
            SlashCommand(
                command="/provider",
                description="Switch AI provider",
                aliases=["/p"],
                parameters=["[provider_name]"],
                examples=["/provider", "/provider openai"],
                category="ai",
            )
        )

        self.register_command(
            SlashCommand(
                command="/models",
                description="List available models for current provider",
                examples=["/models"],
                category="ai",
            )
        )

        # Session management
        self.register_command(
            SlashCommand(
                command="/sessions",
                description="Browse previous sessions",
                aliases=["/s"],
                examples=["/sessions"],
                category="session",
            )
        )

        self.register_command(
            SlashCommand(
                command="/history",
                description="Show command history",
                aliases=["/h"],
                parameters=["[count]"],
                examples=["/history", "/history 10"],
                category="session",
            )
        )

        self.register_command(
            SlashCommand(
                command="/save",
                description="Save current session",
                parameters=["[filename]"],
                examples=["/save", "/save my_session"],
                category="session",
            )
        )

        self.register_command(
            SlashCommand(
                command="/load",
                description="Load saved session",
                parameters=["<filename>"],
                examples=["/load my_session"],
                category="session",
            )
        )

        self.register_command(
            SlashCommand(
                command="/export",
                description="Export current session to file",
                parameters=["[filename]"],
                examples=["/export", "/export session.json"],
                category="session",
            )
        )

        self.register_command(
            SlashCommand(
                command="/import",
                description="Import session from file",
                parameters=["<filename>"],
                examples=["/import session.json"],
                category="session",
            )
        )

        # Context and conversation management
        self.register_command(
            SlashCommand(
                command="/compact",
                description="Compress conversation context to save tokens",
                examples=["/compact"],
                category="context",
            )
        )

        self.register_command(
            SlashCommand(
                command="/context",
                description="Show current context information",
                examples=["/context"],
                category="context",
            )
        )

        self.register_command(
            SlashCommand(
                command="/reset",
                description="Reset conversation context",
                examples=["/reset"],
                category="context",
            )
        )

        # Git and development commands
        self.register_command(
            SlashCommand(
                command="/diff",
                description="Show git diff of current changes",
                parameters=["[file_pattern]"],
                examples=["/diff", "/diff *.py"],
                category="git",
            )
        )

        self.register_command(
            SlashCommand(
                command="/status",
                description="Show git status",
                examples=["/status"],
                category="git",
            )
        )

        self.register_command(
            SlashCommand(
                command="/branch",
                description="Show current git branch",
                examples=["/branch"],
                category="git",
            )
        )

        # Configuration commands
        self.register_command(
            SlashCommand(
                command="/config",
                description="Show or modify configuration",
                parameters=["[key]", "[value]"],
                examples=["/config", "/config model gpt-4"],
                category="config",
            )
        )

        self.register_command(
            SlashCommand(
                command="/approval",
                description="Open approval mode selection",
                parameters=["[mode]"],
                examples=["/approval", "/approval auto-edit"],
                category="config",
            )
        )

        # File and project commands
        self.register_command(
            SlashCommand(
                command="/files",
                description="List files in current directory",
                parameters=["[pattern]"],
                examples=["/files", "/files *.py"],
                category="files",
            )
        )

        self.register_command(
            SlashCommand(
                command="/tree",
                description="Show directory tree structure",
                parameters=["[depth]"],
                examples=["/tree", "/tree 2"],
                category="files",
            )
        )

        self.register_command(
            SlashCommand(
                command="/find",
                description="Find files by name or pattern",
                parameters=["<pattern>"],
                examples=["/find *.py", "/find main"],
                category="files",
            )
        )

        # Debugging and diagnostics
        self.register_command(
            SlashCommand(
                command="/debug",
                description="Toggle debug mode",
                examples=["/debug"],
                category="debug",
            )
        )

        self.register_command(
            SlashCommand(
                command="/stats",
                description="Show performance statistics",
                examples=["/stats"],
                category="debug",
            )
        )

        self.register_command(
            SlashCommand(
                command="/bug",
                description="Generate bug report URL",
                examples=["/bug"],
                category="debug",
            )
        )

        # Advanced features
        self.register_command(
            SlashCommand(
                command="/analyze",
                description="Analyze current project structure",
                parameters=["[scope]"],
                examples=["/analyze", "/analyze deep"],
                category="advanced",
            )
        )

        self.register_command(
            SlashCommand(
                command="/optimize",
                description="Optimize conversation for performance",
                examples=["/optimize"],
                category="advanced",
            )
        )

        self.register_command(
            SlashCommand(
                command="/benchmark",
                description="Run performance benchmarks",
                examples=["/benchmark"],
                category="advanced",
            )
        )

    def register_command(self, command: SlashCommand) -> None:
        """
        Register a new slash command.

        Args:
            command: Command to register
        """
        self.commands[command.command] = command

        # Register aliases
        for alias in command.aliases:
            self.commands[alias] = command

        logger.debug(f"Registered command: {command.command}")

    def register_handler(self, command: str, handler: Callable) -> None:
        """
        Register a command handler.

        Args:
            command: Command name
            handler: Handler function
        """
        self.handlers[command] = handler
        logger.debug(f"Registered handler for: {command}")

    def get_command(self, command: str) -> Optional[SlashCommand]:
        """
        Get command definition.

        Args:
            command: Command name

        Returns:
            Command definition or None
        """
        return self.commands.get(command)

    def is_command(self, text: str) -> bool:
        """
        Check if text is a slash command.

        Args:
            text: Text to check

        Returns:
            True if text is a command
        """
        return text.strip().startswith("/")

    def parse_command(self, text: str) -> tuple[str, List[str]]:
        """
        Parse command and arguments.

        Args:
            text: Command text

        Returns:
            Tuple of (command, arguments)
        """
        parts = text.strip().split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        return command, args

    async def execute_command(self, text: str, context: Dict[str, Any] = None) -> Any:
        """
        Execute a slash command.

        Args:
            text: Command text
            context: Execution context

        Returns:
            Command result
        """
        if not self.is_command(text):
            raise ValueError(f"Not a slash command: {text}")

        command, args = self.parse_command(text)

        # Track usage
        self.usage_stats[command] = self.usage_stats.get(command, 0) + 1
        self.command_history.append(text)

        # Find handler
        handler = self.handlers.get(command)
        if not handler:
            # Try to find a built-in handler
            handler = self._get_builtin_handler(command)

        if not handler:
            raise ValueError(f"Unknown command: {command}")

        logger.debug(f"Executing command: {command} with args: {args}")

        # Execute handler
        if context is None:
            context = {}

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(args, context)
            else:
                result = handler(args, context)

            return result
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            raise

    def _get_builtin_handler(self, command: str) -> Optional[Callable]:
        """Get built-in command handler."""
        handlers = {
            "/help": self._handle_help,
            "/clear": self._handle_clear,
            "/quit": self._handle_quit,
            "/model": self._handle_model,
            "/provider": self._handle_provider,
            "/models": self._handle_models,
            "/sessions": self._handle_sessions,
            "/history": self._handle_history,
            "/save": self._handle_save,
            "/load": self._handle_load,
            "/export": self._handle_export,
            "/import": self._handle_import,
            "/compact": self._handle_compact,
            "/context": self._handle_context,
            "/reset": self._handle_reset,
            "/diff": self._handle_diff,
            "/status": self._handle_status,
            "/branch": self._handle_branch,
            "/config": self._handle_config,
            "/approval": self._handle_approval,
            "/files": self._handle_files,
            "/tree": self._handle_tree,
            "/find": self._handle_find,
            "/debug": self._handle_debug,
            "/stats": self._handle_stats,
            "/bug": self._handle_bug,
            "/analyze": self._handle_analyze,
            "/optimize": self._handle_optimize,
            "/benchmark": self._handle_benchmark,
        }

        return handlers.get(command)

    def get_completions(self, text: str) -> List[str]:
        """
        Get command completions for partial text.

        Args:
            text: Partial command text

        Returns:
            List of possible completions
        """
        if not text.startswith("/"):
            return []

        # Get all command names
        all_commands = set(self.commands.keys())

        # Filter by prefix
        prefix = text.lower()
        matches = [cmd for cmd in all_commands if cmd.lower().startswith(prefix)]

        # Sort by usage frequency and alphabetically
        def sort_key(cmd):
            usage = self.usage_stats.get(cmd, 0)
            return (-usage, cmd)  # Negative usage for descending order

        matches.sort(key=sort_key)

        return matches[:10]  # Limit to top 10

    def get_help_text(self, command: str = None) -> str:
        """
        Get help text for command or all commands.

        Args:
            command: Specific command to get help for

        Returns:
            Help text
        """
        if command:
            cmd_obj = self.get_command(command)
            if not cmd_obj:
                return f"Unknown command: {command}"

            help_text = f"**{cmd_obj.command}**\n"
            help_text += f"{cmd_obj.description}\n\n"

            if cmd_obj.parameters:
                help_text += f"**Parameters:** {' '.join(cmd_obj.parameters)}\n\n"

            if cmd_obj.aliases:
                help_text += f"**Aliases:** {', '.join(cmd_obj.aliases)}\n\n"

            if cmd_obj.examples:
                help_text += "**Examples:**\n"
                for example in cmd_obj.examples:
                    help_text += f"  {example}\n"

            return help_text

        else:
            # Show all commands grouped by category
            categories = {}
            for cmd_obj in set(self.commands.values()):
                category = cmd_obj.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(cmd_obj)

            help_text = "**Available Commands:**\n\n"

            for category, commands in sorted(categories.items()):
                help_text += f"**{category.title()}:**\n"
                for cmd in sorted(commands, key=lambda x: x.command):
                    help_text += f"  {cmd.command:<20} {cmd.description}\n"
                help_text += "\n"

            help_text += (
                "Use `/help <command>` for detailed help on a specific command.\n"
            )

            return help_text

    # Built-in command handlers
    async def _handle_help(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle help command."""
        command = args[0] if args else None
        return self.get_help_text(command)

    async def _handle_clear(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle clear command."""
        # This would be handled by the UI
        return "CLEAR_CHAT"

    async def _handle_quit(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle quit command."""
        return "QUIT_APPLICATION"

    async def _handle_model(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle model command."""
        if args:
            return f"SWITCH_MODEL:{args[0]}"
        else:
            return "SHOW_MODEL_SELECTION"

    async def _handle_provider(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle provider command."""
        if args:
            return f"SWITCH_PROVIDER:{args[0]}"
        else:
            return "SHOW_PROVIDER_SELECTION"

    async def _handle_models(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle models command."""
        return "LIST_MODELS"

    async def _handle_sessions(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle sessions command."""
        return "SHOW_SESSIONS"

    async def _handle_history(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle history command."""
        count = 10
        if args:
            try:
                count = int(args[0])
            except ValueError:
                pass

        recent_commands = self.command_history[-count:]
        if recent_commands:
            history_text = "**Recent Commands:**\n"
            for i, cmd in enumerate(recent_commands, 1):
                history_text += f"{i}. {cmd}\n"
            return history_text
        else:
            return "No command history found."

    async def _handle_save(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle save command."""
        filename = args[0] if args else None
        return f"SAVE_SESSION:{filename}" if filename else "SAVE_SESSION"

    async def _handle_load(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle load command."""
        if not args:
            return "Error: Filename required for load command"
        return f"LOAD_SESSION:{args[0]}"

    async def _handle_export(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle export command."""
        filename = args[0] if args else None
        return f"EXPORT_SESSION:{filename}" if filename else "EXPORT_SESSION"

    async def _handle_import(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle import command."""
        if not args:
            return "Error: Filename required for import command"
        return f"IMPORT_SESSION:{args[0]}"

    async def _handle_compact(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle compact command."""
        return "COMPACT_CONVERSATION"

    async def _handle_context(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle context command."""
        return "SHOW_CONTEXT_INFO"

    async def _handle_reset(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle reset command."""
        return "RESET_CONVERSATION"

    async def _handle_diff(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle diff command."""
        try:
            diff = get_git_diff()
            if diff:
                return f"**Git Diff:**\n```diff\n{diff}\n```"
            else:
                return "No git changes found."
        except Exception as e:
            return f"Error getting git diff: {e}"

    async def _handle_status(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle status command."""
        try:
            from kritrima_ai.utils.git_utils import get_git_status

            status = get_git_status()
            return (
                f"**Git Status:**\n```\n{status}\n```"
                if status
                else "No git status available."
            )
        except Exception as e:
            return f"Error getting git status: {e}"

    async def _handle_branch(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle branch command."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                return f"Current branch: {branch}" if branch else "Not on any branch"
            else:
                return "Not in a git repository"
        except Exception as e:
            return f"Error getting branch info: {e}"

    async def _handle_config(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle config command."""
        if len(args) >= 2:
            return f"SET_CONFIG:{args[0]}={args[1]}"
        elif len(args) == 1:
            return f"GET_CONFIG:{args[0]}"
        else:
            return "SHOW_CONFIG"

    async def _handle_approval(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle approval command."""
        if args:
            return f"SET_APPROVAL_MODE:{args[0]}"
        else:
            return "SHOW_APPROVAL_SETTINGS"

    async def _handle_files(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle files command."""
        pattern = args[0] if args else "*"
        return f"LIST_FILES:{pattern}"

    async def _handle_tree(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle tree command."""
        depth = 2
        if args:
            try:
                depth = int(args[0])
            except ValueError:
                pass
        return f"SHOW_TREE:{depth}"

    async def _handle_find(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle find command."""
        if not args:
            return "Error: Pattern required for find command"
        pattern = args[0]
        return f"FIND_FILES:{pattern}"

    async def _handle_debug(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle debug command."""
        return "TOGGLE_DEBUG"

    async def _handle_stats(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle stats command."""
        return "SHOW_STATS"

    async def _handle_bug(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle bug command."""
        return "GENERATE_BUG_REPORT"

    async def _handle_analyze(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle analyze command."""
        scope = args[0] if args else "normal"
        return f"ANALYZE_PROJECT:{scope}"

    async def _handle_optimize(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle optimize command."""
        return "OPTIMIZE_CONVERSATION"

    async def _handle_benchmark(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle benchmark command."""
        return "RUN_BENCHMARK"

    def get_command_categories(self) -> Dict[str, List[SlashCommand]]:
        """
        Get commands grouped by category.

        Returns:
            Dictionary of category -> commands
        """
        categories = {}
        for cmd_obj in set(self.commands.values()):
            category = cmd_obj.category
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd_obj)

        return categories

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get command usage statistics.

        Returns:
            Dictionary of command -> usage count
        """
        return self.usage_stats.copy()

    def clear_history(self) -> None:
        """Clear command history."""
        self.command_history.clear()
        logger.debug("Command history cleared")


# Global instance
_command_processor = SlashCommandProcessor()


def get_command_processor() -> SlashCommandProcessor:
    """Get global command processor instance."""
    return _command_processor


# Convenience functions
SLASH_COMMANDS = [
    SlashCommand(command="/help", description="Show help information"),
    SlashCommand(command="/clear", description="Clear conversation history"),
    SlashCommand(command="/model", description="Open model selection panel"),
    SlashCommand(command="/sessions", description="Browse previous sessions"),
    SlashCommand(command="/history", description="Show command history"),
    SlashCommand(command="/compact", description="Compress conversation context"),
    SlashCommand(command="/diff", description="Show git diff"),
    SlashCommand(command="/config", description="Show configuration"),
    SlashCommand(command="/approval", description="Open approval mode selection"),
    SlashCommand(command="/bug", description="Generate bug report URL"),
    SlashCommand(command="/stats", description="Show performance statistics"),
    SlashCommand(command="/quit", description="Exit the application"),
]


def get_command_completions(text: str) -> List[str]:
    """Get command completions for text."""
    return _command_processor.get_completions(text)


async def execute_slash_command(text: str, context: Dict[str, Any] = None) -> Any:
    """Execute a slash command."""
    return await _command_processor.execute_command(text, context)
