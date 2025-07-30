"""
Workflow and Template Management Tool for Kritrima AI CLI.

This module provides comprehensive workflow and template management capabilities including:
- Workflow creation, execution, and monitoring
- Template generation and project scaffolding
- Automation and scheduling features
- Integration with existing tools and systems
"""

import json
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.agent.tool_registry import ToolRegistry
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger
from kritrima_ai.utils.template_system import (
    TemplateEngine,
    TemplateVariable,
    get_template_engine,
)
from kritrima_ai.utils.workflow_automation import (
    WorkflowEngine,
    WorkflowScheduler,
    get_workflow_engine,
)

logger = get_logger(__name__)


class WorkflowManagementTool(BaseTool):
    """
    Comprehensive workflow and template management tool.

    Provides workflow automation, template generation, and project
    scaffolding capabilities for development workflows.
    """

    def __init__(
        self, config: AppConfig, tool_registry: Optional[ToolRegistry] = None
    ) -> None:
        """
        Initialize workflow management tool.

        Args:
            config: Application configuration
            tool_registry: Tool registry for workflow execution
        """
        super().__init__(config)
        self.tool_registry = tool_registry
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.template_engine: Optional[TemplateEngine] = None
        self.scheduler: Optional[WorkflowScheduler] = None

        # Initialize engines when tool registry is available
        if tool_registry:
            self._initialize_engines()

        logger.info("Workflow management tool initialized")

    def _initialize_engines(self) -> None:
        """Initialize workflow and template engines."""
        self.workflow_engine = get_workflow_engine(self.config, self.tool_registry)
        self.template_engine = get_template_engine(self.config)
        self.scheduler = WorkflowScheduler(self.workflow_engine)

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the workflow management tool."""
        return create_tool_metadata(
            name="workflow_management",
            description="Manage workflows, templates, and automation for development tasks",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            # Workflow operations
                            "list_workflows",
                            "create_workflow",
                            "execute_workflow",
                            "cancel_workflow",
                            "workflow_status",
                            "create_workflow_from_template",
                            "save_workflow_as_template",
                            "export_workflow",
                            "import_workflow",
                            # Template operations
                            "list_templates",
                            "get_template_info",
                            "generate_project",
                            "create_template",
                            "export_template",
                            "import_template",
                            "template_preview",
                            # Scheduling operations
                            "schedule_workflow",
                            "list_scheduled",
                            "start_scheduler",
                            "stop_scheduler",
                            # Utility operations
                            "workflow_templates",
                            "validate_template_variables",
                        ],
                        "description": "The workflow/template operation to perform",
                    },
                    # Workflow parameters
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow identifier",
                    },
                    "workflow_name": {"type": "string", "description": "Workflow name"},
                    "workflow_description": {
                        "type": "string",
                        "description": "Workflow description",
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Workflow template name",
                    },
                    "template_parameters": {
                        "type": "object",
                        "description": "Template parameters for workflow creation",
                    },
                    "tasks": {
                        "type": "array",
                        "description": "List of tasks for custom workflow creation",
                    },
                    "variables": {
                        "type": "object",
                        "description": "Workflow variables",
                    },
                    "schedule": {
                        "type": "string",
                        "description": "Schedule expression for workflow automation",
                    },
                    # Template parameters
                    "template_id": {
                        "type": "string",
                        "description": "Template identifier",
                    },
                    "target_directory": {
                        "type": "string",
                        "description": "Target directory for project generation",
                    },
                    "template_variables": {
                        "type": "object",
                        "description": "Template variables for project generation",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to overwrite existing files",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter templates by category",
                    },
                    "language": {
                        "type": "string",
                        "description": "Filter templates by programming language",
                    },
                    # File operations
                    "file_path": {
                        "type": "string",
                        "description": "File path for import/export operations",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Project path for template creation",
                    },
                },
                required=["operation"],
            ),
            category="automation",
            risk_level="medium",
            requires_approval=True,
            supports_streaming=True,
            examples=[
                {
                    "description": "List available workflow templates",
                    "parameters": {"operation": "workflow_templates"},
                },
                {
                    "description": "Create a project setup workflow",
                    "parameters": {
                        "operation": "create_workflow_from_template",
                        "template_name": "project_setup",
                        "template_parameters": {
                            "project_name": "my-new-project",
                            "project_type": "python",
                        },
                    },
                },
                {
                    "description": "Generate a Python CLI project",
                    "parameters": {
                        "operation": "generate_project",
                        "template_id": "python-cli",
                        "target_directory": "./my-cli-app",
                        "template_variables": {
                            "project_name": "my-cli-app",
                            "author_name": "John Doe",
                        },
                    },
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute workflow and template management operations.

        Args:
            **kwargs: Operation parameters

        Returns:
            Tool execution result
        """
        try:
            operation = kwargs.get("operation")
            if not operation:
                return ToolExecutionResult(
                    success=False, result=None, error="Operation parameter is required"
                )

            # Ensure engines are initialized
            if not self.workflow_engine or not self.template_engine:
                return ToolExecutionResult(
                    success=False,
                    result=None,
                    error="Workflow and template engines not initialized",
                )

            # Route to appropriate method based on operation
            if operation.startswith("workflow"):
                result = await self._handle_workflow_operation(operation, kwargs)
            elif operation.startswith("template") or operation in [
                "list_templates",
                "get_template_info",
                "generate_project",
                "create_template",
                "export_template",
                "import_template",
            ]:
                result = await self._handle_template_operation(operation, kwargs)
            elif operation.startswith("schedule") or operation in [
                "list_scheduled",
                "start_scheduler",
                "stop_scheduler",
            ]:
                result = await self._handle_scheduling_operation(operation, kwargs)
            elif operation in [
                "list_workflows",
                "create_workflow",
                "execute_workflow",
                "cancel_workflow",
                "workflow_status",
                "create_workflow_from_template",
                "save_workflow_as_template",
                "export_workflow",
                "import_workflow",
            ]:
                result = await self._handle_workflow_operation(operation, kwargs)
            elif operation == "validate_template_variables":
                result = await self._handle_template_operation(operation, kwargs)
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

            return result

        except Exception as e:
            logger.error(f"Workflow management operation failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute workflow and template operations with streaming output.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming operation results
        """
        try:
            operation = kwargs.get("operation")

            if operation == "execute_workflow":
                async for output in self._stream_workflow_execution(kwargs):
                    yield output
            elif operation == "generate_project":
                async for output in self._stream_project_generation(kwargs):
                    yield output
            else:
                # Fall back to regular execution
                result = await self.execute(**kwargs)
                if result.success:
                    yield json.dumps(result.result, indent=2, default=str)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error in streaming operation: {str(e)}"

    async def _handle_workflow_operation(
        self, operation: str, kwargs: Dict[str, Any]
    ) -> ToolExecutionResult:
        """Handle workflow-related operations."""
        try:
            if operation == "list_workflows":
                workflows = self.workflow_engine.list_workflows()
                result = [
                    {
                        "id": w.id,
                        "name": w.name,
                        "description": w.description,
                        "status": w.status.value,
                        "progress": w.progress,
                        "created_at": w.created_at.isoformat(),
                        "task_count": len(w.tasks),
                    }
                    for w in workflows
                ]

            elif operation == "workflow_templates":
                templates = self.workflow_engine.list_templates()
                result = [
                    {"name": name, "info": self.workflow_engine.get_template_info(name)}
                    for name in templates
                ]

            elif operation == "create_workflow_from_template":
                template_name = kwargs.get("template_name")
                template_parameters = kwargs.get("template_parameters", {})

                if not template_name:
                    raise ValueError("template_name is required")

                workflow = self.workflow_engine.create_workflow_from_template(
                    template_name, template_parameters
                )
                result = {
                    "workflow_id": workflow.id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "task_count": len(workflow.tasks),
                }

            elif operation == "create_workflow":
                workflow_name = kwargs.get("workflow_name")
                workflow_description = kwargs.get("workflow_description", "")
                tasks = kwargs.get("tasks", [])
                variables = kwargs.get("variables", {})

                if not workflow_name:
                    raise ValueError("workflow_name is required")

                workflow = self.workflow_engine.create_custom_workflow(
                    workflow_name, workflow_description, tasks, variables
                )
                result = {
                    "workflow_id": workflow.id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "task_count": len(workflow.tasks),
                }

            elif operation == "execute_workflow":
                workflow_id = kwargs.get("workflow_id")
                if not workflow_id:
                    raise ValueError("workflow_id is required")

                workflow = await self.workflow_engine.execute_workflow(workflow_id)
                result = {
                    "workflow_id": workflow.id,
                    "status": workflow.status.value,
                    "progress": workflow.progress,
                    "error": workflow.error,
                }

            elif operation == "cancel_workflow":
                workflow_id = kwargs.get("workflow_id")
                if not workflow_id:
                    raise ValueError("workflow_id is required")

                cancelled = self.workflow_engine.cancel_workflow(workflow_id)
                result = {"cancelled": cancelled}

            elif operation == "workflow_status":
                workflow_id = kwargs.get("workflow_id")
                if not workflow_id:
                    raise ValueError("workflow_id is required")

                workflow = self.workflow_engine.get_workflow_status(workflow_id)
                if workflow:
                    result = {
                        "id": workflow.id,
                        "name": workflow.name,
                        "status": workflow.status.value,
                        "progress": workflow.progress,
                        "error": workflow.error,
                        "tasks": [
                            {
                                "id": task.id,
                                "name": task.name,
                                "status": task.status.value,
                                "error": task.error,
                            }
                            for task in workflow.tasks
                        ],
                    }
                else:
                    result = {"error": "Workflow not found"}

            elif operation == "save_workflow_as_template":
                workflow_id = kwargs.get("workflow_id")
                template_name = kwargs.get("template_name")
                template_description = kwargs.get("template_description", "")

                if not workflow_id or not template_name:
                    raise ValueError("workflow_id and template_name are required")

                self.workflow_engine.save_workflow_as_template(
                    workflow_id, template_name, template_description
                )
                result = {"message": f"Workflow saved as template '{template_name}'"}

            elif operation == "export_workflow":
                workflow_id = kwargs.get("workflow_id")
                file_path = kwargs.get("file_path")

                if not workflow_id or not file_path:
                    raise ValueError("workflow_id and file_path are required")

                self.workflow_engine.export_workflow(workflow_id, Path(file_path))
                result = {"message": f"Workflow exported to '{file_path}'"}

            elif operation == "import_workflow":
                file_path = kwargs.get("file_path")

                if not file_path:
                    raise ValueError("file_path is required")

                workflow = self.workflow_engine.import_workflow(Path(file_path))
                result = {
                    "workflow_id": workflow.id,
                    "name": workflow.name,
                    "message": f"Workflow imported from '{file_path}'",
                }

            else:
                raise ValueError(f"Unknown workflow operation: {operation}")

            return ToolExecutionResult(
                success=True, result=result, metadata={"operation": operation}
            )

        except Exception as e:
            logger.error(f"Workflow operation '{operation}' failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def _handle_template_operation(
        self, operation: str, kwargs: Dict[str, Any]
    ) -> ToolExecutionResult:
        """Handle template-related operations."""
        try:
            if operation == "list_templates":
                category = kwargs.get("category")
                language = kwargs.get("language")

                templates = self.template_engine.list_templates(category, language)
                result = [
                    {
                        "id": template.name.lower().replace(" ", "-"),
                        "name": template.name,
                        "description": template.description,
                        "category": template.category,
                        "language": template.language,
                        "framework": template.framework,
                        "tags": template.tags,
                        "variable_count": len(template.variables),
                    }
                    for template in templates
                ]

            elif operation == "get_template_info":
                template_id = kwargs.get("template_id")
                if not template_id:
                    raise ValueError("template_id is required")

                template = self.template_engine.get_template(template_id)
                if template:
                    result = {
                        "name": template.name,
                        "description": template.description,
                        "category": template.category,
                        "language": template.language,
                        "framework": template.framework,
                        "version": template.version,
                        "author": template.author,
                        "license": template.license,
                        "tags": template.tags,
                        "variables": [
                            {
                                "name": var.name,
                                "description": var.description,
                                "type": var.type,
                                "default": var.default,
                                "required": var.required,
                                "choices": var.choices,
                            }
                            for var in template.variables
                        ],
                        "file_count": len(template.files),
                        "post_generation_commands": template.post_generation_commands,
                    }
                else:
                    result = {"error": "Template not found"}

            elif operation == "generate_project":
                template_id = kwargs.get("template_id")
                target_directory = kwargs.get("target_directory")
                template_variables = kwargs.get("template_variables", {})
                overwrite = kwargs.get("overwrite", False)

                if not template_id or not target_directory:
                    raise ValueError("template_id and target_directory are required")

                success = self.template_engine.generate_project(
                    template_id, Path(target_directory), template_variables, overwrite
                )

                result = {
                    "success": success,
                    "target_directory": target_directory,
                    "template_id": template_id,
                }

            elif operation == "template_preview":
                template_id = kwargs.get("template_id")
                template_variables = kwargs.get("template_variables", {})

                if not template_id:
                    raise ValueError("template_id is required")

                preview = self.template_engine.get_template_preview(
                    template_id, template_variables
                )
                result = preview

            elif operation == "validate_template_variables":
                template_id = kwargs.get("template_id")
                template_variables = kwargs.get("template_variables", {})

                if not template_id:
                    raise ValueError("template_id is required")

                errors = self.template_engine.validate_template_variables(
                    template_id, template_variables
                )
                result = {"valid": len(errors) == 0, "errors": errors}

            elif operation == "create_template":
                project_path = kwargs.get("project_path")
                template_id = kwargs.get("template_id")
                template_name = kwargs.get("template_name")
                template_description = kwargs.get("template_description", "")
                variables = kwargs.get("variables", [])

                if not all([project_path, template_id, template_name]):
                    raise ValueError(
                        "project_path, template_id, and template_name are required"
                    )

                # Convert variable dictionaries to TemplateVariable objects
                template_variables = [
                    TemplateVariable(
                        name=var["name"],
                        description=var["description"],
                        type=var.get("type", "string"),
                        default=var.get("default"),
                        required=var.get("required", True),
                        choices=var.get("choices"),
                        validation_pattern=var.get("validation_pattern"),
                    )
                    for var in variables
                ]

                success = self.template_engine.create_template_from_project(
                    Path(project_path),
                    template_id,
                    template_name,
                    template_description,
                    template_variables,
                )

                result = {
                    "success": success,
                    "template_id": template_id,
                    "message": f"Template '{template_name}' created from project",
                }

            elif operation == "export_template":
                template_id = kwargs.get("template_id")
                file_path = kwargs.get("file_path")

                if not template_id or not file_path:
                    raise ValueError("template_id and file_path are required")

                success = self.template_engine.export_template(
                    template_id, Path(file_path)
                )
                result = {
                    "success": success,
                    "message": f"Template exported to '{file_path}'",
                }

            elif operation == "import_template":
                file_path = kwargs.get("file_path")
                template_id = kwargs.get("template_id")

                if not file_path:
                    raise ValueError("file_path is required")

                success = self.template_engine.import_template(
                    Path(file_path), template_id
                )
                result = {
                    "success": success,
                    "message": f"Template imported from '{file_path}'",
                }

            else:
                raise ValueError(f"Unknown template operation: {operation}")

            return ToolExecutionResult(
                success=True, result=result, metadata={"operation": operation}
            )

        except Exception as e:
            logger.error(f"Template operation '{operation}' failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def _handle_scheduling_operation(
        self, operation: str, kwargs: Dict[str, Any]
    ) -> ToolExecutionResult:
        """Handle scheduling-related operations."""
        try:
            if operation == "schedule_workflow":
                workflow_id = kwargs.get("workflow_id")
                schedule = kwargs.get("schedule")

                if not workflow_id or not schedule:
                    raise ValueError("workflow_id and schedule are required")

                schedule_id = self.scheduler.schedule_workflow(workflow_id, schedule)
                result = {
                    "schedule_id": schedule_id,
                    "workflow_id": workflow_id,
                    "schedule": schedule,
                    "message": "Workflow scheduled successfully",
                }

            elif operation == "list_scheduled":
                scheduled = self.scheduler.scheduled_workflows
                result = [
                    {
                        "schedule_id": schedule_id,
                        "workflow_id": info["workflow_id"],
                        "schedule": info["schedule"],
                        "enabled": info["enabled"],
                        "last_run": (
                            info["last_run"].isoformat() if info["last_run"] else None
                        ),
                        "next_run": (
                            info["next_run"].isoformat() if info["next_run"] else None
                        ),
                        "run_count": info["run_count"],
                    }
                    for schedule_id, info in scheduled.items()
                ]

            elif operation == "start_scheduler":
                await self.scheduler.start_scheduler()
                result = {"message": "Workflow scheduler started"}

            elif operation == "stop_scheduler":
                await self.scheduler.stop_scheduler()
                result = {"message": "Workflow scheduler stopped"}

            else:
                raise ValueError(f"Unknown scheduling operation: {operation}")

            return ToolExecutionResult(
                success=True, result=result, metadata={"operation": operation}
            )

        except Exception as e:
            logger.error(f"Scheduling operation '{operation}' failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def _stream_workflow_execution(
        self, kwargs: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """Stream workflow execution with progress updates."""
        workflow_id = kwargs.get("workflow_id")
        if not workflow_id:
            yield "Error: workflow_id is required"
            return

        yield f"Starting workflow execution: {workflow_id}\n"

        def progress_callback(workflow):
            return f"Progress: {workflow.progress:.1%} - {workflow.status.value}\n"

        try:
            workflow = await self.workflow_engine.execute_workflow(
                workflow_id,
                progress_callback=lambda w: None,  # We'll handle progress differently
            )

            yield f"Workflow completed with status: {workflow.status.value}\n"

            if workflow.error:
                yield f"Error: {workflow.error}\n"

            # Show task results
            for task in workflow.tasks:
                yield f"Task '{task.name}': {task.status.value}\n"
                if task.error:
                    yield f"  Error: {task.error}\n"

        except Exception as e:
            yield f"Workflow execution failed: {str(e)}\n"

    async def _stream_project_generation(
        self, kwargs: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """Stream project generation with progress updates."""
        template_id = kwargs.get("template_id")
        target_directory = kwargs.get("target_directory")
        template_variables = kwargs.get("template_variables", {})
        overwrite = kwargs.get("overwrite", False)

        if not template_id or not target_directory:
            yield "Error: template_id and target_directory are required"
            return

        yield f"Generating project from template: {template_id}\n"
        yield f"Target directory: {target_directory}\n"

        try:
            # Get template preview first
            preview = self.template_engine.get_template_preview(
                template_id, template_variables
            )

            yield f"Files to generate: {len(preview.get('files', []))}\n"
            for file_info in preview.get("files", []):
                yield f"  - {file_info['path']}\n"

            if preview.get("commands"):
                yield f"Post-generation commands: {len(preview['commands'])}\n"
                for cmd in preview["commands"]:
                    yield f"  - {cmd}\n"

            yield "\nGenerating project...\n"

            success = self.template_engine.generate_project(
                template_id, Path(target_directory), template_variables, overwrite
            )

            if success:
                yield "✅ Project generated successfully!\n"
            else:
                yield "❌ Project generation failed\n"

        except Exception as e:
            yield f"Project generation failed: {str(e)}\n"
