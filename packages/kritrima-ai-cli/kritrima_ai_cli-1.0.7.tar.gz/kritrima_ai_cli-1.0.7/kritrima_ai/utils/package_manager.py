"""
Package manager detection and management utilities.

This module provides functionality to detect various package managers
and generate appropriate commands for updates, installs, and project management.
"""

import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class PackageManager(Enum):
    """Supported package managers."""

    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"
    DENO = "deno"
    PIP = "pip"
    POETRY = "poetry"
    PIPENV = "pipenv"
    CONDA = "conda"
    CARGO = "cargo"
    GO = "go"
    COMPOSER = "composer"
    MAVEN = "mvn"
    GRADLE = "gradle"
    DOTNET = "dotnet"
    UNKNOWN = "unknown"


@dataclass
class PackageManagerInfo:
    """Information about a detected package manager."""

    name: PackageManager
    version: Optional[str]
    executable_path: str
    config_files: List[Path]
    lock_files: List[Path]
    install_command: str
    update_command: str
    dev_command: Optional[str] = None
    build_command: Optional[str] = None
    test_command: Optional[str] = None


class PackageManagerDetector:
    """
    Detects and manages various package managers in a project.

    Features:
    - Auto-detection based on lock files and configuration
    - Version checking and command generation
    - Multi-language support (JavaScript, Python, Rust, Go, etc.)
    - Project-specific recommendations
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the package manager detector.

        Args:
            project_root: Project root directory (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.detected_managers: List[PackageManagerInfo] = []

        # Package manager signatures
        self.signatures = {
            PackageManager.NPM: {
                "config_files": ["package.json"],
                "lock_files": ["package-lock.json"],
                "install_cmd": "npm install",
                "update_cmd": "npm update",
                "dev_cmd": "npm run dev",
                "build_cmd": "npm run build",
                "test_cmd": "npm test",
            },
            PackageManager.YARN: {
                "config_files": ["package.json", "yarn.json"],
                "lock_files": ["yarn.lock"],
                "install_cmd": "yarn install",
                "update_cmd": "yarn upgrade",
                "dev_cmd": "yarn dev",
                "build_cmd": "yarn build",
                "test_cmd": "yarn test",
            },
            PackageManager.PNPM: {
                "config_files": ["package.json", "pnpm-workspace.yaml"],
                "lock_files": ["pnpm-lock.yaml"],
                "install_cmd": "pnpm install",
                "update_cmd": "pnpm update",
                "dev_cmd": "pnpm dev",
                "build_cmd": "pnpm build",
                "test_cmd": "pnpm test",
            },
            PackageManager.BUN: {
                "config_files": ["package.json", "bun.toml"],
                "lock_files": ["bun.lockb"],
                "install_cmd": "bun install",
                "update_cmd": "bun update",
                "dev_cmd": "bun dev",
                "build_cmd": "bun build",
                "test_cmd": "bun test",
            },
            PackageManager.DENO: {
                "config_files": ["deno.json", "deno.jsonc"],
                "lock_files": ["deno.lock"],
                "install_cmd": "deno install",
                "update_cmd": "deno upgrade",
                "dev_cmd": "deno run --watch",
                "build_cmd": "deno compile",
                "test_cmd": "deno test",
            },
            PackageManager.PIP: {
                "config_files": ["requirements.txt", "setup.py", "pyproject.toml"],
                "lock_files": ["requirements-lock.txt"],
                "install_cmd": "pip install -r requirements.txt",
                "update_cmd": "pip install --upgrade -r requirements.txt",
                "dev_cmd": None,
                "build_cmd": "python setup.py build",
                "test_cmd": "python -m pytest",
            },
            PackageManager.POETRY: {
                "config_files": ["pyproject.toml"],
                "lock_files": ["poetry.lock"],
                "install_cmd": "poetry install",
                "update_cmd": "poetry update",
                "dev_cmd": "poetry run python",
                "build_cmd": "poetry build",
                "test_cmd": "poetry run pytest",
            },
            PackageManager.PIPENV: {
                "config_files": ["Pipfile"],
                "lock_files": ["Pipfile.lock"],
                "install_cmd": "pipenv install",
                "update_cmd": "pipenv update",
                "dev_cmd": "pipenv run python",
                "build_cmd": None,
                "test_cmd": "pipenv run pytest",
            },
            PackageManager.CONDA: {
                "config_files": ["environment.yml", "environment.yaml"],
                "lock_files": [],
                "install_cmd": "conda env create -f environment.yml",
                "update_cmd": "conda env update -f environment.yml",
                "dev_cmd": None,
                "build_cmd": None,
                "test_cmd": "pytest",
            },
            PackageManager.CARGO: {
                "config_files": ["Cargo.toml"],
                "lock_files": ["Cargo.lock"],
                "install_cmd": "cargo build",
                "update_cmd": "cargo update",
                "dev_cmd": "cargo run",
                "build_cmd": "cargo build --release",
                "test_cmd": "cargo test",
            },
            PackageManager.GO: {
                "config_files": ["go.mod"],
                "lock_files": ["go.sum"],
                "install_cmd": "go mod download",
                "update_cmd": "go get -u ./...",
                "dev_cmd": "go run .",
                "build_cmd": "go build",
                "test_cmd": "go test ./...",
            },
            PackageManager.COMPOSER: {
                "config_files": ["composer.json"],
                "lock_files": ["composer.lock"],
                "install_cmd": "composer install",
                "update_cmd": "composer update",
                "dev_cmd": None,
                "build_cmd": None,
                "test_cmd": "composer test",
            },
            PackageManager.MAVEN: {
                "config_files": ["pom.xml"],
                "lock_files": [],
                "install_cmd": "mvn install",
                "update_cmd": "mvn versions:use-latest-versions",
                "dev_cmd": "mvn spring-boot:run",
                "build_cmd": "mvn package",
                "test_cmd": "mvn test",
            },
            PackageManager.GRADLE: {
                "config_files": ["build.gradle", "build.gradle.kts"],
                "lock_files": ["gradle.lockfile"],
                "install_cmd": "./gradlew build",
                "update_cmd": "./gradlew dependencies --refresh-dependencies",
                "dev_cmd": "./gradlew bootRun",
                "build_cmd": "./gradlew build",
                "test_cmd": "./gradlew test",
            },
            PackageManager.DOTNET: {
                "config_files": ["*.csproj", "*.sln", "*.fsproj", "*.vbproj"],
                "lock_files": ["packages.lock.json"],
                "install_cmd": "dotnet restore",
                "update_cmd": "dotnet add package",
                "dev_cmd": "dotnet run",
                "build_cmd": "dotnet build",
                "test_cmd": "dotnet test",
            },
        }

        logger.debug(f"Initialized package manager detector for: {self.project_root}")

    def detect_package_managers(self) -> List[PackageManagerInfo]:
        """
        Detect all package managers in the project.

        Returns:
            List of detected package manager information
        """
        self.detected_managers.clear()

        for manager, signature in self.signatures.items():
            if self._check_manager_presence(manager, signature):
                info = self._build_manager_info(manager, signature)
                if info:
                    self.detected_managers.append(info)

        logger.info(f"Detected {len(self.detected_managers)} package managers")
        return self.detected_managers

    def _check_manager_presence(self, manager: PackageManager, signature: Dict) -> bool:
        """Check if a package manager is present in the project."""
        # Check for config files
        config_files = signature.get("config_files", [])
        for config_file in config_files:
            if "*" in config_file:
                # Handle glob patterns
                from glob import glob

                matches = glob(str(self.project_root / config_file))
                if matches:
                    return True
            else:
                if (self.project_root / config_file).exists():
                    return True

        # Check for lock files (optional but strong indicator)
        lock_files = signature.get("lock_files", [])
        for lock_file in lock_files:
            if (self.project_root / lock_file).exists():
                return True

        return False

    def _build_manager_info(
        self, manager: PackageManager, signature: Dict
    ) -> Optional[PackageManagerInfo]:
        """Build package manager information."""
        # Check if executable is available
        executable_path = shutil.which(manager.value)
        if not executable_path and manager != PackageManager.DOTNET:
            # Special case for .NET which might use 'dotnet' command
            if manager == PackageManager.DOTNET:
                executable_path = shutil.which("dotnet")

            if not executable_path:
                logger.debug(f"Executable not found for {manager.value}")
                return None

        # Get version
        version = self._get_manager_version(manager, executable_path)

        # Find config and lock files
        config_files = []
        lock_files = []

        for config_file in signature.get("config_files", []):
            file_path = self.project_root / config_file
            if file_path.exists():
                config_files.append(file_path)

        for lock_file in signature.get("lock_files", []):
            file_path = self.project_root / lock_file
            if file_path.exists():
                lock_files.append(file_path)

        return PackageManagerInfo(
            name=manager,
            version=version,
            executable_path=executable_path,
            config_files=config_files,
            lock_files=lock_files,
            install_command=signature.get("install_cmd", ""),
            update_command=signature.get("update_cmd", ""),
            dev_command=signature.get("dev_cmd"),
            build_command=signature.get("build_cmd"),
            test_command=signature.get("test_cmd"),
        )

    def _get_manager_version(
        self, manager: PackageManager, executable_path: str
    ) -> Optional[str]:
        """Get package manager version."""
        try:
            version_args = {
                PackageManager.NPM: ["--version"],
                PackageManager.YARN: ["--version"],
                PackageManager.PNPM: ["--version"],
                PackageManager.BUN: ["--version"],
                PackageManager.DENO: ["--version"],
                PackageManager.PIP: ["--version"],
                PackageManager.POETRY: ["--version"],
                PackageManager.PIPENV: ["--version"],
                PackageManager.CONDA: ["--version"],
                PackageManager.CARGO: ["--version"],
                PackageManager.GO: ["version"],
                PackageManager.COMPOSER: ["--version"],
                PackageManager.MAVEN: ["--version"],
                PackageManager.GRADLE: ["--version"],
                PackageManager.DOTNET: ["--version"],
            }

            args = version_args.get(manager, ["--version"])
            result = subprocess.run(
                [executable_path] + args, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                version_output = result.stdout.strip()
                # Extract version number from output
                if manager == PackageManager.GO:
                    # Go version output: "go version go1.19.1 linux/amd64"
                    parts = version_output.split()
                    if len(parts) >= 3:
                        return parts[2]
                elif manager in [PackageManager.MAVEN, PackageManager.GRADLE]:
                    # Maven/Gradle have multi-line version output
                    lines = version_output.split("\n")
                    for line in lines:
                        if "version" in line.lower():
                            import re

                            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", line)
                            if match:
                                return match.group(1)
                else:
                    # Most package managers just output the version
                    import re

                    match = re.search(r"(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)", version_output)
                    if match:
                        return match.group(1)

                return version_output.split("\n")[0]  # First line as fallback

        except Exception as e:
            logger.debug(f"Error getting version for {manager.value}: {e}")

        return None

    def get_primary_manager(self) -> Optional[PackageManagerInfo]:
        """
        Get the primary package manager for the project.

        Returns:
            Primary package manager info
        """
        if not self.detected_managers:
            self.detect_package_managers()

        if not self.detected_managers:
            return None

        # Priority order for selection
        priority_order = [
            PackageManager.POETRY,  # Python projects
            PackageManager.PIPENV,
            PackageManager.PNPM,  # JavaScript projects
            PackageManager.YARN,
            PackageManager.BUN,
            PackageManager.NPM,
            PackageManager.CARGO,  # Rust projects
            PackageManager.GO,  # Go projects
            PackageManager.COMPOSER,  # PHP projects
            PackageManager.MAVEN,  # Java projects
            PackageManager.GRADLE,
            PackageManager.DOTNET,  # .NET projects
            PackageManager.CONDA,  # Data science projects
            PackageManager.PIP,  # General Python
            PackageManager.DENO,  # Deno projects
        ]

        # Find highest priority manager
        for manager_type in priority_order:
            for manager_info in self.detected_managers:
                if manager_info.name == manager_type:
                    return manager_info

        # Return first detected if none match priority
        return self.detected_managers[0]

    def get_install_command(self, manager: Optional[PackageManager] = None) -> str:
        """
        Get install command for the specified or primary manager.

        Args:
            manager: Specific manager to use

        Returns:
            Install command string
        """
        if manager:
            manager_info = next(
                (m for m in self.detected_managers if m.name == manager), None
            )
        else:
            manager_info = self.get_primary_manager()

        if manager_info:
            return manager_info.install_command

        return "# No package manager detected"

    def get_update_command(self, manager: Optional[PackageManager] = None) -> str:
        """
        Get update command for the specified or primary manager.

        Args:
            manager: Specific manager to use

        Returns:
            Update command string
        """
        if manager:
            manager_info = next(
                (m for m in self.detected_managers if m.name == manager), None
            )
        else:
            manager_info = self.get_primary_manager()

        if manager_info:
            return manager_info.update_command

        return "# No package manager detected"

    def get_dev_command(
        self, manager: Optional[PackageManager] = None
    ) -> Optional[str]:
        """
        Get development/run command for the specified or primary manager.

        Args:
            manager: Specific manager to use

        Returns:
            Development command string or None
        """
        if manager:
            manager_info = next(
                (m for m in self.detected_managers if m.name == manager), None
            )
        else:
            manager_info = self.get_primary_manager()

        if manager_info:
            return manager_info.dev_command

        return None

    def generate_project_commands(self) -> Dict[str, str]:
        """
        Generate common project commands based on detected package managers.

        Returns:
            Dictionary of command name -> command string
        """
        commands = {}
        primary_manager = self.get_primary_manager()

        if not primary_manager:
            return commands

        # Basic commands
        commands["install"] = primary_manager.install_command
        commands["update"] = primary_manager.update_command

        # Optional commands
        if primary_manager.dev_command:
            commands["dev"] = primary_manager.dev_command

        if primary_manager.build_command:
            commands["build"] = primary_manager.build_command

        if primary_manager.test_command:
            commands["test"] = primary_manager.test_command

        return commands

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get comprehensive project information.

        Returns:
            Dictionary with project information
        """
        self.detect_package_managers()
        primary_manager = self.get_primary_manager()

        info = {
            "project_root": str(self.project_root),
            "detected_managers": [
                {
                    "name": m.name.value,
                    "version": m.version,
                    "executable": m.executable_path,
                    "config_files": [str(f) for f in m.config_files],
                    "lock_files": [str(f) for f in m.lock_files],
                }
                for m in self.detected_managers
            ],
            "primary_manager": primary_manager.name.value if primary_manager else None,
            "commands": self.generate_project_commands(),
        }

        return info

    def suggest_updates(self) -> List[str]:
        """
        Suggest update commands based on detected package managers.

        Returns:
            List of suggested update commands
        """
        suggestions = []

        for manager_info in self.detected_managers:
            # Check if updates are available (basic heuristic)
            if manager_info.lock_files:
                suggestions.append(
                    f"Run `{manager_info.update_command}` to update {manager_info.name.value} dependencies"
                )

            # Suggest version updates for the package manager itself
            if manager_info.version:
                suggestions.append(
                    f"Current {manager_info.name.value} version: {manager_info.version}"
                )

        return suggestions


# Global detector instance
_detector = None


def get_package_detector(project_root: Optional[Path] = None) -> PackageManagerDetector:
    """
    Get global package manager detector instance.

    Args:
        project_root: Project root directory

    Returns:
        PackageManagerDetector instance
    """
    global _detector
    if _detector is None or (project_root and _detector.project_root != project_root):
        _detector = PackageManagerDetector(project_root)
    return _detector


def detect_installer_by_path() -> Optional[PackageManager]:
    """
    Detect package manager by analyzing the current installation path.

    Returns:
        Detected package manager or None
    """
    try:
        # Check how this package was installed
        import kritrima_ai

        install_path = Path(kritrima_ai.__file__).parent

        # Check for package manager indicators in path
        path_str = str(install_path).lower()

        if "site-packages" in path_str:
            return PackageManager.PIP
        elif "poetry" in path_str:
            return PackageManager.POETRY
        elif "pipenv" in path_str:
            return PackageManager.PIPENV
        elif "conda" in path_str or "anaconda" in path_str or "miniconda" in path_str:
            return PackageManager.CONDA

    except Exception as e:
        logger.debug(f"Error detecting installer by path: {e}")

    return None


def get_update_command_for_kritrima() -> str:
    """
    Get the appropriate update command for Kritrima AI CLI.

    Returns:
        Update command string
    """
    installer = detect_installer_by_path()

    if installer == PackageManager.PIP:
        return "pip install --upgrade kritrima-ai"
    elif installer == PackageManager.POETRY:
        return "poetry update kritrima-ai"
    elif installer == PackageManager.PIPENV:
        return "pipenv update kritrima-ai"
    elif installer == PackageManager.CONDA:
        return "conda update kritrima-ai"
    else:
        # Default to pip
        return "pip install --upgrade kritrima-ai"
