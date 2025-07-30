"""
Workflow automation system for Kritrima AI CLI.

This module provides comprehensive workflow automation capabilities including:
- Workflow definition and execution
- Task scheduling and dependency management
- Template-based workflow creation
- Progress tracking and error handling
- Workflow sharing and reuse
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from kritrima_ai.agent.tool_registry import ToolRegistry
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskStatus(Enum):
    """Individual task status."""

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTask:
    """Individual task within a workflow."""

    id: str
    name: str
    tool_name: str
    parameters: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[int] = None
    status: TaskStatus = TaskStatus.WAITING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "depends_on": self.depends_on,
            "condition": self.condition,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class Workflow:
    """Workflow definition and execution state."""

    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    variables: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "variables": self.variables,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "error": self.error,
            "progress": self.progress,
            "metadata": self.metadata,
        }


class WorkflowTemplate:
    """Template for creating workflows."""

    def __init__(self, name: str, description: str, template_data: Dict[str, Any]):
        """
        Initialize workflow template.

        Args:
            name: Template name
            description: Template description
            template_data: Template configuration
        """
        self.name = name
        self.description = description
        self.template_data = template_data
        self.parameters = template_data.get("parameters", {})
        self.task_templates = template_data.get("tasks", [])

    def create_workflow(self, parameters: Dict[str, Any]) -> Workflow:
        """
        Create a workflow instance from this template.

        Args:
            parameters: Template parameters

        Returns:
            Workflow instance
        """
        # Merge default parameters with provided ones
        merged_params = {**self.parameters, **parameters}

        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            name=self._substitute_variables(self.name, merged_params),
            description=self._substitute_variables(self.description, merged_params),
            tasks=[],
            variables=merged_params,
        )

        # Create tasks from templates
        for task_template in self.task_templates:
            task = WorkflowTask(
                id=str(uuid.uuid4()),
                name=self._substitute_variables(task_template["name"], merged_params),
                tool_name=task_template["tool_name"],
                parameters=self._substitute_variables(
                    task_template["parameters"], merged_params
                ),
                depends_on=task_template.get("depends_on", []),
                condition=task_template.get("condition"),
                max_retries=task_template.get("max_retries", 3),
                timeout=task_template.get("timeout"),
            )
            workflow.tasks.append(task)

        return workflow

    def _substitute_variables(self, value: Any, variables: Dict[str, Any]) -> Any:
        """Substitute template variables in values."""
        if isinstance(value, str):
            # Replace ${variable} patterns
            for var_name, var_value in variables.items():
                value = value.replace(f"${{{var_name}}}", str(var_value))
            return value
        elif isinstance(value, dict):
            return {
                k: self._substitute_variables(v, variables) for k, v in value.items()
            }
        elif isinstance(value, list):
            return [self._substitute_variables(item, variables) for item in value]
        else:
            return value


class WorkflowEngine:
    """
    Workflow execution engine.

    Manages workflow execution, task scheduling, dependency resolution,
    and progress tracking.
    """

    def __init__(self, config: AppConfig, tool_registry: ToolRegistry):
        """
        Initialize workflow engine.

        Args:
            config: Application configuration
            tool_registry: Tool registry for task execution
        """
        self.config = config
        self.tool_registry = tool_registry
        self.workflows: Dict[str, Workflow] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}

        # Load built-in templates
        self._load_builtin_templates()

        logger.info("Workflow engine initialized")

    def _load_builtin_templates(self) -> None:
        """Load built-in workflow templates."""
        builtin_templates = {
            "project_setup": {
                "name": "Project Setup - ${project_name}",
                "description": "Set up a new ${project_type} project",
                "parameters": {
                    "project_name": "my-project",
                    "project_type": "python",
                    "git_init": True,
                    "create_readme": True,
                },
                "tasks": [
                    {
                        "name": "Create project directory",
                        "tool_name": "file_operations",
                        "parameters": {
                            "operation": "create_directory",
                            "path": "${project_name}",
                        },
                    },
                    {
                        "name": "Initialize Git repository",
                        "tool_name": "command_execution",
                        "parameters": {
                            "operation": "execute",
                            "command": "git init",
                            "working_directory": "${project_name}",
                        },
                        "condition": "${git_init}",
                    },
                    {
                        "name": "Create README.md",
                        "tool_name": "file_operations",
                        "parameters": {
                            "operation": "write_file",
                            "path": "${project_name}/README.md",
                            "content": "# ${project_name}\n\nA new ${project_type} project.\n",
                        },
                        "condition": "${create_readme}",
                    },
                ],
            },
            "code_quality_check": {
                "name": "Code Quality Check - ${target_path}",
                "description": "Run comprehensive code quality checks",
                "parameters": {
                    "target_path": ".",
                    "run_tests": True,
                    "run_linting": True,
                    "run_security_scan": True,
                },
                "tasks": [
                    {
                        "name": "Run linting",
                        "tool_name": "code_analysis",
                        "parameters": {
                            "operation": "lint_code",
                            "path": "${target_path}",
                        },
                        "condition": "${run_linting}",
                    },
                    {
                        "name": "Run tests",
                        "tool_name": "command_execution",
                        "parameters": {
                            "operation": "execute",
                            "command": "python -m pytest",
                            "working_directory": "${target_path}",
                        },
                        "condition": "${run_tests}",
                        "depends_on": ["Run linting"],
                    },
                    {
                        "name": "Security scan",
                        "tool_name": "code_analysis",
                        "parameters": {
                            "operation": "security_scan",
                            "path": "${target_path}",
                        },
                        "condition": "${run_security_scan}",
                        "depends_on": ["Run tests"],
                    },
                ],
            },
            "deployment_pipeline": {
                "name": "Deployment Pipeline - ${environment}",
                "description": "Deploy application to ${environment}",
                "parameters": {
                    "environment": "staging",
                    "run_tests": True,
                    "backup_before_deploy": True,
                    "notify_team": True,
                },
                "tasks": [
                    {
                        "name": "Run pre-deployment tests",
                        "tool_name": "command_execution",
                        "parameters": {"operation": "execute", "command": "npm test"},
                        "condition": "${run_tests}",
                    },
                    {
                        "name": "Create backup",
                        "tool_name": "command_execution",
                        "parameters": {
                            "operation": "execute",
                            "command": "backup-script.sh ${environment}",
                        },
                        "condition": "${backup_before_deploy}",
                        "depends_on": ["Run pre-deployment tests"],
                    },
                    {
                        "name": "Deploy application",
                        "tool_name": "command_execution",
                        "parameters": {
                            "operation": "execute",
                            "command": "deploy.sh ${environment}",
                        },
                        "depends_on": ["Create backup"],
                    },
                    {
                        "name": "Verify deployment",
                        "tool_name": "command_execution",
                        "parameters": {
                            "operation": "execute",
                            "command": "health-check.sh ${environment}",
                        },
                        "depends_on": ["Deploy application"],
                    },
                ],
            },
        }

        for template_name, template_data in builtin_templates.items():
            template = WorkflowTemplate(
                name=template_data["name"],
                description=template_data["description"],
                template_data=template_data,
            )
            self.templates[template_name] = template

    def create_workflow_from_template(
        self, template_name: str, parameters: Dict[str, Any]
    ) -> Workflow:
        """
        Create a workflow from a template.

        Args:
            template_name: Name of the template
            parameters: Template parameters

        Returns:
            Created workflow

        Raises:
            ValueError: If template not found
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]
        workflow = template.create_workflow(parameters)
        self.workflows[workflow.id] = workflow

        logger.info(
            f"Created workflow '{workflow.name}' from template '{template_name}'"
        )
        return workflow

    def create_custom_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]],
        variables: Optional[Dict[str, Any]] = None,
    ) -> Workflow:
        """
        Create a custom workflow.

        Args:
            name: Workflow name
            description: Workflow description
            tasks: List of task definitions
            variables: Workflow variables

        Returns:
            Created workflow
        """
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            tasks=[],
            variables=variables or {},
        )

        # Create tasks
        for task_def in tasks:
            task = WorkflowTask(
                id=str(uuid.uuid4()),
                name=task_def["name"],
                tool_name=task_def["tool_name"],
                parameters=task_def["parameters"],
                depends_on=task_def.get("depends_on", []),
                condition=task_def.get("condition"),
                max_retries=task_def.get("max_retries", 3),
                timeout=task_def.get("timeout"),
            )
            workflow.tasks.append(task)

        self.workflows[workflow.id] = workflow

        logger.info(f"Created custom workflow '{workflow.name}'")
        return workflow

    async def execute_workflow(
        self,
        workflow_id: str,
        progress_callback: Optional[Callable[[Workflow], None]] = None,
    ) -> Workflow:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow ID
            progress_callback: Optional progress callback

        Returns:
            Completed workflow

        Raises:
            ValueError: If workflow not found
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        workflow = self.workflows[workflow_id]

        if workflow.status == WorkflowStatus.RUNNING:
            raise ValueError(f"Workflow '{workflow_id}' is already running")

        # Start execution
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()

        try:
            # Create execution task
            execution_task = asyncio.create_task(
                self._execute_workflow_tasks(workflow, progress_callback)
            )
            self.running_workflows[workflow_id] = execution_task

            # Wait for completion
            await execution_task

            # Mark as completed
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.progress = 1.0

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.now()
            logger.error(f"Workflow '{workflow.name}' failed: {e}")

        finally:
            # Clean up
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]

        return workflow

    async def _execute_workflow_tasks(
        self,
        workflow: Workflow,
        progress_callback: Optional[Callable[[Workflow], None]],
    ) -> None:
        """Execute workflow tasks with dependency resolution."""
        completed_tasks = set()
        failed_tasks = set()

        while len(completed_tasks) + len(failed_tasks) < len(workflow.tasks):
            # Find tasks ready to execute
            ready_tasks = []
            for task in workflow.tasks:
                if task.status == TaskStatus.WAITING and all(
                    dep_id in completed_tasks for dep_id in task.depends_on
                ):

                    # Check condition if specified
                    if task.condition and not self._evaluate_condition(
                        task.condition, workflow.variables
                    ):
                        task.status = TaskStatus.SKIPPED
                        completed_tasks.add(task.id)
                        continue

                    ready_tasks.append(task)

            if not ready_tasks:
                # No more tasks can be executed
                break

            # Execute ready tasks concurrently
            task_futures = []
            for task in ready_tasks:
                task.status = TaskStatus.RUNNING
                task.start_time = datetime.now()
                future = asyncio.create_task(self._execute_task(task, workflow))
                task_futures.append((task, future))

            # Wait for tasks to complete
            for task, future in task_futures:
                try:
                    await future
                    task.status = TaskStatus.COMPLETED
                    completed_tasks.add(task.id)
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    failed_tasks.add(task.id)

                    # Retry if possible
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.WAITING
                        failed_tasks.remove(task.id)
                        logger.warning(
                            f"Retrying task '{task.name}' (attempt {task.retry_count})"
                        )

                task.end_time = datetime.now()

            # Update progress
            total_tasks = len(workflow.tasks)
            completed_count = len(completed_tasks)
            workflow.progress = completed_count / total_tasks

            # Call progress callback
            if progress_callback:
                progress_callback(workflow)

        # Check if any critical tasks failed
        if failed_tasks:
            failed_task_names = [
                task.name for task in workflow.tasks if task.id in failed_tasks
            ]
            raise Exception(f"Tasks failed: {', '.join(failed_task_names)}")

    async def _execute_task(self, task: WorkflowTask, workflow: Workflow) -> None:
        """Execute a single task."""
        try:
            # Get tool
            tool = self.tool_registry.get_tool(task.tool_name)
            if not tool:
                raise ValueError(f"Tool '{task.tool_name}' not found")

            # Execute with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    tool.execute(**task.parameters), timeout=task.timeout
                )
            else:
                result = await tool.execute(**task.parameters)

            if not result.success:
                raise Exception(result.error or "Task execution failed")

            task.result = result.result

        except asyncio.TimeoutError:
            raise Exception(
                f"Task '{task.name}' timed out after {task.timeout} seconds"
            )
        except Exception as e:
            logger.error(f"Task '{task.name}' failed: {e}")
            raise

    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        try:
            # Simple variable substitution and evaluation
            for var_name, var_value in variables.items():
                condition = condition.replace(f"${{{var_name}}}", str(var_value))

            # Basic boolean evaluation
            if condition.lower() in ("true", "1", "yes"):
                return True
            elif condition.lower() in ("false", "0", "no"):
                return False
            else:
                # Try to evaluate as Python expression (safely)
                return bool(eval(condition, {"__builtins__": {}}, variables))

        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False

    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if cancelled, False if not running
        """
        if workflow_id not in self.running_workflows:
            return False

        # Cancel the execution task
        task = self.running_workflows[workflow_id]
        task.cancel()

        # Update workflow status
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()

        del self.running_workflows[workflow_id]

        logger.info(f"Cancelled workflow '{workflow_id}'")
        return True

    def get_workflow_status(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow status."""
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""
        return list(self.workflows.values())

    def list_templates(self) -> List[str]:
        """List available workflow templates."""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template information."""
        if template_name not in self.templates:
            return None

        template = self.templates[template_name]
        return {
            "name": template.name,
            "description": template.description,
            "parameters": template.parameters,
            "tasks": len(template.task_templates),
        }

    def save_workflow_as_template(
        self, workflow_id: str, template_name: str, template_description: str
    ) -> None:
        """Save a workflow as a reusable template."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        workflow = self.workflows[workflow_id]

        # Convert workflow to template format
        template_data = {
            "name": workflow.name,
            "description": template_description,
            "parameters": workflow.variables,
            "tasks": [
                {
                    "name": task.name,
                    "tool_name": task.tool_name,
                    "parameters": task.parameters,
                    "depends_on": task.depends_on,
                    "condition": task.condition,
                    "max_retries": task.max_retries,
                    "timeout": task.timeout,
                }
                for task in workflow.tasks
            ],
        }

        template = WorkflowTemplate(
            name=workflow.name,
            description=template_description,
            template_data=template_data,
        )

        self.templates[template_name] = template

        logger.info(f"Saved workflow '{workflow.name}' as template '{template_name}'")

    def export_workflow(self, workflow_id: str, file_path: Path) -> None:
        """Export workflow to file."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        workflow = self.workflows[workflow_id]

        with open(file_path, "w") as f:
            json.dump(workflow.to_dict(), f, indent=2)

        logger.info(f"Exported workflow '{workflow.name}' to '{file_path}'")

    def import_workflow(self, file_path: Path) -> Workflow:
        """Import workflow from file."""
        with open(file_path, "r") as f:
            workflow_data = json.load(f)

        # Reconstruct workflow
        workflow = Workflow(
            id=workflow_data["id"],
            name=workflow_data["name"],
            description=workflow_data["description"],
            tasks=[],
            variables=workflow_data["variables"],
            status=WorkflowStatus(workflow_data["status"]),
            created_at=datetime.fromisoformat(workflow_data["created_at"]),
            metadata=workflow_data.get("metadata", {}),
        )

        # Reconstruct tasks
        for task_data in workflow_data["tasks"]:
            task = WorkflowTask(
                id=task_data["id"],
                name=task_data["name"],
                tool_name=task_data["tool_name"],
                parameters=task_data["parameters"],
                depends_on=task_data["depends_on"],
                condition=task_data["condition"],
                retry_count=task_data["retry_count"],
                max_retries=task_data["max_retries"],
                timeout=task_data["timeout"],
                status=TaskStatus(task_data["status"]),
                result=task_data["result"],
                error=task_data["error"],
            )

            if task_data["start_time"]:
                task.start_time = datetime.fromisoformat(task_data["start_time"])
            if task_data["end_time"]:
                task.end_time = datetime.fromisoformat(task_data["end_time"])

            workflow.tasks.append(task)

        self.workflows[workflow.id] = workflow

        logger.info(f"Imported workflow '{workflow.name}' from '{file_path}'")
        return workflow


class WorkflowScheduler:
    """
    Workflow scheduling system for automated execution.

    Supports cron-like scheduling and event-based triggers.
    """

    def __init__(self, workflow_engine: WorkflowEngine):
        """
        Initialize workflow scheduler.

        Args:
            workflow_engine: Workflow engine instance
        """
        self.workflow_engine = workflow_engine
        self.scheduled_workflows: Dict[str, Dict[str, Any]] = {}
        self.scheduler_task: Optional[asyncio.Task] = None
        self.running = False

        logger.info("Workflow scheduler initialized")

    def schedule_workflow(
        self, workflow_id: str, schedule: str, enabled: bool = True
    ) -> str:
        """
        Schedule a workflow for automatic execution.

        Args:
            workflow_id: Workflow to schedule
            schedule: Cron-like schedule expression
            enabled: Whether schedule is enabled

        Returns:
            Schedule ID
        """
        schedule_id = str(uuid.uuid4())

        self.scheduled_workflows[schedule_id] = {
            "workflow_id": workflow_id,
            "schedule": schedule,
            "enabled": enabled,
            "last_run": None,
            "next_run": self._calculate_next_run(schedule),
            "run_count": 0,
        }

        logger.info(f"Scheduled workflow '{workflow_id}' with schedule '{schedule}'")
        return schedule_id

    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from schedule expression."""
        # Simple implementation - in production, use a proper cron parser
        now = datetime.now()

        if schedule.startswith("@every"):
            # @every 5m, @every 1h, etc.
            interval_str = schedule.split()[1]
            if interval_str.endswith("m"):
                minutes = int(interval_str[:-1])
                return now + timedelta(minutes=minutes)
            elif interval_str.endswith("h"):
                hours = int(interval_str[:-1])
                return now + timedelta(hours=hours)
            elif interval_str.endswith("d"):
                days = int(interval_str[:-1])
                return now + timedelta(days=days)

        # Default to 1 hour
        return now + timedelta(hours=1)

    async def start_scheduler(self) -> None:
        """Start the workflow scheduler."""
        if self.running:
            return

        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())

        logger.info("Workflow scheduler started")

    async def stop_scheduler(self) -> None:
        """Stop the workflow scheduler."""
        if not self.running:
            return

        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass

        logger.info("Workflow scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            try:
                now = datetime.now()

                for schedule_id, schedule_info in self.scheduled_workflows.items():
                    if schedule_info["enabled"] and schedule_info["next_run"] <= now:

                        # Execute workflow
                        workflow_id = schedule_info["workflow_id"]
                        try:
                            await self.workflow_engine.execute_workflow(workflow_id)
                            schedule_info["last_run"] = now
                            schedule_info["run_count"] += 1

                            logger.info(
                                f"Scheduled execution of workflow '{workflow_id}' completed"
                            )

                        except Exception as e:
                            logger.error(
                                f"Scheduled execution of workflow '{workflow_id}' failed: {e}"
                            )

                        # Calculate next run
                        schedule_info["next_run"] = self._calculate_next_run(
                            schedule_info["schedule"]
                        )

                # Sleep for a minute before checking again
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)


# Global workflow engine instance
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine(
    config: AppConfig, tool_registry: ToolRegistry
) -> WorkflowEngine:
    """
    Get global workflow engine instance.

    Args:
        config: Application configuration
        tool_registry: Tool registry

    Returns:
        WorkflowEngine instance
    """
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine(config, tool_registry)
    return _workflow_engine
