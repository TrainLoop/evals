"""TrainLoop Evaluations CLI entry point."""

import click
from trainloop_cli.commands.init import init_command as init_cmd
from trainloop_cli.commands.eval import eval_command as eval_cmd
from trainloop_cli.commands.studio import studio_command as studio_cmd
from trainloop_cli.commands.add import add_command
from trainloop_cli.commands.benchmark import benchmark_command as benchmark_cmd


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option()
def cli():
    """
    TrainLoop Evaluations - A lightweight test harness for validating LLM behaviour.

    Run without a command to launch the local viewer (studio).
    """
    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        studio_cmd(config_path=None, local_tar_path=None)


@cli.command("studio")
@click.option("--config", help="Path to the trainloop config file.")
@click.option("--local", help="Path to a local studio tar file.")
def studio(config, local):
    """Launch the TrainLoop Studio UI for visualizing and analyzing your evaluation data."""
    studio_cmd(config_path=config, local_tar_path=local)


@cli.command("init")
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite an existing 'trainloop' directory if it exists.",
)
def init(force: bool):
    """Scaffold data/ and eval/ directories, create sample metrics and suites."""
    init_cmd(force=force)


@cli.command("eval")
@click.option("--suite", help="Run only the specified suite instead of all suites.")
def run_eval(suite):
    """Discover suites, apply metrics to new events, append verdicts to data/results/."""
    eval_cmd(suite=suite)


@cli.command("add")
@click.argument(
    "component_type", type=click.Choice(["metric", "suite"]), required=False
)
@click.argument("name", required=False)
@click.option("--force", is_flag=True, help="Overwrite existing components")
@click.option("--version", help="Use a specific version (default: current CLI version)")
@click.option(
    "--list", "list_components", is_flag=True, help="List available components"
)
@click.option(
    "--registry",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to local registry directory (for development)",
)
def add(component_type, name, force, version, list_components, registry):
    """Add metrics or suites from the TrainLoop registry.

    Examples:
        trainloop add --list                # List all metrics and suites
        trainloop add metric --list         # List all metrics
        trainloop add suite --list          # List all suites
        trainloop add metric always_pass    # Install the always_pass metric
        trainloop add suite sample          # Install the sample suite

        # Use local registry for development
        trainloop add --registry /path/to/registry --list
        trainloop add --registry /path/to/registry metric always_pass
    """

    # Handle listing mode
    if list_components:
        if not component_type:
            # List both metrics and suites
            add_command("metric", None, force, version, True, registry)
            click.echo()  # Add a blank line between metrics and suites
            add_command("suite", None, force, version, True, registry)
        else:
            # List specific component type
            add_command(component_type, None, force, version, True, registry)
    else:
        # Installation mode - require both component_type and name
        if not component_type or not name:
            click.echo(
                "Error: Both component type and name are required when not using --list"
            )
            click.echo("Try 'trainloop add --help' for more information.")
            raise click.Abort()
        add_command(component_type, name, force, version, False, registry)


@cli.command("benchmark")
def benchmark():
    """Compare evaluation results across multiple LLM providers."""
    benchmark_cmd()


def main():
    """Main entry point for the CLI."""
    # Pass control to Click - it will handle the context
    cli()


if __name__ == "__main__":
    # This allows the CLI to be run via python -m
    main()
