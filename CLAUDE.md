# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrainLoop Evals is a comprehensive LLM evaluation framework consisting of:
- **CLI Tool** (`trainloop` command) - Python-based evaluation engine
- **Studio UI** (`ui/`) - Next.js web interface for visualization
- **Multi-language SDKs** - Python, TypeScript, and Go instrumentation libraries
- **Registry System** - Shareable metrics and evaluation suites

## Development Commands

### Building & Publishing
```bash
# Build all components
npm run build

# Build individual components
npm run build:docker    # CLI and SDKs only
npm run build:studio    # Studio UI only

# Publish all packages
npm run publish

# Publish individual components
npm run publish:cli
npm run publish:sdk
npm run publish:studio
```

### Development Server
```bash
# Start UI development server
npm run dev
# or
cd ui && npm run dev

# UI-specific commands
cd ui && npm run lint
cd ui && npm run build
```

### Testing
```bash
# Run all tests (from root)
pytest

# Run specific test categories
pytest -m unit          # Fast unit tests
pytest -m integration   # End-to-end tests
pytest -m cli           # CLI command tests
pytest -m judge         # LLM judge functionality
pytest -m scaffold      # Template functionality

# Run single test file
pytest tests/test_cli.py
```

### CLI Development
```bash
# Install CLI for development
cd cli && poetry install

# Run CLI locally
cd cli && poetry run trainloop --help

# Format CLI code
cd cli && poetry run black .
cd cli && poetry run flake8 .
```

## Architecture

### Core Components
- **`cli/trainloop_cli/`** - Main CLI implementation with commands: `init`, `eval`, `studio`, `add`
- **`ui/`** - Next.js 15 Studio UI with DuckDB integration for data visualization
- **`sdk/`** - Zero-touch HTTP instrumentation libraries for Python, TypeScript, Go
- **`registry/`** - Shared evaluation components with Python-based config discovery

### Data Flow
1. SDKs collect LLM request/response data as JSONL files
2. CLI `eval` command applies metrics to events, outputs results
3. Studio UI loads data via DuckDB for interactive visualization
4. Registry system allows sharing metrics via `trainloop add`

### Key Technologies
- **Python**: Poetry, Click, LiteLLM, pytest with custom markers
- **TypeScript**: Next.js 15, React 18, Tailwind CSS, shadcn/ui, DuckDB
- **Infrastructure**: Pulumi for deployment, pipx for CLI distribution

## Project Structure

### Evaluation Workflow
- `trainloop/data/events/` - Raw LLM interaction data (JSONL)
- `trainloop/data/results/` - Evaluation results from metrics
- `trainloop/eval/` - Metrics and suite definitions (Python modules)
- `trainloop.config.yaml` - Configuration file

### Testing Framework
- Test markers defined in `pytest.ini` for categorized test execution
- Comprehensive CLI testing with subprocess integration
- SDK testing across multiple languages

## Configuration Files

- **`pyproject.toml`** - CLI package configuration (Poetry)
- **`package.json`** - UI dependencies and root-level build scripts
- **`pytest.ini`** - Test configuration with custom markers
- **`trainloop.config.yaml`** - Runtime configuration template

## Development Notes

- Use `poetry` for CLI Python dependencies
- Use `npm` for UI and build system management
- Registry components use Python `config.py` files for type-safe discovery
- Studio UI uses DuckDB for local data querying without external databases
- All components support local development with hot reload