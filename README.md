# 🤖📊 TrainLoop Evals (ALPHA)

TrainLoop Evals is a framework for automating the collection and evaluation of LLM outputs. The core tenants of this are

- *Simplicity First* – one environment variable, one function call, one folder of JSON files.
- *Vendor Independence* – everything stored as newline-delimited JSON; no databases required.
- *Meet developers where they are* – accepts our simple declarative flow or existing bespoke loops.
- *Type-safe, In-code Tests* – all code present in codebase
- *Composable, Extensible System* – helper generators mimic shadcn patterns. (`trainloop add` coming soon!)

<p align="center">
  <img src="images/drake_evals.png" alt="Evals Meme" width="400" height="auto" />
</p>

## Demo

- Demo repo: https://github.com/TrainLoop/chat-ui-demo
- Demo deployment: https://evals.trainloop.ai


## Getting started

### Prerequisites

We rely on `pipx` to install the CLI. If you don't have it, follow the [instructions](https://pipx.pypa.io/stable/).

### Installation

Install the TrainLoop CLI using pipx:

```bash
pipx install trainloop-cli
```

Alternatively, you can install with pip:

```bash
pip install trainloop-cli
```

Or run directly without installation:

```bash
pipx run trainloop-cli --help
```

### Quick Start

1. **Create a workspace:**
   ```bash
   trainloop init
   ```

2. **Set the data path** where your data will be written. You can do this via `TRAINLOOP_DATA_FOLDER` environment variable or by setting it in your `trainloop.config.yaml` file under the `data_folder` key. The environment variable takes precedence.

3. **Instrument your app:**

### **Node**
1. Set the `TRAINLOOP_DATA_FOLDER` environment variable to the path where you want the data to be written.
2. Add `NODE_OPTIONS="--require=trainloop-llm-logging"` to your start script.
**Example**:
```bash
TRAINLOOP_DATA_FOLDER=/path/to/data NODE_OPTIONS="--require=trainloop-llm-logging" node index.js
```

### **Python**
1. Either set the `TRAINLOOP_DATA_FOLDER` environment variable to the path where you want the data to be written or set it in your `trainloop.config.yaml` file.
2. Add `from trainloop_llm_logging import collect; collect("../trainloop/trainloop.config.yaml")` to the entrypoint of your application.

**Example**:
```python
from trainloop_llm_logging import collect

collect("../trainloop/trainloop.config.yaml")
```

**Buffering Control**:
By default, the Python SDK buffers LLM calls and flushes them every 10 seconds or when 5+ calls are buffered. For immediate flushing (useful for testing or scripts that may exit quickly):

```python
from trainloop_llm_logging import collect, flush

# Flush immediately after each LLM call
collect("../trainloop/trainloop.config.yaml", flush_immediately=True)

# Or use default buffering and flush manually when needed
collect("../trainloop/trainloop.config.yaml")
# ... your LLM calls ...
flush()  # Manually flush buffered calls
```

4. **Write metrics and suites** in `trainloop/eval/`

5. **Run the evals:**
   ```bash
   trainloop eval
   ```

6. **Visualize results** in the Studio UI:
   ```bash
   trainloop studio
   ```

## About the TrainLoop Folder

The TrainLoop folder is where all your TrainLoop-specific files live and is created via `trainloop init`. It is structured by default as a data directory, evals directory, and config file.

You can find more information about it in [the Scaffold README](cli/trainloop_cli/scaffold/trainloop/README.md).

## CLI Reference

The TrainLoop CLI provides four main commands for managing your evaluation workflow:

### `trainloop init`

Scaffolds data/ and eval/ directories, creates sample metrics and suites.

```bash
trainloop init
```

This command creates a `trainloop/` workspace with the following structure:
- `trainloop/data/` - Where event and result data is stored
- `trainloop/eval/` - Where metrics and test suites are defined
- `trainloop.config.yaml` - Configuration file

### `trainloop eval`

Discovers suites, applies metrics to new events, and appends verdicts to `data/results/`. If the LLM judge is used, it automatically consolidates all trace events for the run into a single timestamped JSONL file in `trainloop/data/judge_traces/`.

```bash
trainloop eval [OPTIONS]
```

**Options:**
- `--suite <suite_name>` - Run only the specified suite instead of all suites

**Examples:**
```bash
# Run all evaluation suites
trainloop eval

# Run only a specific suite
trainloop eval --suite my_test_suite
```

### `trainloop add`

Adds pre-built metrics and suites from the TrainLoop registry to your project. Components are defined with Python-based `config.py` files for type safety and dynamic discovery.

```bash
trainloop add [metric|suite] [NAME] [OPTIONS]
```

**Options:**
- `--list` - List available metrics and/or suites.
- `--registry <path>` - Use a local directory as the registry (for development).

**Examples:**
```bash
# List all available metrics and suites
trainloop add --list

# List available metrics
trainloop add metric --list

# Add a specific metric
trainloop add metric always_pass

# Add a metric from a local registry path
trainloop add --registry ../my-local-registry metric custom_metric
```

### `trainloop studio`

Launches the TrainLoop Studio UI for visualizing and analyzing your evaluation data.

```bash
trainloop studio [OPTIONS]
```

**Options:**
- `--config <path>` - Path to the trainloop config file (overrides auto-discovery)
- `--local <path>` - Path to a local studio tar file (for development)

**Examples:**
```bash
# Launch studio with auto-discovery (default behavior)
trainloop studio

# Use a custom config file
trainloop studio --config /alt/path/to/trainloop.config.yaml

# Use a local development build of Studio
trainloop studio --local /path/to/your/trainloop-studio-runner.tgz

# Combine both options
trainloop studio --config /custom/config.yaml --local /local/studio.tgz
```

### `trainloop benchmark`

Compares evaluation results across multiple LLM providers to understand performance, cost, and quality differences. This command allows you to benchmark different models against your custom evaluation metrics.

```bash
trainloop benchmark
```

**Configuration:**

Add a `benchmark` section to your `trainloop.config.yaml`:

```yaml
trainloop:
  # ... other config ...
  
  benchmark:
    # Simple format
    providers:
      - openai/gpt-4
      - anthropic/claude-3-sonnet-20240229
      - openai/gpt-3.5-turbo
    
    # Or detailed format for multiple models per provider
    providers:
      - name: openai
        models: [gpt-4o, gpt-4o-mini]
      - name: anthropic
        models: [claude-3-5-sonnet-20241022]
    
    # Optional settings (with defaults)
    temperature: 0.7      # Default: 0.7
    max_tokens: 1000     # Default: 1000
    max_samples: 50      # Limit samples to benchmark
    timeout: 60          # Request timeout in seconds
```

**Environment Variables:**

The benchmark command requires API keys for each provider. It automatically loads from a `.env` file in your trainloop folder.

1. Copy the example file:
   ```bash
   cp trainloop/.env.example trainloop/.env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # OpenAI API Key
   OPENAI_API_KEY=sk-...
   
   # Anthropic API Key
   ANTHROPIC_API_KEY=sk-ant-...
   
   # Google Gemini API Key
   GEMINI_API_KEY=...
   ```

You can also specify a custom env file in the config:

```yaml
benchmark:
  env_path: "../.env.benchmark"  # Relative to config file, overrides default .env
  providers:
    # ...
```

**Output:**

Benchmark results are saved to `data/benchmarks/` with timestamped directories and can be visualized in the Studio UI.

**Use Cases:**
- **Provider Selection**: Compare different providers to choose the best one for your use case
- **Cost Analysis**: Understand the cost implications of different models
- **Performance Testing**: Measure latency differences between providers
- **Quality Comparison**: See how different models handle the same evaluation prompts

### Default Behavior

Running `trainloop` without any command automatically launches the Studio UI:

```bash
trainloop  # Same as: trainloop studio
```

### Global Options

- `--version` - Show the version and exit
- `-h, --help` - Show help message and exit


## Testing

TrainLoop includes a comprehensive test suite to ensure reliability across all components.

### Quick Start

Run all tests with one of these commands:

```bash
# Using go-task (recommended)
task test

# Simple tests (when disk space is limited)
task test:simple
```

### Test Categories

The test suite includes:

1. **CLI FSSpec Integration Tests** - Tests for filesystem abstraction in CLI
2. **SDK FSSpec Tests** - Tests for filesystem abstraction in Python SDK
3. **SDK Store Tests** - Tests for data storage functionality
4. **Init Command Tests** - Integration tests for project initialization
5. **All CLI Unit Tests** - Complete CLI unit test suite
6. **All SDK Unit Tests** - Complete SDK unit test suite
7. **MagicMock Directory Check** - Ensures no mock directories are created

### Individual Test Commands

If you want to run specific test categories:

#### CLI Tests
```bash
cd cli
poetry run pytest ../tests/unit/test_fsspec_integration.py -v  # FSSpec tests
poetry run pytest ../tests/integration/init_flow/test_init_command.py -v  # Init tests
poetry run pytest -m unit -v  # All unit tests
```

#### SDK Tests
```bash
cd sdk/python
poetry run pytest tests/unit/test_fsspec_store.py -v  # FSSpec tests
poetry run pytest tests/unit/test_store.py -v  # Store tests
poetry run pytest -m unit -v  # All unit tests
```

#### Using go-task
```bash
task test:cli      # Run only CLI tests
task test:sdk      # Run only SDK tests
task test:fsspec   # Run FSSpec-specific tests
task test:init     # Run init command tests
task clean:mocks   # Clean up any MagicMock directories
task check:mocks   # Check for any MagicMock directories
task clean:all     # Clean up all test artifacts

# View all available tasks
task --list
```

### Expected Results

All tests should pass. The output will show:
- ✓ Green checkmarks for passed test suites
- ✗ Red X marks for failed test suites
- A summary at the end showing total passed/failed

### Troubleshooting

#### MagicMock Directories

If you see directories with names like `<MagicMock name='Path()' id='123456'>`, these are created when tests don't properly mock filesystem operations. Run:

```bash
task clean:mocks
# or
find . -name "*MagicMock*" -type d -exec rm -rf {} + 2>/dev/null
```

#### Poetry Not Found

Make sure you have Poetry installed and the virtual environments are set up:

```bash
cd cli && poetry install
cd ../sdk/python && poetry install
```

#### Test Failures

If tests fail, check:
1. All dependencies are installed
2. You're in the correct directory
3. No leftover test artifacts from previous runs

### Test Coverage

The tests cover:
- FSSpec implementation for cloud storage support (S3, GCS, Azure)
- File operations with proper mocking
- Project initialization and scaffolding
- Registry operations
- Multi-threaded safety
- Prevention of MagicMock directory creation

### Adding New Tests

When adding new tests:
1. Use appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
2. Properly mock filesystem operations to prevent MagicMock directories
3. Follow the existing test patterns in the codebase


## About this repository
The repository is split into several packages:

- **cli/** – command line tool to scaffold workspaces, run suites and launch the Studio.
- **sdk/typescript/** – Node SDK that logs LLM calls automatically.
- **sdk/python/** – Python SDK for the same purpose.
- **ui/** and **runner/** – TrainLoop Studio web interface and its small runner.
- **infra/** – Pulumi config to deploy the Studio demo.

## More information

- [CLI README](cli/README.md)
- [TypeScript SDK](sdk/typescript/README.md)
- [Python SDK](sdk/python/README.md)
- [Go SDK](sdk/go/trainloop-llm-logging/README.md)
- [Studio UI](ui/README.md)
- [Studio Runner](runner/README.md)
- [Infrastructure](infra/README.md)
- [Contributing](CONTRIBUTING.md)
- [Versioning](VERSIONING.md)
- [Changelog](CHANGELOG.md)

## License

MIT
