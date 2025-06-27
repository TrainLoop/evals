"""Tests for fsspec integration in the SDK store module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from trainloop_llm_logging.store import update_registry, save_samples
from trainloop_llm_logging.types import CollectedSample, LLMCallLocation


@pytest.fixture
def sample_location():
    """Create a sample LLM call location."""
    return LLMCallLocation(
        file="test.py", lineNumber="10"  # lineNumber is a string in the type definition
    )


@pytest.fixture
def sample_collected():
    """Create a sample CollectedSample."""
    return CollectedSample(
        durationMs=100,
        tag="test_tag",
        input=[{"role": "user", "content": "Hello"}],
        output={"content": "Hi there!"},
        model="gpt-3.5-turbo",
        modelParams={"temperature": 0.7},
        startTimeMs=1700000000000,
        endTimeMs=1700000000100,
        url="https://api.openai.com/v1/chat/completions",
        location={"file": "test.py", "lineNumber": "10"},
    )


@pytest.mark.unit
def test_update_registry_with_fsspec(tmp_path, sample_location):
    """Test that update_registry uses fsspec for file operations."""
    data_dir = str(tmp_path)

    # Mock fsspec for read operation
    mock_fs_read = Mock()
    mock_fs_read.exists.return_value = False  # File doesn't exist yet

    mock_open_spec_read = Mock()
    mock_open_spec_read.fs = mock_fs_read

    # Mock fsspec for write operation
    mock_fs_write = Mock()

    mock_open_spec_write = Mock()
    mock_open_spec_write.fs = mock_fs_write

    mock_file = MagicMock()
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)

    with patch("fsspec.open") as mock_open:
        # Different calls return different objects
        call_count = 0

        def open_side_effect(path, mode="r", **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call for read fs check
                return mock_open_spec_read
            elif call_count == 2:  # Second call for write fs check
                return mock_open_spec_write
            else:  # Third call for actual file write
                return mock_file

        mock_open.side_effect = open_side_effect

        update_registry(data_dir, sample_location, "test_tag")

        # Verify fsspec was used correctly
        assert mock_open.call_count >= 3
        mock_fs_read.exists.assert_called_once_with(str(tmp_path / "_registry.json"))
        mock_fs_write.makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)

        # Verify registry content was written
        written_data = mock_file.write.call_args[0][0]
        registry = json.loads(written_data)
        assert registry["schema"] == 1
        assert "test.py" in registry["files"]
        # JSON serialization converts integer keys to strings
        assert (
            "10" in registry["files"]["test.py"] or 10 in registry["files"]["test.py"]
        )
        key = "10" if "10" in registry["files"]["test.py"] else 10
        assert registry["files"]["test.py"][key]["tag"] == "test_tag"


@pytest.mark.unit
def test_update_registry_existing_file(tmp_path, sample_location):
    """Test updating registry when file already exists."""
    data_dir = str(tmp_path)
    existing_registry = {
        "schema": 1,
        "files": {
            "test.py": {
                "10": {  # JSON keys are strings
                    "lineNumber": 10,
                    "tag": "old_tag",
                    "firstSeen": "2024-01-01T00:00:00+00:00",
                    "lastSeen": "2024-01-01T00:00:00+00:00",
                    "count": 1,
                }
            }
        },
    }

    # Mock fsspec
    mock_fs = Mock()
    mock_fs.exists.return_value = True  # File exists

    mock_open_spec = Mock()
    mock_open_spec.fs = mock_fs

    # Mock reading existing file
    mock_read_file = MagicMock()
    mock_read_file.__enter__ = Mock(return_value=mock_read_file)
    mock_read_file.__exit__ = Mock(return_value=None)
    mock_read_file.read.return_value = json.dumps(existing_registry)

    # Mock writing file
    mock_write_file = MagicMock()
    mock_write_file.__enter__ = Mock(return_value=mock_write_file)
    mock_write_file.__exit__ = Mock(return_value=None)

    with patch("fsspec.open") as mock_open:
        # Different calls return different objects
        call_count = 0

        def open_side_effect(path, mode="r"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call for fs check
                return mock_open_spec
            elif call_count == 2:  # Second call for reading
                return mock_read_file
            elif call_count == 3:  # Third call for fs write check
                return mock_open_spec
            else:  # Fourth call for writing
                return mock_write_file

        mock_open.side_effect = open_side_effect

        update_registry(data_dir, sample_location, "new_tag")

        # Verify files were opened correctly
        assert mock_open.call_count >= 3

        # Verify updated content
        written_data = mock_write_file.write.call_args[0][0]
        registry = json.loads(written_data)
        # Check both string and int keys
        key = "10" if "10" in registry["files"]["test.py"] else 10
        assert registry["files"]["test.py"][key]["tag"] == "new_tag"
        assert registry["files"]["test.py"][key]["count"] == 2


@pytest.mark.unit
def test_save_samples_with_fsspec(tmp_path, sample_collected):
    """Test that save_samples uses fsspec for file operations."""
    data_dir = str(tmp_path)
    samples = [sample_collected]

    # Mock time to control file naming
    with patch("time.time", return_value=1700000000):
        mock_fs = Mock()
        mock_open_spec = Mock()
        mock_open_spec.fs = mock_fs

        # Mock glob to return no existing files
        with patch.object(Path, "glob", return_value=[]):
            mock_file = MagicMock()
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)

            with patch("fsspec.open") as mock_open:
                # First call for directory check, second for file write
                mock_open.side_effect = [mock_open_spec, mock_file]

                save_samples(data_dir, samples)

                # Verify fsspec was used
                assert mock_open.call_count >= 2
                mock_fs.makedirs.assert_called_once_with(
                    str(tmp_path / "events"), exist_ok=True
                )

                # Verify file was opened with correct timestamp
                expected_path = str(tmp_path / "events" / "1700000000000.jsonl")
                mock_open.assert_any_call(expected_path, "a", encoding="utf-8")

                # Verify sample was written
                written_data = mock_file.write.call_args[0][0]
                assert json.loads(written_data.strip()) == sample_collected


@pytest.mark.unit
def test_save_samples_with_s3_path_mock(sample_collected):
    """Test that save_samples would work with S3 paths (mocked)."""
    s3_path = "s3://my-bucket/data"
    samples = [sample_collected]

    with patch("time.time", return_value=1700000000):
        mock_fs = Mock()
        mock_open_spec = Mock()
        mock_open_spec.fs = mock_fs

        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)

        with patch("fsspec.open") as mock_open:
            # First call for directory check, second for file write
            mock_open.side_effect = [mock_open_spec, mock_file]

            save_samples(s3_path, samples)

            # Verify fsspec was used
            assert mock_open.call_count >= 2
            mock_fs.makedirs.assert_called_once_with(
                "s3://my-bucket/data/events", exist_ok=True
            )

            # Verify S3 path handling
            expected_s3_path = "s3://my-bucket/data/events/1700000000000.jsonl"
            mock_open.assert_any_call(expected_s3_path, "a", encoding="utf-8")


@pytest.mark.unit
def test_save_samples_empty_list(tmp_path):
    """Test that save_samples handles empty sample list correctly."""
    data_dir = str(tmp_path)

    # Should not create any files or directories
    with patch("fsspec.filesystem") as mock_fs_func:
        with patch("fsspec.open") as mock_open:
            save_samples(data_dir, [])

            # Verify nothing was called
            mock_fs_func.assert_not_called()
            mock_open.assert_not_called()
