"""
Kritrima AI CLI - Main Application.

This module contains the main application class that orchestrates all the CLI functionality.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.providers.ai_client import AIClient
from kritrima_ai.agent.agent_loop import AgentLoop
from kritrima_ai.ui.terminal_interface import TerminalInterface
from kritrima_ai.ui.rich_display import RichDisplay
from kritrima_ai.tools.file_operations import FileOperations
from kritrima_ai.tools.command_execution import CommandExecution
from kritrima_ai.storage.session_manager import SessionManager
from kritrima_ai.storage.command_history import CommandHistory
from kritrima_ai.security.approval import ApprovalManager
from kritrima_ai.utils.logger import get_logger


class KritrimaApp:
    """
    Main Kritrima AI CLI application.
    
    This class orchestrates all the components of the AI assistant including
    AI providers, tools, UI, and session management.
    """
    
    def __init__(self, config: AppConfig):
        """Initialize the Kritrima AI application."""
        self.config = config
        self.console = Console()
        self.logger = get_logger(__name__)
        
        # Initialize components
        self.ai_client = AIClient(config)
        self.agent_loop = AgentLoop(config, self.ai_client)
        self.terminal_interface = TerminalInterface(config)
        self.rich_display = RichDisplay(self.console)
        self.file_ops = FileOperations(config)
        self.command_exec = CommandExecution(config)
        self.session_manager = SessionManager(config)
        self.command_history = CommandHistory(config)
        self.approval_manager = ApprovalManager(config)
        
        # Application state
        self.is_running = False
        self.current_session_id = None
        
        self.logger.info(f"Initialized Kritrima AI v{config.version}")
    
    async def run_interactive(
        self, 
        initial_prompt: Optional[str] = None,
        files: Optional[List[Path]] = None
    ) -> None:
        """
        Run the interactive session.
        
        Args:
            initial_prompt: Optional initial prompt to start with
            files: Optional list of files to include in context
        """
        try:
            self.is_running = True
            
            # Start new session
            self.current_session_id = await self.session_manager.start_session()
            
            # Welcome message
            self._show_welcome()
            
            # Add files to context if provided
            if files:
                for file_path in files:
                    if file_path.exists():
                        await self._add_file_to_context(file_path)
            
            # Process initial prompt if provided
            if initial_prompt:
                await self._process_user_input(initial_prompt)
            
            # Main interactive loop
            while self.is_running:
                try:
                    # Get user input
                    user_input = await self.terminal_interface.get_user_input()
                    
                    if not user_input.strip():
                        continue
                    
                    # Check for special commands
                    if user_input.startswith('/'):
                        await self._handle_command(user_input)
                        continue
                    
                    # Process regular input
                    await self._process_user_input(user_input)
                    
                except KeyboardInterrupt:
                    if await self._confirm_exit():
                        break
                except EOFError:
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in interactive session: {e}", exc_info=True)
            self.console.print(f"[red]Error: {e}[/red]")
        finally:
            await self._cleanup()
    
    async def run_single_pass(
        self,
        prompt: Optional[str] = None,
        files: Optional[List[Path]] = None,
        full_context: bool = False
    ) -> None:
        """
        Run a single-pass operation.
        
        Args:
            prompt: The prompt to process
            files: Files to include in context
            full_context: Whether to include full directory context
        """
        try:
            # Start session
            self.current_session_id = await self.session_manager.start_session()
            
            # Build context
            context = await self._build_context(files, full_context)
            
            if prompt:
                # Process the prompt with context
                response = await self.agent_loop.process_prompt(
                    prompt, 
                    context=context,
                    session_id=self.current_session_id
                )
                
                # Display response
                self.rich_display.display_response(response)
                
            else:
                self.console.print("[yellow]No prompt provided for single-pass mode[/yellow]")
                
        except Exception as e:
            self.logger.error(f"Error in single-pass mode: {e}", exc_info=True)
            self.console.print(f"[red]Error: {e}[/red]")
        finally:
            await self._cleanup()
    
    def _show_welcome(self) -> None:
        """Show welcome message and configuration."""
        # Welcome panel
        welcome_text = f"Welcome to Kritrima AI CLI v{self.config.version}"
        self.console.print(Panel(welcome_text, title="Kritrima AI", border_style="cyan"))
        
        # Configuration panel
        config_table = Table.grid(padding=1)
        config_table.add_column(style="cyan")
        config_table.add_column(style="white")
        config_table.add_row("Provider:", self.config.provider)
        config_table.add_row("Model:", self.config.model)
        config_table.add_row("Approval Mode:", self.config.approval_mode)
        
        self.console.print(Panel(config_table, title="Configuration", border_style="blue"))
        
        # Getting started panel
        help_text = """Quick help:
• Type your message and press Enter
• Use /help for commands
• Use /model to change AI model
• Use @filename to include file contents
• Press Ctrl+C to exit"""
        
        self.console.print(Panel(help_text, title="Getting Started", border_style="green"))
    
    async def _process_user_input(self, user_input: str) -> None:
        """Process user input through the agent loop."""
        try:
            # Add to history
            await self.command_history.add_command(user_input, self.current_session_id)
            
            # Check for file references (@filename)
            files_referenced = await self._extract_file_references(user_input)
            context = {}
            
            if files_referenced:
                context = await self._build_file_context(files_referenced)
            
            # Process through agent loop
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("Processing...", total=None)
                
                response = await self.agent_loop.process_prompt(
                    user_input,
                    context=context,
                    session_id=self.current_session_id
                )
                
                progress.remove_task(task)
            
            # Display response
            self.rich_display.display_response(response)
            
            # Handle tool calls if any
            if response.get("tool_calls"):
                await self._handle_tool_calls(response["tool_calls"])
                
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}", exc_info=True)
            self.console.print(f"[red]Error processing request: {e}[/red]")
    
    async def _handle_command(self, command: str) -> None:
        """Handle special commands."""
        parts = command[1:].split()
        cmd = parts[0].lower() if parts else ""
        
        if cmd == "help":
            await self._show_help()
        elif cmd == "exit" or cmd == "quit":
            self.is_running = False
        elif cmd == "model":
            await self._change_model(parts[1] if len(parts) > 1 else None)
        elif cmd == "provider":
            await self._change_provider(parts[1] if len(parts) > 1 else None)
        elif cmd == "clear":
            self.console.clear()
        elif cmd == "history":
            await self._show_history()
        elif cmd == "session":
            await self._show_session_info()
        elif cmd == "config":
            await self._show_config()
        elif cmd == "tools":
            await self._show_tools()
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("Use /help to see available commands")
    
    async def _show_help(self) -> None:
        """Show help information."""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        commands = [
            ("/help", "Show this help message"),
            ("/exit, /quit", "Exit the application"),
            ("/model [name]", "Change AI model"),
            ("/provider [name]", "Change AI provider"),
            ("/clear", "Clear the screen"),
            ("/history", "Show command history"),
            ("/session", "Show session information"),
            ("/config", "Show current configuration"),
            ("/tools", "Show available tools"),
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        
        self.console.print(help_table)
    
    async def _change_model(self, model_name: Optional[str]) -> None:
        """Change the AI model."""
        if model_name:
            # Validate model
            if await self.ai_client.validate_model(model_name):
                self.config.model = model_name
                self.console.print(f"[green]Model changed to: {model_name}[/green]")
            else:
                self.console.print(f"[red]Invalid model: {model_name}[/red]")
        else:
            # Show available models
            models = await self.ai_client.list_models()
            if models:
                table = Table(title="Available Models")
                table.add_column("Model", style="cyan")
                table.add_column("Description", style="white")
                
                for model in models:
                    table.add_row(model.id, getattr(model, 'description', 'AI Model'))
                
                self.console.print(table)
            else:
                self.console.print("[yellow]No models available[/yellow]")
    
    async def _change_provider(self, provider_name: Optional[str]) -> None:
        """Change the AI provider."""
        if provider_name:
            # Validate provider
            from kritrima_ai.config.providers import list_providers
            providers = list_providers()
            
            if provider_name in providers:
                self.config.provider = provider_name
                # Reinitialize AI client with new provider
                self.ai_client = AIClient(self.config)
                self.agent_loop.ai_client = self.ai_client
                self.console.print(f"[green]Provider changed to: {provider_name}[/green]")
            else:
                self.console.print(f"[red]Invalid provider: {provider_name}[/red]")
        else:
            # Show available providers
            from kritrima_ai.config.providers import list_providers
            providers = list_providers()
            
            table = Table(title="Available Providers")
            table.add_column("Provider", style="cyan")
            table.add_column("Name", style="white")
            
            for provider_id, provider_info in providers.items():
                table.add_row(provider_id, provider_info.name)
            
            self.console.print(table)
    
    async def _show_history(self) -> None:
        """Show command history."""
        history = await self.command_history.get_history(self.current_session_id)
        
        if history:
            table = Table(title="Command History")
            table.add_column("Time", style="cyan")
            table.add_column("Command", style="white")
            
            for entry in history[-10:]:  # Show last 10 commands
                table.add_row(entry.timestamp.strftime("%H:%M:%S"), entry.command[:50] + "..." if len(entry.command) > 50 else entry.command)
            
            self.console.print(table)
        else:
            self.console.print("[yellow]No command history[/yellow]")
    
    async def _show_session_info(self) -> None:
        """Show session information."""
        session_info = await self.session_manager.get_session_info(self.current_session_id)
        
        info_table = Table.grid(padding=1)
        info_table.add_column(style="cyan")
        info_table.add_column(style="white")
        info_table.add_row("Session ID:", str(self.current_session_id))
        info_table.add_row("Started:", session_info.get("start_time", "Unknown"))
        info_table.add_row("Commands:", str(session_info.get("command_count", 0)))
        
        self.console.print(Panel(info_table, title="Session Information"))
    
    async def _show_config(self) -> None:
        """Show current configuration."""
        config_table = Table.grid(padding=1)
        config_table.add_column(style="cyan")
        config_table.add_column(style="white")
        
        config_table.add_row("Provider:", self.config.provider)
        config_table.add_row("Model:", self.config.model)
        config_table.add_row("Approval Mode:", self.config.approval_mode)
        config_table.add_row("Version:", getattr(self.config, 'version', 'Unknown'))
        
        self.console.print(Panel(config_table, title="Current Configuration"))
    
    async def _show_tools(self) -> None:
        """Show available tools."""
        tools = self.agent_loop.get_available_tools()
        
        if tools:
            table = Table(title="Available Tools")
            table.add_column("Tool", style="cyan")
            table.add_column("Description", style="white")
            
            for tool in tools:
                table.add_row(tool.name, tool.description)
            
            self.console.print(table)
        else:
            self.console.print("[yellow]No tools available[/yellow]")
    
    async def _extract_file_references(self, text: str) -> List[Path]:
        """Extract file references from user input (@filename)."""
        files = []
        words = text.split()
        
        for word in words:
            if word.startswith('@'):
                file_path = Path(word[1:])
                if file_path.exists():
                    files.append(file_path)
                else:
                    self.console.print(f"[yellow]File not found: {file_path}[/yellow]")
        
        return files
    
    async def _build_file_context(self, files: List[Path]) -> Dict[str, Any]:
        """Build context from files."""
        context = {"files": {}}
        
        for file_path in files:
            try:
                content = await self.file_ops.read_file(file_path)
                context["files"][str(file_path)] = {
                    "path": str(file_path),
                    "content": content,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                }
            except Exception as e:
                self.logger.warning(f"Could not read file {file_path}: {e}")
        
        return context
    
    async def _build_context(
        self, 
        files: Optional[List[Path]] = None,
        full_context: bool = False
    ) -> Dict[str, Any]:
        """Build context for processing."""
        context = {}
        
        if files:
            context.update(await self._build_file_context(files))
        
        if full_context:
            # Add directory context
            context["directory"] = await self._get_directory_context()
        
        return context
    
    async def _get_directory_context(self) -> Dict[str, Any]:
        """Get context about the current directory."""
        cwd = Path.cwd()
        
        context = {
            "path": str(cwd),
            "files": [],
            "structure": {}
        }
        
        try:
            # Get directory structure
            for item in cwd.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    context["files"].append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "type": "file"
                    })
                elif item.is_dir() and not item.name.startswith('.'):
                    context["files"].append({
                        "name": item.name,
                        "type": "directory"
                    })
        except Exception as e:
            self.logger.warning(f"Could not read directory context: {e}")
        
        return context
    
    async def _add_file_to_context(self, file_path: Path) -> None:
        """Add a file to the current context."""
        try:
            content = await self.file_ops.read_file(file_path)
            self.console.print(f"[green]Added file to context: {file_path}[/green]")
            # File is now available for the AI to reference
        except Exception as e:
            self.console.print(f"[red]Could not add file to context: {e}[/red]")
    
    async def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> None:
        """Handle tool calls from the AI."""
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})
            
            # Get approval if required
            if not await self.approval_manager.approve_tool_call(tool_name, tool_args):
                self.console.print(f"[yellow]Tool call rejected: {tool_name}[/yellow]")
                continue
            
            try:
                # Execute tool
                result = await self.agent_loop.execute_tool(tool_name, tool_args)
                
                # Display result
                if result:
                    self.rich_display.display_tool_result(tool_name, result)
                    
            except Exception as e:
                self.logger.error(f"Error executing tool {tool_name}: {e}")
                self.console.print(f"[red]Error executing tool {tool_name}: {e}[/red]")
    
    async def _confirm_exit(self) -> bool:
        """Confirm exit with user."""
        try:
            confirm = Prompt.ask(
                "\n[yellow]Are you sure you want to exit?[/yellow]",
                choices=["y", "n"],
                default="n"
            )
            return confirm.lower() == "y"
        except KeyboardInterrupt:
            return True
    
    async def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.current_session_id:
                await self.session_manager.end_session(self.current_session_id)
            
            # Close AI client connections
            if hasattr(self.ai_client, 'close'):
                await self.ai_client.close()
                
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
