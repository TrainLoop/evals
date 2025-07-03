#!/usr/bin/env python3
"""
Comprehensive integration test runner for TrainLoop LLM Logging SDK.

This script runs all integration tests to verify that the instrumentation works correctly
with various Python HTTP libraries and LLM frameworks.

Test Categories:
1. Core HTTP Libraries (httpx, requests, http.client)
2. Browser Use Integration
3. Popular LLM Libraries (OpenAI SDK, Anthropic SDK, LangChain, LiteLLM, Instructor)
4. Gzip Response Handling
5. Multi-provider Support (OpenAI, Anthropic)

Usage:
    python run_all_integration_tests.py

Environment Variables:
    OPENAI_API_KEY - Required for most tests
    ANTHROPIC_API_KEY - Optional, for Anthropic-specific tests
"""

import asyncio
import os
import sys
import time
from typing import List, Tuple, Dict, Any

# Import test modules
from test_real_api_calls import run_integration_tests as run_core_tests
from test_browser_use_integration import run_browser_use_tests
from test_other_llm_libraries import run_other_llm_library_tests


def check_environment() -> Dict[str, Any]:
    """Check environment and available dependencies."""
    print("🔍 Environment Check")
    print("-" * 40)
    
    env_info = {
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "has_anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "available_libraries": {},
        "python_version": sys.version.split()[0]
    }
    
    # Check Python version
    print(f"Python Version: {env_info['python_version']}")
    
    # Check API keys
    print(f"OpenAI API Key: {'✅' if env_info['has_openai_key'] else '❌ (set OPENAI_API_KEY)'}")
    print(f"Anthropic API Key: {'✅' if env_info['has_anthropic_key'] else '❌ (optional - set ANTHROPIC_API_KEY)'}")
    
    # Check core dependencies
    core_deps = ["httpx", "requests", "trainloop_llm_logging"]
    for dep in core_deps:
        try:
            __import__(dep)
            env_info["available_libraries"][dep] = True
            print(f"{dep}: ✅")
        except ImportError:
            env_info["available_libraries"][dep] = False
            print(f"{dep}: ❌")
    
    # Check optional dependencies
    optional_deps = [
        "browser_use", "playwright", "litellm", "openai", "anthropic",
        "langchain_openai", "langchain_anthropic", "instructor"
    ]
    
    print("\nOptional Libraries:")
    for dep in optional_deps:
        try:
            __import__(dep)
            env_info["available_libraries"][dep] = True
            print(f"  {dep}: ✅")
        except ImportError:
            env_info["available_libraries"][dep] = False
            print(f"  {dep}: ❌")
    
    return env_info


def run_test_suite(name: str, test_func, env_info: Dict[str, Any]) -> Tuple[str, bool, str]:
    """Run a test suite and capture results."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        if asyncio.iscoroutinefunction(test_func):
            asyncio.run(test_func())
        else:
            test_func()
        
        duration = time.time() - start_time
        print(f"\n✅ {name} completed successfully in {duration:.2f}s")
        return (name, True, f"Completed in {duration:.2f}s")
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        print(f"\n❌ {name} failed after {duration:.2f}s: {error_msg}")
        return (name, False, error_msg)


def print_final_summary(results: List[Tuple[str, bool, str]], env_info: Dict[str, Any]):
    """Print comprehensive final summary."""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    # Test results
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n🎯 Overall Results: {passed}/{total} test suites passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\n📋 Test Suite Results:")
    for name, success, details in results:
        status = "PASS" if success else "FAIL"
        print(f"  {status:4} | {name:30} | {details}")
    
    # Environment summary
    print(f"\n🔧 Environment Summary:")
    print(f"  Python: {env_info['python_version']}")
    print(f"  OpenAI API: {'Available' if env_info['has_openai_key'] else 'Not configured'}")
    print(f"  Anthropic API: {'Available' if env_info['has_anthropic_key'] else 'Not configured'}")
    
    # Library coverage
    available_libs = sum(1 for lib, available in env_info['available_libraries'].items() if available)
    total_libs = len(env_info['available_libraries'])
    print(f"  Library Coverage: {available_libs}/{total_libs} libraries available")
    
    # Detailed library status
    core_libs = ["httpx", "requests", "trainloop_llm_logging"]
    optional_libs = [lib for lib in env_info['available_libraries'] if lib not in core_libs]
    
    print(f"\n📚 Core Libraries:")
    for lib in core_libs:
        status = "✅" if env_info['available_libraries'].get(lib, False) else "❌"
        print(f"    {lib:20} {status}")
    
    print(f"\n📦 Optional Libraries:")
    for lib in optional_libs:
        status = "✅" if env_info['available_libraries'].get(lib, False) else "❌"
        print(f"    {lib:20} {status}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if not env_info['has_openai_key']:
        print("  • Set OPENAI_API_KEY to run core functionality tests")
    
    if not env_info['has_anthropic_key']:
        print("  • Set ANTHROPIC_API_KEY to test Anthropic integration (optional)")
    
    missing_optional = [lib for lib, available in env_info['available_libraries'].items() 
                       if not available and lib not in core_libs]
    if missing_optional:
        print("  • Consider installing optional libraries for broader test coverage:")
        for lib in missing_optional[:5]:  # Show first 5
            print(f"    - pip install {lib}")
        if len(missing_optional) > 5:
            print(f"    - ... and {len(missing_optional) - 5} more")
    
    # Final verdict
    print(f"\n🏁 Final Verdict:")
    if passed == total:
        print("🎉 ALL TESTS PASSED! The TrainLoop LLM Logging instrumentation is working correctly.")
        if env_info['has_openai_key'] and env_info['has_anthropic_key']:
            print("🌟 Full test coverage with both OpenAI and Anthropic APIs.")
        else:
            print("⚠️  Limited API coverage - consider adding missing API keys for complete testing.")
    elif passed >= total * 0.8:  # 80% or more
        print("✅ Most tests passed! The instrumentation is working well.")
        print("💡 Check failed tests above for specific issues.")
    else:
        print("⚠️  Multiple test failures detected. The instrumentation may have issues.")
        print("🔧 Review the failed tests and ensure all dependencies are properly installed.")
    
    # Usage recommendations
    print(f"\n🚀 Next Steps:")
    print("  1. Review any failed tests above")
    print("  2. Install missing optional libraries if needed")
    print("  3. Configure missing API keys for broader coverage")
    print("  4. Run individual test suites for focused debugging:")
    print("     • python test_real_api_calls.py")
    print("     • python test_browser_use_integration.py")
    print("     • python test_other_llm_libraries.py")


def main():
    """Run all integration tests."""
    print("🚀 TrainLoop LLM Logging - Comprehensive Integration Test Suite")
    print("="*80)
    print("This test suite verifies that the instrumentation captures LLM API calls")
    print("across various Python libraries and frameworks.")
    print()
    
    # Check environment
    env_info = check_environment()
    
    # Check if we can run any tests
    if not env_info["available_libraries"].get("trainloop_llm_logging", False):
        print("\n❌ TrainLoop LLM Logging SDK not available. Cannot run tests.")
        return 1
    
    if not env_info["has_openai_key"]:
        print("\n⚠️  OPENAI_API_KEY not set. Most tests will be skipped.")
        print("Set OPENAI_API_KEY to run the full test suite.")
        
        # Ask user if they want to continue
        try:
            response = input("\nContinue anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("Exiting...")
                return 0
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0
    
    # Define test suites
    test_suites = [
        ("Core HTTP Libraries", run_core_tests),
        ("Browser Use Integration", run_browser_use_tests),
        ("Other LLM Libraries", run_other_llm_library_tests),
    ]
    
    # Run all test suites
    results = []
    
    print(f"\n🎬 Starting test execution...")
    start_time = time.time()
    
    for suite_name, test_func in test_suites:
        result = run_test_suite(suite_name, test_func, env_info)
        results.append(result)
    
    total_duration = time.time() - start_time
    
    # Print final summary
    print(f"\n⏱️  Total execution time: {total_duration:.2f}s")
    print_final_summary(results, env_info)
    
    # Return exit code
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    if passed == total:
        return 0  # Success
    else:
        return 1  # Some failures


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)