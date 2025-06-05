from trainloop_cli.eval_core.helpers import tag
from ..metrics import is_helpful

# You can define as many metrics as you like to test against and chain them here. These will run on every sample matching "my-tag".
results = tag("my-tag").check(is_helpful)
