"""Tests for connector modules."""

import pytest
from src.connectors import ModelResponse, ConnectorFactory


def test_model_response_creation():
    """Test ModelResponse dataclass."""
    response = ModelResponse(
        response_text="Hello, world!",
        input_tokens=10,
        output_tokens=20,
        total_tokens=30,
        latency_ms=100.5,
        model_name="test-model",
        provider="test-provider",
    )

    assert response.response_text == "Hello, world!"
    assert response.total_tokens == 30
    assert response.status == 'success'


def test_model_response_to_dict():
    """Test ModelResponse conversion to dict."""
    response = ModelResponse(
        response_text="Test response",
        input_tokens=5,
        output_tokens=15,
        total_tokens=20,
        latency_ms=50.0,
        model_name="test",
        provider="test",
    )

    result = response.to_dict()

    assert result['response_text'] == "Test response"
    assert result['total_tokens'] == 20
    assert result['provider'] == 'test'


def test_connector_factory_list_providers():
    """Test listing available providers."""
    providers = ConnectorFactory.list_providers()

    assert 'openai' in providers
    assert 'anthropic' in providers


def test_connector_factory_get_connector():
    """Test getting connector instances."""
    # This will fail without API keys, but tests the factory pattern
    with pytest.raises(ValueError, match="API key"):
        ConnectorFactory.get_connector('openai')

    with pytest.raises(ValueError, match="API key"):
        ConnectorFactory.get_connector('anthropic')


def test_connector_factory_unknown_provider():
    """Test error for unknown provider."""
    with pytest.raises(ValueError, match="Unknown provider"):
        ConnectorFactory.get_connector('unknown_provider')
