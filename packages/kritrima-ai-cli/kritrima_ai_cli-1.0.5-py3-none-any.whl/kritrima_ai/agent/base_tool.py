"""
Base tool classes and utilities for Kritrima AI CLI.

This module defines the base classes and utilities that all tools must implement,
separated from the tool registry to avoid circular imports.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""

    name: str
    description: str
    parameters: Dict[str, Any]
    category: str
    risk_level: str = "medium"
    requires_approval: bool = True
    supports_streaming: bool = False
    execution_timeout: int = 30
    examples: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []

    def to_function_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class ToolExecutionResult:
    """Result of tool execution."""

    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """
    Base class for all tools in the registry.

    All tools must inherit from this class and implement the execute method.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize the tool.

        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """
        Get tool metadata.

        Returns:
            Tool metadata including schema and description
        """

    @abstractmethod
    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute the tool with streaming output (optional).

        Args:
            **kwargs: Tool parameters

        Yields:
            Streaming output chunks
        """
        # Default implementation - run normal execute and yield result
        result = await self.execute(**kwargs)
        if result.success:
            yield str(result.result)
        else:
            yield f"Error: {result.error}"

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate tool parameters.

        Args:
            parameters: Parameters to validate

        Returns:
            True if parameters are valid
        """
        metadata = self.get_metadata()
        required_params = metadata.parameters.get("required", [])

        # Check required parameters
        for param in required_params:
            if param not in parameters:
                return False

        return True

    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get the parameter schema for this tool."""
        return self.get_metadata().parameters


def create_tool_metadata(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    category: str = "general",
    risk_level: str = "medium",
    requires_approval: bool = True,
    supports_streaming: bool = False,
    examples: Optional[List[Dict[str, Any]]] = None,
) -> ToolMetadata:
    """
    Create tool metadata with validation.

    Args:
        name: Tool name
        description: Tool description
        parameters: Parameter schema
        category: Tool category
        risk_level: Risk level (low, medium, high)
        requires_approval: Whether tool requires approval
        supports_streaming: Whether tool supports streaming
        examples: Usage examples

    Returns:
        ToolMetadata instance
    """
    if examples is None:
        examples = []

    return ToolMetadata(
        name=name,
        description=description,
        parameters=parameters,
        category=category,
        risk_level=risk_level,
        requires_approval=requires_approval,
        supports_streaming=supports_streaming,
        examples=examples,
    )


def create_parameter_schema(
    properties: Dict[str, Dict[str, Any]], required: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a parameter schema for tool functions.

    Args:
        properties: Parameter properties
        required: Required parameter names

    Returns:
        Parameter schema dictionary
    """
    if required is None:
        required = []

    return {"type": "object", "properties": properties, "required": required}
