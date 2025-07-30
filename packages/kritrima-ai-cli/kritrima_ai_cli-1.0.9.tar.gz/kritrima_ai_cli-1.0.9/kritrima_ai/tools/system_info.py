"""
System Information Tool for Kritrima AI CLI.

This module provides comprehensive system information gathering capabilities including:
- Hardware specifications and resource monitoring
- Operating system details and environment
- Network configuration and connectivity
- Process monitoring and system performance
- Development environment detection
- Security and permission analysis
"""

import asyncio
import json
import os
import platform
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import psutil

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemSpecs:
    """System hardware specifications."""

    cpu_count: int
    cpu_freq: Dict[str, float]
    memory_total: int
    memory_available: int
    disk_usage: Dict[str, Dict[str, int]]
    gpu_info: List[Dict[str, Any]]


@dataclass
class OSInfo:
    """Operating system information."""

    system: str
    release: str
    version: str
    machine: str
    processor: str
    architecture: Tuple[str, str]
    python_version: str
    python_executable: str


@dataclass
class NetworkInfo:
    """Network configuration information."""

    hostname: str
    ip_addresses: List[str]
    network_interfaces: Dict[str, Dict[str, Any]]
    internet_connectivity: bool
    dns_servers: List[str]


@dataclass
class ProcessInfo:
    """Process and performance information."""

    current_process: Dict[str, Any]
    system_load: Dict[str, float]
    top_processes: List[Dict[str, Any]]
    boot_time: str
    uptime: str


@dataclass
class DevelopmentEnvironment:
    """Development environment information."""

    shell: str
    terminal: str
    editors_available: List[str]
    version_control: Dict[str, str]
    package_managers: Dict[str, str]
    programming_languages: Dict[str, str]
    docker_info: Optional[Dict[str, Any]]


@dataclass
class SecurityInfo:
    """Security and permissions information."""

    user_permissions: Dict[str, bool]
    firewall_status: Optional[str]
    antivirus_status: Optional[str]
    encryption_support: Dict[str, bool]
    secure_boot: Optional[bool]


class SystemInfoTool(BaseTool):
    """
    Comprehensive system information gathering tool.

    Provides detailed information about:
    - Hardware specifications and performance
    - Operating system and environment
    - Network configuration and connectivity
    - Running processes and system load
    - Development environment setup
    - Security configuration and permissions
    """

    def __init__(self, config: AppConfig):
        """Initialize the system info tool."""
        super().__init__(config)
        self.cache_duration = timedelta(minutes=5)
        self._cache: Dict[str, Tuple[datetime, Any]] = {}

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the system info tool."""
        return create_tool_metadata(
            name="system_info",
            description="Gather comprehensive system information including hardware, OS, network, processes, and development environment",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            "full_info",
                            "system_specs",
                            "os_info",
                            "network_info",
                            "process_info",
                            "dev_env",
                            "security_info",
                            "resource_usage",
                            "system_health",
                        ],
                        "description": "The type of system information to gather",
                    },
                    "include_sensitive": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to include sensitive information like IP addresses",
                    },
                    "duration": {
                        "type": "integer",
                        "default": 60,
                        "description": "Duration for resource monitoring (in seconds)",
                    },
                    "interval": {
                        "type": "integer",
                        "default": 5,
                        "description": "Interval for resource monitoring (in seconds)",
                    },
                },
                required=["operation"],
            ),
            category="system",
            risk_level="low",
            requires_approval=False,
            supports_streaming=True,
            examples=[
                {
                    "description": "Get full system information",
                    "parameters": {
                        "operation": "full_info",
                        "include_sensitive": False,
                    },
                },
                {
                    "description": "Get hardware specifications",
                    "parameters": {"operation": "system_specs"},
                },
                {
                    "description": "Monitor resource usage",
                    "parameters": {"operation": "resource_usage", "duration": 30},
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute system information gathering based on the specified operation.

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

            include_sensitive = kwargs.get("include_sensitive", False)

            # Route to appropriate method based on operation
            if operation == "full_info":
                result = self.get_system_info(include_sensitive)
            elif operation == "system_specs":
                result = asdict(self.get_system_specs())
            elif operation == "os_info":
                result = asdict(self.get_os_info())
            elif operation == "network_info":
                result = asdict(self.get_network_info(include_sensitive))
            elif operation == "process_info":
                result = asdict(self.get_process_info())
            elif operation == "dev_env":
                result = asdict(self.get_development_environment())
            elif operation == "security_info":
                result = asdict(self.get_security_info())
            elif operation == "resource_usage":
                result = self.get_resource_usage()
            elif operation == "system_health":
                result = self.get_system_health()
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

            return ToolExecutionResult(
                success=True,
                result=result,
                metadata={
                    "operation": operation,
                    "include_sensitive": include_sensitive,
                },
            )

        except Exception as e:
            logger.error(f"System info operation failed: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute system info operations with streaming output for large data.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming output chunks
        """
        operation = kwargs.get("operation")

        try:
            if operation == "resource_usage":
                # Stream resource monitoring
                duration = kwargs.get("duration", 60)
                interval = kwargs.get("interval", 5)

                yield f"Starting resource monitoring for {duration} seconds...\n"

                start_time = time.time()
                while time.time() - start_time < duration:
                    usage = self.get_resource_usage()
                    timestamp = datetime.now().strftime("%H:%M:%S")

                    yield f"[{timestamp}] CPU: {usage['cpu_percent']:.1f}% | "
                    yield f"Memory: {usage['memory_percent']:.1f}% | "
                    yield f"Disk I/O: {usage['disk_io']['read_mb']:.1f}MB/s read, {usage['disk_io']['write_mb']:.1f}MB/s write\n"

                    await asyncio.sleep(interval)

                yield "Resource monitoring completed.\n"
            else:
                # For other operations, just yield the final result
                result = await self.execute(**kwargs)
                if result.success:
                    import json

                    yield json.dumps(result.result, indent=2, default=str)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error: {str(e)}"

    def get_system_info(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive system information.

        Args:
            include_sensitive: Whether to include sensitive information like IPs

        Returns:
            Dictionary containing all system information
        """
        try:
            logger.info("Gathering comprehensive system information")

            info = {
                "timestamp": datetime.now().isoformat(),
                "system_specs": asdict(self.get_system_specs()),
                "os_info": asdict(self.get_os_info()),
                "network_info": asdict(self.get_network_info(include_sensitive)),
                "process_info": asdict(self.get_process_info()),
                "development_env": asdict(self.get_development_environment()),
                "security_info": asdict(self.get_security_info()),
                "environment_variables": self.get_environment_variables(
                    include_sensitive
                ),
                "system_health": self.get_system_health(),
                "resource_usage": self.get_resource_usage(),
            }

            logger.info("System information gathered successfully")
            return info

        except Exception as e:
            logger.error(f"Error gathering system information: {e}")
            raise

    def get_system_specs(self) -> SystemSpecs:
        """Get hardware specifications."""
        cache_key = "system_specs"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            # CPU information
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}

            # Memory information
            memory = psutil.virtual_memory()
            memory_total = memory.total
            memory_available = memory.available

            # Disk usage for all mounted drives
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": round((usage.used / usage.total) * 100, 2),
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                    }
                except (PermissionError, OSError):
                    continue

            # GPU information (basic detection)
            gpu_info = self._get_gpu_info()

            specs = SystemSpecs(
                cpu_count=cpu_count,
                cpu_freq=cpu_freq,
                memory_total=memory_total,
                memory_available=memory_available,
                disk_usage=disk_usage,
                gpu_info=gpu_info,
            )

            self._set_cache(cache_key, specs)
            return specs

        except Exception as e:
            logger.error(f"Error getting system specs: {e}")
            raise

    def get_os_info(self) -> OSInfo:
        """Get operating system information."""
        cache_key = "os_info"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            info = OSInfo(
                system=platform.system(),
                release=platform.release(),
                version=platform.version(),
                machine=platform.machine(),
                processor=platform.processor(),
                architecture=platform.architecture(),
                python_version=platform.python_version(),
                python_executable=sys.executable,
            )

            self._set_cache(cache_key, info)
            return info

        except Exception as e:
            logger.error(f"Error getting OS info: {e}")
            raise

    def get_network_info(self, include_sensitive: bool = False) -> NetworkInfo:
        """Get network configuration information."""
        try:
            hostname = socket.gethostname()

            # Get IP addresses
            ip_addresses = []
            if include_sensitive:
                try:
                    # Get local IP
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    ip_addresses.append(local_ip)
                except:
                    pass

                # Get all interface IPs
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            ip_addresses.append(addr.address)

            # Network interfaces
            network_interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {"addresses": [], "stats": {}}

                for addr in addrs:
                    addr_info = {
                        "family": str(addr.family),
                        "broadcast": getattr(addr, "broadcast", None),
                        "netmask": getattr(addr, "netmask", None),
                        "ptp": getattr(addr, "ptp", None),
                    }

                    if include_sensitive:
                        addr_info["address"] = addr.address

                    interface_info["addresses"].append(addr_info)

                # Interface statistics
                try:
                    stats = psutil.net_if_stats()[interface]
                    interface_info["stats"] = {
                        "isup": stats.isup,
                        "duplex": str(stats.duplex),
                        "speed": stats.speed,
                        "mtu": stats.mtu,
                    }
                except KeyError:
                    pass

                network_interfaces[interface] = interface_info

            # Test internet connectivity
            internet_connectivity = self._test_internet_connectivity()

            # DNS servers (basic detection)
            dns_servers = self._get_dns_servers() if include_sensitive else []

            return NetworkInfo(
                hostname=hostname,
                ip_addresses=ip_addresses,
                network_interfaces=network_interfaces,
                internet_connectivity=internet_connectivity,
                dns_servers=dns_servers,
            )

        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            raise

    def get_process_info(self) -> ProcessInfo:
        """Get process and performance information."""
        try:
            # Current process info
            current_proc = psutil.Process()
            current_process = {
                "pid": current_proc.pid,
                "name": current_proc.name(),
                "cpu_percent": current_proc.cpu_percent(),
                "memory_percent": current_proc.memory_percent(),
                "memory_info": current_proc.memory_info()._asdict(),
                "create_time": datetime.fromtimestamp(
                    current_proc.create_time()
                ).isoformat(),
                "status": current_proc.status(),
                "num_threads": current_proc.num_threads(),
            }

            # System load
            system_load = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
                "memory_percent": psutil.virtual_memory().percent,
                "swap_percent": psutil.swap_memory().percent,
            }

            # Top processes by CPU usage
            top_processes = []
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                try:
                    proc_info = proc.info
                    if proc_info["cpu_percent"] > 0:
                        top_processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            top_processes = sorted(
                top_processes, key=lambda x: x["cpu_percent"], reverse=True
            )[:10]

            # Boot time and uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
            uptime = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))

            return ProcessInfo(
                current_process=current_process,
                system_load=system_load,
                top_processes=top_processes,
                boot_time=boot_time,
                uptime=uptime,
            )

        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            raise

    def get_development_environment(self) -> DevelopmentEnvironment:
        """Get development environment information."""
        cache_key = "dev_env"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            # Shell information
            shell = os.environ.get("SHELL", os.environ.get("ComSpec", "unknown"))
            terminal = os.environ.get("TERM", os.environ.get("TERM_PROGRAM", "unknown"))

            # Available editors
            editors_available = []
            common_editors = [
                "code",
                "vim",
                "nano",
                "emacs",
                "subl",
                "atom",
                "notepad++",
            ]
            for editor in common_editors:
                if self._command_exists(editor):
                    editors_available.append(editor)

            # Version control systems
            version_control = {}
            vcs_systems = ["git", "svn", "hg", "bzr"]
            for vcs in vcs_systems:
                version = self._get_command_version(vcs)
                if version:
                    version_control[vcs] = version

            # Package managers
            package_managers = {}
            managers = ["pip", "npm", "yarn", "cargo", "go", "composer", "gem"]
            for manager in managers:
                version = self._get_command_version(manager)
                if version:
                    package_managers[manager] = version

            # Programming languages
            programming_languages = {}
            languages = {
                "python": ["python", "--version"],
                "python3": ["python3", "--version"],
                "node": ["node", "--version"],
                "java": ["java", "-version"],
                "javac": ["javac", "-version"],
                "gcc": ["gcc", "--version"],
                "clang": ["clang", "--version"],
                "rustc": ["rustc", "--version"],
                "go": ["go", "version"],
                "ruby": ["ruby", "--version"],
                "php": ["php", "--version"],
                "dotnet": ["dotnet", "--version"],
            }

            for lang, cmd in languages.items():
                version = self._get_command_version(cmd[0], cmd[1:])
                if version:
                    programming_languages[lang] = version

            # Docker information
            docker_info = self._get_docker_info()

            env = DevelopmentEnvironment(
                shell=shell,
                terminal=terminal,
                editors_available=editors_available,
                version_control=version_control,
                package_managers=package_managers,
                programming_languages=programming_languages,
                docker_info=docker_info,
            )

            self._set_cache(cache_key, env)
            return env

        except Exception as e:
            logger.error(f"Error getting development environment: {e}")
            raise

    def get_security_info(self) -> SecurityInfo:
        """Get security and permissions information."""
        try:
            # User permissions
            user_permissions = {
                "is_admin": self._is_admin(),
                "can_write_system": os.access(
                    "/usr/local" if os.name != "nt" else "C:\\Windows", os.W_OK
                ),
                "can_execute": True,  # Basic assumption
                "home_writable": os.access(Path.home(), os.W_OK),
            }

            # Platform-specific security info
            firewall_status = self._get_firewall_status()
            antivirus_status = self._get_antivirus_status()

            # Encryption support
            encryption_support = {
                "ssl_available": self._check_ssl_support(),
                "cryptography_available": self._check_module_available("cryptography"),
                "keyring_available": self._check_module_available("keyring"),
            }

            # Secure boot (Linux/Windows specific)
            secure_boot = self._check_secure_boot()

            return SecurityInfo(
                user_permissions=user_permissions,
                firewall_status=firewall_status,
                antivirus_status=antivirus_status,
                encryption_support=encryption_support,
                secure_boot=secure_boot,
            )

        except Exception as e:
            logger.error(f"Error getting security info: {e}")
            raise

    def get_environment_variables(
        self, include_sensitive: bool = False
    ) -> Dict[str, str]:
        """Get environment variables."""
        try:
            env_vars = {}
            sensitive_patterns = [
                "key",
                "secret",
                "token",
                "password",
                "auth",
                "credential",
            ]

            for key, value in os.environ.items():
                if include_sensitive:
                    env_vars[key] = value
                else:
                    # Filter out potentially sensitive variables
                    is_sensitive = any(
                        pattern.lower() in key.lower() for pattern in sensitive_patterns
                    )
                    if not is_sensitive:
                        env_vars[key] = value
                    else:
                        env_vars[key] = "[REDACTED]"

            return env_vars

        except Exception as e:
            logger.error(f"Error getting environment variables: {e}")
            return {}

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health indicators."""
        try:
            health = {
                "cpu_temperature": self._get_cpu_temperature(),
                "disk_health": self._check_disk_health(),
                "memory_pressure": self._check_memory_pressure(),
                "network_latency": self._check_network_latency(),
                "system_errors": self._check_system_errors(),
                "overall_status": "healthy",  # Will be determined based on other metrics
            }

            # Determine overall status
            issues = []
            if health["memory_pressure"] and health["memory_pressure"] > 80:
                issues.append("high_memory_usage")
            if health["disk_health"] and any(
                disk["percent"] > 90 for disk in health["disk_health"].values()
            ):
                issues.append("low_disk_space")
            if health["network_latency"] and health["network_latency"] > 1000:
                issues.append("high_network_latency")

            if issues:
                health["overall_status"] = "warning" if len(issues) <= 2 else "critical"
                health["issues"] = issues

            return health

        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {"overall_status": "unknown", "error": str(e)}

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        try:
            # CPU usage per core
            cpu_per_core = psutil.cpu_percent(percpu=True, interval=1)

            # Memory details
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk I/O
            disk_io = psutil.disk_io_counters()

            # Network I/O
            network_io = psutil.net_io_counters()

            # Process counts
            process_counts = {
                "total": len(psutil.pids()),
                "running": len(
                    [
                        p
                        for p in psutil.process_iter()
                        if p.status() == psutil.STATUS_RUNNING
                    ]
                ),
                "sleeping": len(
                    [
                        p
                        for p in psutil.process_iter()
                        if p.status() == psutil.STATUS_SLEEPING
                    ]
                ),
            }

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "overall_percent": psutil.cpu_percent(),
                    "per_core": cpu_per_core,
                    "load_average": (
                        os.getloadavg() if hasattr(os, "getloadavg") else None
                    ),
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent,
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_percent": swap.percent,
                },
                "disk_io": {
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0,
                },
                "network_io": {
                    "bytes_sent": network_io.bytes_sent if network_io else 0,
                    "bytes_recv": network_io.bytes_recv if network_io else 0,
                    "packets_sent": network_io.packets_sent if network_io else 0,
                    "packets_recv": network_io.packets_recv if network_io else 0,
                },
                "processes": process_counts,
            }

        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {"error": str(e)}

    def monitor_resources(
        self, duration: int = 60, interval: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Monitor system resources over time.

        Args:
            duration: Total monitoring duration in seconds
            interval: Sampling interval in seconds

        Returns:
            List of resource usage snapshots
        """
        try:
            logger.info(
                f"Starting resource monitoring for {duration}s with {interval}s intervals"
            )

            snapshots = []
            start_time = time.time()

            while time.time() - start_time < duration:
                snapshot = self.get_resource_usage()
                snapshots.append(snapshot)

                time.sleep(interval)

            logger.info(
                f"Resource monitoring completed. Collected {len(snapshots)} snapshots"
            )
            return snapshots

        except Exception as e:
            logger.error(f"Error during resource monitoring: {e}")
            raise

    def get_system_summary(self) -> str:
        """Get a human-readable system summary."""
        try:
            info = self.get_system_info(include_sensitive=False)

            summary_lines = [
                "=== SYSTEM SUMMARY ===",
                f"OS: {info['os_info']['system']} {info['os_info']['release']}",
                f"CPU: {info['system_specs']['cpu_count']} cores",
                f"Memory: {info['system_specs']['memory_total'] // (1024**3)} GB total, "
                f"{info['system_specs']['memory_available'] // (1024**3)} GB available",
                f"Python: {info['os_info']['python_version']}",
                f"Hostname: {info['network_info']['hostname']}",
                f"Internet: {'Connected' if info['network_info']['internet_connectivity'] else 'Disconnected'}",
                f"System Health: {info['system_health']['overall_status'].upper()}",
                "",
                "=== DEVELOPMENT ENVIRONMENT ===",
                f"Shell: {info['development_env']['shell']}",
                f"Editors: {', '.join(info['development_env']['editors_available'])}",
                f"Version Control: {', '.join(info['development_env']['version_control'].keys())}",
                f"Package Managers: {', '.join(info['development_env']['package_managers'].keys())}",
                "",
                "=== RESOURCE USAGE ===",
                f"CPU: {info['resource_usage']['cpu']['overall_percent']:.1f}%",
                f"Memory: {info['resource_usage']['memory']['percent']:.1f}%",
                f"Processes: {info['resource_usage']['processes']['total']} total, "
                f"{info['resource_usage']['processes']['running']} running",
            ]

            return "\n".join(summary_lines)

        except Exception as e:
            logger.error(f"Error generating system summary: {e}")
            return f"Error generating system summary: {e}"

    # Helper methods

    def _get_cached(self, key: str) -> Any:
        """Get cached value if still valid."""
        if key in self._cache:
            timestamp, value = self._cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                return value
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        """Set cached value with timestamp."""
        self._cache[key] = (datetime.now(), value)

    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Get GPU information (basic detection)."""
        gpu_info = []

        try:
            # Try nvidia-smi for NVIDIA GPUs
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(", ")
                        if len(parts) >= 3:
                            gpu_info.append(
                                {
                                    "name": parts[0],
                                    "memory_total": int(parts[1]),
                                    "memory_used": int(parts[2]),
                                    "vendor": "NVIDIA",
                                }
                            )
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        # If no NVIDIA GPUs found, try basic detection
        if not gpu_info:
            try:
                if platform.system() == "Linux":
                    result = subprocess.run(
                        ["lspci"], capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split("\n"):
                            if "VGA" in line or "Display" in line:
                                gpu_info.append(
                                    {
                                        "name": (
                                            line.split(": ")[-1]
                                            if ": " in line
                                            else line
                                        ),
                                        "vendor": "Unknown",
                                        "memory_total": None,
                                        "memory_used": None,
                                    }
                                )
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                subprocess.SubprocessError,
            ):
                pass

        return gpu_info

    def _test_internet_connectivity(self) -> bool:
        """Test internet connectivity."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def _get_dns_servers(self) -> List[str]:
        """Get DNS servers (basic detection)."""
        dns_servers = []

        try:
            if platform.system() == "Linux":
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            dns_servers.append(line.split()[1])
            elif platform.system() == "Windows":
                result = subprocess.run(
                    ["nslookup", "localhost"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                # Parse nslookup output for DNS servers
                for line in result.stdout.split("\n"):
                    if "Server:" in line:
                        server = line.split(":")[-1].strip()
                        if server and server != "localhost":
                            dns_servers.append(server)
        except (FileNotFoundError, subprocess.SubprocessError, PermissionError):
            pass

        return dns_servers

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run([command, "--version"], capture_output=True, timeout=5)
            return True
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            try:
                subprocess.run(["which", command], capture_output=True, timeout=5)
                return True
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                subprocess.SubprocessError,
            ):
                return False

    def _get_command_version(
        self, command: str, args: List[str] = None
    ) -> Optional[str]:
        """Get version of a command."""
        if args is None:
            args = ["--version"]

        try:
            result = subprocess.run(
                [command] + args, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Extract version from output (first line usually contains version)
                output = result.stdout.strip() or result.stderr.strip()
                return output.split("\n")[0] if output else None
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        return None

    def _get_docker_info(self) -> Optional[Dict[str, Any]]:
        """Get Docker information if available."""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                docker_info = {"version": result.stdout.strip()}

                # Get Docker system info
                result = subprocess.run(
                    ["docker", "system", "info", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    try:
                        system_info = json.loads(result.stdout)
                        docker_info.update(
                            {
                                "containers": system_info.get("Containers", 0),
                                "images": system_info.get("Images", 0),
                                "server_version": system_info.get("ServerVersion"),
                                "storage_driver": system_info.get("Driver"),
                            }
                        )
                    except json.JSONDecodeError:
                        pass

                return docker_info
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        return None

    def _is_admin(self) -> bool:
        """Check if running with admin/root privileges."""
        try:
            if os.name == "nt":
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False

    def _get_firewall_status(self) -> Optional[str]:
        """Get firewall status (platform-specific)."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["netsh", "advfirewall", "show", "allprofiles", "state"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    return "enabled" if "ON" in result.stdout else "disabled"
            elif platform.system() == "Linux":
                # Try ufw first
                result = subprocess.run(
                    ["ufw", "status"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return (
                        "enabled" if "active" in result.stdout.lower() else "disabled"
                    )

                # Try iptables
                result = subprocess.run(
                    ["iptables", "-L"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return "enabled" if result.stdout.strip() else "disabled"
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        return None

    def _get_antivirus_status(self) -> Optional[str]:
        """Get antivirus status (Windows-specific)."""
        if platform.system() != "Windows":
            return None

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-MpComputerStatus | Select-Object AntivirusEnabled",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return "enabled" if "True" in result.stdout else "disabled"
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        return None

    def _check_ssl_support(self) -> bool:
        """Check if SSL/TLS support is available."""
        try:
            pass

            return True
        except ImportError:
            return False

    def _check_module_available(self, module_name: str) -> bool:
        """Check if a Python module is available."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def _check_secure_boot(self) -> Optional[bool]:
        """Check if Secure Boot is enabled (Linux/Windows)."""
        try:
            if platform.system() == "Linux":
                # Check for Secure Boot on Linux
                secure_boot_path = "/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c"
                if os.path.exists(secure_boot_path):
                    with open(secure_boot_path, "rb") as f:
                        data = f.read()
                        return len(data) > 4 and data[4] == 1
            elif platform.system() == "Windows":
                # Check Secure Boot on Windows
                result = subprocess.run(
                    ["powershell", "-Command", "Confirm-SecureBootUEFI"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    return "True" in result.stdout
        except (FileNotFoundError, PermissionError, subprocess.SubprocessError):
            pass

        return None

    def _get_cpu_temperature(self) -> Optional[Dict[str, float]]:
        """Get CPU temperature if available."""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    cpu_temps = {}
                    for name, entries in temps.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            for entry in entries:
                                cpu_temps[f"{name}_{entry.label or 'temp'}"] = (
                                    entry.current
                                )
                    return cpu_temps if cpu_temps else None
        except:
            pass

        return None

    def _check_disk_health(self) -> Dict[str, Dict[str, Any]]:
        """Check disk health and usage."""
        disk_health = {}

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_health[partition.device] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": round((usage.used / usage.total) * 100, 2),
                    "status": (
                        "warning" if usage.used / usage.total > 0.9 else "healthy"
                    ),
                }
            except (PermissionError, OSError):
                continue

        return disk_health

    def _check_memory_pressure(self) -> float:
        """Check memory pressure percentage."""
        memory = psutil.virtual_memory()
        return memory.percent

    def _check_network_latency(self) -> Optional[float]:
        """Check network latency to a common server."""
        try:
            start_time = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except OSError:
            return None

    def _check_system_errors(self) -> List[str]:
        """Check for recent system errors (basic implementation)."""
        errors = []

        try:
            # Check for high CPU usage processes
            for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    if proc.info["cpu_percent"] > 90:
                        errors.append(
                            f"High CPU usage: {proc.info['name']} ({proc.info['cpu_percent']:.1f}%)"
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Check for memory issues
            memory = psutil.virtual_memory()
            if memory.percent > 95:
                errors.append(f"Critical memory usage: {memory.percent:.1f}%")

            # Check for disk space issues
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    if (usage.used / usage.total) > 0.95:
                        errors.append(
                            f"Critical disk usage: {partition.device} ({(usage.used / usage.total) * 100:.1f}%)"
                        )
                except (PermissionError, OSError):
                    continue

        except Exception as e:
            errors.append(f"Error checking system status: {e}")

        return errors
