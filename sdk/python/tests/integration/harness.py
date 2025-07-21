"""
Test harness for validating JSONL file creation and content.
"""

import functools
from pathlib import Path
import os
import tempfile
import shutil
import time
from typing import List, Dict, Any
import json
import pytest

# Import TrainLoop SDK
import trainloop_llm_logging as tl

# Load environment variables from .env file using python-dotenv
from dotenv import load_dotenv

# Load .env file at module import
load_dotenv(Path(__file__).parent.parent.parent / ".env")


class IntegrationTestHarness:
    """Test harness for validating JSONL file creation and content."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.temp_dir = None
        self.data_folder = None

    def __enter__(self):
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix=f"trainloop_test_{self.test_name}_")
        self.data_folder = Path(self.temp_dir) / "trainloop" / "data" / "events"
        self.data_folder.mkdir(parents=True, exist_ok=True)

        # Set environment variable
        os.environ["TRAINLOOP_DATA_FOLDER"] = str(
            Path(self.temp_dir) / "trainloop" / "data"
        )

        # Integration test fix: Some pytest decorators (like @require_library)
        # may import HTTP libraries before this harness runs. The TrainLoop SDK
        # requires that those libraries are not imported prior to calling collect().
        # Remove any pre-imported libraries from sys.modules before calling collect().
        import sys
        for _mod in ("requests", "httpx", "openai"):
            sys.modules.pop(_mod, None)

        # Initialize TrainLoop SDK with auto_flush for reliable testing
        tl.collect(flush_immediately=True)

        print(f"🔧 Test harness initialized: {self.temp_dir}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Before tearing down, make sure any buffered calls are written to disk
        try:
            import trainloop_llm_logging as tl

            # Force a flush so that no buffered entries leak into the next test
            tl.flush()
        except Exception:
            # Flushing is best-effort – never fail test cleanup
            pass

        # Clean up
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if "TRAINLOOP_DATA_FOLDER" in os.environ:
            del os.environ["TRAINLOOP_DATA_FOLDER"]

    def get_jsonl_files(self) -> List[Path]:
        """Get all JSONL files created during the test."""
        if self.data_folder is None:
            raise ValueError("Data folder not initialized")

        return list(self.data_folder.glob("*.jsonl"))

    def read_jsonl_entries(self) -> List[Dict[str, Any]]:
        """Read all JSONL entries from all files."""
        entries = []
        for file_path in self.get_jsonl_files():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        return entries

    def wait_for_entries(
        self, expected_count: int = 1, timeout: int = 10, tag: str | None = None
    ) -> List[Dict[str, Any]]:
        """Wait for expected number of JSONL entries to be written."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            entries = self.read_jsonl_entries()
            # Filter by tag if specified
            if tag:
                entries = [e for e in entries if e.get("tag") == tag]
            if len(entries) >= expected_count:
                return entries
            time.sleep(0.1)

        # Return whatever we have (filtered by tag if specified)
        entries = self.read_jsonl_entries()
        if tag:
            entries = [e for e in entries if e.get("tag") == tag]
        return entries

    def validate_entry(
        self,
        entry: Dict[str, Any],
        expected_model: str | None = None,
        expected_tag: str | None = None,
    ) -> bool:
        """Validate that a JSONL entry has the expected structure."""
        required_fields = [
            "durationMs",
            "input",
            "output",
            "model",
            "modelParams",
            "startTimeMs",
            "endTimeMs",
            "url",
            "location",
        ]

        for field in required_fields:
            if field not in entry:
                print(f"❌ Missing required field: {field}")
                return False

        # Validate types
        if not isinstance(entry["durationMs"], int):
            print(f"❌ durationMs should be int, got {type(entry['durationMs'])}")
            return False

        if not isinstance(entry["input"], list):
            print(f"❌ input should be list, got {type(entry['input'])}")
            return False

        if not isinstance(entry["output"], dict) or "content" not in entry["output"]:
            print(f"❌ output should be dict with 'content', got {entry['output']}")
            return False

        # Validate expected values
        if expected_model and entry["model"] != expected_model:
            print(f"❌ Expected model {expected_model}, got {entry['model']}")
            return False

        if expected_tag and entry.get("tag") != expected_tag:
            print(f"❌ Expected tag {expected_tag}, got {entry.get('tag')}")
            return False

        print(
            f"✅ Entry validation passed: {entry['model']} - {len(entry['output']['content'])} chars"
        )
        return True


def require_openai_key():
    """Decorator to skip tests if OPENAI_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY environment variable not set",
    )


def require_anthropic_key():
    """Decorator to skip tests if ANTHROPIC_API_KEY is not set."""
    return pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY environment variable not set",
    )


def require_library(library_name: str):
    """Decorator to skip tests if a library is not available."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                __import__(library_name)
                return func(*args, **kwargs)
            except ImportError:
                pytest.skip(
                    f"{library_name} library not installed. Install with: pip install {library_name}"
                )

        return wrapper

    return decorator
