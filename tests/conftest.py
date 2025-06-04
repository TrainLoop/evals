"""
Pytest configuration and shared fixtures for TrainLoop tests.
"""

import tempfile
import shutil
from pathlib import Path
from typing import Generator
import json
import pytest
import yaml

# Test markers
pytest_markers = [
    "unit: Fast unit tests",
    "integration: End-to-end integration tests",
    "slow: Tests that take longer to run",
    "judge: Tests that involve LLM judge functionality",
    "cli: Tests for CLI commands",
]


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory that gets cleaned up after test."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_config() -> dict:
    """Sample trainloop configuration for testing."""
    return {
        "trainloop": {
            "data_folder": "data",
            "host_allowlist": ["api.openai.com", "api.anthropic.com"],
            "log_level": "info",
            "judge": {
                "models": ["openai/gpt-4o"],
                "calls_per_model_per_claim": 1,  # Faster for tests
                "temperature": 0.5,
            },
        }
    }


@pytest.fixture
def sample_jsonl_data() -> list:
    """Sample JSONL data for testing evaluations."""
    return [
        {
            "input": [{"role": "user", "content": "What is Python?"}],
            "output": {"content": "Python is a programming language."},
            "metadata": {
                "tag": "python-questions",
                "timestamp": "2024-01-01T00:00:00Z",
            },
        },
        {
            "input": [{"role": "user", "content": "How do I write a loop?"}],
            "output": {"content": "Use a for loop: for i in range(10):"},
            "metadata": {
                "tag": "python-questions",
                "timestamp": "2024-01-01T00:01:00Z",
            },
        },
    ]


@pytest.fixture
def mock_project(temp_dir: Path, sample_config: dict, sample_jsonl_data: list) -> Path:
    """Create a mock TrainLoop project structure for testing."""
    project_dir = temp_dir / "test_project"

    # Create directory structure
    trainloop_dir = project_dir / "trainloop"
    trainloop_dir.mkdir(parents=True)

    (trainloop_dir / "data").mkdir()
    (trainloop_dir / "data" / "events").mkdir()
    (trainloop_dir / "data" / "results").mkdir()

    (trainloop_dir / "eval").mkdir()
    (trainloop_dir / "eval" / "metrics").mkdir()
    (trainloop_dir / "eval" / "suites").mkdir()

    # Create config file
    config_path = trainloop_dir / "trainloop.config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(sample_config, f)

    # Create sample data files
    events_dir = trainloop_dir / "data" / "events"
    with open(events_dir / "python-questions.jsonl", "w", encoding="utf-8") as f:
        for item in sample_jsonl_data:
            f.write(json.dumps(item) + "\n")

    # Create sample metric
    metrics_dir = trainloop_dir / "eval" / "metrics"
    with open(metrics_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    with open(metrics_dir / "test_metric.py", "w", encoding="utf-8") as f:
        f.write(
            '''
from ...types import Sample

def test_metric(sample: Sample) -> int:
    """Simple test metric."""
    return 1 if len(sample.output.get("content", "")) > 10 else 0
'''
        )

    return project_dir


@pytest.fixture
def scaffold_path() -> Path:
    """Path to the actual scaffold directory."""
    return Path(__file__).parent.parent / "cli" / "trainloop_cli" / "scaffold"


@pytest.fixture
def registry_path() -> Path:
    """Path to the registry directory."""
    return Path(__file__).parent.parent / "registry"
