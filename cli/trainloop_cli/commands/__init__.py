"""TrainLoop Evaluations CLI commands."""

from .init import init_command as init_cmd
from .eval import eval_command as eval_cmd
from .studio import studio_command as studio_cmd
from .add import add_command as add_cmd
from .upgrade import upgrade_command as upgrade_cmd

__all__ = ["init_cmd", "eval_cmd", "studio_cmd", "add_cmd", "upgrade_cmd"]
