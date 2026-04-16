"""Anthropic provider connector."""

import time
from typing import Optional, Dict, Any
import anthropic
from .base import BaseConnector, ModelResponse


class AnthropicConnector(BaseConnector):
    """Connector for Anthropic models."""

    @property
    def provider_name(self) -> str:
        return 'anthropic'

    def __init__(self, api_key: Optional[str] = None):
        import os
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        model: str = 'claude-3-sonnet-20240229',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate response using Anthropic API."""
        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                messages=[{'role': 'user', 'content': prompt}],
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000

            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            total_tokens = input_tokens + output_tokens

            return ModelResponse(
                response_text=response.content[0].text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                model_name=model,
                provider=self.provider_name,
                status='success',
                raw_response={'id': response.id, 'type': response.type},
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ModelResponse(
                response_text='',
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                model_name=model,
                provider=self.provider_name,
                status='error',
                error_message=str(e),
            )
