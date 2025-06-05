from trainloop_cli.eval_core.types import Sample


def always_pass(_: Sample) -> int:  # 1 = pass, 0 = fail
    return 1
