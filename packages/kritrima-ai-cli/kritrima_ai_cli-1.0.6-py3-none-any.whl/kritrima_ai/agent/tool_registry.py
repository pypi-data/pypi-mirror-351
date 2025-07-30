"""
Tool registry system for Kritrima AI CLI.

This module implements a comprehensive tool registry that manages all available
tools for the AI agent, including registration, validation, execution, and
streaming support.
"""

import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from kritrima_ai.agent.base_tool import BaseTool, ToolMetadata
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """
    Comprehensive tool registry for managing AI agent tools.

    Handles tool registration, discovery, validation, and execution
    with support for streaming and error handling.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize the tool registry.

        Args:
            config: Application configuration
        """
        self.config = config
        self.tools: Dict[str, BaseTool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.execution_stats: Dict[str, Dict[str, Any]] = {}

        # Initialize built-in tools
        self._register_builtin_tools()

        logger.info(f"Tool registry initialized with {len(self.tools)} tools")

    def _register_builtin_tools(self):
        """Register all built-in tools."""
        try:
            # Import tools dynamically to avoid circular imports
            from kritrima_ai.tools.code_analysis import CodeAnalysisTool
            from kritrima_ai.tools.command_execution import CommandExecutionTool
            from kritrima_ai.tools.file_operations import FileOperationsTool
            from kritrima_ai.tools.full_context import FullContextAnalyzer
            from kritrima_ai.tools.project_management import ProjectManagementTool
            from kritrima_ai.tools.system_info import SystemInfoTool

            # File operations tools
            file_ops_tool = FileOperationsTool(self.config)
            self.register_tool(file_ops_tool)

            # Command execution tools
            cmd_tool = CommandExecutionTool(self.config)
            self.register_tool(cmd_tool)

            # Code analysis tools
            code_tool = CodeAnalysisTool(self.config)
            self.register_tool(code_tool)

            # System information tools
            system_tool = SystemInfoTool(self.config)
            self.register_tool(system_tool)

            # Project management tools
            project_tool = ProjectManagementTool(self.config)
            self.register_tool(project_tool)

            # Full context analysis tools
            context_tool = FullContextAnalyzer(self.config)
            self.register_tool(context_tool)

            logger.info("Built-in tools registered successfully")

        except Exception as e:
            logger.error(f"Error registering built-in tools: {e}")

    def register_tool(self, tool: BaseTool) -> bool:
        """
        Register a tool in the registry.

        Args:
            tool: Tool instance to register

        Returns:
            True if tool was registered successfully
        """
        try:
            metadata = tool.get_metadata()
            tool_name = metadata.name

            # Validate tool
            if not self._validate_tool(tool, metadata):
                logger.error(f"Tool validation failed for: {tool_name}")
                return False

            # Register tool
            self.tools[tool_name] = tool
            self.tool_metadata[tool_name] = metadata
            self.execution_stats[tool_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0,
                "last_execution": None,
            }

            logger.info(f"Registered tool: {tool_name} ({metadata.category})")
            return True

        except Exception as e:
            logger.error(f"Error registering tool: {e}")
            return False

    def _validate_tool(self, tool: BaseTool, metadata: ToolMetadata) -> bool:
        """
        Validate a tool before registration.

        Args:
            tool: Tool to validate
            metadata: Tool metadata

        Returns:
            True if tool is valid
        """
        # Check required methods
        if not hasattr(tool, "execute"):
            logger.error("Tool missing execute method")
            return False

        # Validate metadata
        if not metadata.name or not metadata.description:
            logger.error("Tool metadata missing name or description")
            return False

        # Check for duplicate names
        if metadata.name in self.tools:
            logger.error(f"Tool with name '{metadata.name}' already registered")
            return False

        # Validate parameter schema
        try:
            schema = metadata.parameters
            if not isinstance(schema, dict):
                logger.error("Tool parameter schema must be a dictionary")
                return False
        except Exception as e:
            logger.error(f"Error validating parameter schema: {e}")
            return False

        return True

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Additional execution context

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        tool = self.tools[tool_name]
        stats = self.execution_stats[tool_name]

        # Update execution statistics
        stats["total_executions"] += 1
        stats["last_execution"] = time.time()

        try:
            # Validate parameters
            if not tool.validate_parameters(parameters):
                raise ValueError(f"Invalid parameters for tool '{tool_name}'")

            # Add context to parameters if provided
            if context:
                parameters["_context"] = context

            # Execute tool
            start_time = time.time()
            result = await tool.execute(**parameters)
            execution_time = time.time() - start_time

            # Update statistics
            stats["total_execution_time"] += execution_time
            if result.success:
                stats["successful_executions"] += 1
            else:
                stats["failed_executions"] += 1

            stats["average_execution_time"] = (
                stats["total_execution_time"] / stats["total_executions"]
            )

            logger.info(f"Tool '{tool_name}' executed in {execution_time:.2f}s")

            if result.success:
                return result.result
            else:
                raise RuntimeError(f"Tool execution failed: {result.error}")

        except Exception as e:
            stats["failed_executions"] += 1
            logger.error(f"Error executing tool '{tool_name}': {e}")
            raise

    async def execute_tool_stream(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """
        Execute a tool with streaming output.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Additional execution context

        Yields:
            Streaming output chunks
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        tool = self.tools[tool_name]
        metadata = self.tool_metadata[tool_name]

        if not metadata.supports_streaming:
            # Fall back to regular execution
            result = await self.execute_tool(tool_name, parameters, context)
            yield str(result)
            return

        try:
            # Validate parameters
            if not tool.validate_parameters(parameters):
                raise ValueError(f"Invalid parameters for tool '{tool_name}'")

            # Add context to parameters if provided
            if context:
                parameters["_context"] = context

            # Stream tool execution
            async for chunk in tool.execute_stream(**parameters):
                yield chunk

        except Exception as e:
            logger.error(f"Error streaming tool '{tool_name}': {e}")
            yield f"Error: {str(e)}"

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools in OpenAI function schema format.

        Returns:
            List of tool schemas for AI function calling
        """
        schemas = []

        for tool_name, metadata in self.tool_metadata.items():
            schemas.append(metadata.to_function_schema())

        return schemas

    def get_registered_tools(self) -> List[str]:
        """
        Get list of registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """
        Get metadata for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata or None if not found
        """
        return self.tool_metadata.get(tool_name)

    def get_tools_by_category(self, category: str) -> List[str]:
        """
        Get tools by category.

        Args:
            category: Tool category

        Returns:
            List of tool names in the category
        """
        return [
            name
            for name, metadata in self.tool_metadata.items()
            if metadata.category == category
        ]

    def get_tool_categories(self) -> List[str]:
        """
        Get all available tool categories.

        Returns:
            List of unique categories
        """
        categories = {metadata.category for metadata in self.tool_metadata.values()}
        return sorted(list(categories))

    def get_execution_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics.

        Args:
            tool_name: Specific tool name, or None for all tools

        Returns:
            Execution statistics
        """
        if tool_name:
            return self.execution_stats.get(tool_name, {})

        # Aggregate statistics for all tools
        total_stats = {
            "total_tools": len(self.tools),
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0.0,
            "tools": {},
        }

        for name, stats in self.execution_stats.items():
            total_stats["total_executions"] += stats["total_executions"]
            total_stats["successful_executions"] += stats["successful_executions"]
            total_stats["failed_executions"] += stats["failed_executions"]
            total_stats["total_execution_time"] += stats["total_execution_time"]
            total_stats["tools"][name] = stats.copy()

        # Calculate success rate
        if total_stats["total_executions"] > 0:
            total_stats["success_rate"] = (
                total_stats["successful_executions"] / total_stats["total_executions"]
            )
            total_stats["average_execution_time"] = (
                total_stats["total_execution_time"] / total_stats["total_executions"]
            )
        else:
            total_stats["success_rate"] = 0.0
            total_stats["average_execution_time"] = 0.0

        return total_stats

    def search_tools(self, query: str) -> List[str]:
        """
        Search tools by name or description.

        Args:
            query: Search query

        Returns:
            List of matching tool names
        """
        query_lower = query.lower()
        matches = []

        for name, metadata in self.tool_metadata.items():
            if (
                query_lower in name.lower()
                or query_lower in metadata.description.lower()
                or query_lower in metadata.category.lower()
            ):
                matches.append(name)

        return matches

    def get_tool_examples(self, tool_name: str) -> List[Dict[str, Any]]:
        """
        Get usage examples for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of usage examples
        """
        metadata = self.tool_metadata.get(tool_name)
        if metadata:
            return metadata.examples
        return []

    def get_tool_documentation(self, tool_name: str) -> Optional[str]:
        """
        Get comprehensive documentation for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool documentation string
        """
        metadata = self.tool_metadata.get(tool_name)
        if not metadata:
            return None

        doc_parts = [
            f"# {metadata.name}",
            f"**Category:** {metadata.category}",
            f"**Risk Level:** {metadata.risk_level}",
            f"**Requires Approval:** {metadata.requires_approval}",
            f"**Supports Streaming:** {metadata.supports_streaming}",
            "",
            f"## Description",
            metadata.description,
            "",
            f"## Parameters",
        ]

        # Add parameter documentation
        if "properties" in metadata.parameters:
            for param_name, param_info in metadata.parameters["properties"].items():
                param_type = param_info.get("type", "unknown")
                param_desc = param_info.get("description", "No description")
                required = param_name in metadata.parameters.get("required", [])
                required_str = " (required)" if required else " (optional)"

                doc_parts.append(
                    f"- **{param_name}** ({param_type}){required_str}: {param_desc}"
                )

        # Add examples
        if metadata.examples:
            doc_parts.extend(["", "## Examples"])
            for i, example in enumerate(metadata.examples, 1):
                doc_parts.append(f"### Example {i}")
                if "description" in example:
                    doc_parts.append(example["description"])
                if "parameters" in example:
                    doc_parts.append("```json")
                    doc_parts.append(json.dumps(example["parameters"], indent=2))
                    doc_parts.append("```")
                if "expected_result" in example:
                    doc_parts.append(
                        f"**Expected Result:** {example['expected_result']}"
                    )
                doc_parts.append("")

        return "\n".join(doc_parts)

    def reset_statistics(self, tool_name: Optional[str] = None) -> None:
        """
        Reset execution statistics.

        Args:
            tool_name: Specific tool name, or None for all tools
        """
        if tool_name:
            if tool_name in self.execution_stats:
                self.execution_stats[tool_name] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "total_execution_time": 0.0,
                    "average_execution_time": 0.0,
                    "last_execution": None,
                }
                logger.info(f"Reset statistics for tool: {tool_name}")
        else:
            for tool_name in self.execution_stats:
                self.execution_stats[tool_name] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "total_execution_time": 0.0,
                    "average_execution_time": 0.0,
                    "last_execution": None,
                }
            logger.info("Reset statistics for all tools")

    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool from the registry.

        Args:
            tool_name: Name of the tool to unregister

        Returns:
            True if tool was unregistered successfully
        """
        if tool_name not in self.tools:
            logger.warning(f"Tool '{tool_name}' not found for unregistration")
            return False

        del self.tools[tool_name]
        del self.tool_metadata[tool_name]
        del self.execution_stats[tool_name]

        logger.info(f"Unregistered tool: {tool_name}")
        return True

    async def validate_tool_execution(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> bool:
        """
        Validate if a tool can be executed with given parameters.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            True if execution is valid
        """
        if tool_name not in self.tools:
            return False

        tool = self.tools[tool_name]
        return tool.validate_parameters(parameters)

    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the tool registry.

        Returns:
            Registry summary information
        """
        categories = {}
        for metadata in self.tool_metadata.values():
            category = metadata.category
            if category not in categories:
                categories[category] = {"count": 0, "tools": [], "risk_levels": {}}

            categories[category]["count"] += 1
            categories[category]["tools"].append(metadata.name)

            risk_level = metadata.risk_level
            if risk_level not in categories[category]["risk_levels"]:
                categories[category]["risk_levels"][risk_level] = 0
            categories[category]["risk_levels"][risk_level] += 1

        total_executions = sum(
            stats["total_executions"] for stats in self.execution_stats.values()
        )

        return {
            "total_tools": len(self.tools),
            "total_categories": len(categories),
            "categories": categories,
            "total_executions": total_executions,
            "most_used_tools": self._get_most_used_tools(5),
            "registry_health": self._calculate_registry_health(),
        }

    def _get_most_used_tools(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently used tools."""
        tool_usage = [
            {
                "name": name,
                "executions": stats["total_executions"],
                "success_rate": (
                    stats["successful_executions"] / max(stats["total_executions"], 1)
                ),
            }
            for name, stats in self.execution_stats.items()
        ]

        # Sort by executions descending
        tool_usage.sort(key=lambda x: x["executions"], reverse=True)
        return tool_usage[:limit]

    def _calculate_registry_health(self) -> Dict[str, Any]:
        """Calculate overall registry health metrics."""
        total_executions = sum(
            stats["total_executions"] for stats in self.execution_stats.values()
        )

        if total_executions == 0:
            return {"overall_health": "excellent", "success_rate": 1.0}

        total_successful = sum(
            stats["successful_executions"] for stats in self.execution_stats.values()
        )

        success_rate = total_successful / total_executions

        if success_rate >= 0.95:
            health = "excellent"
        elif success_rate >= 0.85:
            health = "good"
        elif success_rate >= 0.70:
            health = "fair"
        else:
            health = "poor"

        return {
            "overall_health": health,
            "success_rate": success_rate,
            "total_executions": total_executions,
            "recommendations": self._get_health_recommendations(success_rate),
        }

    def _get_health_recommendations(self, success_rate: float) -> List[str]:
        """Get recommendations based on registry health."""
        recommendations = []

        if success_rate < 0.85:
            recommendations.append(
                "Consider reviewing tool implementations for common failure patterns"
            )
            recommendations.append(
                "Check if tool parameters are being validated properly"
            )

        if success_rate < 0.70:
            recommendations.append("Review error handling in tool implementations")
            recommendations.append("Consider adding more robust input validation")

        # Add more specific recommendations based on tool statistics
        failed_tools = [
            name
            for name, stats in self.execution_stats.items()
            if stats["total_executions"] > 0
            and (stats["successful_executions"] / stats["total_executions"]) < 0.5
        ]

        if failed_tools:
            recommendations.append(
                f"Focus on improving these tools: {', '.join(failed_tools[:3])}"
            )

        return recommendations

    async def cleanup(self) -> None:
        """Clean up registry resources."""
        try:
            # Cleanup individual tools if they have cleanup methods
            for tool_name, tool in self.tools.items():
                if hasattr(tool, "cleanup"):
                    try:
                        await tool.cleanup()
                    except Exception as e:
                        logger.warning(f"Error cleaning up tool {tool_name}: {e}")

            logger.info("Tool registry cleanup completed")

        except Exception as e:
            logger.error(f"Error during tool registry cleanup: {e}")


# Convenience functions for tool development


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
    Convenience function to create tool metadata.

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
    return ToolMetadata(
        name=name,
        description=description,
        parameters=parameters,
        category=category,
        risk_level=risk_level,
        requires_approval=requires_approval,
        supports_streaming=supports_streaming,
        examples=examples or [],
    )


def create_parameter_schema(
    properties: Dict[str, Dict[str, Any]], required: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to create parameter schema.

    Args:
        properties: Parameter properties
        required: Required parameter names

    Returns:
        Parameter schema dictionary
    """
    return {"type": "object", "properties": properties, "required": required or []}
