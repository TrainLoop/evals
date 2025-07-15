---
sidebar_position: 1
---

# Event Data Format

TrainLoop SDKs collect LLM interaction data in a standardized JSONL format.

## Overview

Event data is stored as newline-delimited JSON (JSONL) files in the `data/events/` folder. Each line represents a single LLM interaction.

## File Structure

```
data/
├── events/
│   ├── 2024-01-15.jsonl    # Events from January 15, 2024
│   ├── 2024-01-16.jsonl    # Events from January 16, 2024
│   └── ...
```

## Event Schema

### Basic Event Structure

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": { ... },
  "output": { ... },
  "metadata": { ... }
}
```

### Complete Event Example

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": {
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "output": {
    "content": "The capital of France is Paris.",
    "role": "assistant",
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 8,
      "total_tokens": 33
    },
    "finish_reason": "stop"
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tags": ["qa", "geography"],
    "duration_ms": 1250,
    "request_id": "req_abc123",
    "response_id": "resp_xyz789"
  }
}
```

## Field Descriptions

### Root Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp when the request was made |
| `input` | object | LLM request parameters |
| `output` | object | LLM response data |
| `metadata` | object | Additional tracking information |

### Input Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | LLM model name (e.g., "gpt-4o-mini") |
| `messages` | array | Chat completion messages |
| `temperature` | number | Sampling temperature (0-2) |
| `max_tokens` | number | Maximum tokens to generate |
| `top_p` | number | Nucleus sampling parameter |
| `frequency_penalty` | number | Frequency penalty (-2 to 2) |
| `presence_penalty` | number | Presence penalty (-2 to 2) |
| `stop` | array | Stop sequences |
| `stream` | boolean | Whether response was streamed |

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Generated text content |
| `role` | string | Response role (usually "assistant") |
| `usage` | object | Token usage information |
| `finish_reason` | string | Why generation stopped |
| `tool_calls` | array | Function/tool calls made |

### Usage Fields

| Field | Type | Description |
|-------|------|-------------|
| `prompt_tokens` | number | Tokens in the prompt |
| `completion_tokens` | number | Tokens in the completion |
| `total_tokens` | number | Total tokens used |

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `provider` | string | LLM provider (openai, anthropic, etc.) |
| `model` | string | Model name |
| `tags` | array | Custom tags for filtering |
| `duration_ms` | number | Request duration in milliseconds |
| `request_id` | string | Unique request identifier |
| `response_id` | string | Unique response identifier |
| `error` | string | Error message if request failed |

## Provider-Specific Examples

### OpenAI

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": {
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "output": {
    "content": "Hello! How can I help you today?",
    "role": "assistant",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 8,
      "total_tokens": 18
    },
    "finish_reason": "stop"
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tags": ["greeting"],
    "duration_ms": 1250
  }
}
```

### Anthropic

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": {
    "model": "claude-3-haiku-20240307",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "max_tokens": 1000,
    "temperature": 0.7
  },
  "output": {
    "content": "Hello! How can I assist you today?",
    "role": "assistant",
    "usage": {
      "input_tokens": 10,
      "output_tokens": 8,
      "total_tokens": 18
    },
    "stop_reason": "end_turn"
  },
  "metadata": {
    "provider": "anthropic",
    "model": "claude-3-haiku-20240307",
    "tags": ["greeting"],
    "duration_ms": 1100
  }
}
```

## Error Events

When LLM calls fail, error information is captured:

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": {
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  },
  "output": null,
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tags": ["greeting"],
    "duration_ms": 5000,
    "error": "Rate limit exceeded"
  }
}
```

## Streaming Events

For streaming responses, events are captured when the stream completes:

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": {
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Tell me a story"}
    ],
    "stream": true
  },
  "output": {
    "content": "Once upon a time...",
    "role": "assistant",
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 250,
      "total_tokens": 265
    },
    "finish_reason": "stop"
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tags": ["story"],
    "duration_ms": 8500,
    "stream": true
  }
}
```

## Custom Tags

Events can be tagged for targeted evaluation:

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": { ... },
  "output": { ... },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tags": [
      "customer-support",
      "priority-high",
      "v1.0"
    ],
    "duration_ms": 1250
  }
}
```

## Reading Event Data

### Command Line

```bash
# View recent events
tail -f data/events/$(date +%Y-%m-%d).jsonl

# Count events
wc -l data/events/*.jsonl

# Filter by tag
grep '"customer-support"' data/events/*.jsonl
```

### Python

```python
import json
from pathlib import Path

def read_events(data_folder):
    events = []
    events_dir = Path(data_folder) / "events"
    
    for event_file in events_dir.glob("*.jsonl"):
        with open(event_file) as f:
            for line in f:
                events.append(json.loads(line))
    
    return events

# Usage
events = read_events("trainloop/data")
print(f"Found {len(events)} events")
```

### SQL (via DuckDB)

```sql
-- Query events in Studio UI
SELECT 
  timestamp,
  metadata.provider,
  metadata.model,
  metadata.tags,
  input.model,
  output.content
FROM 'data/events/*.jsonl'
WHERE 'customer-support' = ANY(metadata.tags)
ORDER BY timestamp DESC
LIMIT 10;
```

## Best Practices

1. **Tagging**: Use meaningful tags for targeted evaluation
2. **Retention**: Regularly clean up old event files
3. **Monitoring**: Track event volume and storage usage
4. **Security**: Avoid logging sensitive information
5. **Compression**: Compress old event files to save space

## See Also

- [Results Data Format](results.md) - Evaluation results schema
- [SDK Reference](../sdk/index.md) - How to collect event data
- [CLI Reference](../cli/eval.md) - How to process event data