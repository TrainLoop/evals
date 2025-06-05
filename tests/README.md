# TrainLoop Tests

This directory contains comprehensive tests for the TrainLoop ecosystem, including CLI functionality, metrics, and integration testing.

## Test Structure

```
tests/
├── unit/                    # Fast unit tests
│   ├── cli/                # CLI command tests
│   ├── metrics/            # Metric function tests  
│   └── scaffold/           # Scaffold template tests
├── integration/            # End-to-end integration tests
│   ├── init_flow/          # Test `trainloop init` workflow
│   ├── eval_flow/          # Test `trainloop eval` workflow
│   ├── add_flow/           # Test `trainloop add` workflow
│   └── judge_flow/         # Test judge functionality
├── fixtures/               # Test data and sample projects
│   ├── sample_project/     # Mock project structure
│   ├── sample_data/        # JSONL test data
│   └── configs/            # Test configuration files
├── helpers/                # Test utilities and mocks
│   ├── mock_llm.py         # Mock LLM responses for judge tests
│   ├── temp_project.py     # Temporary project creation
│   └── cli_runner.py       # CLI testing utilities
└── conftest.py             # Pytest configuration and fixtures

```

## Test Categories

### Unit Tests (`tests/unit/`)
- **CLI Commands**: Test individual CLI commands in isolation
- **Metrics**: Test metric functions from registry and scaffold
- **Scaffold**: Test template generation and validation

### Integration Tests (`tests/integration/`)
- **Init Flow**: Test complete project initialization
- **Eval Flow**: Test data collection → evaluation → results
- **Add Flow**: Test adding metrics/suites from registry
- **Judge Flow**: Test LLM judge with mocked responses

## Running Tests

```bash
# Run all tests
poetry run pytest tests/

# Run only unit tests
poetry run pytest tests/unit/

# Run only integration tests  
poetry run pytest tests/integration/

# Run with coverage
poetry run pytest tests/ --cov=trainloop_cli --cov-report=html

# Run specific test category
poetry run pytest tests/unit/cli/ -v
```

## Key Benefits

1. **Separation**: Tests are separate from production code
2. **Comprehensive**: Covers CLI, metrics, scaffold, and integration
3. **Fast Feedback**: Unit tests run quickly for development
4. **Real Testing**: Integration tests use actual scaffold templates
5. **No Shipping**: Tests don't get included in CLI distribution

## Test Philosophy

- Use real scaffold templates in integration tests
- Mock external dependencies (LLM APIs, file system when appropriate)
- Test the actual user workflows end-to-end
- Maintain test isolation with temporary directories
- Validate that scaffold components work correctly when installed
