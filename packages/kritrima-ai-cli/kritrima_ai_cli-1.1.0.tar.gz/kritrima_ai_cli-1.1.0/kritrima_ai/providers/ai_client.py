"""
AI client for communicating with various AI providers.

This module provides a unified interface for communicating with different AI
providers, handling authentication, request formatting, and response parsing.
"""

import json
from typing import Any, AsyncIterator, Dict, List

import httpx

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.config.providers import (
    create_auth_headers,
    get_api_key,
    get_base_url,
    get_provider_info,
)
from kritrima_ai.utils.logger import get_logger, performance_timer

logger = get_logger(__name__)


class AIClient:
    """
    Unified AI client for multiple providers.

    Provides a consistent interface for communicating with various AI providers
    while handling provider-specific differences in authentication, request
    formatting, and response parsing.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize AI client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.provider_id = config.provider
        self.model = config.model

        # Get provider information
        self.provider_info = get_provider_info(self.provider_id)
        if not self.provider_info:
            raise ValueError(f"Unknown provider: {self.provider_id}")

        # Get API key and base URL
        self.api_key = get_api_key(self.provider_id)
        self.base_url = get_base_url(self.provider_id)

        if not self.api_key and self.provider_info.auth_type != "none":
            raise ValueError(f"No API key found for provider {self.provider_id}")

        # Create HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=config.timeout,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

        logger.info(
            f"AI client initialized for {self.provider_id} with model {self.model}"
        )

    async def chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """
        Get chat completion from the AI provider.

        Args:
            messages: List of messages in OpenAI format
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            AI response in OpenAI format
        """
        with performance_timer(f"ai_request_{self.provider_id}", logger):
            # Prepare request based on provider
            if self.provider_id == "openai":
                return await self._openai_chat_completion(messages, stream, **kwargs)
            elif self.provider_id == "anthropic":
                return await self._anthropic_chat_completion(messages, stream, **kwargs)
            elif self.provider_id == "gemini":
                return await self._gemini_chat_completion(messages, stream, **kwargs)
            elif self.provider_id == "ollama":
                return await self._ollama_chat_completion(messages, stream, **kwargs)
            else:
                # Default to OpenAI-compatible API
                return await self._openai_compatible_chat_completion(
                    messages, stream, **kwargs
                )

    async def chat_completion_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream chat completion from the AI provider.

        Args:
            messages: List of messages in OpenAI format
            **kwargs: Additional parameters

        Yields:
            AI response chunks in OpenAI format
        """
        # For streaming, we call the appropriate provider-specific method
        if self.provider_id == "openai":
            async for chunk in self._openai_chat_completion_stream(messages, **kwargs):
                yield chunk
        elif self.provider_id == "anthropic":
            async for chunk in self._anthropic_chat_completion_stream(
                messages, **kwargs
            ):
                yield chunk
        elif self.provider_id == "gemini":
            async for chunk in self._gemini_chat_completion_stream(messages, **kwargs):
                yield chunk
        elif self.provider_id == "ollama":
            async for chunk in self._ollama_chat_completion_stream(messages, **kwargs):
                yield chunk
        else:
            # Default to OpenAI-compatible streaming
            async for chunk in self._openai_compatible_chat_completion_stream(
                messages, **kwargs
            ):
                yield chunk

    # OpenAI provider implementation
    async def _openai_chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """OpenAI chat completion implementation."""
        headers = create_auth_headers(self.provider_id, self.api_key)
        headers["Content-Type"] = "application/json"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        # Add function calling if tools are provided
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
            payload["tool_choice"] = kwargs.get("tool_choice", "auto")

        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"OpenAI API error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"OpenAI request error: {e}")
            raise

    async def _openai_chat_completion_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """OpenAI streaming chat completion implementation."""
        headers = create_auth_headers(self.provider_id, self.api_key)
        headers["Content-Type"] = "application/json"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        try:
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI streaming error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"OpenAI streaming request error: {e}")
            raise

    # Anthropic provider implementation
    async def _anthropic_chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Anthropic chat completion implementation."""
        headers = create_auth_headers(self.provider_id, self.api_key)
        headers["Content-Type"] = "application/json"
        headers["anthropic-version"] = "2023-06-01"

        # Convert OpenAI format to Anthropic format
        anthropic_messages = []
        system_message = None

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens or 4096),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": stream,
        }

        if system_message:
            payload["system"] = system_message

        try:
            response = await self.http_client.post(
                f"{self.base_url}/v1/messages", headers=headers, json=payload
            )
            response.raise_for_status()

            # Convert Anthropic response to OpenAI format
            anthropic_response = response.json()
            return self._convert_anthropic_to_openai(anthropic_response)

        except httpx.HTTPStatusError as e:
            logger.error(f"Anthropic API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Anthropic request error: {e}")
            raise

    async def _anthropic_chat_completion_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Anthropic streaming implementation."""
        # Simplified streaming implementation
        # In a full implementation, this would handle Anthropic's SSE format
        response = await self._anthropic_chat_completion(
            messages, stream=True, **kwargs
        )
        yield response

    # Gemini provider implementation
    async def _gemini_chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Gemini chat completion implementation."""
        # Convert OpenAI format to Gemini format
        contents = []
        for msg in messages:
            if msg["role"] == "user":
                contents.append({"parts": [{"text": msg["content"]}], "role": "user"})
            elif msg["role"] == "assistant":
                contents.append({"parts": [{"text": msg["content"]}], "role": "model"})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "maxOutputTokens": kwargs.get(
                    "max_tokens", self.config.max_tokens or 4096
                ),
            },
        }

        try:
            response = await self.http_client.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                json=payload,
            )
            response.raise_for_status()

            # Convert Gemini response to OpenAI format
            gemini_response = response.json()
            return self._convert_gemini_to_openai(gemini_response)

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Gemini request error: {e}")
            raise

    async def _gemini_chat_completion_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Gemini streaming implementation."""
        # Simplified streaming implementation
        response = await self._gemini_chat_completion(messages, stream=True, **kwargs)
        yield response

    # Ollama provider implementation
    async def _ollama_chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Ollama chat completion implementation."""
        headers = {"Content-Type": "application/json"}

        # Ollama uses OpenAI-compatible format
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
            },
        }

        if self.config.max_tokens:
            payload["options"]["num_predict"] = self.config.max_tokens

        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Ollama request error: {e}")
            raise

    async def _ollama_chat_completion_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Ollama streaming implementation."""
        # Use the OpenAI-compatible streaming for Ollama
        async for chunk in self._openai_compatible_chat_completion_stream(
            messages, **kwargs
        ):
            yield chunk

    # Generic OpenAI-compatible implementation
    async def _openai_compatible_chat_completion(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Generic OpenAI-compatible chat completion."""
        headers = create_auth_headers(self.provider_id, self.api_key)
        headers["Content-Type"] = "application/json"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise

    async def _openai_compatible_chat_completion_stream(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Generic OpenAI-compatible streaming."""
        headers = create_auth_headers(self.provider_id, self.api_key)
        headers["Content-Type"] = "application/json"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        try:
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(f"Streaming API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Streaming request error: {e}")
            raise

    def _convert_anthropic_to_openai(
        self, anthropic_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert Anthropic response format to OpenAI format."""
        content = ""
        if anthropic_response.get("content"):
            content = anthropic_response["content"][0].get("text", "")

        return {
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": anthropic_response.get("usage", {}),
            "model": anthropic_response.get("model", self.model),
        }

    def _convert_gemini_to_openai(
        self, gemini_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert Gemini response format to OpenAI format."""
        content = ""
        if gemini_response.get("candidates"):
            candidate = gemini_response["candidates"][0]
            if candidate.get("content", {}).get("parts"):
                content = candidate["content"]["parts"][0].get("text", "")

        return {
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {},  # Gemini doesn't provide usage info in the same format
            "model": self.model,
        }

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models for the current provider.

        Returns:
            List of model information
        """
        try:
            if self.provider_id == "openai":
                return await self._list_openai_models()
            elif self.provider_id == "ollama":
                return await self._list_ollama_models()
            else:
                # For other providers, return the configured models
                return [{"id": model} for model in self.provider_info.models]

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    async def _list_openai_models(self) -> List[Dict[str, Any]]:
        """List OpenAI models."""
        headers = create_auth_headers(self.provider_id, self.api_key)

        try:
            response = await self.http_client.get(
                f"{self.base_url}/models", headers=headers
            )
            response.raise_for_status()

            data = response.json()
            return data.get("data", [])

        except Exception as e:
            logger.error(f"Error listing OpenAI models: {e}")
            return []

    async def _list_ollama_models(self) -> List[Dict[str, Any]]:
        """List Ollama models."""
        try:
            # Ollama has a different endpoint for listing models
            response = await self.http_client.get(
                f"{self.base_url.replace('/v1', '')}/api/tags"
            )
            response.raise_for_status()

            data = response.json()
            models = data.get("models", [])

            # Convert to OpenAI format
            return [{"id": model["name"]} for model in models]

        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []

    async def cleanup(self) -> None:
        """Clean up HTTP client resources."""
        await self.http_client.aclose()
        logger.debug("AI client cleanup completed")
