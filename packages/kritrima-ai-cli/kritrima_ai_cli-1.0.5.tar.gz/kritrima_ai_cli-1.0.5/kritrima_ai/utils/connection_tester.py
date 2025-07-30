"""
Connection tester for AI providers.

This module provides utilities to test API connections to various AI providers
and validate that the configuration is working correctly.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.providers.ai_client import AIClient
from kritrima_ai.providers.model_manager import ModelManager
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionTestResult:
    """Result of a connection test."""

    success: bool
    error: Optional[str] = None
    response_time: Optional[float] = None
    available_models: Optional[List[str]] = None
    provider_info: Optional[Dict[str, Any]] = None


class ConnectionTester:
    """Test connections to AI providers."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize connection tester.

        Args:
            config: Application configuration
        """
        self.config = config

    async def test_connection(self) -> ConnectionTestResult:
        """
        Test connection to the configured AI provider.

        Returns:
            Connection test result
        """
        try:
            import time

            start_time = time.time()

            # Create AI client
            ai_client = AIClient(self.config)

            # Test basic connection with a simple message
            test_messages = [
                {"role": "user", "content": "Hello, please respond with just 'OK'"}
            ]

            response = await ai_client.chat_completion(
                messages=test_messages, stream=False
            )

            response_time = time.time() - start_time

            # Check if we got a valid response
            if response and "choices" in response and len(response["choices"]) > 0:
                # Try to get available models
                available_models = []
                try:
                    model_manager = ModelManager(self.config)
                    models = await model_manager.list_models()
                    available_models = [model.id for model in models] if models else []
                except Exception as e:
                    logger.warning(f"Could not fetch models: {e}")

                # Get provider info
                provider_info = {
                    "provider": self.config.provider,
                    "model": self.config.model,
                    "base_url": ai_client.base_url,
                }

                return ConnectionTestResult(
                    success=True,
                    response_time=response_time,
                    available_models=available_models,
                    provider_info=provider_info,
                )
            else:
                return ConnectionTestResult(
                    success=False, error="Invalid response format from provider"
                )

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return ConnectionTestResult(success=False, error=str(e))

    async def test_model_availability(self, model: str) -> bool:
        """
        Test if a specific model is available.

        Args:
            model: Model name to test

        Returns:
            True if model is available, False otherwise
        """
        try:
            # Create a temporary config with the specified model
            test_config = AppConfig(
                provider=self.config.provider, model=model, api_key=self.config.api_key
            )

            ai_client = AIClient(test_config)

            # Test with a minimal request
            test_messages = [{"role": "user", "content": "test"}]

            response = await ai_client.chat_completion(
                messages=test_messages, stream=False
            )

            return response is not None and "choices" in response

        except Exception as e:
            logger.debug(f"Model {model} not available: {e}")
            return False

    async def test_all_providers(self) -> Dict[str, ConnectionTestResult]:
        """
        Test connections to all configured providers.

        Returns:
            Dictionary mapping provider names to test results
        """
        from kritrima_ai.config.providers import list_providers

        results = {}
        providers = list_providers()

        for provider_id, provider_info in providers.items():
            try:
                # Create config for this provider
                test_config = AppConfig(
                    provider=provider_id, model=self._get_default_model(provider_id)
                )

                # Test connection
                tester = ConnectionTester(test_config)
                result = await tester.test_connection()
                results[provider_id] = result

            except Exception as e:
                results[provider_id] = ConnectionTestResult(
                    success=False, error=f"Configuration error: {e}"
                )

        return results

    def _get_default_model(self, provider: str) -> str:
        """Get default model for a provider."""
        default_models = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-haiku-20240307",
            "gemini": "gemini-pro",
            "ollama": "llama2",
            "mistral": "mistral-tiny",
            "deepseek": "deepseek-chat",
            "xai": "grok-beta",
            "groq": "llama2-70b-4096",
            "arceeai": "arcee-agent",
            "openrouter": "openrouter/auto",
        }
        return default_models.get(provider, "gpt-3.5-turbo")
