from trainloop_cli.eval_core.judge import assert_true
from trainloop_cli.eval_core.types import Sample


def response_is_polite(sample: Sample) -> int:  # 1 = pass, 0 = fail
    resp = sample.output["content"]
    yes = f"The reply '{resp}' is polite, apologetic, and offers a clear resolution."
    no = f"The reply '{resp}' is rude OR fails to apologise OR lacks a resolution."
    # The assert_true function takes in a positive and negative prompt. e.g. "x is blue" and "x is not blue"
    return assert_true(yes, no)
