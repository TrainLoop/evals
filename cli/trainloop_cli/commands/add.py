"""TrainLoop add command for installing metrics and suites from the registry."""

import ast
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List
import click
import tomli
import yaml
from packaging import version as version_package


def get_current_version() -> str:
    """Get the current CLI version from pyproject.toml."""

    cli_root = Path(__file__).parent.parent.parent
    pyproject_path = cli_root / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)
        return data["tool"]["poetry"]["version"]


def fetch_from_github(path: str, version: str) -> str:
    """Fetch content from GitHub at a specific version."""
    url = f"https://raw.githubusercontent.com/TrainLoop/evals/v{version}/{path}"

    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise click.ClickException(f"Component not found at version {version}")
        else:
            raise click.ClickException(f"Failed to fetch from GitHub: {e}")


def parse_metadata(content: str) -> dict:
    """Parse metadata from config module using AST."""
    tree = ast.parse(content)

    # Find the config assignment
    config_data = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "config":
                    # Found the config assignment, extract the call arguments
                    if isinstance(node.value, ast.Call):
                        # Extract keyword arguments
                        for keyword in node.value.keywords:
                            key = keyword.arg
                            value = ast.literal_eval(keyword.value)
                            config_data[key] = value

    # Ensure all expected fields are present with defaults
    return {
        "name": config_data.get("name", ""),
        "description": config_data.get("description", ""),
        "min_version": config_data.get("min_version", "0.1.0"),
        "dependencies": config_data.get("dependencies", []),
        "author": config_data.get("author", "TrainLoop Team"),
        "tags": config_data.get("tags", []),
    }


def check_version_compatibility(metadata: Dict, cli_version: str) -> bool:
    """Check if component is compatible with current CLI version."""
    min_version = metadata.get("min_version", "0.0.0")

    return version_package.parse(cli_version) >= version_package.parse(min_version)


def get_trainloop_dir() -> Path:
    """Find the trainloop directory in the current project."""
    current = Path.cwd()

    # Look for trainloop directory
    trainloop_dir = current / "trainloop"
    if trainloop_dir.exists():
        return trainloop_dir

    # Look for trainloop.config.yaml
    config_path = current / "trainloop.config.yaml"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
            data_folder = config.get("dataFolder", "trainloop/data")
            # Extract the trainloop directory from data folder path
            return Path(data_folder).parent

    raise click.ClickException(
        "No trainloop directory found. Please run 'trainloop init' first."
    )


def rewrite_imports(content: str) -> str:
    """Rewrite registry imports to relative imports for the target environment."""
    replacements = {
        "from registry.types import": "from ..types import",
        "from registry.metrics import": "from ..metrics import",
        "from registry.helpers import": "from ..helpers import",
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Also remove TYPE_CHECKING imports as they're not needed in the target
    lines = content.split("\n")
    filtered_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        if "from typing import TYPE_CHECKING" in line:
            continue
        if "if TYPE_CHECKING:" in line:
            skip_next = True
            continue
        if skip_next and line.strip().startswith("from"):
            skip_next = False
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)


def install_metric(name: str, version: str, force: bool = False) -> bool:
    """Install a metric from the registry."""
    trainloop_dir = get_trainloop_dir()
    metrics_dir = trainloop_dir / "eval" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    target_file = metrics_dir / f"{name}.py"

    if target_file.exists() and not force:
        click.echo(f"Metric '{name}' already exists. Use --force to overwrite.")
        return False

    # Fetch metadata
    metadata_path = f"registry/metrics/{name}/config.py"
    metadata_content = fetch_from_github(metadata_path, version)
    metadata = parse_metadata(metadata_content)

    # Check version compatibility
    cli_version = get_current_version()
    if not check_version_compatibility(metadata, cli_version):
        raise click.ClickException(
            f"Metric '{name}' requires CLI version >= {metadata['min_version']}, "
            f"but you have {cli_version}"
        )

    # Fetch implementation
    impl_path = f"registry/metrics/{name}/{name}.py"
    impl_content = fetch_from_github(impl_path, version)

    # Rewrite imports for target environment
    impl_content = rewrite_imports(impl_content)

    # Write to target
    target_file.write_text(impl_content)

    # Update __init__.py
    update_metrics_init(metrics_dir, name)

    click.echo(f"✓ Installed metric '{name}'")
    return True


def install_suite(name: str, version: str, force: bool = False) -> None:
    """Install a suite and its dependencies from the registry."""
    trainloop_dir = get_trainloop_dir()
    suites_dir = trainloop_dir / "eval" / "suites"
    suites_dir.mkdir(parents=True, exist_ok=True)

    target_file = suites_dir / f"{name}.py"

    if target_file.exists() and not force:
        click.echo(f"Suite '{name}' already exists. Use --force to overwrite.")
        return

    # Fetch metadata
    metadata_path = f"registry/suites/{name}/config.py"
    metadata_content = fetch_from_github(metadata_path, version)
    metadata = parse_metadata(metadata_content)

    # Check version compatibility
    cli_version = get_current_version()
    if not check_version_compatibility(metadata, cli_version):
        raise click.ClickException(
            f"Suite '{name}' requires CLI version >= {metadata['min_version']}, "
            f"but you have {cli_version}"
        )

    # Install dependencies (metrics)
    dependencies = metadata.get("dependencies", [])
    installed_deps = []

    for dep in dependencies:
        click.echo(f"Installing dependency: {dep}")
        if install_metric(dep, version, force):
            installed_deps.append(dep)

    # Fetch suite implementation
    impl_path = f"registry/suites/{name}/{name}.py"
    impl_content = fetch_from_github(impl_path, version)

    # Rewrite imports for target environment
    impl_content = rewrite_imports(impl_content)

    # Write to target
    target_file.write_text(impl_content)

    click.echo(f"✓ Installed suite '{name}' with {len(installed_deps)} dependencies")


def update_metrics_init(metrics_dir: Path, metric_name: str) -> None:
    """Update the metrics __init__.py to include the new metric."""
    init_file = metrics_dir / "__init__.py"

    if not init_file.exists():
        # Create a new __init__.py
        init_file.write_text(f"from .{metric_name} import {metric_name}\n")
        return

    content = init_file.read_text()
    import_line = f"from .{metric_name} import {metric_name}"

    if import_line not in content:
        # Add the import
        lines = content.strip().split("\n")
        lines.append(import_line)
        lines.sort()  # Keep imports sorted
        init_file.write_text("\n".join(lines) + "\n")


def list_available(component_type: str, version: str) -> List[Dict]:
    """List available components from the registry."""
    index_path = f"registry/{component_type}/index.py"

    try:
        index_content = fetch_from_github(index_path, version)
        # Parse the Python module to extract components
        tree = ast.parse(index_content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "components":
                        # Found the components list
                        components = []
                        if isinstance(node.value, ast.List):
                            for item in node.value.elts:
                                if isinstance(item, ast.Call):
                                    # Extract component info from constructor call
                                    component_data = {}
                                    for keyword in item.keywords:
                                        key = keyword.arg
                                        value = ast.literal_eval(keyword.value)
                                        component_data[key] = value
                                    components.append(component_data)
                        return components
        return []
    except (urllib.error.URLError, SyntaxError):
        # Fallback: return empty list if can't fetch or parse
        return []


def add_command(
    component_type: str, name: str, force: bool, version: str, list_components: bool
):
    """Add metrics or suites from the TrainLoop registry.

    Examples:
        trainloop add metric always_pass
        trainloop add suite sample
        trainloop add metric --list
    """
    if version is None:
        version = get_current_version()

    if list_components:
        available = list_available(f"{component_type}s", version)
        if available:
            click.echo(f"Available {component_type}s:")
            for comp in available:
                click.echo(f"  - {comp}")
        else:
            click.echo(f"No {component_type}s found in registry")
        return

    try:
        if component_type == "metric":
            install_metric(name, version, force)
        else:  # suite
            install_suite(name, version, force)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
