---
sidebar_position: 7
---

# Configuration

TrainLoop CLI configuration file format and options.

## Configuration File

TrainLoop uses `trainloop.config.yaml` for configuration. A minimal configuration looks like:

```yaml
# trainloop.config.yaml
trainloop:
  data_folder: "./data"
  project: "my-evals"
```

## Configuration Discovery

The CLI searches for configuration files in this order:

1. `--config` command line argument
2. `TRAINLOOP_CONFIG_FILE` environment variable  
3. `trainloop.config.yaml` in current directory
4. `trainloop/trainloop.config.yaml` in current directory
5. Same search repeated in parent directories (up to git root)
6. `~/.trainloop/config.yaml` in home directory

Values in files found later override those found earlier.

## Complete Configuration Reference

```yaml
trainloop:
  # Basic settings
  project: "my-project"
  data_folder: "./data"
  log_level: "info"  # debug, info, warn, error
  
  # Host filtering for SDK instrumentation (optional)
  # Overrides the default allowlist when specified
  host_allowlist:
    - api.openai.com
    - api.anthropic.com
    - generativelanguage.googleapis.com
    - api.cohere.ai
    - api.groq.com
    - api.mistral.ai
    - api.together.xyz
    - api.endpoints.anyscale.com
    - api.perplexity.ai
    - api.deepinfra.com
    - api.replicate.com
    - api-inference.huggingface.co
    - openai.azure.com
  
  # Data retention (days)
  data_retention:
    events: 30
    results: 90
    judge_traces: 7
  
  # Performance settings
  performance:
    batch_size: 1000
    max_concurrent_evaluations: 10
    evaluation_timeout: 300
    cache_enabled: true
  
  # LLM Judge configuration
  judge:
    models:
      - openai/gpt-4o-mini
      - anthropic/claude-3-haiku-20240307
    calls_per_model_per_claim: 2
    temperature: 0.1
    max_tokens: 100
    timeout: 30
    
  # Benchmarking configuration
  benchmark:
    providers:
      - provider: openai
        model: gpt-4o
        temperature: 0.7
        max_tokens: 1000
      - provider: openai
        model: gpt-4o-mini
        temperature: 0.7
        max_tokens: 1000
      - provider: anthropic
        model: claude-3-5-sonnet-20241022
        temperature: 0.7
        max_tokens: 1000
    
    # Optional benchmark settings
    max_samples: 1000
    parallel_requests: 5
    timeout: 30
    cost_limit: 50.00
    
  # Studio UI configuration
  studio:
    port: 3000
    host: "localhost"
    auto_refresh: true
    theme: "light"  # light, dark, auto
    
  # Monitoring and alerting
  monitoring:
    enabled: false
    metrics_endpoint: "http://localhost:9090"
    alert_threshold: 0.7
    
  # Security settings
  security:
    encrypt_events: false
    anonymize_data: false
    retention_policy: "standard"
```

## Environment-Specific Configurations

### Development

```yaml
# trainloop.config.yaml (development)
trainloop:
  data_folder: "./dev-data"
  log_level: "debug"
  
  judge:
    models:
      - openai/gpt-4o-mini  # Cheaper for development
    calls_per_model_per_claim: 1
    
  benchmark:
    max_samples: 10  # Small samples for testing
    parallel_requests: 2
```

### Production

```yaml
# trainloop.config.yaml (production)
trainloop:
  data_folder: "/var/lib/trainloop/data"
  log_level: "info"
  
  data_retention:
    events: 90
    results: 365
    
  performance:
    batch_size: 5000
    max_concurrent_evaluations: 20
    
  judge:
    models:
      - openai/gpt-4o
      - anthropic/claude-3-5-sonnet-20241022
    calls_per_model_per_claim: 3
    
  monitoring:
    enabled: true
    metrics_endpoint: "http://prometheus:9090"
```

### CI/CD

```yaml
# ci.config.yaml
trainloop:
  data_folder: "/tmp/trainloop-ci"
  log_level: "warn"
  
  judge:
    models:
      - openai/gpt-4o-mini
    calls_per_model_per_claim: 1
    timeout: 15
    
  benchmark:
    max_samples: 50
    parallel_requests: 3
    timeout: 10
```

## Configuration Validation

Validate your configuration:

```bash
# Check configuration
trainloop config --validate

# Show current configuration
trainloop config --show

# Show configuration sources
trainloop config --show-sources
```

## Environment Variables

Override configuration with environment variables:

```bash
# Override data folder
export TRAINLOOP_DATA_FOLDER="/custom/data/path"

# Override log level
export TRAINLOOP_LOG_LEVEL="debug"

# Override judge models
export TRAINLOOP_JUDGE_MODELS="openai/gpt-4o-mini,anthropic/claude-3-haiku"
```

## Best Practices

### 1. Environment-Specific Files

```bash
# Use different configs for different environments
trainloop eval --config production.config.yaml
trainloop eval --config development.config.yaml
trainloop eval --config ci.config.yaml
```

### 2. Sensitive Data

```yaml
# Don't put API keys in config files
# Use environment variables instead
trainloop:
  judge:
    models:
      - openai/gpt-4o
    # API keys from environment: OPENAI_API_KEY
```

### 3. Version Control

```bash
# Include in version control
git add trainloop.config.yaml

# But exclude environment-specific ones
echo "*.local.config.yaml" >> .gitignore
```

## See Also

- [Environment Variables](env-vars.md) - Environment variable reference
- [Architecture](../../explanation/architecture.md) - How configuration fits into the system
- [Production Setup](../../tutorials/production-setup.md) - Production configuration examples