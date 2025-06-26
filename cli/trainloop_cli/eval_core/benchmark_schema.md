# Benchmark Data Schema Design

## Overview

The benchmark feature enables comparing evaluation results across multiple LLM providers. This document describes the data schema and JSONL output format for benchmark runs.

## Design Principles

1. **Compatibility**: Extends existing `Sample` and `Result` types rather than replacing them
2. **Flexibility**: Supports various comparison dimensions (providers, models, parameters)
3. **UI-Friendly**: Structured for efficient querying and visualization in DuckDB
4. **Extensibility**: Easy to add new metrics or provider configurations

## JSONL Output Format

Benchmark results are saved to `data/benchmarks/{timestamp}/{suite_name}.jsonl` with three types of records:

### 1. Metadata Record (First Line)
```json
{
  "type": "metadata",
  "data": {
    "benchmark_id": "bench_20240315_143022_abc123",
    "timestamp": "2024-03-15T14:30:22.123Z",
    "base_eval_run": "2024-03-15_14-25-00",
    "suite_name": "qa_accuracy",
    "description": "Comparing GPT-4 vs Claude vs Gemini on QA tasks",
    "tags": ["production", "qa"],
    "providers": [
      {
        "provider": "openai",
        "model": "gpt-4",
        "model_params": {"temperature": 0.0, "max_tokens": 1000}
      },
      {
        "provider": "anthropic", 
        "model": "claude-3-opus-20240229",
        "model_params": {"temperature": 0.0, "max_tokens": 1000}
      }
    ]
  }
}
```

### 2. Result Records (Multiple Lines)
```json
{
  "type": "result",
  "data": {
    "provider_config": {
      "provider": "openai",
      "model": "gpt-4",
      "model_params": {"temperature": 0.0}
    },
    "sample": {
      "duration_ms": 1523,
      "tag": "customer_support_001",
      "input": [{"role": "user", "content": "How do I reset my password?"}],
      "output": {"content": "To reset your password..."},
      "model": "gpt-4",
      "model_params": {"temperature": 0.0},
      "start_time_ms": 1710515422000,
      "end_time_ms": 1710515423523,
      "url": "https://api.openai.com/v1/chat/completions",
      "location": {"tag": "customer_support", "lineNumber": "42"}
    },
    "metrics": [
      {
        "metric": "response_quality",
        "passed": 1,
        "score": 0.92,
        "reason": null
      },
      {
        "metric": "hallucination_check", 
        "passed": 0,
        "score": 0.3,
        "reason": "Response contains unverified claim about password reset timeframe"
      }
    ],
    "summary": {
      "total_metrics": 2,
      "passed_metrics": 1,
      "avg_score": 0.61,
      "pass_rate": 0.5
    },
    "timing": {
      "provider_latency_ms": 1523,
      "evaluation_time_ms": 342
    }
  }
}
```

### 3. Summary Record (Last Line)
```json
{
  "type": "summary",
  "data": {
    "benchmark_id": "bench_20240315_143022_abc123",
    "timestamp": "2024-03-15T14:30:22.123Z",
    "suite_name": "qa_accuracy",
    "total_samples": 50,
    "total_providers": 2,
    "provider_summaries": {
      "openai/gpt-4": {
        "total_evaluations": 50,
        "avg_pass_rate": 0.84,
        "avg_latency_ms": 1456,
        "total_cost": 2.34,
        "metrics": {
          "response_quality": {"pass_rate": 0.92, "avg_score": 0.89},
          "hallucination_check": {"pass_rate": 0.76, "avg_score": 0.71}
        }
      },
      "anthropic/claude-3-opus": {
        "total_evaluations": 50,
        "avg_pass_rate": 0.88,
        "avg_latency_ms": 2103,
        "total_cost": 3.12,
        "metrics": {
          "response_quality": {"pass_rate": 0.94, "avg_score": 0.91},
          "hallucination_check": {"pass_rate": 0.82, "avg_score": 0.78}
        }
      }
    },
    "metric_comparisons": {
      "response_quality": {
        "best_provider": "anthropic/claude-3-opus",
        "worst_provider": "openai/gpt-4",
        "spread": 0.02
      }
    },
    "overall": {
      "best_provider": "anthropic/claude-3-opus",
      "worst_provider": "openai/gpt-4",
      "avg_duration_ms": 1779.5,
      "total_duration_ms": 177950
    }
  }
}
```

## DuckDB View Schema

The UI will create a `benchmarks` view with the following structure:

```sql
CREATE VIEW benchmarks AS
SELECT
  -- Extracted from filename/path
  regexp_extract(filename, '/benchmarks/([^/]+)/', 1) AS ts,
  regexp_extract(filename, '/benchmarks/[^/]+/([^/]+)\.jsonl', 1) AS suite,
  
  -- Record type discrimination
  type,
  
  -- Flattened fields for easier querying
  data->>'benchmark_id' AS benchmark_id,
  data->>'timestamp' AS benchmark_timestamp,
  
  -- For result records
  data->'provider_config'->>'provider' AS provider,
  data->'provider_config'->>'model' AS model,
  data->'sample'->>'tag' AS sample_tag,
  data->'summary'->>'avg_score' AS avg_score,
  data->'summary'->>'pass_rate' AS pass_rate,
  
  -- Full JSON for detailed views
  data
FROM read_json_auto('${ROOT}/benchmarks/*/*.jsonl', filename=true);
```

## Key Design Decisions

1. **Three-Record Structure**: Separates metadata, individual results, and summary for efficient processing
2. **Provider Namespacing**: Uses "provider/model" format for clear identification
3. **Metric Flexibility**: Supports both binary pass/fail and numeric scoring
4. **Timing Separation**: Tracks both provider latency and evaluation overhead
5. **Cost Tracking**: Placeholder for future cost comparison features
6. **Reference Linking**: Optional link to original evaluation run for traceability

## UI Visualization Support

This schema enables the UI to:
- Show side-by-side provider comparisons
- Generate charts for metric performance across providers
- Calculate cost/performance tradeoffs
- Filter by tags, suites, or specific providers
- Drill down from summary to individual sample results

## Future Extensions

The schema is designed to support:
- Multi-model comparisons within same provider
- Parameter sensitivity analysis (temperature, etc.)
- Cross-suite benchmark aggregation
- Historical trend analysis
- Custom metric plugins