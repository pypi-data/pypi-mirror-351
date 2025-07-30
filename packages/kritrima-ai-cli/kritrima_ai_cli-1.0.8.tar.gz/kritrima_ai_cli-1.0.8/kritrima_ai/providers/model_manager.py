"""
Model manager for AI provider model discovery and management.

This module provides model discovery, validation, and management capabilities
across different AI providers.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.config.providers import get_provider_models, list_providers
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ModelInfo:
    """Information about an AI model."""

    id: str
    provider: str
    context_length: Optional[int] = None
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_streaming: bool = True
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None


class ModelManager:
    """
    Model discovery and management system.

    Handles model discovery, validation, and selection across
    different AI providers.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize model manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self._model_cache: Dict[str, List[ModelInfo]] = {}

        logger.info("Model manager initialized")

    async def list_models(self, provider: Optional[str] = None) -> List[ModelInfo]:
        """
        List available models for a provider.

        Args:
            provider: Provider to list models for (defaults to configured provider)

        Returns:
            List of available models
        """
        provider = provider or self.config.provider

        # Check cache first
        if provider in self._model_cache:
            return self._model_cache[provider]

        try:
            # Get static models from provider configuration
            static_models = get_provider_models(provider)

            # Convert to ModelInfo objects
            models = []
            for model_id in static_models:
                model_info = self._create_model_info_from_id(model_id, provider)
                models.append(model_info)

            # Cache the results
            self._model_cache[provider] = models

            return models

        except Exception as e:
            logger.error(f"Error listing models for {provider}: {e}")
            return []

    def _create_model_info_from_id(self, model_id: str, provider: str) -> ModelInfo:
        """
        Create ModelInfo from model ID and provider.

        Args:
            model_id: Model identifier
            provider: Provider name

        Returns:
            ModelInfo object
        """
        # Set default capabilities based on provider and model
        context_length = None
        supports_vision = False
        supports_function_calling = False

        if provider == "openai":
            if "gpt-4" in model_id:
                context_length = 128000 if "turbo" in model_id else 8192
                supports_function_calling = True
                supports_vision = "vision" in model_id or "gpt-4o" in model_id
            elif "gpt-3.5" in model_id:
                context_length = 16385 if "16k" in model_id else 4096
                supports_function_calling = True

        elif provider == "anthropic":
            if "claude-3" in model_id:
                context_length = 200000
                supports_function_calling = True
                supports_vision = "opus" in model_id or "sonnet" in model_id

        elif provider == "gemini":
            if "gemini" in model_id:
                context_length = 1000000 if "1.5" in model_id else 32000
                supports_function_calling = True
                supports_vision = "pro" in model_id

        return ModelInfo(
            id=model_id,
            provider=provider,
            context_length=context_length,
            supports_vision=supports_vision,
            supports_function_calling=supports_function_calling,
            supports_streaming=True,  # Most models support streaming
        )

    async def validate_model(self, model_id: str, provider: str) -> bool:
        """
        Validate that a model is available for a provider.

        Args:
            model_id: Model identifier
            provider: Provider name

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = await self.list_models(provider)
            return any(model.id == model_id for model in models)
        except Exception as e:
            logger.error(f"Error validating model {model_id} for {provider}: {e}")
            return False

    def get_model_info(self, model_id: str, provider: str) -> Optional[ModelInfo]:
        """
        Get information about a specific model.

        Args:
            model_id: Model identifier
            provider: Provider name

        Returns:
            ModelInfo if found, None otherwise
        """
        if provider in self._model_cache:
            for model in self._model_cache[provider]:
                if model.id == model_id:
                    return model

        return None

    async def get_recommended_model(self, provider: str) -> Optional[str]:
        """
        Get a recommended model for a provider.

        Args:
            provider: Provider name

        Returns:
            Recommended model ID, or None if none available
        """
        try:
            models = await self.list_models(provider)

            if not models:
                return None

            # Recommendation logic based on provider
            if provider == "openai":
                # Prefer GPT-4 models
                for model in models:
                    if "gpt-4o" in model.id:
                        return model.id
                for model in models:
                    if "gpt-4" in model.id and "vision" not in model.id:
                        return model.id
                # Fallback to GPT-3.5
                for model in models:
                    if "gpt-3.5-turbo" in model.id:
                        return model.id

            elif provider == "anthropic":
                # Prefer Claude 3.5 Sonnet, then Claude 3 Sonnet
                for model in models:
                    if "claude-3-5-sonnet" in model.id:
                        return model.id
                for model in models:
                    if "claude-3-sonnet" in model.id:
                        return model.id

            elif provider == "gemini":
                # Prefer Gemini 1.5 Pro
                for model in models:
                    if "gemini-1.5-pro" in model.id:
                        return model.id
                for model in models:
                    if "gemini-pro" in model.id:
                        return model.id

            # Default to first available model
            return models[0].id if models else None

        except Exception as e:
            logger.error(f"Error getting recommended model for {provider}: {e}")
            return None

    async def refresh_cache(self, provider: Optional[str] = None) -> None:
        """
        Refresh the model cache for a provider.

        Args:
            provider: Provider to refresh (defaults to all providers)
        """
        if provider:
            if provider in self._model_cache:
                del self._model_cache[provider]
            await self.list_models(provider)
        else:
            self._model_cache.clear()
            # Refresh all available providers
            for provider_id in list_providers():
                try:
                    await self.list_models(provider_id)
                except Exception as e:
                    logger.debug(f"Could not refresh models for {provider_id}: {e}")

    def get_cached_models(self, provider: str) -> List[ModelInfo]:
        """
        Get cached models for a provider.

        Args:
            provider: Provider name

        Returns:
            List of cached models
        """
        return self._model_cache.get(provider, [])

    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._model_cache.clear()
        logger.debug("Model cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get model manager statistics.

        Returns:
            Statistics dictionary
        """
        total_models = sum(len(models) for models in self._model_cache.values())

        return {
            "cached_providers": len(self._model_cache),
            "total_cached_models": total_models,
            "providers": {
                provider: len(models) for provider, models in self._model_cache.items()
            },
        }
