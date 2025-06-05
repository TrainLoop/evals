"""
Metric using the TrainLoop judge to evaluate response helpfulness.

This demonstrates how to use multiple assert_true calls to evaluate
different aspects of helpfulness in LLM outputs.
"""

from trainloop_cli.eval_core.judge import assert_true
from trainloop_cli.eval_core.types import Sample


def is_helpful(sample: Sample) -> int:
    """
    Evaluates if a response is helpful using multiple judge criteria.

    This metric uses the judge to evaluate several aspects:
    - Relevance: Does the response address the question?
    - Accuracy: Is the information provided correct?
    - Completeness: Are all aspects of the question covered?
    - Clarity: Is the response easy to understand?

    Args:
        sample: A sample containing 'input' messages and 'output' response

    Returns:
        1 if the response passes all helpfulness criteria, 0 otherwise
    """
    # Extract the user's question and the model's response
    messages = sample.input
    response = sample.output.get("content", "")

    # Find the last user message
    user_question = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_question = msg.get("content", "")
            break

    if not user_question or not response:
        return 0

    # Custom configuration for more thorough evaluation
    custom_cfg = {
        "models": ["openai/gpt-4o"],
        "calls_per_model_per_claim": 3,
        "temperature": 0.3,
    }

    # Check relevance
    relevance_yes = f"""
    This response directly addresses and is relevant to the user's question.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    relevance_no = f"""
    This response does NOT directly address or is NOT relevant to the user's question.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    relevance_score = assert_true(relevance_yes, relevance_no, cfg=custom_cfg)

    # Check accuracy
    accuracy_yes = f"""
    The information provided in this response is factually accurate and correct.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    accuracy_no = f"""
    The information provided in this response contains factual errors or is incorrect.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    accuracy_score = assert_true(accuracy_yes, accuracy_no, cfg=custom_cfg)

    # Check completeness
    completeness_yes = f"""
    This response thoroughly addresses all aspects of the user's question.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    completeness_no = f"""
    This response is incomplete and does NOT address all aspects of the user's question.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    completeness_score = assert_true(completeness_yes, completeness_no, cfg=custom_cfg)

    # Check clarity
    clarity_yes = f"""
    This response is clear, well-structured, and easy to understand.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    clarity_no = f"""
    This response is unclear, poorly structured, or difficult to understand.
    
    <Question>{user_question}</Question>
    <Response>{response}</Response>
    """

    clarity_score = assert_true(clarity_yes, clarity_no, cfg=custom_cfg)

    # Combine scores - require all aspects to pass for overall helpfulness
    total_score = relevance_score + accuracy_score + completeness_score + clarity_score

    # Return 1 only if all 4 aspects pass (total score = 4)
    return 1 if total_score == 4 else 0
