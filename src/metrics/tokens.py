"""Token usage metrics."""

from typing import List, Dict, Any


def average_tokens_by_model(requests: List[Dict[str, Any]], token_type: str = 'total') -> Dict[str, float]:
    """Calculate average tokens per model."""
    model_tokens: Dict[str, List[int]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')

        if token_type == 'input':
            tokens = req.get('input_tokens', 0)
        elif token_type == 'output':
            tokens = req.get('output_tokens', 0)
        else:
            tokens = req.get('total_tokens', 0)

        if model_id not in model_tokens:
            model_tokens[model_id] = []
        model_tokens[model_id].append(tokens)

    return {
        model_id: round(sum(tokens) / len(tokens), 2)
        for model_id, tokens in model_tokens.items()
    }


def token_efficiency_score(
    output_tokens: int,
    response_quality: float,
    max_tokens: int = 4096
) -> float:
    """
    Calculate token efficiency score.

    Higher score = more output quality per token used.
    """
    if output_tokens == 0:
        return 0

    quality_weighted = response_quality * output_tokens
    max_possible = max_tokens
    return round(quality_weighted / max_possible, 4)


def tokens_per_dollar(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate tokens received per dollar spent by model."""
    model_stats: Dict[str, Dict[str, float]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        cost = req.get('cost', 0)
        tokens = req.get('total_tokens', 0)

        if model_id not in model_stats:
            model_stats[model_id] = {'tokens': 0, 'cost': 0}

        model_stats[model_id]['tokens'] += tokens
        model_stats[model_id]['cost'] += cost

    return {
        model_id: round(stats['tokens'] / stats['cost'], 2) if stats['cost'] > 0 else 0
        for model_id, stats in model_stats.items()
    }
