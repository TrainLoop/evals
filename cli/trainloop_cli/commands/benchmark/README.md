# Benchmark Module Structure

The benchmark command has been refactored into a modular structure for better organization and maintainability.

## Module Files

- **`__init__.py`** - Module entry point, exports `benchmark_command`
- **`command.py`** - Main command implementation and orchestration
- **`constants.py`** - Shared constants (ANSI colors, emojis, provider mappings)
- **`types.py`** - Type definitions (`BenchmarkResult` dataclass)
- **`loaders.py`** - Functions for loading data (metrics, results, config)
- **`validators.py`** - Validation logic (API key checking)
- **`runner.py`** - Core benchmarking logic (running prompts through providers)
- **`storage.py`** - Saving benchmark results to JSONL files
- **`output.py`** - Console output and summary display

## Data Flow

1. **command.py** orchestrates the entire process
2. **loaders.py** loads evaluation results, metrics, and config
3. **validators.py** checks API keys are available
4. **runner.py** executes benchmarks across providers
5. **storage.py** saves results to disk
6. **output.py** displays summary to console

## Adding New Features

- New providers: Add to `PROVIDER_KEY_MAP` in `constants.py`
- New output formats: Extend `storage.py`
- New validation: Add to `validators.py`
- New metrics: Are loaded dynamically by `loaders.py`