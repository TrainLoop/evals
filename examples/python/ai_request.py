from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client (reads the key from the OPENAI_API_KEY env var).
client = OpenAI()


def make_ai_request(
    prompt: str,
    model: str = "gpt-4.1",
    max_tokens: int = 500,
    extra_headers: dict = {},
):
    """
    Makes a request to the OpenAI API using the specified model and prompt.

    :param prompt: The prompt string to send to the model.
    :param model: The model ID to use for the request. Defaults to (GPT-4.1).
    :param max_tokens: Maximum number of tokens to generate in the response.
    :param extra_headers: Additional headers to pass with the request (e.g., for tagging).
    :return: The AI's response as a string.
    """
    try:
        # The new SDK exposes completion endpoints via
        # the `client.completions` namespace.
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            extra_headers=extra_headers,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
