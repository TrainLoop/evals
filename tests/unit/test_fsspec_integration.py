"""Tests for fsspec integration in CLI and SDK."""

import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytest

from trainloop_cli.eval_core.runner import _write_results
from trainloop_cli.eval_core._trace_helpers import write_trace_log, ensure_trace_dir
from trainloop_cli.eval_core.types import Result, Sample
from trainloop_cli.commands.benchmark.storage import save_benchmark_results
from trainloop_cli.commands.benchmark.types import BenchmarkResult


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


@pytest.mark.unit
def test_write_results_with_fsspec(tmp_path, sample_result):
    """Test that _write_results uses fsspec for file operations."""
    results = [sample_result]

    # Mock fsspec to test S3 path handling
    mock_fs = Mock()
    mock_open_spec = Mock()
    mock_open_spec.fs = mock_fs

    # Mock the file handle
    mock_file = MagicMock()
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("fsspec.open") as mock_open:
        # First call returns the spec object for fs access
        # Second call returns the file handle for writing
        mock_open.side_effect = [mock_open_spec, mock_file]

        _write_results("test_suite", results, tmp_path)

        # Verify fsspec was used correctly
        assert mock_open.call_count == 2
        mock_open.assert_any_call(str(tmp_path / "test_suite.jsonl"), "a")
        mock_open.assert_any_call(
            str(tmp_path / "test_suite.jsonl"), "a", encoding="utf-8"
        )
        mock_fs.makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)

        # Verify data was written
        expected_data = (
            json.dumps(
                {
                    "metric": "test_metric",
                    "sample": {
                        "duration_ms": 100,
                        "tag": "test_sample",
                        "input": [{"role": "user", "content": "Hello"}],
                        "output": {"content": "Hi there!"},
                        "model": "gpt-3.5-turbo",
                        "model_params": {"temperature": 0.7, "max_tokens": 100},
                        "start_time_ms": 1700000000000,
                        "end_time_ms": 1700000000100,
                        "url": "https://api.openai.com/v1/chat/completions",
                        "location": {"tag": "test", "lineNumber": "1"},
                    },
                    "passed": 1,
                    "reason": None,
                },
                default=str,
            )
            + "\n"
        )

        mock_file.write.assert_called_once_with(expected_data)


@pytest.mark.unit
def test_write_results_with_s3_path_mock(sample_result):
    """Test that _write_results would work with S3 paths (mocked)."""
    results = [sample_result]
    # Use string directly since Path might not handle S3 URLs properly
    s3_path = "s3://my-bucket/results/test"

    # Mock fsspec for S3
    mock_fs = Mock()
    mock_open_spec = Mock()
    mock_open_spec.fs = mock_fs

    mock_file = MagicMock()
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("fsspec.open") as mock_open:
        # First call returns the spec object for fs access
        # Second call returns the file handle for writing
        mock_open.side_effect = [mock_open_spec, mock_file]

        _write_results("test_suite", results, s3_path)

        # Verify S3 path was handled correctly
        assert mock_open.call_count == 2
        mock_open.assert_any_call("s3://my-bucket/results/test/test_suite.jsonl", "a")
        mock_open.assert_any_call(
            "s3://my-bucket/results/test/test_suite.jsonl", "a", encoding="utf-8"
        )
        mock_fs.makedirs.assert_called_once_with(
            "s3://my-bucket/results/test", exist_ok=True
        )


@pytest.mark.unit
def test_ensure_trace_dir_with_fsspec(tmp_path):
    """Test that ensure_trace_dir uses fsspec."""
    with patch.dict("os.environ", {"TRAINLOOP_DATA_FOLDER": str(tmp_path)}):
        mock_fs = Mock()
        mock_open_spec = Mock()
        mock_open_spec.fs = mock_fs

        with patch("fsspec.open") as mock_open:
            mock_open.return_value = mock_open_spec

            trace_dir = ensure_trace_dir()

            # Verify fsspec was used
            mock_open.assert_called_once_with(
                str(tmp_path / "judge_traces/.placeholder"), "w"
            )
            mock_fs.makedirs.assert_called_once_with(
                str(tmp_path / "judge_traces"), exist_ok=True
            )
            assert trace_dir == tmp_path / "judge_traces"


@pytest.mark.unit
def test_write_trace_log_with_fsspec(tmp_path):
    """Test that write_trace_log uses fsspec."""
    trace_events = [
        {"event": "test1", "timestamp": "2024-01-01T00:00:00Z"},
        {"event": "test2", "timestamp": "2024-01-01T00:00:01Z"},
    ]

    mock_file = MagicMock()
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("fsspec.open", return_value=mock_file) as mock_open:
        write_trace_log("test-trace-id", trace_events, tmp_path)

        # Verify fsspec.open was called
        mock_open.assert_called_once_with(
            str(tmp_path / "test-trace-id.jsonl"), "w", encoding="utf-8"
        )

        # Verify events were written (json.dump might write in multiple chunks)
        assert mock_file.write.call_count >= len(
            trace_events
        )  # At least one write per event


@pytest.mark.unit
def test_save_benchmark_results_with_fsspec(tmp_path, sample_result):
    """Test that save_benchmark_results uses fsspec."""
    benchmark_results = [
        BenchmarkResult(
            original_result=sample_result,
            provider_results={
                "openai/gpt-4": {
                    "response": "Test response",
                    "latency_ms": 150,
                    "cost": 0.001,
                    "error": None,
                    "verdict": 1,
                    "metric_results": {"test_metric": {"passed": 1, "error": None}},
                }
            },
            timestamp=datetime.now().isoformat(),
        )
    ]

    mock_fs = Mock()
    mock_open_spec = Mock()
    mock_open_spec.fs = mock_fs

    mock_file = MagicMock()
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("fsspec.open") as mock_open:
        # First call returns the spec object for fs access
        # Subsequent calls return the file handle for writing
        mock_open.side_effect = [mock_open_spec, mock_file]

        _ = save_benchmark_results(benchmark_results, tmp_path, ["openai/gpt-4"])

        # Verify fsspec was used
        assert (
            mock_open.call_count >= 2
        )  # At least one for dir check and one for file write
        mock_fs.makedirs.assert_called_once()

        # Verify some data was written
        assert mock_file.write.called
