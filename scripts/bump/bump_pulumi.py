#!/usr/bin/env python3
"""
trainloop-pulumi - update docker tag in Pulumi YAML and (optionally) deploy.

usage:
  python scripts/pulumi.py           # just rewrites YAML
  python scripts/pulumi.py --up      # rewrite YAML, then `pulumi up --yes`
  python scripts/pulumi.py --preview # rewrite YAML, then `pulumi preview`
"""
from __future__ import annotations
import argparse
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
VER = ROOT.joinpath("VERSION").read_text(encoding="utf-8").strip()
REG = os.getenv("REGISTRY", "ghcr.io/trainloop")
IMAGE = f"{REG}/evals:{VER}"


def sh(cmd: str, cwd: pathlib.Path):
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def update_yaml(yaml: pathlib.Path) -> None:
    text = yaml.read_text()
    text = re.sub(r"^\s*appImage:.*$", f"  appImage: {REG}/evals", text, flags=re.M)
    text = re.sub(r"^\s*appVersion:.*$", f"  appVersion: {VER}", text, flags=re.M)
    yaml.write_text(text)
    print(f"📝 updated {yaml.name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--up", action="store_true", help="run pulumi up --yes")
    g.add_argument("--preview", action="store_true", help="run pulumi preview")
    args = ap.parse_args()

    for yaml in (ROOT / "infra").glob("Pulumi.*.yaml"):
        update_yaml(yaml)

    if args.up:
        sh("pulumi up --yes", ROOT / "infra")
    elif args.preview:
        sh("pulumi preview", ROOT / "infra")
    else:
        print("🔔 YAML updated - no pulumi command executed")


if __name__ == "__main__":
    main()
