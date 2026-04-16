"""Streamlit dashboard for TokenSelect."""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(
    page_title="TokenSelect Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("TokenSelect - Model Evaluation Dashboard")


@st.cache_resource
def get_db_engine():
    return create_engine("sqlite:///./tokenselect.db")


def load_benchmark_runs():
    engine = get_db_engine()
    query = "SELECT * FROM benchmark_runs ORDER BY created_at DESC"
    return pd.read_sql_query(query, engine)


def load_benchmark_results(run_id):
    engine = get_db_engine()
    query = f"SELECT * FROM model_requests WHERE run_id = '{run_id}'"
    return pd.read_sql_query(query, engine)


def load_models():
    engine = get_db_engine()
    query = "SELECT * FROM models"
    return pd.read_sql_query(query, engine)


# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["Overview", "Benchmark Results", "Model Comparison", "Registered Models"]
)

# Load data
try:
    benchmark_runs = load_benchmark_runs()
    models_df = load_models()
except Exception as e:
    st.warning(f"Could not load data: {e}")
    benchmark_runs = pd.DataFrame()
    models_df = pd.DataFrame()

# Overview Page
if page == "Overview":
    st.header("Benchmark Overview")

    if not benchmark_runs.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Benchmarks", len(benchmark_runs))
        col2.metric("Completed", len(benchmark_runs[benchmark_runs['status'] == 'completed']))
        col3.metric("Models Registered", len(models_df))

        st.subheader("Recent Benchmarks")
        st.dataframe(
            benchmark_runs[['benchmark_name', 'task_type', 'status', 'created_at']],
            use_container_width=True
        )
    else:
        st.info("No benchmark runs yet. Run a benchmark to see results.")

# Benchmark Results Page
elif page == "Benchmark Results":
    st.header("Benchmark Results")

    if not benchmark_runs.empty:
        selected_run = st.selectbox(
            "Select Benchmark Run",
            benchmark_runs['run_id'].tolist(),
            format_func=lambda x: benchmark_runs[benchmark_runs['run_id'] == x]['benchmark_name'].iloc[0]
        )

        if selected_run:
            results = load_benchmark_results(selected_run)

            if not results.empty:
                # Summary stats
                success_results = results[results['status'] == 'success']

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Requests", len(results))
                col2.metric("Successful", len(success_results))
                col3.metric("Avg Cost", f"${success_results['cost'].mean():.6f}")
                col4.metric("Avg Latency", f"{success_results['latency_ms'].mean():.2f}ms")

                # Results table
                st.subheader("Detailed Results")
                display_cols = ['model_id', 'input_tokens', 'output_tokens', 'latency_ms', 'cost', 'status']
                st.dataframe(results[display_cols], use_container_width=True)

                # Charts
                col1, col2 = st.columns(2)

                with col1:
                    fig_cost = px.bar(
                        success_results.groupby('model_id')['cost'].mean().reset_index(),
                        x='model_id', y='cost',
                        title="Average Cost by Model"
                    )
                    st.plotly_chart(fig_cost, use_container_width=True)

                with col2:
                    fig_latency = px.bar(
                        success_results.groupby('model_id')['latency_ms'].mean().reset_index(),
                        x='model_id', y='latency_ms',
                        title="Average Latency by Model"
                    )
                    st.plotly_chart(fig_latency, use_container_width=True)

                # Token usage
                fig_tokens = px.bar(
                    success_results.groupby('model_id')[['input_tokens', 'output_tokens']].mean().reset_index(),
                    x='model_id', y=['input_tokens', 'output_tokens'],
                    title="Average Token Usage by Model",
                    barmode='group'
                )
                st.plotly_chart(fig_tokens, use_container_width=True)
    else:
        st.info("No benchmark runs available.")

# Model Comparison Page
elif page == "Model Comparison":
    st.header("Model Comparison")

    if not benchmark_runs.empty:
        selected_run = st.selectbox(
            "Select Benchmark Run",
            benchmark_runs['run_id'].tolist(),
            format_func=lambda x: benchmark_runs[benchmark_runs['run_id'] == x]['benchmark_name'].iloc[0]
        )

        if selected_run:
            results = load_benchmark_results(selected_run)
            success_results = results[results['status'] == 'success']

            if not success_results.empty:
                # Aggregated comparison
                comparison = success_results.groupby('model_id').agg({
                    'cost': 'mean',
                    'latency_ms': 'mean',
                    'total_tokens': 'mean',
                    'quality_score': 'mean',
                }).round(4)

                st.subheader("Comparison Table")
                st.dataframe(comparison, use_container_width=True)

                # Cost vs Quality scatter
                if 'quality_score' in comparison.columns and comparison['quality_score'].notna().any():
                    fig = px.scatter(
                        comparison.reset_index(),
                        x='cost', y='quality_score',
                        size='total_tokens', color='model_id',
                        title="Cost vs Quality (size = tokens)",
                        labels={'cost': 'Average Cost ($)', 'quality_score': 'Quality Score'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Quality scores not available. Add quality_score to see comparison.")
    else:
        st.info("No benchmark runs available for comparison.")

# Registered Models Page
elif page == "Registered Models":
    st.header("Registered Models")

    if not models_df.empty:
        st.dataframe(
            models_df[['model_id', 'provider', 'model_name', 'model_family', 'active_flag']],
            use_container_width=True
        )

        st.subheader("Pricing")
        pricing_df = models_df[['model_id', 'pricing_input_per_1k', 'pricing_output_per_1k']].copy()
        pricing_df.columns = ['Model ID', 'Input ($/1K)', 'Output ($/1K)']
        st.dataframe(pricing_df, use_container_width=True)
    else:
        st.info("No models registered yet.")
