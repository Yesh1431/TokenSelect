"""Overall scoring and recommendation logic."""

from typing import List, Dict, Any, Optional
from .cost import average_cost_by_model
from .tokens import average_tokens_by_model
from .latency import average_latency_by_model, latency_score
from .quality import average_quality_by_model


def calculate_overall_score(
    model_stats: Dict[str, Any],
    weights: Dict[str, float],
    all_model_stats: List[Dict[str, Any]]
) -> float:
    """
    Calculate overall score for a model.

    overall_score = (quality_weight * quality_score)
                  - (cost_weight * normalized_cost)
                  - (latency_weight * normalized_latency)
                  - (token_weight * normalized_tokens)
    """
    quality_weight = weights.get('quality', 1.0)
    cost_weight = weights.get('cost', 0.5)
    latency_weight = weights.get('latency', 0.3)
    token_weight = weights.get('tokens', 0.2)

    # Get model's metrics
    quality = model_stats.get('avg_quality', 0)
    cost = model_stats.get('avg_cost', 0)
    latency = model_stats.get('avg_latency_ms', 0)
    tokens = model_stats.get('avg_total_tokens', 0)

    # Normalize across all models
    max_cost = max((m.get('avg_cost', 0) for m in all_model_stats), default=1) or 1
    max_latency = max((m.get('avg_latency_ms', 0) for m in all_model_stats), default=1) or 1
    max_tokens = max((m.get('avg_total_tokens', 0) for m in all_model_stats), default=1) or 1

    normalized_cost = cost / max_cost
    normalized_latency = latency / max_latency
    normalized_tokens = tokens / max_tokens

    score = (
        quality_weight * quality
        - cost_weight * normalized_cost
        - latency_weight * normalized_latency
        - token_weight * normalized_tokens
    )

    return round(score, 4)


def recommend_best_model(
    requests: List[Dict[str, Any]],
    task_type: str = 'general',
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Recommend the best model based on benchmark results.

    Returns recommendation with model, reason, and scores.
    """
    if not weights:
        weights = {
            'quality': 1.0,
            'cost': 0.5,
            'latency': 0.3,
            'tokens': 0.2,
        }

    # Aggregate stats by model
    model_stats = _aggregate_model_stats(requests)

    if not model_stats:
        return {'error': 'No requests to analyze'}

    # Calculate overall scores
    all_stats_list = list(model_stats.values())
    for model_id, stats in model_stats.items():
        stats['overall_score'] = calculate_overall_score(
            stats, weights, all_stats_list
        )

    # Find best by category
    best_quality = max(model_stats.items(), key=lambda x: x[1].get('avg_quality', 0))
    best_cost = min(model_stats.items(), key=lambda x: x[1].get('avg_cost', float('inf')))
    best_latency = min(model_stats.items(), key=lambda x: x[1].get('avg_latency_ms', float('inf')))
    best_balanced = max(model_stats.items(), key=lambda x: x[1].get('overall_score', 0))

    return {
        'task_type': task_type,
        'recommendations': {
            'best_quality': {
                'model_id': best_quality[0],
                'score': best_quality[1].get('avg_quality', 0),
                'reason': f"Highest quality score ({best_quality[1].get('avg_quality', 0):.4f})",
            },
            'best_cost': {
                'model_id': best_cost[0],
                'score': best_cost[1].get('avg_cost', 0),
                'reason': f"Lowest average cost (${best_cost[1].get('avg_cost', 0):.6f})",
            },
            'best_speed': {
                'model_id': best_latency[0],
                'score': best_latency[1].get('avg_latency_ms', 0),
                'reason': f"Fastest average latency ({best_latency[1].get('avg_latency_ms', 0):.2f}ms)",
            },
            'best_balanced': {
                'model_id': best_balanced[0],
                'score': best_balanced[1].get('overall_score', 0),
                'reason': f"Best overall balance (score: {best_balanced[1].get('overall_score', 0):.4f})",
            },
        },
        'all_models': model_stats,
    }


def _aggregate_model_stats(requests: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Aggregate request-level stats by model."""
    model_data: Dict[str, List[Dict[str, Any]]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        if model_id not in model_data:
            model_data[model_id] = []
        model_data[model_id].append(req)

    result = {}
    for model_id, model_requests in model_data.items():
        valid_requests = [r for r in model_requests if r.get('status') == 'success']

        if not valid_requests:
            continue

        quality_scores = [r.get('quality_score') for r in valid_requests if r.get('quality_score') is not None]
        costs = [r.get('cost', 0) for r in valid_requests]
        latencies = [r.get('latency_ms', 0) for r in valid_requests]
        tokens = [r.get('total_tokens', 0) for r in valid_requests]

        result[model_id] = {
            'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'avg_cost': sum(costs) / len(costs),
            'avg_latency_ms': sum(latencies) / len(latencies),
            'avg_total_tokens': sum(tokens) / len(tokens),
            'request_count': len(valid_requests),
        }

    return result
