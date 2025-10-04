"""
LLM adapter template - suited for OpenAI-compatible providers

Usage: copy this file into tradingagents/llm_adapters/{provider}_adapter.py
and customize provider_name, base_url, API key environment variable, and any provider-specific defaults.
"""

from typing import Any, Dict
import os
import logging

from tradingagents.llm_adapters.openai_compatible_base import OpenAICompatibleBase

logger = logging.getLogger(__name__)


class ChatProviderTemplate(OpenAICompatibleBase):
    """{ProviderDisplayName} OpenAI-compatible adapter"""

    def __init__(
        self,
        model: str = "{default-model-name}",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 120,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the {ProviderDisplayName} OpenAI-compatible client.

        Parameters:
        - model: default model name
        - temperature: sampling temperature
        - max_tokens: model max tokens
        - timeout: request timeout in seconds
        """
        super().__init__(
            provider_name="{provider}",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key_env_var="{PROVIDER_API_KEY}",
            base_url="{https://api.provider.com/v1}",
            request_timeout=timeout,
            **kwargs,
        )
        logger.info("✅ {ProviderDisplayName} OpenAI-compatible adapter initialized successfully")


# Reference for openai_compatible_base.py
PROVIDER_TEMPLATE_MODELS: Dict[str, Dict[str, Any]] = {
    "{default-model-name}": {"context_length": 8192, "supports_function_calling": True},
    "{advanced-model-name}": {"context_length": 32768, "supports_function_calling": True},
}