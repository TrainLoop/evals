---
sidebar_position: 4
---

# SDK Testing Guide

This document describes how to run tests for both Python and TypeScript SDKs in the TrainLoop Evals ecosystem.

## Overview

Both SDKs have comprehensive test suites covering:
- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test components working together
- **Edge case tests**: Test boundary conditions and error scenarios

## Python SDK Testing

### Prerequisites
```bash
cd sdk/python
poetry install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test categories
poetry run pytest -m unit              # Unit tests only
poetry run pytest -m integration       # Integration tests only
poetry run pytest -m edge_case         # Edge case tests only

# Run tests in parallel
poetry run pytest -n auto

# Run specific test file
poetry run pytest tests/unit/test_config.py

# Run with verbose output
poetry run pytest -v

# Generate HTML coverage report
poetry run pytest --cov --cov-report=html
```

### Test Structure
```
sdk/python/tests/
├── conftest.py          # Shared fixtures and configuration
├── unit/                # Unit tests
│   ├── test_config.py
│   ├── test_exporter.py
│   ├── test_store.py
│   └── ...
├── integration/         # Integration tests
│   ├── test_collection.py
│   ├── test_instrumentation.py
│   └── ...
└── edge_cases/          # Edge case tests
    ├── test_config_edge_cases.py
    ├── test_network_edge_cases.py
    └── ...
```

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow tests (>1s)
- `@pytest.mark.edge_case`: Edge case tests
- `@pytest.mark.requires_network`: Tests requiring network access
- `@pytest.mark.requires_fs`: Tests requiring filesystem access

## TypeScript SDK Testing

### Prerequisites
```bash
cd sdk/typescript
npm install
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test categories
npm run test:unit              # Unit tests only
npm run test:integration       # Integration tests only
npm run test:edge             # Edge case tests only

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- config.test.ts

# Generate coverage report
npm run test:coverage
```

### Test Structure
```
sdk/typescript/tests/
├── setup.ts             # Jest setup and configuration
├── test-utils.ts        # Shared test utilities
├── unit/                # Unit tests
│   ├── config.test.ts
│   ├── exporter.test.ts
│   ├── store.test.ts
│   └── ...
├── integration/         # Integration tests
│   ├── collection.test.ts
│   ├── instrumentation.test.ts
│   └── ...
├── edge-cases/          # Edge case tests
│   ├── config-edge.test.ts
│   ├── network-edge.test.ts
│   └── ...
└── fixtures/            # Test data and fixtures
```

## Test Architecture

### Clean Code Separation

The SDKs maintain clean separation between production and test code:

- **No test logic in production code**: The main SDK files (e.g., `index.ts`) contain only production code
- **Test isolation via mocking**: Tests mock the FileExporter to prevent background timers and file I/O
- **Graceful shutdown**: The `shutdown()` function is useful for both production (graceful shutdown) and tests (cleanup)

### TypeScript Test Setup

The TypeScript test setup (`tests/setup.ts`) handles:
1. Setting test environment variables
2. Mocking the FileExporter to prevent background operations
3. Suppressing console output during tests
4. Cleaning up after all tests complete

### Python Test Setup

The Python test setup (`tests/conftest.py`) provides:
1. Fixtures for temporary directories and files
2. Environment variable management
3. Mock objects for testing without side effects
4. Sample request/response data for different LLM providers

## Common Test Scenarios

### Configuration Tests
- Missing environment variables
- Invalid YAML syntax
- Missing config files
- Path resolution (absolute/relative)
- Environment variable precedence

### HTTP Instrumentation Tests
- Different HTTP libraries (requests, httpx, urllib)
- Network failures
- Timeouts
- Invalid responses
- Large payloads
- Concurrent requests

### Storage Tests
- File system permissions
- Disk full scenarios
- Concurrent writes
- Registry corruption
- Invalid data formats

### Parser Tests
- OpenAI format parsing
- Anthropic format parsing
- Malformed JSON
- Missing fields
- Streaming responses

### Exporter Tests
- Buffer management
- Timer cleanup
- Export failures
- Shutdown handling

## Writing New Tests

### Python Example
```python
import pytest
from trainloop_llm_logging import collect

@pytest.mark.unit
def test_my_feature(temp_data_dir, mock_env_vars):
    """Test description."""
    # Arrange
    os.environ["TRAINLOOP_DATA_FOLDER"] = temp_data_dir
    
    # Act
    result = my_function()
    
    # Assert
    assert result == expected_value
```

### TypeScript Example
```typescript
import { myFunction } from '../../src/myModule';
import { createTempDir, cleanupTempDir } from '../test-utils';

describe('My Feature', () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = createTempDir();
  });

  afterEach(() => {
    cleanupTempDir(tempDir);
  });

  it('should do something', () => {
    // Arrange
    process.env.TRAINLOOP_DATA_FOLDER = tempDir;
    
    // Act
    const result = myFunction();
    
    // Assert
    expect(result).toBe(expectedValue);
  });
});
```

## Continuous Integration

Both test suites are designed to run in CI environments:
- Tests run in isolated environments
- No external dependencies required
- Temporary files are cleaned up
- Console output is suppressed

## Debugging Tests

### Python
```bash
# Run with debugging output
poetry run pytest -s

# Run with breakpoint
poetry run pytest --pdb

# Run specific test with verbose output
poetry run pytest -v -k "test_name"
```

### TypeScript
```bash
# Run with debugging
node --inspect-brk ./node_modules/.bin/jest --runInBand

# Run specific test
npm test -- --testNamePattern="test name"

# Show console output
npm test -- --verbose
```

## Coverage Goals

Both SDKs aim for:
- 80%+ line coverage
- 80%+ branch coverage
- 80%+ function coverage
- Critical paths at 100% coverage

View coverage reports:
- Python: `open htmlcov/index.html`
- TypeScript: `open coverage/lcov-report/index.html`

## Integration with CLI Testing

SDK tests integrate with the broader CLI testing framework:

```bash
# Run all tests including CLI integration
pytest

# Run SDK-specific integration tests
pytest -m sdk

# Run full integration test suite
pytest -m integration
```

## Performance Testing

### Python SDK Performance
```bash
# Run performance benchmarks
poetry run pytest tests/performance/ -v

# Profile memory usage
poetry run pytest --profile tests/unit/test_exporter.py
```

### TypeScript SDK Performance
```bash
# Run performance tests
npm run test:performance

# Profile memory and CPU usage
npm run test:profile
```

## Mock LLM Providers

For testing without hitting real APIs:

### Python
```python
from tests.helpers.mock_llm import MockOpenAI, MockAnthropic

@pytest.fixture
def mock_openai():
    return MockOpenAI(responses=["Test response"])
```

### TypeScript
```typescript
import { mockLLMProvider } from '../test-utils';

describe('LLM Integration', () => {
  beforeEach(() => {
    mockLLMProvider('openai', { response: 'Test response' });
  });
});
```

## Best Practices

1. **Isolate tests**: Each test should be independent
2. **Use meaningful names**: Test names should describe what is being tested
3. **Test edge cases**: Include boundary conditions and error scenarios
4. **Mock external dependencies**: Don't rely on external services
5. **Keep tests fast**: Unit tests should run in milliseconds
6. **Clean up resources**: Ensure temporary files and connections are closed
7. **Use fixtures**: Share common setup code via fixtures
8. **Test error paths**: Verify error handling works correctly