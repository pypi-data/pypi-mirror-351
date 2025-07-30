"""
Kritrima AI CLI Tools System.

This module provides comprehensive tool functionality for the AI agent including:
- File operations and manipulation
- Command execution and shell integration
- Code analysis and generation
- Project management tools
- System information gathering
- Workflow automation and template management
"""

from kritrima_ai.tools.code_analysis import CodeAnalysisTool
from kritrima_ai.tools.command_execution import CommandExecutionTool
from kritrima_ai.tools.file_operations import FileOperationsTool
from kritrima_ai.tools.full_context import FullContextAnalyzer
from kritrima_ai.tools.project_management import ProjectManagementTool
from kritrima_ai.tools.system_info import SystemInfoTool
from kritrima_ai.tools.workflow_management import WorkflowManagementTool

__all__ = [
    "FileOperationsTool",
    "CommandExecutionTool",
    "CodeAnalysisTool",
    "ProjectManagementTool",
    "SystemInfoTool",
    "FullContextAnalyzer",
    "WorkflowManagementTool",
]
