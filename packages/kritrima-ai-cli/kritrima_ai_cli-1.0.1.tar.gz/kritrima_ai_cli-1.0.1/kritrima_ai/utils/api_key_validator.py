"""
API key validation and connection testing for AI providers.

This module provides utilities to validate API keys and test connections
to various AI providers before starting the main application.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

from kritrima_ai.config.providers import get_api_key, get_base_url, get_provider_info
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionTestResult:
    """Result of a connection test."""

    success: bool
    provider: str
    model: Optional[str] = None
    error: Optional[str] = None
    response_time: Optional[float] = None
    available_models: Optional[List[str]] = None


async def validate_api_key(provider: str, model: Optional[str] = None) -> bool:
    """
    Validate API key for a provider by making a test request.

    Args:
        provider: Provider identifier
        model: Model to test (optional)

    Returns:
        True if API key is valid, False otherwise.
    """
    try:
        result = await test_provider_connection(provider, model)
        return result.success
    except Exception as e:
        logger.error(f"API key validation failed for {provider}: {e}")
        return False


async def test_provider_connection(
    provider: str, model: Optional[str] = None, timeout: int = 30
) -> ConnectionTestResult:
    """
    Test connection to an AI provider.

    Args:
        provider: Provider identifier
        model: Model to test (optional)
        timeout: Request timeout in seconds

    Returns:
        ConnectionTestResult with test details.
    """
    import time

    start_time = time.time()

    try:
        # Get provider info
        provider_info = get_provider_info(provider)
        api_key = get_api_key(provider)
        base_url = get_base_url(provider)

        if not api_key:
            return ConnectionTestResult(
                success=False,
                provider=provider,
                error=f"No API key found for {provider}. Set {provider_info.env_key} environment variable.",
            )

        # Test based on provider type
        if provider == "openai":
            result = await _test_openai_connection(base_url, api_key, model, timeout)
        elif provider == "anthropic":
            result = await _test_anthropic_connection(base_url, api_key, model, timeout)
        elif provider == "gemini":
            result = await _test_gemini_connection(base_url, api_key, model, timeout)
        elif provider == "ollama":
            result = await _test_ollama_connection(base_url, api_key, model, timeout)
        else:
            # Generic OpenAI-compatible test
            result = await _test_openai_compatible_connection(
                base_url, api_key, model, timeout
            )

        # Add timing and provider info
        result.provider = provider
        result.response_time = time.time() - start_time

        return result

    except Exception as e:
        logger.error(f"Connection test failed for {provider}: {e}")
        return ConnectionTestResult(
            success=False,
            provider=provider,
            error=str(e),
            response_time=time.time() - start_time,
        )


async def _test_openai_connection(
    base_url: str, api_key: str, model: Optional[str] = None, timeout: int = 30
) -> ConnectionTestResult:
    """Test OpenAI API connection."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            # First, try to list models
            models_response = await client.get(f"{base_url}/models", headers=headers)

            if models_response.status_code == 200:
                models_data = models_response.json()
                available_models = [m["id"] for m in models_data.get("data", [])]

                # Test with a simple completion request
                test_model = model or "gpt-3.5-turbo"
                if test_model not in available_models and available_models:
                    test_model = available_models[0]

                completion_data = {
                    "model": test_model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 1,
                }

                completion_response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=completion_data,
                )

                if completion_response.status_code == 200:
                    return ConnectionTestResult(
                        success=True,
                        provider="openai",
                        model=test_model,
                        available_models=available_models,
                    )
                else:
                    return ConnectionTestResult(
                        success=False,
                        provider="openai",
                        error=f"Completion test failed: {completion_response.status_code}",
                    )
            else:
                return ConnectionTestResult(
                    success=False,
                    provider="openai",
                    error=f"Models list failed: {models_response.status_code}",
                )

    except Exception as e:
        return ConnectionTestResult(
            success=False, provider="openai", error=f"Connection failed: {e}"
        )


async def _test_anthropic_connection(
    base_url: str, api_key: str, model: Optional[str] = None, timeout: int = 30
) -> ConnectionTestResult:
    """Test Anthropic API connection."""
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            test_model = model or "claude-3-sonnet-20240229"

            completion_data = {
                "model": test_model,
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}],
            }

            response = await client.post(
                f"{base_url}/v1/messages", headers=headers, json=completion_data
            )

            if response.status_code == 200:
                return ConnectionTestResult(
                    success=True, provider="anthropic", model=test_model
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    provider="anthropic",
                    error=f"API test failed: {response.status_code}",
                )

    except Exception as e:
        return ConnectionTestResult(
            success=False, provider="anthropic", error=f"Connection failed: {e}"
        )


async def _test_gemini_connection(
    base_url: str, api_key: str, model: Optional[str] = None, timeout: int = 30
) -> ConnectionTestResult:
    """Test Google Gemini API connection."""
    try:
        test_model = model or "gemini-pro"

        async with httpx.AsyncClient(timeout=timeout) as client:
            completion_data = {
                "contents": [{"parts": [{"text": "Hi"}]}],
                "generationConfig": {"maxOutputTokens": 1},
            }

            response = await client.post(
                f"{base_url}/models/{test_model}:generateContent?key={api_key}",
                json=completion_data,
            )

            if response.status_code == 200:
                return ConnectionTestResult(
                    success=True, provider="gemini", model=test_model
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    provider="gemini",
                    error=f"API test failed: {response.status_code}",
                )

    except Exception as e:
        return ConnectionTestResult(
            success=False, provider="gemini", error=f"Connection failed: {e}"
        )


async def _test_ollama_connection(
    base_url: str, api_key: str, model: Optional[str] = None, timeout: int = 30
) -> ConnectionTestResult:
    """Test Ollama API connection."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # First check if Ollama is running
            health_response = await client.get(
                f"{base_url.replace('/v1', '')}/api/tags"
            )

            if health_response.status_code == 200:
                models_data = health_response.json()
                available_models = [m["name"] for m in models_data.get("models", [])]

                if available_models:
                    test_model = model or available_models[0]

                    # Test with a simple generation
                    completion_data = {
                        "model": test_model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "stream": False,
                    }

                    headers = {}
                    if api_key and api_key != "ollama":  # ollama might not need auth
                        headers["Authorization"] = f"Bearer {api_key}"

                    completion_response = await client.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json=completion_data,
                    )

                    if completion_response.status_code == 200:
                        return ConnectionTestResult(
                            success=True,
                            provider="ollama",
                            model=test_model,
                            available_models=available_models,
                        )
                    else:
                        return ConnectionTestResult(
                            success=False,
                            provider="ollama",
                            error=f"Generation test failed: {completion_response.status_code}",
                        )
                else:
                    return ConnectionTestResult(
                        success=False,
                        provider="ollama",
                        error="No models available in Ollama",
                    )
            else:
                return ConnectionTestResult(
                    success=False,
                    provider="ollama",
                    error="Ollama service not responding",
                )

    except Exception as e:
        return ConnectionTestResult(
            success=False, provider="ollama", error=f"Connection failed: {e}"
        )


async def _test_openai_compatible_connection(
    base_url: str, api_key: str, model: Optional[str] = None, timeout: int = 30
) -> ConnectionTestResult:
    """Test OpenAI-compatible API connection."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            # Try to list models first
            try:
                models_response = await client.get(
                    f"{base_url}/models", headers=headers
                )

                available_models = []
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    available_models = [m["id"] for m in models_data.get("data", [])]
            except:
                # Some providers might not support model listing
                available_models = []

            # Test with a simple completion
            test_model = model or (
                available_models[0] if available_models else "gpt-3.5-turbo"
            )

            completion_data = {
                "model": test_model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1,
            }

            completion_response = await client.post(
                f"{base_url}/chat/completions", headers=headers, json=completion_data
            )

            if completion_response.status_code == 200:
                return ConnectionTestResult(
                    success=True,
                    provider="openai-compatible",
                    model=test_model,
                    available_models=available_models if available_models else None,
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    provider="openai-compatible",
                    error=f"API test failed: {completion_response.status_code}",
                )

    except Exception as e:
        return ConnectionTestResult(
            success=False, provider="openai-compatible", error=f"Connection failed: {e}"
        )


async def test_all_configured_providers() -> Dict[str, ConnectionTestResult]:
    """
    Test all configured providers.

    Returns:
        Dictionary mapping provider names to test results.
    """
    from kritrima_ai.config.providers import list_providers

    results = {}

    for provider_id in list_providers():
        api_key = get_api_key(provider_id)
        if api_key:  # Only test providers with API keys
            logger.info(f"Testing connection to {provider_id}...")
            result = await test_provider_connection(provider_id)
            results[provider_id] = result

            if result.success:
                logger.info(f"✓ {provider_id} connection successful")
            else:
                logger.warning(f"✗ {provider_id} connection failed: {result.error}")

    return results


class ConnectionTester:
    """Helper class for testing provider connections."""

    def __init__(self, config):
        self.config = config

    async def test_connection(self) -> ConnectionTestResult:
        """Test connection for the configured provider."""
        return await test_provider_connection(self.config.provider, self.config.model)

    async def test_all_providers(self) -> Dict[str, ConnectionTestResult]:
        """Test all configured providers."""
        return await test_all_configured_providers()
