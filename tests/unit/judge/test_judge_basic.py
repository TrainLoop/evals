"""
Unit tests for the TrainLoop judge functionality.
"""

import sys
import os
from unittest.mock import patch
from pathlib import Path
import yaml
import pytest
from ...helpers.mock_llm import (
    mock_judge_calls,
    POSITIVE_RESPONSES,
    NEGATIVE_RESPONSES,
)

# Import from the scaffold (this simulates how users will import)
scaffold_path = (
    Path(__file__).parent.parent.parent.parent
    / "cli"
    / "trainloop_cli"
    / "scaffold"
    / "trainloop"
)
# print the scaffold path
print(scaffold_path)
# print the current path to this file
print(Path(__file__).parent)
sys.path.insert(0, str(scaffold_path))

from eval.judge import assert_true, make_prompt, _load_cfg


@pytest.mark.unit
@pytest.mark.judge
class TestJudgeBasic:
    """Basic judge functionality tests."""

    def test_make_prompt_basic(self):
        """Test basic prompt generation."""
        claim = "This is a test claim."
        prompt = make_prompt(claim)

        assert claim in prompt
        assert "<claim>" in prompt
        assert "</claim>" in prompt
        assert "reasoning" in prompt.lower()
        assert "result" in prompt.lower()

    def test_make_prompt_custom_template(self):
        """Test prompt generation with custom template."""
        claim = "Test claim"
        template = "Evaluate: {claim}\nAnswer: true/false"

        prompt = make_prompt(claim, template)

        assert prompt == "Evaluate: Test claim\nAnswer: true/false"

    def test_make_prompt_detailed_inspection(self):
        """Test detailed prompt inspection like in scaffold."""
        claim = "The code follows Python best practices."
        prompt = make_prompt(claim)
        
        # Verify the prompt contains expected elements
        assert claim in prompt
        assert "true" in prompt.lower()
        assert "false" in prompt.lower()
        
        # This mirrors the scaffold's prompt inspection functionality
        print("\n" + "="*50)
        print("Generated prompt:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)

    @patch("eval.judge._find_config_file")
    def test_load_cfg_defaults(self, mock_find_config):
        """Test config loading with defaults when no config file exists."""
        mock_find_config.return_value = None

        cfg = _load_cfg(None)

        assert cfg["models"] == ["openai/gpt-4o"]
        assert cfg["calls_per_model_per_claim"] == 3
        assert cfg["temperature"] == 0.7

    @patch("eval.judge._find_config_file")
    def test_load_cfg_override(self, mock_find_config):
        """Test config loading with override parameters."""
        mock_find_config.return_value = None

        override = {
            "models": ["anthropic/claude-3-sonnet"],
            "temperature": 0.5,
        }

        cfg = _load_cfg(override)

        assert cfg["models"] == ["anthropic/claude-3-sonnet"]
        assert cfg["temperature"] == 0.5
        assert cfg["calls_per_model_per_claim"] == 3  # Default preserved

    def test_load_cfg_from_yaml(self, temp_dir):
        """Test config loading from YAML file."""
        config_data = {
            "trainloop": {
                "judge": {
                    "models": ["openai/gpt-4o-mini"],
                    "calls_per_model_per_claim": 5,
                    "temperature": 0.3,
                }
            }
        }

        config_file = temp_dir / "trainloop.config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Temporarily change working directory
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            cfg = _load_cfg(None)
        finally:
            os.chdir(old_cwd)

        assert cfg["models"] == ["openai/gpt-4o-mini"]
        assert cfg["calls_per_model_per_claim"] == 5
        assert cfg["temperature"] == 0.3


@pytest.mark.unit
@pytest.mark.judge
class TestJudgeWithMocks:
    """Judge tests using mocked LLM responses."""

    def test_assert_true_positive_case(self):
        """Test assert_true with positive verdict."""
        with mock_judge_calls(POSITIVE_RESPONSES):
            verdict = assert_true(
                "This response is helpful.", "This response is not helpful."
            )

        assert verdict == 1

    def test_assert_true_negative_case(self):
        """Test assert_true with negative verdict."""
        with mock_judge_calls(NEGATIVE_RESPONSES):
            verdict = assert_true(
                "This response is helpful.", "This response is not helpful."
            )

        assert verdict == 0

    def test_assert_true_with_custom_config(self):
        """Test assert_true with custom configuration."""
        custom_cfg = {
            "models": ["openai/gpt-4o-mini"],
            "calls_per_model_per_claim": 1,
            "temperature": 0.3,
        }

        with mock_judge_calls(POSITIVE_RESPONSES):
            verdict = assert_true(
                "This is accurate.", "This is not accurate.", cfg=custom_cfg
            )

        assert verdict == 1

    def test_xor_sanity_check(self):
        """Test that contradictory responses are filtered out."""
        # Both claims get "true" responses (should be filtered by XOR)
        contradictory_responses = {
            "helpful": ["true", "true", "true"],
            "not helpful": ["true", "true", "true"],
        }

        with mock_judge_calls(contradictory_responses):
            # Should return 0 since all samples are filtered out
            verdict = assert_true("This is helpful.", "This is not helpful.")

        assert verdict == 0

    def test_scaffold_examples_mocked(self):
        """Test the scaffold examples with mocked responses."""
        print("\n=== Testing Scaffold Examples (Mocked) ===")
        
        # Test 1: Simple factual claim (mocked)
        print("\nTest 1: Factual claim (mocked)")
        with mock_judge_calls(POSITIVE_RESPONSES):
            verdict = assert_true(
                "The number 2 + 2 equals 4.", 
                "The number 2 + 2 does not equal 4."
            )
        print(f"Verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
        assert verdict == 1

        # Test 2: Subjective evaluation (mocked)
        print("\nTest 2: Response quality evaluation (mocked)")
        user_question = "What is Python?"
        good_response = "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms and has a vast ecosystem of libraries."

        yes_claim = f"""
        The following response provides a clear and accurate answer to the question.
        Question: {user_question}
        Response: {good_response}
        """

        no_claim = f"""
        The following response does NOT provide a clear and accurate answer to the question.
        Question: {user_question}
        Response: {good_response}
        """

        with mock_judge_calls(POSITIVE_RESPONSES):
            verdict = assert_true(yes_claim, no_claim)
        print(f"Verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
        assert verdict == 1


@pytest.mark.integration
@pytest.mark.judge
@pytest.mark.slow
class TestJudgeIntegration:
    """Integration tests that require real API calls."""

    def _check_api_requirements(self):
        """Check if API requirements are met."""
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip(
                "API integration tests require API keys. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable."
            )

    def test_basic_factual_claim_real_api(self):
        """Test basic factual claim with real API."""
        self._check_api_requirements()
        
        print("\n=== Testing Basic Judge (Real API) ===")
        print("\nTest: Simple factual claim")
        
        try:
            verdict = assert_true(
                "The number 2 + 2 equals 4.", 
                "The number 2 + 2 does not equal 4."
            )
            print(f"Verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
            
            # This should almost certainly pass with real models
            assert verdict in [0, 1]  # Just verify it returns a valid verdict
            
        except Exception as e:
            pytest.fail(f"Real API test failed: {e}")

    def test_response_quality_evaluation_real_api(self):
        """Test response quality evaluation with real API."""
        self._check_api_requirements()
        
        print("\n=== Testing Response Quality (Real API) ===")
        
        user_question = "What is Python?"
        good_response = "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms and has a vast ecosystem of libraries."

        yes_claim = f"""
        The following response provides a clear and accurate answer to the question.
        Question: {user_question}
        Response: {good_response}
        """

        no_claim = f"""
        The following response does NOT provide a clear and accurate answer to the question.
        Question: {user_question}
        Response: {good_response}
        """

        try:
            verdict = assert_true(yes_claim, no_claim)
            print(f"Verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
            
            # Just verify it returns a valid verdict
            assert verdict in [0, 1]
            
        except Exception as e:
            pytest.fail(f"Real API test failed: {e}")

    def test_custom_config_real_api(self):
        """Test judge with custom configuration and real API."""
        self._check_api_requirements()
        
        print("\n=== Testing Custom Configuration (Real API) ===")

        custom_cfg = {
            "calls_per_model_per_claim": 1,  # Faster for testing
            "temperature": 0.3,  # More deterministic
        }

        try:
            verdict = assert_true(
                "The sky is typically blue during a clear day.",
                "The sky is not typically blue during a clear day.",
                cfg=custom_cfg,
            )

            print(f"Verdict with custom config: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
            assert verdict in [0, 1]
            
        except Exception as e:
            pytest.fail(f"Real API test with custom config failed: {e}")

    def test_error_handling_and_setup_guidance(self):
        """Test error handling and provide setup guidance."""
        print("\n=== Testing Error Handling and Setup ===")
        
        # Test what happens when no API keys are set
        original_openai_key = os.environ.get("OPENAI_API_KEY")
        original_anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        
        try:
            # Temporarily remove API keys
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            if "ANTHROPIC_API_KEY" in os.environ:
                del os.environ["ANTHROPIC_API_KEY"]
            
            print("\nTesting without API keys...")
            print("Note: Make sure you have configured your LLM API keys")
            print("(e.g., OPENAI_API_KEY environment variable)")
            
            # This should either skip or provide helpful error message
            with pytest.raises((Exception, SystemExit)):
                assert_true("Test claim", "Test counter-claim")
                
        except Exception as e:
            print(f"Expected error when no API keys configured: {e}")
            print("\nSetup instructions:")
            print("1. Install litellm: pip install litellm")
            print("2. Set up your API keys (e.g., export OPENAI_API_KEY=your-key)")
            
        finally:
            # Restore original API keys
            if original_openai_key:
                os.environ["OPENAI_API_KEY"] = original_openai_key
            if original_anthropic_key:
                os.environ["ANTHROPIC_API_KEY"] = original_anthropic_key


@pytest.mark.integration
@pytest.mark.judge
class TestJudgeDemo:
    """Demonstration tests that show judge functionality."""

    def test_demo_all_features(self):
        """Demonstrate all judge features like the scaffold test."""
        print("\n" + "="*50)
        print("TrainLoop Judge Test Suite")
        print("="*50)
        
        print("\n=== Prompt Inspection Demo ===")
        claim = "The code follows Python best practices."
        prompt = make_prompt(claim)
        
        print("Generated prompt:")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
        
        print("\n=== Configuration Demo ===")
        
        # Show default config
        default_cfg = _load_cfg(None)
        print("Default configuration:")
        for key, value in default_cfg.items():
            print(f"  {key}: {value}")
        
        # Show custom config
        custom_cfg = {
            "calls_per_model_per_claim": 1,
            "temperature": 0.3,
        }
        merged_cfg = _load_cfg(custom_cfg)
        print("\nCustom configuration:")
        for key, value in merged_cfg.items():
            print(f"  {key}: {value}")
        
        print("\n=== Mock Evaluation Demo ===")
        print("(Using mocked responses for reliable testing)")
        
        with mock_judge_calls(POSITIVE_RESPONSES):
            verdict = assert_true(
                "This is a helpful response.",
                "This is not a helpful response."
            )
        print(f"Mock verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
        
        print("\nDemo completed! For real API testing, use:")
        print("  pytest tests/unit/judge/ -m integration -v")
        print("  (requires API keys to be configured)")
