#!/usr/bin/env python3
"""
Integration tests for OpenAI SDK with TrainLoop LLM Logging.
"""

import os
import pytest

# Test harness
from .harness import (
    IntegrationTestHarness,
    require_openai_key,
    require_library,
)


class TestOpenAISDKIntegration:
    """Test Official OpenAI Python SDK integration."""

    @require_openai_key()
    def test_openai_sdk_sync(self):
        """Test OpenAI SDK sync client."""
        with IntegrationTestHarness("openai_sdk_sync") as harness:
            try:
                import openai
                import httpx
            except ImportError:
                pytest.skip("openai library not installed. Install with: pip install openai")

            # Debug: Check if httpx is patched
            print(f"Debug: httpx.Client type: {type(httpx.Client)}")
            print(f"Debug: httpx.Client module: {httpx.Client.__module__}")

            # Create OpenAI client
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            print(f"Debug: OpenAI client._client type: {type(client._client)}")

            # Make a chat completion
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                max_tokens=10,
            )

            assert response.choices[0].message.content

            # Force flush before checking
            import trainloop_llm_logging as tl
            tl.flush()
            
            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            
            # Debug: list files if no entries found
            if len(entries) == 0:
                files = harness.get_jsonl_files()
                print(f"Debug: JSONL files found: {files}")
                for file in files:
                    with open(file) as f:
                        content = f.read()
                        print(f"Debug: File {file} content: {content[:500]}")
            
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]

    @require_openai_key()
    @pytest.mark.asyncio
    async def test_openai_sdk_async(self):
        """Test OpenAI SDK async client."""
        with IntegrationTestHarness("openai_sdk_async") as harness:
            try:
                import openai
            except ImportError:
                pytest.skip("openai library not installed. Install with: pip install openai")

            # Create async OpenAI client
            client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Make a chat completion
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                max_tokens=10,
            )

            assert response.choices[0].message.content

            # Force flush before checking
            import trainloop_llm_logging as tl
            tl.flush()
            
            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            
            # Debug: list files if no entries found
            if len(entries) == 0:
                files = harness.get_jsonl_files()
                print(f"Debug: JSONL files found: {files}")
                for file in files:
                    with open(file) as f:
                        content = f.read()
                        print(f"Debug: File {file} content: {content[:500]}")
            
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]
