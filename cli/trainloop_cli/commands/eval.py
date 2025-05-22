"""TrainLoop CLI - ultra-thin `eval` wrapper."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional
from .utils import find_root, load_config_for_cli


# --------------------------------------------------------------------------- #
# Public entry-point (invoked by Click)
# --------------------------------------------------------------------------- #
def eval_command(suite: Optional[str] = None) -> None:
    """
    trainloop eval                # run every suite
    trainloop eval --suite foo    # run only suite 'foo'
    """
    try:
        root = find_root()
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    load_config_for_cli(root)
    os.chdir(root)  # so relative paths inside the runner resolve

    cmd = [sys.executable, "-m", "eval.runner"]
    if suite:
        cmd.append(suite)

    # Stream output directly; propagate same exit-code
    proc = subprocess.run(cmd, check=False)
    sys.exit(proc.returncode)
