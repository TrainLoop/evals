#!/usr/bin/env python3
"""
Integration tests for other popular LLM libraries with TrainLoop LLM Logging.

This test covers other popular Python libraries that make LLM API calls:
1. LiteLLM - Universal LLM API interface
2. OpenAI Python SDK - Official OpenAI client
3. Anthropic Python SDK - Official Anthropic client
4. LangChain - LLM framework
5. Instructor - Structured outputs from LLMs

All of these should work with our instrumentation since they use standard HTTP libraries under the hood.
"""

import asyncio
import functools
import json
import os
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any
import shutil

import pytest

# Import TrainLoop SDK
import trainloop_llm_logging as tl

# Test harness from the main integration tests
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


class TestLiteLLMIntegration:
    """Test LiteLLM library integration."""

    @require_library("litellm")
    @require_openai_key()
    def test_litellm_openai(self):
        """Test LiteLLM with OpenAI API."""
        try:
            import litellm
        except ImportError:
            pytest.skip("litellm library not available")

        with IntegrationTestHarness("litellm_openai") as harness:
            # Configure LiteLLM
            litellm.api_key = os.getenv("OPENAI_API_KEY")

            # Make a call using LiteLLM
            response = litellm.completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say hello briefly"}],
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

    @require_library("litellm")
    @require_anthropic_key()
    def test_litellm_anthropic(self):
        """Test LiteLLM with Anthropic API."""
        try:
            import litellm
        except ImportError:
            pytest.skip("litellm library not available")

        with IntegrationTestHarness("litellm_anthropic") as harness:
            # Configure LiteLLM for Anthropic
            response = litellm.completion(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": "Say hello briefly"}],
                max_tokens=10,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )

            assert response.choices[0].message.content

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(
                entry, expected_model="claude-3-haiku-20240307"
            )
            assert "api.anthropic.com" in entry["url"]


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


class TestInstructorIntegration:
    """Test Instructor library integration (structured outputs)."""

    @require_library("instructor")
    @require_openai_key()
    def test_instructor_openai(self):
        """Test Instructor with OpenAI for structured outputs."""
        with IntegrationTestHarness("instructor_openai") as harness:
            try:
                import instructor
                import openai
                from pydantic import BaseModel
            except ImportError:
                pytest.skip("instructor, openai, or pydantic library not available")
            # Create instructor-patched OpenAI client
            client = instructor.from_openai(
                openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            )

            # Define a simple model
            class SimpleResponse(BaseModel):
                message: str

            # Make a structured call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=SimpleResponse,
                messages=[{"role": "user", "content": "Say hello in 3 words"}],
                max_tokens=50,  # Increased for structured output parsing
            )

            assert response.message

            # Wait for JSONL entries
            entries = harness.wait_for_entries(expected_count=1)
            assert len(entries) >= 1, f"Expected at least 1 entry, got {len(entries)}"

            # Validate entry
            entry = entries[0]
            assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
            assert "api.openai.com" in entry["url"]


# Test runner function for manual execution
def run_other_llm_library_tests():
    """Run integration tests for other LLM libraries manually."""
    print("🚀 Running Other LLM Libraries Integration Tests")
    print("=" * 60)

    # Check which libraries are available
    libraries = {
        "litellm": "LiteLLM",
        "openai": "OpenAI SDK",
        "anthropic": "Anthropic SDK",
        "langchain_openai": "LangChain OpenAI",
        "langchain_anthropic": "LangChain Anthropic",
        "instructor": "Instructor",
    }

    available_libraries = []
    for lib, name in libraries.items():
        try:
            __import__(lib)
            available_libraries.append((lib, name))
            print(f"✅ {name} available")
        except ImportError:
            print(f"❌ {name} not available")

    print()

    # Check API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    print(f"OpenAI API Key: {'✅' if has_openai else '❌'}")
    print(f"Anthropic API Key: {'✅' if has_anthropic else '❌'}")
    print()

    if not available_libraries:
        print("⚠️  No LLM libraries available for testing")
        return

    if not has_openai:
        print("⚠️  No API keys available for testing")
        return

    # Run tests
    async def run_tests():
        results = []

        # Test each available library
        test_classes = [
            TestLiteLLMIntegration(),
            TestOpenAISDKIntegration(),
            TestAnthropicSDKIntegration(),
            TestLangChainIntegration(),
            TestInstructorIntegration(),
        ]

        test_methods = [
            ("LiteLLM OpenAI", lambda: test_classes[0].test_litellm_openai()),
            ("OpenAI SDK Sync", lambda: test_classes[1].test_openai_sdk_sync()),
            ("OpenAI SDK Async", lambda: test_classes[1].test_openai_sdk_async()),
            ("LangChain OpenAI", lambda: test_classes[3].test_langchain_openai()),
            ("Instructor OpenAI", lambda: test_classes[4].test_instructor_openai()),
        ]

        if has_anthropic:
            test_methods.extend(
                [
                    (
                        "LiteLLM Anthropic",
                        lambda: test_classes[0].test_litellm_anthropic(),
                    ),
                    (
                        "Anthropic SDK Sync",
                        lambda: test_classes[2].test_anthropic_sdk_sync(),
                    ),
                    (
                        "Anthropic SDK Async",
                        lambda: test_classes[2].test_anthropic_sdk_async(),
                    ),
                    (
                        "LangChain Anthropic",
                        lambda: test_classes[3].test_langchain_anthropic(),
                    ),
                ]
            )

        for test_name, test_func in test_methods:
            try:
                print(f"🧪 Running {test_name}...")
                if "Async" in test_name:
                    await test_func()
                else:
                    test_func()
                print(f"✅ {test_name} PASSED")
                results.append((test_name, True, None))
            except Exception as e:
                if "not available" in str(e) or "skip" in str(e).lower():
                    print(f"⏭️ {test_name} SKIPPED: {e}")
                    continue
                print(f"❌ {test_name} FAILED: {e}")
                results.append((test_name, False, str(e)))
            print()

        # Summary
        print("=" * 60)
        print("📊 Other LLM Libraries Test Results:")
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)

        for test_name, success, error in results:
            status = "PASS" if success else "FAIL"
            print(f"  {status:4} | {test_name}")
            if error:
                print(f"       | Error: {error}")

        print(f"\n🎯 {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All other LLM library tests passed!")
        else:
            print("⚠️  Some tests failed.")

    try:
        asyncio.run(run_tests())
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")


if __name__ == "__main__":
    run_other_llm_library_tests()
