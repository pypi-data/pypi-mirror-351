"""
Application configuration management.

This module handles the main application configuration, including loading from
files, environment variables, and command-line arguments.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import platformdirs
import yaml
from pydantic import BaseModel, Field

from kritrima_ai.config.providers import load_custom_providers
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)

# Type definitions
ApprovalMode = Literal["suggest", "auto-edit", "full-auto"]
Theme = Literal["dark", "light", "auto"]


class UIConfig(BaseModel):
    """UI-related configuration."""

    theme: Theme = Field(default="dark", description="UI theme")
    notifications: bool = Field(
        default=True, description="Enable desktop notifications"
    )
    auto_save: bool = Field(default=True, description="Automatically save sessions")
    max_history_items: int = Field(
        default=1000, description="Maximum items in command history"
    )
    show_thinking: bool = Field(default=True, description="Show AI thinking indicators")
    confirm_dangerous_commands: bool = Field(
        default=True, description="Confirm dangerous commands"
    )


class SecurityConfig(BaseModel):
    """Security-related configuration."""

    enable_sandbox: bool = Field(default=True, description="Enable command sandboxing")
    safe_commands: List[str] = Field(
        default_factory=lambda: [
            "ls",
            "dir",
            "cat",
            "type",
            "head",
            "tail",
            "grep",
            "findstr",
            "find",
            "pwd",
            "cd",
            "echo",
            "which",
            "where",
            "ps",
            "top",
            "df",
            "du",
            "free",
            "uptime",
            "date",
            "whoami",
            "id",
        ],
        description="Commands that are considered safe for auto-approval",
    )
    dangerous_commands: List[str] = Field(
        default_factory=lambda: [
            "rm",
            "del",
            "rmdir",
            "rd",
            "mv",
            "move",
            "sudo",
            "su",
            "chmod",
            "chown",
            "format",
            "fdisk",
            "mkfs",
            "mount",
            "umount",
            "kill",
            "killall",
            "taskkill",
            "shutdown",
            "reboot",
            "halt",
            "init",
        ],
        description="Commands that require explicit approval",
    )
    writable_roots: List[str] = Field(
        default_factory=list,
        description="Additional writable root directories for sandboxing",
    )


class SessionConfig(BaseModel):
    """Session management configuration."""

    auto_save_interval: int = Field(
        default=300, description="Auto-save interval in seconds"
    )
    max_session_size: int = Field(
        default=10_000_000, description="Maximum session size in bytes"
    )
    compress_old_sessions: bool = Field(
        default=True, description="Compress old sessions"
    )
    session_retention_days: int = Field(default=30, description="Days to keep sessions")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Logging level")
    file_logging: bool = Field(default=True, description="Enable file logging")
    console_logging: bool = Field(default=False, description="Enable console logging")
    max_file_size: int = Field(
        default=10_000_000, description="Maximum log file size in bytes"
    )
    backup_count: int = Field(
        default=5, description="Number of backup log files to keep"
    )


@dataclass
class AppConfig:
    """Main application configuration."""

    # Core settings
    model: str = "gpt-4"
    provider: str = "openai"
    approval_mode: ApprovalMode = "suggest"

    # Configuration management
    config_file: Optional[Path] = None
    custom_providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Sub-configurations
    ui: UIConfig = field(default_factory=UIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Advanced settings
    context_window: Optional[int] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 60
    max_retries: int = 3

    # Git integration
    suppress_git_warnings: bool = False
    auto_commit: bool = False

    # Development settings
    debug: bool = False
    verbose: bool = False

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Convert dict configs to Pydantic models if needed
        if isinstance(self.ui, dict):
            self.ui = UIConfig(**self.ui)
        if isinstance(self.security, dict):
            self.security = SecurityConfig(**self.security)
        if isinstance(self.session, dict):
            self.session = SessionConfig(**self.session)
        if isinstance(self.logging, dict):
            self.logging = LoggingConfig(**self.logging)

        # Load custom providers
        if self.custom_providers:
            load_custom_providers(self.custom_providers)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            "model": self.model,
            "provider": self.provider,
            "approval_mode": self.approval_mode,
            "custom_providers": self.custom_providers,
            "ui": self.ui.model_dump() if isinstance(self.ui, UIConfig) else self.ui,
            "security": (
                self.security.model_dump()
                if isinstance(self.security, SecurityConfig)
                else self.security
            ),
            "session": (
                self.session.model_dump()
                if isinstance(self.session, SessionConfig)
                else self.session
            ),
            "logging": (
                self.logging.model_dump()
                if isinstance(self.logging, LoggingConfig)
                else self.logging
            ),
            "context_window": self.context_window,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "suppress_git_warnings": self.suppress_git_warnings,
            "auto_commit": self.auto_commit,
            "debug": self.debug,
            "verbose": self.verbose,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], config_file: Optional[Path] = None
    ) -> "AppConfig":
        """Create config from dictionary."""
        # Handle sub-configurations
        ui_data = data.get("ui", {})
        security_data = data.get("security", {})
        session_data = data.get("session", {})
        logging_data = data.get("logging", {})

        return cls(
            model=data.get("model", "gpt-4"),
            provider=data.get("provider", "openai"),
            approval_mode=data.get("approval_mode", "suggest"),
            config_file=config_file,
            custom_providers=data.get("custom_providers", {}),
            ui=UIConfig(**ui_data),
            security=SecurityConfig(**security_data),
            session=SessionConfig(**session_data),
            logging=LoggingConfig(**logging_data),
            context_window=data.get("context_window"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            timeout=data.get("timeout", 60),
            max_retries=data.get("max_retries", 3),
            suppress_git_warnings=data.get("suppress_git_warnings", False),
            auto_commit=data.get("auto_commit", False),
            debug=data.get("debug", False),
            verbose=data.get("verbose", False),
        )


def get_config_dir() -> Path:
    """Get the configuration directory."""
    return Path(platformdirs.user_config_dir("kritrima-ai"))


def get_data_dir() -> Path:
    """Get the data directory."""
    return Path(platformdirs.user_data_dir("kritrima-ai"))


def get_cache_dir() -> Path:
    """Get the cache directory."""
    return Path(platformdirs.user_cache_dir("kritrima-ai"))


def get_config_paths() -> List[Path]:
    """
    Get configuration file paths in order of precedence.

    Returns:
        List of configuration file paths to check.
    """
    paths = []

    # Project-specific configuration
    project_config = Path.cwd() / ".kritrima-ai" / "config.json"
    if project_config.exists():
        paths.append(project_config)

    project_config_yaml = Path.cwd() / ".kritrima-ai" / "config.yaml"
    if project_config_yaml.exists():
        paths.append(project_config_yaml)

    # User configuration
    config_dir = get_config_dir()
    user_config = config_dir / "config.json"
    if user_config.exists():
        paths.append(user_config)

    user_config_yaml = config_dir / "config.yaml"
    if user_config_yaml.exists():
        paths.append(user_config_yaml)

    return paths


def load_config_file(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from a file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                return yaml.safe_load(f) or {}
            else:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config file {config_path}: {e}")
        return {}


def save_config_file(config: AppConfig, config_path: Path) -> None:
    """
    Save configuration to a file.

    Args:
        config: Configuration to save
        config_path: Path to save the configuration
    """
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = config.to_dict()

        with open(config_path, "w", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_data, f, indent=2)

        logger.info(f"Configuration saved to {config_path}")

    except Exception as e:
        logger.error(f"Failed to save config file {config_path}: {e}")
        raise


def load_config(config_file: Optional[Path] = None) -> AppConfig:
    """
    Load application configuration.

    Args:
        config_file: Specific configuration file to load

    Returns:
        Loaded configuration
    """
    config_data = {}
    used_config_file = None

    if config_file:
        # Load specific config file
        if config_file.exists():
            config_data = load_config_file(config_file)
            used_config_file = config_file
        else:
            logger.warning(f"Specified config file not found: {config_file}")
    else:
        # Load from standard locations
        for config_path in get_config_paths():
            if config_path.exists():
                file_config = load_config_file(config_path)
                # Merge configurations (later files override earlier ones)
                config_data.update(file_config)
                used_config_file = config_path

    # Override with environment variables
    env_overrides = load_env_config()
    config_data.update(env_overrides)

    # Create configuration object
    config = AppConfig.from_dict(config_data, used_config_file)

    return config


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Returns:
        Configuration dictionary from environment variables
    """
    env_config = {}

    # Main settings
    if model := os.getenv("KRITRIMA_AI_MODEL"):
        env_config["model"] = model

    if provider := os.getenv("KRITRIMA_AI_PROVIDER"):
        env_config["provider"] = provider

    if approval_mode := os.getenv("KRITRIMA_AI_APPROVAL_MODE"):
        env_config["approval_mode"] = approval_mode

    # Advanced settings
    if context_window := os.getenv("KRITRIMA_AI_CONTEXT_WINDOW"):
        try:
            env_config["context_window"] = int(context_window)
        except ValueError:
            logger.warning(f"Invalid context window value: {context_window}")

    if temperature := os.getenv("KRITRIMA_AI_TEMPERATURE"):
        try:
            env_config["temperature"] = float(temperature)
        except ValueError:
            logger.warning(f"Invalid temperature value: {temperature}")

    if max_tokens := os.getenv("KRITRIMA_AI_MAX_TOKENS"):
        try:
            env_config["max_tokens"] = int(max_tokens)
        except ValueError:
            logger.warning(f"Invalid max tokens value: {max_tokens}")

    # Boolean settings
    if debug := os.getenv("KRITRIMA_AI_DEBUG"):
        env_config["debug"] = debug.lower() in ("true", "1", "yes", "on")

    if verbose := os.getenv("KRITRIMA_AI_VERBOSE"):
        env_config["verbose"] = verbose.lower() in ("true", "1", "yes", "on")

    return env_config


def save_config(config: AppConfig, config_file: Optional[Path] = None) -> None:
    """
    Save application configuration.

    Args:
        config: Configuration to save
        config_file: Specific file to save to (defaults to user config)
    """
    if not config_file:
        config_dir = get_config_dir()
        config_file = config_dir / "config.json"

    save_config_file(config, config_file)
    config.config_file = config_file


def reset_config() -> None:
    """Reset configuration to defaults by removing config files."""
    config_paths = get_config_paths()

    for config_path in config_paths:
        try:
            if config_path.exists():
                config_path.unlink()
                logger.info(f"Removed config file: {config_path}")
        except Exception as e:
            logger.error(f"Failed to remove config file {config_path}: {e}")

    # Also remove the entire config directory if empty
    config_dir = get_config_dir()
    try:
        if config_dir.exists() and not any(config_dir.iterdir()):
            config_dir.rmdir()
            logger.info(f"Removed empty config directory: {config_dir}")
    except Exception as e:
        logger.debug(f"Could not remove config directory: {e}")


def create_default_config() -> AppConfig:
    """Create a default configuration."""
    return AppConfig()


def validate_config(config: AppConfig) -> List[str]:
    """
    Validate configuration and return any errors.

    Args:
        config: Configuration to validate

    Returns:
        List of validation error messages
    """
    errors = []

    # Validate approval mode
    if config.approval_mode not in ["suggest", "auto-edit", "full-auto"]:
        errors.append(f"Invalid approval mode: {config.approval_mode}")

    # Validate temperature
    if not 0.0 <= config.temperature <= 2.0:
        errors.append(
            f"Temperature must be between 0.0 and 2.0, got: {config.temperature}"
        )

    # Validate timeout
    if config.timeout <= 0:
        errors.append(f"Timeout must be positive, got: {config.timeout}")

    # Validate max_retries
    if config.max_retries < 0:
        errors.append(f"Max retries must be non-negative, got: {config.max_retries}")

    # Validate context_window if set
    if config.context_window is not None and config.context_window <= 0:
        errors.append(f"Context window must be positive, got: {config.context_window}")

    # Validate max_tokens if set
    if config.max_tokens is not None and config.max_tokens <= 0:
        errors.append(f"Max tokens must be positive, got: {config.max_tokens}")

    return errors
