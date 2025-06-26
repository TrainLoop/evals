"""Tests for the benchmark command."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import shutil
import yaml
import pytest

from trainloop_cli.commands.benchmark import (
    _load_latest_results,
    _validate_provider_keys,
    _save_benchmark_results,
    BenchmarkResult,
)
from trainloop_cli.eval_core.types import Result, Sample


@pytest.fixture
def sample_result():
    """Create a sample Result object for testing."""
    sample = Sample(
        duration_ms=100,
        tag="test_sample",
        input=[{"role": "user", "content": "Hello"}],
        output={"content": "Hi there!"},
        model="gpt-3.5-turbo",
        model_params={"temperature": 0.7, "max_tokens": 100},
        start_time_ms=1700000000000,
        end_time_ms=1700000000100,
        url="https://api.openai.com/v1/chat/completions",
        location={"tag": "test", "lineNumber": "1"},
    )

    return Result(metric="test_metric", sample=sample, passed=1, reason=None)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    # Create directories
    (tmp_path / "data" / "results" / "2024-01-01_12-00-00").mkdir(parents=True)
    (tmp_path / "data" / "benchmarks").mkdir(parents=True)

    # Create config file
    config = {
        "trainloop": {
            "data_folder": "data",
            "benchmark": {
                "providers": ["openai/gpt-4", "anthropic/claude-3-sonnet-20240229"],
                "temperature": 0.5,
                "max_samples": 10,
            },
        }
    }

    with (tmp_path / "trainloop.config.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(config, f)

    return tmp_path


@pytest.mark.benchmark
@pytest.mark.unit
def test_load_latest_results(temp_project: Path, sample_result: Result):
    """Test loading latest evaluation results."""
    # Create test results
    results_dir = temp_project / "data" / "results" / "2024-01-01_12-00-00"

    result_data = {
        "metric": sample_result.metric,
        "sample": {
            "duration_ms": sample_result.sample.duration_ms,
            "tag": sample_result.sample.tag,
            "input": sample_result.sample.input,
            "output": sample_result.sample.output,
            "model": sample_result.sample.model,
            "model_params": sample_result.sample.model_params,
            "start_time_ms": sample_result.sample.start_time_ms,
            "end_time_ms": sample_result.sample.end_time_ms,
            "url": sample_result.sample.url,
            "location": sample_result.sample.location,
        },
        "passed": sample_result.passed,
        "reason": sample_result.reason,
    }

    with (results_dir / "test_suite.jsonl").open("w") as f:
        f.write(json.dumps(result_data) + "\n")

    # Load results
    results = _load_latest_results(temp_project)

    assert "test_suite" in results
    assert len(results["test_suite"]) == 1
    assert results["test_suite"][0].metric == "test_metric"


@pytest.mark.benchmark
@pytest.mark.unit
def test_validate_provider_keys():
    """Test provider API key validation."""
    providers = ["openai/gpt-4", "anthropic/claude-3-sonnet-20240229", "unknown/model"]

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        valid_providers = _validate_provider_keys(providers)

        # Should have openai and unknown (unknown providers are assumed valid)
        assert len(valid_providers) == 2
        assert "openai/gpt-4" in valid_providers
        assert "unknown/model" in valid_providers
        assert "anthropic/claude-3-sonnet-20240229" not in valid_providers


@pytest.mark.benchmark
@pytest.mark.unit
def test_save_benchmark_results(temp_project: Path, sample_result: Result):
    """Test saving benchmark results."""
    benchmark_results = [
        BenchmarkResult(
            original_result=sample_result,
            provider_results={
                "openai/gpt-4": {
                    "response": "Test response",
                    "latency_ms": 150,
                    "cost": 0.001,
                    "error": None,
                }
            },
            timestamp=datetime.now().isoformat(),
        )
    ]

    output_dir = _save_benchmark_results(
        benchmark_results, temp_project, ["openai/gpt-4"]
    )

    # Check that files were created
    assert output_dir.exists()
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "results.jsonl").exists()

    # Check metadata
    with (output_dir / "metadata.json").open() as f:
        metadata = json.load(f)
        assert metadata["providers"] == ["openai/gpt-4"]
        assert metadata["total_samples"] == 1

    # Check results
    with (output_dir / "results.jsonl").open() as f:
        line = f.readline()
        result = json.loads(line)
        assert "original_result" in result
        assert "provider_results" in result
        assert result["provider_results"]["openai/gpt-4"]["response"] == "Test response"


@pytest.mark.benchmark
@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_single_result():
    """Test benchmarking a single result (mocked)."""
    from trainloop_cli.commands.benchmark import _benchmark_single_result

    # Create a sample result
    sample = Sample(
        duration_ms=100,
        tag="test",
        input=[{"role": "user", "content": "Test"}],
        output={"content": "Response"},
        model="gpt-3.5-turbo",
        model_params={"temperature": 0.7},
        start_time_ms=1700000000000,
        end_time_ms=1700000000100,
        url="https://api.openai.com",
        location={"tag": "test", "lineNumber": "1"},
    )

    result = Result(metric="test", sample=sample, passed=1)

    # Mock litellm response
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Mocked response"))]
    mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20)

    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        mock_acompletion.return_value = mock_response

        with patch("litellm.completion_cost", return_value=0.001):
            provider_results = await _benchmark_single_result(
                result, ["openai/gpt-4"], temperature=0.7, max_tokens=100
            )

    assert "openai/gpt-4" in provider_results
    assert provider_results["openai/gpt-4"]["response"] == "Mocked response"
    assert provider_results["openai/gpt-4"]["error"] is None
    assert provider_results["openai/gpt-4"]["cost"] == 0.001


@pytest.mark.benchmark
@pytest.mark.cli
def test_benchmark_command_no_results(temp_project: Path):
    """Test benchmark command when no results exist."""
    # Remove results directory
    shutil.rmtree(temp_project / "data" / "results")

    with patch("trainloop_cli.commands.benchmark.find_root", return_value=temp_project):
        with patch("sys.exit") as mock_exit:
            from trainloop_cli.commands.benchmark import benchmark_command

            benchmark_command()

            # Should exit with error
            mock_exit.assert_called_once_with(1)
