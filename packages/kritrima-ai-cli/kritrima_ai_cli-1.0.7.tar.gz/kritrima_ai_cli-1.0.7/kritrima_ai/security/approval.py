"""
Security approval system for Kritrima AI CLI.

This module implements a comprehensive approval system for tool execution and
command approval with different approval modes and security policies.
"""

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.security.validator import SecurityValidator
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ApprovalMode(Enum):
    """Approval modes for tool execution."""

    SUGGEST = "suggest"  # Manual approval for all actions
    AUTO_EDIT = "auto_edit"  # Auto approve file edits, manual for commands
    FULL_AUTO = "full_auto"  # Auto approve everything (with safety checks)


class ApprovalDecision(Enum):
    """Approval decision types."""

    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    ALWAYS_ALLOW = "always_allow"
    ALWAYS_DENY = "always_deny"


@dataclass
class ApprovalRequest:
    """Request for tool execution approval."""

    request_id: str
    tool_name: str
    arguments: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: float
    risk_level: str
    explanation: str
    auto_approvable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "context": self.context,
            "timestamp": self.timestamp,
            "risk_level": self.risk_level,
            "explanation": self.explanation,
            "auto_approvable": self.auto_approvable,
        }


@dataclass
class ApprovalResult:
    """Result of approval request."""

    approved: bool
    decision: ApprovalDecision
    reason: str
    auto_approved: bool = False
    remember_decision: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ApprovalPolicy:
    """Approval policy configuration."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.mode = ApprovalMode(config.approval_mode)

        # Risk-based approval rules
        self.high_risk_commands = {
            "rm",
            "del",
            "rmdir",
            "format",
            "fdisk",
            "dd",
            "sudo",
            "su",
            "chmod +x",
            "chown",
            "systemctl",
            "service",
            "kill",
            "killall",
            "mv /*",
            "cp /* /",
            "wget",
            "curl",
            "ssh",
            "scp",
            "rsync",
        }

        self.medium_risk_commands = {
            "git reset --hard",
            "git clean -fd",
            "npm install",
            "pip install",
            "make install",
            "cargo install",
            "go install",
            "docker run",
            "docker build",
            "kubectl",
            "terraform",
        }

        self.safe_commands = {
            "ls",
            "dir",
            "pwd",
            "cd",
            "cat",
            "type",
            "head",
            "tail",
            "grep",
            "find",
            "locate",
            "which",
            "where",
            "echo",
            "printf",
            "date",
            "ps",
            "top",
            "htop",
            "df",
            "du",
            "free",
            "uname",
            "whoami",
            "git status",
            "git log",
            "git diff",
            "git branch",
            "git show",
        }

        # File operation rules
        self.protected_paths = {
            "/etc",
            "/boot",
            "/sys",
            "/proc",
            "/dev",
            "C:\\Windows",
            "C:\\Program Files",
            "/System",
            "/Library/System",
        }

        self.auto_approve_extensions = {
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
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
        }

    def assess_risk(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Assess risk level of tool execution."""
        if tool_name in ["file_write", "file_create"]:
            file_path = arguments.get("path", "")
            if any(protected in file_path for protected in self.protected_paths):
                return "HIGH"
            if Path(file_path).suffix in self.auto_approve_extensions:
                return "LOW"
            return "MEDIUM"

        elif tool_name in ["command_execution", "shell_command"]:
            command = arguments.get("command", "")
            if any(risk_cmd in command for risk_cmd in self.high_risk_commands):
                return "HIGH"
            if any(risk_cmd in command for risk_cmd in self.medium_risk_commands):
                return "MEDIUM"
            if any(safe_cmd in command for safe_cmd in self.safe_commands):
                return "LOW"
            return "MEDIUM"

        elif tool_name in ["file_delete", "directory_delete"]:
            return "HIGH"

        elif tool_name in ["file_read", "directory_list", "system_info"]:
            return "LOW"

        return "MEDIUM"

    def is_auto_approvable(
        self, tool_name: str, arguments: Dict[str, Any], risk_level: str
    ) -> bool:
        """Check if tool execution can be auto-approved."""
        if self.mode == ApprovalMode.SUGGEST:
            return False

        if self.mode == ApprovalMode.FULL_AUTO:
            return risk_level != "HIGH"  # Auto approve everything except high risk

        if self.mode == ApprovalMode.AUTO_EDIT:
            # Auto approve file operations but not commands
            if tool_name in [
                "file_read",
                "file_write",
                "file_create",
                "directory_list",
            ]:
                return risk_level in ["LOW", "MEDIUM"]
            return False

        return False


class ApprovalSystem:
    """
    Comprehensive approval system for tool execution.

    Manages approval requests, user interactions, and approval policies
    with support for different approval modes and security levels.
    """

    def __init__(self, config: AppConfig, approval_callback: Optional[Callable] = None):
        """
        Initialize the approval system.

        Args:
            config: Application configuration
            approval_callback: Optional callback for approval requests
        """
        self.config = config
        self.approval_callback = approval_callback
        self.policy = ApprovalPolicy(config)
        self.validator = SecurityValidator(config)

        # Approval state
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, str] = (
            {}
        )  # tool_name -> always_allow/always_deny

        # Performance tracking
        self.total_requests = 0
        self.auto_approved = 0
        self.manual_approved = 0
        self.denied = 0

        logger.info(f"Approval system initialized with mode: {self.policy.mode.value}")

    async def request_approval(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ApprovalResult:
        """
        Request approval for tool execution.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            context: Additional context information

        Returns:
            ApprovalResult indicating approval status
        """
        try:
            self.total_requests += 1
            request_id = f"approval_{int(time.time() * 1000)}"

            if context is None:
                context = {}

            # Check user preferences first
            preference = self.user_preferences.get(tool_name)
            if preference == "always_allow":
                self.auto_approved += 1
                return ApprovalResult(
                    approved=True,
                    decision=ApprovalDecision.ALWAYS_ALLOW,
                    reason="User preference: always allow",
                    auto_approved=True,
                )
            elif preference == "always_deny":
                self.denied += 1
                return ApprovalResult(
                    approved=False,
                    decision=ApprovalDecision.ALWAYS_DENY,
                    reason="User preference: always deny",
                )

            # Assess risk level
            risk_level = self.policy.assess_risk(tool_name, arguments)

            # Security validation
            validation_result = await self.validator.validate_tool_execution(
                tool_name, arguments, context
            )

            if not validation_result.valid:
                self.denied += 1
                return ApprovalResult(
                    approved=False,
                    decision=ApprovalDecision.DENIED,
                    reason=f"Security validation failed: {validation_result.reason}",
                )

            # Check if auto-approvable
            auto_approvable = self.policy.is_auto_approvable(
                tool_name, arguments, risk_level
            )

            if auto_approvable:
                self.auto_approved += 1
                result = ApprovalResult(
                    approved=True,
                    decision=ApprovalDecision.APPROVED,
                    reason=f"Auto-approved: {risk_level.lower()} risk",
                    auto_approved=True,
                )

                # Log approval
                await self._log_approval(request_id, tool_name, arguments, result)
                return result

            # Create approval request
            approval_request = ApprovalRequest(
                request_id=request_id,
                tool_name=tool_name,
                arguments=arguments,
                context=context,
                timestamp=time.time(),
                risk_level=risk_level,
                explanation=self._generate_explanation(
                    tool_name, arguments, risk_level
                ),
                auto_approvable=auto_approvable,
            )

            # Store pending request
            self.pending_requests[request_id] = approval_request

            # Request user approval
            result = await self._request_user_approval(approval_request)

            # Update counters
            if result.approved:
                self.manual_approved += 1
            else:
                self.denied += 1

            # Log approval
            await self._log_approval(request_id, tool_name, arguments, result)

            # Update user preferences if requested
            if result.remember_decision:
                if result.approved:
                    self.user_preferences[tool_name] = "always_allow"
                else:
                    self.user_preferences[tool_name] = "always_deny"

            # Remove from pending
            self.pending_requests.pop(request_id, None)

            return result

        except Exception as e:
            logger.error(f"Error in approval request: {e}")
            self.denied += 1
            return ApprovalResult(
                approved=False,
                decision=ApprovalDecision.DENIED,
                reason=f"Approval system error: {str(e)}",
            )

    async def _request_user_approval(self, request: ApprovalRequest) -> ApprovalResult:
        """
        Request approval from the user.

        Args:
            request: Approval request

        Returns:
            ApprovalResult from user
        """
        if self.approval_callback:
            # Use provided callback
            try:
                return await self.approval_callback(request)
            except Exception as e:
                logger.error(f"Approval callback error: {e}")
                return ApprovalResult(
                    approved=False,
                    decision=ApprovalDecision.DENIED,
                    reason=f"Approval callback failed: {str(e)}",
                )
        else:
            # Default console-based approval
            return await self._console_approval(request)

    async def _console_approval(self, request: ApprovalRequest) -> ApprovalResult:
        """
        Console-based approval interface.

        Args:
            request: Approval request

        Returns:
            ApprovalResult from console interaction
        """
        print(f"\n{'='*60}")
        print(f"APPROVAL REQUIRED - {request.risk_level} RISK")
        print(f"{'='*60}")
        print(f"Tool: {request.tool_name}")
        print(f"Risk Level: {request.risk_level}")
        print(f"Explanation: {request.explanation}")
        print(f"\nArguments:")
        for key, value in request.arguments.items():
            print(f"  {key}: {value}")

        if request.context:
            print(f"\nContext:")
            for key, value in request.context.items():
                if len(str(value)) > 100:
                    print(f"  {key}: {str(value)[:100]}...")
                else:
                    print(f"  {key}: {value}")

        print(f"\nOptions:")
        print(f"  y/yes    - Approve this request")
        print(f"  n/no     - Deny this request")
        print(f"  a/always - Always approve this tool")
        print(f"  d/deny   - Always deny this tool")
        print(f"  e/explain - Explain the request in detail")
        print(f"  q/quit   - Quit the application")

        while True:
            try:
                response = (
                    input(f"\nApprove {request.tool_name}? [y/n/a/d/e/q]: ")
                    .lower()
                    .strip()
                )

                if response in ["y", "yes"]:
                    return ApprovalResult(
                        approved=True,
                        decision=ApprovalDecision.APPROVED,
                        reason="User approved",
                    )
                elif response in ["n", "no"]:
                    return ApprovalResult(
                        approved=False,
                        decision=ApprovalDecision.DENIED,
                        reason="User denied",
                    )
                elif response in ["a", "always"]:
                    return ApprovalResult(
                        approved=True,
                        decision=ApprovalDecision.ALWAYS_ALLOW,
                        reason="User approved with always allow",
                        remember_decision=True,
                    )
                elif response in ["d", "deny"]:
                    return ApprovalResult(
                        approved=False,
                        decision=ApprovalDecision.ALWAYS_DENY,
                        reason="User denied with always deny",
                        remember_decision=True,
                    )
                elif response in ["e", "explain"]:
                    await self._explain_request(request)
                    continue
                elif response in ["q", "quit"]:
                    import sys

                    sys.exit(0)
                else:
                    print("Invalid response. Please enter y/n/a/d/e/q")

            except (KeyboardInterrupt, EOFError):
                return ApprovalResult(
                    approved=False,
                    decision=ApprovalDecision.DENIED,
                    reason="User interrupted",
                )

    async def _explain_request(self, request: ApprovalRequest) -> None:
        """
        Provide detailed explanation of the approval request.

        Args:
            request: Approval request to explain
        """
        print(f"\n{'='*60}")
        print(f"DETAILED EXPLANATION")
        print(f"{'='*60}")

        # Tool-specific explanations
        if request.tool_name in ["file_write", "file_create"]:
            file_path = request.arguments.get("path", "")
            content_preview = str(request.arguments.get("content", ""))[:200]
            print(f"This will write/create a file at: {file_path}")
            print(f"Content preview: {content_preview}...")
            print(f"Risk: File operations can modify your project")

        elif request.tool_name in ["command_execution", "shell_command"]:
            command = request.arguments.get("command", "")
            print(f"This will execute the command: {command}")
            print(f"Risk: Commands can modify system state")
            print(f"Safety: Commands are run in a sandboxed environment")

        elif request.tool_name in ["file_delete", "directory_delete"]:
            path = request.arguments.get("path", "")
            print(f"This will delete: {path}")
            print(f"Risk: Deletion is permanent and cannot be undone")
            print(f"Recommendation: Ensure you have backups")

        elif request.tool_name in ["file_read", "directory_list"]:
            path = request.arguments.get("path", "")
            print(f"This will read/list: {path}")
            print(f"Risk: Low - only reading information")

        else:
            print(
                f"Tool '{request.tool_name}' will execute with the provided arguments"
            )
            print(f"Risk level assessed as: {request.risk_level}")

        # Security considerations
        print(f"\nSecurity Considerations:")
        print(f"- All operations are logged for audit")
        print(f"- High-risk operations require explicit approval")
        print(f"- You can set preferences to auto-approve/deny specific tools")
        print(f"- Operations are sandboxed when possible")

        print(f"\nPress Enter to continue...")
        input()

    def _generate_explanation(
        self, tool_name: str, arguments: Dict[str, Any], risk_level: str
    ) -> str:
        """Generate human-readable explanation of tool execution."""
        if tool_name in ["file_write", "file_create"]:
            file_path = arguments.get("path", "unknown")
            return f"Write/create file at '{file_path}'"

        elif tool_name in ["command_execution", "shell_command"]:
            command = arguments.get("command", "unknown")
            return f"Execute command: '{command}'"

        elif tool_name in ["file_delete", "directory_delete"]:
            path = arguments.get("path", "unknown")
            return f"Delete '{path}'"

        elif tool_name in ["file_read", "directory_list"]:
            path = arguments.get("path", "unknown")
            return f"Read/list '{path}'"

        else:
            return f"Execute {tool_name} with {len(arguments)} arguments"

    async def _log_approval(
        self,
        request_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        result: ApprovalResult,
    ) -> None:
        """Log approval decision for audit."""
        log_entry = {
            "timestamp": time.time(),
            "request_id": request_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "approved": result.approved,
            "decision": result.decision.value,
            "reason": result.reason,
            "auto_approved": result.auto_approved,
        }

        self.approval_history.append(log_entry)

        # Keep only last 1000 entries
        if len(self.approval_history) > 1000:
            self.approval_history = self.approval_history[-1000:]

        logger.info(f"Approval logged: {tool_name} - {result.decision.value}")

    def get_approval_stats(self) -> Dict[str, Any]:
        """Get approval system statistics."""
        return {
            "total_requests": self.total_requests,
            "auto_approved": self.auto_approved,
            "manual_approved": self.manual_approved,
            "denied": self.denied,
            "approval_rate": (self.auto_approved + self.manual_approved)
            / max(self.total_requests, 1),
            "auto_approval_rate": self.auto_approved / max(self.total_requests, 1),
            "pending_requests": len(self.pending_requests),
            "user_preferences": len(self.user_preferences),
            "current_mode": self.policy.mode.value,
        }

    def get_approval_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent approval history."""
        return self.approval_history[-limit:] if self.approval_history else []

    def set_approval_mode(self, mode: str) -> bool:
        """
        Set approval mode.

        Args:
            mode: New approval mode

        Returns:
            True if mode was changed successfully
        """
        try:
            new_mode = ApprovalMode(mode)
            self.policy.mode = new_mode
            self.config.approval_mode = mode
            logger.info(f"Approval mode changed to: {mode}")
            return True
        except ValueError:
            logger.error(f"Invalid approval mode: {mode}")
            return False

    def clear_user_preferences(self) -> None:
        """Clear all user preferences."""
        self.user_preferences.clear()
        logger.info("User approval preferences cleared")

    def get_user_preferences(self) -> Dict[str, str]:
        """Get current user preferences."""
        return self.user_preferences.copy()

    async def cleanup(self) -> None:
        """Clean up approval system resources."""
        try:
            # Cancel any pending requests
            for request_id in list(self.pending_requests.keys()):
                self.pending_requests.pop(request_id, None)

            # Save approval history if needed
            # This could be extended to persist to disk

            logger.info("Approval system cleanup completed")

        except Exception as e:
            logger.error(f"Error during approval system cleanup: {e}")

    async def approve_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> bool:
        """
        Approve a tool call execution.
        
        This is a convenience method that wraps request_approval and returns
        a simple boolean for easy integration with existing code.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Tool arguments
            
        Returns:
            True if approved, False if denied
        """
        try:
            result = await self.request_approval(tool_name, tool_args)
            return result.approved
        except Exception as e:
            logger.error(f"Error in approve_tool_call: {e}")
            return False

# Alias for backward compatibility and import error resolution
ApprovalManager = ApprovalSystem
