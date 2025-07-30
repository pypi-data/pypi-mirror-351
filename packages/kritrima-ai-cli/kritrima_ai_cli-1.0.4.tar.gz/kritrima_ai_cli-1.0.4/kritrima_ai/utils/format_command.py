"""
Command formatting utilities for Kritrima AI CLI.

This module provides utilities for formatting commands for display,
shell execution, and user interaction.
"""

import os
import re
import shlex
from typing import Any, Dict, List, Optional, Union

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


def format_command_for_display(command: Union[List[str], str]) -> str:
    """
    Format a command for user-friendly display.

    This function handles various command formats and presents them
    in a readable way for users, including unwrapping shell wrappers
    and proper quote handling.

    Args:
        command: Command as list of strings or single string

    Returns:
        Formatted command string for display
    """
    try:
        # Handle different input types
        if isinstance(command, str):
            # Already a string, just clean it up
            formatted = command.strip()
        elif isinstance(command, list):
            # List of command parts
            if not command:
                return ""

            # Check for bash -c wrapper and unwrap it
            if (
                len(command) >= 3
                and command[0] == "bash"
                and command[1] in ["-c", "-lc"]
            ):
                # Unwrap bash -c "actual command"
                actual_command = command[2]
                formatted = actual_command
            else:
                # Join command parts with proper quoting
                formatted = format_command_list(command)
        else:
            # Fallback for other types
            formatted = str(command)

        # Clean up the formatted command
        formatted = formatted.strip()

        # Remove unnecessary quotes if they wrap the entire command
        if (
            formatted.startswith('"')
            and formatted.endswith('"')
            and formatted.count('"') == 2
        ):
            formatted = formatted[1:-1]
        elif (
            formatted.startswith("'")
            and formatted.endswith("'")
            and formatted.count("'") == 2
        ):
            formatted = formatted[1:-1]

        return formatted

    except Exception as e:
        logger.warning(f"Error formatting command for display: {e}")
        # Fallback to string representation
        return str(command)


def format_command_list(command_parts: List[str]) -> str:
    """
    Format a list of command parts into a shell command string.

    Args:
        command_parts: List of command arguments

    Returns:
        Properly quoted shell command string
    """
    if not command_parts:
        return ""

    formatted_parts = []

    for part in command_parts:
        # Quote parts that need it
        if needs_quoting(part):
            formatted_parts.append(shlex.quote(part))
        else:
            formatted_parts.append(part)

    return " ".join(formatted_parts)


def needs_quoting(arg: str) -> bool:
    """
    Determine if a command argument needs shell quoting.

    Args:
        arg: Command argument to check

    Returns:
        True if quoting is needed
    """
    if not arg:
        return True

    # Characters that require quoting
    special_chars = set(" \t\n\r\f\v;\"'\\|&<>(){}[]$`!?*~")

    return any(char in special_chars for char in arg)


def parse_command_string(command_str: str) -> List[str]:
    """
    Parse a command string into component parts.

    Args:
        command_str: Shell command string

    Returns:
        List of command parts
    """
    try:
        return shlex.split(command_str)
    except ValueError as e:
        logger.warning(f"Error parsing command string: {e}")
        # Fallback to simple split
        return command_str.split()


def escape_shell_arg(arg: str) -> str:
    """
    Escape a shell argument for safe execution.

    Args:
        arg: Argument to escape

    Returns:
        Escaped argument
    """
    return shlex.quote(arg)


def build_shell_command(
    command: str,
    args: List[str] = None,
    env: Dict[str, str] = None,
    working_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a complete shell command with environment and working directory.

    Args:
        command: Base command to execute
        args: Additional arguments
        env: Environment variables
        working_dir: Working directory

    Returns:
        Dictionary with command execution details
    """
    cmd_parts = [command]

    if args:
        cmd_parts.extend(args)

    result = {
        "command": cmd_parts,
        "command_str": format_command_list(cmd_parts),
        "env": env or {},
        "cwd": working_dir or os.getcwd(),
    }

    return result


def format_execution_result(
    command: str,
    return_code: int,
    stdout: str = "",
    stderr: str = "",
    execution_time: float = 0.0,
) -> str:
    """
    Format command execution results for display.

    Args:
        command: Command that was executed
        return_code: Process return code
        stdout: Standard output
        stderr: Standard error
        execution_time: Execution time in seconds

    Returns:
        Formatted execution result
    """
    result_lines = []

    # Command header
    result_lines.append(f"Command: {command}")
    result_lines.append(f"Return code: {return_code}")
    result_lines.append(f"Execution time: {execution_time:.2f}s")
    result_lines.append("")

    # Output sections
    if stdout:
        result_lines.append("--- STDOUT ---")
        result_lines.append(stdout.rstrip())
        result_lines.append("")

    if stderr:
        result_lines.append("--- STDERR ---")
        result_lines.append(stderr.rstrip())
        result_lines.append("")

    return "\n".join(result_lines)


def format_command_for_approval(
    command: Union[List[str], str],
    explanation: str = "",
    working_dir: Optional[str] = None,
) -> str:
    """
    Format a command for approval display.

    Args:
        command: Command to format
        explanation: Optional explanation
        working_dir: Working directory

    Returns:
        Formatted approval message
    """
    formatted_cmd = format_command_for_display(command)

    approval_text = f"Execute command: {formatted_cmd}"

    if working_dir:
        approval_text += f"\nWorking directory: {working_dir}"

    if explanation:
        approval_text += f"\nExplanation: {explanation}"

    return approval_text


def sanitize_command_for_log(command: Union[List[str], str]) -> str:
    """
    Sanitize a command for logging by removing sensitive information.

    Args:
        command: Command to sanitize

    Returns:
        Sanitized command string
    """
    formatted = format_command_for_display(command)

    # Patterns for sensitive information
    sensitive_patterns = [
        (r"--password[=\s]+\S+", "--password=***"),
        (r"--token[=\s]+\S+", "--token=***"),
        (r"--key[=\s]+\S+", "--key=***"),
        (r"--secret[=\s]+\S+", "--secret=***"),
        (r"-p\s+\S+", "-p ***"),
        (r"--api-key[=\s]+\S+", "--api-key=***"),
        (r"Authorization:\s*Bearer\s+\S+", "Authorization: Bearer ***"),
        (r"https://[^:]+:[^@]+@", "https://***:***@"),
    ]

    for pattern, replacement in sensitive_patterns:
        formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)

    return formatted


def format_multiline_command(command: str, indent: int = 2) -> str:
    """
    Format a long command with line breaks for readability.

    Args:
        command: Command string to format
        indent: Indentation for continuation lines

    Returns:
        Multi-line formatted command
    """
    if len(command) <= 80:
        return command

    # Split on common break points
    parts = []
    current_part = ""

    tokens = command.split()

    for token in tokens:
        if len(current_part + " " + token) > 80:
            if current_part:
                parts.append(current_part)
                current_part = " " * indent + token
            else:
                parts.append(token)
        else:
            if current_part:
                current_part += " " + token
            else:
                current_part = token

    if current_part:
        parts.append(current_part)

    return " \\\n".join(parts)


def extract_command_name(command: Union[List[str], str]) -> str:
    """
    Extract the base command name from a command.

    Args:
        command: Command to extract from

    Returns:
        Base command name
    """
    if isinstance(command, list):
        if not command:
            return ""
        cmd_name = command[0]
    else:
        parts = command.strip().split()
        if not parts:
            return ""
        cmd_name = parts[0]

    # Remove path and get just the command name
    return os.path.basename(cmd_name)


def is_dangerous_command(command: Union[List[str], str]) -> bool:
    """
    Check if a command is potentially dangerous.

    Args:
        command: Command to check

    Returns:
        True if command is potentially dangerous
    """
    cmd_name = extract_command_name(command).lower()

    dangerous_commands = {
        "rm",
        "rmdir",
        "del",
        "delete",
        "format",
        "fdisk",
        "mkfs",
        "dd",
        "shred",
        "wipe",
        "sudo",
        "su",
        "doas",
        "chmod",
        "chown",
        "chgrp",
        "mount",
        "umount",
        "unmount",
        "kill",
        "killall",
        "pkill",
        "shutdown",
        "reboot",
        "halt",
        "poweroff",
        "crontab",
        "at",
        "batch",
        "passwd",
        "usermod",
        "userdel",
        "iptables",
        "ufw",
        "firewall-cmd",
        "systemctl",
        "service",
        "eval",
        "exec",
        "source",
    }

    return cmd_name in dangerous_commands


def get_command_category(command: Union[List[str], str]) -> str:
    """
    Categorize a command by its primary function.

    Args:
        command: Command to categorize

    Returns:
        Command category
    """
    cmd_name = extract_command_name(command).lower()

    categories = {
        "file_ops": [
            "ls",
            "dir",
            "cat",
            "head",
            "tail",
            "find",
            "grep",
            "cp",
            "mv",
            "rm",
            "mkdir",
            "rmdir",
        ],
        "text_ops": ["sed", "awk", "cut", "sort", "uniq", "wc", "tr", "paste"],
        "archive": ["tar", "zip", "unzip", "gzip", "gunzip", "7z"],
        "network": ["curl", "wget", "ping", "nslookup", "dig", "ssh", "scp", "rsync"],
        "process": ["ps", "top", "htop", "kill", "killall", "jobs", "bg", "fg"],
        "system": ["systemctl", "service", "mount", "df", "du", "free", "uname"],
        "development": [
            "git",
            "svn",
            "make",
            "cmake",
            "gcc",
            "python",
            "node",
            "npm",
            "pip",
        ],
        "package": [
            "apt",
            "yum",
            "dnf",
            "pacman",
            "brew",
            "choco",
            "pip",
            "npm",
            "yarn",
        ],
    }

    for category, commands in categories.items():
        if cmd_name in commands:
            return category

    return "other"


def format_command_help(
    command: str, description: str, examples: List[str] = None
) -> str:
    """
    Format help text for a command.

    Args:
        command: Command name
        description: Command description
        examples: List of usage examples

    Returns:
        Formatted help text
    """
    help_text = f"{command}\n"
    help_text += "=" * len(command) + "\n\n"
    help_text += f"{description}\n\n"

    if examples:
        help_text += "Examples:\n"
        for example in examples:
            help_text += f"  {example}\n"
        help_text += "\n"

    return help_text


def wrap_command_in_shell(command: str, shell: str = "bash") -> List[str]:
    """
    Wrap a command string in a shell for execution.

    Args:
        command: Command string to wrap
        shell: Shell to use (default: bash)

    Returns:
        Command list with shell wrapper
    """
    if shell == "bash":
        return ["bash", "-c", command]
    elif shell == "sh":
        return ["sh", "-c", command]
    elif shell == "cmd":
        return ["cmd", "/c", command]
    elif shell == "powershell":
        return ["powershell", "-Command", command]
    else:
        # Default to bash
        return ["bash", "-c", command]


def unwrap_shell_command(command: List[str]) -> str:
    """
    Unwrap a shell-wrapped command to get the original command string.

    Args:
        command: Command list potentially wrapped in shell

    Returns:
        Unwrapped command string
    """
    if len(command) >= 3:
        if command[0] == "bash" and command[1] in ["-c", "-lc"]:
            return command[2]
        elif command[0] == "sh" and command[1] == "-c":
            return command[2]
        elif command[0] == "cmd" and command[1] == "/c":
            return command[2]
        elif command[0] == "powershell" and command[1] in ["-Command", "-c"]:
            return command[2]

    # Not wrapped, return as-is
    return format_command_list(command)
