---
sidebar_position: 2
---

# Python SDK API

The TrainLoop Evals Python SDK provides zero-touch instrumentation for Python applications.

## Installation

```bash
pip install trainloop-sdk
```

## Quick Start

```python
import trainloop

# Initialize the SDK
trainloop.init(endpoint="http://localhost:8000")

# Your LLM calls are automatically instrumented
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello, world!"}]
)
```

## Configuration

The SDK can be configured using environment variables or initialization parameters:

### Environment Variables

- `TRAINLOOP_ENDPOINT` - The endpoint to send traces to (default: `http://localhost:8000`)
- `TRAINLOOP_API_KEY` - API key for authentication (optional)
- `TRAINLOOP_DEBUG` - Enable debug logging (default: `false`)

### Initialization Parameters

```python
import trainloop

trainloop.init(
    endpoint="http://localhost:8000",
    api_key="your-api-key",
    debug=True
)
```

## Supported Libraries

The Python SDK automatically instruments the following libraries:

- OpenAI
- Anthropic
- LiteLLM
- LangChain
- LlamaIndex

## Manual Instrumentation

For custom instrumentation, you can use the manual tracing API:

```python
import trainloop

with trainloop.trace("my-llm-call") as span:
    span.set_input({"prompt": "Hello, world!"})
    # Your LLM call here
    span.set_output({"response": "Hello! How can I help you?"})
```