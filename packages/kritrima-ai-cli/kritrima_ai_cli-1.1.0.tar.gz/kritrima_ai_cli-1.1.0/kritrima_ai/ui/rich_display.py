"""
Rich display components for Kritrima AI CLI.

This module provides rich text formatting and display capabilities using
the Rich library for enhanced terminal output.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class RichDisplay:
    """
    Rich text display manager for the terminal interface.

    Provides methods for formatting and displaying various types of content
    with rich styling, syntax highlighting, and layout management.
    """

    def __init__(self, console: Console) -> None:
        """
        Initialize the rich display manager.

        Args:
            console: Rich console instance
        """
        self.console = console
        self._message_count = 0

    def show_user_message(
        self, message: str, timestamp: Optional[float] = None
    ) -> None:
        """
        Display a user message with formatting.

        Args:
            message: User message content
            timestamp: Message timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()

        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        # Create user message panel
        user_panel = Panel(
            Text(message, style="white"),
            title=f"[bold blue]You[/bold blue] [dim]({time_str})[/dim]",
            title_align="left",
            border_style="blue",
            padding=(0, 1),
        )

        self.console.print(user_panel)
        self._message_count += 1

    def show_ai_message(
        self,
        message: str,
        timestamp: Optional[float] = None,
        streaming: bool = False,
        final: bool = True,
    ) -> None:
        """
        Display an AI message with formatting.

        Args:
            message: AI message content
            timestamp: Message timestamp
            streaming: Whether this is a streaming update
            final: Whether this is the final message
        """
        if timestamp is None:
            timestamp = time.time()

        time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        # Format content based on type
        formatted_content = self._format_content(message)

        # Create title
        if streaming and not final:
            title = (
                f"[bold green]AI[/bold green] [dim]({time_str}) - Streaming...[/dim]"
            )
            border_style = "yellow"
        else:
            title = f"[bold green]AI[/bold green] [dim]({time_str})[/dim]"
            border_style = "green"

        # Create AI message panel
        ai_panel = Panel(
            formatted_content,
            title=title,
            title_align="left",
            border_style=border_style,
            padding=(0, 1),
        )

        self.console.print(ai_panel)
        if final:
            self._message_count += 1

    def show_system_message(self, message: str, level: str = "info") -> None:
        """
        Display a system message.

        Args:
            message: System message content
            level: Message level (info, warning, error, success)
        """
        styles = {
            "info": ("blue", "ℹ"),
            "warning": ("yellow", "⚠"),
            "error": ("red", "✗"),
            "success": ("green", "✓"),
        }

        style, icon = styles.get(level, ("white", "•"))

        system_panel = Panel(
            Text(f"{icon} {message}", style=style),
            title=f"[bold {style}]System[/bold {style}]",
            title_align="left",
            border_style=style,
            padding=(0, 1),
        )

        self.console.print(system_panel)

    def show_tool_execution(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[str] = None,
        status: str = "executing",
        execution_time: Optional[float] = None,
    ) -> None:
        """
        Display tool execution information.

        Args:
            tool_name: Name of the tool being executed
            arguments: Tool arguments
            result: Tool execution result
            status: Execution status (executing, completed, failed)
            execution_time: Time taken to execute
        """
        # Create tool execution table
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Tool", tool_name)

        # Format arguments
        if arguments:
            args_str = ", ".join(f"{k}={v}" for k, v in arguments.items())
            table.add_row(
                "Arguments", args_str[:100] + "..." if len(args_str) > 100 else args_str
            )

        # Status with icon
        status_icons = {
            "executing": ("⏳", "yellow"),
            "completed": ("✓", "green"),
            "failed": ("✗", "red"),
        }
        icon, color = status_icons.get(status, ("•", "white"))
        table.add_row("Status", f"[{color}]{icon} {status.title()}[/{color}]")

        if execution_time is not None:
            table.add_row("Duration", f"{execution_time:.2f}s")

        if result:
            # Truncate long results
            result_display = result[:200] + "..." if len(result) > 200 else result
            table.add_row("Result", result_display)

        # Create panel
        border_color = status_icons.get(status, ("•", "white"))[1]
        tool_panel = Panel(
            table,
            title=f"[bold {border_color}]Tool Execution[/bold {border_color}]",
            title_align="left",
            border_style=border_color,
            padding=(0, 1),
        )

        self.console.print(tool_panel)

    def show_error(self, error: str, details: Optional[str] = None) -> None:
        """
        Display an error message.

        Args:
            error: Error message
            details: Additional error details
        """
        error_content = Text(f"✗ {error}", style="red")

        if details:
            error_content.append("\n\n")
            error_content.append(Text(details, style="dim red"))

        error_panel = Panel(
            error_content,
            title="[bold red]Error[/bold red]",
            title_align="left",
            border_style="red",
            padding=(0, 1),
        )

        self.console.print(error_panel)

    def show_thinking_indicator(self, message: str = "Thinking...") -> Progress:
        """
        Show a thinking indicator with spinner.

        Args:
            message: Thinking message

        Returns:
            Progress instance for updating
        """
        progress = Progress(
            SpinnerColumn(spinner_style="cyan"),
            TextColumn(f"[cyan]{message}[/cyan]"),
            console=self.console,
            transient=True,
        )

        task = progress.add_task("thinking", total=None)
        return progress

    def show_progress(
        self, description: str, total: Optional[int] = None, show_time: bool = True
    ) -> Progress:
        """
        Show a progress bar.

        Args:
            description: Progress description
            total: Total number of items (None for indeterminate)
            show_time: Whether to show elapsed time

        Returns:
            Progress instance for updating
        """
        columns = [
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ]

        if show_time:
            columns.append(TimeElapsedColumn())

        progress = Progress(*columns, console=self.console)
        task = progress.add_task(description, total=total)
        return progress

    def show_table(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        styles: Optional[List[str]] = None,
    ) -> None:
        """
        Display a formatted table.

        Args:
            title: Table title
            headers: Column headers
            rows: Table rows
            styles: Column styles (optional)
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")

        # Add columns
        for i, header in enumerate(headers):
            style = styles[i] if styles and i < len(styles) else "white"
            table.add_column(header, style=style)

        # Add rows
        for row in rows:
            table.add_row(*row)

        self.console.print(table)

    def show_code_block(
        self,
        code: str,
        language: str = "text",
        title: Optional[str] = None,
        line_numbers: bool = True,
    ) -> None:
        """
        Display a code block with syntax highlighting.

        Args:
            code: Code content
            language: Programming language for highlighting
            title: Optional title for the code block
            line_numbers: Whether to show line numbers
        """
        syntax = Syntax(
            code, language, theme="monokai", line_numbers=line_numbers, word_wrap=True
        )

        if title:
            code_panel = Panel(
                syntax,
                title=f"[bold yellow]{title}[/bold yellow]",
                title_align="left",
                border_style="yellow",
                padding=(0, 1),
            )
            self.console.print(code_panel)
        else:
            self.console.print(syntax)

    def show_file_diff(self, diff_content: str, filename: Optional[str] = None) -> None:
        """
        Display a file diff with appropriate formatting.

        Args:
            diff_content: Diff content
            filename: Optional filename
        """
        # Format diff with colors
        lines = diff_content.split("\n")
        formatted_lines = []

        for line in lines:
            if line.startswith("+"):
                formatted_lines.append(Text(line, style="green"))
            elif line.startswith("-"):
                formatted_lines.append(Text(line, style="red"))
            elif line.startswith("@@"):
                formatted_lines.append(Text(line, style="cyan"))
            else:
                formatted_lines.append(Text(line, style="white"))

        diff_content = Text()
        for line in formatted_lines:
            diff_content.append(line)
            diff_content.append("\n")

        title = (
            f"[bold yellow]Diff: {filename}[/bold yellow]"
            if filename
            else "[bold yellow]Diff[/bold yellow]"
        )

        diff_panel = Panel(
            diff_content,
            title=title,
            title_align="left",
            border_style="yellow",
            padding=(0, 1),
        )

        self.console.print(diff_panel)

    def show_separator(self, text: Optional[str] = None) -> None:
        """
        Show a separator line.

        Args:
            text: Optional text for the separator
        """
        if text:
            self.console.print(Rule(text, style="dim"))
        else:
            self.console.print(Rule(style="dim"))

    def clear_screen(self) -> None:
        """Clear the console screen."""
        self.console.clear()

    def _format_content(self, content: str) -> Union[Text, Syntax, Markdown]:
        """
        Format content based on its type.

        Args:
            content: Content to format

        Returns:
            Formatted content object
        """
        # Check if content looks like code
        if self._looks_like_code(content):
            language = self._detect_language(content)
            return Syntax(content, language, theme="monokai", word_wrap=True)

        # Check if content looks like markdown
        if self._looks_like_markdown(content):
            try:
                return Markdown(content)
            except Exception:
                pass

        # Default to plain text
        return Text(content, style="white")

    def _looks_like_code(self, content: str) -> bool:
        """Check if content appears to be code."""
        code_indicators = [
            "def ",
            "class ",
            "import ",
            "from ",
            "function ",
            "const ",
            "let ",
            "var ",
            "#!/",
            "<?php",
            "<script",
            "<html",
            "{",
            "}",
            "()",
            "=>",
            "::",
            "if __name__",
            "async def",
            "await ",
        ]
        return any(indicator in content for indicator in code_indicators)

    def _looks_like_markdown(self, content: str) -> bool:
        """Check if content appears to be markdown."""
        markdown_indicators = [
            "# ",
            "## ",
            "### ",
            "**",
            "__",
            "*",
            "_",
            "```",
            "`",
            "[",
            "](",
            "- ",
            "* ",
            "1. ",
        ]
        return any(indicator in content for indicator in markdown_indicators)

    def _detect_language(self, content: str) -> str:
        """Detect programming language from content."""
        if "def " in content and ("import " in content or "from " in content):
            return "python"
        elif "function " in content or "const " in content or "let " in content:
            return "javascript"
        elif "<html" in content or "<script" in content:
            return "html"
        elif "<?php" in content:
            return "php"
        elif "class " in content and "{" in content and "}" in content:
            return "java"
        elif "#include" in content or "int main(" in content:
            return "c"
        elif "fn " in content and "let " in content:
            return "rust"
        elif "package " in content and "func " in content:
            return "go"
        else:
            return "text"

    def display_response(self, response: Dict[str, Any]) -> None:
        """
        Display an AI response.
        
        Args:
            response: Response dictionary from the AI
        """
        content = response.get("content", str(response))
        self.show_ai_message(content)
    
    def display_tool_result(self, tool_name: str, result: Any) -> None:
        """
        Display the result of a tool execution.
        
        Args:
            tool_name: Name of the tool that was executed
            result: Result from the tool execution
        """
        self.show_tool_execution(
            tool_name=tool_name,
            arguments={},
            result=str(result),
            status="completed"
        )

    def get_message_count(self) -> int:
        """Get the current message count."""
        return self._message_count

    def reset_message_count(self) -> None:
        """Reset the message count."""
        self._message_count = 0
