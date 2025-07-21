from trainloop_cli.eval_core.helpers import tag
from ..metrics.is_active_voice import is_active_voice

results = tag("active-voice").check(is_active_voice)
