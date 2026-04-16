"""Latency metrics."""

from typing import List, Dict, Any
import statistics


def average_latency_by_model(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate average latency per model in milliseconds."""
    model_latencies: Dict[str, List[float]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        latency = req.get('latency_ms', 0)

        if model_id not in model_latencies:
            model_latencies[model_id] = []
        model_latencies[model_id].append(latency)

    return {
        model_id: round(statistics.mean(latencies), 2)
        for model_id, latencies in model_latencies.items()
    }


def p95_latency_by_model(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate P95 latency per model."""
    model_latencies: Dict[str, List[float]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        latency = req.get('latency_ms', 0)

        if model_id not in model_latencies:
            model_latencies[model_id] = []
        model_latencies[model_id].append(latency)

    result = {}
    for model_id, latencies in model_latencies.items():
        if len(latencies) >= 2:
            sorted_latencies = sorted(latencies)
            p95_index = int(len(sorted_latencies) * 0.95)
            result[model_id] = round(sorted_latencies[min(p95_index, len(sorted_latencies) - 1)], 2)
        else:
            result[model_id] = round(statistics.mean(latencies), 2)

    return result


def latency_score(latency_ms: float, max_acceptable_ms: float = 5000) -> float:
    """
    Calculate latency score (0-1).

    1.0 = instant, 0.0 = at or above max acceptable
    """
    if latency_ms <= 0:
        return 0
    score = 1 - (latency_ms / max_acceptable_ms)
    return round(max(0, min(1, score)), 4)
