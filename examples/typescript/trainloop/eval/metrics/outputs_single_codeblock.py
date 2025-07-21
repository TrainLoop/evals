from trainloop_cli.eval_core.types import Sample
import re


def outputs_single_codeblock(sample: Sample) -> int:  # 1 = pass, 0 = fail
    content = sample.output["content"]

    # Use regex to find complete code blocks
    # Pattern matches: optional whitespace, opening ```, optional language identifier, newline, content, newline, optional whitespace, closing ```
    pattern = r"\s*```[^\n]*\n(.*?)\n\s*```"
    matches = re.findall(pattern, content, re.DOTALL)

    return 1 if len(matches) == 1 else 0
