#!/usr/bin/env python3
"""
Kritrima AI CLI - Main command-line interface.

This module provides the main entry point for the Kritrima AI CLI application.
It handles command-line argument parsing, configuration setup, and application
initialization.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from kritrima_ai.app import KritrimaApp
from kritrima_ai.config.app_config import AppConfig, load_config
from kritrima_ai.config.providers import get_provider_info, list_providers
from kritrima_ai.utils.api_key_validator import validate_api_key
from kritrima_ai.utils.git_utils import check_in_git
from kritrima_ai.utils.logger import get_logger, setup_logging
from kritrima_ai.version import __version__

# Initialize Typer app and Rich console
app = typer.Typer(
    name="kritrima-ai",
    help="Comprehensive AI-powered CLI assistant with autonomous agent capabilities",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()
logger = get_logger(__name__)


def main() -> None:
    """Entry point for console scripts."""
    app()


@app.callback(invoke_without_command=True)
def cli_main(
    ctx: typer.Context,
    prompt: Optional[str] = typer.Argument(
        None, help="Initial prompt for the AI assistant"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="AI model to use (e.g., gpt-4, claude-3-sonnet)"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="AI provider to use (e.g., openai, anthropic)"
    ),
    approval_mode: Optional[str] = typer.Option(
        None,
        "--approval-mode",
        "-a",
        help="Approval mode: suggest, auto-edit, full-auto",
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    full_context: bool = typer.Option(
        False, "--full-context", help="Enable full context mode for directory analysis"
    ),
    single_pass: bool = typer.Option(
        False, "--single-pass", help="Single-pass mode for batch operations"
    ),
    file: Optional[List[Path]] = typer.Option(
        None, "--file", "-f", help="Include specific files in context"
    ),
    working_dir: Optional[Path] = typer.Option(
        None, "--working-dir", "-w", help="Set working directory"
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    setup: bool = typer.Option(False, "--setup", help="Run initial setup"),
    test_connection: bool = typer.Option(
        False, "--test-connection", help="Test API connection"
    ),
    list_models: bool = typer.Option(
        False, "--list-models", help="List available models"
    ),
    reset_config: bool = typer.Option(
        False, "--reset-config", help="Reset configuration to defaults"
    ),
) -> None:
    """
    Launch the Kritrima AI CLI assistant.

    The Kritrima AI CLI is a comprehensive AI-powered assistant that provides:
    - Multi-provider AI integration (OpenAI, Anthropic, Google, Ollama, etc.)
    - Autonomous agent capabilities with tool calling
    - Advanced code assistance and file operations
    - Multi-modal input support (text and images)
    - Secure sandboxed execution
    - Rich terminal interface

    Examples:
        # Start interactive session
        kritrima-ai

        # Single command with specific model
        kritrima-ai "Explain this code" --model gpt-4 --file main.py

        # Full context analysis
        kritrima-ai --full-context "Refactor this project"

        # Test API connection
        kritrima-ai --test-connection
    """
    # If a subcommand was invoked, don't run the main logic
    if ctx.invoked_subcommand is not None:
        return

    asyncio.run(
        _async_main(
            prompt,
            model,
            provider,
            approval_mode,
            config_file,
            full_context,
            single_pass,
            file,
            working_dir,
            debug,
            verbose,
            setup,
            test_connection,
            list_models,
            reset_config,
        )
    )


async def _async_main(
    prompt: Optional[str],
    model: Optional[str],
    provider: Optional[str],
    approval_mode: Optional[str],
    config_file: Optional[Path],
    full_context: bool,
    single_pass: bool,
    file: Optional[List[Path]],
    working_dir: Optional[Path],
    debug: bool,
    verbose: bool,
    setup: bool,
    test_connection: bool,
    list_models: bool,
    reset_config: bool,
) -> None:
    """Async main function."""
    try:
        # Setup logging based on debug/verbose flags
        setup_logging(debug=debug, verbose=verbose)

        # Handle special commands first
        if setup:
            return await _run_setup()

        if reset_config:
            return await _reset_config()

        if test_connection:
            return await _test_connection(provider, model)

        if list_models:
            return await _list_models(provider)

        # Change working directory if specified
        if working_dir:
            os.chdir(working_dir)
            logger.info(f"Changed working directory to: {working_dir}")

        # Load configuration
        config = load_config(config_file)

        # Override config with command-line arguments
        if model:
            config.model = model
        if provider:
            config.provider = provider
        if approval_mode:
            config.approval_mode = approval_mode

        # Validate configuration
        await _validate_configuration(config)

        # Check git repository status
        if not check_in_git() and not config.suppress_git_warnings:
            _show_git_warning()

        # Initialize and run the application
        kritima_app = KritrimaApp(config)

        if full_context or single_pass:
            await kritima_app.run_single_pass(
                prompt=prompt,
                files=file,
                full_context=full_context,
            )
        else:
            await kritima_app.run_interactive(
                initial_prompt=prompt,
                files=file,
            )

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=debug)
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command("providers")
def show_providers() -> None:
    """Show available AI providers and their configuration."""
    console.print("\n[bold cyan]Available AI Providers[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Base URL")
    table.add_column("Env Key", style="yellow")
    table.add_column("Status", style="white")

    for provider_id, provider_info in list_providers().items():
        # Check if API key is configured
        api_key = os.getenv(provider_info.env_key)
        status = "[green]✓ Configured[/green]" if api_key else "[red]✗ No API Key[/red]"

        table.add_row(
            provider_id,
            provider_info.name,
            provider_info.base_url,
            provider_info.env_key,
            status,
        )

    console.print(table)
    console.print(
        "\n[dim]Set environment variables (e.g., OPENAI_API_KEY) to configure providers[/dim]"
    )


@app.command("config")
def show_config(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    )
) -> None:
    """Show current configuration."""
    try:
        config = load_config(config_file)

        console.print("\n[bold cyan]Current Configuration[/bold cyan]\n")

        # Main settings
        main_table = Table(title="Main Settings")
        main_table.add_column("Setting", style="cyan")
        main_table.add_column("Value", style="green")

        main_table.add_row("Model", config.model)
        main_table.add_row("Provider", config.provider)
        main_table.add_row("Approval Mode", config.approval_mode)
        main_table.add_row(
            "Config File", str(config.config_file) if config.config_file else "Default"
        )

        console.print(main_table)

        # Provider settings
        if config.custom_providers:
            console.print("\n[bold cyan]Custom Providers[/bold cyan]")
            provider_table = Table()
            provider_table.add_column("Provider", style="cyan")
            provider_table.add_column("Name", style="green")
            provider_table.add_column("Base URL")
            provider_table.add_column("Env Key", style="yellow")

            for provider_id, provider_info in config.custom_providers.items():
                provider_table.add_row(
                    provider_id,
                    provider_info["name"],
                    provider_info["base_url"],
                    provider_info["env_key"],
                )

            console.print(provider_table)

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@app.command("version")
def show_version() -> None:
    """Show version information."""
    console.print(
        Panel(
            f"[bold cyan]Kritrima AI CLI[/bold cyan]\n"
            f"Version: [green]{__version__}[/green]\n"
            f"Python: [yellow]{sys.version.split()[0]}[/yellow]\n"
            f"Platform: [blue]{sys.platform}[/blue]",
            title="Version Information",
            border_style="cyan",
        )
    )


async def _run_setup() -> None:
    """Run the initial setup wizard."""
    from kritrima_ai.config.setup_wizard import SetupWizard

    console.print("[bold cyan]Kritrima AI CLI Setup[/bold cyan]\n")

    wizard = SetupWizard()
    await wizard.run()

    console.print("\n[green]Setup completed successfully![/green]")


async def _reset_config() -> None:
    """Reset configuration to defaults."""
    from kritrima_ai.config.app_config import reset_config

    confirm = typer.confirm("This will reset all configuration to defaults. Continue?")
    if confirm:
        reset_config()
        console.print("[green]Configuration reset to defaults[/green]")
    else:
        console.print("[yellow]Configuration reset cancelled[/yellow]")


async def _test_connection(
    provider: Optional[str] = None, model: Optional[str] = None
) -> None:
    """Test API connection to the specified provider."""
    from kritrima_ai.utils.connection_tester import ConnectionTester

    console.print("[bold cyan]Testing API Connection[/bold cyan]\n")

    config = load_config()
    if provider:
        config.provider = provider
    if model:
        config.model = model

    tester = ConnectionTester(config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Testing connection to {config.provider}...", total=None
        )

        try:
            result = await tester.test_connection()
            progress.remove_task(task)

            if result.success:
                console.print(f"[green]✓ Connection successful[/green]")
                console.print(f"Provider: {config.provider}")
                console.print(f"Model: {config.model}")
                if result.available_models:
                    console.print(f"Available models: {len(result.available_models)}")
            else:
                console.print(f"[red]✗ Connection failed: {result.error}[/red]")
                sys.exit(1)

        except Exception as e:
            progress.remove_task(task)
            console.print(f"[red]✗ Connection test failed: {e}[/red]")
            sys.exit(1)


async def _list_models(provider: Optional[str] = None) -> None:
    """List available models for the specified provider."""
    from kritrima_ai.providers.model_manager import ModelManager

    config = load_config()
    if provider:
        config.provider = provider

    console.print(f"[bold cyan]Available Models for {config.provider}[/bold cyan]\n")

    model_manager = ModelManager(config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching models...", total=None)

        try:
            models = await model_manager.list_models()
            progress.remove_task(task)

            if models:
                table = Table()
                table.add_column("Model ID", style="cyan")
                table.add_column("Context Length", style="green")
                table.add_column("Capabilities", style="yellow")

                for model in models:
                    capabilities = []
                    if hasattr(model, "supports_vision") and model.supports_vision:
                        capabilities.append("Vision")
                    if (
                        hasattr(model, "supports_function_calling")
                        and model.supports_function_calling
                    ):
                        capabilities.append("Functions")

                    table.add_row(
                        model.id,
                        str(getattr(model, "context_length", "Unknown")),
                        ", ".join(capabilities) or "Text",
                    )

                console.print(table)
            else:
                console.print("[yellow]No models found[/yellow]")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"[red]Error fetching models: {e}[/red]")
            sys.exit(1)


async def _validate_configuration(config: AppConfig) -> None:
    """Validate the configuration and API keys."""
    try:
        # Validate API key
        is_valid = await validate_api_key(config.provider, config.model)
        if not is_valid:
            console.print(
                f"[red]API key validation failed for provider '{config.provider}'[/red]"
            )
            console.print(
                f"Please set the {get_provider_info(config.provider).env_key} environment variable"
            )
            sys.exit(1)

    except Exception as e:
        logger.warning(f"Could not validate API key: {e}")
        # Continue anyway - validation might fail due to network issues


def _show_git_warning() -> None:
    """Show warning when not in a git repository."""
    console.print(
        Panel(
            "[yellow]Warning: Not in a git repository[/yellow]\n\n"
            "Kritrima AI works best when run inside a git repository to:\n"
            "• Track changes and generate diffs\n"
            "• Provide better context about your project\n"
            "• Enable safe rollback of changes\n\n"
            "Consider running [cyan]git init[/cyan] to initialize a repository.",
            title="Git Repository",
            border_style="yellow",
        )
    )


if __name__ == "__main__":
    main()
