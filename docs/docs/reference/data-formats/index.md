---
sidebar_position: 1
---

# Data Formats

TrainLoop Evals uses standardized data formats for interoperability and vendor independence.

## Overview

All data in TrainLoop Evals is stored as JSON or JSONL (newline-delimited JSON) files. This ensures:

- **Vendor independence** - No proprietary databases
- **Easy integration** - Works with any text processing tools
- **Version control friendly** - Text files can be tracked in git
- **Transparent format** - Human-readable and debuggable

## File Types

| Format | Extension | Description | Location |
|--------|-----------|-------------|----------|
| Events | `.jsonl` | LLM interaction data | `data/events/` |
| Results | `.json` | Evaluation results | `data/results/` |
| Benchmarks | `.json` | Model comparison data | `data/benchmarks/` |
| Configuration | `.yaml` | TrainLoop configuration | `trainloop.config.yaml` |

## Data Flow

```
Application → SDK → Events (JSONL) → CLI → Results (JSON) → Studio UI
```

1. **SDKs** capture LLM interactions and write events
2. **CLI** processes events and generates results
3. **Studio UI** reads results and events for visualization

## Quick Reference

### Event Data

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": { "model": "gpt-4o-mini", "messages": [...] },
  "output": { "content": "Hello!", "usage": {...} },
  "metadata": { "provider": "openai", "tags": ["greeting"] }
}
```

### Results Data

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "suites": {
    "greeting_evaluation": {
      "metrics": {
        "has_greeting_word": { "passed": 42, "total": 45, "score": 0.933 }
      },
      "overall_score": 0.889
    }
  },
  "summary": { "overall_score": 0.897 }
}
```

## Working with Data

### Command Line Tools

```bash
# View recent events
tail -f data/events/$(date +%Y-%m-%d).jsonl

# Count events
wc -l data/events/*.jsonl

# Extract specific fields
jq '.metadata.provider' data/events/*.jsonl | sort | uniq -c

# View results summary
jq '.summary.overall_score' data/results/evaluation_summary.json
```

### Python Processing

```python
import json
from pathlib import Path

# Read events
def read_events(data_folder):
    events = []
    for file in Path(data_folder).glob("events/*.jsonl"):
        with open(file) as f:
            for line in f:
                events.append(json.loads(line))
    return events

# Read results
def read_results(data_folder):
    results_file = Path(data_folder) / "results" / "evaluation_summary.json"
    with open(results_file) as f:
        return json.load(f)
```

### SQL Queries

TrainLoop Studio UI uses DuckDB for SQL queries:

```sql
-- Events by provider
SELECT 
  metadata.provider,
  COUNT(*) as event_count
FROM 'data/events/*.jsonl'
GROUP BY metadata.provider;

-- Results over time
SELECT 
  timestamp,
  summary.overall_score
FROM 'data/results/evaluation_*.json'
ORDER BY timestamp DESC;
```

## Schema Validation

All data formats include schema validation:

```python
# Validate event data
from trainloop_cli.data.schemas import validate_event

event = {...}
is_valid, errors = validate_event(event)
if not is_valid:
    print(f"Invalid event: {errors}")
```

## Detailed Documentation

- **[Event Data Format](events.md)** - Complete event schema and examples
- **[Results Data Format](results.md)** - Evaluation results structure
- **[Configuration Format](../cli/config.md)** - YAML configuration reference

## Best Practices

1. **Regular Backups**: Back up data files regularly
2. **Compression**: Compress old files to save space
3. **Monitoring**: Track data volume and growth
4. **Validation**: Validate data integrity periodically
5. **Archiving**: Archive important datasets

## Migration and Compatibility

TrainLoop Evals maintains backward compatibility:

- **Version tracking** - All files include format version
- **Migration tools** - Automatic migration between versions
- **Validation** - Schema validation ensures compatibility

## See Also

- [Architecture](../../explanation/architecture.md) - How data flows through the system
- [SDK Reference](../sdks/index.md) - How to collect event data
- [CLI Reference](../cli/index.md) - How to process data