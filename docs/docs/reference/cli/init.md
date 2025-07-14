---
sidebar_position: 2
---

# trainloop init

Initialize a new TrainLoop project by creating the workspace structure and installing dependencies.

## Synopsis

```bash
trainloop init [OPTIONS]
```

## Description

The `trainloop init` command scaffolds a new TrainLoop evaluation project by creating the necessary directory structure, example files, and Python virtual environment.

## Options

| Option | Description |
|--------|-------------|
| `--force` | Overwrite any existing `trainloop/` directory |
| `--no-venv` | Skip creating Python virtual environment |
| `--template <name>` | Use a specific project template |
| `--help` | Show help message |

## What Gets Created

When you run `trainloop init`, the following structure is created:

```
trainloop/
├── .venv/                      # Python virtual environment
├── data/                       # Data storage (auto-created)
│   ├── events/                 # Raw LLM interaction data
│   └── results/                # Evaluation results
├── eval/                       # Evaluation code
│   ├── __init__.py
│   ├── metrics/                # Custom metrics
│   │   ├── __init__.py
│   │   └── example_metrics.py  # Example metric implementations
│   └── suites/                 # Test suites
│       ├── __init__.py
│       └── example_suite.py    # Example test suite
├── trainloop.config.yaml       # Configuration file
├── .env.example               # Environment variable template
└── requirements.txt           # Python dependencies
```

## Examples

### Basic Initialization

```bash
# Create new project in current directory
trainloop init
```

### Force Overwrite

```bash
# Overwrite existing trainloop/ directory
trainloop init --force
```

### Skip Virtual Environment

```bash
# Initialize without creating Python virtual environment
trainloop init --no-venv
```

### Use Template

```bash
# Initialize with specific template
trainloop init --template customer-support
```

## Generated Files

### Configuration File (`trainloop.config.yaml`)

```yaml
trainloop:
  data_folder: "./data"
  log_level: "info"
  
  # LLM Judge configuration
  judge:
    models:
      - openai/gpt-4o-mini
      - anthropic/claude-3-haiku-20240307
    calls_per_model_per_claim: 2
    temperature: 0.1
    
  # Benchmark configuration
  benchmark:
    providers:
      - openai/gpt-4o
      - openai/gpt-4o-mini
      - anthropic/claude-3-5-sonnet-20241022
    temperature: 0.7
    max_tokens: 1000
```

### Example Metric (`eval/metrics/example_metrics.py`)

```python
from trainloop_cli.eval_core.types import Sample

def has_greeting(sample: Sample) -> int:
    """Check if response contains a greeting"""
    response = sample.output.get("content", "").lower()
    greetings = ["hello", "hi", "greetings", "good morning", "good afternoon"]
    return 1 if any(greeting in response for greeting in greetings) else 0

def appropriate_length(sample: Sample) -> int:
    """Check if response length is appropriate"""
    response = sample.output.get("content", "")
    word_count = len(response.split())
    return 1 if 10 <= word_count <= 200 else 0
```

### Example Suite (`eval/suites/example_suite.py`)

```python
from trainloop_cli.eval_core.helpers import tag
from ..metrics.example_metrics import has_greeting, appropriate_length

# Evaluate all collected data
results = tag("").check(
    has_greeting,
    appropriate_length
)
```

### Environment Variables Template (`.env.example`)

```bash
# LLM API Keys
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# TrainLoop Configuration
TRAINLOOP_DATA_FOLDER=./trainloop/data
TRAINLOOP_LOG_LEVEL=info
```

## Available Templates

| Template | Description |
|----------|-------------|
| `default` | Basic setup with example metrics |
| `customer-support` | Customer service evaluation templates |
| `content-generation` | Content quality evaluation templates |
| `question-answering` | QA system evaluation templates |
| `code-generation` | Code generation evaluation templates |

## Virtual Environment

By default, `trainloop init` creates a Python virtual environment in `trainloop/.venv/` with the TrainLoop CLI installed. To activate it:

```bash
# Activate virtual environment
source trainloop/.venv/bin/activate

# Verify installation
trainloop --version

# Deactivate when done
deactivate
```

## Next Steps

After running `trainloop init`:

1. **Set up environment variables**:
   ```bash
   cp trainloop/.env.example trainloop/.env
   # Edit trainloop/.env with your API keys
   ```

2. **Configure data collection**:
   ```bash
   export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"
   ```

3. **Install SDK in your application** (see [SDK documentation](../sdk/index.md))

4. **Run your application** to collect data

5. **Run evaluations**:
   ```bash
   trainloop eval
   ```

6. **View results**:
   ```bash
   trainloop studio
   ```

## Common Issues

### Permission Errors

```bash
# If you get permission errors, try:
sudo chown -R $USER:$USER trainloop/
```

### Python Virtual Environment Issues

```bash
# If virtual environment creation fails:
trainloop init --no-venv
pip install trainloop-cli
```

### Directory Already Exists

```bash
# If trainloop/ already exists:
trainloop init --force
```

## See Also

- [eval](eval.md) - Run evaluation suites
- [studio](studio.md) - Launch Studio UI
- [Configuration](config.md) - Configure TrainLoop behavior
- [SDK Reference](../sdk/index.md) - Instrument your application