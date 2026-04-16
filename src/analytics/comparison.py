"""Model comparison analytics."""

from typing import List, Dict, Any
import pandas as pd


def create_comparison_table(requests: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a comparison DataFrame from benchmark requests."""
    df = pd.DataFrame(requests)

    if df.empty:
        return df

    # Filter successful requests
    df_success = df[df['status'] == 'success']

    # Group by model
    comparison = df_success.groupby('model_id').agg({
        'input_tokens': 'mean',
        'output_tokens': 'mean',
        'total_tokens': 'mean',
        'latency_ms': 'mean',
        'cost': 'mean',
        'quality_score': 'mean',
        'request_id': 'count'
    }).rename(columns={'request_id': 'request_count'})

    return comparison.round(4)


def generate_comparison_report(
    requests: List[Dict[str, Any]],
    models: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate a full comparison report."""
    if not requests:
        return {'error': 'No requests to analyze'}

    df = create_comparison_table(requests)

    if df.empty:
        return {'error': 'No successful requests'}

    # Best by category
    best_quality = df['quality_score'].idxmax() if 'quality_score' in df.columns else None
    best_cost = df['cost'].idxmin()
    best_latency = df['latency_ms'].idxmin()
    best_tokens = df['total_tokens'].idxmin()

    return {
        'summary': {
            'total_requests': len(requests),
            'successful_requests': len(df),
            'models_tested': len(df),
        },
        'best_by_category': {
            'quality': best_quality,
            'cost': best_cost,
            'latency': best_latency,
            'token_efficiency': best_tokens,
        },
        'comparison_table': df.to_dict('index'),
        'models_info': models,
    }
