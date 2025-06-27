#!/usr/bin/env python3
"""
TrainLoop Release Script - Automated release workflow

This script handles the complete release process:
1. Ensures you're on main branch and up to date
2. Creates release notes file (or uses existing one)
3. Creates release branch
4. Runs version bump
5. Creates PR to main
6. Provides instructions for merge and monitoring

Usage:
    python scripts/release.py minor "New FSSpec support and benchmarking"
    python scripts/release.py patch "Bug fixes and improvements"
    python scripts/release.py major "Breaking API changes"

Options:
    --release-notes PATH    Use existing release notes file
    --dry-run              Show what would be done without executing
    --skip-pr              Create branch and bump but don't create PR
"""

import argparse
import pathlib
import re
import subprocess
import sys
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
RELEASES_DIR = ROOT / "releases"
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def run_cmd(
    cmd: str, capture_output: bool = False, check: bool = True
) -> Optional[str]:
    """Run a shell command."""
    print(f"🔧 {cmd}")
    if capture_output:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip()
    else:
        subprocess.run(cmd, shell=True, check=check)
        return None


def get_current_version() -> str:
    """Get current version from VERSION file."""
    if not VERSION_FILE.exists():
        sys.exit("❌ VERSION file not found")

    version_text = VERSION_FILE.read_text().strip()
    if not SEMVER.fullmatch(version_text):
        sys.exit(f"❌ Malformed VERSION file: {version_text}")

    return version_text


def calculate_new_version(current: str, bump_type: str) -> str:
    """Calculate new version based on bump type."""
    match = SEMVER.fullmatch(current)
    if not match:
        sys.exit(f"❌ Invalid current version: {current}")

    major, minor, patch = map(int, match.groups())

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        sys.exit(f"❌ Invalid bump type: {bump_type}. Use major, minor, or patch.")


def check_git_status():
    """Ensure git repo is in a clean state."""
    print("🔍 Checking git status...")

    # Check if we're in a git repo
    try:
        run_cmd("git status", capture_output=True)
    except subprocess.CalledProcessError:
        sys.exit("❌ Not in a git repository")

    # Check for uncommitted changes
    status = run_cmd("git status --porcelain", capture_output=True)
    if status:
        print("❌ You have uncommitted changes:")
        print(status)
        sys.exit("Please commit or stash your changes before releasing")

    print("✅ Git status is clean")


def ensure_main_branch():
    """Ensure we're on main branch and up to date."""
    print("🔍 Checking current branch...")

    current_branch = run_cmd("git branch --show-current", capture_output=True)

    if current_branch != "main":
        print(f"🔄 Switching from {current_branch} to main...")
        run_cmd("git checkout main")

    print("🔄 Pulling latest changes...")
    run_cmd("git pull origin main")

    print("✅ On main branch and up to date")


def create_release_notes(
    new_version: str, description: str, existing_file: Optional[str] = None
) -> pathlib.Path:
    """Create or validate release notes file."""
    release_file = RELEASES_DIR / f"{new_version}.md"

    if existing_file:
        existing_path = pathlib.Path(existing_file)
        if not existing_path.exists():
            sys.exit(f"❌ Release notes file not found: {existing_file}")

        # Copy existing file to correct location
        release_file.write_text(existing_path.read_text())
        print(f"✅ Using existing release notes: {existing_file}")
        return release_file

    if release_file.exists():
        print(f"✅ Release notes already exist: {release_file}")
        return release_file

    print(f"📝 Creating release notes: {release_file}")

    # Create release notes template
    content = f"""Summary: {description}

**Release {new_version}**

The changes in this release include:

### 🚀 New Features
- {description}

### 🐛 Bug Fixes
- Various bug fixes and improvements

### 🛠️ Technical Improvements
- Performance optimizations
- Code quality improvements

For detailed technical information, see the commit history since the last release.
"""

    release_file.write_text(content)

    # Open in editor if available
    editor = run_cmd("echo $EDITOR", capture_output=True) or "nano"
    try:
        print(f"📝 Opening release notes in {editor} for editing...")
        print("   Please review and edit the release notes, then save and close.")
        input("   Press Enter when ready to continue...")
        run_cmd(f"{editor} {release_file}")
    except KeyboardInterrupt:
        sys.exit("❌ Release cancelled")
    except subprocess.CalledProcessError:
        print(f"⚠️  Could not open {editor}. Please edit {release_file} manually.")
        input("   Press Enter when you've finished editing the release notes...")

    # Validate release notes format
    content = release_file.read_text()
    if not content.startswith("Summary: "):
        sys.exit("❌ Release notes must start with 'Summary: <description>'")

    print("✅ Release notes created and validated")
    return release_file


def create_release_branch(new_version: str) -> str:
    """Create and checkout release branch."""
    branch_name = f"release/v{new_version}"

    print(f"🌿 Creating release branch: {branch_name}")

    # Check if branch already exists
    try:
        run_cmd(f"git rev-parse --verify {branch_name}", capture_output=True)
        print(f"⚠️  Branch {branch_name} already exists")
        choice = input(
            "   Do you want to (d)elete and recreate, (c)heckout existing, or (a)bort? [d/c/a]: "
        )

        if choice.lower() == "d":
            run_cmd(f"git branch -D {branch_name}")
            run_cmd(f"git checkout -b {branch_name}")
        elif choice.lower() == "c":
            run_cmd(f"git checkout {branch_name}")
        else:
            sys.exit("❌ Release cancelled")
    except subprocess.CalledProcessError:
        # Branch doesn't exist, create it
        run_cmd(f"git checkout -b {branch_name}")

    print(f"✅ On release branch: {branch_name}")
    return branch_name


def run_version_bump(bump_type: str):
    """Run the version bump script."""
    print(f"📈 Running version bump: {bump_type}")

    bump_script = ROOT / "scripts" / "bump" / "bump_version.py"
    if not bump_script.exists():
        sys.exit(f"❌ Bump script not found: {bump_script}")

    run_cmd(f"python {bump_script} {bump_type}")
    print("✅ Version bump completed")


def create_pull_request(new_version: str, description: str, branch_name: str):
    """Create pull request using GitHub CLI."""
    print("🔀 Creating pull request...")

    # Check if gh CLI is available
    try:
        run_cmd("gh --version", capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI (gh) is not installed")
        print("   Install it from: https://cli.github.com/")
        print(f"   Then manually create a PR from branch: {branch_name}")
        return

    # Check if user is authenticated
    try:
        run_cmd("gh auth status", capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Not authenticated with GitHub CLI")
        print("   Run: gh auth login")
        print(f"   Then manually create a PR from branch: {branch_name}")
        return

    pr_title = f"Release v{new_version}"
    pr_body = f"""# Release v{new_version}

{description}

## 🚀 Release Workflow
This PR updates the VERSION file to trigger the automated release workflow when merged.

**What happens after merge:**
1. ✅ GitHub Actions validates the release
2. 🏷️ Creates git tag `v{new_version}`
3. 🏗️ Builds all components (CLI, SDK, Studio)
4. 📦 Publishes to PyPI and NPM
5. 📋 Creates GitHub release

## 📋 Pre-merge Checklist
- [ ] Release notes are complete and accurate
- [ ] All tests are passing
- [ ] Version bump is correct
- [ ] Ready to publish to production

/cc @team for review
"""

    try:
        # Create the PR
        pr_url = run_cmd(
            f'gh pr create --title "{pr_title}" --body "{pr_body}"', capture_output=True
        )

        print(f"✅ Pull request created: {pr_url}")

        # Open PR in browser
        try:
            run_cmd("gh pr view --web", capture_output=True)
        except subprocess.CalledProcessError:
            pass

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create PR: {e}")
        print(f"   Manually create a PR from branch: {branch_name}")


def print_next_steps(new_version: str, pr_created: bool):
    """Print instructions for completing the release."""
    print("\n" + "=" * 60)
    print("🎉 RELEASE PREPARATION COMPLETE!")
    print("=" * 60)

    if pr_created:
        print(
            f"""
✅ Release v{new_version} is ready for review and merge!

📋 NEXT STEPS:
1. Review the pull request and get team approval
2. Merge the PR into main (DO NOT SQUASH - keep commit history)
3. Monitor the release workflow: https://github.com/trainloop/evals/actions
4. Verify packages are published:
   - PyPI: https://pypi.org/project/trainloop-cli/
   - NPM: https://www.npmjs.com/package/@trainloop/typescript-sdk
5. Check GitHub release: https://github.com/trainloop/evals/releases

⚠️  IMPORTANT: The release will be published automatically when the PR is merged!
"""
        )
    else:
        print(
            f"""
✅ Release v{new_version} branch is ready!

📋 NEXT STEPS:
1. Manually create a PR from the release branch to main
2. Get team approval and merge (DO NOT SQUASH)
3. Monitor the automated release workflow
4. Verify all packages are published correctly

⚠️  IMPORTANT: The release will be published automatically when merged to main!
"""
        )

    print("🔧 REQUIRED GITHUB SECRETS:")
    print("   Make sure these are configured in repository settings:")
    print("   - PYPI_TOKEN: For publishing Python packages to PyPI")
    print("   - NPM_TOKEN: For publishing TypeScript packages to NPM")
    print("   - GITHUB_TOKEN: Automatically available (for creating releases)")
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="TrainLoop automated release script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump to perform",
    )

    parser.add_argument(
        "description", help="Brief description of the release (used in release notes)"
    )

    parser.add_argument("--release-notes", help="Path to existing release notes file")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )

    parser.add_argument(
        "--skip-pr",
        action="store_true",
        help="Create branch and bump but don't create PR",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    print("🚀 TrainLoop Release Script")
    print("=" * 40)

    # Get current and new versions
    current_version = get_current_version()
    new_version = calculate_new_version(current_version, args.bump_type)

    print(f"📊 Current version: {current_version}")
    print(f"📈 New version: {new_version}")
    print(f"📝 Description: {args.description}")

    if args.dry_run:
        print("\n✅ DRY RUN COMPLETE - No changes made")
        return

    # Confirm with user
    confirm = input(f"\n🤔 Proceed with release v{new_version}? [y/N]: ")
    if confirm.lower() != "y":
        print("❌ Release cancelled")
        return

    try:
        # Execute release workflow
        check_git_status()
        ensure_main_branch()
        release_file = create_release_notes(
            new_version, args.description, args.release_notes
        )
        branch_name = create_release_branch(new_version)
        run_version_bump(args.bump_type)

        pr_created = False
        if not args.skip_pr:
            create_pull_request(new_version, args.description, branch_name)
            pr_created = True

        print_next_steps(new_version, pr_created)

    except KeyboardInterrupt:
        print("\n❌ Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
