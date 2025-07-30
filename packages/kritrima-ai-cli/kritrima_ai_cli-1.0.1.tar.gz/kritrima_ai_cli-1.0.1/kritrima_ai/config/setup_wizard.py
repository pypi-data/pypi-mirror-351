"""
Setup wizard for Kritrima AI CLI initial configuration.

This module provides an interactive setup wizard to help users configure
the Kritrima AI CLI for first-time use.
"""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from kritrima_ai.config.app_config import AppConfig, save_config
from kritrima_ai.config.providers import get_provider_info, list_providers
from kritrima_ai.utils.api_key_validator import validate_api_key
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class SetupWizard:
    """Interactive setup wizard for Kritrima AI CLI."""

    def __init__(self) -> None:
        """Initialize the setup wizard."""
        self.config = AppConfig()

    async def run(self) -> None:
        """Run the complete setup wizard."""
        console.print(
            Panel(
                "[bold cyan]Welcome to Kritrima AI CLI Setup![/bold cyan]\n\n"
                "This wizard will help you configure the CLI for first-time use.\n"
                "You can change these settings later using the config commands.",
                title="Setup Wizard",
                border_style="cyan",
            )
        )

        # Step 1: Choose provider
        await self._setup_provider()

        # Step 2: Configure API key
        await self._setup_api_key()

        # Step 3: Choose model
        await self._setup_model()

        # Step 4: Configure approval mode
        await self._setup_approval_mode()

        # Step 5: Additional settings
        await self._setup_additional_settings()

        # Step 6: Save configuration
        await self._save_configuration()

        # Step 7: Test connection
        if Confirm.ask("Would you like to test the connection now?"):
            await self._test_connection()

        console.print("\n[green]Setup completed successfully![/green]")
        console.print("You can now start using Kritrima AI CLI!")

    async def _setup_provider(self) -> None:
        """Setup AI provider selection."""
        console.print("\n[bold cyan]Step 1: Choose AI Provider[/bold cyan]")

        providers = list_providers()

        # Show available providers
        table = Table(title="Available Providers")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description")

        provider_choices = []
        for provider_id, provider_info in providers.items():
            table.add_row(
                provider_id,
                provider_info.name,
                provider_info.description or "AI Provider",
            )
            provider_choices.append(provider_id)

        console.print(table)

        # Get user choice
        while True:
            provider = Prompt.ask(
                "Choose a provider", choices=provider_choices, default="openai"
            )

            if provider in providers:
                self.config.provider = provider
                console.print(
                    f"[green]Selected provider: {providers[provider].name}[/green]"
                )
                break
            else:
                console.print(
                    "[red]Invalid provider. Please choose from the list.[/red]"
                )

    async def _setup_api_key(self) -> None:
        """Setup API key for the selected provider."""
        console.print("\n[bold cyan]Step 2: Configure API Key[/bold cyan]")

        provider_info = get_provider_info(self.config.provider)

        # Check if API key is already set
        existing_key = os.getenv(provider_info.env_key)
        if existing_key:
            console.print(
                f"[green]API key already configured for {provider_info.name}[/green]"
            )
            if not Confirm.ask("Would you like to update it?"):
                return

        console.print(f"Please set your API key for {provider_info.name}")
        console.print(f"Environment variable: [cyan]{provider_info.env_key}[/cyan]")

        if provider_info.auth_type == "none":
            console.print("[yellow]This provider doesn't require an API key[/yellow]")
            return

        # Provide instructions for setting API key
        console.print(
            Panel(
                f"To set your API key, run one of these commands:\n\n"
                f"[cyan]# Windows (PowerShell)[/cyan]\n"
                f'$env:{provider_info.env_key}="your-api-key-here"\n\n'
                f"[cyan]# Windows (Command Prompt)[/cyan]\n"
                f"set {provider_info.env_key}=your-api-key-here\n\n"
                f"[cyan]# Linux/macOS[/cyan]\n"
                f'export {provider_info.env_key}="your-api-key-here"\n\n'
                f"[cyan]# Or add to your shell profile (.bashrc, .zshrc, etc.)[/cyan]\n"
                f"echo 'export {provider_info.env_key}=\"your-api-key-here\"' >> ~/.bashrc",
                title="API Key Setup Instructions",
                border_style="yellow",
            )
        )

        # Wait for user to set the key
        while True:
            if Confirm.ask("Have you set the API key?"):
                # Check if the key is now available
                if os.getenv(provider_info.env_key):
                    console.print("[green]API key detected![/green]")
                    break
                else:
                    console.print(
                        "[red]API key not found. Please set it and try again.[/red]"
                    )
            else:
                if Confirm.ask(
                    "Would you like to continue without setting the API key?"
                ):
                    console.print(
                        "[yellow]Warning: You'll need to set the API key before using the CLI[/yellow]"
                    )
                    break

    async def _setup_model(self) -> None:
        """Setup model selection."""
        console.print("\n[bold cyan]Step 3: Choose AI Model[/bold cyan]")

        # Try to fetch available models
        try:
            from kritrima_ai.providers.model_manager import ModelManager

            model_manager = ModelManager(self.config)
            models = await model_manager.list_models()

            if models:
                console.print("Available models:")
                model_choices = []
                for i, model in enumerate(models[:10]):  # Show first 10 models
                    console.print(f"{i+1}. {model.id}")
                    model_choices.append(model.id)

                if len(models) > 10:
                    console.print(f"... and {len(models) - 10} more")

                # Get user choice
                model = Prompt.ask(
                    "Choose a model (or press Enter for default)",
                    choices=model_choices + [""],
                    default="",
                )

                if model:
                    self.config.model = model
                    console.print(f"[green]Selected model: {model}[/green]")
                else:
                    # Use provider default
                    default_models = {
                        "openai": "gpt-4",
                        "anthropic": "claude-3-sonnet-20240229",
                        "gemini": "gemini-pro",
                        "ollama": "llama2",
                    }
                    self.config.model = default_models.get(
                        self.config.provider, "gpt-3.5-turbo"
                    )
                    console.print(
                        f"[green]Using default model: {self.config.model}[/green]"
                    )
            else:
                console.print("[yellow]Could not fetch models. Using default.[/yellow]")

        except Exception as e:
            logger.warning(f"Could not fetch models: {e}")
            console.print("[yellow]Could not fetch models. Using default.[/yellow]")

    async def _setup_approval_mode(self) -> None:
        """Setup approval mode."""
        console.print("\n[bold cyan]Step 4: Configure Approval Mode[/bold cyan]")

        console.print("Approval modes:")
        console.print(
            "1. [cyan]suggest[/cyan] - Manual approval for all actions (safest)"
        )
        console.print(
            "2. [yellow]auto-edit[/yellow] - Auto-approve file edits, manual for commands"
        )
        console.print(
            "3. [red]full-auto[/red] - Auto-approve everything (use with caution)"
        )

        mode = Prompt.ask(
            "Choose approval mode",
            choices=["suggest", "auto-edit", "full-auto"],
            default="suggest",
        )

        self.config.approval_mode = mode
        console.print(f"[green]Set approval mode to: {mode}[/green]")

    async def _setup_additional_settings(self) -> None:
        """Setup additional settings."""
        console.print("\n[bold cyan]Step 5: Additional Settings[/bold cyan]")

        # Debug mode
        if Confirm.ask("Enable debug logging?", default=False):
            self.config.debug = True

        # Git warnings
        if Confirm.ask("Suppress git repository warnings?", default=False):
            self.config.suppress_git_warnings = True

        # Auto-save sessions
        if Confirm.ask("Enable automatic session saving?", default=True):
            self.config.auto_save_sessions = True

    async def _save_configuration(self) -> None:
        """Save the configuration."""
        console.print("\n[bold cyan]Step 6: Save Configuration[/bold cyan]")

        # Choose config location
        config_dir = Path.home() / ".kritrima-ai"
        config_file = config_dir / "config.json"

        if config_file.exists():
            if not Confirm.ask("Configuration file exists. Overwrite?"):
                return

        try:
            save_config(self.config, config_file)
            console.print(f"[green]Configuration saved to: {config_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving configuration: {e}[/red]")

    async def _test_connection(self) -> None:
        """Test the API connection."""
        console.print("\n[bold cyan]Testing Connection[/bold cyan]")

        try:
            is_valid = await validate_api_key(self.config.provider, self.config.model)
            if is_valid:
                console.print("[green]✓ Connection successful![/green]")
            else:
                console.print(
                    "[red]✗ Connection failed. Please check your API key.[/red]"
                )
        except Exception as e:
            console.print(f"[red]✗ Connection test failed: {e}[/red]")
