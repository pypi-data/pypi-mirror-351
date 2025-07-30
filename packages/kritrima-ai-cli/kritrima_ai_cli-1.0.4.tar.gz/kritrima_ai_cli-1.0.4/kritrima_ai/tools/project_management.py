"""
Project management tool for Kritrima AI CLI.

This module provides comprehensive project management capabilities including:
- Project structure analysis and management
- Dependency management and analysis
- Build system integration
- Project configuration management
- Development workflow automation
"""

import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import toml

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.security.sandbox import SandboxManager
from kritrima_ai.utils.file_utils import read_file_safe
from kritrima_ai.utils.git_utils import get_git_status
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProjectDependency:
    """Represents a project dependency."""

    name: str
    version: Optional[str]
    type: str  # 'runtime', 'dev', 'build', 'test'
    source: str  # 'pip', 'npm', 'cargo', etc.
    description: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None


@dataclass
class ProjectInfo:
    """Complete project information."""

    name: str
    root_path: Path
    project_type: str
    language: str
    version: Optional[str]
    description: Optional[str]
    dependencies: List[ProjectDependency]
    dev_dependencies: List[ProjectDependency]
    build_dependencies: List[ProjectDependency]
    config_files: List[Path]
    entry_points: List[Path]
    test_directories: List[Path]
    documentation_files: List[Path]
    build_system: Optional[str]
    package_manager: Optional[str]
    git_info: Optional[Dict[str, Any]]


class ProjectManagementTool(BaseTool):
    """
    Comprehensive project management tool.

    Provides project analysis, dependency management, and development
    workflow automation capabilities.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize project management tool.

        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.sandbox = SandboxManager(config)

        # Project type detectors
        self.project_detectors = {
            "python": self._detect_python_project,
            "javascript": self._detect_javascript_project,
            "typescript": self._detect_typescript_project,
            "rust": self._detect_rust_project,
            "go": self._detect_go_project,
            "java": self._detect_java_project,
            "cpp": self._detect_cpp_project,
        }

        # Dependency parsers
        self.dependency_parsers = {
            "requirements.txt": self._parse_requirements_txt,
            "pyproject.toml": self._parse_pyproject_toml,
            "package.json": self._parse_package_json,
            "Cargo.toml": self._parse_cargo_toml,
            "go.mod": self._parse_go_mod,
            "pom.xml": self._parse_pom_xml,
            "build.gradle": self._parse_gradle,
            "CMakeLists.txt": self._parse_cmake,
        }

        logger.info("Project management tool initialized")

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the project management tool."""
        return create_tool_metadata(
            name="project_management",
            description="Analyze and manage project structure, dependencies, and development workflows",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            "analyze_project",
                            "install_dependencies",
                            "run_tests",
                            "build_project",
                            "dependency_info",
                            "project_structure",
                        ],
                        "description": "The project management operation to perform",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project root directory (defaults to current directory)",
                    },
                    "dev_dependencies": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to include development dependencies",
                    },
                    "test_pattern": {
                        "type": "string",
                        "description": "Test pattern or specific test to run",
                    },
                    "build_target": {
                        "type": "string",
                        "description": "Specific build target or configuration",
                    },
                    "include_git": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include Git information in analysis",
                    },
                },
                required=["operation"],
            ),
            category="development",
            risk_level="medium",
            requires_approval=True,
            supports_streaming=True,
            examples=[
                {
                    "description": "Analyze current project",
                    "parameters": {"operation": "analyze_project"},
                },
                {
                    "description": "Install project dependencies",
                    "parameters": {
                        "operation": "install_dependencies",
                        "dev_dependencies": True,
                    },
                },
                {
                    "description": "Run project tests",
                    "parameters": {"operation": "run_tests"},
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute project management operations.

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

            project_path = kwargs.get("project_path")

            # Route to appropriate method based on operation
            if operation == "analyze_project":
                result = await self.analyze_project(project_path)
                return ToolExecutionResult(
                    success=True, result=self._format_project_info(result)
                )
            elif operation == "install_dependencies":
                dev_dependencies = kwargs.get("dev_dependencies", False)
                result = await self.install_dependencies(project_path, dev_dependencies)
                return ToolExecutionResult(success=True, result=result)
            elif operation == "run_tests":
                test_pattern = kwargs.get("test_pattern")
                result = await self.run_tests(project_path, test_pattern)
                return ToolExecutionResult(success=True, result=result)
            elif operation == "build_project":
                build_target = kwargs.get("build_target")
                result = await self.build_project(project_path, build_target)
                return ToolExecutionResult(success=True, result=result)
            elif operation == "dependency_info":
                project_info = await self.analyze_project(project_path)
                result = self._format_dependency_info(project_info)
                return ToolExecutionResult(success=True, result=result)
            elif operation == "project_structure":
                project_info = await self.analyze_project(project_path)
                result = self._format_project_structure(project_info)
                return ToolExecutionResult(success=True, result=result)
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

        except Exception as e:
            logger.error(f"Error in project management: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute project management operations with streaming output.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming operation results
        """
        try:
            operation = kwargs.get("operation")
            project_path = kwargs.get("project_path")

            yield f"Starting {operation}...\n"

            if operation == "analyze_project":
                yield "Analyzing project structure...\n"
                result = await self.analyze_project(project_path)
                yield self._format_project_info(result)
            elif operation == "install_dependencies":
                dev_dependencies = kwargs.get("dev_dependencies", False)
                async for output in self._stream_dependency_installation(
                    project_path, dev_dependencies
                ):
                    yield output
            elif operation == "run_tests":
                test_pattern = kwargs.get("test_pattern")
                async for output in self._stream_test_execution(
                    project_path, test_pattern
                ):
                    yield output
            elif operation == "build_project":
                build_target = kwargs.get("build_target")
                async for output in self._stream_build_process(
                    project_path, build_target
                ):
                    yield output
            else:
                # Fall back to regular execution
                result = await self.execute(**kwargs)
                if result.success:
                    yield str(result.result)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error in streaming operation: {str(e)}"

    async def _stream_dependency_installation(
        self, project_path: Optional[str], dev_dependencies: bool
    ) -> AsyncIterator[str]:
        """Stream dependency installation process."""
        try:
            yield "Installing dependencies...\n"
            result = await self.install_dependencies(project_path, dev_dependencies)
            yield result
        except Exception as e:
            yield f"Error installing dependencies: {str(e)}\n"

    async def _stream_test_execution(
        self, project_path: Optional[str], test_pattern: Optional[str]
    ) -> AsyncIterator[str]:
        """Stream test execution process."""
        try:
            yield "Running tests...\n"
            result = await self.run_tests(project_path, test_pattern)
            yield result
        except Exception as e:
            yield f"Error running tests: {str(e)}\n"

    async def _stream_build_process(
        self, project_path: Optional[str], build_target: Optional[str]
    ) -> AsyncIterator[str]:
        """Stream build process."""
        try:
            yield "Building project...\n"
            result = await self.build_project(project_path, build_target)
            yield result
        except Exception as e:
            yield f"Error building project: {str(e)}\n"

    def _format_project_info(self, project_info: ProjectInfo) -> str:
        """Format project information for display."""
        lines = [
            f"Project Analysis: {project_info.name}",
            f"Type: {project_info.project_type}",
            f"Language: {project_info.language}",
            f"Version: {project_info.version or 'Unknown'}",
            f"Root Path: {project_info.root_path}",
            "",
        ]

        if project_info.description:
            lines.append(f"Description: {project_info.description}")
            lines.append("")

        lines.extend(
            [
                f"Dependencies: {len(project_info.dependencies)}",
                f"Dev Dependencies: {len(project_info.dev_dependencies)}",
                f"Build Dependencies: {len(project_info.build_dependencies)}",
                f"Config Files: {len(project_info.config_files)}",
                f"Entry Points: {len(project_info.entry_points)}",
                f"Test Directories: {len(project_info.test_directories)}",
                "",
            ]
        )

        if project_info.build_system:
            lines.append(f"Build System: {project_info.build_system}")
        if project_info.package_manager:
            lines.append(f"Package Manager: {project_info.package_manager}")

        if project_info.git_info:
            lines.extend(
                [
                    "",
                    "Git Information:",
                    f"  Branch: {project_info.git_info.get('branch', 'Unknown')}",
                    f"  Status: {project_info.git_info.get('status', 'Unknown')}",
                ]
            )

        return "\n".join(lines)

    def _format_dependency_info(self, project_info: ProjectInfo) -> str:
        """Format dependency information."""
        lines = [f"Dependencies for {project_info.name}"]

        if project_info.dependencies:
            lines.append("\nRuntime Dependencies:")
            for dep in project_info.dependencies[:10]:  # Show first 10
                lines.append(f"  - {dep.name} {dep.version or ''} ({dep.source})")

        if project_info.dev_dependencies:
            lines.append("\nDevelopment Dependencies:")
            for dep in project_info.dev_dependencies[:10]:  # Show first 10
                lines.append(f"  - {dep.name} {dep.version or ''} ({dep.source})")

        return "\n".join(lines)

    def _format_project_structure(self, project_info: ProjectInfo) -> str:
        """Format project structure information."""
        lines = [f"Project Structure: {project_info.name}"]

        if project_info.entry_points:
            lines.append("\nEntry Points:")
            for entry in project_info.entry_points:
                lines.append(f"  - {entry.relative_to(project_info.root_path)}")

        if project_info.config_files:
            lines.append("\nConfiguration Files:")
            for config in project_info.config_files:
                lines.append(f"  - {config.relative_to(project_info.root_path)}")

        if project_info.test_directories:
            lines.append("\nTest Directories:")
            for test_dir in project_info.test_directories:
                lines.append(f"  - {test_dir.relative_to(project_info.root_path)}")

        return "\n".join(lines)

    async def analyze_project(self, project_path: Optional[str] = None) -> ProjectInfo:
        """
        Analyze a project and extract comprehensive information.

        Args:
            project_path: Path to project root (defaults to current directory)

        Returns:
            Complete project information
        """
        try:
            root_path = Path(project_path).resolve() if project_path else Path.cwd()

            # Security check
            if not self.sandbox.is_path_allowed(root_path, "read"):
                raise PermissionError(f"Access denied to project: {root_path}")

            if not root_path.exists():
                raise FileNotFoundError(f"Project path not found: {root_path}")

            logger.info(f"Analyzing project: {root_path}")

            # Detect project type and language
            project_type, language = self._detect_project_type(root_path)

            # Get basic project info
            name, version, description = self._extract_basic_info(
                root_path, project_type
            )

            # Find configuration files
            config_files = self._find_config_files(root_path)

            # Parse dependencies
            dependencies, dev_dependencies, build_dependencies = (
                await self._parse_dependencies(root_path, config_files)
            )

            # Find entry points
            entry_points = self._find_entry_points(root_path, language)

            # Find test directories
            test_directories = self._find_test_directories(root_path)

            # Find documentation
            documentation_files = self._find_documentation_files(root_path)

            # Detect build system and package manager
            build_system = self._detect_build_system(root_path, config_files)
            package_manager = self._detect_package_manager(root_path, config_files)

            # Get Git information
            git_info = self._get_git_info(root_path)

            project_info = ProjectInfo(
                name=name,
                root_path=root_path,
                project_type=project_type,
                language=language,
                version=version,
                description=description,
                dependencies=dependencies,
                dev_dependencies=dev_dependencies,
                build_dependencies=build_dependencies,
                config_files=config_files,
                entry_points=entry_points,
                test_directories=test_directories,
                documentation_files=documentation_files,
                build_system=build_system,
                package_manager=package_manager,
                git_info=git_info,
            )

            logger.info(f"Project analysis completed: {name} ({project_type})")
            return project_info

        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            raise

    async def install_dependencies(
        self, project_path: Optional[str] = None, dev_dependencies: bool = False
    ) -> str:
        """
        Install project dependencies.

        Args:
            project_path: Path to project root
            dev_dependencies: Whether to install development dependencies

        Returns:
            Installation result message
        """
        try:
            root_path = Path(project_path).resolve() if project_path else Path.cwd()
            project_info = await self.analyze_project(str(root_path))

            if not project_info.package_manager:
                return "No package manager detected for this project"

            # Build installation command
            commands = []

            if project_info.package_manager == "pip":
                if (root_path / "requirements.txt").exists():
                    commands.append(["pip", "install", "-r", "requirements.txt"])
                if dev_dependencies and (root_path / "requirements-dev.txt").exists():
                    commands.append(["pip", "install", "-r", "requirements-dev.txt"])
                if (root_path / "pyproject.toml").exists():
                    commands.append(["pip", "install", "-e", "."])

            elif project_info.package_manager == "npm":
                cmd = ["npm", "install"]
                if not dev_dependencies:
                    cmd.append("--production")
                commands.append(cmd)

            elif project_info.package_manager == "yarn":
                cmd = ["yarn", "install"]
                if not dev_dependencies:
                    cmd.append("--production")
                commands.append(cmd)

            elif project_info.package_manager == "cargo":
                commands.append(["cargo", "build"])

            elif project_info.package_manager == "go":
                commands.append(["go", "mod", "download"])

            # Execute commands
            results = []
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=root_path,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes timeout
                    )

                    if result.returncode == 0:
                        results.append(f"✓ {' '.join(cmd)} - Success")
                    else:
                        results.append(f"✗ {' '.join(cmd)} - Failed: {result.stderr}")

                except subprocess.TimeoutExpired:
                    results.append(f"✗ {' '.join(cmd)} - Timeout")
                except Exception as e:
                    results.append(f"✗ {' '.join(cmd)} - Error: {e}")

            return "\n".join(results)

        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            raise

    async def run_tests(self, project_path: Optional[str] = None) -> str:
        """
        Run project tests.

        Args:
            project_path: Path to project root

        Returns:
            Test execution result
        """
        try:
            root_path = Path(project_path).resolve() if project_path else Path.cwd()
            project_info = await self.analyze_project(str(root_path))

            # Determine test command based on project type
            test_commands = []

            if project_info.language == "python":
                if (root_path / "pytest.ini").exists() or any(
                    "pytest" in str(f) for f in project_info.config_files
                ):
                    test_commands.append(["pytest"])
                elif (root_path / "setup.py").exists():
                    test_commands.append(["python", "setup.py", "test"])
                elif project_info.test_directories:
                    test_commands.append(["python", "-m", "unittest", "discover"])

            elif project_info.language in ["javascript", "typescript"]:
                if (root_path / "package.json").exists():
                    # Check for test script in package.json
                    package_json = json.loads(
                        read_file_safe(root_path / "package.json")
                    )
                    if "scripts" in package_json and "test" in package_json["scripts"]:
                        test_commands.append(["npm", "test"])
                    else:
                        test_commands.append(["npm", "run", "test"])

            elif project_info.language == "rust":
                test_commands.append(["cargo", "test"])

            elif project_info.language == "go":
                test_commands.append(["go", "test", "./..."])

            elif project_info.language == "java":
                if (root_path / "pom.xml").exists():
                    test_commands.append(["mvn", "test"])
                elif (root_path / "build.gradle").exists():
                    test_commands.append(["gradle", "test"])

            if not test_commands:
                return "No test framework detected for this project"

            # Execute test commands
            results = []
            for cmd in test_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=root_path,
                        capture_output=True,
                        text=True,
                        timeout=600,  # 10 minutes timeout
                    )

                    results.append(f"Command: {' '.join(cmd)}")
                    results.append(f"Exit code: {result.returncode}")

                    if result.stdout:
                        results.append("STDOUT:")
                        results.append(result.stdout)

                    if result.stderr:
                        results.append("STDERR:")
                        results.append(result.stderr)

                    results.append("-" * 50)

                except subprocess.TimeoutExpired:
                    results.append(f"✗ {' '.join(cmd)} - Timeout")
                except Exception as e:
                    results.append(f"✗ {' '.join(cmd)} - Error: {e}")

            return "\n".join(results)

        except Exception as e:
            logger.error(f"Error running tests: {e}")
            raise

    async def build_project(self, project_path: Optional[str] = None) -> str:
        """
        Build the project.

        Args:
            project_path: Path to project root

        Returns:
            Build result message
        """
        try:
            root_path = Path(project_path).resolve() if project_path else Path.cwd()
            project_info = await self.analyze_project(str(root_path))

            # Determine build command based on build system
            build_commands = []

            if project_info.build_system == "setuptools":
                build_commands.append(["python", "setup.py", "build"])
            elif project_info.build_system == "poetry":
                build_commands.append(["poetry", "build"])
            elif project_info.build_system == "webpack":
                build_commands.append(["npm", "run", "build"])
            elif project_info.build_system == "cargo":
                build_commands.append(["cargo", "build", "--release"])
            elif project_info.build_system == "go":
                build_commands.append(["go", "build"])
            elif project_info.build_system == "maven":
                build_commands.append(["mvn", "compile"])
            elif project_info.build_system == "gradle":
                build_commands.append(["gradle", "build"])
            elif project_info.build_system == "cmake":
                build_commands.extend([["cmake", "."], ["make"]])

            if not build_commands:
                return "No build system detected for this project"

            # Execute build commands
            results = []
            for cmd in build_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=root_path,
                        capture_output=True,
                        text=True,
                        timeout=600,  # 10 minutes timeout
                    )

                    if result.returncode == 0:
                        results.append(f"✓ {' '.join(cmd)} - Success")
                    else:
                        results.append(f"✗ {' '.join(cmd)} - Failed")
                        if result.stderr:
                            results.append(f"Error: {result.stderr}")

                except subprocess.TimeoutExpired:
                    results.append(f"✗ {' '.join(cmd)} - Timeout")
                except Exception as e:
                    results.append(f"✗ {' '.join(cmd)} - Error: {e}")

            return "\n".join(results)

        except Exception as e:
            logger.error(f"Error building project: {e}")
            raise

    def _detect_project_type(self, root_path: Path) -> Tuple[str, str]:
        """Detect project type and primary language."""
        # Check for specific project files
        if (root_path / "pyproject.toml").exists() or (root_path / "setup.py").exists():
            return "python_package", "python"
        elif (root_path / "package.json").exists():
            package_json = json.loads(read_file_safe(root_path / "package.json"))
            if "dependencies" in package_json and "@types" in str(
                package_json.get("devDependencies", {})
            ):
                return "typescript_project", "typescript"
            else:
                return "javascript_project", "javascript"
        elif (root_path / "Cargo.toml").exists():
            return "rust_project", "rust"
        elif (root_path / "go.mod").exists():
            return "go_project", "go"
        elif (root_path / "pom.xml").exists():
            return "java_maven", "java"
        elif (root_path / "build.gradle").exists():
            return "java_gradle", "java"
        elif (root_path / "CMakeLists.txt").exists():
            return "cpp_cmake", "cpp"
        else:
            # Fallback: detect by file extensions
            languages = defaultdict(int)
            for file_path in root_path.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext == ".py":
                        languages["python"] += 1
                    elif ext in [".js", ".jsx"]:
                        languages["javascript"] += 1
                    elif ext in [".ts", ".tsx"]:
                        languages["typescript"] += 1
                    elif ext == ".rs":
                        languages["rust"] += 1
                    elif ext == ".go":
                        languages["go"] += 1
                    elif ext == ".java":
                        languages["java"] += 1
                    elif ext in [".cpp", ".cc", ".cxx"]:
                        languages["cpp"] += 1

            if languages:
                primary_language = max(languages, key=languages.get)
                return f"{primary_language}_project", primary_language
            else:
                return "unknown", "unknown"

    def _extract_basic_info(
        self, root_path: Path, project_type: str
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """Extract basic project information."""
        name = root_path.name
        version = None
        description = None

        # Try to extract from project files
        if (root_path / "pyproject.toml").exists():
            try:
                pyproject = toml.load(root_path / "pyproject.toml")
                if "project" in pyproject:
                    name = pyproject["project"].get("name", name)
                    version = pyproject["project"].get("version")
                    description = pyproject["project"].get("description")
                elif "tool" in pyproject and "poetry" in pyproject["tool"]:
                    poetry = pyproject["tool"]["poetry"]
                    name = poetry.get("name", name)
                    version = poetry.get("version")
                    description = poetry.get("description")
            except Exception:
                pass

        elif (root_path / "package.json").exists():
            try:
                package = json.loads(read_file_safe(root_path / "package.json"))
                name = package.get("name", name)
                version = package.get("version")
                description = package.get("description")
            except Exception:
                pass

        elif (root_path / "Cargo.toml").exists():
            try:
                cargo = toml.load(root_path / "Cargo.toml")
                if "package" in cargo:
                    name = cargo["package"].get("name", name)
                    version = cargo["package"].get("version")
                    description = cargo["package"].get("description")
            except Exception:
                pass

        return name, version, description

    def _find_config_files(self, root_path: Path) -> List[Path]:
        """Find configuration files in the project."""
        config_patterns = [
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements*.txt",
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "Cargo.toml",
            "Cargo.lock",
            "go.mod",
            "go.sum",
            "pom.xml",
            "build.gradle",
            "gradle.properties",
            "CMakeLists.txt",
            "Makefile",
            "tsconfig.json",
            "webpack.config.js",
            "babel.config.js",
            "pytest.ini",
            "tox.ini",
            ".flake8",
            "mypy.ini",
            ".eslintrc*",
            ".prettierrc*",
            "jest.config.js",
        ]

        config_files = []
        for pattern in config_patterns:
            for file_path in root_path.glob(pattern):
                if file_path.is_file():
                    config_files.append(file_path)

        return config_files

    async def _parse_dependencies(
        self, root_path: Path, config_files: List[Path]
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse project dependencies from configuration files."""
        dependencies = []
        dev_dependencies = []
        build_dependencies = []

        for config_file in config_files:
            file_name = config_file.name

            if file_name in self.dependency_parsers:
                try:
                    deps, dev_deps, build_deps = await self.dependency_parsers[
                        file_name
                    ](config_file)
                    dependencies.extend(deps)
                    dev_dependencies.extend(dev_deps)
                    build_dependencies.extend(build_deps)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse dependencies from {config_file}: {e}"
                    )

        return dependencies, dev_dependencies, build_dependencies

    async def _parse_requirements_txt(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse requirements.txt file."""
        content = read_file_safe(file_path)
        dependencies = []

        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # Simple parsing - could be enhanced
                if "==" in line:
                    name, version = line.split("==", 1)
                elif ">=" in line:
                    name, version = line.split(">=", 1)
                    version = f">={version}"
                else:
                    name, version = line, None

                dependencies.append(
                    ProjectDependency(
                        name=name.strip(),
                        version=version.strip() if version else None,
                        type="runtime",
                        source="pip",
                    )
                )

        return dependencies, [], []

    async def _parse_pyproject_toml(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse pyproject.toml file."""
        try:
            data = toml.load(file_path)
            dependencies = []
            dev_dependencies = []
            build_dependencies = []

            # Standard project dependencies
            if "project" in data and "dependencies" in data["project"]:
                for dep in data["project"]["dependencies"]:
                    name, version = self._parse_dependency_spec(dep)
                    dependencies.append(
                        ProjectDependency(
                            name=name, version=version, type="runtime", source="pip"
                        )
                    )

            # Poetry dependencies
            if "tool" in data and "poetry" in data["tool"]:
                poetry = data["tool"]["poetry"]

                if "dependencies" in poetry:
                    for name, spec in poetry["dependencies"].items():
                        if name != "python":
                            version = (
                                spec if isinstance(spec, str) else spec.get("version")
                            )
                            dependencies.append(
                                ProjectDependency(
                                    name=name,
                                    version=version,
                                    type="runtime",
                                    source="pip",
                                )
                            )

                if "dev-dependencies" in poetry:
                    for name, spec in poetry["dev-dependencies"].items():
                        version = spec if isinstance(spec, str) else spec.get("version")
                        dev_dependencies.append(
                            ProjectDependency(
                                name=name, version=version, type="dev", source="pip"
                            )
                        )

            return dependencies, dev_dependencies, build_dependencies

        except Exception as e:
            logger.warning(f"Error parsing pyproject.toml: {e}")
            return [], [], []

    async def _parse_package_json(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse package.json file."""
        try:
            data = json.loads(read_file_safe(file_path))
            dependencies = []
            dev_dependencies = []

            if "dependencies" in data:
                for name, version in data["dependencies"].items():
                    dependencies.append(
                        ProjectDependency(
                            name=name, version=version, type="runtime", source="npm"
                        )
                    )

            if "devDependencies" in data:
                for name, version in data["devDependencies"].items():
                    dev_dependencies.append(
                        ProjectDependency(
                            name=name, version=version, type="dev", source="npm"
                        )
                    )

            return dependencies, dev_dependencies, []

        except Exception as e:
            logger.warning(f"Error parsing package.json: {e}")
            return [], [], []

    async def _parse_cargo_toml(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse Cargo.toml file."""
        try:
            data = toml.load(file_path)
            dependencies = []
            dev_dependencies = []
            build_dependencies = []

            if "dependencies" in data:
                for name, spec in data["dependencies"].items():
                    version = spec if isinstance(spec, str) else spec.get("version")
                    dependencies.append(
                        ProjectDependency(
                            name=name, version=version, type="runtime", source="cargo"
                        )
                    )

            if "dev-dependencies" in data:
                for name, spec in data["dev-dependencies"].items():
                    version = spec if isinstance(spec, str) else spec.get("version")
                    dev_dependencies.append(
                        ProjectDependency(
                            name=name, version=version, type="dev", source="cargo"
                        )
                    )

            if "build-dependencies" in data:
                for name, spec in data["build-dependencies"].items():
                    version = spec if isinstance(spec, str) else spec.get("version")
                    build_dependencies.append(
                        ProjectDependency(
                            name=name, version=version, type="build", source="cargo"
                        )
                    )

            return dependencies, dev_dependencies, build_dependencies

        except Exception as e:
            logger.warning(f"Error parsing Cargo.toml: {e}")
            return [], [], []

    async def _parse_go_mod(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse go.mod file."""
        # Simplified go.mod parsing
        return [], [], []

    async def _parse_pom_xml(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse pom.xml file."""
        # Simplified pom.xml parsing
        return [], [], []

    async def _parse_gradle(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse build.gradle file."""
        # Simplified gradle parsing
        return [], [], []

    async def _parse_cmake(
        self, file_path: Path
    ) -> Tuple[
        List[ProjectDependency], List[ProjectDependency], List[ProjectDependency]
    ]:
        """Parse CMakeLists.txt file."""
        # Simplified cmake parsing
        return [], [], []

    def _parse_dependency_spec(self, spec: str) -> Tuple[str, Optional[str]]:
        """Parse dependency specification string."""
        # Simple parsing - could be enhanced
        for op in [">=", "<=", "==", ">", "<", "~="]:
            if op in spec:
                name, version = spec.split(op, 1)
                return name.strip(), f"{op}{version.strip()}"

        return spec.strip(), None

    def _find_entry_points(self, root_path: Path, language: str) -> List[Path]:
        """Find likely entry point files."""
        entry_points = []

        common_names = ["main", "index", "app", "server", "__main__"]

        if language == "python":
            for name in common_names:
                for ext in [".py"]:
                    file_path = root_path / f"{name}{ext}"
                    if file_path.exists():
                        entry_points.append(file_path)

        elif language in ["javascript", "typescript"]:
            for name in common_names:
                for ext in [".js", ".ts", ".jsx", ".tsx"]:
                    file_path = root_path / f"{name}{ext}"
                    if file_path.exists():
                        entry_points.append(file_path)

        # Check for src directory
        src_dir = root_path / "src"
        if src_dir.exists():
            for name in common_names:
                for file_path in src_dir.glob(f"{name}.*"):
                    if file_path.is_file():
                        entry_points.append(file_path)

        return entry_points

    def _find_test_directories(self, root_path: Path) -> List[Path]:
        """Find test directories."""
        test_dirs = []

        common_test_dirs = ["test", "tests", "spec", "__tests__"]

        for dir_name in common_test_dirs:
            test_dir = root_path / dir_name
            if test_dir.exists() and test_dir.is_dir():
                test_dirs.append(test_dir)

        return test_dirs

    def _find_documentation_files(self, root_path: Path) -> List[Path]:
        """Find documentation files."""
        doc_files = []

        doc_patterns = ["README*", "CHANGELOG*", "LICENSE*", "CONTRIBUTING*", "docs/*"]

        for pattern in doc_patterns:
            for file_path in root_path.glob(pattern):
                if file_path.is_file():
                    doc_files.append(file_path)

        return doc_files

    def _detect_build_system(
        self, root_path: Path, config_files: List[Path]
    ) -> Optional[str]:
        """Detect build system."""
        config_names = [f.name for f in config_files]

        if "pyproject.toml" in config_names:
            # Check if it's poetry or setuptools
            try:
                pyproject = toml.load(root_path / "pyproject.toml")
                if "tool" in pyproject and "poetry" in pyproject["tool"]:
                    return "poetry"
                else:
                    return "setuptools"
            except Exception:
                return "setuptools"
        elif "setup.py" in config_names:
            return "setuptools"
        elif "package.json" in config_names:
            return "webpack"  # Simplified
        elif "Cargo.toml" in config_names:
            return "cargo"
        elif "go.mod" in config_names:
            return "go"
        elif "pom.xml" in config_names:
            return "maven"
        elif "build.gradle" in config_names:
            return "gradle"
        elif "CMakeLists.txt" in config_names:
            return "cmake"

        return None

    def _detect_package_manager(
        self, root_path: Path, config_files: List[Path]
    ) -> Optional[str]:
        """Detect package manager."""
        config_names = [f.name for f in config_files]

        if (
            any(name.startswith("requirements") for name in config_names)
            or "pyproject.toml" in config_names
        ):
            return "pip"
        elif "yarn.lock" in config_names:
            return "yarn"
        elif "package.json" in config_names:
            return "npm"
        elif "Cargo.toml" in config_names:
            return "cargo"
        elif "go.mod" in config_names:
            return "go"

        return None

    def _get_git_info(self, root_path: Path) -> Optional[Dict[str, Any]]:
        """Get Git repository information."""
        try:
            git_status = get_git_status(str(root_path))
            if git_status.is_repo:
                return {
                    "branch": git_status.branch,
                    "commit_hash": git_status.commit_hash,
                    "remote_url": git_status.remote_url,
                    "has_changes": git_status.has_changes,
                    "untracked_files": len(git_status.untracked_files),
                    "modified_files": len(git_status.modified_files),
                    "staged_files": len(git_status.staged_files),
                }
        except Exception:
            pass

        return None

    # Placeholder methods for project type detectors
    def _detect_python_project(self, root_path: Path) -> bool:
        return (root_path / "pyproject.toml").exists() or (
            root_path / "setup.py"
        ).exists()

    def _detect_javascript_project(self, root_path: Path) -> bool:
        return (root_path / "package.json").exists()

    def _detect_typescript_project(self, root_path: Path) -> bool:
        return (root_path / "tsconfig.json").exists()

    def _detect_rust_project(self, root_path: Path) -> bool:
        return (root_path / "Cargo.toml").exists()

    def _detect_go_project(self, root_path: Path) -> bool:
        return (root_path / "go.mod").exists()

    def _detect_java_project(self, root_path: Path) -> bool:
        return (root_path / "pom.xml").exists() or (root_path / "build.gradle").exists()

    def _detect_cpp_project(self, root_path: Path) -> bool:
        return (root_path / "CMakeLists.txt").exists()
