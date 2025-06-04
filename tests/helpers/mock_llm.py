"""
Mock LLM responses for testing judge functionality.
"""

from typing import Dict, List, Optional
from unittest.mock import patch


class MockLLMResponse:
    """Mock response object that mimics litellm response structure."""

    def __init__(self, content: str):
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock choice object."""

    def __init__(self, content: str):
        self.message = MockMessage(content)


class MockMessage:
    """Mock message object."""

    def __init__(self, content: str):
        self.content = content


class MockJudge:
    """Mock judge for testing without real LLM calls."""

    def __init__(self, responses: Optional[Dict[str, List[str]]] = None):
        """
        Args:
            responses: Dict mapping claim substrings to lists of responses.
                    If None, uses default responses.
        """
        self.responses = responses or {
            "something a dog would do": ["true", "yes", "correct"],
            "not something a dog would do": ["false", "no", "incorrect"],
            "factual": ["true", "yes"],
            "not factual": ["false", "no"],
            "helpful": ["true", "yes"],
            "not helpful": ["false", "no"],
        }
        self.call_count = 0

    async def mock_acompletion(
        self, model: str, messages: List[Dict], **kwargs
    ) -> MockLLMResponse:
        """Mock the litellm.acompletion function."""
        self.call_count += 1

        # Extract the claim from the prompt
        prompt = messages[0]["content"]

        # Find matching response based on claim content
        for key, responses in self.responses.items():
            if key.lower() in prompt.lower():
                # Cycle through responses for consistency testing
                response_idx = (self.call_count - 1) % len(responses)
                response = responses[response_idx]

                # Format as expected by judge
                formatted_response = f"""
<reasoning>
Based on the claim analysis, this appears to be {response}.
</reasoning>

<result>
{response}
</result>
"""
                return MockLLMResponse(formatted_response)

        # Default response if no match found
        return MockLLMResponse(
            """
<reasoning>
Unable to determine from the given information.
</reasoning>

<result>
false
</result>
"""
        )


def mock_judge_calls(responses: Optional[Dict[str, List[str]]] = None):
    """
    Context manager that mocks litellm calls for judge testing.

    Usage:
        with mock_judge_calls({"helpful": ["true", "yes"]}):
            verdict = assert_true("This is helpful", "This is not helpful")
    """
    mock_judge = MockJudge(responses)
    return patch("litellm.acompletion", side_effect=mock_judge.mock_acompletion)


# Predefined response sets for common test scenarios
POSITIVE_RESPONSES = {
    "helpful": ["true", "yes", "correct", "true"],
    "not helpful": ["false", "no", "incorrect", "false"],
    "accurate": ["true", "yes", "correct", "true"],
    "not accurate": ["false", "no", "incorrect", "false"],
    "clear": ["true", "yes", "correct", "true"],
    "not clear": ["false", "no", "incorrect", "false"],
}

NEGATIVE_RESPONSES = {
    "helpful": ["false", "no", "incorrect", "false"],
    "not helpful": ["true", "yes", "correct", "true"],
    "accurate": ["false", "no", "incorrect", "false"],
    "not accurate": ["true", "yes", "correct", "true"],
}

MIXED_RESPONSES = {
    "helpful": ["true", "false", "yes", "no"],
    "not helpful": ["false", "true", "no", "yes"],
}

ABSTAIN_RESPONSES = {
    "helpful": ["unclear", "unknown", "cannot determine"],
    "not helpful": ["unclear", "unknown", "cannot determine"],
}
