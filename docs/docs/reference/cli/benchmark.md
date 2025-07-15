---
sidebar_position: 6
---

# trainloop benchmark

Compare multiple LLM providers by re-running prompts and evaluating results with the same metrics.

## Synopsis

```bash
trainloop benchmark [OPTIONS]
```

## Description

The `trainloop benchmark` command takes your existing event data and re-runs the same prompts against multiple LLM providers configured in your settings. It then applies your evaluation metrics to all responses, enabling direct comparison of model performance.

## Options

| Option | Description |
|--------|-------------|
| `--config <path>` | Path to configuration file |
| `--max-samples <number>` | Limit number of samples per provider |
| `--tag <name>` | Only benchmark events with specific tag |
| `--providers <list>` | Comma-separated list of providers to test |
| `--output <path>` | Output directory for results |
| `--verbose` | Enable verbose output |
| `--help` | Show help message |

## Examples

### Basic Benchmarking

```bash
# Run benchmark with configured providers
trainloop benchmark
```

### Limited Sampling

```bash
# Test with only 100 samples per provider
trainloop benchmark --max-samples 100
```

### Specific Tags

```bash
# Only benchmark greeting generation
trainloop benchmark --tag greeting-generation
```

### Custom Providers

```bash
# Test specific providers
trainloop benchmark --providers openai/gpt-4o,anthropic/claude-3-sonnet
```

## Configuration

Configure benchmark providers in `trainloop.config.yaml`:

```yaml
trainloop:
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
    
    # Optional settings
    max_samples: 1000
    parallel_requests: 5
    timeout: 30
```

## How It Works

1. **Sample Selection**: Selects events from your data based on tags/filters
2. **Provider Execution**: Re-runs prompts against each configured provider
3. **Metric Application**: Applies your existing metrics to all responses
4. **Result Generation**: Creates comparison data with performance statistics
5. **Visualization**: Results viewable in Studio UI

## Output

### Console Output

```
🔍 Starting benchmark with 3 providers...
📊 Selected 150 events for benchmarking

🚀 Running prompts against providers:
✅ openai/gpt-4o: 150/150 completed (avg: 1.2s)
✅ openai/gpt-4o-mini: 150/150 completed (avg: 0.8s)
✅ anthropic/claude-3-5-sonnet: 150/150 completed (avg: 1.5s)

📈 Applying metrics to results...
✅ helpful_check: Applied to 450 responses
✅ accuracy_check: Applied to 450 responses
✅ safety_check: Applied to 450 responses

💾 Benchmark results saved to data/benchmarks/2024-01-15_14-30-25/
```

### Results Structure

```
data/
├── benchmarks/
│   └── 2024-01-15_14-30-25/
│       ├── benchmark_results.json     # Main results
│       ├── provider_comparison.json   # Provider stats
│       └── detailed_results.jsonl     # Individual responses
```

### Results Content

```json
{
  "timestamp": "2024-01-15T14:30:25Z",
  "providers": ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3-5-sonnet"],
  "total_samples": 150,
  "metrics": {
    "helpful_check": {
      "openai/gpt-4o": {"score": 0.85, "passed": 128, "total": 150},
      "openai/gpt-4o-mini": {"score": 0.82, "passed": 123, "total": 150},
      "anthropic/claude-3-5-sonnet": {"score": 0.88, "passed": 132, "total": 150}
    }
  },
  "cost_analysis": {
    "openai/gpt-4o": {"total_cost": 4.50, "cost_per_token": 0.015},
    "openai/gpt-4o-mini": {"total_cost": 0.30, "cost_per_token": 0.001}
  }
}
```

## Analysis in Studio UI

After benchmarking, use Studio UI to analyze results:

```bash
trainloop studio
```

Features available:
- **Performance comparison charts**
- **Cost vs. quality analysis**
- **Individual response comparison**
- **Metric breakdown by provider**
- **Statistical significance testing**

## Best Practices

### 1. Representative Sampling

```bash
# Use sufficient samples for statistical significance
trainloop benchmark --max-samples 500

# Include diverse event types
trainloop benchmark --tag "" # All events
```

### 2. Consistent Configuration

```yaml
# Use same temperature/settings across providers
benchmark:
  providers:
    - provider: openai
      model: gpt-4o
      temperature: 0.7  # Same across all
    - provider: anthropic
      model: claude-3-sonnet
      temperature: 0.7  # Same across all
```

### 3. Cost Management

```bash
# Start with small samples
trainloop benchmark --max-samples 50

# Monitor costs in configuration
benchmark:
  cost_limit: 10.00  # Stop at $10
```

## Troubleshooting

### API Rate Limits

```bash
# Reduce parallel requests
trainloop benchmark --parallel 2

# Add delays between requests
trainloop benchmark --delay 1.0
```

### Insufficient Data

```bash
# Check available events
ls data/events/

# Verify tags exist
trainloop eval --dry-run
```

### Provider Errors

```bash
# Test individual provider
trainloop benchmark --providers openai/gpt-4o

# Check API keys
env | grep API_KEY
```

## See Also

- [Benchmarking Tutorial](../../tutorials/benchmarking.md) - Complete benchmarking guide
- [Configuration](config.md) - Configure benchmark settings
- [Studio UI](studio.md) - Analyze benchmark results