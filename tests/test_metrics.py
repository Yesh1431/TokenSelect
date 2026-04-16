"""Tests for metrics modules."""

import pytest
from src.metrics import (
    calculate_cost,
    average_cost_by_model,
    average_tokens_by_model,
    average_latency_by_model,
    latency_score,
    calculate_quality_score,
)


class TestCostMetrics:
    def test_calculate_cost(self):
        """Test cost calculation."""
        cost = calculate_cost(
            input_tokens=1000,
            output_tokens=500,
            pricing_input_per_1k=0.001,
            pricing_output_per_1k=0.002
        )
        assert cost == 0.002  # 0.001 + 0.001

    def test_average_cost_by_model(self):
        """Test average cost aggregation."""
        requests = [
            {'model_id': 'model_a', 'cost': 0.01, 'status': 'success'},
            {'model_id': 'model_a', 'cost': 0.02, 'status': 'success'},
            {'model_id': 'model_b', 'cost': 0.03, 'status': 'success'},
        ]

        result = average_cost_by_model(requests)

        assert result['model_a'] == 0.015
        assert result['model_b'] == 0.03


class TestTokenMetrics:
    def test_average_tokens_by_model(self):
        """Test token aggregation."""
        requests = [
            {'model_id': 'model_a', 'total_tokens': 100},
            {'model_id': 'model_a', 'total_tokens': 200},
            {'model_id': 'model_b', 'total_tokens': 150},
        ]

        result = average_tokens_by_model(requests)

        assert result['model_a'] == 150.0
        assert result['model_b'] == 150.0


class TestLatencyMetrics:
    def test_latency_score(self):
        """Test latency scoring."""
        assert latency_score(0) == 0
        assert latency_score(1000, max_acceptable_ms=5000) > 0.5
        assert latency_score(5000, max_acceptable_ms=5000) == 0
        assert latency_score(10000, max_acceptable_ms=5000) == 0

    def test_average_latency_by_model(self):
        """Test latency aggregation."""
        requests = [
            {'model_id': 'model_a', 'latency_ms': 100},
            {'model_id': 'model_a', 'latency_ms': 200},
            {'model_id': 'model_b', 'latency_ms': 150},
        ]

        result = average_latency_by_model(requests)

        assert result['model_a'] == 150.0
        assert result['model_b'] == 150.0


class TestQualityMetrics:
    def test_calculate_quality_score_exact_match(self):
        """Test quality score with exact match."""
        score = calculate_quality_score(
            response_text="Hello world",
            expected_output="Hello world"
        )
        assert score == 1.0

    def test_calculate_quality_score_partial_match(self):
        """Test quality score with partial match."""
        score = calculate_quality_score(
            response_text="Hello world, how are you?",
            expected_output="Hello world"
        )
        assert score >= 0.7

    def test_calculate_quality_score_empty(self):
        """Test quality score with empty response."""
        score = calculate_quality_score(response_text="")
        assert score == 0.0
