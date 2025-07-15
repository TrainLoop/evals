---
sidebar_position: 1
---

# Reference

Complete API reference and technical documentation for TrainLoop Evals.

## Overview

This reference section provides comprehensive technical documentation for all TrainLoop Evals components. Use this section to find detailed information about APIs, configuration options, and data formats.

## Quick Navigation

### Command Line Interface

- **[CLI Overview](cli/index.md)** - Complete command reference
- **[trainloop init](cli/init.md)** - Initialize projects
- **[trainloop eval](cli/eval.md)** - Run evaluations
- **[trainloop studio](cli/studio.md)** - Launch Studio UI
- **[trainloop add](cli/add.md)** - Add registry components
- **[trainloop benchmark](cli/benchmark.md)** - Compare models
- **[Configuration](cli/config.md)** - YAML configuration reference
- **[Environment Variables](cli/env-vars.md)** - Environment variable reference

### SDKs

- **[SDK Overview](sdk/index.md)** - Multi-language SDK documentation
- **[Python SDK](sdk/python/api.md)** - Python API reference
- **[TypeScript SDK](sdk/typescript/api.md)** - TypeScript/JavaScript API reference
- **[Go SDK](sdk/go/api.md)** - Go API reference

### Data Formats

- **[Data Formats Overview](data-formats/index.md)** - Data format documentation
- **[Event Data](data-formats/events.md)** - LLM interaction data schema
- **[Results Data](data-formats/results.md)** - Evaluation results schema

## Component Overview

### TrainLoop CLI

The command-line interface provides:
- Project initialization and scaffolding
- Evaluation execution and management
- Studio UI launching and configuration
- Registry component management
- Model benchmarking and comparison

### TrainLoop SDKs

Zero-touch instrumentation libraries for:
- **Python**: `trainloop-llm-logging` package
- **TypeScript/JavaScript**: `trainloop-llm-logging` npm package
- **Go**: `trainloop-llm-logging` module

### Data Pipeline

TrainLoop processes data through these stages:
1. **Collection** - SDKs capture LLM interactions
2. **Storage** - Events saved as JSONL files
3. **Evaluation** - CLI applies metrics to events
4. **Analysis** - Studio UI provides visualization

## API Patterns

### Consistent Interfaces

All TrainLoop components follow consistent patterns:

```python
# Python SDK
collect(config_path)
trainloop_tag("tag-name")
```

```bash
# CLI commands
trainloop init
trainloop eval --suite my-suite
trainloop studio --port 8080
```

```javascript
// TypeScript SDK
trainloopTag("tag-name")
```

### Configuration

All components use consistent configuration:

```yaml
# trainloop.config.yaml
trainloop:
  data_folder: "./data"
  log_level: "info"
  
  judge:
    models: ["openai/gpt-4o-mini"]
    
  benchmark:
    providers: ["openai/gpt-4o", "anthropic/claude-3-sonnet"]
```

### Error Handling

All components use consistent error handling:

```python
# Python - graceful degradation
try:
    collect()
except Exception as e:
    logger.warning(f"TrainLoop initialization failed: {e}")
    # Continue without instrumentation
```

## Integration Examples

### Basic Workflow

```bash
# 1. Initialize project
trainloop init

# 2. Set up environment
export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"
export OPENAI_API_KEY="your-key"

# 3. Run instrumented application
python your_app.py

# 4. Run evaluation
trainloop eval

# 5. View results
trainloop studio
```

### CI/CD Integration

```yaml
# .github/workflows/eval.yml
- name: Run evaluations
  run: |
    trainloop eval --config ci.config.yaml
    trainloop benchmark --max-samples 50
```

### Production Deployment

```dockerfile
# Dockerfile
FROM python:3.11
RUN pip install trainloop-cli
CMD ["trainloop", "studio", "--host", "0.0.0.0"]
```

## Performance Considerations

### SDK Performance

- **Buffering**: Events are buffered for efficient I/O
- **Async logging**: Non-blocking data collection
- **Memory usage**: Configurable buffer sizes

### CLI Performance

- **Parallel processing**: Multiple evaluation processes
- **Caching**: Results cached to avoid re-evaluation
- **Incremental processing**: Only process new events

### Data Volume

- **Event size**: Typical event is 1-5KB
- **Storage growth**: Plan for ~1MB per 1000 events
- **Retention**: Configure automatic cleanup

## Security Considerations

### Data Protection

- **Encryption**: Optional encryption at rest
- **Access control**: File-based permissions
- **Audit logging**: All operations logged

### API Security

- **Key management**: Secure API key storage
- **Rate limiting**: Respect provider limits
- **Error handling**: No sensitive data in logs

## Versioning and Compatibility

### Semantic Versioning

TrainLoop Evals follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes

### Compatibility

- **Data formats**: Backward compatible
- **API interfaces**: Deprecated features marked
- **Migration tools**: Automatic data migration

## Getting Help

### Documentation

- **[Tutorials](../tutorials/index.md)** - Step-by-step learning
- **[How-to Guides](../guides/)** - Problem-solving guides
- **[Explanation](../explanation/index.md)** - Conceptual information

### Community

- **[GitHub Issues](https://github.com/trainloop/evals/issues)** - Bug reports and feature requests
- **[Discussions](https://github.com/trainloop/evals/discussions)** - Community questions
- **[Contributing](https://github.com/trainloop/evals/blob/main/CONTRIBUTING.md)** - How to contribute

## See Also

- [Architecture](../explanation/concepts/architecture.md) - System architecture overview
- [Getting Started](../tutorials/getting-started.md) - Quick start guide
- [Production Setup](../tutorials/production-setup.md) - Deployment guide