#!/usr/bin/env python3
"""
Integration tests for LiteLLM with TrainLoop LLM Logging.
"""

import os

# Test harness
from .harness import (
    IntegrationTestHarness,
    require_openai_key,
    require_anthropic_key,
    require_library,
)


class TestLiteLLMIntegration:
    """Test LiteLLM library integration."""

    @require_openai_key()
    def test_litellm_openai(self):
        """Test LiteLLM with OpenAI API."""
        with IntegrationTestHarness("litellm_openai") as harness:
            try:
                import litellm
            except ImportError:
                pytest.skip("litellm library not installed. Install with: pip install litellm")

            # Configure LiteLLM
            litellm.api_key = os.getenv("OPENAI_API_KEY")

            # Make a call using LiteLLM
            response = litellm.completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello briefly"}],
                max_tokens=10,
            )

            assert response

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]

    @require_anthropic_key()
    def test_litellm_anthropic(self):
        """Test LiteLLM with Anthropic API."""
        with IntegrationTestHarness("litellm_anthropic") as harness:
            try:
                import litellm
            except ImportError:
                pytest.skip("litellm library not installed. Install with: pip install litellm")

            # Configure LiteLLM for Anthropic
            response = litellm.completion(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Say hello briefly"}],
                max_tokens=10,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
            assert response
            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="claude-3-haiku-20240307"
            )
            assert "api.anthropic.com" in entry["url"]
