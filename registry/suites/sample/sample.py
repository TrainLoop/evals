from registry.metrics_registry import always_pass
from registry.helpers import tag

# You can define as many metrics as you like to test against and chain them here. These will run on every sample matching "my-tag".
results = tag("my-tag").check(always_pass, always_pass)
