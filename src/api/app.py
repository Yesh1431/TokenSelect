"""FastAPI application for TokenSelect."""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from ..storage import init_db, db, Model, Prompt, BenchmarkRun, ModelRequest, Recommendation
from ..benchmarks import BenchmarkRunner
from ..analytics import generate_comparison_report
from ..metrics import recommend_best_model


app = FastAPI(
    title="TokenSelect",
    description="Plug-and-play LLM model evaluation and routing platform",
    version="0.1.0"
)


class ModelConfig(BaseModel):
    model_id: str
    provider: str
    model_name: str
    pricing_input_per_1k: float = 0
    pricing_output_per_1k: float = 0


class PromptInput(BaseModel):
    prompt_text: str
    task_type: str = 'general'
    expected_output: Optional[str] = None


class BenchmarkRequest(BaseModel):
    name: str
    prompts: List[PromptInput]
    models: List[ModelConfig]
    task_type: str = 'general'


class RecommendationRequest(BaseModel):
    run_id: str
    weights: Optional[Dict[str, float]] = None


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    return {"message": "TokenSelect API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/benchmark/run")
async def run_benchmark(benchmark: BenchmarkRequest):
    """Run a benchmark with provided prompts and models."""
    session = db.get_session()

    try:
        runner = BenchmarkRunner(db_session=session)

        prompts_data = [
            {
                'prompt_id': str(uuid.uuid4()),
                'prompt_text': p.prompt_text,
                'task_type': p.task_type,
            }
            for p in benchmark.prompts
        ]

        models_data = [m.model_dump() for m in benchmark.models]

        run_id = await runner.run_benchmark(
            benchmark_name=benchmark.name,
            prompts=prompts_data,
            models=models_data,
            task_type=benchmark.task_type,
        )

        return {
            "run_id": run_id,
            "status": "completed",
            "prompts_count": len(benchmark.prompts),
            "models_count": len(benchmark.models),
        }
    finally:
        session.close()


@app.get("/benchmark/{run_id}")
async def get_benchmark_results(run_id: str):
    """Get results for a benchmark run."""
    session = db.get_session()

    try:
        runner = BenchmarkRunner(db_session=session)
        results = runner.get_results(run_id)

        if not results:
            raise HTTPException(status_code=404, detail="Benchmark run not found")

        return {"run_id": run_id, "results": results}
    finally:
        session.close()


@app.post("/recommend")
async def get_recommendation(rec: RecommendationRequest):
    """Get model recommendation based on benchmark results."""
    session = db.get_session()

    try:
        requests = (
            session.query(ModelRequest)
            .filter(ModelRequest.run_id == rec.run_id)
            .all()
        )

        if not requests:
            raise HTTPException(status_code=404, detail="No requests found for run_id")

        requests_data = [
            {
                'model_id': r.model_id,
                'input_tokens': r.input_tokens,
                'output_tokens': r.output_tokens,
                'total_tokens': r.total_tokens,
                'latency_ms': r.latency_ms,
                'cost': r.cost,
                'status': r.status,
                'quality_score': r.quality_score,
            }
            for r in requests
        ]

        recommendation = recommend_best_model(
            requests_data,
            weights=rec.weights
        )

        return recommendation
    finally:
        session.close()


@app.get("/models")
async def list_models():
    """List all registered models."""
    session = db.get_session()

    try:
        models = session.query(Model).all()
        return {
            "models": [
                {
                    'model_id': m.model_id,
                    'provider': m.provider,
                    'model_name': m.model_name,
                    'active': m.active_flag,
                }
                for m in models
            ]
        }
    finally:
        session.close()


@app.post("/models")
async def register_model(model: ModelConfig):
    """Register a new model."""
    session = db.get_session()

    try:
        db_model = Model(
            model_id=model.model_id,
            provider=model.provider,
            model_name=model.model_name,
            pricing_input_per_1k=model.pricing_input_per_1k,
            pricing_output_per_1k=model.pricing_output_per_1k,
        )
        session.add(db_model)
        session.commit()

        return {"message": "Model registered", "model_id": model.model_id}
    finally:
        session.close()
