# TokenSelect Interactive UI Product Enhancement Spec

## 1. Objective

Enhance TokenSelect from a model benchmarking concept into an interactive end product where users can register any model endpoint, select one or more models, run controlled test cases, and view token utilization, latency, cost, quality, and agent-level behavior through a clean UI.

The product should not be limited to OpenAI, Claude, or any specific vendor SDK. It should work with any model provider that exposes an HTTP endpoint, including providers such as Kimi, OpenAI-compatible APIs, self-hosted models, internal gateways, or custom enterprise endpoints.

---

## 2. Product Goal

TokenSelect should become a provider-agnostic model analytics and routing intelligence platform.

The user should be able to:

1. Add any model endpoint through the UI.
2. Select the model provider and endpoint configuration.
3. Run predefined context test cases.
4. Run the same prompt through multiple models.
5. Track token usage across model calls and agent workflows.
6. Compare models by cost, latency, token efficiency, output quality, and reliability.
7. View interactive charts and recommendation summaries.
8. Decide which model is best for a specific workload or agent task.

---

## 3. Core Enhancement Summary

Current direction:

- Model benchmarking and comparison platform.
- Token, latency, quality, and cost tracking.
- Recommendation logic.

Enhanced direction:

- Interactive UI product.
- Endpoint-driven model registration.
- Any-model testing instead of only OpenAI or Claude SDK usage.
- Context-case based evaluation.
- Agent-level token observability.
- Model-specific pages with drill-down metrics.
- Reusable testing framework for models like Kimi, Gemini, Mistral, Llama, internal APIs, and OpenAI-compatible endpoints.

---

## 4. Key Product Principle

Do not hardcode providers.

Instead of building separate logic like:

```text
openai_api_key = ...
claude_api_key = ...
```

Build a generic model endpoint configuration layer:

```text
model_name
provider_name
endpoint_url
auth_type
api_key
request_format
response_mapping
token_mapping
pricing_config
context_window
active_flag
```

This allows TokenSelect to analyze any model as long as it can send a request and normalize the response.

---

## 5. Target User Experience

### Step 1: Add Model Endpoint

User opens the UI and adds a model configuration.

Fields:

- Provider Name: `Kimi`, `OpenAI-Compatible`, `Internal Gateway`, `Self Hosted`, etc.
- Model Display Name: `kimi-k2`, `gpt-4.1`, `llama-3.1-70b`, etc.
- Endpoint URL: model inference endpoint.
- HTTP Method: POST by default.
- Auth Type: API Key, Bearer Token, Basic Auth, No Auth.
- API Key / Token: stored securely through environment variables or local encrypted config.
- Request Format: OpenAI-compatible, Anthropic-compatible, custom JSON.
- Response Mapping: where the response text and usage metrics are located.
- Pricing: input token price and output token price.
- Context Window: model max context length.
- Timeout: request timeout.
- Retry Count: retry attempts for transient failures.

---

### Step 2: Select Model or Compare Models

User selects:

- one model for detailed analysis, or
- multiple models for side-by-side comparison.

UI should support filters:

- provider
- model family
- active models
- task type
- context window
- price range
- average latency
- quality score

---

### Step 3: Select Context Test Cases

User chooses test cases from built-in templates or uploads custom cases.

Built-in test case categories:

1. Short Q&A
2. Long-context summarization
3. Information extraction
4. JSON generation
5. Code generation
6. Multi-step reasoning
7. Agent tool-use simulation
8. RAG-style context answer
9. Customer support response
10. Hallucination-resistance test

Each test case should include:

```yaml
case_id: support_case_001
task_type: customer_support
prompt: "Answer the customer based only on the policy text."
context: "<long context here>"
expected_behavior: "Should answer only from context."
expected_output: optional
rubric:
  correctness: 40
  completeness: 20
  format_following: 20
  conciseness: 10
  safety: 10
```

---

### Step 4: Run Benchmark

When the user clicks `Run Benchmark`, TokenSelect should:

1. Load selected models.
2. Load selected test cases.
3. Send the same case to each model endpoint.
4. Capture raw request and response metadata.
5. Normalize response text.
6. Extract usage metrics when available.
7. Estimate token usage when the endpoint does not return usage.
8. Calculate latency, cost, quality, and reliability.
9. Store all run results.
10. Update the dashboard.

---

### Step 5: View Interactive Results

The UI should show:

- overall model ranking
- tokens by model
- input tokens vs output tokens
- cost by model
- latency by model
- quality score by model
- error rate by model
- context utilization percentage
- cost per successful answer
- tokens per quality point
- best model by task type
- best model by agent step

---

## 6. Recommended UI Pages

## Page 1: Home / Executive Summary

Purpose: Give a high-level product view.

Components:

- Total models configured
- Total benchmark runs
- Total test cases executed
- Total tokens consumed
- Total estimated cost
- Best balanced model
- Cheapest model
- Fastest model
- Highest quality model

Charts:

- Model score leaderboard
- Cost vs quality scatter plot
- Latency vs quality scatter plot
- Token usage by provider

---

## Page 2: Model Registry

Purpose: Register and manage any model endpoint.

Features:

- Add model endpoint
- Edit endpoint
- Deactivate endpoint
- Test connection
- View endpoint health
- View latest successful run

Model configuration example:

```yaml
model_id: kimi_k2
provider: kimi
model_name: kimi-k2
endpoint_url: ${KIMI_ENDPOINT_URL}
auth_type: bearer_token
auth_env_var: KIMI_API_KEY
request_format: openai_compatible
response_text_path: choices[0].message.content
usage_input_tokens_path: usage.prompt_tokens
usage_output_tokens_path: usage.completion_tokens
usage_total_tokens_path: usage.total_tokens
pricing:
  input_per_1m_tokens: 0.15
  output_per_1m_tokens: 2.50
context_window: 128000
timeout_seconds: 60
retry_count: 2
active: true
```

Important: Pricing values should be configurable and user-maintained because provider pricing can change.

---

## Page 3: Test Case Library

Purpose: Manage context cases used to evaluate models.

Features:

- Create test case
- Upload CSV / JSON / YAML test cases
- Tag by task type
- Add expected answer
- Add scoring rubric
- Add long context payload
- Version test cases

Example test case schema:

```yaml
case_id: rag_policy_001
task_type: rag_answering
difficulty: medium
prompt: "Using only the provided policy context, answer the user question."
context: "Policy text goes here."
user_question: "Can I cancel after 30 days?"
expected_output: "The answer should mention the cancellation window based on the policy."
scoring_method: rubric
```

---

## Page 4: Benchmark Runner

Purpose: Let the user execute benchmarks without writing code.

Inputs:

- Benchmark name
- Model selection
- Test case selection
- Max output tokens
- Temperature
- Top P
- Timeout
- Number of repetitions
- Scoring method

Buttons:

- Run benchmark
- Run connection test only
- Save benchmark template
- Export results

Execution status should show:

- queued
- running
- completed
- failed
- partially completed

---

## Page 5: Model Metrics Dashboard

Purpose: Show metrics based on selected model.

When the user selects a model, the page should update all metrics for that model.

Metrics:

- total runs
- success rate
- failure rate
- average latency
- p50 latency
- p95 latency
- average input tokens
- average output tokens
- average total tokens
- average cost
- context window utilization
- average quality score
- tokens per successful response
- cost per successful response
- cost per quality point

Charts:

- Token usage over time
- Input vs output tokens
- Cost trend
- Latency trend
- Quality trend
- Errors by test case
- Context utilization by case

---

## Page 6: Model Comparison Dashboard

Purpose: Compare selected models side by side.

Views:

- leaderboard table
- radar chart by quality, speed, cost, reliability, token efficiency
- cost vs quality chart
- latency vs quality chart
- task-level winner table

Comparison table columns:

```text
model_name
provider
avg_quality_score
avg_latency_ms
avg_input_tokens
avg_output_tokens
avg_total_tokens
avg_cost
success_rate
error_rate
efficiency_score
overall_score
recommendation_label
```

Recommendation labels:

- Best for quality
- Best for cost
- Best for speed
- Best balanced
- Not recommended due to failure rate
- Good for long context
- Good for structured output

---

## Page 7: Agent Token Analytics

Purpose: Track how tokens are used across multi-agent workflows.

This is a key differentiator.

Many applications use multiple agents or steps such as:

1. Planner Agent
2. Retriever Agent
3. Reasoning Agent
4. Tool Execution Agent
5. Summarizer Agent
6. Final Response Agent

TokenSelect should show token usage per agent step.

Agent run schema:

```yaml
agent_run_id: run_001
workflow_name: customer_support_agent
model_id: kimi_k2
steps:
  - step_name: planner_agent
    input_tokens: 1200
    output_tokens: 300
    latency_ms: 1200
    cost: 0.0004
  - step_name: retriever_agent
    input_tokens: 800
    output_tokens: 150
    latency_ms: 900
    cost: 0.0002
  - step_name: final_response_agent
    input_tokens: 2500
    output_tokens: 600
    latency_ms: 1800
    cost: 0.0011
```

Agent analytics should show:

- total tokens by agent
- token share by agent step
- cost by agent step
- latency by agent step
- most expensive agent step
- highest token-consuming step
- redundant context usage
- repeated prompt overhead
- context compression opportunities

Charts:

- stacked bar chart: tokens by agent step
- waterfall chart: cost accumulation across workflow
- heatmap: model vs agent step token usage
- trend: tokens per workflow run

---

## Page 8: Run Details / Trace View

Purpose: Debug every model call and agent step.

For each run, show:

- request ID
- benchmark ID
- model ID
- endpoint used
- request payload
- response payload
- normalized response text
- input tokens
- output tokens
- total tokens
- latency
- status code
- error message
- retry count
- timestamp

This page is important for engineering users who need traceability.

---

## Page 9: Recommendations

Purpose: Convert raw metrics into actionable decisions.

Recommendation examples:

- Use `Model A` for customer support because it has the best quality/cost balance.
- Use `Model B` for summarization because it is 35% cheaper with similar quality.
- Avoid `Model C` for JSON generation because it has high format failure rate.
- Use `Model D` for long-context RAG because context utilization is high and failure rate is low.
- Compress retrieved context before the final agent step because 62% of tokens are being consumed there.

---

## 7. Backend Design

## 7.1 Endpoint-Driven Connector Interface

Create a generic connector instead of provider-specific connectors only.

Suggested interface:

```python
class BaseModelConnector:
    def validate_config(self, model_config: dict) -> bool:
        pass

    def build_request(self, prompt: str, context: str | None, params: dict) -> dict:
        pass

    def call_model(self, model_config: dict, payload: dict) -> dict:
        pass

    def normalize_response(self, raw_response: dict, model_config: dict) -> dict:
        pass
```

The normalized response should always look like:

```json
{
  "response_text": "...",
  "input_tokens": 1000,
  "output_tokens": 300,
  "total_tokens": 1300,
  "finish_reason": "stop",
  "raw_response": {},
  "status": "success",
  "error_message": null
}
```

---

## 7.2 Request Format Strategy

Support these request formats:

1. `openai_compatible`
2. `anthropic_compatible`
3. `custom_json`
4. `raw_http`

For Kimi or any OpenAI-compatible endpoint, the payload can follow this format:

```json
{
  "model": "kimi-k2",
  "messages": [
    {"role": "system", "content": "You are a helpful evaluator."},
    {"role": "user", "content": "<prompt and context>"}
  ],
  "temperature": 0.2,
  "max_tokens": 1000
}
```

Do not assume every endpoint returns token usage. If usage is missing, estimate tokens using a tokenizer fallback.

---

## 7.3 Response Mapping Strategy

Allow users to configure response paths.

Example:

```yaml
response_text_path: choices[0].message.content
usage_input_tokens_path: usage.prompt_tokens
usage_output_tokens_path: usage.completion_tokens
usage_total_tokens_path: usage.total_tokens
```

For custom endpoints, users can map fields manually.

---

## 8. Data Model Enhancements

## Table: model_endpoints

```sql
CREATE TABLE model_endpoints (
    model_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    endpoint_url TEXT NOT NULL,
    auth_type TEXT,
    auth_env_var TEXT,
    request_format TEXT,
    response_text_path TEXT,
    usage_input_tokens_path TEXT,
    usage_output_tokens_path TEXT,
    usage_total_tokens_path TEXT,
    input_price_per_1m_tokens NUMERIC,
    output_price_per_1m_tokens NUMERIC,
    context_window INTEGER,
    timeout_seconds INTEGER,
    retry_count INTEGER,
    active_flag BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Table: context_test_cases

```sql
CREATE TABLE context_test_cases (
    case_id TEXT PRIMARY KEY,
    case_name TEXT,
    task_type TEXT,
    difficulty TEXT,
    prompt TEXT,
    context TEXT,
    expected_output TEXT,
    scoring_method TEXT,
    rubric_json TEXT,
    version TEXT,
    active_flag BOOLEAN,
    created_at TIMESTAMP
);
```

## Table: benchmark_runs

```sql
CREATE TABLE benchmark_runs (
    benchmark_id TEXT PRIMARY KEY,
    benchmark_name TEXT,
    run_status TEXT,
    selected_models_json TEXT,
    selected_cases_json TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by TEXT
);
```

## Table: model_run_results

```sql
CREATE TABLE model_run_results (
    result_id TEXT PRIMARY KEY,
    benchmark_id TEXT,
    case_id TEXT,
    model_id TEXT,
    provider TEXT,
    endpoint_url TEXT,
    response_text TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    estimated_tokens_flag BOOLEAN,
    latency_ms INTEGER,
    cost NUMERIC,
    quality_score NUMERIC,
    status TEXT,
    status_code INTEGER,
    error_message TEXT,
    retry_count INTEGER,
    raw_request_json TEXT,
    raw_response_json TEXT,
    created_at TIMESTAMP
);
```

## Table: agent_step_results

```sql
CREATE TABLE agent_step_results (
    agent_step_result_id TEXT PRIMARY KEY,
    benchmark_id TEXT,
    agent_run_id TEXT,
    workflow_name TEXT,
    case_id TEXT,
    model_id TEXT,
    step_name TEXT,
    step_order INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms INTEGER,
    cost NUMERIC,
    status TEXT,
    created_at TIMESTAMP
);
```

---

## 9. Metrics Engine

Calculate these metrics at model, task, benchmark, and agent-step level.

### Token Metrics

- total input tokens
- total output tokens
- total tokens
- average tokens per request
- max tokens per request
- context utilization percentage
- estimated vs provider-reported tokens

### Cost Metrics

- input token cost
- output token cost
- total cost
- cost per request
- cost per successful response
- cost per quality point

### Latency Metrics

- average latency
- median latency
- p95 latency
- max latency
- latency by task type
- latency by agent step

### Quality Metrics

- average quality score
- rubric score
- exact match score
- JSON validity score
- format-following score
- hallucination penalty

### Reliability Metrics

- success rate
- failure rate
- timeout rate
- retry rate
- invalid response rate

### Agent Metrics

- tokens by agent step
- cost by agent step
- latency by agent step
- most expensive step
- highest-token step
- repeated context overhead
- workflow efficiency score

---

## 10. Scoring Formula

Use configurable scoring.

```text
overall_score =
    (quality_weight * normalized_quality)
  + (reliability_weight * normalized_success_rate)
  - (cost_weight * normalized_cost)
  - (latency_weight * normalized_latency)
  - (token_weight * normalized_tokens)
```

Recommended default weights:

```yaml
quality_weight: 0.40
reliability_weight: 0.20
cost_weight: 0.15
latency_weight: 0.15
token_weight: 0.10
```

For each use case, allow the user to adjust weights.

Example:

- Customer support: prioritize quality and latency.
- Batch summarization: prioritize cost and token efficiency.
- JSON extraction: prioritize format correctness.
- Agent workflow: prioritize total workflow cost and reliability.

---

## 11. Suggested Repository Structure

```text
TokenSelect/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── configs/
│   ├── model_endpoints.yaml
│   ├── scoring.yaml
│   ├── test_cases.yaml
│   └── app_config.yaml
├── data/
│   ├── sample_context_cases/
│   ├── benchmark_outputs/
│   └── exports/
├── src/
│   ├── connectors/
│   │   ├── base.py
│   │   ├── generic_http_connector.py
│   │   ├── openai_compatible_connector.py
│   │   └── response_mapper.py
│   ├── benchmarks/
│   │   ├── runner.py
│   │   └── case_loader.py
│   ├── agents/
│   │   ├── workflow_runner.py
│   │   └── step_tracker.py
│   ├── metrics/
│   │   ├── token_metrics.py
│   │   ├── cost_metrics.py
│   │   ├── latency_metrics.py
│   │   ├── quality_metrics.py
│   │   ├── reliability_metrics.py
│   │   └── scoring.py
│   ├── storage/
│   │   ├── db.py
│   │   ├── schema.py
│   │   └── repository.py
│   ├── api/
│   │   ├── app.py
│   │   ├── routes_models.py
│   │   ├── routes_benchmarks.py
│   │   └── routes_metrics.py
│   ├── dashboard/
│   │   ├── streamlit_app.py
│   │   ├── pages/
│   │   │   ├── 1_home.py
│   │   │   ├── 2_model_registry.py
│   │   │   ├── 3_test_cases.py
│   │   │   ├── 4_benchmark_runner.py
│   │   │   ├── 5_model_metrics.py
│   │   │   ├── 6_model_comparison.py
│   │   │   ├── 7_agent_token_analytics.py
│   │   │   ├── 8_run_trace.py
│   │   │   └── 9_recommendations.py
│   └── utils/
│       ├── config_loader.py
│       ├── token_estimator.py
│       └── json_path.py
├── tests/
│   ├── test_generic_connector.py
│   ├── test_response_mapping.py
│   ├── test_token_metrics.py
│   ├── test_agent_step_metrics.py
│   └── test_benchmark_runner.py
└── docs/
    ├── interactive_model_token_analytics_ui_spec.md
    ├── architecture.md
    ├── schema.md
    └── api_contract.md
```

---

## 12. Build Plan

## Phase 1: Productize the Foundation

Deliverables:

- Create model endpoint schema.
- Create context test case schema.
- Create benchmark result schema.
- Create agent step result schema.
- Add local SQLite or DuckDB storage.

---

## Phase 2: Build Generic Endpoint Connector

Deliverables:

- Generic HTTP connector.
- OpenAI-compatible request builder.
- Custom JSON request builder.
- Response path mapper.
- Token usage extractor.
- Token estimator fallback.

Acceptance criteria:

- User can configure a Kimi-style endpoint without writing custom connector code.
- User can test endpoint connection from the UI.
- User can see normalized response output.

---

## Phase 3: Build Interactive UI Pages

Deliverables:

- Home dashboard.
- Model registry page.
- Test case library page.
- Benchmark runner page.
- Model metrics page.
- Model comparison page.
- Agent token analytics page.
- Run trace page.
- Recommendations page.

Recommended first UI framework:

- Streamlit for fast MVP.

Recommended later production UI:

- React / Next.js frontend with FastAPI backend.

---

## Phase 4: Add Benchmark Execution

Deliverables:

- Select models.
- Select context cases.
- Run benchmark.
- Store results.
- Display progress.
- Export results.

---

## Phase 5: Add Agent Workflow Analytics

Deliverables:

- Define agent workflow schema.
- Capture per-agent step usage.
- Store step-level token, cost, and latency.
- Show agent token breakdown dashboard.
- Recommend context compression or model changes per step.

---

## Phase 6: Add Recommendation Engine

Deliverables:

- Configurable scoring weights.
- Model ranking.
- Task-level winner.
- Agent-step winner.
- Natural language recommendation summary.

---

## 13. Cursor / Copilot Build Prompt

Use this prompt with a coding agent:

```text
Enhance this TokenSelect repository into an interactive provider-agnostic model token analytics product.

Do not hardcode OpenAI or Claude as the only supported providers. Build a generic endpoint-based model registry where users can configure any model endpoint, including OpenAI-compatible endpoints such as Kimi or custom internal HTTP endpoints.

Implement the product with these priorities:

1. Create schemas for model_endpoints, context_test_cases, benchmark_runs, model_run_results, and agent_step_results.
2. Build a generic HTTP connector that can call any configured endpoint.
3. Support request formats: openai_compatible, custom_json, and raw_http.
4. Support response path mapping for response text and usage fields.
5. If token usage is missing from the model response, estimate tokens with a tokenizer fallback.
6. Build a Streamlit UI with pages for Home, Model Registry, Test Case Library, Benchmark Runner, Model Metrics, Model Comparison, Agent Token Analytics, Run Trace, and Recommendations.
7. Allow users to select a model and see metrics update dynamically based on that model.
8. Allow users to select multiple models and compare token usage, cost, latency, quality, success rate, and overall score.
9. Add context test cases for short Q&A, long summarization, extraction, JSON generation, code generation, RAG, and multi-agent workflows.
10. Track token utilization across agent steps such as planner, retriever, reasoning, tool execution, summarizer, and final response.
11. Store every model call with raw request, raw response, normalized response, tokens, latency, cost, status, and error message.
12. Build charts for tokens over time, cost by model, latency by model, quality by model, context utilization, and agent step token breakdown.
13. Build a recommendation engine that recommends best model for quality, cost, latency, balanced score, long context, and agent workflow efficiency.

Keep the first implementation simple and working end to end using Python, FastAPI, Streamlit, pandas, SQLAlchemy, and SQLite or DuckDB. Do not overbuild enterprise features in the first version.
```

---

## 14. MVP Acceptance Criteria

The enhanced product is successful when this demo works:

1. User opens TokenSelect UI.
2. User adds a Kimi or OpenAI-compatible endpoint through Model Registry.
3. User adds or selects context test cases.
4. User runs benchmarks against one or more models.
5. UI displays token usage, latency, cost, quality, and reliability metrics.
6. User selects a model and sees model-specific pages update dynamically.
7. User opens Agent Token Analytics and sees token usage by agent step.
8. User opens Recommendations and sees which model is best for quality, cost, speed, and balanced usage.
9. User can export benchmark results.

---

## 15. Final Product Positioning

TokenSelect should be positioned as:

> An interactive model selection and token analytics platform that helps teams evaluate any LLM endpoint, understand token usage across prompts and agents, and choose the best model for each workload.

One-line version:

> TokenSelect helps teams test any LLM endpoint, compare model performance, and control token cost across agents.
