# Testing Guide

This guide covers the comprehensive testing framework used in TrainLoop Evals, including test categories, execution methods, and best practices.

## Test Framework Overview

TrainLoop Evals uses a multi-layered testing approach:

- **Unit Tests** - Fast, isolated tests for individual functions
- **Integration Tests** - Component interaction tests
- **End-to-End Tests** - Complete user workflow tests
- **Performance Tests** - Load and benchmark tests
- **SDK Integration Tests** - Cross-language SDK compatibility

## Test Categories

The test suite is organized using pytest markers for categorization:

### Core Test Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - End-to-end integration tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.judge` - Tests involving LLM judge functionality
- `@pytest.mark.cli` - Tests for CLI commands
- `@pytest.mark.scaffold` - Tests for scaffold template functionality
- `@pytest.mark.registry` - Tests for registry components
- `@pytest.mark.benchmark` - Tests for benchmark functionality

### Test Configuration

Test configuration is defined in `pytest.ini`:

```ini
[pytest]
testpaths = tests,sdk
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Fast unit tests
    integration: End-to-end integration tests
    slow: Tests that take longer to run
    judge: Tests that involve LLM judge functionality
    cli: Tests for CLI commands
    scaffold: Tests for scaffold template functionality
    registry: Tests for registry components
    benchmark: Tests for benchmark functionality

addopts = 
    -v
    --tb=short
    --strict-markers
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
task test

# Run simplified tests (recommended for limited disk space)
task test:simple

# Run component-specific tests
task test:cli      # CLI tests only
task test:sdk      # SDK tests only
```

### Using pytest Directly

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Fast unit tests
pytest -m integration   # Integration tests
pytest -m cli           # CLI command tests
pytest -m judge         # LLM judge functionality

# Run specific test files
pytest tests/test_cli.py
pytest tests/unit/test_config_utils.py
```

## Component-Specific Testing

### CLI Testing

#### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_config_utils.py
│   └── judge/
│       └── test_judge_basic.py
├── integration/            # Integration tests
│   └── init_flow/
│       └── test_init_command.py
├── helpers/               # Test utilities
│   └── mock_llm.py
└── conftest.py           # Test configuration
```

#### Running CLI Tests

```bash
cd cli

# Run all CLI tests
poetry run pytest

# Run specific test categories
poetry run pytest -m unit
poetry run pytest -m integration
poetry run pytest -m cli

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest ../tests/unit/test_config_utils.py
```

#### CLI Test Examples

```python
# tests/unit/test_config_utils.py
import pytest
from trainloop_cli.commands.utils import load_config

class TestConfigUtils:
    def test_load_config_with_valid_file(self):
        """Test loading a valid configuration file."""
        config = load_config("valid_config.yaml")
        assert config is not None
        assert "data_folder" in config
    
    @pytest.mark.cli
    def test_cli_command_execution(self):
        """Test CLI command execution."""
        result = subprocess.run(["trainloop", "--version"], capture_output=True)
        assert result.returncode == 0
```

### SDK Testing

#### Python SDK Testing

```bash
cd sdk/python

# Run all SDK unit tests
poetry run pytest -m unit

# Run unit tests only (recommended for development)
poetry run pytest -m unit

# Run integration tests (requires API keys) - MUST use standalone runner
python run_integration_tests.py                    # All integration tests
python run_integration_tests.py --test openai      # OpenAI only
python run_integration_tests.py --verbose          # With detailed output

# Run specific unit test categories
poetry run pytest tests/unit/test_store.py
```

#### 🚨 Important: SDK Integration Tests

**SDK integration tests cannot be run through pytest** due to a fundamental architectural limitation. The TrainLoop SDK requires initialization before any HTTP libraries are imported, but pytest imports these libraries before our SDK can instrument them.

**Why this happens:**
- pytest and its plugins import `requests`, `httpx`, and other HTTP libraries at startup
- TrainLoop SDK needs to patch these libraries before they're imported
- Once imported, the libraries cannot be re-patched in the same process

**Solution:** Use the standalone integration test runner:
```bash
# Located in sdk/python/run_integration_tests.py
python run_integration_tests.py --help
```

#### Python SDK Test Structure

```
sdk/python/tests/
├── unit/                     # Unit tests
│   ├── test_config.py
│   ├── test_store.py
│   ├── test_logger.py
│   └── test_fsspec_store.py
├── integration/              # Integration tests
│   ├── test_openai_sdk.py
│   ├── test_anthropic_sdk.py
│   ├── test_langchain.py
│   └── test_litellm.py
├── edge_cases/              # Edge case tests
└── conftest.py              # Test configuration
```

#### TypeScript SDK Testing

```bash
cd sdk/typescript

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test files
npm test -- --testNamePattern="config"
npm test -- tests/unit/store.test.ts
```

#### Go SDK Testing

```bash
cd sdk/go/trainloop-llm-logging

# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific packages
go test ./internal/config
go test ./instrumentation
```

## Test Execution Strategies

### Parallel Testing

```bash
# Run tests in parallel (pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Test Filtering

```bash
# Run tests matching pattern
pytest -k "test_config"

# Run tests not matching pattern
pytest -k "not slow"

# Combine filters
pytest -k "config and not integration"
```

### Test Output Control

```bash
# Minimal output
pytest -q

# Verbose output
pytest -v

# Show local variables in failures
pytest -l

# Show full traceback
pytest --tb=long
```

## Integration Testing

### SDK Integration Tests

SDK integration tests verify compatibility with real LLM providers but **cannot be run through pytest**. Due to import order requirements, they use a standalone test runner.

#### Environment Setup for Integration Tests

```bash
# Set up API keys for integration tests
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here

# Run integration tests using standalone runner
cd sdk/python
python run_integration_tests.py
```

#### Integration Test Categories

```bash
# All integration tests
task test:sdk:integration

# Specific integration tests
task test:sdk:integration:openai      # OpenAI SDK integration
task test:sdk:integration:anthropic   # Anthropic SDK integration
task test:sdk:integration:litellm     # LiteLLM integration
task test:sdk:integration:httpx       # Raw httpx integration

# With verbose output
task test:sdk:integration:verbose
```

#### How SDK Integration Tests Work

The standalone integration test runner executes each test as a separate Python process:

1. **Process Isolation**: Each test runs in its own subprocess to avoid import conflicts
2. **SDK Initialization**: TrainLoop SDK is initialized before importing HTTP libraries
3. **Real API Calls**: Tests make actual API calls to verify instrumentation
4. **JSONL Validation**: Tests verify that API calls are properly logged to JSONL files
5. **Graceful Skipping**: Tests skip automatically if API keys are not available

Example test execution:
```python
# This runs as a subprocess with clean imports
import trainloop_llm_logging as tl
tl.collect(flush_immediately=True)  # Initialize SDK first

import openai  # Import after SDK initialization
client = openai.OpenAI()
response = client.chat.completions.create(...)  # Instrumentation captures this
```

## Performance Testing

### Load Testing

```bash
# Run performance tests
pytest -m slow

# Run with profiling
pytest --profile

# Run load tests
pytest tests/performance/test_load.py
```

### Benchmark Testing

```bash
# Run benchmark tests
pytest -m benchmark

# Run CLI benchmark command tests
pytest -m benchmark -k "benchmark"
```

## Test Data Management

### Test Fixtures

```python
# conftest.py
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }
```

### Test Data Files

```
tests/fixtures/
├── config/
│   ├── valid_config.yaml
│   └── invalid_config.yaml
├── events/
│   ├── sample_events.jsonl
│   └── benchmark_events.jsonl
└── responses/
    ├── openai_response.json
    └── anthropic_response.json
```

## Continuous Integration Testing

### GitHub Actions Workflow

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          cd cli && poetry install
          cd ../sdk/python && poetry install
      
      - name: Run tests
        run: task test:simple
```

### Test Reporting

```bash
# Generate test coverage report
pytest --cov=trainloop_cli --cov-report=html

# Generate JUnit XML report
pytest --junitxml=test-results.xml

# Generate comprehensive report
pytest --cov=trainloop_cli --cov-report=html --cov-report=term --junitxml=test-results.xml
```

## Test Debugging

### Debugging Failed Tests

```bash
# Run with debugger
pytest --pdb

# Run with verbose output and local variables
pytest -vvv -l

# Run specific failing test
pytest tests/unit/test_config.py::TestConfig::test_load_config -vvv
```

### Test Isolation

```bash
# Run tests in isolation
pytest --forked

# Run with clean environment
pytest --cache-clear

# Run with specific temporary directory
pytest --basetemp=/tmp/pytest-custom
```

## Mock and Fixture Management

### Common Mock Patterns

```python
from unittest.mock import patch, MagicMock

@patch('trainloop_llm_logging.store.Path')
def test_store_with_mock_filesystem(mock_path):
    """Test store functionality with mocked filesystem."""
    mock_path.return_value.exists.return_value = True
    
    # Test logic here
    assert store.save_data(data) is True
```

### Preventing MagicMock Directory Creation

```python
# Good: Properly configure mocks
@patch('pathlib.Path')
def test_path_operations(mock_path):
    mock_path.return_value.mkdir.return_value = None
    mock_path.return_value.exists.return_value = True
    
    # Test logic
```

### Cleanup Tasks

```bash
# Clean up MagicMock directories
task clean:mocks

# Check for MagicMock directories
task check:mocks

# Clean all test artifacts
task clean:all
```

## Writing New Tests

### Test Structure Guidelines

```python
class TestComponentName:
    """Test suite for ComponentName."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.component = ComponentName()
    
    def test_basic_functionality(self):
        """Test basic component functionality."""
        result = self.component.do_something()
        assert result == expected_value
    
    @pytest.mark.integration
    def test_integration_scenario(self):
        """Test integration with external services."""
        # Integration test logic
        pass
    
    @pytest.mark.slow
    def test_performance_scenario(self):
        """Test performance characteristics."""
        # Performance test logic
        pass
```

### Test Naming Conventions

- Use descriptive test names: `test_save_config_creates_file`
- Group related tests in classes: `TestConfigManager`
- Use appropriate markers: `@pytest.mark.unit`
- Include docstrings for complex tests

### Assertion Best Practices

```python
# Good: Specific assertions
assert response.status_code == 200
assert len(results) == 3
assert "expected_key" in response_data

# Better: Use pytest helpers
pytest.approx(actual_value, expected_value, rel=1e-3)
```

## Test Maintenance

### Regular Test Maintenance

```bash
# Run tests frequently during development
pytest -x  # Stop on first failure

# Update test dependencies
cd cli && poetry update
cd ../sdk/python && poetry update
```

### Test Performance Optimization

```bash
# Profile test execution
pytest --durations=10

# Identify slow tests
pytest --durations=0 | grep -E "slow|SLOW"
```

## Troubleshooting Common Issues

### Test Environment Issues

```bash
# Clear pytest cache
pytest --cache-clear

# Reset test environment
task clean:all
```

### API Key Issues

```bash
# Check API key configuration
echo $OPENAI_API_KEY

# Skip integration tests without API keys
pytest -m "not integration"
```

### Dependency Issues

```bash
# Reinstall test dependencies
poetry install --no-cache

# Check for conflicting dependencies
poetry check
```

## Best Practices

### Test Organization

- Keep tests close to the code they test
- Use clear, descriptive test names
- Group related tests in classes
- Use appropriate test markers

### Test Data

- Use fixtures for reusable test data
- Keep test data minimal and focused
- Use factory patterns for complex test objects
- Clean up test data after tests

### Test Performance

- Keep unit tests fast (< 100ms each)
- Use mocks for external dependencies
- Run integration tests separately
- Profile slow tests regularly

### Test Coverage

- Aim for high test coverage (>90%)
- Focus on critical paths and edge cases
- Use coverage reports to identify gaps
- Don't sacrifice test quality for coverage

## Next Steps

- Review the [Local Development](./local-development.md) guide for test setup
- Check the [Building from Source](./building-from-source.md) guide for build testing
- See the [Code Style](./code-style.md) guide for test code standards
- Follow the [Pull Request Process](./pull-request-process.md) for test requirements