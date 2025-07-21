from trainloop_cli.eval_core.judge import assert_true
from trainloop_cli.eval_core.types import Sample


def is_active_voice(sample: Sample) -> int:
    rewritten = sample.output["content"].strip()
    yes = f'The sentence "{rewritten}" is written in active voice.'
    no = f'The sentence "{rewritten}" is NOT active voice.'

    # The assert_true function takes in a positive and negative prompt. e.g. "x is blue" and "x is not blue"
    return assert_true(yes, no)
