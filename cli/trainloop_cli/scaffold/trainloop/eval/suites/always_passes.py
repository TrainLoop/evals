from trainloop_cli.eval_core.helpers import tag
from ..metrics import always_pass

# You can define as many metrics as you like to test against and chain them here. These will run on every sample matching "my-tag".
results = tag("my-tag").check(always_pass, always_pass)
