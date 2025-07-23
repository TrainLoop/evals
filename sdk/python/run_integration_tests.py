#!/usr/bin/env python3
"""
Standalone integration test runner for TrainLoop SDK.

This script runs integration tests outside of pytest to avoid import conflicts
with the TrainLoop SDK's instrumentation requirements.

Usage:
    python run_integration_tests.py [--test TEST_NAME] [--verbose]

Examples:
    python run_integration_tests.py                    # Run all tests
    python run_integration_tests.py --test openai      # Run only OpenAI tests
    python run_integration_tests.py --verbose          # Run with detailed output
"""

import argparse
import sys
import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import json
import time
from typing import List, Dict, Any, Optional
import importlib.util


class IntegrationTestResult:
    """Result of running an integration test."""
    
    def __init__(self, name: str, success: bool, message: str, duration_ms: int):
        self.name = name
        self.success = success
        self.message = message
        self.duration_ms = duration_ms


class StandaloneTestRunner:
    """Runs integration tests as standalone scripts to avoid pytest import conflicts."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[IntegrationTestResult] = []
    
    def log(self, message: str, force: bool = False):
        """Log a message if verbose mode is enabled."""
        if self.verbose or force:
            print(message)
    
    def run_test_script(self, test_script: str, test_name: str) -> IntegrationTestResult:
        """Run a single test script and return the result."""
        self.log(f"🧪 Running {test_name}...")
        
        start_time = time.time()
        
        try:
            # Run the test script as a separate Python process
            result = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd=Path(__file__).parent
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if result.returncode == 0:
                success_msg = f"✅ {test_name} PASSED ({duration_ms}ms)"
                self.log(success_msg, force=True)
                if self.verbose and result.stdout:
                    self.log(f"   Output: {result.stdout.strip()}")
                return IntegrationTestResult(test_name, True, success_msg, duration_ms)
            else:
                error_msg = f"❌ {test_name} FAILED ({duration_ms}ms)"
                if result.stderr:
                    error_msg += f": {result.stderr.strip()}"
                elif result.stdout:
                    error_msg += f": {result.stdout.strip()}"
                    
                self.log(error_msg, force=True)
                if self.verbose:
                    if result.stdout:
                        self.log(f"   Stdout: {result.stdout}")
                    if result.stderr:
                        self.log(f"   Stderr: {result.stderr}")
                        
                return IntegrationTestResult(test_name, False, error_msg, duration_ms)
                
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"❌ {test_name} TIMEOUT ({duration_ms}ms)"
            self.log(error_msg, force=True)
            return IntegrationTestResult(test_name, False, error_msg, duration_ms)
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f"❌ {test_name} ERROR ({duration_ms}ms): {str(e)}"
            self.log(error_msg, force=True)
            return IntegrationTestResult(test_name, False, error_msg, duration_ms)
    
    def create_openai_test(self) -> str:
        """Create OpenAI integration test script."""
        return '''
import os
import tempfile
import shutil
from pathlib import Path
import json

# Check prerequisites
if not os.getenv("OPENAI_API_KEY"):
    print("SKIP: OPENAI_API_KEY not set")
    exit(0)

# Initialize TrainLoop before any HTTP imports
import trainloop_llm_logging as tl

temp_dir = tempfile.mkdtemp(prefix="trainloop_openai_test_")
data_folder = Path(temp_dir) / "trainloop" / "data"
data_folder.mkdir(parents=True, exist_ok=True)
os.environ["TRAINLOOP_DATA_FOLDER"] = str(data_folder)

try:
    tl.collect(flush_immediately=True)
    
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test sync call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in 2 words"}],
        max_tokens=5,
    )
    
    tl.flush()
    
    # Validate results
    events_folder = data_folder / "events"
    jsonl_files = list(events_folder.glob("*.jsonl")) if events_folder.exists() else []
    
    if not jsonl_files:
        raise Exception("No JSONL files created")
    
    entries = []
    for file_path in jsonl_files:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    
    if not entries:
        raise Exception("No entries found in JSONL files")
    
    entry = entries[0]
    if entry["model"] != "gpt-4o-mini":
        raise Exception(f"Expected model gpt-4o-mini, got {entry['model']}")
    
    if "api.openai.com" not in entry["url"]:
        raise Exception(f"Expected api.openai.com in URL, got {entry['url']}")
    
    print(f"OpenAI sync test passed: {len(entries)} entries, {entry['durationMs']}ms")
    
finally:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if "TRAINLOOP_DATA_FOLDER" in os.environ:
        del os.environ["TRAINLOOP_DATA_FOLDER"]
'''

    def create_anthropic_test(self) -> str:
        """Create Anthropic integration test script."""
        return '''
import os
import tempfile
import shutil
from pathlib import Path
import json

# Check prerequisites
if not os.getenv("ANTHROPIC_API_KEY"):
    print("SKIP: ANTHROPIC_API_KEY not set")
    exit(0)

# Initialize TrainLoop before any HTTP imports
import trainloop_llm_logging as tl

temp_dir = tempfile.mkdtemp(prefix="trainloop_anthropic_test_")
data_folder = Path(temp_dir) / "trainloop" / "data"
data_folder.mkdir(parents=True, exist_ok=True)
os.environ["TRAINLOOP_DATA_FOLDER"] = str(data_folder)

try:
    tl.collect(flush_immediately=True)
    
    try:
        import anthropic
    except ImportError:
        print("SKIP: anthropic library not installed")
        exit(0)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Test sync call
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hello in 2 words"}],
    )
    
    tl.flush()
    
    # Validate results
    events_folder = data_folder / "events"
    jsonl_files = list(events_folder.glob("*.jsonl")) if events_folder.exists() else []
    
    if not jsonl_files:
        raise Exception("No JSONL files created")
    
    entries = []
    for file_path in jsonl_files:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    
    if not entries:
        raise Exception("No entries found in JSONL files")
    
    entry = entries[0]
    if entry["model"] != "claude-3-haiku-20240307":
        raise Exception(f"Expected model claude-3-haiku-20240307, got {entry['model']}")
    
    if "api.anthropic.com" not in entry["url"]:
        raise Exception(f"Expected api.anthropic.com in URL, got {entry['url']}")
    
    print(f"Anthropic sync test passed: {len(entries)} entries, {entry['durationMs']}ms")
    
finally:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if "TRAINLOOP_DATA_FOLDER" in os.environ:
        del os.environ["TRAINLOOP_DATA_FOLDER"]
'''

    def create_litellm_test(self) -> str:
        """Create LiteLLM integration test script."""
        return '''
import os
import tempfile
import shutil
from pathlib import Path
import json

# Check prerequisites
if not os.getenv("OPENAI_API_KEY"):
    print("SKIP: OPENAI_API_KEY not set")
    exit(0)

# Initialize TrainLoop before any HTTP imports
import trainloop_llm_logging as tl

temp_dir = tempfile.mkdtemp(prefix="trainloop_litellm_test_")
data_folder = Path(temp_dir) / "trainloop" / "data"
data_folder.mkdir(parents=True, exist_ok=True)
os.environ["TRAINLOOP_DATA_FOLDER"] = str(data_folder)

try:
    tl.collect(flush_immediately=True)
    
    try:
        import litellm
    except ImportError:
        print("SKIP: litellm library not installed")
        exit(0)
    
    # Test LiteLLM with OpenAI
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in 2 words"}],
        max_tokens=5,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tl.flush()
    
    # Validate results
    events_folder = data_folder / "events"
    jsonl_files = list(events_folder.glob("*.jsonl")) if events_folder.exists() else []
    
    if not jsonl_files:
        raise Exception("No JSONL files created")
    
    entries = []
    for file_path in jsonl_files:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    
    if not entries:
        raise Exception("No entries found in JSONL files")
    
    entry = entries[0]
    if entry["model"] != "gpt-4o-mini":
        raise Exception(f"Expected model gpt-4o-mini, got {entry['model']}")
    
    if "api.openai.com" not in entry["url"]:
        raise Exception(f"Expected api.openai.com in URL, got {entry['url']}")
    
    print(f"LiteLLM test passed: {len(entries)} entries, {entry['durationMs']}ms")
    
finally:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if "TRAINLOOP_DATA_FOLDER" in os.environ:
        del os.environ["TRAINLOOP_DATA_FOLDER"]
'''

    def create_httpx_test(self) -> str:
        """Create httpx integration test script."""
        return '''
import os
import tempfile
import shutil
from pathlib import Path
import json

# Check prerequisites
if not os.getenv("OPENAI_API_KEY"):
    print("SKIP: OPENAI_API_KEY not set")
    exit(0)

# Initialize TrainLoop before any HTTP imports
import trainloop_llm_logging as tl

temp_dir = tempfile.mkdtemp(prefix="trainloop_httpx_test_")
data_folder = Path(temp_dir) / "trainloop" / "data"
data_folder.mkdir(parents=True, exist_ok=True)
os.environ["TRAINLOOP_DATA_FOLDER"] = str(data_folder)

try:
    tl.collect(flush_immediately=True)
    
    try:
        import httpx
    except ImportError:
        print("SKIP: httpx library not installed")
        exit(0)
    
    # Test httpx with OpenAI API directly
    client = httpx.Client()
    response = client.post(
        "https://api.openai.com/v1/chat/completions",
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Say hello in 2 words"}],
            "max_tokens": 5
        },
        headers={
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
    )
    client.close()
    
    tl.flush()
    
    # Validate results
    events_folder = data_folder / "events"
    jsonl_files = list(events_folder.glob("*.jsonl")) if events_folder.exists() else []
    
    if not jsonl_files:
        raise Exception("No JSONL files created")
    
    entries = []
    for file_path in jsonl_files:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    
    if not entries:
        raise Exception("No entries found in JSONL files")
    
    entry = entries[0]
    if entry["model"] != "gpt-4o-mini":
        raise Exception(f"Expected model gpt-4o-mini, got {entry['model']}")
    
    if "api.openai.com" not in entry["url"]:
        raise Exception(f"Expected api.openai.com in URL, got {entry['url']}")
    
    print(f"httpx test passed: {len(entries)} entries, {entry['durationMs']}ms")
    
finally:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if "TRAINLOOP_DATA_FOLDER" in os.environ:
        del os.environ["TRAINLOOP_DATA_FOLDER"]
'''

    def run_all_tests(self, test_filter: Optional[str] = None) -> bool:
        """Run all integration tests."""
        tests = {
            "openai": self.create_openai_test(),
            "anthropic": self.create_anthropic_test(),
            "litellm": self.create_litellm_test(),
            "httpx": self.create_httpx_test(),
        }
        
        # Filter tests if specified
        if test_filter:
            filtered_tests = {k: v for k, v in tests.items() if test_filter.lower() in k.lower()}
            if not filtered_tests:
                print(f"❌ No tests found matching filter: {test_filter}")
                return False
            tests = filtered_tests
        
        print(f"🚀 Running {len(tests)} integration tests...")
        print("=" * 60)
        
        # Run all tests
        for test_name, test_script in tests.items():
            result = self.run_test_script(test_script, test_name)
            self.results.append(result)
        
        # Print summary
        print("=" * 60)
        print("📊 Test Summary:")
        
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {status} {result.name} ({result.duration_ms}ms)")
            if not result.success and not self.verbose:
                print(f"    {result.message}")
        
        total_time = sum(r.duration_ms for r in self.results)
        print(f"\\n🎯 Results: {passed}/{total} tests passed in {total_time}ms")
        
        return passed == total


def main():
    parser = argparse.ArgumentParser(
        description="Run TrainLoop SDK integration tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1] if "Usage:" in __doc__ else ""
    )
    
    parser.add_argument(
        "--test", 
        help="Run only tests matching this name (e.g., 'openai', 'anthropic')",
        default=None
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    runner = StandaloneTestRunner(verbose=args.verbose)
    success = runner.run_all_tests(test_filter=args.test)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()