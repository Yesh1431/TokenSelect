"""Cost calculation metrics."""

from typing import List, Dict, Any


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    pricing_input_per_1k: float,
    pricing_output_per_1k: float
) -> float:
    """Calculate total cost for a request."""
    input_cost = (input_tokens / 1000) * pricing_input_per_1k
    output_cost = (output_tokens / 1000) * pricing_output_per_1k
    return round(input_cost + output_cost, 6)


def average_cost_by_model(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate average cost per model."""
    model_costs: Dict[str, List[float]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        cost = req.get('cost', 0)

        if model_id not in model_costs:
            model_costs[model_id] = []
        model_costs[model_id].append(cost)

    return {
        model_id: round(sum(costs) / len(costs), 6)
        for model_id, costs in model_costs.items()
    }


def total_cost_by_model(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate total cost per model."""
    model_costs: Dict[str, float] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        cost = req.get('cost', 0)

        model_costs[model_id] = model_costs.get(model_id, 0) + cost

    return {
        model_id: round(total, 6)
        for model_id, total in model_costs.items()
    }
