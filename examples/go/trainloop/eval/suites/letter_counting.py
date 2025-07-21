from trainloop_cli.eval_core.helpers import tag
from ..metrics.outputs_single_codeblock import outputs_single_codeblock
from ..metrics.letter_count_format import letter_count_format

# Evaluation suite for letter counting
# Tests that the output contains a single code block with proper format and correct counts
results = tag("letter-counting").check(outputs_single_codeblock, letter_count_format)
