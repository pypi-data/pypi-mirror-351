"""
Advanced sandbox execution system for Kritrima AI CLI.

This module implements platform-specific sandboxing mechanisms to provide
secure command execution with restricted file system access, network isolation,
and resource limiting.
"""

import asyncio
import os
import platform
import shutil
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger, performance_timer

logger = get_logger(__name__)


class SandboxType(Enum):
    """Types of sandbox implementations."""

    LANDLOCK = "landlock"  # Linux Landlock LSM
    SEATBELT = "seatbelt"  # macOS Seatbelt
    APPCONTAINER = "appcontainer"  # Windows AppContainer
    CHROOT = "chroot"  # Traditional chroot jail
    CONTAINER = "container"  # Docker/Podman container
    RAW = "raw"  # No sandboxing (fallback)


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""

    type: SandboxType
    allowed_read_paths: List[Path]
    allowed_write_paths: List[Path]
    allowed_exec_paths: List[Path]
    network_access: bool = False
    timeout: float = 30.0
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    temp_dir: Optional[Path] = None
    environment_vars: Dict[str, str] = None

    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}


@dataclass
class SandboxResult:
    """Result of sandbox execution."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    memory_peak_mb: float
    cpu_time: float
    sandbox_type: SandboxType
    warnings: List[str] = None
    violations: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.violations is None:
            self.violations = []


class SandboxManager:
    """
    Advanced sandbox manager with platform-specific implementations.

    Provides secure command execution with comprehensive access control,
    resource limiting, and violation monitoring.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the sandbox manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()

        # Detect best available sandbox type
        self.preferred_sandbox = self._detect_best_sandbox()

        # Create secure temp directory
        self.temp_root = Path(tempfile.mkdtemp(prefix="kritrima_sandbox_"))
        self.temp_root.chmod(0o700)

        # Process monitoring
        self._active_processes: Dict[str, psutil.Process] = {}

        logger.info(
            f"Sandbox manager initialized - Type: {self.preferred_sandbox.value}, Platform: {self.platform}"
        )

    async def execute_command(
        self,
        command: List[str],
        working_dir: Optional[Path] = None,
        sandbox_config: Optional[SandboxConfig] = None,
        request_id: Optional[str] = None,
    ) -> SandboxResult:
        """
        Execute a command in a secure sandbox.

        Args:
            command: Command and arguments to execute
            working_dir: Working directory for execution
            sandbox_config: Custom sandbox configuration
            request_id: Request identifier for tracking

        Returns:
            Sandbox execution result
        """
        if sandbox_config is None:
            sandbox_config = self._create_default_sandbox_config(working_dir)

        start_time = time.time()

        try:
            with performance_timer(
                f"sandbox_execute_{sandbox_config.type.value}", logger
            ):
                # Select execution method based on sandbox type
                if sandbox_config.type == SandboxType.LANDLOCK:
                    result = await self._execute_with_landlock(
                        command, working_dir, sandbox_config, request_id
                    )
                elif sandbox_config.type == SandboxType.SEATBELT:
                    result = await self._execute_with_seatbelt(
                        command, working_dir, sandbox_config, request_id
                    )
                elif sandbox_config.type == SandboxType.APPCONTAINER:
                    result = await self._execute_with_appcontainer(
                        command, working_dir, sandbox_config, request_id
                    )
                elif sandbox_config.type == SandboxType.CHROOT:
                    result = await self._execute_with_chroot(
                        command, working_dir, sandbox_config, request_id
                    )
                elif sandbox_config.type == SandboxType.CONTAINER:
                    result = await self._execute_with_container(
                        command, working_dir, sandbox_config, request_id
                    )
                else:
                    result = await self._execute_raw(
                        command, working_dir, sandbox_config, request_id
                    )

                # Add execution time
                result.execution_time = time.time() - start_time

                # Log execution details
                logger.info(
                    f"Sandbox execution completed - "
                    f"Type: {sandbox_config.type.value}, "
                    f"Success: {result.success}, "
                    f"Exit code: {result.exit_code}, "
                    f"Time: {result.execution_time:.2f}s"
                )

                return result

        except Exception as e:
            logger.error(f"Sandbox execution error: {e}", exc_info=True)
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Sandbox execution error: {str(e)}",
                execution_time=time.time() - start_time,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=sandbox_config.type,
                violations=[f"Execution error: {str(e)}"],
            )

    async def _execute_with_landlock(
        self,
        command: List[str],
        working_dir: Optional[Path],
        config: SandboxConfig,
        request_id: Optional[str],
    ) -> SandboxResult:
        """Execute command with Linux Landlock LSM."""
        try:
            # Create landlock script
            landlock_script = self._create_landlock_script(command, working_dir, config)

            # Execute with landlock restrictions
            process = await asyncio.create_subprocess_exec(
                "python3",
                "-c",
                landlock_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=self._prepare_environment(config),
            )

            # Monitor process
            if request_id:
                self._active_processes[request_id] = psutil.Process(process.pid)

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise TimeoutError(f"Command timed out after {config.timeout} seconds")

            # Get resource usage
            memory_peak_mb, cpu_time = self._get_process_stats(request_id)

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=0.0,  # Will be set by caller
                memory_peak_mb=memory_peak_mb,
                cpu_time=cpu_time,
                sandbox_type=SandboxType.LANDLOCK,
            )

        except Exception as e:
            logger.error(f"Landlock execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Landlock execution error: {str(e)}",
                execution_time=0.0,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=SandboxType.LANDLOCK,
                violations=[f"Landlock error: {str(e)}"],
            )
        finally:
            if request_id and request_id in self._active_processes:
                del self._active_processes[request_id]

    async def _execute_with_seatbelt(
        self,
        command: List[str],
        working_dir: Optional[Path],
        config: SandboxConfig,
        request_id: Optional[str],
    ) -> SandboxResult:
        """Execute command with macOS Seatbelt."""
        try:
            # Create seatbelt profile
            seatbelt_profile = self._create_seatbelt_profile(config)

            # Write profile to temp file
            profile_path = (
                self.temp_root / f"seatbelt_profile_{request_id or 'default'}.sb"
            )
            profile_path.write_text(seatbelt_profile)

            # Execute with sandbox-exec
            sandbox_command = ["sandbox-exec", "-f", str(profile_path), *command]

            process = await asyncio.create_subprocess_exec(
                *sandbox_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=self._prepare_environment(config),
            )

            # Monitor process
            if request_id:
                self._active_processes[request_id] = psutil.Process(process.pid)

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise TimeoutError(f"Command timed out after {config.timeout} seconds")

            # Get resource usage
            memory_peak_mb, cpu_time = self._get_process_stats(request_id)

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=0.0,
                memory_peak_mb=memory_peak_mb,
                cpu_time=cpu_time,
                sandbox_type=SandboxType.SEATBELT,
            )

        except Exception as e:
            logger.error(f"Seatbelt execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Seatbelt execution error: {str(e)}",
                execution_time=0.0,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=SandboxType.SEATBELT,
                violations=[f"Seatbelt error: {str(e)}"],
            )

    async def _execute_with_appcontainer(
        self,
        command: List[str],
        working_dir: Optional[Path],
        config: SandboxConfig,
        request_id: Optional[str],
    ) -> SandboxResult:
        """Execute command with Windows AppContainer."""
        try:
            # For Windows, use PowerShell with restricted execution policy
            ps_script = self._create_powershell_restricted_script(command, config)

            process = await asyncio.create_subprocess_exec(
                "powershell.exe",
                "-ExecutionPolicy",
                "Restricted",
                "-Command",
                ps_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=self._prepare_environment(config),
            )

            # Monitor process
            if request_id:
                self._active_processes[request_id] = psutil.Process(process.pid)

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise TimeoutError(f"Command timed out after {config.timeout} seconds")

            # Get resource usage
            memory_peak_mb, cpu_time = self._get_process_stats(request_id)

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=0.0,
                memory_peak_mb=memory_peak_mb,
                cpu_time=cpu_time,
                sandbox_type=SandboxType.APPCONTAINER,
            )

        except Exception as e:
            logger.error(f"AppContainer execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"AppContainer execution error: {str(e)}",
                execution_time=0.0,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=SandboxType.APPCONTAINER,
                violations=[f"AppContainer error: {str(e)}"],
            )

    async def _execute_with_chroot(
        self,
        command: List[str],
        working_dir: Optional[Path],
        config: SandboxConfig,
        request_id: Optional[str],
    ) -> SandboxResult:
        """Execute command with chroot jail."""
        try:
            # Create chroot environment
            chroot_dir = self.temp_root / f"chroot_{request_id or 'default'}"
            chroot_dir.mkdir(exist_ok=True)

            # Setup basic chroot environment
            await self._setup_chroot_environment(chroot_dir, config)

            # Execute with chroot
            chroot_command = ["sudo", "chroot", str(chroot_dir), *command]

            process = await asyncio.create_subprocess_exec(
                *chroot_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._prepare_environment(config),
            )

            # Monitor process
            if request_id:
                self._active_processes[request_id] = psutil.Process(process.pid)

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise TimeoutError(f"Command timed out after {config.timeout} seconds")

            # Get resource usage
            memory_peak_mb, cpu_time = self._get_process_stats(request_id)

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=0.0,
                memory_peak_mb=memory_peak_mb,
                cpu_time=cpu_time,
                sandbox_type=SandboxType.CHROOT,
            )

        except Exception as e:
            logger.error(f"Chroot execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Chroot execution error: {str(e)}",
                execution_time=0.0,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=SandboxType.CHROOT,
                violations=[f"Chroot error: {str(e)}"],
            )

    async def _execute_with_container(
        self,
        command: List[str],
        working_dir: Optional[Path],
        config: SandboxConfig,
        request_id: Optional[str],
    ) -> SandboxResult:
        """Execute command with container isolation."""
        try:
            # Try Docker first, then Podman
            container_runtime = await self._detect_container_runtime()
            if not container_runtime:
                raise RuntimeError("No container runtime available")

            # Create container command
            container_command = [
                container_runtime,
                "run",
                "--rm",
                "--network=none" if not config.network_access else "--network=bridge",
                f"--memory={config.max_memory_mb}m",
                f"--cpus={config.max_cpu_percent / 100}",
                "--security-opt=no-new-privileges",
                "--user=1000:1000",
                "-w",
                "/workspace",
                "-v",
                f"{working_dir or Path.cwd()}:/workspace:ro",
            ]

            # Add write mounts
            for write_path in config.allowed_write_paths:
                container_command.extend(
                    ["-v", f"{write_path}:/mnt/{write_path.name}:rw"]
                )

            # Use Alpine Linux for minimal attack surface
            container_command.extend(["alpine:latest", *command])

            process = await asyncio.create_subprocess_exec(
                *container_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._prepare_environment(config),
            )

            # Monitor process
            if request_id:
                self._active_processes[request_id] = psutil.Process(process.pid)

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise TimeoutError(f"Command timed out after {config.timeout} seconds")

            # Get resource usage
            memory_peak_mb, cpu_time = self._get_process_stats(request_id)

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=0.0,
                memory_peak_mb=memory_peak_mb,
                cpu_time=cpu_time,
                sandbox_type=SandboxType.CONTAINER,
            )

        except Exception as e:
            logger.error(f"Container execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Container execution error: {str(e)}",
                execution_time=0.0,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=SandboxType.CONTAINER,
                violations=[f"Container error: {str(e)}"],
            )

    async def _execute_raw(
        self,
        command: List[str],
        working_dir: Optional[Path],
        config: SandboxConfig,
        request_id: Optional[str],
    ) -> SandboxResult:
        """Execute command without sandboxing (fallback)."""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=self._prepare_environment(config),
            )

            # Monitor process
            if request_id:
                self._active_processes[request_id] = psutil.Process(process.pid)

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                raise TimeoutError(f"Command timed out after {config.timeout} seconds")

            # Get resource usage
            memory_peak_mb, cpu_time = self._get_process_stats(request_id)

            return SandboxResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=0.0,
                memory_peak_mb=memory_peak_mb,
                cpu_time=cpu_time,
                sandbox_type=SandboxType.RAW,
                warnings=["No sandboxing applied - security reduced"],
            )

        except Exception as e:
            logger.error(f"Raw execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Raw execution error: {str(e)}",
                execution_time=0.0,
                memory_peak_mb=0.0,
                cpu_time=0.0,
                sandbox_type=SandboxType.RAW,
                violations=[f"Raw execution error: {str(e)}"],
            )
        finally:
            if request_id and request_id in self._active_processes:
                del self._active_processes[request_id]

    def _detect_best_sandbox(self) -> SandboxType:
        """Detect the best available sandbox type for the current platform."""
        if self.platform == "linux":
            # Check for Landlock support (Linux 5.13+)
            if self._check_landlock_support():
                return SandboxType.LANDLOCK
            # Fall back to chroot
            elif os.geteuid() == 0:  # Root required for chroot
                return SandboxType.CHROOT
        elif self.platform == "darwin":
            # Check for sandbox-exec
            if shutil.which("sandbox-exec"):
                return SandboxType.SEATBELT
        elif self.platform == "windows":
            # Use AppContainer on Windows
            return SandboxType.APPCONTAINER

        # Check for container runtime
        if shutil.which("docker") or shutil.which("podman"):
            return SandboxType.CONTAINER

        # Fallback to raw execution
        return SandboxType.RAW

    def _check_landlock_support(self) -> bool:
        """Check if Landlock LSM is available."""
        try:
            # Check kernel version
            with open("/proc/version", "r") as f:
                version_str = f.read()
            # Simple check - Landlock was introduced in 5.13
            # More sophisticated check would parse version numbers
            return (
                "5.13" in version_str
                or "5.14" in version_str
                or "5.15" in version_str
                or "6." in version_str
            )
        except (FileNotFoundError, PermissionError):
            return False

    async def _detect_container_runtime(self) -> Optional[str]:
        """Detect available container runtime."""
        for runtime in ["docker", "podman"]:
            if shutil.which(runtime):
                try:
                    # Test if runtime is actually working
                    process = await asyncio.create_subprocess_exec(
                        runtime,
                        "version",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    await asyncio.wait_for(process.communicate(), timeout=5.0)
                    if process.returncode == 0:
                        return runtime
                except (asyncio.TimeoutError, Exception):
                    continue
        return None

    def _create_default_sandbox_config(
        self, working_dir: Optional[Path]
    ) -> SandboxConfig:
        """Create default sandbox configuration."""
        current_dir = working_dir or Path.cwd()

        return SandboxConfig(
            type=self.preferred_sandbox,
            allowed_read_paths=[
                current_dir,
                Path.home(),
                Path("/usr"),
                Path("/bin"),
                Path("/lib"),
                Path("/etc"),
            ],
            allowed_write_paths=[current_dir, self.temp_root],
            allowed_exec_paths=[Path("/usr/bin"), Path("/bin"), Path("/usr/local/bin")],
            network_access=self.config.security.allow_network_access,
            timeout=self.config.security.command_timeout,
            max_memory_mb=self.config.security.max_memory_mb,
            max_cpu_percent=self.config.security.max_cpu_percent,
        )

    def _create_landlock_script(
        self, command: List[str], working_dir: Optional[Path], config: SandboxConfig
    ) -> str:
        """Create a script for Landlock-based sandboxing."""
        command_str = " ".join(repr(arg) for arg in command)
        working_dir_str = repr(str(working_dir)) if working_dir else "None"
        read_paths_str = ", ".join(repr(str(p)) for p in config.allowed_read_paths)
        write_paths_str = ", ".join(repr(str(p)) for p in config.allowed_write_paths)
        timeout_str = str(config.timeout)

        return f"""#!/usr/bin/env python3
import subprocess
import ctypes
import ctypes.util
import sys
import os

try:
    # Load libc
    libc = ctypes.CDLL(ctypes.util.find_library("c"))
    
    # Apply Landlock restrictions
    read_paths = [{read_paths_str}]
    write_paths = [{write_paths_str}]
    
    # Note: Full Landlock implementation would require more complex setup
    # This is a simplified version for demonstration
    
    # Execute the command
    result = subprocess.run(
        {command_str},
        cwd={working_dir_str},
        capture_output=True,
        text=True,
        timeout={timeout_str}
    )
    
    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    
    exit(result.returncode)
    
except Exception as e:
    print(f"Landlock execution error: {{e}}", file=sys.stderr)
    exit(1)
"""

    def _create_seatbelt_profile(self, config: SandboxConfig) -> str:
        """Create macOS Seatbelt sandbox profile."""
        read_paths = " ".join(f'(literal "{p}")' for p in config.allowed_read_paths)
        write_paths = " ".join(f'(literal "{p}")' for p in config.allowed_write_paths)

        return f"""
(version 1)
(deny default)
(import "system.sb")

; Allow reading from specified paths
(allow file-read*
    {read_paths}
    (literal "/dev/null")
    (literal "/dev/zero")
    (literal "/dev/random")
    (literal "/dev/urandom")
)

; Allow writing to specified paths
(allow file-write*
    {write_paths}
)

; Allow execution of system binaries
(allow process-exec
    (literal "/bin/sh")
    (literal "/usr/bin/env")
    (regex #"^/usr/bin/.*")
    (regex #"^/bin/.*")
)

; Network access
{"(allow network*)" if config.network_access else "(deny network*)"}

; Basic system access
(allow process-info-pidinfo)
(allow process-info-pidfdinfo)
(allow process-info-pidfileportinfo)
(allow process-info-setcontrol)
(allow process-info-dirtycontrol)
(allow process-info-rusage)
"""

    def _create_powershell_restricted_script(
        self, command: List[str], config: SandboxConfig
    ) -> str:
        """Create PowerShell script with restrictions."""
        " ".join(f'"{arg}"' for arg in command)
        return f"""
$ErrorActionPreference = "Stop"
try {{
    $process = Start-Process -FilePath "{command[0]}" -ArgumentList @({", ".join(repr(arg) for arg in command[1:])}) -Wait -PassThru -NoNewWindow -RedirectStandardOutput "stdout.txt" -RedirectStandardError "stderr.txt"
    $stdout = Get-Content "stdout.txt" -Raw -ErrorAction SilentlyContinue
    $stderr = Get-Content "stderr.txt" -Raw -ErrorAction SilentlyContinue
    if ($stdout) {{ Write-Output $stdout }}
    if ($stderr) {{ Write-Error $stderr }}
    exit $process.ExitCode
}} catch {{
    Write-Error "PowerShell execution error: $($_.Exception.Message)"
    exit 1
}} finally {{
    Remove-Item "stdout.txt" -ErrorAction SilentlyContinue
    Remove-Item "stderr.txt" -ErrorAction SilentlyContinue
}}
"""

    async def _setup_chroot_environment(
        self, chroot_dir: Path, config: SandboxConfig
    ) -> None:
        """Setup basic chroot environment."""
        # Create basic directory structure
        for dir_name in ["bin", "lib", "lib64", "usr", "etc", "tmp", "dev"]:
            (chroot_dir / dir_name).mkdir(exist_ok=True)

        # Copy essential binaries
        essential_binaries = ["/bin/sh", "/bin/bash", "/usr/bin/env"]
        for binary in essential_binaries:
            if Path(binary).exists():
                shutil.copy2(binary, chroot_dir / binary.lstrip("/"))

        # Copy essential libraries (simplified)
        try:
            # This is a simplified approach - a full implementation would
            # need to copy all dependencies
            lib_dirs = ["/lib", "/lib64", "/usr/lib"]
            for lib_dir in lib_dirs:
                if Path(lib_dir).exists():
                    for lib_file in Path(lib_dir).glob("libc.*"):
                        dest = chroot_dir / lib_file.relative_to("/")
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(lib_file, dest)
        except Exception as e:
            logger.warning(f"Failed to copy some libraries: {e}")

    def _prepare_environment(self, config: SandboxConfig) -> Dict[str, str]:
        """Prepare environment variables for execution."""
        env = os.environ.copy()

        # Remove potentially dangerous environment variables
        dangerous_vars = [
            "LD_PRELOAD",
            "LD_LIBRARY_PATH",
            "DYLD_INSERT_LIBRARIES",
            "PYTHONPATH",
            "PATH_INFO",
            "SCRIPT_NAME",
        ]
        for var in dangerous_vars:
            env.pop(var, None)

        # Add config-specific environment variables
        env.update(config.environment_vars)

        # Limit PATH to safe directories
        safe_paths = ["/usr/bin", "/bin", "/usr/local/bin"]
        env["PATH"] = ":".join(safe_paths)

        return env

    def _get_process_stats(self, request_id: Optional[str]) -> tuple[float, float]:
        """Get process statistics for monitoring."""
        if not request_id or request_id not in self._active_processes:
            return 0.0, 0.0

        try:
            process = self._active_processes[request_id]
            memory_info = process.memory_info()
            cpu_times = process.cpu_times()

            memory_peak_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            cpu_time = cpu_times.user + cpu_times.system

            return memory_peak_mb, cpu_time
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0, 0.0

    async def terminate_process(self, request_id: str) -> bool:
        """Terminate a running sandboxed process."""
        if request_id not in self._active_processes:
            return False

        try:
            process = self._active_processes[request_id]
            process.terminate()

            # Wait for graceful termination
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if graceful termination fails
                process.kill()

            del self._active_processes[request_id]
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def get_active_processes(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active sandboxed processes."""
        active = {}
        for request_id, process in self._active_processes.items():
            try:
                active[request_id] = {
                    "pid": process.pid,
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": process.memory_info().rss / 1024 / 1024,
                    "create_time": process.create_time(),
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return active

    def cleanup(self) -> None:
        """Cleanup sandbox resources."""
        try:
            # Terminate all active processes
            for request_id in list(self._active_processes.keys()):
                self.terminate_process(request_id)

            # Remove temp directory
            if self.temp_root.exists():
                shutil.rmtree(self.temp_root, ignore_errors=True)
        except Exception as e:
            logger.error(f"Sandbox cleanup error: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Don't raise in destructor
