"""
Unit tests for the store module with proper fsspec mocking.
"""

import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import threading

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

    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_creates_new_registry(self, mock_fsspec_open):
        """Test update_registry creates a new registry if none exists."""
        # Set up mocks
        mock_fs = MagicMock()
        mock_fs.exists.return_value = False

        # Mock fsspec.open to return object with .fs attribute
        mock_open_file = MagicMock()
        mock_open_file.fs = mock_fs

        # Mock file write
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)

        # Set up side effects for different calls
        def open_side_effect(path, mode="r", **kwargs):
            if mode == "r":
                return mock_open_file
            else:
                return mock_file

        mock_fsspec_open.side_effect = open_side_effect

        # Call update_registry
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "test-tag")

        # Should write a new registry
        assert mock_fsspec_open.call_count == 2  # One for read check, one for write
        written_data = json.loads(mock_file.write.call_args[0][0])

        assert written_data["schema"] == 1
        assert "test.py" in written_data["files"]
        assert "10" in written_data["files"]["test.py"]

        entry = written_data["files"]["test.py"]["10"]
        assert entry["tag"] == "test-tag"
        assert entry["count"] == 1
        assert "firstSeen" in entry
        assert "lastSeen" in entry

    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_updates_existing_entry(self, mock_fsspec_open):
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
        mock_fs.exists.return_value = True

        # Mock fsspec.open to return object with .fs attribute
        mock_open_file = MagicMock()
        mock_open_file.fs = mock_fs

        # Mock file read
        mock_read_file = MagicMock()
        mock_read_file.__enter__ = MagicMock(return_value=mock_read_file)
        mock_read_file.__exit__ = MagicMock(return_value=None)
        mock_read_file.read.return_value = json.dumps(existing_registry)

        # Mock file write
        mock_write_file = MagicMock()
        mock_write_file.__enter__ = MagicMock(return_value=mock_write_file)
        mock_write_file.__exit__ = MagicMock(return_value=None)

        def open_side_effect(path, mode="r", **kwargs):
            if mode == "r":
                if kwargs:  # actual read operation
                    return mock_read_file
                return mock_open_file  # fs check
            else:
                return mock_write_file

        mock_fsspec_open.side_effect = open_side_effect

        # Call update_registry with same location but different tag
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "new-tag")

        # Should update the entry
        assert mock_fsspec_open.call_count >= 3
        written_data = json.loads(mock_write_file.write.call_args[0][0])

        entry = written_data["files"]["test.py"]["10"]
        assert entry["tag"] == "new-tag"  # Tag should be updated
        assert entry["count"] == 6  # Count should be incremented
        assert entry["firstSeen"] == "2024-01-01T00:00:00Z"  # First seen preserved
        assert entry["lastSeen"] != "2024-01-01T00:00:00Z"  # Last seen updated

    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_handles_corrupt_registry(self, mock_fsspec_open):
        """Test update_registry handles corrupt registry files."""
        # Set up mocks
        mock_fs = MagicMock()
        mock_fs.exists.return_value = True

        # Mock fsspec.open to return object with .fs attribute
        mock_open_file = MagicMock()
        mock_open_file.fs = mock_fs

        # Mock file read with invalid JSON
        mock_read_file = MagicMock()
        mock_read_file.__enter__ = MagicMock(return_value=mock_read_file)
        mock_read_file.__exit__ = MagicMock(return_value=None)
        mock_read_file.read.return_value = "invalid json {"

        # Mock file write
        mock_write_file = MagicMock()
        mock_write_file.__enter__ = MagicMock(return_value=mock_write_file)
        mock_write_file.__exit__ = MagicMock(return_value=None)

        def open_side_effect(path, mode="r", **kwargs):
            if mode == "r":
                if kwargs:  # actual read operation
                    return mock_read_file
                return mock_open_file  # fs check
            else:
                return mock_write_file

        mock_fsspec_open.side_effect = open_side_effect

        # Call update_registry
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "test-tag")

        # Should recreate registry
        assert mock_fsspec_open.call_count >= 3
        written_data = json.loads(mock_write_file.write.call_args[0][0])

        assert written_data["schema"] == 1
        assert "test.py" in written_data["files"]

    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_handles_empty_registry(self, mock_fsspec_open):
        """Test update_registry handles empty registry file."""
        # Set up mocks
        mock_fs = MagicMock()
        mock_fs.exists.return_value = True

        # Mock fsspec.open to return object with .fs attribute
        mock_open_file = MagicMock()
        mock_open_file.fs = mock_fs

        # Mock file read with empty JSON
        mock_read_file = MagicMock()
        mock_read_file.__enter__ = MagicMock(return_value=mock_read_file)
        mock_read_file.__exit__ = MagicMock(return_value=None)
        mock_read_file.read.return_value = "{}"

        # Mock file write
        mock_write_file = MagicMock()
        mock_write_file.__enter__ = MagicMock(return_value=mock_write_file)
        mock_write_file.__exit__ = MagicMock(return_value=None)

        def open_side_effect(path, mode="r", **kwargs):
            if mode == "r":
                if kwargs:  # actual read operation
                    return mock_read_file
                return mock_open_file  # fs check
            else:
                return mock_write_file

        mock_fsspec_open.side_effect = open_side_effect

        # Call update_registry
        location: LLMCallLocation = {"file": "test.py", "lineNumber": "10"}
        update_registry("/tmp/data", location, "test-tag")

        # Should initialize the registry structure
        assert mock_fsspec_open.call_count >= 3
        written_data = json.loads(mock_write_file.write.call_args[0][0])

        assert written_data["schema"] == 1
        assert "files" in written_data

    @patch("trainloop_llm_logging.store.time")
    @patch("trainloop_llm_logging.store.fsspec.open")
    @patch("trainloop_llm_logging.store.Path")
    def test_save_samples_creates_jsonl_file(
        self, mock_path_class, mock_fsspec_open, mock_time
    ):
        """Test save_samples creates a JSONL file with timestamp."""
        # Set up mocks
        mock_time.time.return_value = 1234567890.123

        # Mock filesystem
        mock_fs = MagicMock()

        # Mock fsspec.open to return object with .fs attribute
        mock_open_file = MagicMock()
        mock_open_file.fs = mock_fs

        # Create a better Path mock that won't create real directories
        # We need to mock both Path(data_dir) / "events" and Path(event_dir_str)
        def create_path_mock(path_str):
            path_mock = MagicMock()
            path_mock.__str__ = MagicMock(return_value=path_str)
            path_mock.__truediv__ = MagicMock(side_effect=lambda x: create_path_mock(f"{path_str}/{x}"))
            path_mock.glob = MagicMock(return_value=[])  # No existing files
            return path_mock
        
        mock_path_class.side_effect = lambda x: create_path_mock(x)

        # Mock file write
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)

        def open_side_effect(path, mode="r", **kwargs):
            if mode == "w":
                return mock_open_file
            else:
                return mock_file

        mock_fsspec_open.side_effect = open_side_effect

        # Create samples
        samples: list[CollectedSample] = [
            {
                "tag": "test-1",
                "input": [{"role": "user", "content": "Hello"}],
                "output": {"content": "Hi!"},
                "model": "gpt-4",
                "modelParams": {},
                "durationMs": 100,
                "startTimeMs": 1234567890000,
                "endTimeMs": 1234567890100,
                "url": "https://api.openai.com/v1/chat/completions",
                "location": {"file": "test.py", "lineNumber": "10"},
            }
        ]

        # Call save_samples
        save_samples("/tmp/data", samples)

        # Should create directory and write file
        mock_fs.makedirs.assert_called_once_with("/tmp/data/events", exist_ok=True)

        # Check written content
        written_content = mock_file.write.call_args[0][0]
        assert json.loads(written_content.strip()) == samples[0]

    @patch("trainloop_llm_logging.store.time")
    @patch("trainloop_llm_logging.store.fsspec.open")
    @patch("trainloop_llm_logging.store.Path")
    def test_save_samples_ensures_events_dir_exists(
        self, mock_path_class, mock_fsspec_open, mock_time
    ):
        """Test save_samples creates events directory if it doesn't exist."""
        # Set up mocks
        mock_time.time.return_value = 1234567890.123

        # Mock filesystem
        mock_fs = MagicMock()

        # Mock fsspec.open to return object with .fs attribute
        mock_open_file = MagicMock()
        mock_open_file.fs = mock_fs

        # Create a better Path mock that won't create real directories
        def create_path_mock(path_str):
            path_mock = MagicMock()
            path_mock.__str__ = MagicMock(return_value=path_str)
            path_mock.__truediv__ = MagicMock(side_effect=lambda x: create_path_mock(f"{path_str}/{x}"))
            path_mock.glob = MagicMock(return_value=[])  # No existing files
            return path_mock
        
        mock_path_class.side_effect = lambda x: create_path_mock(x)

        # Mock file write
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)

        def open_side_effect(path, mode="r", **kwargs):
            if mode == "w":
                return mock_open_file
            else:
                return mock_file

        mock_fsspec_open.side_effect = open_side_effect

        # Call save_samples
        samples: list[CollectedSample] = [
            {
                "tag": "test",
                "input": [],
                "output": {"content": "test"},
                "model": "test",
                "modelParams": {},
                "durationMs": 0,
                "startTimeMs": 0,
                "endTimeMs": 0,
                "url": "",
                "location": {"file": "", "lineNumber": "0"},
            }
        ]

        save_samples("/tmp/data", samples)

        # Should ensure directory exists
        mock_fs.makedirs.assert_called_once_with("/tmp/data/events", exist_ok=True)

    @patch("trainloop_llm_logging.store.fsspec.open")
    def test_update_registry_thread_safety(self, mock_fsspec_open):
        """Test update_registry can handle concurrent updates."""
        # Track call count
        call_count = 0
        results = []

        # Set up mocks
        def make_open_file():
            mock_fs = MagicMock()
            mock_fs.exists.return_value = False
            mock_open_file = MagicMock()
            mock_open_file.fs = mock_fs
            return mock_open_file

        def make_file():
            nonlocal call_count
            call_count += 1
            mock_file = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)

            # Capture write calls
            def capture_write(data):
                results.append(data)

            mock_file.write = capture_write
            return mock_file

        def open_side_effect(path, mode="r", **kwargs):
            if mode == "r":
                return make_open_file()
            else:
                return make_file()

        mock_fsspec_open.side_effect = open_side_effect

        # Run concurrent updates
        def update_thread(i):
            location: LLMCallLocation = {"file": f"test{i}.py", "lineNumber": str(i)}
            update_registry("/tmp/data", location, f"tag-{i}")

        threads = []
        for i in range(10):
            t = threading.Thread(target=update_thread, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All threads should have written something
        assert call_count == 10
        assert len(results) == 10
