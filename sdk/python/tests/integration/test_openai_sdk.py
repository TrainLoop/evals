#!/usr/bin/env python3
"""
Integration tests for OpenAI SDK with TrainLoop LLM Logging.
"""

import asyncio
import functools
import os
import pytest

# Import TrainLoop SDK
import trainloop_llm_logging as tl

# Test harness
from .test_real_api_calls import (
    IntegrationTestHarness,
    require_openai_key,
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
                pytest.skip(f"{library_name} library not installed. Install with: pip install {library_name}")
        return wrapper

    return decorator


class TestOpenAISDKIntegration:
    """Test Official OpenAI Python SDK integration."""

    @require_library("openai")
    @require_openai_key()
    def test_openai_sdk_sync(self):
        """Test OpenAI SDK sync client."""
        with IntegrationTestHarness("openai_sdk_sync") as harness:
            try:
                import openai
            except ImportError:
                pytest.skip("openai library not available")
            # Create OpenAI client
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Make a chat completion
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                max_tokens=10,
            )

            assert response.choices[0].message.content

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]

    @require_library("openai")
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_openai_sdk_async(self):
        """Test OpenAI SDK async client."""
        with IntegrationTestHarness("openai_sdk_async") as harness:
            try:
                import openai
            except ImportError:
                pytest.skip("openai library not available")
            # Create async OpenAI client
            client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Make a chat completion
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                max_tokens=10,
            )

            assert response.choices[0].message.content

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]