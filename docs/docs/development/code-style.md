# Code Style Guide

This guide defines the coding standards and conventions used across the TrainLoop Evals project. Following these guidelines ensures consistency, readability, and maintainability.

## General Principles

### Code Quality Standards

1. **Readability First** - Code is read 10× more than it's written
2. **Consistency** - Follow established patterns throughout the codebase
3. **Simplicity** - Prefer simple, clear solutions over complex ones
4. **Single Responsibility** - Each function/class should have one reason to change
5. **DRY (Don't Repeat Yourself)** - Avoid code duplication
6. **YAGNI (You Aren't Gonna Need It)** - Don't build features until needed

### File Organization

- Use clear, descriptive file and directory names
- Group related functionality together
- Keep file lengths reasonable (< 500 lines for most files)
- Use consistent file naming conventions

## Language-Specific Guidelines

### Python

TrainLoop Evals uses Python 3.9+ with modern Python conventions.

#### Code Formatting

We use **Black** for code formatting with the following configuration:

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  __pycache__
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

#### Linting

We use **flake8** for linting with these rules:

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, E266, E501, W503
max-complexity = 10
exclude = .git,__pycache__,dist,build,.venv
```

#### Import Organization

Use **isort** for import sorting:

```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import click
import yaml
from pydantic import BaseModel

# Local application imports
from trainloop_cli.commands.utils import load_config
from trainloop_cli.eval_core.types import EvalResult
```

#### Type Hints

Use type hints for all public functions and complex private functions:

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def load_config(config_path: Path) -> Dict[str, Union[str, int, bool]]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is malformed
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
```

#### Function and Class Conventions

```python
# Good: Clear function names with type hints
def calculate_metrics(events: List[Dict], suite_name: str) -> EvalResult:
    """Calculate evaluation metrics for a suite of events."""
    pass

# Good: Class naming with clear purpose
class MetricsCalculator:
    """Handles calculation of evaluation metrics."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._cache: Dict[str, Any] = {}
    
    def calculate(self, events: List[Dict]) -> EvalResult:
        """Calculate metrics for the given events."""
        pass

# Good: Use dataclasses for data structures
from dataclasses import dataclass
from typing import Optional

@dataclass
class EvalConfig:
    """Configuration for evaluation runs."""
    suite_name: str
    data_folder: Path
    output_format: str = "jsonl"
    max_workers: int = 4
    timeout: Optional[int] = None
```

#### Error Handling

```python
# Good: Specific exception handling
try:
    config = load_config(config_path)
except FileNotFoundError:
    logger.error(f"Config file not found: {config_path}")
    raise
except yaml.YAMLError as e:
    logger.error(f"Invalid YAML in config file: {e}")
    raise

# Good: Custom exceptions for domain-specific errors
class EvaluationError(Exception):
    """Base exception for evaluation-related errors."""
    pass

class MetricNotFoundError(EvaluationError):
    """Raised when a requested metric is not available."""
    pass
```

### TypeScript

For the TypeScript SDK and UI components, we follow modern TypeScript conventions.

#### Code Formatting

Use **Prettier** with these settings:

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

#### Type Definitions

```typescript
// Good: Use interfaces for object shapes
interface LLMEvent {
  id: string;
  timestamp: number;
  provider: string;
  model: string;
  prompt: string;
  response: string;
  metadata?: Record<string, unknown>;
}

// Good: Use union types for known values
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// Good: Use generic types for reusable functions
function processEvents<T extends LLMEvent>(
  events: T[],
  processor: (event: T) => T
): T[] {
  return events.map(processor);
}
```

#### React Component Conventions

```typescript
// Good: Functional components with TypeScript
import React from 'react';

interface DashboardProps {
  title: string;
  events: LLMEvent[];
  onEventSelect?: (event: LLMEvent) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  title,
  events,
  onEventSelect,
}) => {
  return (
    <div className="dashboard">
      <h1>{title}</h1>
      {events.map((event) => (
        <div key={event.id} onClick={() => onEventSelect?.(event)}>
          {event.provider}: {event.model}
        </div>
      ))}
    </div>
  );
};
```

### Go

For the Go SDK, we follow standard Go conventions.

#### Code Formatting

Use `gofmt` and `goimports` for formatting:

```bash
# Format all Go files
go fmt ./...

# Organize imports
goimports -w .
```

#### Package Organization

```go
// Good: Clear package documentation
// Package instrumentation provides HTTP instrumentation for TrainLoop logging.
package instrumentation

import (
    "context"
    "net/http"
    "time"
)

// Good: Exported types with documentation
type Config struct {
    DataFolder string `json:"data_folder"`
    FlushInterval time.Duration `json:"flush_interval"`
}

// Good: Interface definitions
type HTTPClient interface {
    Do(req *http.Request) (*http.Response, error)
}

// Good: Factory functions
func NewInstrumentedClient(client HTTPClient, config Config) HTTPClient {
    return &instrumentedClient{
        client: client,
        config: config,
    }
}
```

## Documentation Standards

### Docstrings and Comments

#### Python Docstrings

Use Google-style docstrings:

```python
def evaluate_suite(
    suite_name: str,
    events: List[Dict],
    config: EvalConfig
) -> EvalResult:
    """Evaluate a suite of events against configured metrics.
    
    This function loads the specified evaluation suite and applies
    all configured metrics to the provided events.
    
    Args:
        suite_name: Name of the evaluation suite to run
        events: List of LLM events to evaluate
        config: Evaluation configuration
        
    Returns:
        EvalResult containing metrics and verdicts
        
    Raises:
        SuiteNotFoundError: If the specified suite doesn't exist
        MetricError: If any metric fails to execute
        
    Example:
        >>> config = EvalConfig(suite_name="basic", data_folder=Path("./data"))
        >>> events = load_events("events.jsonl")
        >>> result = evaluate_suite("basic", events, config)
        >>> print(f"Passed: {result.passed}/{result.total}")
    """
```

#### TypeScript JSDoc

```typescript
/**
 * Collects and logs LLM events for evaluation.
 * 
 * @param config - Configuration object for data collection
 * @param options - Optional parameters for collection behavior
 * @returns Promise that resolves when collection is initialized
 * 
 * @example
 * ```typescript
 * await collect({
 *   dataFolder: './data',
 *   flushInterval: 5000
 * });
 * ```
 */
export async function collect(
  config: CollectionConfig,
  options?: CollectionOptions
): Promise<void> {
  // Implementation
}
```

#### Go Comments

```go
// Config represents the configuration for TrainLoop logging.
// It contains settings for data storage, flush intervals, and other
// operational parameters.
type Config struct {
    // DataFolder is the directory where event data will be stored
    DataFolder string `json:"data_folder"`
    
    // FlushInterval determines how often buffered events are written
    FlushInterval time.Duration `json:"flush_interval"`
}

// NewConfig creates a new Config instance with default values.
// The default data folder is "./data" and flush interval is 10 seconds.
func NewConfig() *Config {
    return &Config{
        DataFolder:    "./data",
        FlushInterval: 10 * time.Second,
    }
}
```

### Code Comments

```python
# Good: Explain why, not what
def calculate_score(responses: List[str]) -> float:
    # Use harmonic mean to penalize inconsistent responses more heavily
    # than arithmetic mean would
    scores = [rate_response(r) for r in responses]
    return len(scores) / sum(1/s for s in scores if s > 0)

# Good: Explain complex algorithms
def find_optimal_threshold(metrics: List[float]) -> float:
    """Find the optimal threshold using Otsu's method."""
    # Implementation of Otsu's method for automatic threshold selection
    # This maximizes the between-class variance while minimizing within-class variance
    histogram = create_histogram(metrics)
    # ... rest of implementation
```

## Testing Standards

### Test Organization

```python
# Good: Clear test structure
class TestMetricsCalculator:
    """Test suite for MetricsCalculator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = MetricsCalculator(config={"timeout": 30})
        self.sample_events = [
            {"id": "1", "prompt": "Hello", "response": "Hi there"},
            {"id": "2", "prompt": "Goodbye", "response": "See you later"}
        ]
    
    def test_calculate_with_valid_events(self):
        """Test calculation with valid event data."""
        result = self.calculator.calculate(self.sample_events)
        
        assert result.total == 2
        assert result.passed >= 0
        assert result.failed >= 0
        assert result.passed + result.failed == result.total
    
    @pytest.mark.integration
    def test_calculate_with_llm_judge(self):
        """Test calculation using LLM judge integration."""
        # Integration test logic
        pass
```

### Test Naming

- Use descriptive test names: `test_calculate_score_with_empty_responses`
- Group related tests in classes: `TestMetricsCalculator`
- Use appropriate markers: `@pytest.mark.unit`

## Performance Guidelines

### Python Performance

```python
# Good: Use list comprehensions for simple transformations
filtered_events = [e for e in events if e.get("score", 0) > 0.5]

# Good: Use generator expressions for large datasets
total_score = sum(e.get("score", 0) for e in events)

# Good: Use dataclasses for structured data
@dataclass
class CachedResult:
    result: EvalResult
    timestamp: float
    
# Good: Use proper caching
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(event_id: str) -> float:
    # Expensive calculation here
    pass
```

### Memory Management

```python
# Good: Use context managers for resource cleanup
def process_large_file(file_path: Path) -> Iterator[Dict]:
    """Process large JSONL file with streaming."""
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)

# Good: Use generators for large datasets
def load_events_streaming(data_folder: Path) -> Iterator[Dict]:
    """Load events from multiple files without loading all into memory."""
    for file_path in data_folder.glob("*.jsonl"):
        yield from process_large_file(file_path)
```

## Security Guidelines

### Input Validation

```python
# Good: Validate input parameters
def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from file with validation."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    if not config_path.is_file():
        raise ValueError(f"Config path is not a file: {config_path}")
    
    # Validate file size (prevent DoS)
    max_size = 10 * 1024 * 1024  # 10MB
    if config_path.stat().st_size > max_size:
        raise ValueError(f"Config file too large: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
```

### Environment Variables

```python
# Good: Use environment variables safely
import os
from pathlib import Path

def get_data_folder() -> Path:
    """Get data folder from environment or config."""
    data_folder = os.getenv("TRAINLOOP_DATA_FOLDER")
    if not data_folder:
        raise ValueError("TRAINLOOP_DATA_FOLDER environment variable not set")
    
    path = Path(data_folder).expanduser().resolve()
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    return path
```

## Version Control

### Commit Messages

Use conventional commit format:

```
feat(cli): add benchmark command for model comparison

Add a new benchmark command that allows users to compare different
LLM models across evaluation metrics. The command supports multiple
providers and generates comparison reports.

- Add benchmark command with provider configuration
- Implement parallel model evaluation
- Add comparison report generation
- Include performance metrics and cost analysis

Closes #123
```

### Branch Management

```bash
# Good: Descriptive branch names
git checkout -b feature/add-benchmark-command
git checkout -b fix/config-loading-error
git checkout -b docs/update-installation-guide

# Good: Keep branches focused
# One feature or fix per branch
# Regular rebasing to keep history clean
```

## Tools and Automation

### Pre-commit Hooks

Set up pre-commit hooks to enforce code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

### IDE Configuration

#### VS Code Settings

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Best Practices Summary

### Do's

- ✅ Use descriptive names for variables, functions, and classes
- ✅ Write comprehensive docstrings for public APIs
- ✅ Add type hints to improve code clarity
- ✅ Use consistent formatting tools (Black, Prettier, gofmt)
- ✅ Write tests for all new functionality
- ✅ Handle errors gracefully with appropriate exceptions
- ✅ Use logging for debugging and monitoring
- ✅ Follow the principle of least surprise
- ✅ Keep functions small and focused
- ✅ Use version control effectively

### Don'ts

- ❌ Don't use magic numbers or hardcoded values
- ❌ Don't ignore error conditions
- ❌ Don't write overly complex functions
- ❌ Don't duplicate code across the codebase
- ❌ Don't commit code without running tests
- ❌ Don't use global variables unless absolutely necessary
- ❌ Don't write code without documentation
- ❌ Don't ignore linting warnings
- ❌ Don't use deprecated APIs
- ❌ Don't commit sensitive information

## Code Review Checklist

When reviewing code, check for:

- [ ] **Functionality** - Does the code do what it's supposed to do?
- [ ] **Style** - Does the code follow the style guidelines?
- [ ] **Testing** - Are there adequate tests for the new functionality?
- [ ] **Documentation** - Is the code properly documented?
- [ ] **Performance** - Are there any obvious performance issues?
- [ ] **Security** - Are there any security vulnerabilities?
- [ ] **Maintainability** - Is the code easy to understand and modify?
- [ ] **Error Handling** - Are errors handled appropriately?
- [ ] **Edge Cases** - Are edge cases considered and handled?
- [ ] **Backwards Compatibility** - Are breaking changes justified and documented?

## Resources

- **[Contributing Guide](./contributing.md)** - General contribution guidelines
- **[Testing Guide](./testing.md)** - Testing standards and practices
- **[Pull Request Process](./pull-request-process.md)** - Code review workflow
- **[Local Development](./local-development.md)** - Development environment setup

## Getting Help

If you have questions about code style or need clarification on any guidelines:

- **Open a discussion** on [GitHub Discussions](https://github.com/trainloop/evals/discussions)
- **Ask in your pull request** if you're unsure about specific changes
- **Check existing code** in the repository for examples
- **Refer to language-specific style guides** for detailed formatting rules

---

Following these guidelines helps maintain a high-quality, consistent codebase that's easy for everyone to understand and contribute to.