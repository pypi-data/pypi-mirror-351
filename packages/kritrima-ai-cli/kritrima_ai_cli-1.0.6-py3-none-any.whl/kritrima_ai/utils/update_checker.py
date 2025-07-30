"""
Update checker and version management for Kritrima AI CLI.

This module provides automatic update checking, version comparison, and
update notification functionality with package manager integration.
"""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

import httpx
import platformdirs

from kritrima_ai import __version__
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger
from kritrima_ai.utils.notifications import get_notification_manager

logger = get_logger(__name__)


class VersionInfo(NamedTuple):
    """Version information."""

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None


@dataclass
class UpdateInfo:
    """Information about available updates."""

    current_version: str
    latest_version: str
    update_available: bool
    is_major_update: bool
    is_security_update: bool
    release_notes: Optional[str] = None
    download_url: Optional[str] = None
    published_at: Optional[datetime] = None
    changelog_url: Optional[str] = None


@dataclass
class PackageManagerInfo:
    """Package manager information."""

    name: str
    command: str
    update_command: List[str]
    check_command: List[str]
    available: bool = False


class UpdateChecker:
    """
    Comprehensive update checker for Kritrima AI CLI.

    Features:
    - Automatic version checking from PyPI and GitHub
    - Package manager detection and integration
    - Update notification system
    - Configurable check intervals
    - Changelog and release notes fetching
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the update checker.

        Args:
            config: Application configuration
        """
        self.config = config
        self.current_version = __version__
        self.update_config = getattr(config, "updates", self._default_update_config())

        # Cache settings
        self.cache_dir = Path(platformdirs.user_cache_dir("kritrima-ai"))
        self.cache_file = self.cache_dir / "update_cache.json"
        self.cache_expiry = timedelta(
            hours=self.update_config.get("check_interval_hours", 24)
        )

        # API endpoints
        self.pypi_api_url = "https://pypi.org/pypi/kritrima-ai-cli/json"
        self.github_api_url = (
            "https://api.github.com/repos/kritrima/kritrima-ai-cli/releases/latest"
        )

        # Package managers
        self.package_managers = self._detect_package_managers()

        # HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={"User-Agent": f"Kritrima-AI-CLI/{self.current_version}"},
        )

        logger.info(
            f"Update checker initialized (current version: {self.current_version})"
        )

    def _default_update_config(self) -> Dict[str, Any]:
        """Get default update configuration."""
        return {
            "enabled": True,
            "check_interval_hours": 24,
            "auto_check_on_startup": True,
            "notify_major_updates": True,
            "notify_security_updates": True,
            "include_prereleases": False,
            "sources": ["pypi", "github"],
        }

    def _detect_package_managers(self) -> List[PackageManagerInfo]:
        """Detect available package managers."""
        managers = [
            PackageManagerInfo(
                name="pip",
                command="pip",
                update_command=["pip", "install", "--upgrade", "kritrima-ai-cli"],
                check_command=["pip", "show", "kritrima-ai-cli"],
            ),
            PackageManagerInfo(
                name="pipx",
                command="pipx",
                update_command=["pipx", "upgrade", "kritrima-ai-cli"],
                check_command=["pipx", "list"],
            ),
            PackageManagerInfo(
                name="poetry",
                command="poetry",
                update_command=["poetry", "update", "kritrima-ai-cli"],
                check_command=["poetry", "show", "kritrima-ai-cli"],
            ),
            PackageManagerInfo(
                name="conda",
                command="conda",
                update_command=["conda", "update", "kritrima-ai-cli"],
                check_command=["conda", "list", "kritrima-ai-cli"],
            ),
        ]

        # Check which managers are available
        for manager in managers:
            try:
                result = subprocess.run(
                    [manager.command, "--version"],
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
                manager.available = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError, OSError):
                manager.available = False

        available_managers = [m for m in managers if m.available]
        logger.info(
            f"Available package managers: {[m.name for m in available_managers]}"
        )

        return available_managers

    async def check_for_updates(self, force: bool = False) -> Optional[UpdateInfo]:
        """
        Check for available updates.

        Args:
            force: Force check even if cache is valid

        Returns:
            UpdateInfo if update is available, None otherwise
        """
        if not self.update_config.get("enabled", True):
            logger.debug("Update checking is disabled")
            return None

        try:
            # Check cache first
            if not force:
                cached_info = self._load_cache()
                if cached_info and self._is_cache_valid():
                    logger.debug("Using cached update information")
                    return cached_info

            logger.info("Checking for updates...")

            # Try different sources
            update_info = None
            sources = self.update_config.get("sources", ["pypi"])

            for source in sources:
                try:
                    if source == "pypi":
                        update_info = await self._check_pypi_updates()
                    elif source == "github":
                        update_info = await self._check_github_updates()

                    if update_info:
                        break

                except Exception as e:
                    logger.warning(f"Failed to check {source} for updates: {e}")
                    continue

            if update_info:
                # Save to cache
                self._save_cache(update_info)

                # Send notification if configured
                await self._notify_update_available(update_info)

                logger.info(f"Update available: {update_info.latest_version}")
            else:
                logger.info("No updates available")

            return update_info

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None

    async def _check_pypi_updates(self) -> Optional[UpdateInfo]:
        """Check for updates from PyPI."""
        try:
            response = await self.http_client.get(self.pypi_api_url)
            response.raise_for_status()

            data = response.json()
            latest_version = data["info"]["version"]

            # Get release information
            releases = data.get("releases", {})
            latest_release = releases.get(latest_version, [])

            if not latest_release:
                logger.warning("No release files found for latest version")
                return None

            # Check if update is available
            if self._is_newer_version(latest_version, self.current_version):
                # Get download URL
                download_url = None
                for release_file in latest_release:
                    if release_file.get("packagetype") == "sdist":
                        download_url = release_file.get("url")
                        break

                return UpdateInfo(
                    current_version=self.current_version,
                    latest_version=latest_version,
                    update_available=True,
                    is_major_update=self._is_major_update(
                        self.current_version, latest_version
                    ),
                    is_security_update=False,  # Could be enhanced to detect security updates
                    release_notes=data["info"].get("description"),
                    download_url=download_url,
                    changelog_url=data["info"].get("project_urls", {}).get("Changelog"),
                )

            return None

        except Exception as e:
            logger.error(f"Error checking PyPI updates: {e}")
            raise

    async def _check_github_updates(self) -> Optional[UpdateInfo]:
        """Check for updates from GitHub releases."""
        try:
            response = await self.http_client.get(self.github_api_url)
            response.raise_for_status()

            data = response.json()
            latest_version = data["tag_name"].lstrip(
                "v"
            )  # Remove 'v' prefix if present

            # Check if update is available
            if self._is_newer_version(latest_version, self.current_version):
                published_at = None
                if data.get("published_at"):
                    published_at = datetime.fromisoformat(
                        data["published_at"].replace("Z", "+00:00")
                    )

                return UpdateInfo(
                    current_version=self.current_version,
                    latest_version=latest_version,
                    update_available=True,
                    is_major_update=self._is_major_update(
                        self.current_version, latest_version
                    ),
                    is_security_update="security" in data.get("body", "").lower(),
                    release_notes=data.get("body"),
                    download_url=data.get("html_url"),
                    published_at=published_at,
                    changelog_url=data.get("html_url"),
                )

            return None

        except Exception as e:
            logger.error(f"Error checking GitHub updates: {e}")
            raise

    def _parse_version(self, version_str: str) -> VersionInfo:
        """Parse version string into components."""
        # Remove 'v' prefix if present
        clean_version = version_str.lstrip("v")

        # Match semantic version pattern
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$"
        match = re.match(pattern, clean_version)

        if not match:
            # Fallback for simple versions like "1.0.0"
            parts = clean_version.split(".")
            if len(parts) >= 3:
                return VersionInfo(
                    major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2])
                )
            else:
                raise ValueError(f"Invalid version format: {version_str}")

        major, minor, patch, prerelease, build = match.groups()

        return VersionInfo(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build=build,
        )

    def _is_newer_version(self, new_version: str, current_version: str) -> bool:
        """Check if new version is newer than current version."""
        try:
            new_ver = self._parse_version(new_version)
            current_ver = self._parse_version(current_version)

            # Compare major.minor.patch
            if new_ver.major != current_ver.major:
                return new_ver.major > current_ver.major
            elif new_ver.minor != current_ver.minor:
                return new_ver.minor > current_ver.minor
            elif new_ver.patch != current_ver.patch:
                return new_ver.patch > current_ver.patch
            else:
                # Same base version, check prerelease
                if current_ver.prerelease and not new_ver.prerelease:
                    return True  # Stable is newer than prerelease
                elif not current_ver.prerelease and new_ver.prerelease:
                    return False  # Prerelease is not newer than stable
                elif current_ver.prerelease and new_ver.prerelease:
                    return new_ver.prerelease > current_ver.prerelease
                else:
                    return False  # Same version

        except Exception as e:
            logger.warning(f"Error comparing versions: {e}")
            # Fallback to string comparison
            return new_version > current_version

    def _is_major_update(self, current_version: str, new_version: str) -> bool:
        """Check if this is a major version update."""
        try:
            current_ver = self._parse_version(current_version)
            new_ver = self._parse_version(new_version)

            return new_ver.major > current_ver.major

        except Exception:
            return False

    def _load_cache(self) -> Optional[UpdateInfo]:
        """Load cached update information."""
        try:
            if not self.cache_file.exists():
                return None

            with open(self.cache_file, "r") as f:
                data = json.load(f)

            # Reconstruct UpdateInfo
            published_at = None
            if data.get("published_at"):
                published_at = datetime.fromisoformat(data["published_at"])

            return UpdateInfo(
                current_version=data["current_version"],
                latest_version=data["latest_version"],
                update_available=data["update_available"],
                is_major_update=data["is_major_update"],
                is_security_update=data["is_security_update"],
                release_notes=data.get("release_notes"),
                download_url=data.get("download_url"),
                published_at=published_at,
                changelog_url=data.get("changelog_url"),
            )

        except Exception as e:
            logger.warning(f"Error loading update cache: {e}")
            return None

    def _save_cache(self, update_info: UpdateInfo) -> None:
        """Save update information to cache."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            data = {
                "current_version": update_info.current_version,
                "latest_version": update_info.latest_version,
                "update_available": update_info.update_available,
                "is_major_update": update_info.is_major_update,
                "is_security_update": update_info.is_security_update,
                "release_notes": update_info.release_notes,
                "download_url": update_info.download_url,
                "published_at": (
                    update_info.published_at.isoformat()
                    if update_info.published_at
                    else None
                ),
                "changelog_url": update_info.changelog_url,
                "cached_at": datetime.now().isoformat(),
            }

            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.warning(f"Error saving update cache: {e}")

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        try:
            if not self.cache_file.exists():
                return False

            cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            return datetime.now() - cache_time < self.cache_expiry

        except Exception:
            return False

    async def _notify_update_available(self, update_info: UpdateInfo) -> None:
        """Send notification about available update."""
        try:
            notification_manager = get_notification_manager()
            if not notification_manager:
                return

            # Check notification settings
            should_notify = False

            if update_info.is_security_update and self.update_config.get(
                "notify_security_updates", True
            ):
                should_notify = True
            elif update_info.is_major_update and self.update_config.get(
                "notify_major_updates", True
            ):
                should_notify = True
            elif self.update_config.get("notify_all_updates", False):
                should_notify = True

            if should_notify:
                title = "Update Available"
                if update_info.is_security_update:
                    title = "Security Update Available"
                elif update_info.is_major_update:
                    title = "Major Update Available"

                message = f"Version {update_info.latest_version} is now available!"

                await notification_manager.notify(
                    title=title, message=message, notification_type="info"
                )

        except Exception as e:
            logger.warning(f"Error sending update notification: {e}")

    def get_update_command(self) -> Optional[List[str]]:
        """Get the appropriate update command for the current environment."""
        # Try to detect how Kritrima AI was installed
        for manager in self.package_managers:
            if manager.available:
                # Could add more sophisticated detection here
                return manager.update_command

        # Default fallback
        return ["pip", "install", "--upgrade", "kritrima-ai-cli"]

    def format_update_info(self, update_info: UpdateInfo) -> str:
        """Format update information for display."""
        lines = [
            f"🎉 Update Available!",
            f"",
            f"Current Version: {update_info.current_version}",
            f"Latest Version:  {update_info.latest_version}",
            f"",
        ]

        if update_info.is_security_update:
            lines.append("⚠️  This is a security update - update recommended!")
        elif update_info.is_major_update:
            lines.append("🚀 This is a major version update with new features!")

        if update_info.published_at:
            lines.append(f"Released: {update_info.published_at.strftime('%Y-%m-%d')}")

        # Add update command
        update_cmd = self.get_update_command()
        if update_cmd:
            lines.extend(["", f"To update, run:", f"  {' '.join(update_cmd)}"])

        if update_info.changelog_url:
            lines.extend(["", f"View changelog: {update_info.changelog_url}"])

        return "\n".join(lines)

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            await self.http_client.aclose()
        except Exception as e:
            logger.warning(f"Error cleaning up update checker: {e}")


# Global update checker instance
_update_checker: Optional[UpdateChecker] = None


def initialize_update_checker(config: AppConfig) -> UpdateChecker:
    """Initialize the global update checker."""
    global _update_checker
    _update_checker = UpdateChecker(config)
    return _update_checker


def get_update_checker() -> Optional[UpdateChecker]:
    """Get the global update checker instance."""
    return _update_checker


async def check_for_updates_startup(config: AppConfig) -> Optional[UpdateInfo]:
    """Check for updates on application startup."""
    if not config.updates.get("auto_check_on_startup", True):
        return None

    checker = get_update_checker()
    if not checker:
        checker = initialize_update_checker(config)

    return await checker.check_for_updates()


async def check_for_updates_manual() -> Optional[UpdateInfo]:
    """Manually check for updates."""
    checker = get_update_checker()
    if not checker:
        logger.warning("Update checker not initialized")
        return None

    return await checker.check_for_updates(force=True)
