#!/usr/bin/env python3
"""
Integration tests that make actual API calls to verify instrumentation works correctly.

These tests validate that:
1. Each supported HTTP library properly captures LLM API calls
2. JSONL files are created with correct structure
3. Both sync and async variants work
4. Gzipped responses are handled correctly
5. Different LLM providers work (OpenAI, Anthropic)

Environment Variables:
- OPENAI_API_KEY: Required for OpenAI tests
- ANTHROPIC_API_KEY: Required for Anthropic tests (optional)
- TRAINLOOP_DATA_FOLDER: Set automatically by test harness
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil

import pytest

# HTTP libraries will be imported inside test functions after tl.collect()
from urllib.parse import urlparse

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

        # Initialize TrainLoop SDK with auto_flush for reliable testing
        tl.collect(auto_flush=True)

        print(f"🔧 Test harness initialized: {self.temp_dir}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if "TRAINLOOP_DATA_FOLDER" in os.environ:
            del os.environ["TRAINLOOP_DATA_FOLDER"]

    def get_jsonl_files(self) -> List[Path]:
        """Get all JSONL files created during the test."""
        return list(self.data_folder.glob("*.jsonl"))

    def read_jsonl_entries(self) -> List[Dict[str, Any]]:
        """Read all JSONL entries from all files."""
        entries = []
        for file_path in self.get_jsonl_files():
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        return entries

    def wait_for_entries(
        self, expected_count: int = 1, timeout: int = 10
    ) -> List[Dict[str, Any]]:
        """Wait for expected number of JSONL entries to be written."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            entries = self.read_jsonl_entries()
            if len(entries) >= expected_count:
                return entries
            time.sleep(0.1)

        # Return whatever we have
        return self.read_jsonl_entries()

    def validate_entry(
        self,
        entry: Dict[str, Any],
        expected_model: str = None,
        expected_tag: str = None,
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


class TestHttpxIntegration:
    """Test httpx library integration (sync and async)."""

    @require_openai_key()
    def test_httpx_sync_openai(self):
        """Test sync httpx with OpenAI API."""
        with IntegrationTestHarness("httpx_sync") as harness:
            import httpx  # Import after tl.collect() is called
            client = httpx.Client()

            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    **tl.trainloop_tag("test-httpx-sync"),
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                    "max_tokens": 10,
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert "choices" in result

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-httpx-sync"
            )

    @require_openai_key()
    @pytest.mark.asyncio
    async def test_httpx_async_openai(self):
        """Test async httpx with OpenAI API."""
        with IntegrationTestHarness("httpx_async") as harness:
            import httpx  # Import after tl.collect() is called
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                        **tl.trainloop_tag("test-httpx-async"),
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "user", "content": "Say hello in exactly 3 words"}
                        ],
                        "max_tokens": 10,
                    },
                )

            assert response.status_code == 200
            result = response.json()
            assert "choices" in result

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-httpx-async"
            )


class TestRequestsIntegration:
    """Test requests library integration."""

    @require_openai_key()
    def test_requests_openai(self):
        """Test requests library with OpenAI API."""
        with IntegrationTestHarness("requests") as harness:
            import requests  # Import after tl.collect() is called
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json",
                    **tl.trainloop_tag("test-requests"),
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                    "max_tokens": 10,
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert "choices" in result

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-requests"
            )


class TestHttpClientIntegration:
    """Test http.client library integration."""

    @require_openai_key()
    def test_http_client_openai(self):
        """Test http.client with OpenAI API."""
        with IntegrationTestHarness("http_client") as harness:
            import http.client  # Import after tl.collect() is called
            # Prepare request data
            payload = json.dumps(
                {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                    "max_tokens": 10,
                }
            )

            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
                **tl.trainloop_tag("test-http-client"),
            }

            # Make request with http.client
            conn = http.client.HTTPSConnection("api.openai.com")
            conn.request("POST", "/v1/chat/completions", payload, headers)
            response = conn.getresponse()

            assert response.status == 200
            data = response.read().decode()
            result = json.loads(data)
            assert "choices" in result

            conn.close()

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-http-client"
            )


class TestAnthropicIntegration:
    """Test with Anthropic API to ensure multi-provider support."""

    @require_anthropic_key()
    def test_httpx_anthropic(self):
        """Test httpx with Anthropic API."""
        with IntegrationTestHarness("anthropic") as harness:
            import httpx  # Import after tl.collect() is called
            client = httpx.Client()

            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                    **tl.trainloop_tag("test-anthropic"),
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 10,
                    "messages": [
                        {"role": "user", "content": "Say hello in exactly 3 words"}
                    ],
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert "content" in result

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry,
                expected_model="claude-3-haiku-20240307",
                expected_tag="test-anthropic",
            )


class TestGzipResponseHandling:
    """Test that gzipped responses are handled correctly."""

    @require_openai_key()
    def test_gzipped_response_with_httpx(self):
        """Test that gzipped responses from OpenAI are properly handled."""
        with IntegrationTestHarness("gzip") as harness:
            import httpx  # Import after tl.collect() is called
            client = httpx.Client()

            # Make request that will likely return gzipped response
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Accept-Encoding": "gzip",  # Explicitly request gzip
                    **tl.trainloop_tag("test-gzip"),
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Write a short poem about computers (2-3 lines)",
                        }
                    ],
                    "max_tokens": 50,
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert "choices" in result

            # Verify response was actually gzipped by checking headers
            print(
                f"Response encoding: {response.headers.get('content-encoding', 'none')}"
            )

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry - this test specifically validates the gzip fix
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="gpt-4o-mini", expected_tag="test-gzip"
            )

            # Verify the content was properly captured (not empty or malformed)
            assert (
                len(entry["output"]["content"]) > 10
            ), "Content should be substantial for a poem"
            print(f"✅ Captured content: {entry['output']['content'][:100]}...")


# Test runner function for manual execution
def run_integration_tests():
    """Run integration tests manually (without pytest)."""
    print("🚀 Running TrainLoop LLM Logging Integration Tests")
    print("=" * 60)

    # Check API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    print(
        f"OpenAI API Key: {'✅' if has_openai else '❌ (set OPENAI_API_KEY to run OpenAI tests)'}"
    )
    print(
        f"Anthropic API Key: {'✅' if has_anthropic else '❌ (optional - set ANTHROPIC_API_KEY for Anthropic tests)'}"
    )
    print()

    if not has_openai:
        print(
            "⚠️  Skipping tests - OPENAI_API_KEY required for basic functionality tests"
        )
        return

    # Run individual tests
    test_cases = [
        ("httpx sync", TestHttpxIntegration().test_httpx_sync_openai),
        ("requests", TestRequestsIntegration().test_requests_openai),
        ("http.client", TestHttpClientIntegration().test_http_client_openai),
        ("gzip handling", TestGzipResponseHandling().test_gzipped_response_with_httpx),
    ]

    if has_anthropic:
        test_cases.append(
            ("anthropic", TestAnthropicIntegration().test_httpx_anthropic)
        )

    # Run async test separately
    async def run_async_test():
        await TestHttpxIntegration().test_httpx_async_openai()

    results = []
    for test_name, test_func in test_cases:
        try:
            print(f"🧪 Running {test_name}...")
            test_func()
            print(f"✅ {test_name} PASSED")
            results.append((test_name, True, None))
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            results.append((test_name, False, str(e)))
        print()

    # Run async test
    try:
        print("🧪 Running httpx async...")
        asyncio.run(run_async_test())
        print("✅ httpx async PASSED")
        results.append(("httpx async", True, None))
    except Exception as e:
        print(f"❌ httpx async FAILED: {e}")
        results.append(("httpx async", False, str(e)))

    # Summary
    print("=" * 60)
    print("📊 Test Results Summary:")
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for test_name, success, error in results:
        status = "PASS" if success else "FAIL"
        print(f"  {status:4} | {test_name}")
        if error:
            print(f"       | Error: {error}")

    print(f"\n🎯 {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The instrumentation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    run_integration_tests()
