from trainloop_llm_logging import collect, trainloop_tag

# Notice that this is imported BEFORE openai is imported! This is critical!
collect(flush_immediately=True)

from ai_request import make_ai_request


# Example usage
if __name__ == "__main__":
    prompt_text = """Write a Python function that calculates the factorial of a number recursively. 
The function should be named 'factorial' and take one parameter 'n'. 
It should return 1 if n is 0 or 1, and n * factorial(n-1) otherwise.
Include proper error handling for negative numbers.
Output only the code in a single code block, no explanations."""

    # Tag this request for the code generation evaluation suite
    headers = trainloop_tag("code-generation")
    response = make_ai_request(prompt_text, extra_headers=headers)
    if response:
        print("AI Response:", response)
