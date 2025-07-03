# TrainLoop LLM Logging - Integration Tests

This directory contains comprehensive integration tests that verify the TrainLoop LLM Logging SDK works correctly with various Python HTTP libraries and LLM frameworks.

## 🎯 Purpose

These tests make **actual API calls** to verify that:

1. **HTTP Library Instrumentation**: All supported HTTP libraries (httpx, requests, http.client) properly capture LLM API calls
2. **LLM Framework Support**: Popular LLM frameworks (OpenAI SDK, Anthropic SDK, LangChain, etc.) work correctly with instrumentation
3. **Browser Automation**: Browser Use library integration for AI agent workflows
4. **Response Handling**: Gzipped responses and various response formats are handled correctly
5. **Multi-provider Support**: Both OpenAI and Anthropic APIs work correctly
6. **JSONL File Creation**: All captured data is properly written to JSONL files with correct structure

## 📁 Test Files

### Core Integration Tests
- **`test_real_api_calls.py`** - Tests core HTTP libraries (httpx, requests, http.client)
- **`example_integration_test.py`** - Simple standalone example that anyone can run

### Specialized Tests
- **`test_browser_use_integration.py`** - Tests Browser Use library with LLM APIs
- **`test_other_llm_libraries.py`** - Tests popular LLM frameworks and SDKs

### Test Infrastructure
- **`run_all_integration_tests.py`** - Comprehensive test runner for all integration tests
- **`README.md`** - This documentation

## 🔧 Setup

### 1. Install Dependencies

```bash
# Core dependencies (required)
cd /path/to/sdk/python
poetry install

# Optional dependencies for extended testing
poetry install --extras dev

# Or install individual libraries:
pip install browser-use playwright litellm openai anthropic langchain-openai langchain-anthropic instructor
```

### 2. Set Environment Variables

```bash
# Required for most tests
export OPENAI_API_KEY="your-openai-api-key"

# Optional for Anthropic-specific tests
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optional - will use temporary directory if not set
export TRAINLOOP_DATA_FOLDER="./trainloop/data"
```

### 3. Install Browser Dependencies (for Browser Use tests)

```bash
# Install playwright browsers
playwright install chromium
```

## 🚀 Running Tests

### Quick Start - Simple Example

```bash
# Run the simple example (requires OPENAI_API_KEY)
poetry run python example_integration_test.py
```

This will:
- Make a few API calls using different libraries
- Show captured data in JSONL files
- Verify gzip response handling

### Run All Integration Tests

```bash
# Run comprehensive test suite
poetry run python tests/integration/run_all_integration_tests.py
```

This will:
- Check environment and dependencies
- Run all available integration tests
- Provide detailed summary and recommendations

### Run Individual Test Suites

```bash
# Core HTTP libraries
poetry run python tests/integration/test_real_api_calls.py

# Browser Use integration
poetry run python tests/integration/test_browser_use_integration.py

# Other LLM libraries
poetry run python tests/integration/test_other_llm_libraries.py
```

### Run with Pytest

```bash
# Run specific test classes
poetry run pytest tests/integration/test_real_api_calls.py::TestHttpxIntegration -v

# Run all integration tests
poetry run pytest tests/integration/ -v

# Run with markers
poetry run pytest tests/integration/ -m "not browser_use" -v
```

## 📊 What Gets Tested

### HTTP Libraries
- ✅ **httpx** (sync and async)
- ✅ **requests**
- ✅ **http.client**

### LLM Frameworks & SDKs
- ✅ **OpenAI Python SDK** (sync and async)
- ✅ **Anthropic Python SDK** (sync and async)
- ✅ **LangChain** (OpenAI and Anthropic integrations)
- ✅ **LiteLLM** (universal LLM interface)
- ✅ **Instructor** (structured outputs)
- ✅ **Browser Use** (AI browser automation)

### LLM Providers
- ✅ **OpenAI** (GPT models)
- ✅ **Anthropic** (Claude models)

### Special Cases
- ✅ **Gzipped responses** (compressed API responses)
- ✅ **Multiple API calls** in single session
- ✅ **Mixed library usage** (manual + framework calls)
- ✅ **Custom tags** for call tracking
- ✅ **Error handling** and edge cases

## 📋 Test Results Validation

Each test validates that:

1. **API calls succeed** - The underlying library call works
2. **JSONL files are created** - Files appear in the data directory
3. **Correct structure** - Each entry has required fields:
   - `durationMs`, `input`, `output`, `model`, `modelParams`
   - `startTimeMs`, `endTimeMs`, `url`, `location`
4. **Proper content** - Input/output data is correctly captured
5. **Tags are preserved** - Custom tags are maintained
6. **Provider detection** - Correct API endpoints are identified

## 🐛 Troubleshooting

### No JSONL Files Created

1. **Check API keys**: Ensure `OPENAI_API_KEY` is set correctly
2. **Check data folder**: Verify `TRAINLOOP_DATA_FOLDER` is set or temporary directory permissions
3. **Check SDK initialization**: Ensure `tl.collect()` is called before API calls
4. **Check network**: Verify internet connectivity to API endpoints

### Tests Skipped

- **Missing dependencies**: Install optional libraries as needed
- **Missing API keys**: Set required environment variables
- **Platform issues**: Some tests may require specific OS features

### API Rate Limits

- Tests use minimal token counts to reduce costs
- Add delays between tests if hitting rate limits
- Consider using different API keys for different test suites

## 🔍 Understanding Results

### Expected Outputs

When tests pass, you should see:
```
🎉 All tests passed! The instrumentation is working correctly.
```

### JSONL File Structure

Example captured entry:
```json
{
  "durationMs": 1250,
  "tag": "test-httpx-sync",
  "input": [{"role": "user", "content": "Say hello"}],
  "output": {"content": "Hello! How can I help you today?"},
  "model": "gpt-4o-mini",
  "modelParams": {"max_tokens": 10},
  "startTimeMs": 1703123456789,
  "endTimeMs": 1703123458039,
  "url": "https://api.openai.com/v1/chat/completions",
  "location": {"file": "/path/to/test.py", "lineNumber": "42"}
}
```

## 📈 Coverage Matrix

| Library | OpenAI | Anthropic | Sync | Async | Gzip | Tags |
|---------|--------|-----------|------|-------|------|------|
| httpx | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| requests | ✅ | ✅ | ✅ | N/A | ✅ | ✅ |
| http.client | ✅ | ✅ | ✅ | N/A | ✅ | ✅ |
| OpenAI SDK | ✅ | N/A | ✅ | ✅ | ✅ | ✅ |
| Anthropic SDK | N/A | ✅ | ✅ | ✅ | ✅ | ✅ |
| LangChain | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| LiteLLM | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Instructor | ✅ | N/A | ✅ | ✅ | ✅ | ✅ |
| Browser Use | ✅ | ✅ | N/A | ✅ | ✅ | ✅ |

## 🤝 Contributing

To add new integration tests:

1. **Create test class** following existing patterns
2. **Use IntegrationTestHarness** for consistent JSONL validation
3. **Add require_* decorators** for dependencies
4. **Test both success and failure cases**
5. **Update coverage matrix** in this README
6. **Add to run_all_integration_tests.py**

### Test Class Template

```python
class TestNewLibraryIntegration:
    @require_library("new_library")
    @require_openai_key()
    def test_new_library_basic(self):
        with IntegrationTestHarness("new_library") as harness:
            # Make API call using new library
            # ...
            
            # Validate JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1
            assert harness.validate_entry(entries[0], expected_model="gpt-4o-mini")
```

## 📞 Support

If integration tests fail:

1. **Check the debug output** for specific error messages
2. **Verify environment setup** using the test runner
3. **Run individual tests** to isolate issues
4. **Check API quotas and rate limits**
5. **Review network connectivity** to API endpoints

The integration tests are designed to be comprehensive and should catch any issues with the instrumentation across different usage patterns and libraries.