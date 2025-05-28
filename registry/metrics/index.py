"""Index of available metrics in the TrainLoop registry."""

from pathlib import Path
from importlib import import_module
import sys

# Add registry to path so we can import configs
registry_path = Path(__file__).parent.parent
sys.path.insert(0, str(registry_path))

# Dynamically discover all metrics
components = []
metrics_dir = Path(__file__).parent

for metric_dir in metrics_dir.iterdir():
    if metric_dir.is_dir() and not metric_dir.name.startswith("_"):
        config_file = metric_dir / "config.py"
        if config_file.exists():
            try:
                # Import the config module
                module = import_module(f"metrics.{metric_dir.name}.config")
                if hasattr(module, "config"):
                    components.append({
                        "name": module.config.name,
                        "description": module.config.description,
                        "tags": module.config.tags,
                    })
            except ImportError as e:
                print(f"Failed to import metrics.{metric_dir.name}.config: {e}")
            except Exception as e:
                print(f"Error processing {metric_dir.name}: {e}")

# Clean up sys.path
sys.path.pop(0)
