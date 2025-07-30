"""
AI provider configuration and management.

This module provides comprehensive support for multiple AI providers with:
- Provider registration and discovery
- API key management and validation
- Feature detection (vision, function calling, etc.)
- Custom provider support
- Automatic model discovery
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class ProviderCapability(Enum):
    """AI provider capabilities."""

    CHAT_COMPLETION = "chat_completion"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    MULTIMODAL = "multimodal"
    CODE_INTERPRETER = "code_interpreter"


@dataclass
class ProviderInfo:
    """Information about an AI provider."""

    name: str
    base_url: str
    env_key: str
    default_model: str
    capabilities: Set[ProviderCapability] = field(default_factory=set)
    headers: Dict[str, str] = field(default_factory=dict)
    auth_type: str = "bearer"  # bearer, api_key, custom
    custom_auth_header: Optional[str] = None
    models: List[str] = field(default_factory=list)
    supports_streaming: bool = True
    max_context_length: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "base_url": self.base_url,
            "env_key": self.env_key,
            "default_model": self.default_model,
            "capabilities": [cap.value for cap in self.capabilities],
            "headers": self.headers,
            "auth_type": self.auth_type,
            "custom_auth_header": self.custom_auth_header,
            "models": self.models,
            "supports_streaming": self.supports_streaming,
            "max_context_length": self.max_context_length,
        }


# Global provider registry
_providers: Dict[str, ProviderInfo] = {}
_custom_providers: Dict[str, ProviderInfo] = {}


def _initialize_default_providers() -> None:
    """Initialize default AI providers."""
    global _providers

    # OpenAI
    _providers["openai"] = ProviderInfo(
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        env_key="OPENAI_API_KEY",
        default_model="gpt-4",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.VISION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
            ProviderCapability.EMBEDDINGS,
            ProviderCapability.IMAGE_GENERATION,
            ProviderCapability.MULTIMODAL,
        },
        models=[
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-vision-preview",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ],
        max_context_length=128000,
    )

    # Anthropic
    _providers["anthropic"] = ProviderInfo(
        name="Anthropic",
        base_url="https://api.anthropic.com",
        env_key="ANTHROPIC_API_KEY",
        default_model="claude-3-sonnet-20240229",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.VISION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
            ProviderCapability.MULTIMODAL,
        },
        auth_type="api_key",
        custom_auth_header="x-api-key",
        models=[
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
        ],
        max_context_length=200000,
    )

    # Google Gemini
    _providers["gemini"] = ProviderInfo(
        name="Google Gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        env_key="GOOGLE_AI_KEY",
        default_model="gemini-pro",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.VISION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
            ProviderCapability.MULTIMODAL,
        },
        auth_type="query_param",  # Uses query parameter instead of header
        models=[
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
        max_context_length=1000000,
    )

    # Azure OpenAI
    _providers["azure"] = ProviderInfo(
        name="Azure OpenAI",
        base_url="https://{resource}.openai.azure.com/openai/deployments/{deployment}",
        env_key="AZURE_OPENAI_KEY",
        default_model="gpt-4",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.VISION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
            ProviderCapability.EMBEDDINGS,
        },
        headers={"api-version": "2024-02-15-preview"},
        models=["gpt-4", "gpt-35-turbo", "gpt-4-vision"],
        max_context_length=128000,
    )

    # Ollama
    _providers["ollama"] = ProviderInfo(
        name="Ollama",
        base_url="http://localhost:11434/v1",
        env_key="OLLAMA_API_KEY",
        default_model="llama2",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.STREAMING,
            ProviderCapability.EMBEDDINGS,
        },
        auth_type="none",  # Usually no auth for local Ollama
        models=[
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "codellama",
            "codellama:13b",
            "codellama:34b",
            "mistral",
            "mixtral",
            "phi",
            "neural-chat",
        ],
        max_context_length=4096,
    )

    # Mistral AI
    _providers["mistral"] = ProviderInfo(
        name="Mistral AI",
        base_url="https://api.mistral.ai/v1",
        env_key="MISTRAL_API_KEY",
        default_model="mistral-medium",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
            ProviderCapability.EMBEDDINGS,
        },
        models=[
            "mistral-tiny",
            "mistral-small",
            "mistral-medium",
            "mistral-large",
            "mixtral-8x7b",
            "mixtral-8x22b",
        ],
        max_context_length=32000,
    )

    # DeepSeek
    _providers["deepseek"] = ProviderInfo(
        name="DeepSeek",
        base_url="https://api.deepseek.com/v1",
        env_key="DEEPSEEK_API_KEY",
        default_model="deepseek-chat",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
        },
        models=["deepseek-chat", "deepseek-coder"],
        max_context_length=64000,
    )

    # xAI Grok
    _providers["xai"] = ProviderInfo(
        name="xAI",
        base_url="https://api.x.ai/v1",
        env_key="XAI_API_KEY",
        default_model="grok-beta",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
        },
        models=["grok-beta"],
        max_context_length=131072,
    )

    # Groq
    _providers["groq"] = ProviderInfo(
        name="Groq",
        base_url="https://api.groq.com/openai/v1",
        env_key="GROQ_API_KEY",
        default_model="mixtral-8x7b-32768",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
        },
        models=[
            "mixtral-8x7b-32768",
            "llama2-70b-4096",
            "gemma-7b-it",
            "whisper-large-v3",
        ],
        max_context_length=32768,
    )

    # ArceeAI
    _providers["arceeai"] = ProviderInfo(
        name="ArceeAI",
        base_url="https://api.arcee.ai/v1",
        env_key="ARCEEAI_API_KEY",
        default_model="arcee-agent",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.STREAMING,
        },
        models=["arcee-agent", "arcee-nova"],
        max_context_length=8192,
    )

    # OpenRouter
    _providers["openrouter"] = ProviderInfo(
        name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        env_key="OPENROUTER_API_KEY",
        default_model="openai/gpt-4",
        capabilities={
            ProviderCapability.CHAT_COMPLETION,
            ProviderCapability.VISION,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.STREAMING,
        },
        models=[
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "google/gemini-pro",
            "meta-llama/llama-2-70b-chat",
            "mistralai/mixtral-8x7b-instruct",
        ],
        max_context_length=128000,
    )


def register_provider(provider_id: str, provider_info: ProviderInfo) -> None:
    """
    Register a custom AI provider.

    Args:
        provider_id: Unique identifier for the provider
        provider_info: Provider configuration
    """
    global _custom_providers
    _custom_providers[provider_id] = provider_info
    logger.info(f"Registered custom provider: {provider_id}")


def get_provider_info(provider_id: str) -> Optional[ProviderInfo]:
    """
    Get provider information by ID.

    Args:
        provider_id: Provider identifier

    Returns:
        ProviderInfo if found, None otherwise
    """
    # Check custom providers first
    if provider_id in _custom_providers:
        return _custom_providers[provider_id]

    # Check default providers
    return _providers.get(provider_id)


def list_providers() -> Dict[str, ProviderInfo]:
    """
    List all available providers.

    Returns:
        Dictionary of provider ID to ProviderInfo
    """
    all_providers = {}
    all_providers.update(_providers)
    all_providers.update(_custom_providers)
    return all_providers


def get_api_key(provider_id: str) -> Optional[str]:
    """
    Get API key for a provider from environment variables.

    Args:
        provider_id: Provider identifier

    Returns:
        API key if found, None otherwise
    """
    provider_info = get_provider_info(provider_id)
    if not provider_info:
        return None

    return os.getenv(provider_info.env_key)


def get_base_url(provider_id: str) -> str:
    """
    Get base URL for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        Base URL for the provider
    """
    provider_info = get_provider_info(provider_id)
    if not provider_info:
        raise ValueError(f"Unknown provider: {provider_id}")

    base_url = provider_info.base_url

    # Handle Azure special case
    if provider_id == "azure":
        resource = os.getenv("AZURE_OPENAI_RESOURCE")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        if resource and deployment:
            base_url = base_url.format(resource=resource, deployment=deployment)
        else:
            logger.warning("Azure OpenAI resource or deployment not configured")

    return base_url


def get_default_model(provider_id: str) -> Optional[str]:
    """
    Get default model for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        Default model name if found, None otherwise
    """
    provider_info = get_provider_info(provider_id)
    return provider_info.default_model if provider_info else None


def provider_supports_capability(
    provider_id: str, capability: ProviderCapability
) -> bool:
    """
    Check if a provider supports a specific capability.

    Args:
        provider_id: Provider identifier
        capability: Capability to check

    Returns:
        True if provider supports capability, False otherwise
    """
    provider_info = get_provider_info(provider_id)
    if not provider_info:
        return False

    return capability in provider_info.capabilities


def get_providers_with_capability(capability: ProviderCapability) -> List[str]:
    """
    Get list of providers that support a specific capability.

    Args:
        capability: Capability to filter by

    Returns:
        List of provider IDs that support the capability
    """
    providers_with_capability = []

    for provider_id, provider_info in list_providers().items():
        if capability in provider_info.capabilities:
            providers_with_capability.append(provider_id)

    return providers_with_capability


def load_custom_providers(custom_config: Dict[str, Dict[str, Any]]) -> None:
    """
    Load custom providers from configuration.

    Args:
        custom_config: Dictionary of custom provider configurations
    """
    for provider_id, config in custom_config.items():
        try:
            # Convert capabilities from strings
            capabilities = set()
            for cap_str in config.get("capabilities", []):
                try:
                    capabilities.add(ProviderCapability(cap_str))
                except ValueError:
                    logger.warning(f"Unknown capability: {cap_str}")

            provider_info = ProviderInfo(
                name=config["name"],
                base_url=config["base_url"],
                env_key=config["env_key"],
                default_model=config.get("default_model", "default"),
                capabilities=capabilities,
                headers=config.get("headers", {}),
                auth_type=config.get("auth_type", "bearer"),
                custom_auth_header=config.get("custom_auth_header"),
                models=config.get("models", []),
                supports_streaming=config.get("supports_streaming", True),
                max_context_length=config.get("max_context_length"),
            )

            register_provider(provider_id, provider_info)

        except KeyError as e:
            logger.error(
                f"Invalid custom provider config for {provider_id}: missing {e}"
            )
        except Exception as e:
            logger.error(f"Error loading custom provider {provider_id}: {e}")


def create_auth_headers(provider_id: str, api_key: str) -> Dict[str, str]:
    """
    Create authentication headers for a provider.

    Args:
        provider_id: Provider identifier
        api_key: API key for authentication

    Returns:
        Dictionary of authentication headers
    """
    provider_info = get_provider_info(provider_id)
    if not provider_info:
        return {}

    headers = provider_info.headers.copy()

    if provider_info.auth_type == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    elif provider_info.auth_type == "api_key" and provider_info.custom_auth_header:
        headers[provider_info.custom_auth_header] = api_key
    elif provider_info.auth_type == "none":
        # No authentication required
        pass
    else:
        # Default to Bearer auth
        headers["Authorization"] = f"Bearer {api_key}"

    return headers


def validate_provider_config(provider_id: str) -> List[str]:
    """
    Validate provider configuration.

    Args:
        provider_id: Provider identifier

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    provider_info = get_provider_info(provider_id)
    if not provider_info:
        errors.append(f"Provider '{provider_id}' not found")
        return errors

    # Check API key
    api_key = get_api_key(provider_id)
    if not api_key and provider_info.auth_type != "none":
        errors.append(
            f"API key not found for provider '{provider_id}' (set {provider_info.env_key})"
        )

    # Validate base URL
    if not provider_info.base_url:
        errors.append(f"Base URL not configured for provider '{provider_id}'")

    # Check Azure-specific configuration
    if provider_id == "azure":
        if not os.getenv("AZURE_OPENAI_RESOURCE"):
            errors.append("AZURE_OPENAI_RESOURCE environment variable not set")
        if not os.getenv("AZURE_OPENAI_DEPLOYMENT"):
            errors.append("AZURE_OPENAI_DEPLOYMENT environment variable not set")

    return errors


def get_provider_models(provider_id: str) -> List[str]:
    """
    Get list of available models for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        List of model names
    """
    provider_info = get_provider_info(provider_id)
    return provider_info.models if provider_info else []


def detect_available_providers() -> Dict[str, bool]:
    """
    Detect which providers are available (have API keys configured).

    Returns:
        Dictionary mapping provider IDs to availability status
    """
    availability = {}

    for provider_id in list_providers():
        api_key = get_api_key(provider_id)
        provider_info = get_provider_info(provider_id)

        # Provider is available if it has an API key or doesn't require auth
        availability[provider_id] = bool(
            api_key or (provider_info and provider_info.auth_type == "none")
        )

    return availability


def get_recommended_provider() -> Optional[str]:
    """
    Get a recommended provider based on availability and capabilities.

    Returns:
        Recommended provider ID, or None if none available
    """
    available_providers = detect_available_providers()

    # Priority order for recommendations
    priority_order = [
        "openai",
        "anthropic",
        "gemini",
        "azure",
        "mistral",
        "groq",
        "deepseek",
        "xai",
        "openrouter",
        "ollama",
        "arceeai",
    ]

    for provider_id in priority_order:
        if available_providers.get(provider_id, False):
            return provider_id

    return None


# Initialize default providers on module import
_initialize_default_providers()

logger.debug(f"Initialized {len(_providers)} default AI providers")
