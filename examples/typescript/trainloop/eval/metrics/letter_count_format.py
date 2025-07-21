from trainloop_cli.eval_core.types import Sample
import re


def letter_count_format(sample: Sample) -> int:  # 1 = pass, 0 = fail
    content = sample.output["content"]
    input_content = sample.input[0]["content"]

    # Extract the sentence from the content
    sentence = input_content.split("<sentence>")[1].split("</sentence>")[0]

    # Convert to lowercase and filter only letters
    letters_only = ''.join(c.lower() for c in sentence if c.isalpha())
    
    # Get unique letters
    unique_letters = set(letters_only)

    # Extract content from code block
    pattern = r"```\s*\n(.*?)\n```"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        return 0

    code_block_content = matches[0].strip()

    # Expected letter counts
    expected_counts = {letter: letters_only.count(letter) for letter in unique_letters}

    # Parse the output
    lines = code_block_content.split("\n")
    found_counts = {}

    # Check each line follows the format "<letter> - <count>"
    line_pattern = r"^([a-zA-Z])\s*-\s*(\d+)$"  # Allow uppercase and lowercase

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(line_pattern, line)
        if not match:
            return 0

        letter, count = match.groups()
        found_counts[letter.lower()] = int(count)  # Normalize to lowercase

    # Verify all expected letters are present with correct counts
    if found_counts != expected_counts:
        return 0

    # Verify alphabetical order (case-insensitive)
    letters = list(found_counts.keys())
    if letters != sorted(letters):
        return 0

    return 1
