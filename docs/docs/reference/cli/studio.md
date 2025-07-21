---
sidebar_position: 4
---

# trainloop studio

Launch the Studio UI web interface for interactive visualization and analysis of evaluation results.

## Synopsis

```bash
trainloop studio [OPTIONS]
```

## Description

The `trainloop studio` command starts a local web server that provides an interactive interface for exploring evaluation results, comparing models, and analyzing LLM performance data.

## Options

| Option | Description |
|--------|-------------|
| `--port <number>` | HTTP port (default: 3000) |
| `--host <address>` | Host binding address (default: localhost) |
| `--config <path>` | Path to configuration file |
| `--local <tar>` | Path to local Studio build (for development) |
| `--help` | Show help message |

## Examples

### Basic Usage

```bash
# Start Studio UI on default port 3000
trainloop studio
```

### Custom Port

```bash
# Start on port 8080
trainloop studio --port 8080
```

### Custom Host

```bash
# Bind to all interfaces (for Docker/remote access)
trainloop studio --host 0.0.0.0
```

### Development Mode

```bash
# Use local build for development
trainloop studio --local trainloop-studio-runner.tgz
```

## What You'll See

The Studio UI provides several key interfaces:

### Dashboard
- Overview of evaluation results
- Summary statistics and trends
- Recent evaluation runs

### Results Explorer
- Interactive tables of evaluation results
- Filtering and search capabilities
- Drill-down to individual events

### Benchmarks
- Model comparison charts
- Performance vs. cost analysis
- Side-by-side result comparison

### Event Browser
- Raw LLM request/response data
- Tagged event exploration
- Data quality inspection

## Data Requirements

Studio UI requires:
- **Event data**: JSONL files in `data/events/`
- **Results data**: JSON files in `data/results/`
- **Valid configuration**: Accessible `trainloop.config.yaml`

## Configuration

Studio UI uses the same [configuration discovery](config.md) as other CLI commands:

1. `--config` command line argument
2. `TRAINLOOP_CONFIG_FILE` environment variable
3. `trainloop.config.yaml` in current directory
4. Parent directories up to git root
5. `~/.trainloop/config.yaml`

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Use different port
trainloop studio --port 8080
```

#### No Data Showing
1. Check data folder exists: `ls $TRAINLOOP_DATA_FOLDER`
2. Verify results exist: `ls $TRAINLOOP_DATA_FOLDER/results/`
3. Run evaluations: `trainloop eval`

#### Can't Access from Remote
```bash
# Allow external access
trainloop studio --host 0.0.0.0 --port 3000
```

## Production Deployment

For production use, consider:

```bash
# Secure external access
trainloop studio --host 0.0.0.0 --port 3000

# Use reverse proxy (nginx, Apache)
# Set up authentication
# Configure SSL/TLS
```

## See Also

- [eval](eval.md) - Generate data for Studio UI
- [Configuration](config.md) - Configure Studio behavior
- [Architecture](../../explanation/architecture.md) - How Studio UI fits into the system