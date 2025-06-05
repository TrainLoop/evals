from registry.metrics_registry import is_helpful
from registry.helpers import tag

# You can define as many metrics as you like to test against and chain them here. These will run on every sample matching "my-tag".
results = tag("my-tag").check(is_helpful)
