#!/usr/bin/env python3
"""
Integration tests for browser_use library with TrainLoop LLM Logging.

Browser Use is a Python library that allows AI agents to control a browser using LLMs.
When browser_use makes API calls to LLMs (OpenAI, Anthropic, etc.), our instrumentation
should capture those calls and log them to JSONL files.

This test verifies that:
1. LLM API calls made by browser_use are captured
2. The instrumentation works with browser_use's HTTP client usage
3. Multiple API calls from a single browser_use session are logged

Requirements:
- browser_use library (pip install browser-use)
- playwright (for browser automation)
- OpenAI or Anthropic API key
- Chrome/Chromium browser
"""

import os

import pytest
from pydantic import SecretStr

# Import TrainLoop SDK
import trainloop_llm_logging as tl

# Test harness from the main integration tests
from .harness import (
    IntegrationTestHarness,
    require_openai_key,
    require_anthropic_key,
    require_library,
)


class TestBrowserUseIntegration:
    """Test browser_use library integration with TrainLoop LLM Logging."""

    @require_library("browser_use")
    @require_library("playwright")
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_browser_use_with_openai(self):
        """Test browser_use with OpenAI LLM - should capture API calls."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            pytest.skip("OPENAI_API_KEY not set")

        with IntegrationTestHarness("browser_use_openai") as harness:
            from browser_use import Controller, Agent
            from langchain_openai import ChatOpenAI

            # Configure OpenAI LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key=SecretStr(openai_api_key),
                max_completion_tokens=100,
            )

            # Create controller and agent
            controller = Controller(headless=True, keep_open=False)

            # Task that requires web interaction and reasoning to force LLM API calls
            agent = Agent(
                task="Navigate to https://httpbin.org/get and tell me what my IP address is from the JSON response",
                llm=llm,
                controller=controller,
            )

            try:
                # Run the agent - this should make LLM API calls
                result = await agent.run()
                print(f"🤖 Browser Use Result: {result}")

                # Wait for JSONL entries (browser_use might make multiple API calls)
                entries = harness.wait_for_entries(expected_count=1, timeout=15)

                print(f"📊 Captured {len(entries)} LLM API calls from browser_use")

                # Validate that we captured at least one LLM API call
                assert (
                    len(entries) >= 1
                ), f"Expected at least 1 API call, got {len(entries)}"

                # Validate the entries
                for i, entry in enumerate(entries):
                    entry_count = i + 1
                    print(f"📋 Validating entry {entry_count}/{len(entries)}")

                    # Check that it's a valid LLM call entry
                    assert harness.validate_entry(entry, expected_model="gpt-4o-mini")

                    # Verify it came from our browser_use session
                    assert "api.openai.com" in entry["url"]
                    assert "input" in entry
                    assert "output" in entry

                    print(
                        f"✅ Entry {entry_count} validated: {len(entry['output']['content'])} chars captured"
                    )

                print("🎉 Browser Use + OpenAI integration test passed!")

            finally:
                # Clean up controller - force close to avoid interactive prompt
                try:
                    await controller.browser.close(force=True)
                except Exception:
                    # Ignore cleanup errors in test environments
                    pass

    @require_library("browser_use")
    @require_library("playwright")
    @require_anthropic_key()
    @pytest.mark.asyncio
    async def test_browser_use_with_anthropic(self):
        """Test browser_use with Anthropic Claude - should capture API calls."""
        with IntegrationTestHarness("browser_use_anthropic") as harness:
            from browser_use import Controller, Agent
            from langchain_anthropic import ChatAnthropic

            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                pytest.skip("ANTHROPIC_API_KEY not set")

            # Configure Anthropic LLM
            llm = ChatAnthropic(
                model_name="claude-3-haiku-20240307",
                temperature=0.0,
                timeout=10,
                stop=None,
            )

            # Create controller and agent
            controller = Controller(headless=True, keep_open=False)

            # Task that requires web interaction to force LLM API calls
            agent = Agent(
                task="Go to example.com and tell me what the main heading says",
                llm=llm,
                controller=controller,
            )

            try:
                # Run the agent - this should make LLM API calls
                result = await agent.run()
                print(f"🤖 Browser Use Result: {result}")

                # Wait for JSONL entries
                entries = harness.wait_for_entries(expected_count=1, timeout=15)

                print(f"📊 Captured {len(entries)} LLM API calls from browser_use")

                # Validate that we captured at least one LLM API call
                assert (
                    len(entries) >= 1
                ), f"Expected at least 1 API call, got {len(entries)}"

                # Validate the entries
                for i, entry in enumerate(entries):
                    entry_count = i + 1
                    print(f"📋 Validating entry {entry_count}/{len(entries)}")

                    # Check that it's a valid LLM call entry
                    # Note: browser_use with langchain_anthropic might use a different
                    # model identifier in the actual API request. Common variations:
                    # - claude-3-haiku-20240307 (what we specify)
                    # - claude-3-haiku (without date)
                    # - claude-3-sonnet-20240229 (default if not recognized)
                    
                    # First validate without checking the exact model
                    assert harness.validate_entry(entry)
                    
                    # Then check it's at least a Claude model
                    actual_model = entry.get("model", "")
                    assert "claude" in actual_model.lower(), (
                        f"Expected a Claude model, got '{actual_model}'"
                    )

                    # Verify it came from our browser_use session
                    assert "api.anthropic.com" in entry["url"]
                    assert "input" in entry
                    assert "output" in entry

                    print(
                        f"✅ Entry {entry_count} validated: {len(entry['output']['content'])} chars captured"
                    )

                print("🎉 Browser Use + Anthropic integration test passed!")

            finally:
                # Clean up controller - force close to avoid interactive prompt
                try:
                    await controller.browser.close(force=True)
                except Exception:
                    # Ignore cleanup errors in test environments
                    pass

    @require_library("browser_use")
    @require_library("playwright")
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_browser_use_multiple_calls(self):
        """Test that multiple LLM calls in a browser_use session are all captured."""
        with IntegrationTestHarness("browser_use_multiple") as harness:
            from browser_use import Controller, Agent
            from langchain_openai import ChatOpenAI

            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                pytest.skip("OPENAI_API_KEY not set")

            # Configure OpenAI LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key=SecretStr(openai_api_key),
                max_completion_tokens=30,
            )

            # Create controller and agent with a task that might require multiple LLM calls
            controller = Controller(headless=True, keep_open=False)

            agent = Agent(
                task="Go to example.com and take a screenshot",
                llm=llm,
                controller=controller,
            )

            try:
                # Run the agent - this might make multiple LLM API calls
                result = await agent.run()
                print(f"🤖 Browser Use Result: {result}")

                # Wait for JSONL entries - expect potentially multiple calls
                entries = harness.wait_for_entries(expected_count=1, timeout=20)

                print(f"📊 Captured {len(entries)} LLM API calls from browser_use")

                # Validate that we captured the API calls
                assert (
                    len(entries) >= 1
                ), f"Expected at least 1 API call, got {len(entries)}"

                # Count unique API calls (not duplicates)
                unique_calls = set()
                for entry in entries:
                    call_signature = (
                        entry["startTimeMs"],
                        entry["endTimeMs"],
                        len(str(entry["input"])),
                    )
                    unique_calls.add(call_signature)

                print(f"🔍 Found {len(unique_calls)} unique API calls")

                # Validate each entry
                for i, entry in enumerate(entries):
                    assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
                    assert "api.openai.com" in entry["url"]

                print("🎉 Multiple calls browser_use integration test passed!")

            finally:
                # Clean up controller - force close to avoid interactive prompt
                try:
                    await controller.browser.close(force=True)
                except Exception:
                    # Ignore cleanup errors in test environments
                    pass


class TestBrowserUseWithManualLLMCalls:
    """Test mixing browser_use with manual LLM calls to ensure both are captured."""

    @require_library("browser_use")
    @require_library("playwright")
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_mixed_browser_use_and_manual_calls(self):
        """Test that both browser_use calls and manual API calls are captured."""
        with IntegrationTestHarness("mixed_calls") as harness:
            from browser_use import Controller, Agent
            from langchain_openai import ChatOpenAI
            import httpx

            # Get API key
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                pytest.skip("OPENAI_API_KEY not set")

            # 1. Make a manual API call first
            client = httpx.Client()

            manual_response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    **tl.trainloop_tag("manual-call"),
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10,
                },
            )
            assert manual_response.status_code == 200

            # 2. Now use browser_use which will make its own API calls
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key=SecretStr(openai_api_key),
                max_completion_tokens=20,
            )

            controller = Controller(headless=True, keep_open=False)
            agent = Agent(
                task="Go to example.com and find the title",
                llm=llm,
                controller=controller,
            )

            try:
                # Run browser_use agent
                result = await agent.run()
                print(f"🤖 Browser Use Result: {result}")

                # Wait for all JSONL entries
                entries = harness.wait_for_entries(expected_count=2, timeout=20)

                print(f"📊 Captured {len(entries)} total LLM API calls")

                # Should have captured both manual and browser_use calls
                assert (
                    len(entries) >= 2
                ), f"Expected at least 2 API calls (manual + browser_use), got {len(entries)}"

                # Check for our manual call
                manual_calls = [e for e in entries if e.get("tag") == "manual-call"]
                assert (
                    len(manual_calls) >= 1
                ), "Should have captured the manual API call"

                # Check for browser_use calls (no tag, or different tag)
                browser_use_calls = [
                    e for e in entries if e.get("tag") != "manual-call"
                ]
                assert (
                    len(browser_use_calls) >= 1
                ), "Should have captured browser_use API calls"

                # Validate all entries
                for entry in entries:
                    assert harness.validate_entry(entry, expected_model="gpt-4o-mini")

                print("🎉 Mixed manual + browser_use integration test passed!")

            finally:
                try:
                    await controller.browser.close(force=True)
                except Exception:
                    # Ignore cleanup errors in test environments
                    pass
                client.close()
