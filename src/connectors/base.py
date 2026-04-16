"""Base connector interface for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ModelResponse:
    """Normalized response from any LLM provider."""
    response_text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    model_name: str
    provider: str
    status: str = 'success'
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'response_text': self.response_text,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'latency_ms': self.latency_ms,
            'model_name': self.model_name,
            'provider': self.provider,
            'status': self.status,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class BaseConnector(ABC):
    """Abstract base class for all LLM provider connectors."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a response from the model.

        Args:
            prompt: The input prompt text
            model: The model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific arguments

        Returns:
            ModelResponse with normalized data
        """
        pass

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        pricing_input_per_1k: float,
        pricing_output_per_1k: float
    ) -> float:
        """Calculate cost based on token usage and pricing."""
        input_cost = (input_tokens / 1000) * pricing_input_per_1k
        output_cost = (output_tokens / 1000) * pricing_output_per_1k
        return input_cost + output_cost

    def normalize_model_name(self, model: str) -> str:
        """Normalize model name for consistent tracking."""
        return model
