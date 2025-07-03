#!/usr/bin/env python3
"""
Integration tests for Anthropic SDK with TrainLoop LLM Logging.
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
    require_anthropic_key,
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


class TestAnthropicSDKIntegration:
    """Test Official Anthropic Python SDK integration."""

    @require_library("anthropic")
    @require_anthropic_key()
    def test_anthropic_sdk_sync(self):
        """Test Anthropic SDK sync client."""
        with IntegrationTestHarness("anthropic_sdk_sync") as harness:
            try:
                import anthropic
            except ImportError:
                pytest.skip("anthropic library not available")
            # Create Anthropic client
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            # Make a message
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
            )

            assert response.content[0].text

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="claude-3-haiku-20240307"
            )
            assert "api.anthropic.com" in entry["url"]

    @require_library("anthropic")
    @require_anthropic_key()
    @pytest.mark.asyncio
    async def test_anthropic_sdk_async(self):
        """Test Anthropic SDK async client."""
        with IntegrationTestHarness("anthropic_sdk_async") as harness:
            try:
                import anthropic
            except ImportError:
                pytest.skip("anthropic library not available")
            # Create async Anthropic client
            client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            # Make a message
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
            )

            assert response.content[0].text

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="claude-3-haiku-20240307"
            )
            assert "api.anthropic.com" in entry["url"]