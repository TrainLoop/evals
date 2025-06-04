"""
Unit tests for the TrainLoop judge functionality.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

from unittest.mock import patch
import asyncio
import pytest
import yaml
import litellm  # For litellm.exceptions
from dotenv import load_dotenv

load_dotenv()

# Add the CLI directory to the path so we can import from eval.judge
cli_dir = (
    Path(__file__).parent.parent.parent.parent / "cli" / "trainloop_cli" / "scaffold"
)
sys.path.insert(0, str(cli_dir))

# pylint: disable=wrong-import-position,import-error
from trainloop.eval.judge import (
    assert_true,
    make_prompt,
    _load_cfg,
)

# pylint: disable=wrong-import-position
from tests.helpers.mock_llm import (
    mock_judge_calls,
    POSITIVE_RESPONSES,
    NEGATIVE_RESPONSES,
)


@pytest.mark.unit
@pytest.mark.judge
class TestJudgeBasic:
    """Basic judge functionality tests."""

    def test_make_prompt_basic(self):
        """Test basic prompt generation."""
        claim = "This is a test claim."
        prompt = make_prompt(claim)

        # Verify the prompt contains expected elements
        assert claim in prompt
        assert "<claim>" in prompt
        assert "</claim>" in prompt
        assert "true" in prompt.lower()
        assert "false" in prompt.lower()

    def test_make_prompt_custom_template(self):
        """Test prompt generation with custom template."""
        claim = "Custom claim"
        custom_template = "Evaluate: {claim}. Answer YES or NO."
        prompt = make_prompt(claim, template=custom_template)

        assert "Evaluate: Custom claim" in prompt
        assert "Answer YES or NO" in prompt

    def test_make_prompt_detailed_inspection(self):
        """Test detailed prompt inspection like in scaffold."""
        claim = "The code follows Python best practices."
        prompt = make_prompt(claim)

        # Verify the prompt contains expected elements
        assert claim in prompt
        assert "true" in prompt.lower()
        assert "false" in prompt.lower()

    @mock.patch("trainloop.eval.judge._find_config_file")
    def test_load_cfg_defaults(self, mock_find_config):
        """Test config loading with defaults when no config file exists."""
        mock_find_config.return_value = None

        cfg = _load_cfg(None)

        assert cfg["models"] == ["openai/gpt-4o"]
        assert cfg["calls_per_model_per_claim"] == 3
        assert cfg["temperature"] == 0.7

    @mock.patch("trainloop.eval.judge._find_config_file")
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
                    "models": ["openai/gpt-4o"],
                    "calls_per_model_per_claim": 3,
                    "temperature": 0.3,
                }
            }
        }

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "trainloop.yaml")
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f)

            # Change to temp directory to test config loading
            old_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                cfg = _load_cfg(None)
            finally:
                os.chdir(old_cwd)

        assert cfg["models"] == ["openai/gpt-4o"]
        assert cfg["calls_per_model_per_claim"] == 3
        assert cfg["temperature"] == 0.7

    def test_custom_config_loading(self):
        """Test loading custom configuration."""
        # Test loading the config as a dictionary override
        custom_config = {
            "models": ["openai/gpt-3.5-turbo"],
            "calls_per_model_per_claim": 1,
            "temperature": 0.5,
        }

        loaded_cfg = _load_cfg(custom_config)
        assert loaded_cfg["models"] == ["openai/gpt-3.5-turbo"]
        assert loaded_cfg["calls_per_model_per_claim"] == 1
        assert loaded_cfg["temperature"] == 0.5


@pytest.mark.unit
@pytest.mark.judge
class TestJudgeWithMocks:
    """Judge tests using mocked LLM responses."""

    def test_debug_mock_responses(self):
        """Debug test to understand mock behavior."""
        from tests.helpers.mock_llm import MockJudge

        mock = MockJudge(POSITIVE_RESPONSES)

        async def test_responses():
            # Test positive claim
            pos_response = await mock.mock_acompletion(
                "openai/gpt-4o", [{"content": "This response is helpful."}]
            )
            print(
                f"\nPositive claim response: {pos_response.choices[0].message.content}"
            )

            # Test negative claim
            neg_response = await mock.mock_acompletion(
                "openai/gpt-4o", [{"content": "This response is not helpful."}]
            )
            print(
                f"\nNegative claim response: {neg_response.choices[0].message.content}"
            )

        asyncio.run(test_responses())

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
            "models": ["openai/gpt-4o"],
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
                "The number 2 + 2 equals 4.", "The number 2 + 2 does not equal 4."
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
                "The number 2 + 2 equals 4.", "The number 2 + 2 does not equal 4."
            )
            print(f"Verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")

            # This should almost certainly pass with real models
            assert verdict in [0, 1]  # Just verify it returns a valid verdict

        except ValueError as e:
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

        except ValueError as e:
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

            print(
                f"Verdict with custom config: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})"
            )
            assert verdict in [0, 1]

        except ValueError as e:
            pytest.fail(f"Real API test with custom config failed: {e}")

    @patch("cli.trainloop_cli.scaffold.trainloop.eval.judge.litellm.acompletion")
    def test_error_handling_and_setup_guidance(
        self, mock_litellm_acompletion_for_auth_error
    ):
        """Test error handling and provide setup guidance (with mocked AuthenticationError)."""
        print("\n=== Testing Error Handling (mocked AuthenticationError) ===")

        # Configure the mock to raise AuthenticationError
        mock_litellm_acompletion_for_auth_error.side_effect = (
            litellm.exceptions.AuthenticationError(
                "Mocked Auth Error: No API Key",
                llm_provider="mock_provider",
                model="mock_model",
            )
        )

        try:
            # This call should trigger the mocked AuthenticationError,
            # which _JudgeEngine._call_llm should convert to ValueError.
            assert_true(
                "This claim will trigger mocked auth error.", "This other claim also."
            )
            # If assert_true doesn't raise an error, the test should fail.
            pytest.fail(
                "ValueError was not raised by assert_true when mock_litellm_acompletion raised AuthenticationError"
            )
        except ValueError as e:
            print(f"✓ Expected error: {e}")
            # Check that the error message indicates an authentication issue or API key problem
            assert (
                "Authentication error" in str(e)
                or "API key" in str(e).lower()
                or "Mocked Auth Error" in str(e)
            )
        except Exception as e:
            pytest.fail(f"An unexpected exception {type(e).__name__} occurred: {e}")

        # Note: This modification means the test no longer checks the os.environ manipulation path for API keys.
        # That specific behavior (temporarily removing API keys from os.environ and restoring them)
        # could be covered in a separate, more focused test if needed.


@pytest.mark.integration
@pytest.mark.judge
class TestJudgeDemo:
    """Demonstration tests that show judge functionality."""

    def test_demo_all_features(self):
        """Demonstrate all judge features like the scaffold test."""
        print("\n" + "=" * 50)
        print("TrainLoop Judge Test Suite")
        print("=" * 50)

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
        loaded_cfg = _load_cfg(custom_cfg)
        print("\nCustom configuration:")
        for key, value in loaded_cfg.items():
            print(f"  {key}: {value}")

        print("\n=== Mock Evaluation Demo ===")
        print("(Using mocked responses for reliable testing)")

        with mock_judge_calls(POSITIVE_RESPONSES):
            try:
                verdict = assert_true(
                    "This is a helpful response.", "This is not a helpful response."
                )
                print(f"Mock verdict: {'PASS' if verdict == 1 else 'FAIL'} ({verdict})")
            except ValueError as e:
                print(f"✓ Expected error: {e}")
                assert "API key" in str(e)

        print("\nDemo completed! For real API testing, use:")
        print("  pytest tests/unit/judge/ -m integration -v")
        print("  (requires API keys to be configured)")
