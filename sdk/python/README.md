# TrainLoop Python SDK

Zero-touch HTTP instrumentation library for collecting LLM request/response data.

## 📚 Documentation

For complete Python SDK documentation, installation guides, and usage examples:

**👉 [evals.docs.trainloop.ai](https://evals.docs.trainloop.ai/reference/sdk/python/api)**

### Quick Links
- **[Python SDK Guide](https://evals.docs.trainloop.ai/docs/python/quick-start)** - Complete integration guide
- **[Installation](https://evals.docs.trainloop.ai/getting-started/installation#python-sdk)** - Install the SDK
- **[Development](https://evals.docs.trainloop.ai/docs/python/development)** - Contributing to the SDK

## Quick Start

```bash
# Install
pip install trainloop-llm-logging
```

```python
from trainloop_llm_logging import collect

# Start collecting LLM data
collect("path/to/trainloop.config.yaml")

# Your existing LLM calls work automatically
# No code changes required!
```

For detailed information, visit **[evals.docs.trainloop.ai/docs/python](https://evals.docs.trainloop.ai/docs/python)**