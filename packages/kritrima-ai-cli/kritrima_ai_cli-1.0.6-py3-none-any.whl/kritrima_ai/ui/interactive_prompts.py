"""
Interactive prompts and user input handling for Kritrima AI CLI.

This module provides interactive prompt functionality for user selections,
confirmations, and input gathering using the Rich library.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class InteractivePrompts:
    """
    Interactive prompt manager for the terminal interface.

    Provides methods for gathering user input through various interactive
    prompts including selections, confirmations, and text input.
    """

    def __init__(self, console: Console) -> None:
        """
        Initialize the interactive prompts manager.

        Args:
            console: Rich console instance
        """
        self.console = console

    async def select_from_list(
        self,
        message: str,
        choices: List[str],
        default: Optional[str] = None,
        allow_custom: bool = False,
    ) -> Optional[str]:
        """
        Present a list of choices for user selection.

        Args:
            message: Prompt message
            choices: List of available choices
            default: Default selection
            allow_custom: Whether to allow custom input

        Returns:
            Selected choice or None if cancelled
        """
        if not choices:
            self.console.print("[yellow]No choices available[/yellow]")
            return None

        try:
            # Create a table to display choices
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Choice", style="white")

            for i, choice in enumerate(choices, 1):
                marker = " (default)" if choice == default else ""
                table.add_row(str(i), f"{choice}{marker}")

            if allow_custom:
                table.add_row("0", "[dim]Enter custom value[/dim]")

            # Display the table
            self.console.print(Panel(table, title=message, border_style="cyan"))

            # Get user selection
            while True:
                try:
                    if default and default in choices:
                        default_index = choices.index(default) + 1
                        prompt_text = f"Select choice (1-{len(choices)}, default: {default_index})"
                    else:
                        prompt_text = f"Select choice (1-{len(choices)})"

                    if allow_custom:
                        prompt_text += " or 0 for custom"

                    selection = Prompt.ask(prompt_text, console=self.console)

                    if not selection and default:
                        return default

                    if selection == "0" and allow_custom:
                        custom_value = Prompt.ask(
                            "Enter custom value", console=self.console
                        )
                        return custom_value if custom_value else None

                    index = int(selection) - 1
                    if 0 <= index < len(choices):
                        return choices[index]
                    else:
                        self.console.print(
                            f"[red]Invalid selection. Please choose 1-{len(choices)}[/red]"
                        )

                except ValueError:
                    self.console.print(
                        "[red]Invalid input. Please enter a number.[/red]"
                    )
                except KeyboardInterrupt:
                    return None

        except Exception as e:
            logger.error(f"Error in select_from_list: {e}")
            return None

    async def multi_select(
        self, message: str, choices: List[str], defaults: Optional[List[str]] = None
    ) -> List[str]:
        """
        Present multiple choices for user selection.

        Args:
            message: Prompt message
            choices: List of available choices
            defaults: Default selections

        Returns:
            List of selected choices
        """
        if not choices:
            self.console.print("[yellow]No choices available[/yellow]")
            return []

        try:
            # Create a table to display choices
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Choice", style="white")
            table.add_column("Selected", style="green")

            selected = set(defaults) if defaults else set()

            for i, choice in enumerate(choices, 1):
                is_selected = choice in selected
                marker = "✓" if is_selected else " "
                table.add_row(str(i), choice, marker)

            # Display the table
            self.console.print(Panel(table, title=message, border_style="cyan"))

            self.console.print(
                "[dim]Enter numbers separated by commas (e.g., 1,3,5) or 'done' to finish[/dim]"
            )

            while True:
                try:
                    selection = Prompt.ask("Select choices", console=self.console)

                    if selection.lower() in ["done", "finish", "exit"]:
                        break

                    if selection.lower() == "all":
                        selected = set(choices)
                        break

                    if selection.lower() == "none":
                        selected = set()
                        break

                    # Parse comma-separated numbers
                    indices = [int(x.strip()) - 1 for x in selection.split(",")]

                    for index in indices:
                        if 0 <= index < len(choices):
                            choice = choices[index]
                            if choice in selected:
                                selected.remove(choice)
                            else:
                                selected.add(choice)
                        else:
                            self.console.print(
                                f"[red]Invalid selection: {index + 1}[/red]"
                            )

                    # Update display
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("#", justify="right", style="cyan")
                    table.add_column("Choice", style="white")
                    table.add_column("Selected", style="green")

                    for i, choice in enumerate(choices, 1):
                        is_selected = choice in selected
                        marker = "✓" if is_selected else " "
                        table.add_row(str(i), choice, marker)

                    self.console.print(Panel(table, title=message, border_style="cyan"))

                except ValueError:
                    self.console.print(
                        "[red]Invalid input. Please enter numbers separated by commas.[/red]"
                    )
                except KeyboardInterrupt:
                    break

            return list(selected)

        except Exception as e:
            logger.error(f"Error in multi_select: {e}")
            return []

    async def confirm(self, message: str, default: bool = True) -> bool:
        """
        Ask for user confirmation.

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            User confirmation
        """
        try:
            return Confirm.ask(message, default=default, console=self.console)
        except KeyboardInterrupt:
            return False
        except Exception as e:
            logger.error(f"Error in confirm: {e}")
            return default

    async def text_input(
        self,
        message: str,
        default: Optional[str] = None,
        password: bool = False,
        multiline: bool = False,
    ) -> Optional[str]:
        """
        Get text input from user.

        Args:
            message: Input prompt message
            default: Default value
            password: Whether to hide input
            multiline: Whether to allow multiline input

        Returns:
            User input or None if cancelled
        """
        try:
            if multiline:
                self.console.print(f"[cyan]{message}[/cyan]")
                self.console.print(
                    "[dim]Enter text (Ctrl+D or empty line to finish):[/dim]"
                )

                lines = []
                while True:
                    try:
                        line = input()
                        if not line:  # Empty line ends input
                            break
                        lines.append(line)
                    except EOFError:
                        break

                return "\n".join(lines) if lines else default

            else:
                if password:
                    import getpass

                    return getpass.getpass(f"{message}: ")
                else:
                    return Prompt.ask(message, default=default, console=self.console)

        except KeyboardInterrupt:
            return None
        except Exception as e:
            logger.error(f"Error in text_input: {e}")
            return default

    async def number_input(
        self,
        message: str,
        default: Optional[int] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> Optional[int]:
        """
        Get numeric input from user.

        Args:
            message: Input prompt message
            default: Default value
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            User input or None if cancelled
        """
        try:
            while True:
                try:
                    result = IntPrompt.ask(
                        message, default=default, console=self.console
                    )

                    if min_value is not None and result < min_value:
                        self.console.print(
                            f"[red]Value must be at least {min_value}[/red]"
                        )
                        continue

                    if max_value is not None and result > max_value:
                        self.console.print(
                            f"[red]Value must be at most {max_value}[/red]"
                        )
                        continue

                    return result

                except ValueError:
                    self.console.print("[red]Please enter a valid number[/red]")

        except KeyboardInterrupt:
            return None
        except Exception as e:
            logger.error(f"Error in number_input: {e}")
            return default

    async def file_selector(
        self,
        message: str,
        directory: Optional[Path] = None,
        file_types: Optional[List[str]] = None,
        allow_multiple: bool = False,
    ) -> Union[Optional[Path], List[Path]]:
        """
        File selection prompt.

        Args:
            message: Selection prompt message
            directory: Starting directory
            file_types: Allowed file extensions
            allow_multiple: Whether to allow multiple selections

        Returns:
            Selected file(s) or None if cancelled
        """
        try:
            if directory is None:
                directory = Path.cwd()

            if not directory.exists():
                self.console.print(f"[red]Directory does not exist: {directory}[/red]")
                return [] if allow_multiple else None

            # Get files in directory
            files = []
            for item in directory.iterdir():
                if item.is_file():
                    if file_types is None or item.suffix.lower() in file_types:
                        files.append(item)

            if not files:
                self.console.print("[yellow]No files found in directory[/yellow]")
                return [] if allow_multiple else None

            # Sort files by name
            files.sort(key=lambda x: x.name.lower())

            # Create choices
            choices = [f.name for f in files]

            if allow_multiple:
                selected_names = await self.multi_select(message, choices)
                return [directory / name for name in selected_names]
            else:
                selected_name = await self.select_from_list(message, choices)
                return directory / selected_name if selected_name else None

        except Exception as e:
            logger.error(f"Error in file_selector: {e}")
            return [] if allow_multiple else None

    async def directory_selector(
        self, message: str, starting_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Directory selection prompt.

        Args:
            message: Selection prompt message
            starting_directory: Starting directory

        Returns:
            Selected directory or None if cancelled
        """
        try:
            if starting_directory is None:
                starting_directory = Path.cwd()

            current_dir = starting_directory

            while True:
                # Get subdirectories
                subdirs = []
                for item in current_dir.iterdir():
                    if item.is_dir() and not item.name.startswith("."):
                        subdirs.append(item)

                # Sort directories
                subdirs.sort(key=lambda x: x.name.lower())

                # Create choices
                choices = ["[Select this directory]"]
                if current_dir.parent != current_dir:  # Not root
                    choices.append(".. (parent directory)")

                choices.extend([d.name + "/" for d in subdirs])

                # Display current directory
                self.console.print(f"\n[cyan]Current directory: {current_dir}[/cyan]")

                selection = await self.select_from_list(message, choices)

                if not selection:
                    return None

                if selection == "[Select this directory]":
                    return current_dir
                elif selection == ".. (parent directory)":
                    current_dir = current_dir.parent
                else:
                    # Remove trailing slash and navigate to subdirectory
                    subdir_name = selection.rstrip("/")
                    current_dir = current_dir / subdir_name

        except Exception as e:
            logger.error(f"Error in directory_selector: {e}")
            return None

    async def progress_with_confirmation(
        self, message: str, items: List[str], action_name: str = "Process"
    ) -> bool:
        """
        Show items to be processed and ask for confirmation.

        Args:
            message: Confirmation message
            items: List of items to be processed
            action_name: Name of the action to be performed

        Returns:
            User confirmation
        """
        try:
            # Display items
            table = Table(
                title=f"Items to {action_name.lower()}",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Item", style="white")

            for i, item in enumerate(items, 1):
                table.add_row(str(i), str(item))

            self.console.print(table)

            # Ask for confirmation
            return await self.confirm(f"{message} ({len(items)} items)")

        except Exception as e:
            logger.error(f"Error in progress_with_confirmation: {e}")
            return False

    def show_menu(
        self, title: str, options: Dict[str, str], show_exit: bool = True
    ) -> Optional[str]:
        """
        Display a menu and get user selection.

        Args:
            title: Menu title
            options: Dictionary of option key to description
            show_exit: Whether to show exit option

        Returns:
            Selected option key or None if exit
        """
        try:
            # Create menu table
            table = Table(title=title, show_header=True, header_style="bold magenta")
            table.add_column("Key", justify="center", style="cyan")
            table.add_column("Description", style="white")

            for key, description in options.items():
                table.add_row(key, description)

            if show_exit:
                table.add_row("q", "Exit")

            self.console.print(table)

            # Get selection
            valid_keys = list(options.keys())
            if show_exit:
                valid_keys.append("q")

            while True:
                selection = Prompt.ask("Select option", console=self.console).lower()

                if selection in valid_keys:
                    return None if selection == "q" else selection
                else:
                    self.console.print(
                        f"[red]Invalid option. Please choose from: {', '.join(valid_keys)}[/red]"
                    )

        except KeyboardInterrupt:
            return None
        except Exception as e:
            logger.error(f"Error in show_menu: {e}")
            return None
