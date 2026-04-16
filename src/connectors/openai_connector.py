"""OpenAI provider connector."""

import time
from typing import Optional, Dict, Any
import openai
from .base import BaseConnector, ModelResponse


class OpenAIConnector(BaseConnector):
    """Connector for OpenAI models."""

    @property
    def provider_name(self) -> str:
        return 'openai'

    def __init__(self, api_key: Optional[str] = None):
        import os
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        model: str = 'gpt-3.5-turbo',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate response using OpenAI API."""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000

            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            return ModelResponse(
                response_text=response.choices[0].message.content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                model_name=model,
                provider=self.provider_name,
                status='success',
                raw_response={'id': response.id, 'created': response.created},
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
