"""Database models for TokenSelect platform."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Model(Base):
    """LLM model registry."""
    __tablename__ = 'models'

    model_id = Column(String, primary_key=True)
    provider = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    model_family = Column(String)
    active_flag = Column(Boolean, default=True)
    pricing_input_per_1k = Column(Float)
    pricing_output_per_1k = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requests = relationship('ModelRequest', back_populates='model')
    recommendations = relationship('Recommendation', back_populates='model')


class Prompt(Base):
    """Prompt templates and datasets."""
    __tablename__ = 'prompts'

    prompt_id = Column(String, primary_key=True)
    prompt_name = Column(String, nullable=False)
    prompt_version = Column(String, default='1.0')
    task_type = Column(String)
    prompt_text = Column(Text, nullable=False)
    expected_output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    requests = relationship('ModelRequest', back_populates='prompt')


class BenchmarkRun(Base):
    """Benchmark execution runs."""
    __tablename__ = 'benchmark_runs'

    run_id = Column(String, primary_key=True)
    benchmark_name = Column(String, nullable=False)
    task_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    status = Column(String, default='pending')

    requests = relationship('ModelRequest', back_populates='benchmark_run')
    recommendations = relationship('Recommendation', back_populates='benchmark_run')


class ModelRequest(Base):
    """Individual model request/response logs."""
    __tablename__ = 'model_requests'

    request_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey('benchmark_runs.run_id'))
    prompt_id = Column(String, ForeignKey('prompts.prompt_id'))
    model_id = Column(String, ForeignKey('models.model_id'))
    task_type = Column(String)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    latency_ms = Column(Float)
    cost = Column(Float)
    response_text = Column(Text)
    status = Column(String, default='success')
    quality_score = Column(Float)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    benchmark_run = relationship('BenchmarkRun', back_populates='requests')
    prompt = relationship('Prompt', back_populates='requests')
    model = relationship('Model', back_populates='requests')


class Recommendation(Base):
    """Model recommendations based on benchmark results."""
    __tablename__ = 'recommendations'

    recommendation_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey('benchmark_runs.run_id'))
    task_type = Column(String)
    recommended_model_id = Column(String, ForeignKey('models.model_id'))
    recommendation_type = Column(String)  # 'best_quality', 'best_cost', 'best_speed', 'best_balanced'
    reason = Column(Text)
    overall_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    benchmark_run = relationship('BenchmarkRun', back_populates='recommendations')
    model = relationship('Model', back_populates='recommendations')
