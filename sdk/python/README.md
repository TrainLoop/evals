# TrainLoop Python SDK

Zero-touch HTTP instrumentation library for collecting LLM request/response data.

## 📚 Documentation

For complete Python SDK documentation, installation guides, and usage examples:

**👉 [docs.trainloop.ai](https://docs.trainloop.ai)**

### Quick Links
- **[Python SDK Guide](https://docs.trainloop.ai/guides/python-sdk)** - Complete integration guide
- **[Installation](https://docs.trainloop.ai/getting-started/installation)** - Install the SDK
- **[API Reference](https://docs.trainloop.ai/reference/sdk/python)** - Complete API documentation
- **[Development](https://docs.trainloop.ai/development/local-development)** - Contributing to the SDK

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

For detailed information, visit **[docs.trainloop.ai](https://docs.trainloop.ai)**