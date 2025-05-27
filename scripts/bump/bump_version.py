#!/usr/bin/env python3
"""
trainloop-bump-version - bump VERSION everywhere, update CHANGELOG, commit, tag, push

usage:
  python scripts/bump_version.py (major|minor|patch)
  
The script expects a release file to exist at releases/<new_version>.md
"""
from __future__ import annotations
import argparse
import datetime
import pathlib
import re
import subprocess
import sys
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"
RELEASES_DIR = ROOT / "releases"
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")

# places that carry a version field
UI_PKG = ROOT / "ui" / "package.json"
TS_PKG = ROOT / "sdk" / "typescript" / "package.json"
RUNNER_PKG = ROOT / "runner" / "package.json"
CLI_PYPROJECT = ROOT / "cli" / "pyproject.toml"
SDK_PYPROJECT = ROOT / "sdk" / "python" / "pyproject.toml"


def sh(cmd: str):
    subprocess.run(cmd, shell=True, check=True)


# -------------------------------------------------------------------------- #
# version helpers
# -------------------------------------------------------------------------- #
def read_version() -> tuple[int, int, int]:
    m = SEMVER.fullmatch(VERSION_FILE.read_text().strip())
    if not m:
        sys.exit("Malformed VERSION file")
    return tuple(map(int, m.groups()))


def bump(part: str) -> str:
    major, minor, patch = read_version()
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    elif part == "patch":
        patch = patch + 1
    else:
        sys.exit("part must be major|minor|patch")
    ver = f"{major}.{minor}.{patch}"
    VERSION_FILE.write_text(ver + "\n")
    return ver


# -------------------------------------------------------------------------- #
# update helper functions
# -------------------------------------------------------------------------- #
def bump_json(pkg_path: pathlib.Path, ver: str) -> None:
    data = json.loads(pkg_path.read_text())
    data["version"] = ver
    pkg_path.write_text(json.dumps(data, indent=2) + "\n")


def regen_lock(pkg_dir: pathlib.Path) -> None:
    """Run `npm install --package-lock-only` in pkg_dir to refresh lock file."""
    subprocess.run(
        ["npm", "install", "--package-lock-only", "--omit=dev"],
        check=True,
        cwd=pkg_dir,
        stdout=subprocess.PIPE,
    )


def bump_pyproject(toml_path: pathlib.Path, ver: str) -> None:
    txt = toml_path.read_text()
    txt = re.sub(r'^version\s*=\s*".*"$', f'version = "{ver}"', txt, flags=re.M)
    toml_path.write_text(txt)


def prepend_changelog(ver: str) -> None:
    """Add a changelog entry that links to the release file."""
    date = datetime.date.today().isoformat()
    entry = f"## {ver} ({date})\n[Release Notes](releases/{ver}.md)\n\n"
    
    if not CHANGELOG.exists():
        CHANGELOG.write_text("# Changelog\n\n" + entry)
        return
    
    lines = CHANGELOG.read_text().splitlines(keepends=True)
    if lines and lines[0].lower().startswith("#"):
        new = "".join(lines[:1]) + "\n" + entry + "".join(lines[1:])
    else:
        new = entry + "".join(lines)
    CHANGELOG.write_text(new)


def get_release_message(ver: str) -> str:
    """Read the release message from releases/<version>.md file."""
    release_file = RELEASES_DIR / f"{ver}.md"
    if not release_file.exists():
        sys.exit(f"Release file not found: {release_file}\n"
                f"Please create the release notes at {release_file} before bumping the version.")
    return release_file.read_text().strip()


def get_commit_message(msg: str) -> str:
    """
    Get a short commit message from the full message.
    If the message has multiple lines, use the first line.
    If it has markdown formatting, extract the key text.
    """
    # Remove markdown formatting for commit message
    msg = msg.strip()
    # Get first line
    first_line = msg.split('\n')[0]
    # Remove common markdown elements
    first_line = re.sub(r'^\W+', '', first_line)  # Remove leading symbols
    first_line = re.sub(r'\*\*(.+?)\*\*', r'\1', first_line)  # Remove bold
    first_line = re.sub(r'`(.+?)`', r'\1', first_line)  # Remove code formatting
    return first_line.strip()


# -------------------------------------------------------------------------- #
# main
# -------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["major", "minor", "patch"])
    args = ap.parse_args()

    # Calculate new version first (without writing it yet)
    major, minor, patch = read_version()
    if args.part == "major":
        new_major, new_minor, new_patch = major + 1, 0, 0
    elif args.part == "minor":
        new_major, new_minor, new_patch = major, minor + 1, 0
    elif args.part == "patch":
        new_major, new_minor, new_patch = major, minor, patch + 1
    
    new_ver = f"{new_major}.{new_minor}.{new_patch}"
    
    # Check if release file exists
    full_message = get_release_message(new_ver)
    commit_msg = get_commit_message(full_message)

    # Now actually bump the version
    ver = bump(args.part)

    # bump JS package.json files
    bump_json(UI_PKG, ver)
    bump_json(TS_PKG, ver)
    bump_json(RUNNER_PKG, ver)

    # refresh lock files that exist
    regen_lock(TS_PKG.parent)
    regen_lock(UI_PKG.parent)
    regen_lock(RUNNER_PKG.parent)

    # bump Python project versions
    bump_pyproject(CLI_PYPROJECT, ver)
    bump_pyproject(SDK_PYPROJECT, ver)

    prepend_changelog(ver)

    # files to commit --------------------------------------------------------
    files_to_add = [
        "VERSION",
        "CHANGELOG.md",
        UI_PKG.relative_to(ROOT),
        TS_PKG.relative_to(ROOT),
        RUNNER_PKG.relative_to(ROOT),
        RUNNER_PKG.parent / "package-lock.json",
        TS_PKG.parent / "package-lock.json",
        UI_PKG.parent / "package-lock.json",
        CLI_PYPROJECT.relative_to(ROOT),
        SDK_PYPROJECT.relative_to(ROOT),
    ]

    sh("git add " + " ".join(map(str, files_to_add)))
    sh(f"git commit -m 'chore: release {ver} - {commit_msg}'")
    sh(f"git tag -a v{ver} -m '{commit_msg}'")
    sh("git push origin main --tags")
    print(f"✅ bumped to {ver}, changelog updated, pushed to origin")


if __name__ == "__main__":
    main()
