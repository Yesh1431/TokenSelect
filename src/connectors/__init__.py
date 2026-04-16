"""Connectors module for LLM providers."""

from .base import BaseConnector, ModelResponse
from .openai_connector import OpenAIConnector
from .anthropic_connector import AnthropicConnector


class ConnectorFactory:
    """Factory for creating provider connectors."""

    _connectors = {
        'openai': OpenAIConnector,
        'anthropic': AnthropicConnector,
    }

    @classmethod
    def register(cls, provider_name: str, connector_class: type):
        """Register a new connector class."""
        cls._connectors[provider_name.lower()] = connector_class

    @classmethod
    def get_connector(cls, provider: str, **kwargs):
        """Get a connector instance for the specified provider."""
        connector_class = cls._connectors.get(provider.lower())
        if not connector_class:
            raise ValueError(f"Unknown provider: {provider}")
        return connector_class(**kwargs)

    @classmethod
    def list_providers(cls) -> list:
        """List available providers."""
        return list(cls._connectors.keys())


__all__ = [
    'BaseConnector',
    'ModelResponse',
    'OpenAIConnector',
    'AnthropicConnector',
    'ConnectorFactory',
]
