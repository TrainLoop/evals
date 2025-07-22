#!/usr/bin/env python3
"""
Integration tests for Anthropic SDK with TrainLoop LLM Logging.
"""

import os
import pytest

# Test harness
from .harness import (
    IntegrationTestHarness,
    require_anthropic_key,
    require_library,
)


class TestAnthropicSDKIntegration:
    """Test Official Anthropic Python SDK integration."""

    @require_anthropic_key()
    def test_anthropic_sdk_sync(self):
        """Test Anthropic SDK sync client."""
        with IntegrationTestHarness("anthropic_sdk_sync") as harness:
            try:
                import anthropic
            except ImportError:
                pytest.skip("anthropic library not installed. Install with: pip install anthropic")

            # Create Anthropic client
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            # Make a message
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
            )
            assert response.content
            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="claude-3-haiku-20240307"
            )
            assert "api.anthropic.com" in entry["url"]

    @require_anthropic_key()
    @pytest.mark.asyncio
    async def test_anthropic_sdk_async(self):
        """Test Anthropic SDK async client."""
        with IntegrationTestHarness("anthropic_sdk_async") as harness:
            try:
                import anthropic
            except ImportError:
                pytest.skip("anthropic library not installed. Install with: pip install anthropic")

            # Create async Anthropic client
            client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            # Make a message
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
            )
            assert response.content
            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="claude-3-haiku-20240307"
            )
            assert "api.anthropic.com" in entry["url"]
