---
sidebar_position: 1
---

# Python SDK API

Complete API reference for the TrainLoop Python SDK.

## Installation

```bash
pip install trainloop-llm-logging
```

## Basic Usage

```python
from trainloop_llm_logging import collect, trainloop_tag

# Initialize TrainLoop (call once at startup)
collect("trainloop/trainloop.config.yaml")

# Use with OpenAI
import openai
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers=trainloop_tag("greeting")  # Optional tagging
)
```

## API Reference

### collect(config_path=None, **kwargs)

Initialize TrainLoop data collection.

**Parameters**:
- `config_path` (str, optional): Path to configuration file
- `flush_immediately` (bool, optional): Disable buffering
- `tags` (list, optional): Default tags for all events

**Example**:
```python
# Basic initialization
collect()

# With configuration file
collect("trainloop/trainloop.config.yaml")

# With options
collect(flush_immediately=True, tags=["production"])
```

### trainloop_tag(tag)

Generate headers for tagging LLM calls.

**Parameters**:
- `tag` (str): Tag name

**Returns**: Dict of headers for OpenAI `extra_headers`

**Example**:
```python
# Basic tagging
headers = trainloop_tag("greeting")
headers = trainloop_tag("customer-support")
```

### flush()

Manually flush buffered events to disk.

**Example**:
```python
from trainloop_llm_logging import flush

# Flush all buffered events
flush()
```

## Supported Libraries

The Python SDK automatically instruments these libraries:

- **OpenAI** (`openai` package)
- **Anthropic** (`anthropic` package)
- **Requests** (`requests` package)
- **HTTPX** (`httpx` package)

## Configuration

### Via Configuration File

```yaml
# trainloop.config.yaml
sdk:
  flush_immediately: false
  buffer_size: 5
  buffer_timeout: 10
  tags: ["production"]
```

### Via Environment Variables

```bash
export TRAINLOOP_DATA_FOLDER="./data"
export TRAINLOOP_FLUSH_IMMEDIATELY=true
export TRAINLOOP_TAGS="production,v1.0"
```

### Via Code

```python
collect(
    flush_immediately=True,
    buffer_size=10,
    buffer_timeout=30,
    tags=["production"]
)
```

## Advanced Usage

### Custom Data Folder

```python
import os
os.environ["TRAINLOOP_DATA_FOLDER"] = "/custom/path"
collect()
```

### Conditional Instrumentation

```python
import os

# Only instrument in production
if os.getenv("ENVIRONMENT") == "production":
    collect()
```

### Error Handling

```python
try:
    collect()
except Exception as e:
    print(f"TrainLoop initialization failed: {e}")
    # Continue without instrumentation
```

## Examples

### OpenAI Chat Completion

```python
import openai
from trainloop_llm_logging import collect, trainloop_tag

collect()
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    extra_headers=trainloop_tag("qa")
)
```

### Anthropic Claude

```python
import anthropic
from trainloop_llm_logging import collect, trainloop_tag

collect()
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ],
    extra_headers=trainloop_tag("greeting")
)
```

### Batch Processing

```python
import openai
from trainloop_llm_logging import collect, trainloop_tag, flush

collect()
client = openai.OpenAI()

# Process multiple requests
for i in range(100):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Request {i}"}],
        extra_headers=trainloop_tag("batch-processing")
    )

# Ensure all events are written
flush()
```

## Troubleshooting

### Common Issues

**ImportError**: Install the package with `pip install trainloop-llm-logging`

**No data collected**: Check that `TRAINLOOP_DATA_FOLDER` is set and writable

**High memory usage**: Enable `flush_immediately=True` for high-volume applications

**Missing events**: Ensure `collect()` is called before making LLM calls

## See Also

- [SDK Overview](../index.md) - Multi-language SDK documentation
- [Getting Started](../../../tutorials/getting-started.md) - Complete setup guide
- [TypeScript SDK](../typescript/api.md) - TypeScript API reference
- [Go SDK](../go/api.md) - Go API reference