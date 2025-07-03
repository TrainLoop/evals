#!/usr/bin/env python3
"""
Integration tests for LangChain with TrainLoop LLM Logging.
"""

import functools
import os
import pytest

# Import TrainLoop SDK
import trainloop_llm_logging as tl

# Test harness
from .test_real_api_calls import (
    IntegrationTestHarness,
    require_openai_key,
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


class TestLangChainIntegration:
    """Test LangChain framework integration."""

    @require_library("langchain_openai")
    @require_openai_key()
    def test_langchain_openai(self):
        """Test LangChain with OpenAI."""
        with IntegrationTestHarness("langchain_openai") as harness:
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                pytest.skip("langchain_openai library not available")
            # Create LangChain LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=10,
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
    def test_langchain_anthropic(self):
        """Test LangChain with Anthropic."""
        with IntegrationTestHarness("langchain_anthropic") as harness:
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError:
                pytest.skip("langchain_anthropic library not available")
            # Create LangChain LLM
            llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=10,
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