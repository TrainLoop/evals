from trainloop_cli.eval_core.types import Sample


def response_is_less_than_120_words(sample: Sample) -> int:  # 1 = pass, 0 = fail
    resp = sample.output["content"]
    word_count = len(resp.split())
    return 1 if word_count <= 120 else 0
