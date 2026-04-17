# TokenSelect

A plug-and-play platform that helps companies benchmark LLMs, compare quality vs token cost, and choose the best model for each task.

## Features

- **Multi-provider support**: OpenAI, Anthropic, and more
- **Benchmark runner**: Execute prompts across multiple models
- **Metrics tracking**: Cost, latency, tokens, and quality
- **Comparison dashboard**: Visual model comparison
- **Recommendations**: Data-driven model selection

## Quick Start

### Installation

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Python version note:** Python **3.11+** is supported, but Windows installs require prebuilt wheels for heavy dependencies.  
> If you see `Preparing metadata (pyproject.toml) ... error` for `pandas`, switch to Python **3.13** and reinstall (this avoids source builds on unsupported combinations).

### Virtual environment activation

- **PowerShell (Windows)**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Command Prompt (Windows)**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **bash/zsh (Linux/macOS/Git Bash)**
  ```bash
  source .venv/bin/activate
  ```

### Configuration

1. Copy `.env.example` to `.env`
2. Set your API keys:
   ```
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

### Run API Server

```bash
python -m uvicorn src.api.app:app --reload
```

### Run Dashboard

```bash
streamlit run src/dashboard/streamlit_app.py
```

## Architecture

```
src/
├── connectors/     # Provider integrations (OpenAI, Anthropic)
├── benchmarks/     # Benchmark runner
├── metrics/        # Cost, token, latency, quality calculations
├── analytics/      # Comparison and recommendations
├── storage/        # Database models and connections
├── api/            # FastAPI REST API
└── dashboard/      # Streamlit UI
```

## Usage Example

```python
from src.benchmarks import BenchmarkRunner
from src.storage import init_db

# Initialize database
init_db()

# Create runner
runner = BenchmarkRunner(db_session=session)

# Run benchmark
run_id = await runner.run_benchmark(
    benchmark_name="support_qa",
    prompts=[{"prompt_text": "How do I reset my password?"}],
    models=[
        {"provider": "openai", "model_name": "gpt-3.5-turbo"},
        {"provider": "anthropic", "model_name": "claude-3-sonnet-20240229"},
    ],
)
```

## License

MIT
