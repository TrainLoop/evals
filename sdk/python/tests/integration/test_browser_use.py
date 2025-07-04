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

import asyncio
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
from .test_real_api_calls import IntegrationTestHarness, require_openai_key, require_anthropic_key


def require_browser_use():
    """Decorator to skip tests if browser_use is not available."""
    try:
        import browser_use
        return lambda func: func  # No skip needed
    except ImportError:
        return pytest.mark.skip(reason="browser_use library not installed. Install with: pip install browser-use")


def require_playwright():
    """Decorator to skip tests if playwright is not available."""
    try:
        import playwright
        return lambda func: func  # No skip needed
    except ImportError:
        return pytest.mark.skip(reason="playwright library not installed. Install with: pip install playwright")


class TestBrowserUseIntegration:
    """Test browser_use library integration with TrainLoop LLM Logging."""
    
    @require_browser_use()
    @require_playwright()
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_browser_use_with_openai(self):
        """Test browser_use with OpenAI LLM - should capture API calls."""
        try:
            from browser_use import Controller, Agent
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")
        
        with IntegrationTestHarness("browser_use_openai") as harness:
            # Configure OpenAI LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=50
            )
            
            # Create controller and agent
            controller = Controller(headless=True)
            
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
                
                # Wait for JSONL entries (browser_use might make multiple API calls)
                entries = harness.wait_for_entries(expected_count=1, timeout=15)
                
                print(f"📊 Captured {len(entries)} LLM API calls from browser_use")
                
                # Validate that we captured at least one LLM API call
                assert len(entries) >= 1, f"Expected at least 1 API call, got {len(entries)}"
                
                # Validate the entries
                for i, entry in enumerate(entries):
                    print(f"📋 Validating entry {i+1}/{len(entries)}")
                    
                    # Check that it's a valid LLM call entry
                    assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
                    
                    # Verify it came from our browser_use session
                    assert "api.openai.com" in entry["url"]
                    assert "input" in entry
                    assert "output" in entry
                    
                    print(f"✅ Entry {i+1} validated: {len(entry['output']['content'])} chars captured")
                
                print("🎉 Browser Use + OpenAI integration test passed!")
                
            finally:
                # Clean up controller
                await controller.browser.close()
    
    @require_browser_use()
    @require_playwright()
    @require_anthropic_key()
    @pytest.mark.asyncio
    async def test_browser_use_with_anthropic(self):
        """Test browser_use with Anthropic Claude - should capture API calls."""
        try:
            from browser_use import Controller, Agent
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")
        
        with IntegrationTestHarness("browser_use_anthropic") as harness:
            # Configure Anthropic LLM
            llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.0,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=50
            )
            
            # Create controller and agent
            controller = Controller(headless=True)
            
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
                assert len(entries) >= 1, f"Expected at least 1 API call, got {len(entries)}"
                
                # Validate the entries
                for i, entry in enumerate(entries):
                    print(f"📋 Validating entry {i+1}/{len(entries)}")
                    
                    # Check that it's a valid LLM call entry
                    assert harness.validate_entry(entry, expected_model="claude-3-haiku-20240307")
                    
                    # Verify it came from our browser_use session
                    assert "api.anthropic.com" in entry["url"]
                    assert "input" in entry
                    assert "output" in entry
                    
                    print(f"✅ Entry {i+1} validated: {len(entry['output']['content'])} chars captured")
                
                print("🎉 Browser Use + Anthropic integration test passed!")
                
            finally:
                # Clean up controller
                await controller.browser.close()
    
    @require_browser_use()
    @require_playwright()
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_browser_use_multiple_calls(self):
        """Test that multiple LLM calls in a browser_use session are all captured."""
        try:
            from browser_use import Controller, Agent
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")
        
        with IntegrationTestHarness("browser_use_multiple") as harness:
            # Configure OpenAI LLM
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=30
            )
            
            # Create controller and agent with a task that might require multiple LLM calls
            controller = Controller(headless=True)
            
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
                assert len(entries) >= 1, f"Expected at least 1 API call, got {len(entries)}"
                
                # Count unique API calls (not duplicates)
                unique_calls = set()
                for entry in entries:
                    call_signature = (entry["startTimeMs"], entry["endTimeMs"], len(str(entry["input"])))
                    unique_calls.add(call_signature)
                
                print(f"🔍 Found {len(unique_calls)} unique API calls")
                
                # Validate each entry
                for i, entry in enumerate(entries):
                    assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
                    assert "api.openai.com" in entry["url"]
                
                print("🎉 Multiple calls browser_use integration test passed!")
                
            finally:
                # Clean up controller
                await controller.browser.close()


class TestBrowserUseWithManualLLMCalls:
    """Test mixing browser_use with manual LLM calls to ensure both are captured."""
    
    @require_browser_use()
    @require_playwright()
    @require_openai_key()
    @pytest.mark.asyncio
    async def test_mixed_browser_use_and_manual_calls(self):
        """Test that both browser_use calls and manual API calls are captured."""
        try:
            from browser_use import Controller, Agent
            from langchain_openai import ChatOpenAI
            import httpx
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")
        
        with IntegrationTestHarness("mixed_calls") as harness:
            # 1. Make a manual API call first
            client = httpx.Client()
            
            manual_response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    **tl.trainloop_tag("manual-call")
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10
                }
            )
            assert manual_response.status_code == 200
            
            # 2. Now use browser_use which will make its own API calls
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=20
            )
            
            controller = Controller(headless=True)
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
                assert len(entries) >= 2, f"Expected at least 2 API calls (manual + browser_use), got {len(entries)}"
                
                # Check for our manual call
                manual_calls = [e for e in entries if e.get("tag") == "manual-call"]
                assert len(manual_calls) >= 1, "Should have captured the manual API call"
                
                # Check for browser_use calls (no tag, or different tag)
                browser_use_calls = [e for e in entries if e.get("tag") != "manual-call"]
                assert len(browser_use_calls) >= 1, "Should have captured browser_use API calls"
                
                # Validate all entries
                for entry in entries:
                    assert harness.validate_entry(entry, expected_model="gpt-4o-mini")
                
                print("🎉 Mixed manual + browser_use integration test passed!")
                
            finally:
                await controller.browser.close()
                client.close()


# Test runner function for manual execution
def run_browser_use_tests():
    """Run browser_use integration tests manually."""
    print("🚀 Running Browser Use Integration Tests")
    print("=" * 60)
    
    # Check dependencies
    try:
        import browser_use
        print("✅ browser_use library available")
    except ImportError:
        print("❌ browser_use library not available (install with: pip install browser-use)")
        return
    
    try:
        import playwright
        print("✅ playwright library available")
    except ImportError:
        print("❌ playwright library not available (install with: pip install playwright)")
        return
    
    # Check API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    print(f"OpenAI API Key: {'✅' if has_openai else '❌'}")
    print(f"Anthropic API Key: {'✅' if has_anthropic else '❌'}")
    print()
    
    if not has_openai:
        print("⚠️  Skipping tests - OPENAI_API_KEY required")
        return
    
    # Run tests
    async def run_tests():
        test_instance = TestBrowserUseIntegration()
        mixed_test_instance = TestBrowserUseWithManualLLMCalls()
        
        results = []
        
        # Test 1: Browser Use with OpenAI
        try:
            print("🧪 Running browser_use + OpenAI test...")
            await test_instance.test_browser_use_with_openai()
            print("✅ browser_use + OpenAI PASSED")
            results.append(("browser_use + OpenAI", True, None))
        except Exception as e:
            print(f"❌ browser_use + OpenAI FAILED: {e}")
            results.append(("browser_use + OpenAI", False, str(e)))
        print()
        
        # Test 2: Browser Use with Anthropic (if key available)
        if has_anthropic:
            try:
                print("🧪 Running browser_use + Anthropic test...")
                await test_instance.test_browser_use_with_anthropic()
                print("✅ browser_use + Anthropic PASSED")
                results.append(("browser_use + Anthropic", True, None))
            except Exception as e:
                print(f"❌ browser_use + Anthropic FAILED: {e}")
                results.append(("browser_use + Anthropic", False, str(e)))
            print()
        
        # Test 3: Multiple calls
        try:
            print("🧪 Running browser_use multiple calls test...")
            await test_instance.test_browser_use_multiple_calls()
            print("✅ browser_use multiple calls PASSED")
            results.append(("browser_use multiple calls", True, None))
        except Exception as e:
            print(f"❌ browser_use multiple calls FAILED: {e}")
            results.append(("browser_use multiple calls", False, str(e)))
        print()
        
        # Test 4: Mixed calls
        try:
            print("🧪 Running mixed calls test...")
            await mixed_test_instance.test_mixed_browser_use_and_manual_calls()
            print("✅ mixed calls PASSED")
            results.append(("mixed calls", True, None))
        except Exception as e:
            print(f"❌ mixed calls FAILED: {e}")
            results.append(("mixed calls", False, str(e)))
        print()
        
        # Summary
        print("=" * 60)
        print("📊 Browser Use Test Results:")
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        
        for test_name, success, error in results:
            status = "PASS" if success else "FAIL"
            print(f"  {status:4} | {test_name}")
            if error:
                print(f"       | Error: {error}")
        
        print(f"\n🎯 {passed}/{total} browser_use tests passed")
        
        if passed == total:
            print("🎉 All browser_use tests passed!")
        else:
            print("⚠️  Some browser_use tests failed.")
    
    try:
        asyncio.run(run_tests())
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")


if __name__ == "__main__":
    run_browser_use_tests()