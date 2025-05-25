"""TrainLoop Evaluations CLI entry point."""

import click
from trainloop_cli.commands.init import init_command as init_cmd
from trainloop_cli.commands.eval import eval_command as eval_cmd
from trainloop_cli.commands.studio import studio_command as studio_cmd


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
def init():
    """Scaffold data/ and eval/ directories, create sample metrics and suites."""
    init_cmd()


@cli.command("eval")
@click.option("--suite", help="Run only the specified suite instead of all suites.")
def run_eval(suite):
    """Discover suites, apply metrics to new events, append verdicts to data/results/."""
    eval_cmd(suite=suite)


def main():
    """Main entry point for the CLI."""
    # Pass control to Click - it will handle the context
    cli()


if __name__ == "__main__":
    # This allows the CLI to be run via python -m
    main()
