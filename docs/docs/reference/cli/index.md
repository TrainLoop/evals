---
sidebar_position: 1
---

# CLI Reference

The TrainLoop CLI (`trainloop`) is the command-line interface for running evaluations, managing projects, and interacting with the TrainLoop Evals system.

## Installation

```bash
# Install via pip
pip install trainloop-cli

# Verify installation
trainloop --version
```

## Global Options

These options work with all commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help information |
| `--version` | Show version information |
| `--config <path>` | Path to configuration file (default: `trainloop.config.yaml`) |
| `--data-folder <path>` | Override data folder location |
| `--verbose` | Enable verbose output for debugging |
| `--quiet` | Suppress non-essential output |

## Environment Variables

The CLI respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TRAINLOOP_DATA_FOLDER` | Data storage location | `./trainloop/data` |
| `TRAINLOOP_CONFIG_FILE` | Configuration file path | `trainloop.config.yaml` |
| `TRAINLOOP_LOG_LEVEL` | Log level (debug, info, warn, error) | `info` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

## Commands

### Core Commands

| Command | Description |
|---------|-------------|
| [`init`](init.md) | Initialize a new TrainLoop project |
| [`eval`](eval.md) | Run evaluation suites |
| [`studio`](studio.md) | Launch the Studio UI |
| [`add`](add.md) | Add components from the registry |
| [`benchmark`](benchmark.md) | Compare LLM providers |

### Configuration

| Command | Description |
|---------|-------------|
| [`config`](config.md) | Configuration file format and options |
| [`env-vars`](env-vars.md) | Environment variable reference |

## Quick Examples

```bash
# Initialize a new project
trainloop init

# Run all evaluation suites
trainloop eval

# Run specific suite
trainloop eval --suite my-suite

# Launch Studio UI
trainloop studio

# Add a metric from registry
trainloop add metric accuracy

# Run benchmark
trainloop benchmark
```

## Configuration Discovery

The CLI searches for configuration files in this order:

1. `--config` command line argument
2. `TRAINLOOP_CONFIG_FILE` environment variable
3. `trainloop.config.yaml` in current directory
4. `trainloop.config.yaml` in parent directories (up to git root)
5. `~/.trainloop/config.yaml` in home directory
6. Default configuration

## Error Handling

The CLI returns these exit codes:

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Configuration error |
| `4` | API error |
| `5` | Evaluation failure |

## Getting Help

```bash
# General help
trainloop --help

# Command-specific help
trainloop eval --help

# Show version
trainloop --version
```

## Common Usage Patterns

### Development Workflow

```bash
# 1. Initialize project
trainloop init

# 2. Set up data collection (see SDK docs)
export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"

# 3. Run your application to collect data
python your_app.py

# 4. Run evaluations
trainloop eval

# 5. View results
trainloop studio
```

### CI/CD Integration

```bash
# Run evaluations in CI
trainloop eval --config ci.config.yaml --verbose

# Check if evaluations pass
if trainloop eval --quiet; then
    echo "Evaluations passed"
else
    echo "Evaluations failed"
    exit 1
fi
```

### Benchmarking Workflow

```bash
# Set up benchmark configuration
trainloop config benchmark --models gpt-4o,claude-3-sonnet

# Run benchmark
trainloop benchmark --max-samples 100

# View results
trainloop studio
```

## Next Steps

- [Initialize a project](init.md) - Set up your first TrainLoop project
- [Run evaluations](eval.md) - Execute your evaluation suites
- [Launch Studio UI](studio.md) - Visualize your results
- [Configuration guide](config.md) - Configure TrainLoop behavior