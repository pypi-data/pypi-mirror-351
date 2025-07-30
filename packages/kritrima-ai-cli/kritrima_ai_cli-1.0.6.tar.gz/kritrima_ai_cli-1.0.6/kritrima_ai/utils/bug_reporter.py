"""
Bug reporting system for Kritrima AI CLI.

This module provides automated bug report generation with session data,
system information, and GitHub integration for streamlined issue reporting.
"""

import json
import os
import platform
import sys
import traceback
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from kritrima_ai import __version__
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.storage.command_history import CommandHistory
from kritrima_ai.storage.session_manager import SessionManager
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemInfo:
    """System information for bug reports."""

    platform: str
    platform_version: str
    architecture: str
    python_version: str
    cli_version: str
    shell: str
    terminal: str
    working_directory: str
    environment_variables: Dict[str, str]


@dataclass
class ErrorInfo:
    """Error information for bug reports."""

    error_type: str
    error_message: str
    traceback: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class SessionInfo:
    """Session information for bug reports."""

    session_id: str
    messages_count: int
    provider: str
    model: str
    approval_mode: str
    recent_commands: List[str]
    session_duration: Optional[str] = None


@dataclass
class BugReport:
    """Complete bug report structure."""

    title: str
    description: str
    steps_to_reproduce: List[str]
    expected_behavior: str
    actual_behavior: str
    system_info: SystemInfo
    session_info: Optional[SessionInfo] = None
    error_info: Optional[ErrorInfo] = None
    additional_context: Optional[str] = None
    attachments: List[str] = None


class BugReporter:
    """
    Comprehensive bug reporting system.

    Features:
    - Automatic system information collection
    - Session data aggregation
    - Error context capture
    - GitHub issue URL generation
    - Privacy-aware data filtering
    - Reproducible bug report generation
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the bug reporter.

        Args:
            config: Application configuration
        """
        self.config = config
        self.github_repo = "kritrima/kritrima-ai-cli"
        self.github_issues_url = f"https://github.com/{self.github_repo}/issues/new"

        # Privacy settings
        self.include_session_data = getattr(config, "bug_reports", {}).get(
            "include_session_data", True
        )
        self.include_environment_vars = getattr(config, "bug_reports", {}).get(
            "include_environment_vars", False
        )
        self.sanitize_sensitive_data = getattr(config, "bug_reports", {}).get(
            "sanitize_sensitive_data", True
        )

        # Sensitive patterns to filter out
        self.sensitive_patterns = [
            r"api[_-]?key",
            r"password",
            r"token",
            r"secret",
            r"credential",
            r"auth",
            r"bearer",
            r"oauth",
        ]

        logger.info("Bug reporter initialized")

    def collect_system_info(self) -> SystemInfo:
        """Collect comprehensive system information."""
        try:
            # Basic platform info
            platform_info = platform.uname()

            # Environment variables (filtered for sensitive data)
            env_vars = {}
            if self.include_environment_vars:
                env_vars = self._filter_environment_variables()

            return SystemInfo(
                platform=platform_info.system,
                platform_version=platform_info.release,
                architecture=platform_info.machine,
                python_version=sys.version,
                cli_version=__version__,
                shell=os.environ.get("SHELL", os.environ.get("ComSpec", "unknown")),
                terminal=os.environ.get(
                    "TERM", os.environ.get("TERM_PROGRAM", "unknown")
                ),
                working_directory=str(Path.cwd()),
                environment_variables=env_vars,
            )

        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            # Return minimal info on error
            return SystemInfo(
                platform=platform.system(),
                platform_version="unknown",
                architecture=platform.machine(),
                python_version=sys.version.split()[0],
                cli_version=__version__,
                shell="unknown",
                terminal="unknown",
                working_directory=str(Path.cwd()),
                environment_variables={},
            )

    async def collect_session_info(
        self,
        session_manager: Optional[SessionManager] = None,
        command_history: Optional[CommandHistory] = None,
    ) -> Optional[SessionInfo]:
        """Collect current session information."""
        if not self.include_session_data:
            return None

        try:
            session_info = SessionInfo(
                session_id="unknown",
                messages_count=0,
                provider=self.config.provider,
                model=self.config.model,
                approval_mode=self.config.approval_mode,
                recent_commands=[],
            )

            # Get current session from session manager
            if session_manager:
                current_session = session_manager.get_current_session()
                if current_session:
                    session_info.session_id = (
                        current_session.session_id[:8] + "..."
                    )  # Truncate for privacy
                    session_info.messages_count = len(current_session.messages)

                    # Calculate session duration
                    if current_session.created_at:
                        duration = datetime.now() - datetime.fromtimestamp(
                            current_session.created_at
                        )
                        session_info.session_duration = str(duration).split(".")[
                            0
                        ]  # Remove microseconds

            # Get recent commands from command history
            if command_history:
                recent_history = await command_history.get_history(limit=5)
                session_info.recent_commands = [
                    self._sanitize_command(entry.command) for entry in recent_history
                ]

            return session_info

        except Exception as e:
            logger.error(f"Error collecting session info: {e}")
            return None

    def create_error_info(
        self, exception: Exception, context: Optional[Dict[str, Any]] = None
    ) -> ErrorInfo:
        """Create error information from an exception."""
        return ErrorInfo(
            error_type=type(exception).__name__,
            error_message=str(exception),
            traceback=traceback.format_exc(),
            timestamp=datetime.now().isoformat(),
            context=context,
        )

    async def generate_bug_report(
        self,
        title: str,
        description: str,
        steps_to_reproduce: List[str],
        expected_behavior: str = "",
        actual_behavior: str = "",
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        session_manager: Optional[SessionManager] = None,
        command_history: Optional[CommandHistory] = None,
    ) -> BugReport:
        """Generate a comprehensive bug report."""
        try:
            # Collect system information
            system_info = self.collect_system_info()

            # Collect session information
            session_info = await self.collect_session_info(
                session_manager, command_history
            )

            # Create error information if provided
            error_info = None
            if error:
                error_info = self.create_error_info(error, context)

            return BugReport(
                title=title,
                description=description,
                steps_to_reproduce=steps_to_reproduce,
                expected_behavior=expected_behavior,
                actual_behavior=actual_behavior,
                system_info=system_info,
                session_info=session_info,
                error_info=error_info,
                additional_context=json.dumps(context, indent=2) if context else None,
            )

        except Exception as e:
            logger.error(f"Error generating bug report: {e}")
            raise

    def format_bug_report_markdown(self, bug_report: BugReport) -> str:
        """Format bug report as GitHub Markdown."""
        lines = [
            f"# {bug_report.title}",
            "",
            "## Description",
            bug_report.description,
            "",
            "## Steps to Reproduce",
        ]

        for i, step in enumerate(bug_report.steps_to_reproduce, 1):
            lines.append(f"{i}. {step}")

        lines.extend(
            [
                "",
                "## Expected Behavior",
                bug_report.expected_behavior or "Please describe the expected behavior",
                "",
                "## Actual Behavior",
                bug_report.actual_behavior or "Please describe what actually happened",
                "",
            ]
        )

        # Add error information if available
        if bug_report.error_info:
            lines.extend(
                [
                    "## Error Information",
                    f"**Error Type:** `{bug_report.error_info.error_type}`",
                    f"**Error Message:** {bug_report.error_info.error_message}",
                    f"**Timestamp:** {bug_report.error_info.timestamp}",
                    "",
                    "### Traceback",
                    "```python",
                    bug_report.error_info.traceback,
                    "```",
                    "",
                ]
            )

        # Add system information
        lines.extend(
            [
                "## System Information",
                f"- **Kritrima AI CLI Version:** {bug_report.system_info.cli_version}",
                f"- **Platform:** {bug_report.system_info.platform} {bug_report.system_info.platform_version}",
                f"- **Architecture:** {bug_report.system_info.architecture}",
                f"- **Python Version:** {bug_report.system_info.python_version.split()[0]}",
                f"- **Shell:** {bug_report.system_info.shell}",
                f"- **Terminal:** {bug_report.system_info.terminal}",
                "",
            ]
        )

        # Add session information if available
        if bug_report.session_info:
            lines.extend(
                [
                    "## Session Information",
                    f"- **Session ID:** {bug_report.session_info.session_id}",
                    f"- **Provider:** {bug_report.session_info.provider}",
                    f"- **Model:** {bug_report.session_info.model}",
                    f"- **Approval Mode:** {bug_report.session_info.approval_mode}",
                    f"- **Messages Count:** {bug_report.session_info.messages_count}",
                ]
            )

            if bug_report.session_info.session_duration:
                lines.append(
                    f"- **Session Duration:** {bug_report.session_info.session_duration}"
                )

            if bug_report.session_info.recent_commands:
                lines.extend(["", "### Recent Commands", "```bash"])
                lines.extend(bug_report.session_info.recent_commands)
                lines.extend(["```", ""])

        # Add additional context if available
        if bug_report.additional_context:
            lines.extend(
                [
                    "## Additional Context",
                    "```json",
                    bug_report.additional_context,
                    "```",
                    "",
                ]
            )

        # Add environment variables if included
        if bug_report.system_info.environment_variables:
            lines.extend(
                [
                    "## Environment Variables",
                    "```",
                ]
            )
            for key, value in bug_report.system_info.environment_variables.items():
                lines.append(f"{key}={value}")
            lines.extend(["```", ""])

        # Add footer
        lines.extend(
            [
                "---",
                "",
                "<!-- This bug report was automatically generated by Kritrima AI CLI -->",
                f"<!-- Report generated at: {datetime.now().isoformat()} -->",
                f"<!-- CLI Version: {__version__} -->",
            ]
        )

        return "\n".join(lines)

    def generate_github_issue_url(self, bug_report: BugReport) -> str:
        """Generate GitHub issue URL with pre-filled bug report."""
        try:
            # Format the bug report as markdown
            body = self.format_bug_report_markdown(bug_report)

            # URL encode the parameters
            params = {
                "title": bug_report.title,
                "body": body,
                "labels": "bug,auto-generated",
            }

            # Add error-specific labels
            if bug_report.error_info:
                params["labels"] += ",error"
                if "timeout" in bug_report.error_info.error_message.lower():
                    params["labels"] += ",timeout"
                elif "permission" in bug_report.error_info.error_message.lower():
                    params["labels"] += ",permissions"
                elif "network" in bug_report.error_info.error_message.lower():
                    params["labels"] += ",network"

            # Build URL
            query_string = urllib.parse.urlencode(params)
            url = f"{self.github_issues_url}?{query_string}"

            # GitHub has URL length limits, so we may need to truncate
            if len(url) > 8000:  # Conservative limit
                # Truncate the body but keep essential information
                truncated_body = body[:4000] + "\n\n... (truncated for URL length)"
                params["body"] = truncated_body
                query_string = urllib.parse.urlencode(params)
                url = f"{self.github_issues_url}?{query_string}"

            return url

        except Exception as e:
            logger.error(f"Error generating GitHub issue URL: {e}")
            # Return basic URL if generation fails
            return (
                f"{self.github_issues_url}?title={urllib.parse.quote(bug_report.title)}"
            )

    def _filter_environment_variables(self) -> Dict[str, str]:
        """Filter environment variables to exclude sensitive data."""
        import re

        filtered_vars = {}

        for key, value in os.environ.items():
            # Check if key matches sensitive patterns
            is_sensitive = any(
                re.search(pattern, key, re.IGNORECASE)
                for pattern in self.sensitive_patterns
            )

            if is_sensitive:
                if self.sanitize_sensitive_data:
                    # Replace with placeholder
                    filtered_vars[key] = "[REDACTED]"
                # Otherwise skip entirely
            else:
                # Include non-sensitive variables
                filtered_vars[key] = value

        return filtered_vars

    def _sanitize_command(self, command: str) -> str:
        """Sanitize command to remove sensitive information."""
        if not self.sanitize_sensitive_data:
            return command

        import re

        sanitized = command

        # Pattern to match common sensitive patterns in commands
        patterns = [
            r"--api[_-]?key[=\s]+[^\s]+",
            r"--token[=\s]+[^\s]+",
            r"--password[=\s]+[^\s]+",
            r"export\s+\w*(?:key|token|password)\w*[=][^\s]+",
        ]

        for pattern in patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    async def create_crash_report(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        session_manager: Optional[SessionManager] = None,
        command_history: Optional[CommandHistory] = None,
    ) -> BugReport:
        """Create a crash report from an unhandled exception."""
        title = f"Crash: {type(exception).__name__} in Kritrima AI CLI"

        description = f"""
Kritrima AI CLI crashed with an unhandled exception.

**Error:** {str(exception)}

This crash report was automatically generated. Please provide any additional context about what you were doing when the crash occurred.
""".strip()

        steps_to_reproduce = [
            "Unfortunately, the exact steps are not known as this was an unexpected crash",
            "Please add any steps you remember that led to this crash",
        ]

        expected_behavior = "The application should not crash"
        actual_behavior = (
            f"Application crashed with {type(exception).__name__}: {str(exception)}"
        )

        return await self.generate_bug_report(
            title=title,
            description=description,
            steps_to_reproduce=steps_to_reproduce,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            error=exception,
            context=context,
            session_manager=session_manager,
            command_history=command_history,
        )

    def get_bug_report_summary(self, bug_report: BugReport) -> str:
        """Get a brief summary of the bug report."""
        lines = [
            f"Title: {bug_report.title}",
            f"CLI Version: {bug_report.system_info.cli_version}",
            f"Platform: {bug_report.system_info.platform}",
        ]

        if bug_report.session_info:
            lines.append(f"Provider: {bug_report.session_info.provider}")
            lines.append(f"Model: {bug_report.session_info.model}")

        if bug_report.error_info:
            lines.append(f"Error: {bug_report.error_info.error_type}")

        return " | ".join(lines)


# Global bug reporter instance
_bug_reporter: Optional[BugReporter] = None


def initialize_bug_reporter(config: AppConfig) -> BugReporter:
    """Initialize the global bug reporter."""
    global _bug_reporter
    _bug_reporter = BugReporter(config)
    return _bug_reporter


def get_bug_reporter() -> Optional[BugReporter]:
    """Get the global bug reporter instance."""
    return _bug_reporter


async def create_bug_report_url(
    title: str,
    description: str,
    steps: List[str],
    session_manager: Optional[SessionManager] = None,
    command_history: Optional[CommandHistory] = None,
) -> Optional[str]:
    """Create a bug report URL for manual reporting."""
    reporter = get_bug_reporter()
    if not reporter:
        logger.warning("Bug reporter not initialized")
        return None

    try:
        bug_report = await reporter.generate_bug_report(
            title=title,
            description=description,
            steps_to_reproduce=steps,
            session_manager=session_manager,
            command_history=command_history,
        )

        return reporter.generate_github_issue_url(bug_report)

    except Exception as e:
        logger.error(f"Error creating bug report URL: {e}")
        return None


async def create_crash_report_url(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    session_manager: Optional[SessionManager] = None,
    command_history: Optional[CommandHistory] = None,
) -> Optional[str]:
    """Create a crash report URL for automatic reporting."""
    reporter = get_bug_reporter()
    if not reporter:
        logger.warning("Bug reporter not initialized")
        return None

    try:
        bug_report = await reporter.create_crash_report(
            exception=exception,
            context=context,
            session_manager=session_manager,
            command_history=command_history,
        )

        return reporter.generate_github_issue_url(bug_report)

    except Exception as e:
        logger.error(f"Error creating crash report URL: {e}")
        return None
