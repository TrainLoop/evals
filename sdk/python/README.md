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

## Development & Testing

For SDK development and testing information:

- **Unit Tests**: `poetry run pytest -m unit`
- **Integration Tests**: `python run_integration_tests.py` (see [INTEGRATION_TESTING.md](./INTEGRATION_TESTING.md))
- **Documentation**: See [docs/development/sdk-testing.md](../../docs/docs/development/sdk-testing.md)

**Note**: Integration tests cannot use pytest due to import order requirements. Use the standalone test runner instead.