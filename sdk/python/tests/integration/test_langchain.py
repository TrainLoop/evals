#!/usr/bin/env python3
"""
Integration tests for LangChain with TrainLoop LLM Logging.
"""

import os
import pytest
from pydantic import SecretStr

# Test harness
from .harness import (
    IntegrationTestHarness,
    require_openai_key,
    require_anthropic_key,
    require_library,
)


class TestLangChainIntegration:
    """Test LangChain framework integration."""

    @require_library("langchain_openai")
    @require_openai_key()
    def test_langchain_openai(self):
        """Test LangChain with OpenAI."""
        with IntegrationTestHarness("langchain_openai") as harness:
            from langchain_openai import ChatOpenAI

            # Get API key
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                pytest.skip("OPENAI_API_KEY not set")
            # Create LangChain LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=SecretStr(openai_api_key),
                max_completion_tokens=10,
            )
            # Make a call
            response = llm.invoke("Say hello in 3 words")
            assert response.content
            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"
            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]

    @require_library("langchain_anthropic")
    @require_anthropic_key()
    @pytest.mark.forked  # run this test in its own subprocess to avoid global state leakage
    def test_langchain_anthropic(self):
        """Test LangChain with Anthropic."""
        with IntegrationTestHarness("langchain_anthropic") as harness:
            from langchain_anthropic import ChatAnthropic

            # Get API key
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                pytest.skip("ANTHROPIC_API_KEY not set")
            # Create LangChain LLM
            llm = ChatAnthropic(
                model_name="claude-3-haiku-20240307",
                api_key=SecretStr(anthropic_api_key),
                timeout=10,
                stop=None,
            )
            # Make a call
            response = llm.invoke("Say hello in 3 words")
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
