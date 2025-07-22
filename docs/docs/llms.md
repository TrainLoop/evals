---
title: "LLM Cheatsheet"
description: "Comprehensive cheatsheet for LLMs to help users implement TrainLoop evaluations"
sidebar_position: 1
---

import CodeBlock from '@theme/CodeBlock';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# LLM Cheatsheet - TrainLoop Evals

<div style={{display: 'flex', gap: '10px', marginBottom: '20px'}}>
  <button 
    className="button button--primary"
    onClick={() => {
      const element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(document.querySelector('.markdown').textContent));
      element.setAttribute('download', 'trainloop-llm-cheatsheet.md');
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }}
  >
    📥 Download Cheatsheet
  </button>
  <button 
    className="button button--secondary"
    onClick={() => {
      navigator.clipboard.writeText(document.querySelector('.markdown').textContent);
      alert('Cheatsheet copied to clipboard!');
    }}
  >
    📋 Copy to Clipboard
  </button>
</div>

This document provides everything an LLM needs to know to help users implement evaluations using TrainLoop's LLM evaluation framework.

## Overview

TrainLoop has created a comprehensive LLM evaluation framework that enables systematic testing, benchmarking, and quality assurance for AI applications. The framework supports Python, TypeScript, and Go applications with minimal code changes.

## Core Workflow: Collect → Evaluate → Compare → Visualize

1. **Collect**: SDKs automatically capture LLM interactions as structured data
2. **Evaluate**: Custom metrics test LLM outputs against specific criteria  
3. **Compare**: Benchmark the same prompts across different LLM providers
4. **Visualize**: Studio UI provides interactive analysis and insights

---

## 1. Setup Phase

### Project Initialization

**Command**: `trainloop init`

**What it creates**:
```
trainloop/                    # Main evaluation directory
├── data/                     # Data storage (git-ignored)
│   ├── events/              # Raw JSONL files of LLM interactions
│   ├── results/             # Evaluation outcomes 
│   ├── benchmarks/          # Provider comparison results
│   ├── judge_traces/        # LLM judge execution logs
│   └── _registry.json       # Instrumentation tracking
├── eval/                    # Your evaluation logic
│   ├── metrics/            # Individual test functions
│   └── suites/             # Collections of related tests
├── trainloop.config.yaml   # Configuration file
└── .venv/                  # Dedicated Python environment
```

**Why this structure matters**:
- **`data/`**: All raw and processed data lives here, git-ignored for privacy (this can also be a path to an S3 or GCS bucket)
- **`eval/`**: Your custom evaluation logic, version controlled
- **Configuration**: Centralized settings for judges, benchmarks, and data paths

---

## 2. SDK Integration & Data Collection

### Multi-Language SDK Setup

#### Python
```python
# At application startup - must happen BEFORE openai/anthropic imports
from trainloop_llm_logging import collect, trainloop_tag

collect("../trainloop/trainloop.config.yaml", flush_immediately=True)

from openai import OpenAI

client = OpenAI()

# Tag requests for targeted evaluation
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a bubble sort function"}],
    extra_headers=trainloop_tag("bubble-sort")  # Tags this request
)
```

#### TypeScript/JavaScript

##### Zero-code-change collection
```bash
# Zero-code-change collection
NODE_OPTIONS="--require=trainloop-llm-logging" npm run dev
```
```typescript
// Tagged requests
import { trainloopTag } from "trainloop-llm-logging";

const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [{ role: "user", content: "Write a bubble sort function" }]
}, {
    headers: { ...trainloopTag("bubble-sort") }  // Tags this request
});
```

##### Explicit collect function
```typescript
// Tagged requests
import { trainloopTag, collect } from "trainloop-llm-logging";

collect(true)

import { OpenAI } from "openai";

const openai = new OpenAI();

const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [{ role: "user", content: "Write a bubble sort function" }]
}, {
    headers: { ...trainloopTag("bubble-sort") }  // Tags this request
});
```

#### Go (experimental)
```go
// At main() startup
import "github.com/trainloop-ai/trainloop-llm-logging-go/trainloop"

func main() {
    trainloop.Collect()  // Auto-instruments HTTP transport
    
    // Tagged requests
    req.Header.Add("X-TrainLoop-Tag", "bubble-sort")
}
```

### Key Integration Concepts

- **Zero-touch instrumentation**: SDKs automatically capture all LLM requests
- **Request tagging**: Use tags to categorize requests for targeted evaluation
- **Automatic storage**: Data flows to `trainloop/data/events/` as JSONL files
- **Multi-provider support**: Works with OpenAI, Anthropic, Google, Cohere, etc.

---

## 3. Evaluation System

### Metrics: The Building Blocks

**Critical Rules for Metrics**:

1. **Function Signature**: Must accept exactly one `Sample` parameter
2. **Return Value**: Must return `int` - either `1` (pass) or `0` (fail)
3. **File Naming**: Function name must match filename
4. **Import Required**: `from trainloop_cli.eval_core.types import Sample`

#### Metric Structure Template
```python
# File: trainloop/eval/metrics/your_metric_name.py
from trainloop_cli.eval_core.types import Sample

def your_metric_name(sample: Sample) -> int:
    # Access LLM response
    response = sample.output["content"]
    
    # Your evaluation logic here
    if condition_met:
        return 1  # Pass
    else:
        return 0  # Fail
```

#### Sample Object Properties
```python
sample.input          # List of conversation messages
sample.output         # Dict with "content" key (LLM response)
sample.model          # Model identifier (e.g., "openai/gpt-4o")
sample.tag            # Request tag for categorization
sample.duration_ms    # Response time in milliseconds
sample.start_time_ms  # Request start timestamp
sample.end_time_ms    # Request end timestamp
sample.location       # Source code location info
```

### Two Evaluation Approaches

#### 1. Programmatic Evaluation (Fast, Deterministic)
```python
def response_is_less_than_120_words(sample: Sample) -> int:
    response = sample.output["content"]
    word_count = len(response.split())
    return 1 if word_count <= 120 else 0

def outputs_single_codeblock(sample: Sample) -> int:
    content = sample.output["content"]
    code_blocks = content.count("```")
    return 1 if code_blocks == 2 else 0  # One opening, one closing
```

#### 2. LLM Judge Evaluation (Flexible, Human-like)
```python
from trainloop_cli.eval_core.judge import assert_true

def response_is_polite(sample: Sample) -> int:
    response = sample.output["content"]
    yes_claim = f"The reply '{response}' is polite, apologetic, and offers a clear resolution."
    no_claim = f"The reply '{response}' is rude OR fails to apologize OR lacks a resolution."
    return assert_true(yes_claim, no_claim)
```

#### Advanced Judge Configuration
```python
def custom_evaluation(sample: Sample) -> int:
    response = sample.output["content"]
    
    custom_config = {
        "models": ["openai/gpt-4o", "anthropic/claude-3-sonnet"],
        "calls_per_model_per_claim": 5,  # More calls = more reliable
        "temperature": 0.3  # Lower = more consistent
    }
    
    yes_claim = f"The response '{response}' meets our quality standards."
    no_claim = f"The response '{response}' fails to meet our quality standards."
    
    return assert_true(yes_claim, no_claim, cfg=custom_config)
```

### Suites: Combining Metrics

**Critical Rules for Suites**:

1. **Tag-based filtering**: `tag("your-tag")` selects which data to evaluate
2. **Metric combination**: `.check(metric1, metric2, ...)` applies multiple metrics
3. **Required export**: Must export a `results` variable
4. **File naming**: Suite filename becomes result filename

#### Suite Structure Template
```python
# File: trainloop/eval/suites/your_suite_name.py
from trainloop_cli.eval_core.helpers import tag
from ..metrics.metric1 import metric1
from ..metrics.metric2 import metric2

# This evaluates all samples tagged "your-tag" against both metrics
results = tag("your-tag").check(metric1, metric2)
```

#### Example Suites
```python
# Simple suite (single metric)
results = tag("active-voice").check(is_active_voice)

# Multi-metric suite (comprehensive evaluation)
results = tag("code-generation").check(
    outputs_single_codeblock,
    code_runs_correctly
)

# Quality assurance suite
results = tag("customer-support").check(
    response_is_polite,
    response_is_less_than_120_words,
    provides_clear_resolution
)
```

### Relationship: Metrics ↔ Suites

- **Metrics**: Atomic evaluation functions (pure, reusable)
- **Suites**: Metric orchestrators (define what to test against which data)
- **Tags**: The bridge linking application instrumentation to evaluation logic

---

## 4. Configuration & Workflow

### Configuration File (`trainloop.config.yaml`)

```yaml
# Data management
data_folder: data
flush_immediately: true
log_level: warn

# LLM Judge settings (for assert_true)
judge:
  models:
    - openai/gpt-4.1-2025-04-14
    - anthropic/claude-sonnet-4-20250514
  calls_per_model_per_claim: 3
  temperature: 0.7
  env_path: ../.env  # API keys location

# Benchmark settings
benchmark:
  providers:
    - openai/gpt-4o
    - anthropic/claude-sonnet-4-20250514
    - gemini/gemini-2.5-flash
  max_samples: 50
  temperature: 0.7
```

### Running Evaluations

```bash
# Run all evaluation suites
trainloop eval

# Run specific suite only
trainloop eval --suite code_generation

# Run with specific tag filter
trainloop eval --tag bubble-sort
```

**What happens during evaluation**:
1. Reads JSONL files from `data/events/`
2. Filters samples by tag
3. Applies metrics
4. Saves results to `data/results/TIMESTAMP/SUITE_NAME.jsonl`

### Data Flow Example
```
Application Code (with tags)
    ↓ [LLM requests]
data/events/1753146600572.jsonl    # Raw interactions
    ↓ [trainloop eval]
data/results/2025-07-21_15-44-19/  # Evaluation results
├── code_generation.jsonl          # Suite results
└── customer_support.jsonl
```

---

## 5. Benchmarks: Comparing LLM Providers

### Purpose
Benchmarks answer: "Which LLM provider/model performs best for my specific use case?"

### How Benchmarks Work
1. **Uses existing evaluation results** as baseline prompts
2. **Re-runs identical prompts** through multiple LLM providers
3. **Applies same metrics** to new responses for fair comparison
4. **Tracks performance metrics**: latency, cost, success rates

### Running Benchmarks
```bash
trainloop benchmark
```

**What it does**:
- Loads latest evaluation results from `data/results/`
- Validates API keys for configured providers
- Sends identical prompts to multiple providers
- Applies existing metrics to all responses
- Saves comparative results to `data/benchmarks/`

### Benchmark Results Structure
```jsonl
{"benchmark_config": {...}, "results": [...]}  # Header with config
{"metric": "code_runs_correctly", "sample": {...}, "provider_result": {
    "provider": "openai/gpt-4o",
    "passed": 1,
    "cost": 0.003,
    "latency_ms": 1250,
    "model": "gpt-4o"
}}
```

### Why Benchmarks Matter
- **Performance tracking**: Monitor which models work best over time
- **Cost optimization**: Find the best price/performance ratio
- **Quality assurance**: Ensure consistency across different providers
- **Provider comparison**: Make data-driven decisions about LLM selection

---

## 6. Visualization: TrainLoop Studio

### Launching Studio
```bash
trainloop studio
```

### What Studio Provides
- **Interactive data exploration** using DuckDB queries
- **Visual comparison** of evaluation results across time
- **Benchmark analysis** with performance metrics
- **Filtering and aggregation** by tags, models, time ranges
- **Export capabilities** for further analysis

### Key Studio Features
- View evaluation trends over time
- Compare provider performance side-by-side
- Drill down into specific failures
- Analyze cost and latency patterns
- Export data for custom analysis

---

## 7. Complete End-to-End Example

### Step 1: Initialize Project
```bash
trainloop init
cd trainloop
```

### Step 2: Instrument Your Application
```python
# Python example
from trainloop_llm_logging import collect, trainloop_tag
from openai import OpenAI

collect("trainloop.config.yaml", flush_immediately=True)
client = OpenAI()

# Tagged request for evaluation
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a Python function that sorts a list"}],
    extra_headers=trainloop_tag("code-generation")
)
```

### Step 3: Create Evaluation Metrics
```python
# trainloop/eval/metrics/code_runs_correctly.py
from trainloop_cli.eval_core.types import Sample
import ast

def code_runs_correctly(sample: Sample) -> int:
    content = sample.output["content"]
    try:
        # Extract and validate Python code
        if "```python" in content:
            code = content.split("```python")[1].split("```")[0].strip()
            ast.parse(code)  # Check syntax
            # Additional validation logic here
            return 1
    except:
        return 0
```

### Step 4: Create Evaluation Suite
```python
# trainloop/eval/suites/code_generation.py
from trainloop_cli.eval_core.helpers import tag
from ..metrics.code_runs_correctly import code_runs_correctly
from ..metrics.outputs_single_codeblock import outputs_single_codeblock

results = tag("code-generation").check(
    outputs_single_codeblock,
    code_runs_correctly
)
```

### Step 5: Run Evaluation
```bash
# Generate some data first (run your application)
python your_app.py

# Then evaluate
trainloop eval
```

### Step 6: Benchmark Providers
```bash
trainloop benchmark
```

### Step 7: Visualize Results
```bash
trainloop studio
```

---

## 8. Best Practices & Tips

### Metric Design
- **Start simple**: Begin with programmatic checks before using LLM judges
- **Combine approaches**: Use deterministic metrics for syntax, LLM judges for quality
- **Handle errors gracefully**: Always return 0 for exceptions unless specifically handling them
- **Make judges specific**: Clear, detailed claims work better than vague ones

### Suite Organization
- **Group related metrics**: Code quality, customer service, factual accuracy
- **Use descriptive tags**: Make it easy to understand what's being tested
- **Start small**: Begin with one metric per suite, expand gradually

### Performance Optimization
- **Batch evaluations**: Run multiple metrics together for efficiency
- **Use appropriate judge models**: Faster models for simple checks, stronger models for complex evaluation
- **Monitor costs**: LLM judges can be expensive at scale

### Data Management
- **Tag consistently**: Use the same tags across your application
- **Regular cleanup**: Archive old evaluation results to manage disk space
- **Version control eval/**: Keep your metrics and suites in git

---

## 9. Common Patterns & Examples

### Code Quality Evaluation
```python
# Metrics for code evaluation
def outputs_single_codeblock(sample: Sample) -> int:
    content = sample.output["content"]
    return 1 if content.count("```") == 2 else 0

def code_compiles(sample: Sample) -> int:
    # Extract and test code compilation
    pass

def includes_comments(sample: Sample) -> int:
    content = sample.output["content"]
    return 1 if "#" in content else 0
```

### Customer Service Quality
```python
# Metrics for customer support
def response_is_polite(sample: Sample) -> int:
    response = sample.output["content"]
    yes = f"The reply '{response}' is polite and professional."
    no = f"The reply '{response}' is rude or unprofessional."
    return assert_true(yes, no)

def provides_solution(sample: Sample) -> int:
    response = sample.output["content"]
    yes = f"The reply '{response}' offers a concrete solution or next steps."
    no = f"The reply '{response}' doesn't provide actionable guidance."
    return assert_true(yes, no)
```

### Content Format Validation
```python
# Metrics for content formatting
def proper_json_format(sample: Sample) -> int:
    import json
    try:
        json.loads(sample.output["content"])
        return 1
    except:
        return 0

def contains_required_sections(sample: Sample) -> int:
    content = sample.output["content"].lower()
    required = ["introduction", "methodology", "conclusion"]
    return 1 if all(section in content for section in required) else 0
```

---

This cheatsheet covers everything needed to implement comprehensive LLM evaluation using TrainLoop's framework. Start with simple metrics, gradually add complexity, and use benchmarks to make data-driven decisions about your LLM implementation.