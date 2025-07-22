# SDK Integration Testing

## ⚠️ Important: Why We Don't Use pytest

**SDK integration tests cannot be run through pytest** due to a fundamental architectural limitation:

- **The Problem**: TrainLoop SDK requires initialization before any HTTP libraries (`requests`, `httpx`, `openai`, etc.) are imported
- **Pytest Limitation**: pytest and its plugins import these libraries at startup, before our SDK can instrument them
- **Result**: Once imported, libraries cannot be re-patched in the same Python process

## Solution: Standalone Test Runner

We use `run_integration_tests.py` which runs each test as an isolated subprocess:

```bash
# Run all integration tests
python run_integration_tests.py

# Run specific tests
python run_integration_tests.py --test openai
python run_integration_tests.py --test anthropic
python run_integration_tests.py --test litellm
python run_integration_tests.py --test httpx

# Run with verbose output
python run_integration_tests.py --verbose

# Show help
python run_integration_tests.py --help
```

## Available Integration Tests

| Test | Description | Required API Key |
|------|-------------|-----------------|
| `openai` | Tests OpenAI SDK integration with gpt-4o-mini | `OPENAI_API_KEY` |
| `anthropic` | Tests Anthropic SDK integration with claude-3-haiku | `ANTHROPIC_API_KEY` |
| `litellm` | Tests LiteLLM integration with OpenAI backend | `OPENAI_API_KEY` |
| `httpx` | Tests raw httpx integration with OpenAI API | `OPENAI_API_KEY` |

## How It Works

Each test runs as a separate Python process:

1. **Clean Environment**: Fresh Python process with no pre-imported HTTP libraries
2. **SDK First**: Initialize TrainLoop SDK before importing anything else
3. **HTTP Libraries**: Import and use HTTP libraries after SDK instrumentation is active
4. **API Calls**: Make real API calls to verify instrumentation works
5. **Validation**: Check that JSONL files are created with proper structure
6. **Cleanup**: Temporary directories are cleaned up automatically

## Test Structure

Each integration test follows this pattern:

```python
# Initialize SDK before any HTTP imports
import trainloop_llm_logging as tl
tl.collect(flush_immediately=True)

# Now import HTTP libraries (they will be instrumented)
import openai

# Make API calls (these will be captured)
client = openai.OpenAI()
response = client.chat.completions.create(...)

# Validate that JSONL files were created
# Check JSONL structure and content
```

## Using with Task Runner

The Taskfile includes convenience commands:

```bash
# All integration tests
task test:sdk:integration

# Specific tests with verbose output
task test:sdk:integration:openai
task test:sdk:integration:anthropic
task test:sdk:integration:litellm
task test:sdk:integration:httpx

# Verbose mode for all tests
task test:sdk:integration:verbose
```

## CI/CD Integration

GitHub Actions uses the standalone runner:

```yaml
- name: Run SDK integration tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    if [ -n "$OPENAI_API_KEY" ]; then
      poetry run python run_integration_tests.py --verbose
    else
      echo "⚠️ API keys not set - skipping integration tests"
    fi
```

## Development Workflow

When developing new SDK integration tests:

1. **Never use pytest**: Integration tests must be standalone Python scripts
2. **Follow the pattern**: Initialize SDK first, import libraries second
3. **Test in isolation**: Each test should be independent
4. **Use real APIs**: Don't mock - we need to test actual instrumentation
5. **Validate JSONL**: Always verify that logging works correctly

## Testing Latest Package Versions

The integration tests use the latest versions of:
- OpenAI SDK: 1.97.0
- Anthropic SDK: 0.58.2  
- LiteLLM: 1.56.5
- HTTPX: 0.28.1
- And other packages as specified in `pyproject.toml`

## Troubleshooting

### Common Issues

**Import Error**: If you see "module not found" errors, the library isn't installed:
```bash
cd sdk/python
poetry install  # Install all dependencies
```

**API Key Errors**: Tests will skip if API keys are missing:
```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
```

**No JSONL Files**: If tests fail because no files are created, the SDK instrumentation isn't working. This usually means:
- Libraries were imported before SDK initialization
- The test isn't following the proper pattern

### Debug Mode

Run with verbose output to see detailed information:
```bash
python run_integration_tests.py --verbose
```

This shows:
- Test execution details
- API responses
- File paths and content
- Timing information

## Future Improvements

We're exploring ways to make this more seamless while maintaining the architectural requirements:
- pytest plugins that handle import order
- Alternative test frameworks
- Better tooling integration

For now, the standalone runner provides reliable, fast integration testing that properly validates SDK functionality.