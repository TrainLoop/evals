# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrainLoop Evals is a comprehensive LLM evaluation framework consisting of:
- **CLI Tool** (`trainloop` command) - Python-based evaluation engine
- **Studio UI** (`ui/`) - Next.js web interface for visualization
- **Multi-language SDKs** - Python, TypeScript, and Go HTTP instrumentation libraries
- **Registry System** - Shareable metrics and evaluation suites
- **Runner** (`runner/`) - Distribution wrapper for the Studio UI
- **Documentation** (`docs/`) - Docusaurus 3.8.1 documentation site
- **Infrastructure** (`infra/`) - Pulumi infrastructure as code for AWS deployment

## Quick Start

```bash
# One-command setup for all dependencies
./scripts/setup.py
```

## Development Commands

### Setup & Dependencies
```bash
# Install all dependencies across monorepo
./scripts/setup.py
```

### Version Management
```bash
# Automated release workflow
npm run release <major|minor|patch> "description"

# Manual version bump
npm run bump <major|minor|patch> "description"

# Update Pulumi config with new version
npm run pulumi:bump
```

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
npm run publish:cli      # Publish CLI to PyPI
npm run publish:sdk      # Publish SDKs to registries
npm run publish:studio   # Publish Studio package
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
# Run all tests using Task
task test

# Run simplified test suite
task test:simple

# Run specific component tests
task test:cli              # CLI unit tests
task test:sdk              # SDK unit tests
task test:sdk:integration  # SDK integration tests

# Clean test artifacts
task clean:all

# Run tests with pytest markers
pytest -m unit          # Fast unit tests
pytest -m integration   # End-to-end tests
pytest -m cli           # CLI command tests
pytest -m judge         # LLM judge functionality
pytest -m scaffold      # Template functionality
pytest -m benchmark     # Benchmark functionality

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
- **`cli/trainloop_cli/`** - Main CLI implementation with commands: `init`, `eval`, `studio`, `add`, `benchmark`
- **`ui/`** - Next.js 15 Studio UI with DuckDB integration for data visualization
- **`sdk/`** - Zero-touch HTTP instrumentation libraries for Python, TypeScript, Go
- **`registry/`** - Shared evaluation components with Python-based config discovery
- **`runner/`** - Node.js-based distribution wrapper for the Studio UI executable
- **`docs/`** - Docusaurus 3.8.1 documentation site
- **`infra/`** - Pulumi infrastructure configuration for AWS deployment
- **`scripts/`** - Build, publish, and development automation scripts
- **`tests/`** - Root-level integration tests

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

- **`pyproject.toml`** - Root and component-level Python package configuration (Poetry)
- **`package.json`** - Root scripts and component-level Node.js dependencies
- **`pytest.ini`** - Test configuration with custom markers
- **`trainloop.config.yaml`** - Runtime configuration template
- **`Taskfile.yml`** - Task runner configuration for test automation
- **`VERSION`** - Central version file (source of truth for all components)
- **`poetry.lock`** - Poetry lock files for reproducible Python environments
- **`package-lock.json`** - NPM lock files for reproducible Node.js environments

## Development Notes

- Use `poetry` for Python dependencies (CLI, SDK, root tests)
- Use `npm` for JavaScript/TypeScript dependencies and build scripts
- Version management is centralized through the `VERSION` file
- All components are versioned together for consistency
- Registry components use Python `config.py` files for type-safe discovery
- Studio UI uses DuckDB for local data querying without external databases
- All components support local development with hot reload
- CI/CD workflows are defined in `.github/workflows/`

## Docker Development

```bash
# Build development image with all dependencies
docker build -f Dockerfile.dev -t trainloop-dev .

# Run development container
docker run -it -v $(pwd):/app trainloop-dev

# The setup script is perfect for Docker environments
RUN ./scripts/setup.py
```

## Scripts Directory

The `scripts/` directory contains automation tools:
- **`setup.py`** - Install all dependencies across monorepo
- **`build.py`** - Master build script
- **`publish.py`** - Master publish script
- **`release.py`** - Automated release workflow
- **`bump/`** - Version bumping utilities
- **`build/`** - Component-specific build scripts
- **`publish/`** - Component-specific publish scripts