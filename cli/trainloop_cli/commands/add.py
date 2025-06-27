"""TrainLoop add command for installing metrics and suites from the registry."""

import ast
import sys
import types
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, cast
from importlib import metadata, import_module
import click
import tomli
import yaml
from packaging import version as version_package
import fsspec
from fsspec.spec import AbstractFileSystem


def get_current_version() -> str:
    """Get the current CLI version from installed package metadata."""
    try:
        return metadata.version("trainloop-cli")
    except metadata.PackageNotFoundError:
        # This might happen if running from source without installation or if package name is wrong
        # Fallback or raise a more specific error if needed
        # For now, let's try to read from pyproject.toml as a fallback for local dev
        try:
            cli_root = Path(__file__).parent.parent.parent
            pyproject_path = cli_root.parent / "pyproject.toml"
            if (
                not pyproject_path.exists()
            ):  # if .../cli/ is not project root, try another level up
                pyproject_path = cli_root.parent.parent / "pyproject.toml"

            if pyproject_path.exists():
                with open(pyproject_path, "rb", encoding="utf-8") as f:
                    data = tomli.load(f)
                    return data["tool"]["poetry"]["version"]
            return "0.0.0-dev"  # Fallback version if not found
        except Exception:
            return "0.0.0-unknown"  # Final fallback


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


def fetch_content(path: str, version: str, registry_path: Optional[str] = None) -> str:
    """Fetch content from either local registry or GitHub."""
    if registry_path:
        # Use local registry
        local_path = Path(registry_path) / path
        if not local_path.exists():
            raise click.ClickException(f"File not found in local registry: {path}")
        with open(local_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Fetch from GitHub
        return fetch_from_github(path, version)


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
        "No trainloop directory found. Please run 'trainloop init' first or run this command in the trainloop directory."
    )


def rewrite_imports(content: str) -> str:
    """Rewrite registry imports to absolute imports pointing to trainloop_cli.eval_core."""

    replacements = {
        "from registry.types import": "from trainloop_cli.eval_core.types import",
        "from registry.metrics_registry import": "from ..metrics import",
        "from registry.helpers import": "from trainloop_cli.eval_core.helpers import",
        "from registry.judge import": "from trainloop_cli.eval_core.judge import",
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    return content


def install_metric(
    name: str, version: str, force: bool = False, registry_path: Optional[str] = None
) -> bool:
    """Install a metric from the registry."""
    trainloop_dir = get_trainloop_dir()
    metrics_dir = trainloop_dir / "eval" / "metrics"

    # Use fsspec to create directory
    metrics_dir_str = str(metrics_dir)
    target_file_str = str(metrics_dir / f"{name}.py")
    fs_spec = fsspec.open(target_file_str, "w")
    fs = cast(AbstractFileSystem, fs_spec.fs)

    if fs:
        fs.makedirs(metrics_dir_str, exist_ok=True)
    else:
        raise ValueError(f"Failed to create directory {metrics_dir_str}")

    target_file = metrics_dir / f"{name}.py"

    if target_file.exists() and not force:
        click.echo(f"Metric '{name}' already exists. Use --force to overwrite.")
        return False

    # Fetch metadata
    if registry_path:
        # For local registry, don't include "registry/" prefix
        metadata_path = f"metrics/{name}/config.py"
    else:
        # For GitHub, include the full path
        metadata_path = f"registry/metrics/{name}/config.py"
    metadata_content = fetch_content(metadata_path, version, registry_path)
    metadata = parse_metadata(metadata_content)

    # Check version compatibility
    cli_version = get_current_version()
    if not check_version_compatibility(metadata, cli_version):
        raise click.ClickException(
            f"Metric '{name}' requires CLI version >= {metadata['min_version']}, "
            f"but you have {cli_version}"
        )

    # Fetch implementation
    if registry_path:
        impl_path = f"metrics/{name}/{name}.py"
    else:
        impl_path = f"registry/metrics/{name}/{name}.py"
    impl_content = fetch_content(impl_path, version, registry_path)

    # Rewrite imports for target environment
    impl_content = rewrite_imports(impl_content)

    # Write to target using fsspec
    with fsspec.open(str(target_file), "w") as f:
        f.write(impl_content)  # type: ignore

    click.echo(f"✓ Installed metric '{name}'")
    return True


def install_suite(
    name: str, version: str, force: bool = False, registry_path: Optional[str] = None
) -> None:
    """Install a suite and its dependencies from the registry."""
    trainloop_dir = get_trainloop_dir()
    suites_dir = trainloop_dir / "eval" / "suites"

    # Use fsspec to create directory
    suites_dir_str = str(suites_dir)
    target_file_str = str(suites_dir / f"{name}.py")
    fs_spec = fsspec.open(target_file_str, "w")
    fs = cast(AbstractFileSystem, fs_spec.fs)

    if fs:
        fs.makedirs(suites_dir_str, exist_ok=True)
    else:
        raise ValueError(f"Failed to create directory {suites_dir_str}")

    target_file = suites_dir / f"{name}.py"

    if target_file.exists() and not force:
        click.echo(f"Suite '{name}' already exists. Use --force to overwrite.")
        return

    # Fetch metadata
    if registry_path:
        # For local registry, don't include "registry/" prefix
        metadata_path = f"suites/{name}/config.py"
    else:
        # For GitHub, include the full path
        metadata_path = f"registry/suites/{name}/config.py"
    metadata_content = fetch_content(metadata_path, version, registry_path)
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
        if install_metric(dep, version, force, registry_path):
            installed_deps.append(dep)

    # Fetch suite implementation
    if registry_path:
        impl_path = f"suites/{name}/{name}.py"
    else:
        impl_path = f"registry/suites/{name}/{name}.py"
    impl_content = fetch_content(impl_path, version, registry_path)

    # Rewrite imports for target environment
    impl_content = rewrite_imports(impl_content)

    # Write to target using fsspec
    with fsspec.open(str(target_file), "w") as f:
        f.write(impl_content)  # type: ignore

    click.echo(f"✓ Installed suite '{name}' with {len(installed_deps)} dependencies")


def list_available(
    component_type: str, version: str, registry_path: Optional[str] = None
) -> List[Dict]:
    """List available components from the registry."""
    components = []

    if registry_path:
        # Use local registry - directly scan the directory
        component_dir = Path(registry_path) / f"{component_type}s"
        if not component_dir.exists():
            return []

        for item_dir in component_dir.iterdir():
            if item_dir.is_dir() and not item_dir.name.startswith("_"):
                config_file = item_dir / "config.py"
                if config_file.exists():
                    try:
                        # Read and parse the config file
                        config_content = config_file.read_text()
                        config_data = parse_metadata(config_content)
                        component_info = {
                            "name": config_data.get("name", item_dir.name),
                            "description": config_data.get("description", ""),
                            "tags": config_data.get("tags", []),
                        }
                        # Include dependencies for suites
                        if component_type == "suite" and "dependencies" in config_data:
                            component_info["dependencies"] = config_data["dependencies"]
                        components.append(component_info)
                    except Exception as e:
                        click.echo(
                            f"Warning: Failed to parse {item_dir.name}/config.py: {e}",
                            err=True,
                        )
    else:
        # Fetch from GitHub - use the index
        index_path = f"registry/{component_type}s/index.py"
        try:
            index_content = fetch_content(index_path, version, registry_path)

            index_module = types.ModuleType("index")
            index_module.__dict__["Path"] = Path
            index_module.__dict__["import_module"] = import_module
            index_module.__dict__["sys"] = sys

            exec(index_content, index_module.__dict__)
            components = index_module.__dict__.get("components", [])

            # Add GitHub URLs for each component
            for comp in components:
                comp["github_url"] = (
                    f"https://github.com/TrainLoop/evals/tree/v{version}/registry/{component_type}s/{comp['name']}"
                )

        except Exception:
            # Fallback for development
            local_path = (
                Path(__file__).parent.parent.parent.parent
                / f"registry/{component_type}s"
            )
            if local_path.exists():
                for item_dir in local_path.iterdir():
                    if item_dir.is_dir() and not item_dir.name.startswith("_"):
                        config_file = item_dir / "config.py"
                        if config_file.exists():
                            try:
                                config_content = config_file.read_text()
                                config_data = parse_metadata(config_content)
                                component_info = {
                                    "name": config_data.get("name", item_dir.name),
                                    "description": config_data.get("description", ""),
                                    "tags": config_data.get("tags", []),
                                    "github_url": f"https://github.com/TrainLoop/evals/tree/v{version}/registry/{component_type}s/{item_dir.name}",
                                }
                                # Include dependencies for suites
                                if (
                                    component_type == "suite"
                                    and "dependencies" in config_data
                                ):
                                    component_info["dependencies"] = config_data[
                                        "dependencies"
                                    ]
                                components.append(component_info)
                            except Exception:
                                pass

    return components


def add_command(
    component_type: str,
    name: Optional[str] = None,
    force: Optional[bool] = False,
    version: Optional[str] = None,
    list_components: Optional[bool] = False,
    registry_path: Optional[str] = None,
):
    """Add metrics or suites from the TrainLoop registry.

    Args:
        component_type: Type of component (metric or suite)
        name: Name of the component to install (optional when listing)
        force: Overwrite existing components
        version: Use a specific version (default: current CLI version)
        list_components: List available components instead of installing
        registry_path: Path to local registry directory (for development)
    """
    # Get current version if not specified
    if not version:
        version = get_current_version()

    if list_components:
        components = list_available(component_type, version, registry_path)
        if not components:
            click.echo(f"No {component_type}s available at version {version}")
            return

        click.echo(f"Available {component_type}s:")
        for comp in components:
            click.echo(f"\n  {comp['name']}: {comp['description']}")

            # Show dependencies for suites
            if component_type == "suite" and "dependencies" in comp:
                deps = comp["dependencies"]
                if deps:
                    click.echo(f"    Dependencies: {', '.join(deps)}")
                else:
                    click.echo("    Dependencies: none")

            # Show GitHub URL if not using local registry
            if not registry_path and "github_url" in comp:
                click.echo(f"    Source: {comp['github_url']}")

        return

    # Installation mode - name is required
    if not name:
        click.echo(f"Error: Name is required when installing a {component_type}")
        raise click.Abort()

    if component_type == "metric":
        success = install_metric(name, version, force, registry_path)
        if success:
            click.echo(f"Successfully installed metric: {name}")
    elif component_type == "suite":
        install_suite(name, version, force, registry_path)
        click.echo(f"Successfully installed suite: {name}")
