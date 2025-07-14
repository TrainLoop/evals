---
sidebar_position: 1
---

# CLI Overview

The TrainLoop CLI provides four main commands for managing your evaluation workflow. This page provides a comprehensive reference for all CLI commands and options.

## Core Commands

### `trainloop init`

Scaffolds data/ and eval/ directories, creates sample metrics and suites.

```bash
trainloop init
```

This command creates a `trainloop/` workspace with the following structure:
- `trainloop/data/` - Where event and result data is stored
- `trainloop/eval/` - Where metrics and test suites are defined
- `trainloop.config.yaml` - Configuration file

**What it creates:**
- Sample metrics for common evaluation patterns
- Example test suites demonstrating best practices
- Configuration file with sensible defaults
- Directory structure for organizing evaluation data

See the [scaffold template documentation](../../getting-started/quick-start.md) for more details.

### `trainloop eval`

Discovers suites, applies metrics to new events, and appends verdicts to `data/results/`. If the LLM judge is used, it automatically consolidates all trace events for the run into a single timestamped JSONL file in `trainloop/data/judge_traces/`.

```bash
trainloop eval [OPTIONS]
```

**Options:**
- `--suite <suite_name>` - Run only the specified suite instead of all suites
- `--config <path>` - Path to trainloop config file (overrides auto-discovery)
- `--data-folder <path>` - Override data folder location
- `--verbose` - Enable verbose output for debugging

**Examples:**
```bash
# Run all evaluation suites
trainloop eval

# Run only a specific suite
trainloop eval --suite my_test_suite

# Use custom config file
trainloop eval --config /path/to/custom.yaml

# Run with verbose output
trainloop eval --verbose
```

**Behavior:**
1. Discovers all Python modules in `trainloop/eval/`
2. Identifies metrics and test suites
3. Reads new events from `trainloop/data/events/`
4. Applies metrics to events
5. Saves results to `trainloop/data/results/`
6. If LLM judge is used, saves traces to `trainloop/data/judge_traces/`

### `trainloop add`

Adds pre-built metrics and suites from the TrainLoop registry to your project. Components are defined with Python-based `config.py` files for type safety and dynamic discovery.

```bash
trainloop add [metric|suite] [NAME] [OPTIONS]
```

**Options:**
- `--list` - List available metrics and/or suites
- `--registry <path>` - Use a local directory as the registry (for development)
- `--force` - Overwrite existing files without prompting

**Examples:**
```bash
# List all available metrics and suites
trainloop add --list

# List available metrics
trainloop add metric --list

# List available suites  
trainloop add suite --list

# Add a specific metric
trainloop add metric always_pass

# Add a specific suite
trainloop add suite basic_qa

# Add a metric from a local registry path
trainloop add --registry ../my-local-registry metric custom_metric

# Force overwrite existing files
trainloop add metric response_quality --force
```

**Registry Structure:**
The registry contains reusable components:
- **Metrics**: Individual evaluation functions
- **Suites**: Collections of metrics for specific use cases
- **Utilities**: Helper functions and common patterns

### `trainloop studio`

Launches the TrainLoop Studio UI for visualizing and analyzing your evaluation data.

```bash
trainloop studio [OPTIONS]
```

**Options:**
- `--config <path>` - Path to the trainloop config file (overrides auto-discovery)
- `--local <path>` - Path to a local studio tar file (for development)
- `--port <number>` - Port to run the server on (default: 3000)
- `--host <address>` - Host address to bind to (default: localhost)

**Examples:**
```bash
# Launch studio with auto-discovery (default behavior)
trainloop studio

# Use a custom config file
trainloop studio --config /alt/path/to/trainloop.config.yaml

# Run on a different port
trainloop studio --port 8080

# Use a local development build of Studio
trainloop studio --local /path/to/your/trainloop-studio-runner.tgz

# Combine options
trainloop studio --config /custom/config.yaml --port 8080
```

**Features:**
- Interactive data visualization with DuckDB
- Event timeline and result analysis
- Metric performance tracking
- Benchmark comparison views
- Export capabilities for further analysis

## Global Options

These options work with all commands:

- `--help` - Show help information
- `--version` - Show version information
- `--quiet` - Suppress non-essential output
- `--config <path>` - Specify config file location

## Configuration

### Environment Variables

- `TRAINLOOP_DATA_FOLDER` - Override default data folder location
- `TRAINLOOP_CONFIG_PATH` - Override default config file location
- `TRAINLOOP_LOG_LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)

### Config File Discovery

The CLI automatically discovers config files in this order:
1. `--config` command line argument
2. `TRAINLOOP_CONFIG_PATH` environment variable
3. `trainloop.config.yaml` in current directory
4. `trainloop/trainloop.config.yaml` in current directory
5. Search parent directories for `trainloop.config.yaml`

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Data error (missing events, invalid format)
- `4` - Evaluation error (metric failures)
- `5` - Network error (registry, LLM API)

## Troubleshooting

### Common Issues

**Config file not found:**
```bash
# Verify config file location
trainloop eval --config /path/to/config.yaml --verbose
```

**No events to evaluate:**
```bash
# Check data folder contents
ls trainloop/data/events/

# Verify environment variable
echo $TRAINLOOP_DATA_FOLDER
```

**Module import errors:**
```bash
# Run from project root
cd /path/to/your/project
trainloop eval

# Check Python path
python -c "import sys; print(sys.path)"
```

**Studio won't start:**
```bash
# Check port availability
trainloop studio --port 8080

# Use local build for development
trainloop studio --local /path/to/studio.tgz
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Set log level
export TRAINLOOP_LOG_LEVEL=DEBUG
trainloop eval --verbose

# Or use config file
trainloop eval --config debug.yaml --verbose
```

### Getting Help

For more help:
- Use `trainloop <command> --help` for command-specific help
- Visit [GitHub Discussions](https://github.com/trainloop/evals/discussions)
- Open an issue on [GitHub](https://github.com/trainloop/evals/issues)