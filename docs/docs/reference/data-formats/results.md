---
sidebar_position: 2
---

# Results Data Format

TrainLoop CLI generates evaluation results in JSON format after processing events with metrics.

## Overview

Results data is stored as JSON files in the `data/results/` folder. Each file contains the outcomes of running evaluation metrics on event data.

## File Structure

```
data/
├── results/
│   ├── evaluation_results_2024-01-15_14-30-25.json    # Main evaluation results
│   ├── evaluation_results_2024-01-15_15-00-00.json    # Another evaluation run
│   ├── evaluation_summary.json                        # Latest summary
│   └── benchmark_results_2024-01-15_16-00-00.json     # Benchmark results
```

## Results Schema

### Basic Results Structure

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "duration": 2.3,
  "total_events": 150,
  "suites": { ... },
  "summary": { ... }
}
```

### Complete Results Example

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "duration": 2.3,
  "total_events": 150,
  "suites": {
    "greeting_evaluation": {
      "events_processed": 45,
      "metrics": {
        "has_greeting_word": {
          "passed": 42,
          "total": 45,
          "score": 0.933,
          "details": [
            {
              "event_id": "evt_123",
              "passed": true,
              "input": "Hello, how are you?",
              "output": "Hello! I'm doing well, thanks for asking.",
              "verdict": "Contains greeting word: hello"
            }
          ]
        },
        "is_personalized": {
          "passed": 38,
          "total": 45,
          "score": 0.844,
          "details": [...]
        }
      },
      "overall_score": 0.889,
      "tags": ["greeting-generation"],
      "duration": 1.2
    },
    "accuracy_check": {
      "events_processed": 105,
      "metrics": {
        "is_accurate": {
          "passed": 95,
          "total": 105,
          "score": 0.905,
          "details": [...]
        }
      },
      "overall_score": 0.905,
      "tags": [""],
      "duration": 1.1
    }
  },
  "summary": {
    "total_suites": 2,
    "overall_score": 0.897,
    "total_metrics": 3,
    "total_passed": 175,
    "total_evaluated": 195,
    "pass_rate": 0.897
  },
  "configuration": {
    "data_folder": "./trainloop/data",
    "judge_models": ["openai/gpt-4o-mini"],
    "parallel_evaluations": 10
  }
}
```

## Field Descriptions

### Root Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp when evaluation started |
| `duration` | number | Total evaluation duration in seconds |
| `total_events` | number | Total events processed |
| `suites` | object | Results for each evaluation suite |
| `summary` | object | Aggregated results summary |
| `configuration` | object | Configuration used for evaluation |

### Suite Fields

| Field | Type | Description |
|-------|------|-------------|
| `events_processed` | number | Events processed by this suite |
| `metrics` | object | Results for each metric |
| `overall_score` | number | Average score across all metrics |
| `tags` | array | Tags used to filter events |
| `duration` | number | Suite execution duration |

### Metric Fields

| Field | Type | Description |
|-------|------|-------------|
| `passed` | number | Number of events that passed |
| `total` | number | Total events evaluated |
| `score` | number | Pass rate (passed/total) |
| `details` | array | Individual event results |

### Detail Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Unique event identifier |
| `passed` | boolean | Whether metric passed |
| `input` | string | Input text (truncated) |
| `output` | string | Output text (truncated) |
| `verdict` | string | Explanation of result |
| `metadata` | object | Additional metadata |

## Benchmark Results

Benchmark results have additional fields for model comparison:

```json
{
  "timestamp": "2024-01-15T16:00:00.123Z",
  "type": "benchmark",
  "providers": ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3-sonnet"],
  "total_samples": 100,
  "results": {
    "openai/gpt-4o": {
      "metrics": {
        "helpful_check": {
          "passed": 85,
          "total": 100,
          "score": 0.85
        }
      },
      "overall_score": 0.85,
      "cost_analysis": {
        "total_cost": 4.50,
        "cost_per_token": 0.015,
        "cost_per_score": 0.053
      },
      "performance": {
        "avg_response_time": 1.2,
        "total_tokens": 15000
      }
    },
    "openai/gpt-4o-mini": {
      "metrics": {
        "helpful_check": {
          "passed": 82,
          "total": 100,
          "score": 0.82
        }
      },
      "overall_score": 0.82,
      "cost_analysis": {
        "total_cost": 0.30,
        "cost_per_token": 0.001,
        "cost_per_score": 0.004
      },
      "performance": {
        "avg_response_time": 0.8,
        "total_tokens": 15000
      }
    }
  },
  "comparison": {
    "best_overall": "openai/gpt-4o",
    "best_value": "openai/gpt-4o-mini",
    "cost_savings": 0.93
  }
}
```

## Summary File

The `evaluation_summary.json` file contains a rolling summary:

```json
{
  "latest_evaluation": "2024-01-15T14:30:25.123Z",
  "total_suites": 2,
  "overall_score": 0.897,
  "trending": {
    "score_change": 0.05,
    "trend": "improving",
    "last_7_days": [
      {"date": "2024-01-09", "score": 0.82},
      {"date": "2024-01-10", "score": 0.84},
      {"date": "2024-01-11", "score": 0.86},
      {"date": "2024-01-12", "score": 0.88},
      {"date": "2024-01-13", "score": 0.89},
      {"date": "2024-01-14", "score": 0.90},
      {"date": "2024-01-15", "score": 0.897}
    ]
  },
  "metrics_summary": {
    "total_metrics": 3,
    "critical_metrics": ["is_accurate", "is_safe"],
    "performance_metrics": ["has_greeting_word", "is_personalized"]
  }
}
```

## Reading Results Data

### Command Line

```bash
# View latest results
cat data/results/evaluation_summary.json

# View specific evaluation
cat data/results/evaluation_results_2024-01-15_14-30-25.json

# Extract scores
jq '.summary.overall_score' data/results/evaluation_summary.json
```

### Python

```python
import json
from pathlib import Path

def read_results(data_folder):
    results_dir = Path(data_folder) / "results"
    
    # Read summary
    summary_file = results_dir / "evaluation_summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
        return summary
    
    # Find latest results
    result_files = list(results_dir.glob("evaluation_results_*.json"))
    if not result_files:
        return None
        
    latest_file = max(result_files, key=lambda p: p.stat().st_mtime)
    with open(latest_file) as f:
        return json.load(f)

# Usage
results = read_results("trainloop/data")
if results:
    print(f"Overall score: {results['summary']['overall_score']:.1%}")
```

### SQL (via DuckDB)

```sql
-- Query results in Studio UI
SELECT 
  timestamp,
  summary.overall_score,
  summary.total_suites,
  summary.pass_rate
FROM 'data/results/evaluation_*.json'
ORDER BY timestamp DESC
LIMIT 10;

-- Suite performance over time
SELECT 
  timestamp,
  suite_name,
  suite_data.overall_score
FROM 'data/results/evaluation_*.json',
     UNNEST(suites) AS suite_data
ORDER BY timestamp DESC;
```

## Error Results

When evaluations fail, error information is captured:

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "duration": 0.5,
  "status": "error",
  "error": {
    "type": "MetricError",
    "message": "Metric 'is_helpful' failed to execute",
    "details": {
      "metric": "is_helpful",
      "suite": "quality_check",
      "event_id": "evt_456",
      "traceback": "..."
    }
  },
  "partial_results": {
    "suites": {
      "quality_check": {
        "events_processed": 23,
        "status": "failed",
        "error": "Metric execution failed"
      }
    }
  }
}
```

## Best Practices

1. **Regular Cleanup**: Remove old result files to save space
2. **Monitoring**: Track overall_score trends over time
3. **Alerting**: Set up alerts for score drops
4. **Archiving**: Archive important benchmark results
5. **Analysis**: Use SQL queries for deeper analysis

## See Also

- [Event Data Format](events.md) - Input data structure
- [CLI Reference](../cli/eval.md) - How to generate results
- [Studio UI](../cli/studio.md) - How to visualize results