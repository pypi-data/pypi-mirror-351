"""
Template system for Kritrima AI CLI.

This module provides comprehensive template and scaffolding capabilities including:
- Project template generation and management
- Code snippet templates with variable substitution
- Multi-language and framework support
- Template inheritance and composition
- Dynamic template generation from existing projects
"""

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, Template

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.file_utils import FileUtils
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TemplateVariable:
    """Template variable definition."""

    name: str
    description: str
    type: str = "string"
    default: Optional[Any] = None
    required: bool = True
    choices: Optional[List[str]] = None
    validation_pattern: Optional[str] = None

    def validate(self, value: Any) -> bool:
        """Validate a value against this variable definition."""
        if self.required and value is None:
            return False

        if self.choices and value not in self.choices:
            return False

        if self.validation_pattern and isinstance(value, str):
            return bool(re.match(self.validation_pattern, value))

        return True


@dataclass
class TemplateFile:
    """Template file definition."""

    source_path: str
    target_path: str
    is_template: bool = True
    executable: bool = False
    condition: Optional[str] = None

    def should_include(self, variables: Dict[str, Any]) -> bool:
        """Check if this file should be included based on condition."""
        if not self.condition:
            return True

        try:
            # Simple condition evaluation
            return bool(eval(self.condition, {"__builtins__": {}}, variables))
        except Exception:
            return True


@dataclass
class ProjectTemplate:
    """Project template definition."""

    name: str
    description: str
    category: str
    language: str
    framework: Optional[str] = None
    variables: List[TemplateVariable] = field(default_factory=list)
    files: List[TemplateFile] = field(default_factory=list)
    post_generation_commands: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: Optional[str] = None
    license: Optional[str] = None

    def get_variable(self, name: str) -> Optional[TemplateVariable]:
        """Get a variable by name."""
        return next((var for var in self.variables if var.name == name), None)


class TemplateEngine:
    """
    Template engine for code generation and project scaffolding.

    Provides comprehensive template management with Jinja2 integration,
    variable substitution, and project generation capabilities.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize template engine.

        Args:
            config: Application configuration
        """
        self.config = config
        self.file_utils = FileUtils(config)

        # Template directories
        self.builtin_templates_dir = Path(__file__).parent.parent / "templates"
        self.user_templates_dir = Path.home() / ".kritrima-ai" / "templates"

        # Ensure directories exist
        self.user_templates_dir.mkdir(parents=True, exist_ok=True)

        # Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(
                [str(self.builtin_templates_dir), str(self.user_templates_dir)]
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Template registry
        self.templates: Dict[str, ProjectTemplate] = {}

        # Load templates
        self._load_builtin_templates()
        self._load_user_templates()

        logger.info(f"Template engine initialized with {len(self.templates)} templates")

    def _load_builtin_templates(self) -> None:
        """Load built-in project templates."""
        builtin_templates = {
            "python-cli": ProjectTemplate(
                name="Python CLI Application",
                description="A command-line application using Click and modern Python practices",
                category="application",
                language="python",
                framework="click",
                variables=[
                    TemplateVariable("project_name", "Project name", default="my-cli"),
                    TemplateVariable(
                        "package_name", "Python package name", default="my_cli"
                    ),
                    TemplateVariable("author_name", "Author name", default="Your Name"),
                    TemplateVariable(
                        "author_email", "Author email", default="you@example.com"
                    ),
                    TemplateVariable(
                        "description",
                        "Project description",
                        default="A Python CLI application",
                    ),
                    TemplateVariable(
                        "python_version",
                        "Minimum Python version",
                        default="3.8",
                        choices=["3.8", "3.9", "3.10", "3.11", "3.12"],
                    ),
                    TemplateVariable(
                        "use_poetry",
                        "Use Poetry for dependency management",
                        type="boolean",
                        default=True,
                    ),
                    TemplateVariable(
                        "include_tests",
                        "Include test structure",
                        type="boolean",
                        default=True,
                    ),
                    TemplateVariable(
                        "include_docs",
                        "Include documentation",
                        type="boolean",
                        default=True,
                    ),
                ],
                files=[
                    TemplateFile("python-cli/README.md.j2", "README.md"),
                    TemplateFile(
                        "python-cli/pyproject.toml.j2",
                        "pyproject.toml",
                        condition="use_poetry",
                    ),
                    TemplateFile(
                        "python-cli/setup.py.j2", "setup.py", condition="not use_poetry"
                    ),
                    TemplateFile(
                        "python-cli/requirements.txt.j2",
                        "requirements.txt",
                        condition="not use_poetry",
                    ),
                    TemplateFile(
                        "python-cli/src/__init__.py.j2",
                        "src/{{ package_name }}/__init__.py",
                    ),
                    TemplateFile(
                        "python-cli/src/main.py.j2", "src/{{ package_name }}/main.py"
                    ),
                    TemplateFile(
                        "python-cli/src/cli.py.j2", "src/{{ package_name }}/cli.py"
                    ),
                    TemplateFile(
                        "python-cli/tests/__init__.py.j2",
                        "tests/__init__.py",
                        condition="include_tests",
                    ),
                    TemplateFile(
                        "python-cli/tests/test_main.py.j2",
                        "tests/test_main.py",
                        condition="include_tests",
                    ),
                    TemplateFile(
                        "python-cli/.gitignore", ".gitignore", is_template=False
                    ),
                    TemplateFile("python-cli/LICENSE", "LICENSE", is_template=False),
                ],
                post_generation_commands=[
                    "git init",
                    "poetry install" if "use_poetry" else "pip install -e .",
                ],
                tags=["python", "cli", "click"],
            ),
            "python-web-api": ProjectTemplate(
                name="Python Web API",
                description="A REST API using FastAPI with modern Python practices",
                category="web",
                language="python",
                framework="fastapi",
                variables=[
                    TemplateVariable("project_name", "Project name", default="my-api"),
                    TemplateVariable(
                        "package_name", "Python package name", default="my_api"
                    ),
                    TemplateVariable("author_name", "Author name", default="Your Name"),
                    TemplateVariable(
                        "description", "Project description", default="A Python Web API"
                    ),
                    TemplateVariable(
                        "include_database",
                        "Include database integration",
                        type="boolean",
                        default=True,
                    ),
                    TemplateVariable(
                        "database_type",
                        "Database type",
                        default="postgresql",
                        choices=["postgresql", "mysql", "sqlite"],
                    ),
                    TemplateVariable(
                        "include_auth",
                        "Include authentication",
                        type="boolean",
                        default=True,
                    ),
                    TemplateVariable(
                        "include_docker",
                        "Include Docker configuration",
                        type="boolean",
                        default=True,
                    ),
                ],
                files=[
                    TemplateFile("python-web-api/README.md.j2", "README.md"),
                    TemplateFile("python-web-api/pyproject.toml.j2", "pyproject.toml"),
                    TemplateFile(
                        "python-web-api/src/main.py.j2",
                        "src/{{ package_name }}/main.py",
                    ),
                    TemplateFile(
                        "python-web-api/src/api/__init__.py.j2",
                        "src/{{ package_name }}/api/__init__.py",
                    ),
                    TemplateFile(
                        "python-web-api/src/api/routes.py.j2",
                        "src/{{ package_name }}/api/routes.py",
                    ),
                    TemplateFile(
                        "python-web-api/src/models.py.j2",
                        "src/{{ package_name }}/models.py",
                        condition="include_database",
                    ),
                    TemplateFile(
                        "python-web-api/src/auth.py.j2",
                        "src/{{ package_name }}/auth.py",
                        condition="include_auth",
                    ),
                    TemplateFile(
                        "python-web-api/Dockerfile.j2",
                        "Dockerfile",
                        condition="include_docker",
                    ),
                    TemplateFile(
                        "python-web-api/docker-compose.yml.j2",
                        "docker-compose.yml",
                        condition="include_docker",
                    ),
                ],
                tags=["python", "web", "api", "fastapi"],
            ),
            "react-app": ProjectTemplate(
                name="React Application",
                description="A modern React application with TypeScript and best practices",
                category="web",
                language="typescript",
                framework="react",
                variables=[
                    TemplateVariable(
                        "project_name", "Project name", default="my-react-app"
                    ),
                    TemplateVariable(
                        "description",
                        "Project description",
                        default="A React application",
                    ),
                    TemplateVariable(
                        "use_typescript", "Use TypeScript", type="boolean", default=True
                    ),
                    TemplateVariable(
                        "styling_solution",
                        "Styling solution",
                        default="tailwind",
                        choices=["css", "scss", "styled-components", "tailwind"],
                    ),
                    TemplateVariable(
                        "state_management",
                        "State management",
                        default="redux",
                        choices=["none", "context", "redux", "zustand"],
                    ),
                    TemplateVariable(
                        "include_router",
                        "Include React Router",
                        type="boolean",
                        default=True,
                    ),
                    TemplateVariable(
                        "include_testing",
                        "Include testing setup",
                        type="boolean",
                        default=True,
                    ),
                ],
                files=[
                    TemplateFile("react-app/package.json.j2", "package.json"),
                    TemplateFile("react-app/README.md.j2", "README.md"),
                    TemplateFile("react-app/public/index.html.j2", "public/index.html"),
                    TemplateFile(
                        "react-app/src/index.tsx.j2",
                        "src/index.tsx",
                        condition="use_typescript",
                    ),
                    TemplateFile(
                        "react-app/src/index.jsx.j2",
                        "src/index.jsx",
                        condition="not use_typescript",
                    ),
                    TemplateFile(
                        "react-app/src/App.tsx.j2",
                        "src/App.tsx",
                        condition="use_typescript",
                    ),
                    TemplateFile(
                        "react-app/src/App.jsx.j2",
                        "src/App.jsx",
                        condition="not use_typescript",
                    ),
                    TemplateFile(
                        "react-app/tsconfig.json.j2",
                        "tsconfig.json",
                        condition="use_typescript",
                    ),
                ],
                tags=["react", "typescript", "web", "frontend"],
            ),
            "node-express-api": ProjectTemplate(
                name="Node.js Express API",
                description="A REST API using Express.js with TypeScript",
                category="web",
                language="typescript",
                framework="express",
                variables=[
                    TemplateVariable(
                        "project_name", "Project name", default="my-express-api"
                    ),
                    TemplateVariable(
                        "description",
                        "Project description",
                        default="A Node.js Express API",
                    ),
                    TemplateVariable(
                        "use_typescript", "Use TypeScript", type="boolean", default=True
                    ),
                    TemplateVariable(
                        "database_type",
                        "Database type",
                        default="mongodb",
                        choices=["mongodb", "postgresql", "mysql"],
                    ),
                    TemplateVariable(
                        "include_auth",
                        "Include authentication",
                        type="boolean",
                        default=True,
                    ),
                    TemplateVariable(
                        "include_swagger",
                        "Include Swagger documentation",
                        type="boolean",
                        default=True,
                    ),
                ],
                files=[
                    TemplateFile("node-express-api/package.json.j2", "package.json"),
                    TemplateFile("node-express-api/README.md.j2", "README.md"),
                    TemplateFile(
                        "node-express-api/src/index.ts.j2",
                        "src/index.ts",
                        condition="use_typescript",
                    ),
                    TemplateFile(
                        "node-express-api/src/index.js.j2",
                        "src/index.js",
                        condition="not use_typescript",
                    ),
                    TemplateFile(
                        "node-express-api/tsconfig.json.j2",
                        "tsconfig.json",
                        condition="use_typescript",
                    ),
                ],
                tags=["nodejs", "express", "api", "typescript"],
            ),
            "rust-cli": ProjectTemplate(
                name="Rust CLI Application",
                description="A command-line application using Clap and modern Rust practices",
                category="application",
                language="rust",
                framework="clap",
                variables=[
                    TemplateVariable(
                        "project_name", "Project name", default="my-rust-cli"
                    ),
                    TemplateVariable("author_name", "Author name", default="Your Name"),
                    TemplateVariable(
                        "author_email", "Author email", default="you@example.com"
                    ),
                    TemplateVariable(
                        "description",
                        "Project description",
                        default="A Rust CLI application",
                    ),
                    TemplateVariable(
                        "edition",
                        "Rust edition",
                        default="2021",
                        choices=["2018", "2021"],
                    ),
                ],
                files=[
                    TemplateFile("rust-cli/Cargo.toml.j2", "Cargo.toml"),
                    TemplateFile("rust-cli/README.md.j2", "README.md"),
                    TemplateFile("rust-cli/src/main.rs.j2", "src/main.rs"),
                    TemplateFile("rust-cli/src/lib.rs.j2", "src/lib.rs"),
                    TemplateFile(
                        "rust-cli/.gitignore", ".gitignore", is_template=False
                    ),
                ],
                tags=["rust", "cli", "clap"],
            ),
        }

        for template_id, template in builtin_templates.items():
            self.templates[template_id] = template

    def _load_user_templates(self) -> None:
        """Load user-defined templates."""
        try:
            for template_dir in self.user_templates_dir.iterdir():
                if template_dir.is_dir():
                    template_file = template_dir / "template.yaml"
                    if template_file.exists():
                        with open(template_file, "r") as f:
                            template_data = yaml.safe_load(f)

                        template = self._parse_template_config(
                            template_data, template_dir
                        )
                        if template:
                            self.templates[template_dir.name] = template

        except Exception as e:
            logger.warning(f"Error loading user templates: {e}")

    def _parse_template_config(
        self, config: Dict[str, Any], template_dir: Path
    ) -> Optional[ProjectTemplate]:
        """Parse template configuration from YAML."""
        try:
            # Parse variables
            variables = []
            for var_config in config.get("variables", []):
                variable = TemplateVariable(
                    name=var_config["name"],
                    description=var_config["description"],
                    type=var_config.get("type", "string"),
                    default=var_config.get("default"),
                    required=var_config.get("required", True),
                    choices=var_config.get("choices"),
                    validation_pattern=var_config.get("validation_pattern"),
                )
                variables.append(variable)

            # Parse files
            files = []
            for file_config in config.get("files", []):
                template_file = TemplateFile(
                    source_path=file_config["source"],
                    target_path=file_config["target"],
                    is_template=file_config.get("is_template", True),
                    executable=file_config.get("executable", False),
                    condition=file_config.get("condition"),
                )
                files.append(template_file)

            return ProjectTemplate(
                name=config["name"],
                description=config["description"],
                category=config.get("category", "custom"),
                language=config["language"],
                framework=config.get("framework"),
                variables=variables,
                files=files,
                post_generation_commands=config.get("post_generation_commands", []),
                dependencies=config.get("dependencies", []),
                tags=config.get("tags", []),
                version=config.get("version", "1.0.0"),
                author=config.get("author"),
                license=config.get("license"),
            )

        except Exception as e:
            logger.error(f"Error parsing template config: {e}")
            return None

    def list_templates(
        self, category: Optional[str] = None, language: Optional[str] = None
    ) -> List[ProjectTemplate]:
        """
        List available templates.

        Args:
            category: Filter by category
            language: Filter by language

        Returns:
            List of matching templates
        """
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if language:
            templates = [t for t in templates if t.language == language]

        return templates

    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def generate_project(
        self,
        template_id: str,
        target_directory: Path,
        variables: Dict[str, Any],
        overwrite: bool = False,
    ) -> bool:
        """
        Generate a project from a template.

        Args:
            template_id: Template identifier
            target_directory: Target directory for generation
            variables: Template variables
            overwrite: Whether to overwrite existing files

        Returns:
            True if successful, False otherwise
        """
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template '{template_id}' not found")
            return False

        try:
            # Validate variables
            if not self._validate_variables(template, variables):
                return False

            # Create target directory
            target_directory.mkdir(parents=True, exist_ok=True)

            # Generate files
            for template_file in template.files:
                if not template_file.should_include(variables):
                    continue

                success = self._generate_file(
                    template_file, target_directory, variables, overwrite
                )

                if not success:
                    logger.error(
                        f"Failed to generate file: {template_file.target_path}"
                    )
                    return False

            # Execute post-generation commands
            if template.post_generation_commands:
                self._execute_post_generation_commands(
                    template.post_generation_commands, target_directory, variables
                )

            logger.info(f"Successfully generated project from template '{template_id}'")
            return True

        except Exception as e:
            logger.error(f"Error generating project: {e}")
            return False

    def _validate_variables(
        self, template: ProjectTemplate, variables: Dict[str, Any]
    ) -> bool:
        """Validate template variables."""
        for var in template.variables:
            value = variables.get(var.name, var.default)

            if not var.validate(value):
                logger.error(f"Invalid value for variable '{var.name}': {value}")
                return False

            # Set default if not provided
            if var.name not in variables and var.default is not None:
                variables[var.name] = var.default

        return True

    def _generate_file(
        self,
        template_file: TemplateFile,
        target_directory: Path,
        variables: Dict[str, Any],
        overwrite: bool,
    ) -> bool:
        """Generate a single file from template."""
        try:
            # Resolve target path with variables
            target_path_str = self._render_string(template_file.target_path, variables)
            target_path = target_directory / target_path_str

            # Create parent directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists and overwrite is disabled
            if target_path.exists() and not overwrite:
                logger.warning(f"File exists, skipping: {target_path}")
                return True

            if template_file.is_template:
                # Render template
                template = self.jinja_env.get_template(template_file.source_path)
                content = template.render(**variables)
            else:
                # Copy file as-is
                source_path = self.builtin_templates_dir / template_file.source_path
                if not source_path.exists():
                    source_path = self.user_templates_dir / template_file.source_path

                with open(source_path, "r") as f:
                    content = f.read()

            # Write file
            with open(target_path, "w") as f:
                f.write(content)

            # Set executable if needed
            if template_file.executable:
                target_path.chmod(0o755)

            return True

        except Exception as e:
            logger.error(f"Error generating file '{template_file.target_path}': {e}")
            return False

    def _render_string(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render a template string with variables."""
        template = Template(template_str)
        return template.render(**variables)

    def _execute_post_generation_commands(
        self, commands: List[str], target_directory: Path, variables: Dict[str, Any]
    ) -> None:
        """Execute post-generation commands."""
        import subprocess

        for command in commands:
            try:
                # Render command with variables
                rendered_command = self._render_string(command, variables)

                # Execute command
                result = subprocess.run(
                    rendered_command,
                    shell=True,
                    cwd=target_directory,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info(f"Executed command: {rendered_command}")
                else:
                    logger.warning(f"Command failed: {rendered_command}")
                    logger.warning(f"Error: {result.stderr}")

            except Exception as e:
                logger.error(f"Error executing command '{command}': {e}")

    def create_template_from_project(
        self,
        project_path: Path,
        template_id: str,
        template_name: str,
        description: str,
        variables: List[TemplateVariable],
    ) -> bool:
        """
        Create a template from an existing project.

        Args:
            project_path: Path to existing project
            template_id: Template identifier
            template_name: Template name
            description: Template description
            variables: Template variables

        Returns:
            True if successful, False otherwise
        """
        try:
            template_dir = self.user_templates_dir / template_id
            template_dir.mkdir(parents=True, exist_ok=True)

            # Copy project files
            files_dir = template_dir / "files"
            if files_dir.exists():
                shutil.rmtree(files_dir)

            shutil.copytree(project_path, files_dir)

            # Create template configuration
            template_config = {
                "name": template_name,
                "description": description,
                "category": "custom",
                "language": "unknown",
                "variables": [
                    {
                        "name": var.name,
                        "description": var.description,
                        "type": var.type,
                        "default": var.default,
                        "required": var.required,
                        "choices": var.choices,
                        "validation_pattern": var.validation_pattern,
                    }
                    for var in variables
                ],
                "files": [],  # Will be populated by scanning files
                "tags": ["custom"],
            }

            # Scan files and create file list
            for file_path in files_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(files_dir)
                    template_config["files"].append(
                        {
                            "source": str(relative_path),
                            "target": str(relative_path),
                            "is_template": True,
                        }
                    )

            # Save template configuration
            with open(template_dir / "template.yaml", "w") as f:
                yaml.dump(template_config, f, default_flow_style=False)

            logger.info(f"Created template '{template_id}' from project")
            return True

        except Exception as e:
            logger.error(f"Error creating template from project: {e}")
            return False

    def get_template_variables(self, template_id: str) -> List[TemplateVariable]:
        """Get variables for a template."""
        template = self.get_template(template_id)
        return template.variables if template else []

    def validate_template_variables(
        self, template_id: str, variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Validate template variables and return validation errors.

        Args:
            template_id: Template identifier
            variables: Variables to validate

        Returns:
            Dictionary of variable name -> error message
        """
        template = self.get_template(template_id)
        if not template:
            return {"template": "Template not found"}

        errors = {}

        for var in template.variables:
            value = variables.get(var.name)

            if var.required and value is None:
                errors[var.name] = "This field is required"
                continue

            if value is not None and not var.validate(value):
                if var.choices:
                    errors[var.name] = f"Must be one of: {', '.join(var.choices)}"
                elif var.validation_pattern:
                    errors[var.name] = f"Must match pattern: {var.validation_pattern}"
                else:
                    errors[var.name] = f"Invalid {var.type} value"

        return errors

    def get_template_preview(
        self, template_id: str, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get a preview of what files will be generated.

        Args:
            template_id: Template identifier
            variables: Template variables

        Returns:
            Preview information
        """
        template = self.get_template(template_id)
        if not template:
            return {}

        preview = {"template": template.name, "files": [], "commands": []}

        # Preview files
        for template_file in template.files:
            if template_file.should_include(variables):
                target_path = self._render_string(template_file.target_path, variables)
                preview["files"].append(
                    {
                        "path": target_path,
                        "type": "template" if template_file.is_template else "static",
                        "executable": template_file.executable,
                    }
                )

        # Preview commands
        for command in template.post_generation_commands:
            rendered_command = self._render_string(command, variables)
            preview["commands"].append(rendered_command)

        return preview

    def export_template(self, template_id: str, export_path: Path) -> bool:
        """
        Export a template to a file.

        Args:
            template_id: Template identifier
            export_path: Export file path

        Returns:
            True if successful, False otherwise
        """
        template = self.get_template(template_id)
        if not template:
            return False

        try:
            # Create export data
            export_data = {
                "template": {
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "language": template.language,
                    "framework": template.framework,
                    "version": template.version,
                    "author": template.author,
                    "license": template.license,
                    "tags": template.tags,
                    "variables": [
                        {
                            "name": var.name,
                            "description": var.description,
                            "type": var.type,
                            "default": var.default,
                            "required": var.required,
                            "choices": var.choices,
                            "validation_pattern": var.validation_pattern,
                        }
                        for var in template.variables
                    ],
                    "files": [
                        {
                            "source": file.source_path,
                            "target": file.target_path,
                            "is_template": file.is_template,
                            "executable": file.executable,
                            "condition": file.condition,
                        }
                        for file in template.files
                    ],
                    "post_generation_commands": template.post_generation_commands,
                    "dependencies": template.dependencies,
                }
            }

            # Write export file
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Exported template '{template_id}' to '{export_path}'")
            return True

        except Exception as e:
            logger.error(f"Error exporting template: {e}")
            return False

    def import_template(
        self, import_path: Path, template_id: Optional[str] = None
    ) -> bool:
        """
        Import a template from a file.

        Args:
            import_path: Import file path
            template_id: Optional template ID (defaults to filename)

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(import_path, "r") as f:
                import_data = json.load(f)

            template_data = import_data["template"]

            if not template_id:
                template_id = import_path.stem

            # Create template
            variables = [
                TemplateVariable(
                    name=var["name"],
                    description=var["description"],
                    type=var.get("type", "string"),
                    default=var.get("default"),
                    required=var.get("required", True),
                    choices=var.get("choices"),
                    validation_pattern=var.get("validation_pattern"),
                )
                for var in template_data["variables"]
            ]

            files = [
                TemplateFile(
                    source_path=file["source"],
                    target_path=file["target"],
                    is_template=file.get("is_template", True),
                    executable=file.get("executable", False),
                    condition=file.get("condition"),
                )
                for file in template_data["files"]
            ]

            template = ProjectTemplate(
                name=template_data["name"],
                description=template_data["description"],
                category=template_data.get("category", "imported"),
                language=template_data["language"],
                framework=template_data.get("framework"),
                variables=variables,
                files=files,
                post_generation_commands=template_data.get(
                    "post_generation_commands", []
                ),
                dependencies=template_data.get("dependencies", []),
                tags=template_data.get("tags", []),
                version=template_data.get("version", "1.0.0"),
                author=template_data.get("author"),
                license=template_data.get("license"),
            )

            self.templates[template_id] = template

            logger.info(f"Imported template '{template_id}' from '{import_path}'")
            return True

        except Exception as e:
            logger.error(f"Error importing template: {e}")
            return False


# Global template engine instance
_template_engine: Optional[TemplateEngine] = None


def get_template_engine(config: AppConfig) -> TemplateEngine:
    """
    Get global template engine instance.

    Args:
        config: Application configuration

    Returns:
        TemplateEngine instance
    """
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine(config)
    return _template_engine
