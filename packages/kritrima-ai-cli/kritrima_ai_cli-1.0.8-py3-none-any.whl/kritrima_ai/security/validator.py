"""
Security validators for input validation and safety checks.

This module provides comprehensive validation for paths, commands, and other
security-sensitive inputs to prevent various attack vectors.
"""

import ipaddress
import os
import re
import shlex
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""


class PathValidator:
    """
    Validates file and directory paths for security.

    Prevents directory traversal attacks, access to sensitive files,
    and other path-based security issues.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize path validator.

        Args:
            config: Application configuration
        """
        self.config = config

        # Dangerous path patterns
        self.dangerous_patterns = [
            r"\.\.[\\/]",  # Directory traversal
            r"[\\/]\.\.[\\/]",  # Directory traversal
            r"^\.\.[\\/]",  # Directory traversal at start
            r"[\\/]\.",  # Hidden files/directories
            r"~[\\/]",  # Home directory shortcuts
            r"\$\{.*\}",  # Variable expansion
            r"%.*%",  # Windows environment variables
        ]

        # Sensitive directories (platform-specific)
        self.sensitive_dirs = self._get_sensitive_directories()

        # Allowed file extensions for reading
        self.safe_read_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".ts",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
            ".xml",
            ".csv",
            ".log",
            ".conf",
            ".cfg",
            ".ini",
            ".toml",
            ".rst",
            ".sh",
            ".bat",
            ".ps1",
            ".sql",
        }

        # Dangerous file extensions
        self.dangerous_extensions = {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".app",
            ".deb",
            ".rpm",
            ".msi",
            ".pkg",
            ".dmg",
            ".iso",
            ".img",
            ".bin",
            ".com",
            ".scr",
            ".pif",
            ".vbs",
            ".jar",
            ".class",
        }

    def _get_sensitive_directories(self) -> Set[Path]:
        """Get platform-specific sensitive directories."""
        sensitive = set()

        # Unix-like systems
        if os.name == "posix":
            sensitive.update(
                [
                    Path("/etc"),
                    Path("/usr/bin"),
                    Path("/usr/sbin"),
                    Path("/bin"),
                    Path("/sbin"),
                    Path("/boot"),
                    Path("/sys"),
                    Path("/proc"),
                    Path("/dev"),
                    Path("/root"),
                    Path("/var/log"),
                    Path("/var/run"),
                    Path("/tmp"),  # Often writable but can be dangerous
                ]
            )

        # Windows
        elif os.name == "nt":
            sensitive.update(
                [
                    Path("C:/Windows"),
                    Path("C:/Program Files"),
                    Path("C:/Program Files (x86)"),
                    Path("C:/ProgramData"),
                    Path("C:/Users/All Users"),
                    Path("C:/System Volume Information"),
                    Path("C:/Recovery"),
                    Path("C:/Boot"),
                ]
            )

        return sensitive

    def validate_path(
        self, path: str, operation: str = "read", allow_create: bool = False
    ) -> Path:
        """
        Validate a file or directory path.

        Args:
            path: Path to validate
            operation: Operation type ("read", "write", "execute")
            allow_create: Whether to allow creation of new files

        Returns:
            Validated and resolved Path object

        Raises:
            ValidationError: If path is invalid or dangerous
        """
        try:
            # Basic input validation
            if not path or not isinstance(path, str):
                raise ValidationError("Path must be a non-empty string")

            if len(path) > 4096:  # Reasonable path length limit
                raise ValidationError("Path too long")

            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    raise ValidationError(f"Dangerous path pattern detected: {pattern}")

            # Convert to Path object and resolve
            path_obj = Path(path)

            # Check if path exists or if creation is allowed
            if not path_obj.exists() and not allow_create:
                if operation in ["read", "execute"]:
                    raise ValidationError(f"Path does not exist: {path}")

            # Resolve the path (this will raise an exception for invalid paths)
            try:
                resolved_path = path_obj.resolve()
            except (OSError, RuntimeError) as e:
                raise ValidationError(f"Cannot resolve path: {e}")

            # Check if path is within sensitive directories
            self._check_sensitive_directories(resolved_path, operation)

            # Check file extension for safety
            if resolved_path.is_file() or (allow_create and resolved_path.suffix):
                self._check_file_extension(resolved_path, operation)

            # Additional checks based on operation
            if operation == "write":
                self._validate_write_operation(resolved_path, allow_create)
            elif operation == "execute":
                self._validate_execute_operation(resolved_path)

            logger.debug(f"Path validated: {resolved_path} (operation: {operation})")
            return resolved_path

        except Exception as e:
            logger.warning(f"Path validation failed for '{path}': {e}")
            raise ValidationError(f"Path validation failed: {e}")

    def _check_sensitive_directories(self, path: Path, operation: str) -> None:
        """Check if path is within sensitive directories."""
        for sensitive_dir in self.sensitive_dirs:
            try:
                path.relative_to(sensitive_dir)
                if operation in ["write", "execute"]:
                    raise ValidationError(
                        f"Access denied to sensitive directory: {sensitive_dir}"
                    )
                elif operation == "read":
                    logger.warning(f"Reading from sensitive directory: {sensitive_dir}")
                break
            except ValueError:
                continue

    def _check_file_extension(self, path: Path, operation: str) -> None:
        """Check file extension for safety."""
        extension = path.suffix.lower()

        if extension in self.dangerous_extensions:
            raise ValidationError(f"Dangerous file extension: {extension}")

        if operation == "read" and extension not in self.safe_read_extensions:
            logger.warning(
                f"Reading file with potentially unsafe extension: {extension}"
            )

    def _validate_write_operation(self, path: Path, allow_create: bool) -> None:
        """Validate write operation specific checks."""
        # Check if parent directory is writable
        parent = path.parent
        if not parent.exists():
            if not allow_create:
                raise ValidationError(f"Parent directory does not exist: {parent}")
        elif not os.access(parent, os.W_OK):
            raise ValidationError(f"Parent directory not writable: {parent}")

        # Check if file is writable (if it exists)
        if path.exists() and not os.access(path, os.W_OK):
            raise ValidationError(f"File not writable: {path}")

    def _validate_execute_operation(self, path: Path) -> None:
        """Validate execute operation specific checks."""
        if not path.exists():
            raise ValidationError(f"Executable does not exist: {path}")

        if not path.is_file():
            raise ValidationError(f"Path is not a file: {path}")

        if not os.access(path, os.X_OK):
            raise ValidationError(f"File not executable: {path}")


class CommandValidator:
    """
    Validates shell commands for security.

    Prevents command injection, dangerous commands, and other
    command-based security issues.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize command validator.

        Args:
            config: Application configuration
        """
        self.config = config

        # Dangerous command patterns
        self.dangerous_patterns = [
            r"[;&|`$()]",  # Command injection characters
            r">\s*/dev/",  # Writing to device files
            r"<\s*/dev/",  # Reading from device files
            r"\$\{.*\}",  # Variable expansion
            r"`.*`",  # Command substitution
            r"\$\(.*\)",  # Command substitution
            r"\\x[0-9a-fA-F]{2}",  # Hex escape sequences
            r"\\[0-7]{3}",  # Octal escape sequences
        ]

        # Commands that should never be allowed
        self.forbidden_commands = {
            "rm",
            "del",
            "format",
            "fdisk",
            "mkfs",
            "dd",
            "shred",
            "sudo",
            "su",
            "passwd",
            "chown",
            "chmod",
            "chgrp",
            "mount",
            "umount",
            "kill",
            "killall",
            "pkill",
            "shutdown",
            "reboot",
            "halt",
            "poweroff",
            "init",
            "crontab",
            "at",
            "batch",
            "systemctl",
            "service",
            "iptables",
            "ufw",
            "firewall-cmd",
            "netsh",
        }

        # Commands that require special approval
        self.restricted_commands = {
            "mv",
            "move",
            "cp",
            "copy",
            "mkdir",
            "rmdir",
            "rd",
            "wget",
            "curl",
            "git",
            "pip",
            "npm",
            "apt",
            "yum",
            "brew",
            "choco",
            "winget",
            "docker",
            "kubectl",
        }

    def validate_command(self, command: str) -> Tuple[List[str], str]:
        """
        Validate a shell command.

        Args:
            command: Command string to validate

        Returns:
            Tuple of (parsed_command_list, risk_level)

        Raises:
            ValidationError: If command is invalid or dangerous
        """
        try:
            # Basic input validation
            if not command or not isinstance(command, str):
                raise ValidationError("Command must be a non-empty string")

            if len(command) > 8192:  # Reasonable command length limit
                raise ValidationError("Command too long")

            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    raise ValidationError(
                        f"Dangerous command pattern detected: {pattern}"
                    )

            # Parse command safely
            try:
                parsed_command = shlex.split(command)
            except ValueError as e:
                raise ValidationError(f"Cannot parse command: {e}")

            if not parsed_command:
                raise ValidationError("Empty command after parsing")

            # Get the base command
            base_command = os.path.basename(parsed_command[0]).lower()

            # Check against forbidden commands
            if base_command in self.forbidden_commands:
                raise ValidationError(f"Forbidden command: {base_command}")

            # Determine risk level
            risk_level = self._assess_risk_level(base_command, parsed_command)

            # Additional validation based on command type
            self._validate_specific_command(base_command, parsed_command)

            logger.debug(f"Command validated: {command} (risk: {risk_level})")
            return parsed_command, risk_level

        except Exception as e:
            logger.warning(f"Command validation failed for '{command}': {e}")
            raise ValidationError(f"Command validation failed: {e}")

    def _assess_risk_level(self, base_command: str, parsed_command: List[str]) -> str:
        """Assess the risk level of a command."""
        # Check if it's a safe command
        if base_command in self.config.security.safe_commands:
            return "low"

        # Check if it's a restricted command
        if base_command in self.restricted_commands:
            return "medium"

        # Check for dangerous flags or arguments
        dangerous_flags = ["-f", "--force", "-r", "--recursive", "--delete"]
        for arg in parsed_command[1:]:
            if arg.lower() in dangerous_flags:
                return "high"

        # Default risk level
        return "medium"

    def _validate_specific_command(
        self, base_command: str, parsed_command: List[str]
    ) -> None:
        """Validate specific command types."""
        if base_command in ["wget", "curl"]:
            self._validate_network_command(parsed_command)
        elif base_command in ["git"]:
            self._validate_git_command(parsed_command)
        elif base_command in ["pip", "npm"]:
            self._validate_package_command(parsed_command)

    def _validate_network_command(self, parsed_command: List[str]) -> None:
        """Validate network-related commands."""
        # Look for URLs in arguments
        for arg in parsed_command[1:]:
            if arg.startswith(("http://", "https://", "ftp://")):
                try:
                    parsed_url = urlparse(arg)
                    if not parsed_url.netloc:
                        raise ValidationError(f"Invalid URL: {arg}")

                    # Check for localhost/private IPs
                    try:
                        ip = ipaddress.ip_address(parsed_url.hostname)
                        if ip.is_private or ip.is_loopback:
                            logger.warning(
                                f"Network command accessing private/local IP: {ip}"
                            )
                    except (ValueError, TypeError):
                        pass  # Not an IP address, hostname is fine

                except Exception as e:
                    raise ValidationError(f"Invalid URL in command: {e}")

    def _validate_git_command(self, parsed_command: List[str]) -> None:
        """Validate git commands."""
        if len(parsed_command) < 2:
            return

        git_subcommand = parsed_command[1].lower()

        # Dangerous git operations
        dangerous_git_ops = ["reset", "clean", "gc", "prune", "reflog"]
        if git_subcommand in dangerous_git_ops:
            logger.warning(f"Potentially dangerous git operation: {git_subcommand}")

    def _validate_package_command(self, parsed_command: List[str]) -> None:
        """Validate package manager commands."""
        if len(parsed_command) < 2:
            return

        subcommand = parsed_command[1].lower()

        # Installation commands require approval
        install_commands = ["install", "add", "update", "upgrade"]
        if subcommand in install_commands:
            logger.info(f"Package installation command detected: {subcommand}")


class SecurityValidator:
    """
    Main security validator that coordinates all validation checks.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize security validator.

        Args:
            config: Application configuration
        """
        self.config = config
        self.path_validator = PathValidator(config)
        self.command_validator = CommandValidator(config)

        logger.info("Security validator initialized")

    def validate_file_operation(
        self, operation: str, path: str, content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a file operation.

        Args:
            operation: Operation type ("read", "write", "delete", etc.)
            path: File path
            content: File content (for write operations)

        Returns:
            Validation result with risk assessment
        """
        try:
            # Validate path
            validated_path = self.path_validator.validate_path(
                path, operation, allow_create=(operation == "write")
            )

            # Assess risk level
            risk_level = self._assess_file_operation_risk(
                operation, validated_path, content
            )

            return {
                "valid": True,
                "path": validated_path,
                "risk_level": risk_level,
                "warnings": [],
            }

        except ValidationError as e:
            return {"valid": False, "error": str(e), "risk_level": "high"}

    def validate_command_execution(self, command: str) -> Dict[str, Any]:
        """
        Validate a command execution.

        Args:
            command: Command to validate

        Returns:
            Validation result with risk assessment
        """
        try:
            # Validate command
            parsed_command, risk_level = self.command_validator.validate_command(
                command
            )

            return {
                "valid": True,
                "command": parsed_command,
                "risk_level": risk_level,
                "warnings": [],
            }

        except ValidationError as e:
            return {"valid": False, "error": str(e), "risk_level": "critical"}

    def _assess_file_operation_risk(
        self, operation: str, path: Path, content: Optional[str]
    ) -> str:
        """Assess risk level for file operations."""
        # Delete operations are always high risk
        if operation == "delete":
            return "high"

        # Writing to system directories
        if operation == "write":
            system_dirs = [
                "/usr",
                "/etc",
                "/bin",
                "/sbin",
                "C:\\Windows",
                "C:\\Program Files",
            ]
            for sys_dir in system_dirs:
                try:
                    path.relative_to(Path(sys_dir))
                    return "high"
                except ValueError:
                    continue

        # Check file extension
        if path.suffix.lower() in [".exe", ".dll", ".so", ".dylib"]:
            return "high"

        # Check content for dangerous patterns (if provided)
        if content and operation == "write":
            dangerous_content_patterns = [
                r"eval\s*\(",
                r"exec\s*\(",
                r"system\s*\(",
                r"shell_exec\s*\(",
                r"passthru\s*\(",
                r"`[^`]*`",  # Backticks
                r"\$\([^)]*\)",  # Command substitution
            ]

            for pattern in dangerous_content_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return "high"

        return "medium" if operation == "write" else "low"

    async def validate_tool_execution(
        self, tool_name: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate a tool execution request.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            context: Additional context information
            
        Returns:
            Validation result with risk assessment
        """
        try:
            # Initialize result
            result = {
                "valid": True,
                "reason": "",
                "risk_level": "low",
                "warnings": []
            }
            
            # Validate based on tool type
            if tool_name in ["file_write", "file_create", "write_file", "create_file"]:
                # File write operations
                path = arguments.get("path", arguments.get("file_path", ""))
                content = arguments.get("content", "")
                file_result = self.validate_file_operation("write", path, content)
                
                if not file_result["valid"]:
                    result["valid"] = False
                    result["reason"] = file_result.get("error", "File operation validation failed")
                    result["risk_level"] = file_result.get("risk_level", "high")
                else:
                    result["risk_level"] = file_result.get("risk_level", "medium")
                    
            elif tool_name in ["file_read", "read_file"]:
                # File read operations
                path = arguments.get("path", arguments.get("file_path", ""))
                file_result = self.validate_file_operation("read", path)
                
                if not file_result["valid"]:
                    result["valid"] = False
                    result["reason"] = file_result.get("error", "File operation validation failed")
                    result["risk_level"] = file_result.get("risk_level", "high")
                else:
                    result["risk_level"] = file_result.get("risk_level", "low")
                    
            elif tool_name in ["file_delete", "delete_file", "remove_file"]:
                # File delete operations
                path = arguments.get("path", arguments.get("file_path", ""))
                file_result = self.validate_file_operation("delete", path)
                
                if not file_result["valid"]:
                    result["valid"] = False
                    result["reason"] = file_result.get("error", "File operation validation failed")
                    result["risk_level"] = "high"
                else:
                    result["risk_level"] = "high"  # Deletions are always high risk
                    
            elif tool_name in ["command_execution", "shell_command", "execute_command", "run_command"]:
                # Command execution
                command = arguments.get("command", "")
                cmd_result = self.validate_command_execution(command)
                
                if not cmd_result["valid"]:
                    result["valid"] = False
                    result["reason"] = cmd_result.get("error", "Command validation failed")
                    result["risk_level"] = cmd_result.get("risk_level", "critical")
                else:
                    result["risk_level"] = cmd_result.get("risk_level", "medium")
                    
            elif tool_name in ["directory_list", "list_directory", "ls", "dir"]:
                # Directory listing - generally safe
                path = arguments.get("path", ".")
                try:
                    self.path_validator.validate_path(path, "read")
                    result["risk_level"] = "low"
                except ValidationError as e:
                    result["valid"] = False
                    result["reason"] = str(e)
                    result["risk_level"] = "medium"
                    
            elif tool_name in ["system_info", "get_system_info"]:
                # System information - generally safe but can reveal sensitive info
                result["risk_level"] = "low"
                result["warnings"].append("System information may reveal sensitive details")
                
            else:
                # Unknown tool - treat as medium risk
                result["risk_level"] = "medium"
                result["warnings"].append(f"Unknown tool type: {tool_name}")
                logger.warning(f"Validation requested for unknown tool: {tool_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating tool execution: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "risk_level": "critical"
            }
