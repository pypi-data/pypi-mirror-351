"""
Command execution tool for Kritrima AI CLI.

This module provides secure command execution capabilities including:
- Shell command execution with sandboxing
- Cross-platform command support
- Output capture and formatting
- Timeout and resource management
- Security validation and approval
"""

import asyncio
import os
import platform
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import psutil

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.security.approval import ApprovalSystem
from kritrima_ai.security.sandbox import SandboxManager
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class CommandExecutionTool(BaseTool):
    """
    Secure command execution tool for the AI agent.

    Provides safe command execution with sandboxing, timeout management,
    and comprehensive security checks.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the command execution tool.

        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.sandbox = SandboxManager(config)
        self.approval = ApprovalSystem(config)
        self._running_processes: Dict[str, subprocess.Popen] = {}

        # Platform-specific settings
        self.is_windows = platform.system() == "Windows"
        self.shell = "cmd.exe" if self.is_windows else "/bin/bash"

        logger.info("Command execution tool initialized")

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the command execution tool."""
        return create_tool_metadata(
            name="command_execution",
            description="Execute shell commands and scripts with security controls and output capture",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            "execute",
                            "script",
                            "system_info",
                            "list_processes",
                            "kill_process",
                        ],
                        "description": "The command operation to perform",
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to execute (for execute operation)",
                    },
                    "script_content": {
                        "type": "string",
                        "description": "Script content to execute (for script operation)",
                    },
                    "script_type": {
                        "type": "string",
                        "enum": ["bash", "python", "powershell", "cmd"],
                        "default": "bash",
                        "description": "Script interpreter type",
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for command execution",
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Timeout in seconds",
                    },
                    "capture_output": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to capture stdout/stderr",
                    },
                    "shell": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to use shell execution",
                    },
                    "env_vars": {
                        "type": "object",
                        "description": "Additional environment variables",
                    },
                    "require_approval": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to require user approval",
                    },
                    "filter_pattern": {
                        "type": "string",
                        "description": "Filter pattern for process listing",
                    },
                    "pid": {
                        "type": "integer",
                        "description": "Process ID for kill operation",
                    },
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force kill process",
                    },
                },
                required=["operation"],
            ),
            category="system",
            risk_level="high",
            requires_approval=True,
            supports_streaming=True,
            examples=[
                {
                    "description": "Execute a simple command",
                    "parameters": {"operation": "execute", "command": "ls -la"},
                },
                {
                    "description": "Run a Python script",
                    "parameters": {
                        "operation": "script",
                        "script_content": "print('Hello, World!')",
                        "script_type": "python",
                    },
                },
                {
                    "description": "Get system information",
                    "parameters": {"operation": "system_info"},
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute command operations based on the specified operation type.

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

            # Route to appropriate method based on operation
            if operation == "execute":
                result = await self.execute_command(
                    kwargs.get("command"),
                    kwargs.get("working_directory"),
                    kwargs.get("timeout", 30),
                    kwargs.get("capture_output", True),
                    kwargs.get("shell", True),
                    kwargs.get("env_vars"),
                    kwargs.get("require_approval", True),
                )
            elif operation == "script":
                result = await self.execute_script(
                    kwargs.get("script_content"),
                    kwargs.get("script_type", "bash"),
                    kwargs.get("working_directory"),
                    kwargs.get("timeout", 60),
                    kwargs.get("require_approval", True),
                )
            elif operation == "system_info":
                result = await self.get_system_info()
            elif operation == "list_processes":
                result = await self.list_processes(kwargs.get("filter_pattern"))
            elif operation == "kill_process":
                result = await self.kill_process(
                    kwargs.get("pid"), kwargs.get("force", False)
                )
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

            return ToolExecutionResult(
                success=True, result=result, metadata={"operation": operation}
            )

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute commands with streaming output for real-time feedback.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming output chunks
        """
        operation = kwargs.get("operation")

        try:
            if operation == "execute":
                # Stream command execution output
                async for chunk in self._stream_command_execution(
                    kwargs.get("command"),
                    kwargs.get("working_directory"),
                    kwargs.get("timeout", 30),
                    kwargs.get("shell", True),
                    kwargs.get("env_vars"),
                    kwargs.get("require_approval", True),
                ):
                    yield chunk
            else:
                # For other operations, just yield the final result
                result = await self.execute(**kwargs)
                if result.success:
                    yield str(result.result)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error: {str(e)}"

    async def _stream_command_execution(
        self,
        command: Union[str, List[str]],
        working_directory: Optional[str] = None,
        timeout: int = 30,
        shell: bool = True,
        env_vars: Optional[Dict[str, str]] = None,
        require_approval: bool = True,
    ) -> AsyncIterator[str]:
        """Stream command execution with real-time output."""
        try:
            # Normalize command
            if isinstance(command, str):
                cmd_str = command
                cmd_list = (
                    shlex.split(command) if not self.is_windows else command.split()
                )
            else:
                cmd_str = " ".join(command)
                cmd_list = command

            # Security validation
            if not await self._validate_command(cmd_str, require_approval):
                yield f"Error: Command not approved: {cmd_str}"
                return

            # Setup working directory
            work_dir = (
                Path(working_directory).resolve() if working_directory else Path.cwd()
            )
            if not self.sandbox.is_path_allowed(work_dir, "execute"):
                yield f"Error: Execution not allowed in directory: {work_dir}"
                return

            # Setup environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            yield f"Executing: {cmd_str}\n"
            yield f"Working Directory: {work_dir}\n"
            yield "--- Output ---\n"

            # Execute command with streaming
            process = await asyncio.create_subprocess_exec(
                *cmd_list if not shell else [self.shell, "-c", cmd_str],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=work_dir,
                env=env,
            )

            # Stream output
            while True:
                try:
                    line = await asyncio.wait_for(
                        process.stdout.readline(), timeout=1.0
                    )
                    if not line:
                        break
                    yield line.decode("utf-8", errors="replace")
                except asyncio.TimeoutError:
                    if process.returncode is not None:
                        break
                    continue

            # Wait for process completion
            await process.wait()
            yield f"\n--- Command completed with return code: {process.returncode} ---\n"

        except Exception as e:
            yield f"Error during command execution: {str(e)}\n"

    async def execute_command(
        self,
        command: Union[str, List[str]],
        working_directory: Optional[str] = None,
        timeout: int = 30,
        capture_output: bool = True,
        shell: bool = True,
        env_vars: Optional[Dict[str, str]] = None,
        require_approval: bool = True,
    ) -> str:
        """
        Execute a command with security checks and output capture.

        Args:
            command: Command to execute (string or list)
            working_directory: Working directory for execution
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr
            shell: Whether to use shell execution
            env_vars: Additional environment variables
            require_approval: Whether to require user approval

        Returns:
            Command output and execution details

        Raises:
            PermissionError: If command is not approved
            TimeoutError: If command times out
            subprocess.CalledProcessError: If command fails
        """
        try:
            # Normalize command
            if isinstance(command, str):
                cmd_str = command
                cmd_list = (
                    shlex.split(command) if not self.is_windows else command.split()
                )
            else:
                cmd_str = " ".join(command)
                cmd_list = command

            # Security validation
            if not await self._validate_command(cmd_str, require_approval):
                raise PermissionError(f"Command not approved: {cmd_str}")

            # Setup working directory
            work_dir = (
                Path(working_directory).resolve() if working_directory else Path.cwd()
            )
            if not self.sandbox.is_path_allowed(work_dir, "execute"):
                raise PermissionError(f"Execution not allowed in directory: {work_dir}")

            # Setup environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            # Execute command
            start_time = datetime.now()
            result = await self._execute_with_timeout(
                cmd_list if not shell else cmd_str,
                work_dir,
                timeout,
                capture_output,
                shell,
                env,
            )
            end_time = datetime.now()

            # Format result
            execution_time = (end_time - start_time).total_seconds()

            output_lines = [
                f"Command: {cmd_str}",
                f"Working Directory: {work_dir}",
                f"Execution Time: {execution_time:.2f}s",
                f"Return Code: {result['returncode']}",
                "",
            ]

            if result["stdout"]:
                output_lines.extend(["STDOUT:", result["stdout"], ""])

            if result["stderr"]:
                output_lines.extend(["STDERR:", result["stderr"], ""])

            if result["returncode"] != 0:
                output_lines.append(
                    f"Command failed with return code: {result['returncode']}"
                )

            logger.info(
                f"Executed command: {cmd_str} (return code: {result['returncode']})"
            )
            return "\n".join(output_lines)

        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            raise

    async def execute_script(
        self,
        script_content: str,
        script_type: str = "bash",
        working_directory: Optional[str] = None,
        timeout: int = 60,
        require_approval: bool = True,
    ) -> str:
        """
        Execute a script with the specified interpreter.

        Args:
            script_content: Script content to execute
            script_type: Script type (bash, python, powershell, etc.)
            working_directory: Working directory for execution
            timeout: Timeout in seconds
            require_approval: Whether to require user approval

        Returns:
            Script execution output
        """
        try:
            # Get interpreter command
            interpreter = self._get_interpreter(script_type)

            # Create temporary script file
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=self._get_script_extension(script_type), delete=False
            ) as temp_file:
                temp_file.write(script_content)
                temp_script_path = temp_file.name

            try:
                # Execute script
                command = [interpreter, temp_script_path]
                result = await self.execute_command(
                    command,
                    working_directory=working_directory,
                    timeout=timeout,
                    require_approval=require_approval,
                )

                return result

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_script_path)
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Error executing {script_type} script: {e}")
            raise

    async def get_system_info(self) -> str:
        """
        Get system information using safe commands.

        Returns:
            System information
        """
        try:
            info_lines = [
                f"Platform: {platform.system()} {platform.release()}",
                f"Architecture: {platform.machine()}",
                f"Python Version: {sys.version}",
                f"Current Directory: {os.getcwd()}",
                "",
            ]

            # CPU information
            try:
                cpu_count = psutil.cpu_count()
                cpu_percent = psutil.cpu_percent(interval=1)
                info_lines.extend(
                    [
                        f"CPU Cores: {cpu_count}",
                        f"CPU Usage: {cpu_percent}%",
                    ]
                )
            except Exception:
                pass

            # Memory information
            try:
                memory = psutil.virtual_memory()
                info_lines.extend(
                    [
                        f"Total Memory: {memory.total // (1024**3)} GB",
                        f"Available Memory: {memory.available // (1024**3)} GB",
                        f"Memory Usage: {memory.percent}%",
                    ]
                )
            except Exception:
                pass

            # Disk information
            try:
                disk = psutil.disk_usage("/")
                info_lines.extend(
                    [
                        f"Disk Total: {disk.total // (1024**3)} GB",
                        f"Disk Free: {disk.free // (1024**3)} GB",
                        f"Disk Usage: {(disk.used / disk.total) * 100:.1f}%",
                    ]
                )
            except Exception:
                pass

            return "\n".join(info_lines)

        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            raise

    async def list_processes(self, filter_pattern: Optional[str] = None) -> str:
        """
        List running processes with optional filtering.

        Args:
            filter_pattern: Pattern to filter process names

        Returns:
            Process list
        """
        try:
            processes = []

            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                try:
                    proc_info = proc.info
                    if (
                        filter_pattern
                        and filter_pattern.lower() not in proc_info["name"].lower()
                    ):
                        continue
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by CPU usage
            processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

            # Format output
            result_lines = [
                "Running Processes:",
                f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory%':<8}",
                "-" * 50,
            ]

            for proc in processes[:20]:  # Limit to top 20
                result_lines.append(
                    f"{proc['pid']:<8} {proc['name'][:19]:<20} "
                    f"{proc['cpu_percent'] or 0:<8.1f} {proc['memory_percent'] or 0:<8.1f}"
                )

            return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error listing processes: {e}")
            raise

    async def kill_process(self, pid: int, force: bool = False) -> str:
        """
        Kill a process by PID.

        Args:
            pid: Process ID to kill
            force: Whether to force kill

        Returns:
            Kill result
        """
        try:
            # Security check - only allow killing processes we started
            if str(pid) not in self._running_processes:
                # Additional check for user approval
                if not await self.approval.request_approval(
                    f"kill_process", f"Kill process {pid}", {"pid": pid, "force": force}
                ):
                    raise PermissionError(f"Not approved to kill process {pid}")

            try:
                process = psutil.Process(pid)
                process_name = process.name()

                if force:
                    process.kill()
                else:
                    process.terminate()

                # Wait for process to end
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    if not force:
                        process.kill()
                        process.wait(timeout=5)

                # Remove from our tracking
                if str(pid) in self._running_processes:
                    del self._running_processes[str(pid)]

                result = f"Process killed: {process_name} (PID: {pid})"
                logger.info(result)
                return result

            except psutil.NoSuchProcess:
                return f"Process {pid} not found"
            except psutil.AccessDenied:
                return f"Access denied to kill process {pid}"

        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            raise

    async def _execute_with_timeout(
        self,
        command: Union[str, List[str]],
        working_directory: Path,
        timeout: int,
        capture_output: bool,
        shell: bool,
        env: Dict[str, str],
    ) -> Dict[str, Any]:
        """Execute command with timeout handling."""
        try:
            # Create process
            if shell and isinstance(command, str):
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=working_directory,
                    env=env,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    stdin=subprocess.DEVNULL,
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    cwd=working_directory,
                    env=env,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    stdin=subprocess.DEVNULL,
                )

            # Track process
            self._running_processes[str(process.pid)] = process

            try:
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )

                return {
                    "returncode": process.returncode,
                    "stdout": (
                        stdout.decode("utf-8", errors="replace") if stdout else ""
                    ),
                    "stderr": (
                        stderr.decode("utf-8", errors="replace") if stderr else ""
                    ),
                }

            except asyncio.TimeoutError:
                # Kill process on timeout
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
                raise TimeoutError(f"Command timed out after {timeout} seconds")

            finally:
                # Remove from tracking
                if str(process.pid) in self._running_processes:
                    del self._running_processes[str(process.pid)]

        except Exception as e:
            logger.error(f"Error in command execution: {e}")
            raise

    async def _validate_command(self, command: str, require_approval: bool) -> bool:
        """Validate command for security and approval."""
        try:
            # Check if command is in dangerous list
            dangerous_commands = [
                "rm -rf",
                "del /s",
                "format",
                "fdisk",
                "dd if=",
                "mkfs",
                "sudo rm",
                "sudo dd",
                "shutdown",
                "reboot",
                "halt",
                "poweroff",
            ]

            command_lower = command.lower()
            for dangerous in dangerous_commands:
                if dangerous in command_lower:
                    if require_approval:
                        approved = await self.approval.request_approval(
                            "dangerous_command",
                            f"Execute potentially dangerous command: {command}",
                            {"command": command},
                        )
                        if not approved:
                            return False
                    else:
                        return False

            # Check approval mode
            if require_approval and self.config.approval_mode == "suggest":
                return await self.approval.request_approval(
                    "command_execution",
                    f"Execute command: {command}",
                    {"command": command},
                )

            return True

        except Exception as e:
            logger.error(f"Error validating command: {e}")
            return False

    def _get_interpreter(self, script_type: str) -> str:
        """Get interpreter command for script type."""
        interpreters = {
            "bash": "/bin/bash" if not self.is_windows else "bash",
            "sh": "/bin/sh" if not self.is_windows else "sh",
            "python": sys.executable,
            "python3": "python3" if not self.is_windows else "python",
            "powershell": "powershell" if self.is_windows else "pwsh",
            "cmd": "cmd" if self.is_windows else None,
            "node": "node",
            "npm": "npm",
            "yarn": "yarn",
        }

        interpreter = interpreters.get(script_type.lower())
        if not interpreter:
            raise ValueError(f"Unsupported script type: {script_type}")

        return interpreter

    def _get_script_extension(self, script_type: str) -> str:
        """Get file extension for script type."""
        extensions = {
            "bash": ".sh",
            "sh": ".sh",
            "python": ".py",
            "python3": ".py",
            "powershell": ".ps1",
            "cmd": ".bat",
            "node": ".js",
            "javascript": ".js",
        }

        return extensions.get(script_type.lower(), ".txt")

    async def cleanup(self) -> None:
        """Clean up running processes."""
        try:
            for pid, process in list(self._running_processes.items()):
                try:
                    if process.poll() is None:  # Process still running
                        process.terminate()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=5)
                        except asyncio.TimeoutError:
                            process.kill()
                except Exception:
                    pass

            self._running_processes.clear()
            logger.info("Command execution tool cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Alias for compatibility with app imports
class CommandExecution(CommandExecutionTool):
    """Alias for CommandExecutionTool to maintain compatibility."""
    
    def __init__(self, config: AppConfig):
        super().__init__(config)
