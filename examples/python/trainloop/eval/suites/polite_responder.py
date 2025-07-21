from trainloop_cli.eval_core.helpers import tag
from ..metrics.response_is_polite import response_is_polite
from ..metrics.response_is_less_than_120_words import response_is_less_than_120_words

results = tag("polite-responder").check(
    response_is_polite, response_is_less_than_120_words
)
