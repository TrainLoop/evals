#!/usr/bin/env python3
"""
TrainLoop Evals - Studio Publishing Script

This script publishes the TrainLoop Studio Runner package to GitHub releases.
"""

import os
import subprocess
import sys
import re
from pathlib import Path


def run_command(
    cmd, cwd=None, env=None, check=True, capture_output=False, interactive=False
):
    """Run a command with appropriate handling of output and input.

    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory
        env: Environment variables
        check: Whether to check the return code
        capture_output: Whether to capture and return output
        interactive: Whether to allow interactive input from the user
    """
    print(f"Running: {' '.join(cmd)}")

    if interactive:
        # For truly interactive commands, pass stdin/stdout/stderr directly
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            check=check,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return None  # No output to return as it went directly to terminal
    elif capture_output:
        # For non-interactive commands where we need to capture output
        result = subprocess.run(
            cmd, cwd=cwd, env=env, check=check, capture_output=True, text=True
        )
        return result.stdout.strip()
    else:
        # For non-interactive commands where we want to show output
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
        )

        # Print output in real-time
        for line in process.stdout:
            print(line, end="")

        # Wait for the process to complete
        return_code = process.wait()
        if check and return_code != 0:
            print(f"Error: Command failed with exit code {return_code}")
            sys.exit(return_code)
        return None


def check_command(cmd):
    """Check if a command is available."""
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_git_tags():
    """Get list of git tags."""
    try:
        result = subprocess.run(
            ["git", "tag"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return result.stdout.strip().split("\n")
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def extract_changelog_section(changelog_file, version):
    """Extract the section for the current version from the changelog."""
    if not os.path.exists(changelog_file):
        return None

    with open(changelog_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match the version header (e.g., "## 1.2.3 (2023-01-01)")
    version_pattern = rf"^## {re.escape(version)} \(.*?\)"
    version_match = re.search(version_pattern, content, re.MULTILINE)

    if not version_match:
        return None

    start_pos = version_match.start()

    # Find the next version header or end of file
    next_version_pattern = r"^## \d+\.\d+\.\d+ \(.*?\)"
    next_match = re.search(next_version_pattern, content[start_pos + 1 :], re.MULTILINE)

    if next_match:
        end_pos = start_pos + 1 + next_match.start()
        return content[start_pos:end_pos].strip()
    else:
        return content[start_pos:].strip()


def main():
    # Get script directory and project root
    script_dir = Path(__file__).resolve().parents[1]
    project_root = script_dir.parent

    # Check version file exists and get version
    version_file = project_root / "VERSION"
    if not version_file.exists():
        print(f"ERROR: VERSION file not found at {version_file}")
        sys.exit(1)

    with open(version_file, "r", encoding="utf-8") as f:
        version = f.read().strip()

    # Check that dist directory exists with required artifacts
    dist_dir = project_root / "dist"
    studio_package = dist_dir / f"trainloop-studio-runner-{version}.tgz"

    if not dist_dir.exists():
        print("ERROR: dist/ directory not found. Run build_studio.py first.")
        sys.exit(1)

    if not studio_package.exists():
        print(
            f"ERROR: Studio package not found at {studio_package}. Run build_studio.py first."
        )
        sys.exit(1)

    # Ensure GitHub CLI is installed
    if not check_command(["gh", "--version"]):
        print(
            "ERROR: GitHub CLI (gh) not found. Install it from https://cli.github.com/"
        )
        sys.exit(1)

    tag_name = f"v{version}"

    # Extract the relevant portion of the changelog for this version
    print(f"📝 Extracting release notes for v{version}...")
    release_notes_file = dist_dir / f"release-notes-v{version}.md"
    changelog_file = project_root / "CHANGELOG.md"

    # Check if CHANGELOG.md exists and extract section
    changelog_section = extract_changelog_section(changelog_file, version)

    # Create release notes file
    with open(release_notes_file, "w", encoding="utf-8") as f:
        if changelog_section:
            f.write(changelog_section + "\n\n")
        else:
            if changelog_file.exists():
                print(
                    f"WARNING: Could not extract release notes for version {version} from CHANGELOG.md"
                )
            else:
                print(f"WARNING: CHANGELOG.md not found at {changelog_file}")

            # Create a simple release note
            f.write(f"TrainLoop Studio v{version}\n\n")

        # Add note about SDK and CLI availability
        f.write("---\n")
        f.write("**Note:** Corresponding SDK and CLI versions are available via:\n")
        f.write(f"- Python SDK: `pip install trainloop-evals-sdk=={version}`\n")
        f.write(f"- TypeScript SDK: `npm install trainloop-evals-sdk@{version}`\n")
        f.write(f"- CLI: `pip install trainloop-cli=={version}`\n")
        f.write(
            f"- Studio: `npx --yes https://github.com/trainloop/evals/releases/download/v{version}/trainloop-studio-runner-{version}.tgz` or `trainloop studio` if cli is installed\n"
        )

    # Check if the release already exists
    print(f"🔍 Checking if GitHub release v{version} already exists...")
    release_exists = False
    try:
        # Use 'gh release view' to check if the release exists
        result = run_command(
            ["gh", "release", "view", tag_name, "--json", "name"],
            capture_output=True,
            check=False,  # Don't error out if release doesn't exist
        )
        # If we get a result, the release exists
        if result and not result.startswith("release not found"):
            release_exists = True
    except Exception:
        # If there's an error, assume the release doesn't exist
        release_exists = False

    if release_exists:
        print(f"WARNING: Release {tag_name} already exists.")
        response = input("Do you want to continue anyway? (y/N) ")
        if not response.lower().startswith("y"):
            print("Release creation aborted.")
            sys.exit(1)

        print(f"🔄 Updating release {tag_name}...")
        try:
            # Upload the package with --clobber to overwrite if it exists
            run_command(
                ["gh", "release", "upload", tag_name, str(studio_package), "--clobber"]
            )

            # Update release notes
            run_command(
                [
                    "gh",
                    "release",
                    "edit",
                    tag_name,
                    "--notes-file",
                    str(release_notes_file),
                ]
            )
            print(f"✅ Successfully updated release v{version}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to update release: {e}")
            sys.exit(1)
    else:
        print(f"🚀 Creating new GitHub release v{version}...")
        try:
            run_command(
                [
                    "gh",
                    "release",
                    "create",
                    tag_name,
                    "--title",
                    f"TrainLoop Studio v{version}",
                    "--notes-file",
                    str(release_notes_file),
                    str(studio_package),
                ],
                check=True,
            )
            print(f"✅ Successfully created release v{version}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to create release: {e}")
            sys.exit(1)

    # Clean up temporary file
    if release_notes_file.exists():
        os.unlink(release_notes_file)

    # Get repo info for the URL
    repo_info = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
    )

    print(f"✅ GitHub release v{version} created successfully!")
    print(f"🔗 https://github.com/{repo_info}/releases/tag/{tag_name}")
    print("🎉 Release process completed!")


if __name__ == "__main__":
    main()
