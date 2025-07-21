---
sidebar_position: 6
---

# Production Setup

This tutorial covers the essential considerations for running TrainLoop Evals in production environments.

## Critical Production Recommendation

**⚠️ Important: Do not use `flush_immediately=True` in production.**

When configuring TrainLoop SDKs in production, ensure that `flush_immediately` is set to `false` (or not set at all, as this is the default):

### Python SDK

```python
from trainloop_llm_logging import collect

# ❌ Don't do this in production
collect(flush_immediately=True)

# ✅ Do this instead (default behavior)
collect()  # flush_immediately defaults to False
```

### TypeScript SDK

The TypeScript SDK handles data collection asynchronously by default when using the `NODE_OPTIONS="--require=trainloop-llm-logging"` approach.

### Go SDK  

```go
import trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"

func init() {
    // Default behavior is async
    trainloop.Collect()
}
```

## Why flush_immediately=False Matters

When `flush_immediately=True`:
- **Blocking behavior**: Each LLM call waits for data to be written to disk before returning
- **Performance impact**: Adds latency to every LLM request in your application
- **Reduced throughput**: Your application will handle fewer requests per second

When `flush_immediately=False` (default):
- **Async behavior**: Data is buffered and written to disk in the background
- **Better performance**: No impact on your application's response time
- **Higher throughput**: Your application maintains optimal performance

## Basic Production Configuration

Create a production-ready configuration file:

```yaml
# trainloop.config.yaml (production)
data_folder: "./trainloop/data"
log_level: "warn"  # Reduce verbose logging
```

## Environment Variables

Set these environment variables in your production deployment:

```bash
TRAINLOOP_DATA_FOLDER=/path/to/your/data/directory
TRAINLOOP_LOG_LEVEL=warn
```

## Coming Soon

More detailed production guidance including:
- CI/CD integration patterns
- Data retention strategies  
- Monitoring recommendations
- Scaling considerations

## Next Steps

- Review the [reference documentation](../reference/index.md) for configuration details
- Check the [examples](../examples/) for production-ready code samples
- Explore the [guides](../guides/) for specific implementation patterns