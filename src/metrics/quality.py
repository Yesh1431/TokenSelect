"""Quality scoring metrics."""

from typing import List, Dict, Any, Optional
import re


def average_quality_by_model(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate average quality score per model."""
    model_scores: Dict[str, List[float]] = {}

    for req in requests:
        model_id = req.get('model_id', 'unknown')
        score = req.get('quality_score')

        if score is not None:
            if model_id not in model_scores:
                model_scores[model_id] = []
            model_scores[model_id].append(score)

    return {
        model_id: round(sum(scores) / len(scores), 4)
        for model_id, scores in model_scores.items()
        if len(scores) > 0
    }


def calculate_quality_score(
    response_text: str,
    expected_output: Optional[str] = None,
    rubric_scores: Optional[Dict[str, int]] = None
) -> float:
    """
    Calculate quality score for a response.

    For MVP, supports:
    - Expected output comparison (exact/partial match)
    - Rubric-based scoring
    - Basic heuristics (length, structure)
    """
    if not response_text:
        return 0.0

    scores = []

    # Expected output comparison
    if expected_output:
        if response_text.strip().lower() == expected_output.strip().lower():
            scores.append(1.0)
        elif expected_output.lower() in response_text.lower():
            scores.append(0.7)
        else:
            # Basic similarity check
            similarity = _text_similarity(response_text, expected_output)
            scores.append(similarity)

    # Rubric-based scoring
    if rubric_scores:
        rubric_total = sum(rubric_scores.values())
        rubric_max = len(rubric_scores) * 5  # Assuming 5-point scale
        if rubric_max > 0:
            scores.append(rubric_total / rubric_max)

    # Basic heuristics if no other scores
    if not scores:
        # Prefer responses with reasonable length
        length_score = min(1.0, len(response_text) / 100)
        scores.append(length_score * 0.5)  # Weight heuristics lower

    return round(sum(scores) / len(scores), 4) if scores else 0.0


def _text_similarity(text1: str, text2: str) -> float:
    """Simple word overlap similarity."""
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union) if union else 0.0
