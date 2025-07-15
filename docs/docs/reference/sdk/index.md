---
sidebar_position: 1
---

# SDK Reference

TrainLoop SDKs provide zero-touch instrumentation for capturing LLM interactions in your applications.

## Overview

TrainLoop SDKs automatically capture request/response data from LLM API calls and save it as JSONL files for evaluation. They support:

- **Zero-touch instrumentation** - Minimal code changes required
- **Multi-provider support** - Works with OpenAI, Anthropic, Google, and more
- **Automatic data collection** - Captures all LLM interactions transparently
- **Custom tagging** - Tag specific calls for targeted evaluation
- **Buffered writes** - Efficient data storage with configurable flushing

## Supported Languages

| Language | Package | Documentation |
|----------|---------|---------------|
| Python | `trainloop-llm-logging` | [Python SDK](python/api.md) |
| TypeScript/JavaScript | `trainloop-llm-logging` | [TypeScript SDK](typescript/api.md) |
| Go | `github.com/trainloop/evals/sdk/go/trainloop-llm-logging` | [Go SDK](go/api.md) |

## Common Concepts

### Event Data

All SDKs capture the same event data structure:

```json
{
  "timestamp": "2024-01-15T14:30:25.123Z",
  "input": {
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7
  },
  "output": {
    "content": "Hello! How can I help you today?",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 8,
      "total_tokens": 18
    }
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tags": ["greeting"],
    "duration_ms": 1250
  }
}
```

### Tagging

Tag LLM calls for targeted evaluation:

```python
# Python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers=trainloop_tag("greeting")
)
```

```javascript
// TypeScript/JavaScript
const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{"role": "user", "content": "Hello"}]
}, {
    headers: { ...trainloopTag("greeting") }
});
```

```go
// Go
resp, err := client.CreateChatCompletion(
    context.Background(),
    openai.ChatCompletionRequest{
        Model: openai.GPT4OMini,
        Messages: []openai.ChatCompletionMessage{
            {Role: openai.ChatMessageRoleUser, Content: "Hello"},
        },
    },
)
```

### Data Storage

All SDKs write to the same JSONL format in the configured data folder:

```
$TRAINLOOP_DATA_FOLDER/
├── events/
│   ├── 2024-01-15.jsonl
│   ├── 2024-01-16.jsonl
│   └── ...
```

### Configuration

Common configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `data_folder` | Where to store event files | `./trainloop/data` |
| `flush_immediately` | Disable buffering | `false` |
| `buffer_size` | Events before auto-flush | `5` |
| `buffer_timeout` | Seconds before auto-flush | `10` |
| `tags` | Default tags for all events | `[]` |

## Installation

### Python

```bash
pip install trainloop-llm-logging
```

### TypeScript/JavaScript

```bash
npm install trainloop-llm-logging
```

### Go

```bash
go get github.com/trainloop/evals/sdk/go/trainloop-llm-logging
```

## Quick Start

See the [Getting Started Tutorial](../../tutorials/getting-started.md) for complete setup instructions.

## Environment Variables

All SDKs respect these environment variables:

| Variable | Description |
|----------|-------------|
| `TRAINLOOP_DATA_FOLDER` | Data storage location |
| `TRAINLOOP_FLUSH_IMMEDIATELY` | Disable buffering |
| `TRAINLOOP_TAGS` | Default tags (comma-separated) |

## Language-Specific Documentation

- **[Python SDK](python/api.md)** - Complete Python API reference
- **[TypeScript SDK](typescript/api.md)** - Complete TypeScript API reference  
- **[Go SDK](go/api.md)** - Complete Go API reference

## Common Patterns

### Error Handling

```python
# Python
try:
    collect("trainloop/trainloop.config.yaml")
except Exception as e:
    print(f"Failed to initialize TrainLoop: {e}")
```

### Selective Instrumentation

```python
# Python - Only instrument specific calls
if should_evaluate:
    extra_headers = trainloop_tag("evaluation")
else:
    extra_headers = {}
```

### Testing

```python
# Python - Skip instrumentation in tests
if not os.getenv("TRAINLOOP_ENABLED", "true").lower() == "true":
    # Skip collect() call
    pass
```

## Best Practices

1. **Initialize early** - Set up instrumentation at application startup
2. **Use meaningful tags** - Tag calls for specific evaluation scenarios
3. **Handle errors gracefully** - Don't let instrumentation break your app
4. **Flush on shutdown** - Ensure data is written before exit
5. **Monitor data volume** - Be aware of storage requirements

## Troubleshooting

### Common Issues

**No data being collected**:
- Check `TRAINLOOP_DATA_FOLDER` is set correctly
- Verify SDK is initialized
- Ensure data folder exists and is writable

**High memory usage**:
- Enable `flush_immediately` for high-volume applications
- Reduce `buffer_size` if needed

**Missing events**:
- Check for errors in application logs
- Verify API calls are going through instrumented clients
- Ensure proper shutdown handling

## See Also

- [Getting Started Tutorial](../../tutorials/getting-started.md) - Complete setup guide
- [CLI Reference](../cli/index.md) - Process collected data
- [Architecture](../../explanation/concepts/architecture.md) - How SDKs fit into the system