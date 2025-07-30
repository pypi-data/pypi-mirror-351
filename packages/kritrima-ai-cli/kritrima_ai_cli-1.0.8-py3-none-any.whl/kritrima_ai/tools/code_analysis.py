"""
Code analysis tool for Kritrima AI CLI.

This module provides comprehensive code analysis capabilities including:
- Syntax analysis and AST parsing
- Dependency detection and mapping
- Code quality assessment
- Function and class extraction
- Documentation analysis
- Security vulnerability detection
"""

import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Set, Union

from kritrima_ai.agent.base_tool import (
    BaseTool,
    ToolExecutionResult,
    ToolMetadata,
    create_parameter_schema,
    create_tool_metadata,
)
from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.security.sandbox import SandboxManager
from kritrima_ai.utils.file_utils import is_text_file, read_file_safe
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CodeFunction:
    """Represents a function or method in code."""

    name: str
    line_start: int
    line_end: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class CodeClass:
    """Represents a class in code."""

    name: str
    line_start: int
    line_end: int
    base_classes: List[str]
    methods: List[CodeFunction]
    attributes: List[str]
    docstring: Optional[str]


@dataclass
class CodeImport:
    """Represents an import statement."""

    module: str
    alias: Optional[str]
    from_module: Optional[str]
    line_number: int
    is_standard_library: bool = False
    is_third_party: bool = False


@dataclass
class CodeAnalysisResult:
    """Complete code analysis result."""

    file_path: Path
    language: str
    lines_of_code: int
    lines_of_comments: int
    complexity_score: int
    functions: List[CodeFunction]
    classes: List[CodeClass]
    imports: List[CodeImport]
    dependencies: Set[str]
    security_issues: List[Dict[str, Any]]
    quality_metrics: Dict[str, Any]
    summary: str


class CodeAnalysisTool(BaseTool):
    """
    Comprehensive code analysis tool for various programming languages.

    Provides detailed analysis of code structure, dependencies, quality,
    and potential security issues.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize code analysis tool.

        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.sandbox = SandboxManager(config)

        # Language-specific analyzers
        self.analyzers = {
            "python": self._analyze_python,
            "javascript": self._analyze_javascript,
            "typescript": self._analyze_typescript,
            "java": self._analyze_java,
            "cpp": self._analyze_cpp,
            "c": self._analyze_c,
            "go": self._analyze_go,
            "rust": self._analyze_rust,
        }

        # Security patterns to detect
        self.security_patterns = {
            "python": [
                (r"eval\s*\(", "Use of eval() function", "high"),
                (r"exec\s*\(", "Use of exec() function", "high"),
                (
                    r"subprocess\.call\s*\(.*shell\s*=\s*True",
                    "Shell injection risk",
                    "high",
                ),
                (r"pickle\.loads?\s*\(", "Unsafe pickle usage", "medium"),
                (r"yaml\.load\s*\(", "Unsafe YAML loading", "medium"),
                (r"input\s*\(.*\)", "Use of input() function", "low"),
            ],
            "javascript": [
                (r"eval\s*\(", "Use of eval() function", "high"),
                (r"innerHTML\s*=", "Potential XSS vulnerability", "medium"),
                (r"document\.write\s*\(", "Use of document.write", "medium"),
                (r'setTimeout\s*\(\s*["\']', "String in setTimeout", "medium"),
            ],
            "java": [
                (r"Runtime\.getRuntime\(\)\.exec", "Command execution", "high"),
                (r"Class\.forName\s*\(", "Dynamic class loading", "medium"),
                (r"System\.exit\s*\(", "System exit call", "low"),
            ],
        }

        logger.info("Code analysis tool initialized")

    def get_metadata(self) -> ToolMetadata:
        """Get metadata for the code analysis tool."""
        return create_tool_metadata(
            name="code_analysis",
            description="Analyze code files for structure, dependencies, quality metrics, and security issues",
            parameters=create_parameter_schema(
                properties={
                    "operation": {
                        "type": "string",
                        "enum": [
                            "analyze_file",
                            "analyze_directory",
                            "security_scan",
                            "dependency_analysis",
                            "quality_metrics",
                        ],
                        "description": "The type of code analysis to perform",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file or directory to analyze",
                    },
                    "recursive": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to analyze subdirectories recursively",
                    },
                    "file_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File patterns to include (e.g., ['*.py', '*.js'])",
                    },
                    "include_security": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include security analysis",
                    },
                    "include_quality": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to include quality metrics",
                    },
                    "max_files": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of files to analyze",
                    },
                },
                required=["operation", "file_path"],
            ),
            category="development",
            risk_level="low",
            requires_approval=False,
            supports_streaming=True,
            examples=[
                {
                    "description": "Analyze a single Python file",
                    "parameters": {"operation": "analyze_file", "file_path": "main.py"},
                },
                {
                    "description": "Analyze all Python files in a directory",
                    "parameters": {
                        "operation": "analyze_directory",
                        "file_path": "src/",
                        "file_patterns": ["*.py"],
                    },
                },
                {
                    "description": "Security scan of project",
                    "parameters": {"operation": "security_scan", "file_path": "."},
                },
            ],
        )

    async def execute(self, **kwargs) -> ToolExecutionResult:
        """
        Execute code analysis based on the specified operation.

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

            file_path = kwargs.get("file_path")
            if not file_path:
                return ToolExecutionResult(
                    success=False, result=None, error="file_path parameter is required"
                )

            # Route to appropriate method based on operation
            if operation == "analyze_file":
                result = await self.analyze_file(file_path)
                return ToolExecutionResult(
                    success=True, result=self._format_analysis_result(result)
                )
            elif operation == "analyze_directory":
                recursive = kwargs.get("recursive", True)
                file_patterns = kwargs.get("file_patterns")
                max_files = kwargs.get("max_files", 100)
                results = await self.analyze_directory(
                    file_path, recursive, file_patterns, max_files
                )
                return ToolExecutionResult(
                    success=True, result=self._format_directory_results(results)
                )
            elif operation == "security_scan":
                results = await self.analyze_directory(
                    file_path, True, None, kwargs.get("max_files", 100)
                )
                security_summary = self._extract_security_summary(results)
                return ToolExecutionResult(success=True, result=security_summary)
            elif operation == "dependency_analysis":
                results = await self.analyze_directory(
                    file_path, True, None, kwargs.get("max_files", 100)
                )
                dependency_summary = self._extract_dependency_summary(results)
                return ToolExecutionResult(success=True, result=dependency_summary)
            elif operation == "quality_metrics":
                results = await self.analyze_directory(
                    file_path, True, None, kwargs.get("max_files", 100)
                )
                quality_summary = self._extract_quality_summary(results)
                return ToolExecutionResult(success=True, result=quality_summary)
            else:
                return ToolExecutionResult(
                    success=False, result=None, error=f"Unknown operation: {operation}"
                )

        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            return ToolExecutionResult(success=False, result=None, error=str(e))

    async def execute_stream(self, **kwargs) -> AsyncIterator[str]:
        """
        Execute code analysis with streaming output.

        Args:
            **kwargs: Operation parameters

        Yields:
            Streaming analysis results
        """
        try:
            operation = kwargs.get("operation")
            file_path = kwargs.get("file_path")

            yield f"Starting {operation} for {file_path}...\n"

            if operation == "analyze_file":
                result = await self.analyze_file(file_path)
                yield self._format_analysis_result(result)
            elif operation == "analyze_directory":
                recursive = kwargs.get("recursive", True)
                file_patterns = kwargs.get("file_patterns")
                max_files = kwargs.get("max_files", 100)

                async for file_result in self._stream_directory_analysis(
                    file_path, recursive, file_patterns, max_files
                ):
                    yield file_result
            else:
                # Fall back to regular execution
                result = await self.execute(**kwargs)
                if result.success:
                    yield str(result.result)
                else:
                    yield f"Error: {result.error}"

        except Exception as e:
            yield f"Error in streaming analysis: {str(e)}"

    async def _stream_directory_analysis(
        self,
        directory_path: str,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None,
        max_files: int = 100,
    ) -> AsyncIterator[str]:
        """Stream directory analysis results."""
        try:
            path = Path(directory_path).resolve()

            # Find code files
            files = self._find_code_files(path, recursive, file_patterns)
            files = files[:max_files]  # Limit number of files

            yield f"Found {len(files)} files to analyze\n"

            for i, file_path in enumerate(files, 1):
                try:
                    yield f"[{i}/{len(files)}] Analyzing {file_path.name}...\n"
                    result = await self.analyze_file(str(file_path))
                    yield f"✓ {file_path.name}: {result.language}, {result.lines_of_code} LOC, complexity: {result.complexity_score}\n"

                    if result.security_issues:
                        yield f"  ⚠ {len(result.security_issues)} security issues found\n"

                except Exception as e:
                    yield f"✗ {file_path.name}: Error - {str(e)}\n"

        except Exception as e:
            yield f"Error in directory analysis: {str(e)}\n"

    def _format_analysis_result(self, result: CodeAnalysisResult) -> str:
        """Format a single analysis result."""
        lines = [
            f"Code Analysis: {result.file_path.name}",
            f"Language: {result.language}",
            f"Lines of Code: {result.lines_of_code}",
            f"Lines of Comments: {result.lines_of_comments}",
            f"Complexity Score: {result.complexity_score}",
            f"Functions: {len(result.functions)}",
            f"Classes: {len(result.classes)}",
            f"Imports: {len(result.imports)}",
            f"Dependencies: {len(result.dependencies)}",
        ]

        if result.security_issues:
            lines.append(f"Security Issues: {len(result.security_issues)}")
            for issue in result.security_issues[:5]:  # Show first 5 issues
                lines.append(
                    f"  - {issue['severity']}: {issue['description']} (line {issue['line']})"
                )

        lines.append(f"Summary: {result.summary}")

        return "\n".join(lines)

    def _format_directory_results(self, results: Dict[str, CodeAnalysisResult]) -> str:
        """Format directory analysis results."""
        if not results:
            return "No code files found to analyze."

        lines = [f"Code Analysis Results ({len(results)} files)"]

        total_loc = sum(r.lines_of_code for r in results.values())
        total_complexity = sum(r.complexity_score for r in results.values())
        total_security_issues = sum(len(r.security_issues) for r in results.values())

        lines.extend(
            [
                f"Total Lines of Code: {total_loc}",
                f"Average Complexity: {total_complexity / len(results):.1f}",
                f"Total Security Issues: {total_security_issues}",
                "",
            ]
        )

        # Show top files by complexity
        sorted_files = sorted(
            results.items(), key=lambda x: x[1].complexity_score, reverse=True
        )
        lines.append("Most Complex Files:")
        for file_path, result in sorted_files[:5]:
            lines.append(f"  {result.file_path.name}: {result.complexity_score}")

        return "\n".join(lines)

    def _extract_security_summary(self, results: Dict[str, CodeAnalysisResult]) -> str:
        """Extract security analysis summary."""
        all_issues = []
        for result in results.values():
            for issue in result.security_issues:
                issue["file"] = result.file_path.name
                all_issues.append(issue)

        if not all_issues:
            return "No security issues found."

        # Group by severity
        by_severity = defaultdict(list)
        for issue in all_issues:
            by_severity[issue["severity"]].append(issue)

        lines = [f"Security Analysis: {len(all_issues)} issues found"]
        for severity in ["high", "medium", "low"]:
            if severity in by_severity:
                lines.append(f"{severity.title()}: {len(by_severity[severity])}")
                for issue in by_severity[severity][:3]:  # Show first 3 of each severity
                    lines.append(
                        f"  - {issue['file']}:{issue['line']}: {issue['description']}"
                    )

        return "\n".join(lines)

    def _extract_dependency_summary(
        self, results: Dict[str, CodeAnalysisResult]
    ) -> str:
        """Extract dependency analysis summary."""
        all_deps = set()
        for result in results.values():
            all_deps.update(result.dependencies)

        lines = [f"Dependency Analysis: {len(all_deps)} unique dependencies"]
        for dep in sorted(all_deps)[:20]:  # Show first 20
            lines.append(f"  - {dep}")

        return "\n".join(lines)

    def _extract_quality_summary(self, results: Dict[str, CodeAnalysisResult]) -> str:
        """Extract quality metrics summary."""
        if not results:
            return "No files analyzed for quality metrics."

        total_loc = sum(r.lines_of_code for r in results.values())
        total_comments = sum(r.lines_of_comments for r in results.values())
        avg_complexity = sum(r.complexity_score for r in results.values()) / len(
            results
        )

        comment_ratio = (total_comments / total_loc * 100) if total_loc > 0 else 0

        lines = [
            f"Quality Metrics Summary:",
            f"Total Lines of Code: {total_loc}",
            f"Comment Ratio: {comment_ratio:.1f}%",
            f"Average Complexity: {avg_complexity:.1f}",
            f"Files Analyzed: {len(results)}",
        ]

        return "\n".join(lines)

    async def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """
        Analyze a single code file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Code analysis result
        """
        try:
            path = Path(file_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "read"):
                raise PermissionError(f"Access denied to file: {path}")

            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            if not is_text_file(path):
                raise ValueError(f"File is not a text file: {path}")

            # Detect language
            language = self._detect_language(path)

            # Read file content
            content = read_file_safe(path)
            if not content:
                raise ValueError(f"Could not read file content: {path}")

            # Perform analysis
            if language in self.analyzers:
                result = await self.analyzers[language](path, content)
            else:
                result = await self._analyze_generic(path, content, language)

            logger.info(f"Code analysis completed for {path}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            raise

    async def analyze_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None,
    ) -> Dict[str, CodeAnalysisResult]:
        """
        Analyze all code files in a directory.

        Args:
            directory_path: Directory to analyze
            recursive: Whether to analyze subdirectories
            file_patterns: File patterns to include

        Returns:
            Dictionary mapping file paths to analysis results
        """
        try:
            path = Path(directory_path).resolve()

            # Security check
            if not self.sandbox.is_path_allowed(path, "read"):
                raise PermissionError(f"Access denied to directory: {path}")

            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")

            results = {}

            # Find code files
            code_files = self._find_code_files(path, recursive, file_patterns)

            for file_path in code_files:
                try:
                    result = await self.analyze_file(str(file_path))
                    results[str(file_path)] = result
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")

            logger.info(f"Directory analysis completed: {len(results)} files analyzed")
            return results

        except Exception as e:
            logger.error(f"Error analyzing directory {directory_path}: {e}")
            raise

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        extension = file_path.suffix.lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".fish": "shell",
        }

        return language_map.get(extension, "unknown")

    def _find_code_files(
        self, directory: Path, recursive: bool, file_patterns: Optional[List[str]]
    ) -> List[Path]:
        """Find code files in directory."""
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".cpp",
            ".cc",
            ".cxx",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".cs",
            ".swift",
            ".kt",
            ".scala",
            ".sh",
            ".bash",
        }

        files = []

        if recursive:
            for file_path in directory.rglob("*"):
                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in code_extensions
                    and self._should_include_file(file_path, file_patterns)
                ):
                    files.append(file_path)
        else:
            for file_path in directory.iterdir():
                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in code_extensions
                    and self._should_include_file(file_path, file_patterns)
                ):
                    files.append(file_path)

        return files

    def _should_include_file(
        self, file_path: Path, patterns: Optional[List[str]]
    ) -> bool:
        """Check if file should be included based on patterns."""
        if not patterns:
            return True

        for pattern in patterns:
            if file_path.match(pattern):
                return True

        return False

    async def _analyze_python(
        self, file_path: Path, content: str
    ) -> CodeAnalysisResult:
        """Analyze Python code."""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return self._create_error_result(file_path, "python", str(e))

        # Extract functions and classes
        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func = self._extract_python_function(node, content)
                functions.append(func)
            elif isinstance(node, ast.AsyncFunctionDef):
                func = self._extract_python_function(node, content, is_async=True)
                functions.append(func)
            elif isinstance(node, ast.ClassDef):
                cls = self._extract_python_class(node, content)
                classes.append(cls)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imp = self._extract_python_import(node)
                imports.append(imp)

        # Calculate metrics
        lines = content.split("\n")
        lines_of_code = len(
            [
                line
                for line in lines
                if line.strip() and not line.strip().startswith("#")
            ]
        )
        lines_of_comments = len(
            [line for line in lines if line.strip().startswith("#")]
        )

        # Calculate complexity
        complexity_score = self._calculate_complexity(tree)

        # Extract dependencies
        dependencies = set()
        for imp in imports:
            if imp.from_module:
                dependencies.add(imp.from_module)
            else:
                dependencies.add(imp.module)

        # Security analysis
        security_issues = self._analyze_security(content, "python")

        # Quality metrics
        quality_metrics = {
            "functions_count": len(functions),
            "classes_count": len(classes),
            "imports_count": len(imports),
            "avg_function_complexity": (
                sum(f.complexity for f in functions) / len(functions)
                if functions
                else 0
            ),
            "documentation_ratio": (
                len([f for f in functions if f.docstring]) / len(functions)
                if functions
                else 0
            ),
        }

        # Generate summary
        summary = self._generate_summary(
            file_path, "python", functions, classes, quality_metrics
        )

        return CodeAnalysisResult(
            file_path=file_path,
            language="python",
            lines_of_code=lines_of_code,
            lines_of_comments=lines_of_comments,
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=imports,
            dependencies=dependencies,
            security_issues=security_issues,
            quality_metrics=quality_metrics,
            summary=summary,
        )

    def _extract_python_function(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        content: str,
        is_async: bool = False,
    ) -> CodeFunction:
        """Extract function information from AST node."""
        # Get parameters
        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)

        # Get docstring
        docstring = None
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value

        # Calculate complexity
        complexity = self._calculate_function_complexity(node)

        return CodeFunction(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=parameters,
            return_type=None,  # Would need type annotations analysis
            docstring=docstring,
            complexity=complexity,
            is_async=is_async,
        )

    def _extract_python_class(self, node: ast.ClassDef, content: str) -> CodeClass:
        """Extract class information from AST node."""
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)

        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._extract_python_function(item, content)
                method.is_method = True
                method.class_name = node.name
                methods.append(method)
            elif isinstance(item, ast.AsyncFunctionDef):
                method = self._extract_python_function(item, content, is_async=True)
                method.is_method = True
                method.class_name = node.name
                methods.append(method)

        # Get docstring
        docstring = None
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value

        return CodeClass(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            base_classes=base_classes,
            methods=methods,
            attributes=[],  # Would need more complex analysis
            docstring=docstring,
        )

    def _extract_python_import(
        self, node: Union[ast.Import, ast.ImportFrom]
    ) -> CodeImport:
        """Extract import information from AST node."""
        if isinstance(node, ast.Import):
            # import module [as alias]
            alias_name = node.names[0]
            return CodeImport(
                module=alias_name.name,
                alias=alias_name.asname,
                from_module=None,
                line_number=node.lineno,
            )
        else:
            # from module import name [as alias]
            alias_name = node.names[0] if node.names else None
            return CodeImport(
                module=alias_name.name if alias_name else "*",
                alias=alias_name.asname if alias_name else None,
                from_module=node.module,
                line_number=node.lineno,
            )

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of code."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _calculate_function_complexity(self, node: ast.AST) -> int:
        """Calculate complexity of a single function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _analyze_security(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code for security issues."""
        issues = []

        if language not in self.security_patterns:
            return issues

        lines = content.split("\n")

        for pattern, description, severity in self.security_patterns[language]:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(
                        {
                            "type": "security",
                            "description": description,
                            "severity": severity,
                            "line": line_num,
                            "code": line.strip(),
                        }
                    )

        return issues

    async def _analyze_javascript(
        self, file_path: Path, content: str
    ) -> CodeAnalysisResult:
        """Analyze JavaScript code (simplified)."""
        return await self._analyze_generic(file_path, content, "javascript")

    async def _analyze_typescript(
        self, file_path: Path, content: str
    ) -> CodeAnalysisResult:
        """Analyze TypeScript code (simplified)."""
        return await self._analyze_generic(file_path, content, "typescript")

    async def _analyze_java(self, file_path: Path, content: str) -> CodeAnalysisResult:
        """Analyze Java code (simplified)."""
        return await self._analyze_generic(file_path, content, "java")

    async def _analyze_cpp(self, file_path: Path, content: str) -> CodeAnalysisResult:
        """Analyze C++ code (simplified)."""
        return await self._analyze_generic(file_path, content, "cpp")

    async def _analyze_c(self, file_path: Path, content: str) -> CodeAnalysisResult:
        """Analyze C code (simplified)."""
        return await self._analyze_generic(file_path, content, "c")

    async def _analyze_go(self, file_path: Path, content: str) -> CodeAnalysisResult:
        """Analyze Go code (simplified)."""
        return await self._analyze_generic(file_path, content, "go")

    async def _analyze_rust(self, file_path: Path, content: str) -> CodeAnalysisResult:
        """Analyze Rust code (simplified)."""
        return await self._analyze_generic(file_path, content, "rust")

    async def _analyze_generic(
        self, file_path: Path, content: str, language: str
    ) -> CodeAnalysisResult:
        """Generic analysis for unsupported languages."""
        lines = content.split("\n")
        lines_of_code = len([line for line in lines if line.strip()])
        lines_of_comments = 0

        # Simple comment detection
        comment_patterns = {
            "javascript": [r"//.*", r"/\*.*?\*/"],
            "typescript": [r"//.*", r"/\*.*?\*/"],
            "java": [r"//.*", r"/\*.*?\*/"],
            "cpp": [r"//.*", r"/\*.*?\*/"],
            "c": [r"//.*", r"/\*.*?\*/"],
            "go": [r"//.*", r"/\*.*?\*/"],
            "rust": [r"//.*", r"/\*.*?\*/"],
            "python": [r"#.*"],
        }

        if language in comment_patterns:
            for pattern in comment_patterns[language]:
                for line in lines:
                    if re.search(pattern, line):
                        lines_of_comments += 1

        # Security analysis
        security_issues = self._analyze_security(content, language)

        # Basic quality metrics
        quality_metrics = {
            "lines_of_code": lines_of_code,
            "lines_of_comments": lines_of_comments,
            "comment_ratio": (
                lines_of_comments / lines_of_code if lines_of_code > 0 else 0
            ),
        }

        summary = f"{language.title()} file with {lines_of_code} lines of code"

        return CodeAnalysisResult(
            file_path=file_path,
            language=language,
            lines_of_code=lines_of_code,
            lines_of_comments=lines_of_comments,
            complexity_score=1,
            functions=[],
            classes=[],
            imports=[],
            dependencies=set(),
            security_issues=security_issues,
            quality_metrics=quality_metrics,
            summary=summary,
        )

    def _create_error_result(
        self, file_path: Path, language: str, error: str
    ) -> CodeAnalysisResult:
        """Create analysis result for files with errors."""
        return CodeAnalysisResult(
            file_path=file_path,
            language=language,
            lines_of_code=0,
            lines_of_comments=0,
            complexity_score=0,
            functions=[],
            classes=[],
            imports=[],
            dependencies=set(),
            security_issues=[],
            quality_metrics={"error": error},
            summary=f"Analysis failed: {error}",
        )

    def _generate_summary(
        self,
        file_path: Path,
        language: str,
        functions: List[CodeFunction],
        classes: List[CodeClass],
        quality_metrics: Dict[str, Any],
    ) -> str:
        """Generate analysis summary."""
        parts = [
            f"{language.title()} file: {file_path.name}",
            f"Functions: {len(functions)}",
            f"Classes: {len(classes)}",
        ]

        if functions:
            avg_complexity = quality_metrics.get("avg_function_complexity", 0)
            parts.append(f"Average function complexity: {avg_complexity:.1f}")

        if quality_metrics.get("documentation_ratio"):
            doc_ratio = quality_metrics["documentation_ratio"] * 100
            parts.append(f"Documentation coverage: {doc_ratio:.1f}%")

        return " | ".join(parts)
