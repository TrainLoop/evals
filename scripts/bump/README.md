# Bump Version Script

This script handles version bumping, changelog updates, git commits, tagging, and pushing.

## Usage

### Step 1: Create Release Notes
Before bumping the version, create a release notes file in the `releases/` directory.
The file **must** start with a `Summary:` line that briefly describes the release.

```bash
# For example, if bumping to 0.5.0, create releases/0.5.0.md
cat > releases/0.5.0.md << EOF
Summary: Major SDK refactoring with comprehensive testing infrastructure

**Major SDK Refactoring and Testing Infrastructure**

The changes in this release include:

### 📁 SDK Restructuring
- Renamed SDK from "evals-sdk" to "sdk"
- Renamed packages from "trainloop_evals" to "trainloop_llm_logging"
- Improved config functions to handle environment variable fallbacks

### 🧪 Testing Infrastructure  
- Added comprehensive test suites with over 3000 lines of tests
- Implemented pytest configuration for Python SDK
- Implemented Jest configuration for TypeScript SDK

### 🐛 Bug Fixes
- Fixed UI database initialization to handle empty directories gracefully
- Fixed concurrency issues in DuckDB
EOF
```

### Step 2: Run the Bump Script

**Automated (recommended):**
```bash
# Use the automated release script instead:
npm run release minor
```

**Manual bump (advanced users):**
```bash
npm run bump minor
```

## How It Works

1. Updates all package.json and pyproject.toml files with new version
2. Regenerates npm lock files
3. Adds entry to CHANGELOG.md linking to release notes
4. Commits changes and pushes to current branch (no tag creation)
5. When merged to main, GitHub Actions handles tagging and publishing

## Release File Format

The release file **must** start with a Summary line:
```markdown
Summary: Brief description of the release

[Rest of your detailed release notes in markdown format]
```

## Example Changelog Output

The changelog will contain links to the full release notes:

```markdown
# Changelog

## 0.5.0 (2025-05-27)
[Release Notes](releases/0.5.0.md)

## 0.4.0 (2025-05-22)
• Public Release
```

## Important Notes

- The release file **must** exist before running the bump script
- The release file **must** start with `Summary: <message>`
- The summary is used for the git commit message and tag
- Release files are committed as part of the version bump
- Release files should be markdown formatted for best readability
