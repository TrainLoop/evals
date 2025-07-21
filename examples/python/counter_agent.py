from trainloop_llm_logging import collect, trainloop_tag

# Notice that this is imported BEFORE openai is imported! This is critical!
collect(flush_immediately=True)

from ai_request import make_ai_request


# Example usage
if __name__ == "__main__":
    sentence = "I love strawberries"
    prompt_text = f"""
Count the occurrences of each letter in the following sentence: <sentence>{sentence}</sentence>.
Output your answer in a code block with each letter and its count on a separate line.
Use the exact format: <letter> - <count>
Only include letters that appear in the word.
Sort the letters alphabetically.
"""

    # Tag this request for the letter counting evaluation suite
    headers = trainloop_tag("letter-counting")
    response = make_ai_request(prompt_text, extra_headers=headers)
    if response:
        print("AI Response:", response)
