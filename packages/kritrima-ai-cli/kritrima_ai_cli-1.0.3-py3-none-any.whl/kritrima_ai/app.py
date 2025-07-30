"""
Main application class for Kritrima AI CLI.

This module contains the KritrimaApp class which orchestrates the entire
application, including the UI, agent loop, and session management.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from kritrima_ai.agent.agent_loop import AgentLoop
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.storage.command_history import CommandHistory
from kritrima_ai.storage.session_manager import SessionManager
from kritrima_ai.ui.terminal_interface import TerminalInterface
from kritrima_ai.utils.file_utils import is_text_file, read_file_safe
from kritrima_ai.utils.git_utils import create_git_context, get_git_status
from kritrima_ai.utils.logger import get_logger, performance_timer

logger = get_logger(__name__)
console = Console()


class KritrimaApp:
    """
    Main application class for Kritrima AI CLI.

    This class orchestrates all the major components of the application:
    - Configuration management
    - User interface
    - Agent loop execution
    - Session persistence
    - Git integration
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the Kritrima AI application.

        Args:
            config: Application configuration
        """
        self.config = config
        self.session_manager = SessionManager(config)
        self.command_history = CommandHistory(config)
        self.agent_loop: Optional[AgentLoop] = None
        self.terminal_interface: Optional[TerminalInterface] = None

        # Performance tracking
        self._startup_time = None
        self._total_requests = 0
        self._total_thinking_time = 0.0

        logger.info(
            f"Initialized Kritrima AI CLI - Provider: {config.provider}, Model: {config.model}"
        )

    async def run_interactive(
        self, initial_prompt: Optional[str] = None, files: Optional[List[Path]] = None
    ) -> None:
        """
        Run the application in interactive mode.

        Args:
            initial_prompt: Initial prompt to send to the AI
            files: List of files to include in initial context
        """
        with performance_timer("app_startup", logger):
            try:
                # Initialize components
                await self._initialize_components()

                # Create initial context
                initial_context = await self._create_initial_context(files)

                # Create new session or restore previous
                session_id = await self.session_manager.create_session()
                logger.info(f"Started session: {session_id}")

                # Initialize agent loop
                self.agent_loop = AgentLoop(
                    config=self.config,
                    session_manager=self.session_manager,
                    command_history=self.command_history,
                )

                # Initialize terminal interface
                self.terminal_interface = TerminalInterface(
                    config=self.config,
                    agent_loop=self.agent_loop,
                    session_manager=self.session_manager,
                    command_history=self.command_history,
                )

                # Show welcome message
                self._show_welcome_message()

                # Add initial context if provided
                if initial_context:
                    await self.agent_loop.add_context(initial_context)

                # Send initial prompt if provided
                if initial_prompt:
                    await self.agent_loop.send_message(initial_prompt)

                # Start the terminal interface
                await self.terminal_interface.run()

            except KeyboardInterrupt:
                logger.info("Application interrupted by user")
                console.print("\n[yellow]Goodbye![/yellow]")
            except Exception as e:
                logger.error(f"Application error: {e}", exc_info=True)
                console.print(f"[red]Fatal error: {e}[/red]")
                sys.exit(1)
            finally:
                await self._cleanup()

    async def run_single_pass(
        self,
        prompt: Optional[str] = None,
        files: Optional[List[Path]] = None,
        full_context: bool = False,
    ) -> None:
        """
        Run the application in single-pass mode for batch operations.

        Args:
            prompt: The prompt to process
            files: List of files to include in context
            full_context: Whether to include full directory context
        """
        with performance_timer("single_pass_execution", logger):
            try:
                # Initialize components
                await self._initialize_components()

                # Create context
                if full_context:
                    context = await self._create_full_context()
                else:
                    context = await self._create_initial_context(files)

                # Create temporary session
                session_id = await self.session_manager.create_session(temporary=True)

                # Initialize agent loop
                self.agent_loop = AgentLoop(
                    config=self.config,
                    session_manager=self.session_manager,
                    command_history=self.command_history,
                )

                # Add context
                if context:
                    await self.agent_loop.add_context(context)

                # Process the prompt
                if prompt:
                    console.print(f"[cyan]Processing:[/cyan] {prompt}")

                    async for response in self.agent_loop.send_message_stream(prompt):
                        if response.type == "text":
                            console.print(response.content, end="")
                        elif response.type == "tool_call":
                            console.print(
                                f"\n[yellow]Executing:[/yellow] {response.tool_name}"
                            )
                        elif response.type == "error":
                            console.print(f"\n[red]Error:[/red] {response.content}")

                    console.print()  # Final newline
                else:
                    console.print("[red]No prompt provided for single-pass mode[/red]")
                    sys.exit(1)

            except Exception as e:
                logger.error(f"Single-pass error: {e}", exc_info=True)
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
            finally:
                await self._cleanup()

    async def _initialize_components(self) -> None:
        """Initialize application components."""
        # Setup logging based on config
        from kritrima_ai.utils.logger import setup_logging

        setup_logging(
            debug=self.config.debug,
            verbose=self.config.verbose,
            file_logging=self.config.logging.file_logging,
            console_logging=self.config.logging.console_logging,
        )

        # Initialize session manager
        await self.session_manager.initialize()

        # Initialize command history
        await self.command_history.initialize()

        # Initialize notification system
        from kritrima_ai.utils.notifications import initialize_notifications

        initialize_notifications(self.config)

        # Initialize update checker
        from kritrima_ai.utils.update_checker import (
            check_for_updates_startup,
            initialize_update_checker,
        )

        initialize_update_checker(self.config)

        # Check for updates on startup if enabled
        try:
            update_info = await check_for_updates_startup(self.config)
            if update_info and update_info.update_available:
                from kritrima_ai.utils.notifications import notify_success

                await notify_success(f"Update available: v{update_info.latest_version}")
        except Exception as e:
            logger.debug(f"Update check failed: {e}")

        # Initialize bug reporter
        from kritrima_ai.utils.bug_reporter import initialize_bug_reporter

        initialize_bug_reporter(self.config)

        # Clean up old temporary files
        from kritrima_ai.utils.file_utils import clean_temp_files

        clean_temp_files()

        logger.info("Application components initialized")

    async def _create_initial_context(
        self, files: Optional[List[Path]] = None
    ) -> Dict[str, Any]:
        """
        Create initial context for the AI assistant.

        Args:
            files: List of files to include in context

        Returns:
            Context dictionary
        """
        context = {
            "system_info": self._get_system_info(),
            "git_context": create_git_context(),
            "working_directory": str(Path.cwd()),
        }

        # Add file contents if provided
        if files:
            file_contents = {}
            for file_path in files:
                if file_path.exists() and is_text_file(file_path):
                    content = read_file_safe(file_path)
                    if content:
                        file_contents[str(file_path)] = content
                else:
                    logger.warning(f"Skipping non-text or missing file: {file_path}")

            if file_contents:
                context["files"] = file_contents

        # Add project documentation if available
        project_docs = self._discover_project_documentation()
        if project_docs:
            context["project_docs"] = project_docs

        return context

    async def _create_full_context(self) -> Dict[str, Any]:
        """
        Create full directory context for comprehensive analysis.

        Returns:
            Context dictionary with full project information
        """
        from kritrima_ai.tools.full_context import FullContextAnalyzer

        analyzer = FullContextAnalyzer(self.config)
        return await analyzer.analyze_directory(Path.cwd())

    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for context."""
        import os
        import platform

        return {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "working_directory": os.getcwd(),
            "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
        }

    def _discover_project_documentation(self) -> Optional[str]:
        """Discover and read project documentation."""
        doc_candidates = [
            "README.md",
            "README.rst",
            "README.txt",
            "docs/README.md",
            "AGENTS.md",
            "CONTRIBUTING.md",
        ]

        for doc_file in doc_candidates:
            doc_path = Path(doc_file)
            if doc_path.exists():
                content = read_file_safe(doc_path)
                if content:
                    logger.info(f"Found project documentation: {doc_file}")
                    return f"# {doc_file}\n\n{content}"

        return None

    def _show_welcome_message(self) -> None:
        """Show welcome message to the user."""
        from kritrima_ai import __version__

        # Create welcome text
        welcome_text = Text()
        welcome_text.append("Welcome to ", style="white")
        welcome_text.append("Kritrima AI CLI", style="bold cyan")
        welcome_text.append(f" v{__version__}", style="dim cyan")

        # Create info panel
        info_lines = [
            f"Provider: [green]{self.config.provider}[/green]",
            f"Model: [green]{self.config.model}[/green]",
            f"Approval Mode: [yellow]{self.config.approval_mode}[/yellow]",
        ]

        # Add git info if available
        git_status = get_git_status()
        if git_status.is_repo:
            info_lines.append(f"Git Branch: [blue]{git_status.branch}[/blue]")
            if git_status.has_changes:
                info_lines.append("[yellow]Repository has uncommitted changes[/yellow]")

        info_text = "\n".join(info_lines)

        # Show panels
        console.print(Panel(welcome_text, border_style="cyan"))
        console.print(Panel(info_text, title="Configuration", border_style="blue"))

        # Show quick help
        help_text = (
            "Quick help:\n"
            "• Type your message and press Enter\n"
            "• Use [cyan]/help[/cyan] for commands\n"
            "• Use [cyan]/model[/cyan] to change AI model\n"
            "• Use [cyan]@filename[/cyan] to include file contents\n"
            "• Press [cyan]Ctrl+C[/cyan] to exit"
        )
        console.print(Panel(help_text, title="Getting Started", border_style="green"))
        console.print()

    async def _cleanup(self) -> None:
        """Clean up application resources."""
        try:
            # Save current session
            if self.session_manager:
                await self.session_manager.save_current_session()

            # Save command history
            if self.command_history:
                await self.command_history.save()

            # Cleanup agent loop
            if self.agent_loop:
                await self.agent_loop.cleanup()

            # Cleanup terminal interface
            if self.terminal_interface:
                await self.terminal_interface.cleanup()

            # Cleanup update checker
            try:
                from kritrima_ai.utils.update_checker import get_update_checker

                update_checker = get_update_checker()
                if update_checker:
                    await update_checker.cleanup()
            except Exception as e:
                logger.debug(f"Error cleaning up update checker: {e}")

            # Shutdown logging
            from kritrima_ai.utils.logger import shutdown_logging

            await shutdown_logging()

            logger.info("Application cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get application performance statistics."""
        stats = {
            "total_requests": self._total_requests,
            "total_thinking_time": self._total_thinking_time,
            "startup_time": self._startup_time,
        }

        if self.agent_loop:
            stats.update(self.agent_loop.get_performance_stats())

        return stats

    async def export_session(self, session_id: str, output_path: Path) -> bool:
        """
        Export a session to a file.

        Args:
            session_id: Session ID to export
            output_path: Path to save the exported session

        Returns:
            True if export succeeded, False otherwise
        """
        try:
            return await self.session_manager.export_session(session_id, output_path)
        except Exception as e:
            logger.error(f"Failed to export session {session_id}: {e}")
            return False

    async def import_session(self, input_path: Path) -> Optional[str]:
        """
        Import a session from a file.

        Args:
            input_path: Path to the session file to import

        Returns:
            Session ID if import succeeded, None otherwise
        """
        try:
            return await self.session_manager.import_session(input_path)
        except Exception as e:
            logger.error(f"Failed to import session from {input_path}: {e}")
            return None
