"""
Full context analyzer for Kritrima AI CLI.

This module provides comprehensive project analysis capabilities including:
- Directory structure analysis
- Code dependency mapping
- Project documentation discovery
- Context optimization for AI processing
- Intelligent file filtering and prioritization
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Set

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.file_utils import is_text_file, read_file_safe
from kritrima_ai.utils.git_utils import get_git_files
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FileAnalysis:
    """Analysis result for a single file."""

    path: Path
    size: int
    lines: int
    language: str
    importance_score: float
    dependencies: tuple  # Changed from List[str] to tuple for hashability
    exports: tuple  # Changed from List[str] to tuple for hashability
    summary: str


@dataclass
class ProjectContext:
    """Complete project context analysis."""

    root_path: Path
    total_files: int
    total_size: int
    languages: Dict[str, int]
    file_analyses: List[FileAnalysis]
    dependency_graph: Dict[str, List[str]]
    documentation_files: List[Path]
    config_files: List[Path]
    entry_points: List[Path]
    context_summary: str


class FullContextAnalyzer(BaseTool):
    """
    Comprehensive project analysis tool for full context understanding.

    Analyzes project structure, dependencies, and generates optimized
    context for AI processing with intelligent file prioritization.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the full context analyzer.

        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.max_context_size = 100000  # 100KB default context limit
        self.important_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".scala",
            ".html",
            ".css",
            ".scss",
            ".less",
            ".vue",
            ".svelte",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".md",
            ".rst",
            ".txt",
            ".dockerfile",
            "makefile",
        }

        logger.info("Full context analyzer initialized")

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the full context analyzer tool."""
        return create_tool_metadata(
            name="full_context",
            description="Analyze project structure and generate optimized context for AI processing with intelligent file prioritization",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            "analyze_project",
                            "generate_context",
                            "file_analysis",
                            "dependency_graph",
                            "project_summary",
                        ],
                        "description": "The context analysis operation to perform",
                    },
                    "root_path": {
                        "type": "string",
                        "description": "Root directory to analyze (defaults to current directory)",
                    },
                    "max_files": {
                        "type": "integer",
                        "default": 200,
                        "description": "Maximum number of files to analyze",
                    },
                    "include_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File patterns to include (e.g., ['*.py', '*.js'])",
                    },
                    "exclude_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File patterns to exclude (e.g., ['node_modules/*', '*.pyc'])",
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific areas to focus on for context generation",
                    },
                    "max_context_size": {
                        "type": "integer",
                        "default": 100000,
                        "description": "Maximum context size in characters",
                    },
                },
                required=["operation"],
            ),
            category="analysis",
            risk_level="low",
            requires_approval=False,
            supports_streaming=True,
            examples=[
                {
                    "description": "Analyze current project structure",
                    "parameters": {"operation": "analyze_project"},
                },
                {
                    "description": "Generate optimized context for AI",
                    "parameters": {
                        "operation": "generate_context",
                        "max_context_size": 50000,
                    },
                },
                {
                    "description": "Get project dependency graph",
                    "parameters": {"operation": "dependency_graph"},
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute full context analysis operations.

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

            root_path = kwargs.get("root_path")
            max_files = kwargs.get("max_files", 200)
            include_patterns = kwargs.get("include_patterns")
            exclude_patterns = kwargs.get("exclude_patterns")

            # Route to appropriate method based on operation
            if operation == "analyze_project":
                result = await self.analyze_project(
                    root_path, max_files, include_patterns, exclude_patterns
                )
                return ToolExecutionResult(
                    success=True, result=self._format_project_context(result)
                )
            elif operation == "generate_context":
                focus_areas = kwargs.get("focus_areas")
                max_context_size = kwargs.get("max_context_size", 100000)
                project_context = await self.analyze_project(
                    root_path, max_files, include_patterns, exclude_patterns
                )
                context = await self.generate_optimized_context(
                    project_context, focus_areas, max_context_size
                )
                return ToolExecutionResult(success=True, result=context)
            elif operation == "file_analysis":
                project_context = await self.analyze_project(
                    root_path, max_files, include_patterns, exclude_patterns
                )
                result = self._format_file_analyses(project_context.file_analyses)
                return ToolExecutionResult(success=True, result=result)
            elif operation == "dependency_graph":
                project_context = await self.analyze_project(
                    root_path, max_files, include_patterns, exclude_patterns
                )
                result = self._format_dependency_graph(project_context.dependency_graph)
                return ToolExecutionResult(success=True, result=result)
            elif operation == "project_summary":
                project_context = await self.analyze_project(
                    root_path, max_files, include_patterns, exclude_patterns
                )
                return ToolExecutionResult(
                    success=True, result=project_context.context_summary
                )
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

        except Exception as e:
            logger.error(f"Error in full context analysis: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute full context analysis with streaming output.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming analysis results
        """
        try:
            operation = kwargs.get("operation")
            kwargs.get("root_path")

            yield f"Starting {operation}...\n"

            if operation == "analyze_project":
                async for output in self._stream_project_analysis(kwargs):
                    yield output
            elif operation == "generate_context":
                async for output in self._stream_context_generation(kwargs):
                    yield output
            else:
                # Fall back to regular execution
                result = await self.execute(**kwargs)
                if result.success:
                    yield str(result.result)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error in streaming analysis: {str(e)}"

    async def _stream_project_analysis(
        self, kwargs: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """Stream project analysis process."""
        try:
            root_path = kwargs.get("root_path")
            max_files = kwargs.get("max_files", 200)
            include_patterns = kwargs.get("include_patterns")
            exclude_patterns = kwargs.get("exclude_patterns")

            yield "Discovering files...\n"
            root = Path(root_path).resolve() if root_path else Path.cwd()
            files = await self._discover_files(
                root, max_files, include_patterns, exclude_patterns
            )
            yield f"Found {len(files)} files to analyze\n"

            yield "Analyzing files...\n"
            file_analyses = []
            for i, file_path in enumerate(files, 1):
                try:
                    yield f"[{i}/{len(files)}] Analyzing {file_path.name}...\n"
                    analysis = await self._analyze_file(file_path)
                    if analysis:
                        file_analyses.append(analysis)
                        yield f"✓ {file_path.name}: {analysis.language}, {analysis.lines} lines, score: {analysis.importance_score:.2f}\n"
                except Exception as e:
                    yield f"✗ {file_path.name}: Error - {str(e)}\n"

            yield "Building dependency graph...\n"
            dependency_graph = self._build_dependency_graph(file_analyses)
            yield f"Found {len(dependency_graph)} dependencies\n"

            yield "Analysis complete!\n"

        except Exception as e:
            yield f"Error in project analysis: {str(e)}\n"

    async def _stream_context_generation(
        self, kwargs: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """Stream context generation process."""
        try:
            yield "Analyzing project for context generation...\n"

            root_path = kwargs.get("root_path")
            max_files = kwargs.get("max_files", 200)
            include_patterns = kwargs.get("include_patterns")
            exclude_patterns = kwargs.get("exclude_patterns")
            focus_areas = kwargs.get("focus_areas")
            max_context_size = kwargs.get("max_context_size", 100000)

            project_context = await self.analyze_project(
                root_path, max_files, include_patterns, exclude_patterns
            )
            yield f"Analyzed {project_context.total_files} files\n"

            yield "Generating optimized context...\n"
            context = await self.generate_optimized_context(
                project_context, focus_areas, max_context_size
            )
            yield f"Generated context ({len(context)} characters)\n"
            yield context

        except Exception as e:
            yield f"Error in context generation: {str(e)}\n"

    def _format_project_context(self, project_context: ProjectContext) -> str:
        """Format project context for display."""
        lines = [
            f"Project Context Analysis: {project_context.root_path.name}",
            f"Total Files: {project_context.total_files}",
            f"Total Size: {project_context.total_size:,} bytes",
            "",
        ]

        # Language breakdown
        if project_context.languages:
            lines.append("Languages:")
            for lang, count in sorted(
                project_context.languages.items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(f"  {lang}: {count} files")
            lines.append("")

        # File categories
        lines.extend(
            [
                f"Documentation Files: {len(project_context.documentation_files)}",
                f"Configuration Files: {len(project_context.config_files)}",
                f"Entry Points: {len(project_context.entry_points)}",
                "",
            ]
        )

        # Top files by importance
        top_files = sorted(
            project_context.file_analyses,
            key=lambda x: x.importance_score,
            reverse=True,
        )[:10]
        if top_files:
            lines.append("Most Important Files:")
            for analysis in top_files:
                lines.append(f"  {analysis.path.name}: {analysis.importance_score:.2f}")
            lines.append("")

        lines.append("Summary:")
        lines.append(project_context.context_summary)

        return "\n".join(lines)

    def _format_file_analyses(self, file_analyses: List[FileAnalysis]) -> str:
        """Format file analysis results."""
        if not file_analyses:
            return "No files analyzed."

        lines = [f"File Analysis Results ({len(file_analyses)} files)"]

        # Sort by importance score
        sorted_analyses = sorted(
            file_analyses, key=lambda x: x.importance_score, reverse=True
        )

        for analysis in sorted_analyses[:20]:  # Show top 20
            lines.append(f"{analysis.path.name}:")
            lines.append(f"  Language: {analysis.language}")
            lines.append(f"  Lines: {analysis.lines}")
            lines.append(f"  Size: {analysis.size:,} bytes")
            lines.append(f"  Importance: {analysis.importance_score:.2f}")
            lines.append(f"  Dependencies: {len(analysis.dependencies)}")
            lines.append(f"  Exports: {len(analysis.exports)}")
            lines.append("")

        return "\n".join(lines)

    def _format_dependency_graph(self, dependency_graph: Dict[str, List[str]]) -> str:
        """Format dependency graph."""
        if not dependency_graph:
            return "No dependencies found."

        lines = [f"Dependency Graph ({len(dependency_graph)} files with dependencies)"]

        for file_path, deps in sorted(dependency_graph.items()):
            if deps:  # Only show files with dependencies
                lines.append(f"{Path(file_path).name}:")
                for dep in deps[:5]:  # Show first 5 dependencies
                    lines.append(f"  → {dep}")
                if len(deps) > 5:
                    lines.append(f"  ... and {len(deps) - 5} more")
                lines.append("")

        return "\n".join(lines)

    async def analyze_project(
        self,
        root_path: Optional[str] = None,
        max_files: int = 200,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> ProjectContext:
        """
        Perform comprehensive project analysis.

        Args:
            root_path: Root directory to analyze
            max_files: Maximum number of files to analyze
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude

        Returns:
            Complete project context analysis
        """
        try:
            root = Path(root_path).resolve() if root_path else Path.cwd()

            logger.info(f"Starting full context analysis of: {root}")

            # Discover files
            files = await self._discover_files(
                root, max_files, include_patterns, exclude_patterns
            )

            # Analyze individual files
            file_analyses = []
            total_size = 0
            languages = defaultdict(int)

            for file_path in files:
                try:
                    analysis = await self._analyze_file(file_path)
                    if analysis:
                        file_analyses.append(analysis)
                        total_size += analysis.size
                        languages[analysis.language] += 1
                except Exception as e:
                    logger.warning(f"Failed to analyze file {file_path}: {e}")

            # Build dependency graph
            dependency_graph = self._build_dependency_graph(file_analyses)

            # Categorize files
            documentation_files = self._find_documentation_files(file_analyses)
            config_files = self._find_config_files(file_analyses)
            entry_points = self._find_entry_points(file_analyses)

            # Generate context summary
            context_summary = self._generate_context_summary(
                root, file_analyses, dict(languages), dependency_graph
            )

            project_context = ProjectContext(
                root_path=root,
                total_files=len(file_analyses),
                total_size=total_size,
                languages=dict(languages),
                file_analyses=file_analyses,
                dependency_graph=dependency_graph,
                documentation_files=documentation_files,
                config_files=config_files,
                entry_points=entry_points,
                context_summary=context_summary,
            )

            logger.info(
                f"Project analysis completed: {len(file_analyses)} files analyzed"
            )
            return project_context

        except Exception as e:
            logger.error(f"Error in project analysis: {e}")
            raise

    async def generate_optimized_context(
        self,
        project_context: ProjectContext,
        focus_areas: Optional[List[str]] = None,
        max_context_size: Optional[int] = None,
    ) -> str:
        """
        Generate optimized context for AI processing.

        Args:
            project_context: Project analysis results
            focus_areas: Specific areas to focus on
            max_context_size: Maximum context size in characters

        Returns:
            Optimized context string
        """
        try:
            max_size = max_context_size or self.max_context_size

            # Prioritize files based on importance and focus areas
            prioritized_files = self._prioritize_files(
                project_context.file_analyses, focus_areas
            )

            context_parts = []
            current_size = 0

            # Add project summary
            summary = self._create_project_summary(project_context)
            context_parts.append(summary)
            current_size += len(summary)

            # Add high-priority files
            for analysis in prioritized_files:
                if current_size >= max_size:
                    break

                try:
                    file_content = read_file_safe(analysis.path)
                    file_section = self._format_file_section(analysis, file_content)

                    if current_size + len(file_section) <= max_size:
                        context_parts.append(file_section)
                        current_size += len(file_section)
                    else:
                        # Add truncated version
                        remaining_space = max_size - current_size - 200  # Buffer
                        if remaining_space > 500:  # Minimum useful size
                            truncated_content = (
                                file_content[:remaining_space] + "\n... (truncated)"
                            )
                            truncated_section = self._format_file_section(
                                analysis, truncated_content
                            )
                            context_parts.append(truncated_section)
                        break

                except Exception as e:
                    logger.warning(f"Failed to include file {analysis.path}: {e}")

            # Add dependency information
            if current_size < max_size * 0.9:  # Only if we have space
                dep_info = self._format_dependency_info(
                    project_context.dependency_graph
                )
                if current_size + len(dep_info) <= max_size:
                    context_parts.append(dep_info)

            result = "\n\n".join(context_parts)
            logger.info(f"Generated optimized context: {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Error generating optimized context: {e}")
            raise

    async def _discover_files(
        self,
        root_path: Path,
        max_files: int,
        include_patterns: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[Path]:
        """Discover files for analysis."""
        try:
            files = []

            # Default exclude patterns
            default_excludes = [
                "*.pyc",
                "*.pyo",
                "*.pyd",
                "__pycache__",
                ".git",
                ".svn",
                ".hg",
                ".bzr",
                "node_modules",
                ".npm",
                ".yarn",
                ".venv",
                "venv",
                ".env",
                "build",
                "dist",
                "target",
                "out",
                ".idea",
                ".vscode",
                ".vs",
                "*.log",
                "*.tmp",
                "*.temp",
                ".DS_Store",
                "Thumbs.db",
            ]

            exclude_set = set(default_excludes)
            if exclude_patterns:
                exclude_set.update(exclude_patterns)

            # Use git files if available
            try:
                git_files = get_git_files(str(root_path))
                if git_files:
                    for file_path in git_files:
                        full_path = root_path / file_path
                        if (
                            full_path.exists()
                            and full_path.is_file()
                            and self._should_include_file(full_path, exclude_set)
                        ):
                            files.append(full_path)
                            if len(files) >= max_files:
                                break

                    if files:
                        logger.info(f"Using git files: {len(files)} files discovered")
                        return files
            except Exception:
                pass

            # Fallback to directory traversal
            for file_path in root_path.rglob("*"):
                if len(files) >= max_files:
                    break

                if file_path.is_file() and self._should_include_file(
                    file_path, exclude_set
                ):
                    files.append(file_path)

            # Sort by importance
            files.sort(key=lambda f: self._calculate_file_priority(f), reverse=True)

            logger.info(f"Discovered {len(files)} files for analysis")
            return files[:max_files]

        except Exception as e:
            logger.error(f"Error discovering files: {e}")
            return []

    async def _analyze_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analyze a single file."""
        try:
            if not is_text_file(file_path):
                return None

            stat = file_path.stat()
            content = read_file_safe(file_path)

            # Basic metrics
            size = stat.st_size
            lines = content.count("\n") + 1
            language = self._detect_language(file_path, content)

            # Analyze dependencies and exports
            dependencies = self._extract_dependencies(content, language)
            exports = self._extract_exports(content, language)

            # Calculate importance score
            importance_score = self._calculate_importance_score(
                file_path, size, lines, language, dependencies, exports
            )

            # Generate summary
            summary = self._generate_file_summary(content, language)

            return FileAnalysis(
                path=file_path,
                size=size,
                lines=lines,
                language=language,
                importance_score=importance_score,
                dependencies=tuple(dependencies),
                exports=tuple(exports),
                summary=summary,
            )

        except Exception as e:
            logger.warning(f"Error analyzing file {file_path}: {e}")
            return None

    def _should_include_file(self, file_path: Path, exclude_patterns: Set[str]) -> bool:
        """Check if file should be included in analysis."""
        # Check exclude patterns
        for pattern in exclude_patterns:
            if file_path.match(pattern) or any(
                part.startswith(".") for part in file_path.parts[1:]
            ):
                return False

        # Check file extension
        if file_path.suffix.lower() in self.important_extensions:
            return True

        # Check special files
        special_files = {
            "readme",
            "license",
            "changelog",
            "contributing",
            "makefile",
            "dockerfile",
            "requirements.txt",
            "package.json",
            "composer.json",
            "cargo.toml",
        }

        if file_path.name.lower() in special_files:
            return True

        return False

    def _calculate_file_priority(self, file_path: Path) -> float:
        """Calculate file priority for discovery ordering."""
        priority = 0.0

        # Extension priority
        ext_priorities = {
            ".py": 10,
            ".js": 9,
            ".ts": 9,
            ".jsx": 8,
            ".tsx": 8,
            ".java": 8,
            ".cpp": 7,
            ".c": 7,
            ".h": 7,
            ".md": 6,
            ".json": 5,
            ".yaml": 5,
            ".yml": 5,
        }
        priority += ext_priorities.get(file_path.suffix.lower(), 1)

        # Name priority
        name_priorities = {
            "main": 10,
            "index": 9,
            "app": 8,
            "server": 7,
            "readme": 6,
            "package.json": 5,
            "requirements.txt": 5,
        }
        name_lower = file_path.stem.lower()
        priority += name_priorities.get(name_lower, 0)

        # Depth penalty (prefer files closer to root)
        depth = len(file_path.parts) - 1
        priority -= depth * 0.5

        return priority

    def _detect_language(self, file_path: Path, content: str) -> str:
        """Detect programming language of file."""
        # Check by extension first
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".rst": "rst",
            ".txt": "text",
        }

        ext_lang = ext_map.get(file_path.suffix.lower())
        if ext_lang:
            return ext_lang

        # Check shebang
        if content.startswith("#!"):
            first_line = content.split("\n")[0]
            if "python" in first_line:
                return "python"
            elif "node" in first_line or "javascript" in first_line:
                return "javascript"
            elif "bash" in first_line or "sh" in first_line:
                return "shell"

        return "text"

    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract dependencies from file content."""
        dependencies = []

        try:
            if language == "python":
                # Python imports
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("import ") or line.startswith("from "):
                        # Extract module name
                        if line.startswith("import "):
                            module = line[7:].split()[0].split(".")[0]
                        else:  # from ... import
                            module = line.split()[1].split(".")[0]
                        dependencies.append(module)

            elif language in ["javascript", "typescript"]:
                # JavaScript/TypeScript imports
                import_patterns = [
                    r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                    r'require\([\'"]([^\'"]+)[\'"]\)',
                    r'import\([\'"]([^\'"]+)[\'"]\)',
                ]

                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    dependencies.extend(matches)

            elif language == "java":
                # Java imports
                import_pattern = r"import\s+([^;]+);"
                matches = re.findall(import_pattern, content)
                dependencies.extend([m.split(".")[-1] for m in matches])

        except Exception:
            pass

        return list(set(dependencies))  # Remove duplicates

    def _extract_exports(self, content: str, language: str) -> List[str]:
        """Extract exports/public interfaces from file content."""
        exports = []

        try:
            if language == "python":
                # Python classes and functions
                class_pattern = r"class\s+(\w+)"
                func_pattern = r"def\s+(\w+)"

                exports.extend(re.findall(class_pattern, content))
                exports.extend(re.findall(func_pattern, content))

            elif language in ["javascript", "typescript"]:
                # JavaScript/TypeScript exports
                export_patterns = [
                    r"export\s+(?:default\s+)?(?:class|function)\s+(\w+)",
                    r"export\s+(?:const|let|var)\s+(\w+)",
                    r"exports\.(\w+)",
                    r"module\.exports\s*=\s*(\w+)",
                ]

                for pattern in export_patterns:
                    matches = re.findall(pattern, content)
                    exports.extend(matches)

            elif language == "java":
                # Java public classes and methods
                class_pattern = r"public\s+class\s+(\w+)"
                method_pattern = r"public\s+(?:static\s+)?\w+\s+(\w+)\s*\("

                exports.extend(re.findall(class_pattern, content))
                exports.extend(re.findall(method_pattern, content))

        except Exception:
            pass

        return list(set(exports))  # Remove duplicates

    def _calculate_importance_score(
        self,
        file_path: Path,
        size: int,
        lines: int,
        language: str,
        dependencies: List[str],
        exports: List[str],
    ) -> float:
        """Calculate importance score for file prioritization."""
        score = 0.0

        # Base score by language
        lang_scores = {
            "python": 10,
            "javascript": 9,
            "typescript": 9,
            "java": 8,
            "cpp": 7,
            "c": 7,
            "markdown": 5,
            "json": 4,
            "yaml": 4,
        }
        score += lang_scores.get(language, 1)

        # File name importance
        name_lower = file_path.stem.lower()
        if name_lower in ["main", "index", "app", "server"]:
            score += 10
        elif name_lower in ["config", "settings", "constants"]:
            score += 5
        elif name_lower.startswith("test"):
            score += 2

        # Size factor (moderate size preferred)
        if 100 <= lines <= 1000:
            score += 5
        elif lines > 1000:
            score += 2

        # Connectivity (files with many dependencies/exports)
        score += min(len(dependencies) * 0.5, 5)
        score += min(len(exports) * 0.5, 5)

        # Path depth penalty
        depth = len(file_path.parts) - 1
        score -= depth * 0.5

        return max(score, 0.1)  # Minimum score

    def _generate_file_summary(self, content: str, language: str) -> str:
        """Generate a brief summary of file content."""
        lines = content.split("\n")

        # Look for docstrings, comments, or README content
        summary_lines = []

        if language == "python":
            # Look for module docstring
            in_docstring = False
            for line in lines[:20]:  # Check first 20 lines
                line = line.strip()
                if line.startswith('"""') or line.startswith("'''"):
                    if in_docstring:
                        break
                    in_docstring = True
                    if len(line) > 3:
                        summary_lines.append(line[3:])
                elif in_docstring:
                    if line.endswith('"""') or line.endswith("'''"):
                        summary_lines.append(line[:-3])
                        break
                    summary_lines.append(line)

        elif language in ["javascript", "typescript"]:
            # Look for JSDoc or comments
            for line in lines[:20]:
                line = line.strip()
                if line.startswith("/**") or line.startswith("*"):
                    clean_line = line.lstrip("/*").strip()
                    if clean_line:
                        summary_lines.append(clean_line)

        elif language == "markdown":
            # Use first paragraph
            for line in lines[:10]:
                line = line.strip()
                if line and not line.startswith("#"):
                    summary_lines.append(line)
                    if len(" ".join(summary_lines)) > 200:
                        break

        # Fallback: use first few non-empty lines
        if not summary_lines:
            for line in lines[:5]:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("//"):
                    summary_lines.append(line)

        summary = " ".join(summary_lines)
        return summary[:200] + "..." if len(summary) > 200 else summary

    def _build_dependency_graph(
        self, file_analyses: List[FileAnalysis]
    ) -> Dict[str, List[str]]:
        """Build dependency graph from file analyses."""
        graph = defaultdict(list)

        # Create mapping of exports to files
        exports_map = defaultdict(list)
        for analysis in file_analyses:
            for export in analysis.exports:
                exports_map[export].append(str(analysis.path))

        # Build dependencies
        for analysis in file_analyses:
            file_key = str(analysis.path)
            for dep in analysis.dependencies:
                if dep in exports_map:
                    graph[file_key].extend(exports_map[dep])

        return dict(graph)

    def _find_documentation_files(
        self, file_analyses: List[FileAnalysis]
    ) -> List[Path]:
        """Find documentation files."""
        doc_files = []

        for analysis in file_analyses:
            name_lower = analysis.path.name.lower()
            if (
                analysis.language == "markdown"
                or name_lower.startswith("readme")
                or name_lower.startswith("doc")
                or "doc" in str(analysis.path).lower()
            ):
                doc_files.append(analysis.path)

        return doc_files

    def _find_config_files(self, file_analyses: List[FileAnalysis]) -> List[Path]:
        """Find configuration files."""
        config_files = []

        config_patterns = [
            "config",
            "settings",
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "cargo.toml",
            "composer.json",
        ]

        for analysis in file_analyses:
            name_lower = analysis.path.name.lower()
            if any(
                pattern in name_lower for pattern in config_patterns
            ) or analysis.language in ["json", "yaml", "toml"]:
                config_files.append(analysis.path)

        return config_files

    def _find_entry_points(self, file_analyses: List[FileAnalysis]) -> List[Path]:
        """Find likely entry point files."""
        entry_points = []

        entry_patterns = ["main", "index", "app", "server", "__main__"]

        for analysis in file_analyses:
            name_lower = analysis.path.stem.lower()
            if name_lower in entry_patterns:
                entry_points.append(analysis.path)

        return entry_points

    def _generate_context_summary(
        self,
        root_path: Path,
        file_analyses: List[FileAnalysis],
        languages: Dict[str, int],
        dependency_graph: Dict[str, List[str]],
    ) -> str:
        """Generate overall project context summary."""
        total_files = len(file_analyses)
        total_lines = sum(f.lines for f in file_analyses)

        # Top languages
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]

        # Most connected files
        connectivity = {
            str(f.path): len(dependency_graph.get(str(f.path), []))
            for f in file_analyses
        }
        most_connected = sorted(
            file_analyses, key=lambda f: connectivity[str(f.path)], reverse=True
        )[:5]

        summary_parts = [
            f"Project: {root_path.name}",
            f"Total files: {total_files}",
            f"Total lines: {total_lines:,}",
            "",
            "Languages:",
        ]

        for lang, count in top_languages:
            summary_parts.append(f"  {lang}: {count} files")

        summary_parts.extend(
            [
                "",
                "Key files:",
            ]
        )

        for analysis in most_connected:
            rel_path = analysis.path.relative_to(root_path)
            summary_parts.append(
                f"  {rel_path} ({analysis.language}, {analysis.lines} lines)"
            )

        return "\n".join(summary_parts)

    def _prioritize_files(
        self, file_analyses: List[FileAnalysis], focus_areas: Optional[List[str]] = None
    ) -> List[FileAnalysis]:
        """Prioritize files for context inclusion."""
        # Apply focus area boost
        if focus_areas:
            modified_analyses = []
            for analysis in file_analyses:
                importance_score = analysis.importance_score
                for area in focus_areas:
                    if area.lower() in str(analysis.path).lower():
                        importance_score *= 1.5
                        break

                # Create new FileAnalysis with updated importance score if changed
                if importance_score != analysis.importance_score:
                    modified_analysis = FileAnalysis(
                        path=analysis.path,
                        size=analysis.size,
                        lines=analysis.lines,
                        language=analysis.language,
                        importance_score=importance_score,
                        dependencies=analysis.dependencies,
                        exports=analysis.exports,
                        summary=analysis.summary,
                    )
                    modified_analyses.append(modified_analysis)
                else:
                    modified_analyses.append(analysis)
            file_analyses = modified_analyses

        # Sort by importance score
        return sorted(file_analyses, key=lambda f: f.importance_score, reverse=True)

    def _create_project_summary(self, project_context: ProjectContext) -> str:
        """Create project summary section."""
        return f"""# Project Analysis Summary

{project_context.context_summary}

## File Structure Overview
- Total files analyzed: {project_context.total_files}
- Total size: {project_context.total_size:,} bytes
- Languages: {', '.join(f'{lang} ({count})' for lang, count in project_context.languages.items())}

## Key Components
- Entry points: {len(project_context.entry_points)} files
- Configuration files: {len(project_context.config_files)} files  
- Documentation files: {len(project_context.documentation_files)} files

"""

    def _format_file_section(self, analysis: FileAnalysis, content: str) -> str:
        """Format file content for context inclusion."""
        rel_path = analysis.path.name  # Use just filename for brevity

        return f"""## File: {rel_path}
Language: {analysis.language} | Lines: {analysis.lines} | Importance: {analysis.importance_score:.1f}

{analysis.summary}

```{analysis.language}
{content}
```
"""

    def _format_dependency_info(self, dependency_graph: Dict[str, List[str]]) -> str:
        """Format dependency information."""
        if not dependency_graph:
            return ""

        lines = ["## Dependency Relationships"]

        for file_path, deps in list(dependency_graph.items())[:10]:  # Limit output
            file_name = Path(file_path).name
            dep_names = [Path(dep).name for dep in deps[:5]]  # Limit deps per file
            if dep_names:
                lines.append(f"- {file_name} depends on: {', '.join(dep_names)}")

        return "\n".join(lines)
