"""
Shared test fixtures and configuration for TrainLoop SDK tests.
"""

import os
import tempfile
import shutil
import json
from unittest.mock import patch
from typing import Generator, Dict, Any
import logging
import yaml
import pytest


# Disable logging during tests unless explicitly needed
logging.disable(logging.CRITICAL)


@pytest.fixture(scope="session", autouse=True)
def setup_trainloop_instrumentation():
    """
    IMPORTANT: This fixture must be called before any tests run because we assume that collect is called BEFORE the openai sdk is created. This is the only way to ensure that these work in pytests.
    Session-level fixture that automatically sets up TrainLoop instrumentation
    before any tests run. This ensures that HTTP libraries are instrumented
    before they are imported by test modules.
    """
    # Set up a temporary data folder for the session
    temp_dir = tempfile.mkdtemp(prefix="trainloop_test_session_")
    os.environ["TRAINLOOP_DATA_FOLDER"] = temp_dir

    # Install instrumentation globally for the test session
    # ------------------------------------------------------------------
    # Some pytest plugins (e.g. `pytest-requests`) may import HTTP libraries
    # like `requests` or `httpx` *before* this fixture runs.  The TrainLoop SDK
    # requires that those libraries are **not** imported prior to calling
    # `collect()` so it can monkey-patch them.  If they are already present in
    # `sys.modules`, `collect()` raises a RuntimeError.
    #
    # For unit testing purposes we don’t actually care about patching outbound
    # HTTP – we just want the SDK initialisation to succeed.  Therefore we
    # remove any pre-imported libraries from `sys.modules` before calling
    # `collect()`.  They will be re-imported later after the patches have been
    # installed.
    import sys

    for _mod in ("requests", "httpx", "openai"):
        sys.modules.pop(_mod, None)

    # ------------------------------------------------------------------
    # Patch TrainLoop to *skip* HTTP instrumentation in unit tests – we only
    # need the SDK initialised; we do not actually exercise outbound HTTP.
    import trainloop_llm_logging.register as tl_register

    # Replace the real install_patches with a no-op
    tl_register.install_patches = lambda _exporter: None  # type: ignore[assignment]

    import trainloop_llm_logging as tl

    tl.collect()

    yield  # Run all tests

    # Cleanup (optional - temp dirs are cleaned up automatically)
    if "TRAINLOOP_DATA_FOLDER" in os.environ:
        del os.environ["TRAINLOOP_DATA_FOLDER"]


@pytest.fixture
def temp_data_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_data_dir) -> Generator[str, Any, Any]:
    """Create a temporary config file."""
    config_path = os.path.join(temp_data_dir, "trainloop.config.yaml")
    config_data = {
        "trainloop": {
            "data_folder": "./data",
            "host_allowlist": ["api.openai.com", "api.anthropic.com"],
            "log_level": "debug",
        }
    }
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    yield config_path


@pytest.fixture
def mock_env_vars() -> Generator[None, None, None]:
    """Clean up and restore environment variables."""
    original_env = os.environ.copy()

    # Clear all TRAINLOOP_ variables
    for key in list(os.environ.keys()):
        if key.startswith("TRAINLOOP_"):
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_file_exporter():
    """Mock FileExporter for testing without file I/O."""
    from trainloop_llm_logging.exporter import FileExporter

    with patch.object(FileExporter, "__init__", lambda self: None):
        exporter = FileExporter()
        yield exporter


@pytest.fixture
def sample_llm_request() -> Dict[str, Any]:
    """Sample OpenAI-style request."""
    return {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
        ],
        "temperature": 0.7,
        "max_tokens": 100,
    }


@pytest.fixture
def sample_llm_response() -> Dict[str, Any]:
    """Sample OpenAI-style response."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I'm doing well, thank you! How can I help you today?",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35},
    }


@pytest.fixture
def sample_anthropic_request() -> Dict[str, Any]:
    """Sample Anthropic-style request."""
    return {
        "model": "claude-3-opus-20240229",
        "messages": [{"role": "user", "content": "Hello, Claude!"}],
        "max_tokens": 100,
    }


@pytest.fixture
def sample_anthropic_response() -> Dict[str, Any]:
    """Sample Anthropic-style response."""
    return {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello! It's nice to meet you."}],
        "model": "claude-3-opus-20240229",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 8},
    }


@pytest.fixture
def sample_collected_data():
    """Sample collected data structure."""
    return {
        "durationMs": 1234,
        "tag": "test-tag",
        "input": [{"role": "user", "content": "Hello!"}],
        "output": {"role": "assistant", "content": "Hi there!"},
        "model": "gpt-4o-mini",
        "modelParams": {"temperature": 0.7},
        "startTimeMs": 1000000,
        "endTimeMs": 1001234,
        "url": "https://api.openai.com/v1/chat/completions",
        "location": {"file": "test.py", "lineNumber": "42"},
    }


@pytest.fixture
def mock_time(monkeypatch):
    """Mock time.time() for consistent timestamps."""
    current_time = 1700000000.0

    def mock_time_func():
        nonlocal current_time
        result = current_time
        current_time += 0.1  # Increment by 100ms each call
        return result

    import time

    monkeypatch.setattr(time, "time", mock_time_func)
    return mock_time_func


@pytest.fixture
def corrupt_registry_file(temp_data_dir) -> str:
    """Create a corrupt registry file."""
    registry_path = os.path.join(temp_data_dir, "_registry.json")
    with open(registry_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json")
    return registry_path


@pytest.fixture
def valid_registry_file(temp_data_dir) -> str:
    """Create a valid registry file."""
    registry_path = os.path.join(temp_data_dir, "_registry.json")
    registry_data = {
        "schema": 1,
        "files": {
            "test.py": {
                "42": {
                    "lineNumber": "42",
                    "tag": "existing-tag",
                    "firstSeen": "2024-01-01T00:00:00Z",
                    "lastSeen": "2024-01-01T00:00:00Z",
                    "count": 1,
                }
            }
        },
    }
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry_data, f)
    return registry_path


@pytest.fixture(autouse=True)
def reset_singleton_state():
    """Reset any singleton state between tests."""
    # This will be useful for resetting global state
    yield
    # Cleanup after test


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "edge_case: Edge case tests")
    config.addinivalue_line(
        "markers", "requires_network: Tests that require network access"
    )
    config.addinivalue_line(
        "markers", "requires_fs: Tests that require filesystem access"
    )
