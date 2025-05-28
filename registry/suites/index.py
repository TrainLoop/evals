"""Index of available suites in the TrainLoop registry."""

from pathlib import Path
from importlib import import_module
import sys

# Add registry to path so we can import configs
registry_path = Path(__file__).parent.parent
sys.path.insert(0, str(registry_path))

# Dynamically discover all suites
components = []
suites_dir = Path(__file__).parent

for suite_dir in suites_dir.iterdir():
    if suite_dir.is_dir() and not suite_dir.name.startswith("_"):
        config_file = suite_dir / "config.py"
        if config_file.exists():
            try:
                # Import the config module
                module = import_module(f"suites.{suite_dir.name}.config")
                if hasattr(module, "config"):
                    components.append({
                        "name": module.config.name,
                        "description": module.config.description,
                        "dependencies": module.config.dependencies,
                        "tags": module.config.tags,
                    })
            except ImportError:
                pass  # Skip suites that can't be imported

# Clean up sys.path
sys.path.pop(0)
