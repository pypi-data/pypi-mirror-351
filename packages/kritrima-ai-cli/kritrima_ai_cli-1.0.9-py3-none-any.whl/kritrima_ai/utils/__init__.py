"""Utility modules for Kritrima AI CLI."""

# Core utilities that don't have circular dependencies
from kritrima_ai.utils.file_utils import (
    FileUtils,
    get_file_suggestions,
    read_file_safe,
    write_file_safe,
)
from kritrima_ai.utils.format_command import (
    escape_shell_arg,
    format_command_for_display,
    format_command_list,
)
from kritrima_ai.utils.git_utils import check_in_git, get_git_status
from kritrima_ai.utils.input_utils import (
    collapse_xml_blocks,
    create_input_item,
    expand_file_tags,
    extract_file_references,
)
from kritrima_ai.utils.logger import get_logger, setup_logging
from kritrima_ai.utils.response_utils import (
    create_function_call_response,
    create_text_response,
    stream_responses,
)
from kritrima_ai.utils.slash_commands import (
    SlashCommand,
    SlashCommandProcessor,
    execute_slash_command,
    get_command_processor,
)
from kritrima_ai.utils.text_buffer import (
    CursorMovement,
    CursorPosition,
    TextBuffer,
    UndoState,
)

# Note: The following imports are moved to avoid circular dependencies:
# - notifications (depends on AppConfig)
# - update_checker (depends on AppConfig)
# - bug_reporter (depends on AppConfig)
# - workflow_automation (depends on AppConfig)
# - template_system (depends on AppConfig)
# - package_manager (depends on AppConfig)
# - single_pass (depends on AppConfig)
#
# These can be imported directly where needed instead of through this __init__.py

__all__ = [
    # Core utilities
    "get_logger",
    "setup_logging",
    "check_in_git",
    "get_git_status",
    "read_file_safe",
    "write_file_safe",
    "get_file_suggestions",
    "FileUtils",
    "create_input_item",
    "expand_file_tags",
    "collapse_xml_blocks",
    "extract_file_references",
    "stream_responses",
    "create_text_response",
    "create_function_call_response",
    # Text buffer
    "TextBuffer",
    "CursorPosition",
    "CursorMovement",
    "UndoState",
    # Slash commands
    "SlashCommandProcessor",
    "SlashCommand",
    "get_command_processor",
    "execute_slash_command",
    # Command formatting
    "format_command_for_display",
    "format_command_list",
    "escape_shell_arg",
]
