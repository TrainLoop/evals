#!/usr/bin/env python3
"""
TrainLoop Release Script - Automated release workflow

This script handles the complete release process:
1. Ensures you're on main branch and up to date
2. Creates release notes file using Claude Code AI (or manual template)
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
    --no-claude            Skip Claude Code generation and use manual template

Claude Code Integration:
    If Claude Code CLI is available, the script will:
    - Analyze git commits since the last release
    - Use previous release notes as a template
    - Generate comprehensive release notes automatically
    - Open an editor for review and editing

    Fallback: If Claude Code is not available, uses a manual template.
"""

import argparse
import pathlib
import re
import subprocess
import sys
import os
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
RELEASES_DIR = ROOT / "releases"
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def run_cmd(
    cmd: str, capture_output: bool = False, check: bool = True
) -> Optional[str]:
    """Run a shell command."""
    if not capture_output:
        print(f"🔧 {cmd}")
    if capture_output:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip()
    else:
        subprocess.run(cmd, shell=True, check=check)
        return None


def check_claude_code_available() -> Optional[str]:
    """Check if Claude Code CLI is available and return the path."""
    # Check common locations for Claude Code CLI
    claude_paths = [
        "claude",  # If in PATH
        os.path.expanduser("~/.claude/local/claude"),  # User home
    ]

    for claude_path in claude_paths:
        try:
            result = subprocess.run(
                [claude_path, "--version"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return claude_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    return None


def get_previous_version() -> Optional[str]:
    """Get the previous version by looking at git tags."""
    try:
        # Get all version tags, sorted by version
        tags_output = run_cmd(
            "git tag -l | grep -E '^v[0-9]+\\.[0-9]+\\.[0-9]+$' | sort -V",
            capture_output=True,
            check=False,
        )
        if not tags_output:
            return None

        tags = tags_output.strip().split("\n")
        if len(tags) >= 1:
            # Return the latest tag without the 'v' prefix
            return tags[-1][1:]  # Remove 'v' prefix
        return None
    except Exception:
        return None


def get_git_diff_since_version(previous_version: Optional[str]) -> str:
    """Get git diff with full content since the previous version."""
    if previous_version:
        try:
            # Get commit messages and full diff since the previous tag
            print(f"🔍 Analyzing changes since v{previous_version}...")

            # First get the commit log
            commits_cmd = f"git log v{previous_version}..HEAD --oneline --no-merges"
            commits_output = run_cmd(commits_cmd, capture_output=True, check=False)

            # Then get the actual diff content (limit to avoid overwhelming output)
            diff_cmd = (
                f"git diff v{previous_version}..HEAD --no-merges --stat --summary"
            )
            diff_summary = run_cmd(diff_cmd, capture_output=True, check=False)

            # Get more detailed diff for key files (exclude large generated files)
            detailed_diff_cmd = f"git diff v{previous_version}..HEAD --no-merges -- '*.py' '*.ts' '*.tsx' '*.js' '*.md' '*.yml' '*.yaml' '*.json' '*.toml'"
            detailed_diff = run_cmd(detailed_diff_cmd, capture_output=True, check=False)

            if commits_output:
                result = f"""COMMIT MESSAGES:
{commits_output}

DIFF SUMMARY:
{diff_summary or 'No summary available'}

DETAILED CHANGES (Python, TypeScript, configs, docs):
{detailed_diff or 'No detailed changes available'}"""
                return result
            elif commits_output:
                return f"COMMIT MESSAGES:\n{commits_output}"
        except Exception as e:
            print(f"⚠️  Error getting diff since {previous_version}: {e}")

    # Fallback: get recent commits and diff
    try:
        print("🔍 Analyzing recent changes (last 20 commits)...")

        # Get recent commit messages
        commits_cmd = "git log --oneline --no-merges -20"
        commits_output = run_cmd(commits_cmd, capture_output=True, check=False)

        # Get recent diff summary
        diff_cmd = "git diff HEAD~20..HEAD --stat --summary"
        diff_summary = run_cmd(diff_cmd, capture_output=True, check=False)

        # Get detailed diff for key files
        detailed_diff_cmd = "git diff HEAD~20..HEAD -- '*.py' '*.ts' '*.tsx' '*.js' '*.md' '*.yml' '*.yaml' '*.json' '*.toml'"
        detailed_diff = run_cmd(detailed_diff_cmd, capture_output=True, check=False)

        if commits_output:
            result = f"""RECENT COMMIT MESSAGES:
{commits_output}

RECENT DIFF SUMMARY:
{diff_summary or 'No summary available'}

RECENT DETAILED CHANGES:
{detailed_diff or 'No detailed changes available'}"""
            return result
        else:
            return "No recent commits found"
    except Exception as e:
        print(f"⚠️  Error getting recent changes: {e}")
        return "Could not retrieve git history"


def get_release_template() -> str:
    """Get a template based on recent release files."""
    try:
        release_files = list(RELEASES_DIR.glob("*.md"))
        if not release_files:
            return ""

        # Get the most recent release file
        release_files.sort(key=lambda x: x.stem, reverse=True)
        latest_release = release_files[0]

        content = latest_release.read_text()
        return content
    except Exception:
        return ""


def generate_release_notes_with_claude(
    new_version: str, description: str, previous_version: Optional[str]
) -> Optional[str]:
    """Generate release notes using Claude Code."""
    print("🤖 Generating release notes with Claude Code...")

    # Check if Claude Code is available and get path
    claude_path = check_claude_code_available()
    if not claude_path:
        print("⚠️  Claude Code CLI not available")
        return None

    # Get git changes since previous version
    git_changes = get_git_diff_since_version(previous_version)

    # Get template from previous release
    template = get_release_template()

    # Create prompt for Claude
    prompt = f"""You are helping generate release notes for TrainLoop Evals version {new_version}.

User-provided description: "{description}"

COMPLETE CHANGE ANALYSIS:
<git-changes>
{git_changes}
</git-changes>

RELEASE NOTES TEMPLATE (follow this exact format and style):
<previous-release-notes>
{template}
</previous-release-notes>

INSTRUCTIONS:
Generate comprehensive release notes for version {new_version} by:

1. **FORMAT**: Follow the exact structure shown in the template:
   - Start with "Summary: [brief one-line description]"
   - Use the same markdown formatting and emoji structure
   - Include appropriate sections based on what actually changed

2. **ANALYSIS**: Based on the git commit messages, diff summary, and detailed code changes:
   - Identify NEW features and capabilities added
   - Spot BUG fixes and issues resolved  
   - Note TECHNICAL improvements and refactoring
   - Find CONFIGURATION or setup changes
   - Detect PERFORMANCE optimizations
   - Notice DOCUMENTATION updates

3. **CATEGORIZATION**: Organize changes into logical sections like:
   - 🚀 New Features (new commands, APIs, capabilities)
   - 🐛 Bug Fixes (specific issues resolved)
   - 🛠️ Technical Improvements (refactoring, optimizations)
   - 📊 [Other relevant sections based on actual changes]
   - 🔧 Configuration/Setup changes
   - 📚 Documentation updates

4. **WRITING STYLE**:
   - Be specific about what changed (not just "various improvements")
   - Use professional, clear language
   - Focus on user-facing impact
   - Mention specific files/components when relevant
   - Keep bullet points concise but informative
   - If a section is not relevant, you should not include it in the output.
   - These release notes should be as concise as possible while still being informative.

5. **OUTPUT**: Return ONLY the raw markdown content - no code fences, no explanations."""

    # print(f"Prompt: {prompt}")

    try:
        # Call Claude Code using subprocess directly for better quote handling
        result = subprocess.run(
            [claude_path, "-p", prompt], capture_output=True, text=True, check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            print(f"⚠️  Claude Code failed with return code {result.returncode}")
            if result.stderr:
                print(f"    Error: {result.stderr.strip()}")

    except Exception as e:
        print(f"⚠️  Claude Code generation failed: {e}")

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
    new_version: str,
    description: str,
    existing_file: Optional[str] = None,
    skip_claude: bool = False,
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

    # Ensure releases directory exists
    RELEASES_DIR.mkdir(exist_ok=True)

    # Try to generate with Claude Code first (unless disabled)
    claude_content = None

    if not skip_claude:
        claude_path = check_claude_code_available()

        if claude_path:
            previous_version = get_previous_version()
            if previous_version:
                print(f"📚 Found previous version: {previous_version}")

            claude_content = generate_release_notes_with_claude(
                new_version, description, previous_version
            )
        else:
            print("⚠️  Claude Code not available, using manual template")
    else:
        print("🚫 Claude Code generation disabled, using manual template")

    if claude_content:
        # Write Claude-generated content
        release_file.write_text(claude_content)
        print(f"✅ Generated release notes with Claude Code: {release_file}")
        print("📝 Opening editor for review and editing...")
    else:
        # Fallback to manual template
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

        # Write manual template
        release_file.write_text(content)
        print(f"✅ Created release notes template: {release_file}")
        print("📝 Opening editor to complete release notes...")

    # Open in editor for review/editing
    editor = (
        os.environ.get("EDITOR")
        or run_cmd("echo $EDITOR", capture_output=True)
        or "nano"
    )
    try:
        print(f"   Using editor: {editor}")
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
        nargs="?",  # Make optional
        choices=["major", "minor", "patch"],
        help="Type of version bump to perform",
    )

    parser.add_argument(
        "description",
        nargs="?",  # Make optional
        help="Brief description of the release (used in release notes)",
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

    parser.add_argument(
        "--no-claude",
        action="store_true",
        help="Skip Claude Code generation and use manual template",
    )

    parser.add_argument(
        "--test-notes",
        action="store_true",
        help="Test release notes generation only (no git operations)",
    )

    # Check if we're being called via npm and provide helpful guidance
    if len(sys.argv) == 1 and os.environ.get("npm_execpath"):
        print("🚀 TrainLoop Release Script")
        print("=" * 40)
        print("📝 USAGE VIA NPM:")
        print('   npm run release -- <bump_type> "<description>" [options]')
        print("")
        print("📋 EXAMPLES:")
        print('   npm run release -- patch "Bug fixes and improvements"')
        print('   npm run release -- minor "New features added" --test-notes')
        print('   npm run release -- major "Breaking changes" --dry-run')
        print("")
        print("⚠️  Note: The '--' is required to pass arguments through npm")
        print(
            '💡 Alternatively, run directly: python scripts/release.py patch "description"'
        )
        sys.exit(0)

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    if args.test_notes:
        print("🧪 TEST NOTES MODE - Only generating release notes (no git operations)")

    print("🚀 TrainLoop Release Script")
    print("=" * 40)

    # Prompt for missing arguments if not provided
    bump_type = args.bump_type
    description = args.description

    if not bump_type:
        print("\n📈 RELEASE TYPE:")
        print("  major: Breaking changes (1.0.0 → 2.0.0)")
        print("  minor: New features (1.0.0 → 1.1.0)")
        print("  patch: Bug fixes (1.0.0 → 1.0.1)")

        while not bump_type:
            bump_type = (
                input("\n🤔 Select release type [major/minor/patch]: ").strip().lower()
            )
            if bump_type not in ["major", "minor", "patch"]:
                print("❌ Invalid choice. Please enter: major, minor, or patch")
                bump_type = None

    if not description:
        description = input("\n📝 Brief description of this release: ").strip()
        while not description:
            print("❌ Description is required")
            description = input("📝 Brief description of this release: ").strip()

    # Get current and new versions
    current_version = get_current_version()
    new_version = calculate_new_version(current_version, bump_type)

    print(f"📊 Current version: {current_version}")
    print(f"📈 New version: {new_version}")
    print(f"📝 Description: {description}")

    if args.dry_run:
        print("\n✅ DRY RUN COMPLETE - No changes made")
        return

    # Handle test notes mode
    if args.test_notes:
        print("\n🧪 TESTING CLAUDE CODE RELEASE NOTES GENERATION")
        print("=" * 50)

        if args.no_claude:
            print("❌ Cannot test Claude generation with --no-claude flag")
            return

        claude_path = check_claude_code_available()
        if not claude_path:
            print("❌ Claude Code CLI not available. Install it first:")
            print("   Visit: https://claude.ai/code")
            return

        # Get previous version for context
        previous_version = get_previous_version()
        if previous_version:
            print(f"📚 Previous version found: {previous_version}")
        else:
            print("⚠️  No previous version found - will use recent commits")

        # Generate test release notes
        claude_content = generate_release_notes_with_claude(
            new_version, description, previous_version
        )

        if claude_content:
            print(f"\n📝 GENERATED RELEASE NOTES for v{new_version}:")
            print("=" * 50)
            print(claude_content)
            print("=" * 50)

            # Automatically save to test file in test mode
            test_file = RELEASES_DIR / f"test-{new_version}.md"
            RELEASES_DIR.mkdir(exist_ok=True)
            test_file.write_text(claude_content)
            print(f"✅ Test release notes saved to: {test_file}")
        else:
            print("❌ Failed to generate release notes with Claude Code")

        print("\n✅ TEST NOTES COMPLETE")
        return

    # Confirm with user (only for actual releases, not test mode)
    confirm = input(f"\n🤔 Proceed with release v{new_version}? [y/N]: ")
    if confirm.lower() != "y":
        print("❌ Release cancelled")
        return

    try:
        # Execute release workflow
        check_git_status()
        ensure_main_branch()
        create_release_notes(
            new_version, description, args.release_notes, args.no_claude
        )
        branch_name = create_release_branch(new_version)
        run_version_bump(bump_type)

        pr_created = False
        if not args.skip_pr:
            create_pull_request(new_version, description, branch_name)
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
