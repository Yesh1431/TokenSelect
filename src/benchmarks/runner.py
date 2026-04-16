"""Benchmark runner for executing prompts across multiple models."""

import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..connectors import ConnectorFactory, ModelResponse
from ..storage import db, Model, Prompt, BenchmarkRun, ModelRequest


class BenchmarkRunner:
    """Runs benchmarks across multiple models and stores results."""

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.connectors: Dict[str, Any] = {}

    def _get_connector(self, provider: str):
        """Get or create connector for provider."""
        if provider not in self.connectors:
            self.connectors[provider] = ConnectorFactory.get_connector(provider)
        return self.connectors[provider]

    async def run_single_prompt(
        self,
        prompt: str,
        model_config: Dict[str, Any],
        run_id: str,
        prompt_id: str,
    ) -> ModelResponse:
        """Run a single prompt against a model."""
        provider = model_config['provider']
        model_name = model_config['model_name']
        model_id = model_config['model_id']

        connector = self._get_connector(provider)

        response = await connector.generate(
            prompt=prompt,
            model=model_name,
        )

        # Calculate cost if pricing available
        if response.status == 'success':
            pricing_input = model_config.get('pricing_input_per_1k', 0)
            pricing_output = model_config.get('pricing_output_per_1k', 0)
            cost = connector.calculate_cost(
                response.input_tokens,
                response.output_tokens,
                pricing_input,
                pricing_output
            )
        else:
            cost = 0

        # Store result
        if self.db_session:
            request = ModelRequest(
                request_id=str(uuid.uuid4()),
                run_id=run_id,
                prompt_id=prompt_id,
                model_id=model_id,
                task_type=model_config.get('task_type', 'general'),
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                total_tokens=response.total_tokens,
                latency_ms=response.latency_ms,
                cost=cost,
                response_text=response.response_text,
                status=response.status,
                error_message=response.error_message,
            )
            self.db_session.add(request)
            self.db_session.commit()

        return response

    async def run_benchmark(
        self,
        benchmark_name: str,
        prompts: List[Dict[str, str]],
        models: List[Dict[str, Any]],
        task_type: str = 'general',
        created_by: str = 'system',
    ) -> str:
        """
        Run a benchmark with multiple prompts across multiple models.

        Args:
            benchmark_name: Name for this benchmark run
            prompts: List of prompt dicts with 'prompt_id', 'prompt_text', 'task_type'
            models: List of model config dicts
            task_type: Type of task being benchmarked
            created_by: User identifier

        Returns:
            run_id for the benchmark
        """
        run_id = str(uuid.uuid4())

        if self.db_session:
            benchmark_run = BenchmarkRun(
                run_id=run_id,
                benchmark_name=benchmark_name,
                task_type=task_type,
                created_by=created_by,
                status='running',
            )
            self.db_session.add(benchmark_run)
            self.db_session.commit()

        # Create tasks for all prompt/model combinations
        tasks = []
        for prompt_data in prompts:
            prompt_id = prompt_data.get('prompt_id', str(uuid.uuid4()))
            prompt_text = prompt_data['prompt_text']

            # Store prompt if db available
            if self.db_session:
                prompt = Prompt(
                    prompt_id=prompt_id,
                    prompt_name=f"{benchmark_name}_{prompt_id[:8]}",
                    task_type=task_type,
                    prompt_text=prompt_text,
                )
                self.db_session.add(prompt)
                self.db_session.commit()

            for model_config in models:
                task = self.run_single_prompt(
                    prompt=prompt_text,
                    model_config=model_config,
                    run_id=run_id,
                    prompt_id=prompt_id,
                )
                tasks.append(task)

        # Run all tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

        # Mark benchmark as complete
        if self.db_session:
            benchmark_run.status = 'completed'
            self.db_session.commit()

        return run_id

    def get_results(self, run_id: str) -> List[Dict[str, Any]]:
        """Get results for a benchmark run."""
        if not self.db_session:
            return []

        results = (
            self.db_session.query(ModelRequest)
            .filter(ModelRequest.run_id == run_id)
            .all()
        )

        return [
            {
                'request_id': r.request_id,
                'model_id': r.model_id,
                'input_tokens': r.input_tokens,
                'output_tokens': r.output_tokens,
                'total_tokens': r.total_tokens,
                'latency_ms': r.latency_ms,
                'cost': r.cost,
                'status': r.status,
                'quality_score': r.quality_score,
                'response_text': r.response_text,
            }
            for r in results
        ]
