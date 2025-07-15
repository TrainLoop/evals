---
sidebar_position: 5
---

# trainloop add

Add reusable metrics and suites from the TrainLoop registry to your project.

## Synopsis

```bash
trainloop add [OPTIONS] <TYPE> <NAME>
```

## Description

The `trainloop add` command downloads and installs pre-built evaluation components from the TrainLoop registry. This allows you to quickly add common metrics and evaluation suites to your project.

## Arguments

| Argument | Description |
|----------|-------------|
| `<TYPE>` | Component type: `metric` or `suite` |
| `<NAME>` | Name of the component to add |

## Options

| Option | Description |
|--------|-------------|
| `--list` | List available components |
| `--force` | Overwrite existing files |
| `--registry <path>` | Use local registry directory |
| `--version <tag>` | Pull from specific CLI version |
| `--help` | Show help message |

## Examples

### List Available Components

```bash
# List all available components
trainloop add --list

# List specific component type
trainloop add metric --list
trainloop add suite --list
```

### Add Components

```bash
# Add a metric
trainloop add metric always_pass

# Add a suite
trainloop add suite sample_evaluation

# Force overwrite existing files
trainloop add metric accuracy --force
```

### Development Usage

```bash
# Use local registry for development
trainloop add --registry ../my-registry metric custom_metric

# Use specific version
trainloop add --version v1.2.0 metric helpful_check
```

## Available Components

### Metrics

| Name | Description |
|------|-------------|
| `always_pass` | Always returns 1 (for testing) |
| `always_fail` | Always returns 0 (for testing) |
| `not_empty` | Checks if response is not empty |
| `min_length` | Checks minimum response length |
| `max_length` | Checks maximum response length |
| `contains_keywords` | Checks for specific keywords |
| `no_profanity` | Checks for inappropriate content |
| `helpful_check` | LLM Judge helpfulness evaluation |
| `accuracy_check` | LLM Judge accuracy evaluation |

### Suites

| Name | Description |
|------|-------------|
| `sample` | Basic evaluation suite example |
| `quality_check` | Comprehensive quality evaluation |
| `safety_review` | Safety and appropriateness checks |
| `customer_support` | Customer service evaluation |
| `content_generation` | Content quality evaluation |

## How It Works

1. **Download**: Component is downloaded from registry
2. **Install**: Files are copied to `trainloop/eval/metrics/` or `trainloop/eval/suites/`
3. **Customize**: You can modify the installed files as needed

## File Structure

After adding components, your project structure looks like:

```
trainloop/
├── eval/
│   ├── metrics/
│   │   ├── always_pass.py        # Added metric
│   │   └── helpful_check.py      # Added metric
│   └── suites/
│       ├── sample.py             # Added suite
│       └── quality_check.py      # Added suite
```

## Registry System

### Public Registry

The default registry contains community-maintained components:
- Hosted on GitHub
- Versioned with CLI releases
- Peer-reviewed for quality

### Local Registry

For development or private components:

```bash
# Set up local registry
mkdir my-registry
cd my-registry
# Add your metrics and suites

# Use with trainloop add
trainloop add --registry ./my-registry metric my_custom_metric
```

## Customization

After adding components, you can customize them:

```python
# trainloop/eval/metrics/helpful_check.py (after adding)
from trainloop_cli.eval_core.types import Sample
from trainloop_cli.eval_core.judge import assert_true

def helpful_check(sample: Sample) -> int:
    """Check if response is helpful (customize as needed)"""
    response = sample.output.get("content", "")
    
    # Customize these claims for your use case
    positive_claim = f"The response '{response}' is helpful and informative."
    negative_claim = f"The response '{response}' is not helpful or informative."
    
    return assert_true(positive_claim, negative_claim)
```

## Best Practices

### 1. Start with Registry Components

```bash
# Begin with proven components
trainloop add metric helpful_check
trainloop add suite quality_check

# Then customize for your needs
```

### 2. Review Before Using

```bash
# Add component
trainloop add metric accuracy_check

# Review the code
cat trainloop/eval/metrics/accuracy_check.py

# Test before using in production
trainloop eval --suite test_suite
```

### 3. Version Management

```bash
# Pin to specific version for stability
trainloop add --version v1.0.0 metric core_quality

# Update to latest when ready
trainloop add --force metric core_quality
```

## Troubleshooting

### Component Not Found

```bash
# Check available components
trainloop add --list

# Check spelling and try again
trainloop add metric helpful_check
```

### File Already Exists

```bash
# Use --force to overwrite
trainloop add metric accuracy --force

# Or rename existing file first
mv trainloop/eval/metrics/accuracy.py trainloop/eval/metrics/accuracy_old.py
trainloop add metric accuracy
```

### Registry Connection Issues

```bash
# Use local registry as fallback
trainloop add --registry ./local-registry metric my_metric

# Check network connectivity
ping github.com
```

## Contributing to Registry

To contribute components to the public registry:

1. Follow the [contribution guidelines](https://github.com/trainloop/evals/blob/main/CONTRIBUTING.md)
2. Test components thoroughly
3. Document usage and examples
4. Submit pull request

## See Also

- [Tutorials](../../tutorials/index.md) - Learn to write custom metrics
- [Registry Documentation](../registry/index.md) - Registry system details
- [Contributing Guide](https://github.com/trainloop/evals/blob/main/CONTRIBUTING.md) - How to contribute components