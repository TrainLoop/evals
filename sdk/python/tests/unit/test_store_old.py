"""
Unit tests for the store module.
"""

import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from trainloop_llm_logging.store import save_samples, update_registry, _now_iso
from trainloop_llm_logging.types import CollectedSample, LLMCallLocation


class TestStore:
    """Test the store functions."""

    def test_now_iso_returns_utc_timestamp(self):
        """Test that _now_iso returns a valid UTC ISO timestamp."""
        timestamp = _now_iso()

        # Should be able to parse it back
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed.tzinfo == timezone.utc

        # Should be in the expected format
        assert "T" in timestamp
        assert timestamp.count(":") >= 2

    @patch("trainloop_llm_logging.store.fsspec.filesystem")
    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_creates_new_registry(
        self, mock_fsspec_open, mock_filesystem
    ):
        """Test update_registry creates a new registry if none exists."""
        # Set up mocks
        mock_fs = MagicMock()
        mock_filesystem.return_value = mock_fs
        mock_fs.exists.return_value = False

        # Mock file write
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)
        mock_fsspec_open.return_value = mock_file

        # Call update_registry
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "test-tag")

        # Should write a new registry
        mock_fsspec_open.assert_called_once_with("/tmp/data/_registry.json", "w")
        written_data = json.loads(mock_file.write.call_args[0][0])

        assert written_data["schema"] == 1
        assert "test.py" in written_data["files"]
        assert "10" in written_data["files"]["test.py"]

        entry = written_data["files"]["test.py"]["10"]
        assert entry["tag"] == "test-tag"
        assert entry["count"] == 1
        assert "firstSeen" in entry
        assert "lastSeen" in entry

    @patch("trainloop_llm_logging.store.fsspec.filesystem")
    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_updates_existing_entry(
        self, mock_fsspec_open, mock_filesystem
    ):
        """Test update_registry updates an existing entry."""
        # Set up existing registry data
        existing_registry = {
            "schema": 1,
            "files": {
                "test.py": {
                    "10": {
                        "tag": "old-tag",
                        "firstSeen": "2024-01-01T00:00:00Z",
                        "lastSeen": "2024-01-01T00:00:00Z",
                        "count": 5,
                    }
                }
            },
        }

        # Set up mocks
        mock_fs = MagicMock()
        mock_filesystem.return_value = mock_fs
        mock_fs.exists.return_value = True

        # Mock file read
        mock_read_file = MagicMock()
        mock_read_file.__enter__ = MagicMock(return_value=mock_read_file)
        mock_read_file.__exit__ = MagicMock(return_value=None)
        mock_read_file.read.return_value = json.dumps(existing_registry)

        # Mock file write
        mock_write_file = MagicMock()
        mock_write_file.__enter__ = MagicMock(return_value=mock_write_file)
        mock_write_file.__exit__ = MagicMock(return_value=None)

        mock_fsspec_open.side_effect = [mock_read_file, mock_write_file]

        # Call update_registry with same location but different tag
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "new-tag")

        # Should update the entry
        assert mock_fsspec_open.call_count == 2
        written_data = json.loads(mock_write_file.write.call_args[0][0])

        entry = written_data["files"]["test.py"]["10"]
        assert entry["tag"] == "new-tag"  # Tag should be updated
        assert entry["count"] == 6  # Count should be incremented
        assert entry["firstSeen"] == "2024-01-01T00:00:00Z"  # First seen preserved
        assert entry["lastSeen"] != "2024-01-01T00:00:00Z"  # Last seen updated

    @patch("trainloop_llm_logging.store.Path")
    def test_update_registry_handles_corrupt_registry(self, mock_path_class):
        """Test update_registry handles corrupt registry files."""
        # Set up mocks
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path
        mock_path.__truediv__.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "invalid json {"

        mock_write = MagicMock()
        mock_path.write_text = mock_write

        # Call update_registry
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "test-tag")

        # Should create a new registry
        mock_write.assert_called_once()
        written_data = json.loads(mock_write.call_args[0][0])

        assert written_data["schema"] == 1
        assert "test.py" in written_data["files"]

    @patch("trainloop_llm_logging.store.Path")
    def test_update_registry_handles_empty_registry(self, mock_path_class):
        """Test update_registry handles empty registry file."""
        # Set up mocks
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path
        mock_path.__truediv__.return_value = mock_path
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "{}"

        mock_write = MagicMock()
        mock_path.write_text = mock_write

        # Call update_registry
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "test-tag")

        # Should initialize the registry structure
        mock_write.assert_called_once()
        written_data = json.loads(mock_write.call_args[0][0])

        assert written_data["schema"] == 1
        assert "files" in written_data

    @patch("trainloop_llm_logging.store.time")
    @patch("trainloop_llm_logging.store.Path")
    def test_save_samples_creates_jsonl_file(self, mock_path_class, mock_time):
        """Test save_samples creates a JSONL file with timestamp."""
        # Set up mocks
        mock_time.time.return_value = 1234567890.123

        # Create a proper mock file handle
        mock_file = MagicMock()
        mock_file.write = MagicMock()

        # Mock the Path operations chain
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path

        # Mock events directory path
        events_path = MagicMock()
        mock_path.__truediv__.return_value = events_path
        events_path.mkdir = MagicMock()
        events_path.glob = MagicMock(return_value=[])  # No existing files

        # Mock the file path
        file_path = MagicMock()
        events_path.__truediv__.return_value = file_path

        # Mock the open context manager
        mock_open_cm = MagicMock()
        mock_open_cm.__enter__.return_value = mock_file
        mock_open_cm.__exit__.return_value = None
        file_path.open.return_value = mock_open_cm

        # Create samples
        samples: list[CollectedSample] = [
            {
                "tag": "test-1",
                "input": [{"role": "user", "content": "Hello"}],
                "output": {"content": "Hi!"},
                "model": "gpt-4",
                "modelParams": {},
                "durationMs": 100,
                "startTimeMs": 1000,
                "endTimeMs": 1100,
                "url": "https://api.openai.com/v1/chat",
                "location": {"file": "test.py", "lineNumber": "10"},
            },
            {
                "tag": "test-2",
                "input": [{"role": "user", "content": "Bye"}],
                "output": {"content": "Goodbye!"},
                "model": "gpt-3.5",
                "modelParams": {"temperature": 0.5},
                "durationMs": 50,
                "startTimeMs": 2000,
                "endTimeMs": 2050,
                "url": "https://api.openai.com/v1/chat",
                "location": {"file": "test.py", "lineNumber": "20"},
            },
        ]

        save_samples("/tmp/data", samples)

        # Verify directory creation
        events_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify file naming
        events_path.__truediv__.assert_called_once_with("1234567890123.jsonl")

        # Verify file was opened correctly
        file_path.open.assert_called_once_with("a", encoding="utf-8")

        # Verify content written
        assert mock_file.write.call_count == 2

        # Check the written content
        written_calls = mock_file.write.call_args_list

        # Check first sample
        line1 = json.loads(written_calls[0][0][0].rstrip("\n"))
        assert line1["tag"] == "test-1"
        assert line1["model"] == "gpt-4"

    @patch("trainloop_llm_logging.store.Path")
    def test_save_samples_handles_empty_list(self, mock_path_class):
        """Test save_samples handles empty sample list."""
        # Set up mocks
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path

        save_samples("/tmp/data", [])

        # Should not create any files
        mock_path.__truediv__.assert_not_called()

    @patch("trainloop_llm_logging.store.Path")
    def test_save_samples_ensures_events_dir_exists(self, mock_path_class):
        """Test save_samples creates events directory if needed."""
        # Set up mocks
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path

        events_path = MagicMock()
        mock_path.__truediv__.return_value = events_path

        file_path = MagicMock()
        events_path.__truediv__.return_value = file_path
        file_path.write_text = MagicMock()

        # Create a sample
        sample: CollectedSample = {
            "tag": "test",
            "input": [],
            "output": {"content": ""},
            "model": "gpt-4",
            "modelParams": {},
            "durationMs": 0,
            "startTimeMs": 0,
            "endTimeMs": 0,
            "url": "",
            "location": {"file": "", "lineNumber": "0"},
        }

        save_samples("/tmp/data", [sample])

        # Should create events directory
        mock_path.__truediv__.assert_called_once_with("events")
        events_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("trainloop_llm_logging.store.Path")
    def test_update_registry_thread_safety(self, mock_path_class):
        """Test registry updates handle concurrent access gracefully."""
        # This test verifies the function completes without errors
        # Real thread safety would require file locking mechanisms

        mock_path = MagicMock()
        mock_path_class.return_value = mock_path
        mock_path.__truediv__.return_value = mock_path
        mock_path.exists.return_value = False
        mock_path.write_text = MagicMock()

        # Multiple updates to same file
        locations = [{"file": "test.py", "lineNumber": str(i)} for i in range(10)]

        for i, loc in enumerate(locations):
            update_registry("/tmp/data", loc, f"tag-{i}")

        # Should have written multiple times
        assert mock_path.write_text.call_count == 10
