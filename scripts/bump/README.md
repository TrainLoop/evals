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
```bash
# Bump patch version
npm run bump patch
# or
python scripts/bump/bump_version.py patch

# Bump minor version
npm run bump minor

# Bump major version
npm run bump major
```

## How It Works

1. **Pre-check**: The script calculates the new version and checks if `releases/<new_version>.md` exists
2. **Summary Extraction**: Reads the `Summary:` line from the release file for the commit message
3. **Version Update**: Updates all package.json and pyproject.toml files
4. **Lock Files**: Regenerates npm lock files
5. **Changelog**: Adds an entry to CHANGELOG.md that links to the release notes file
6. **Git Operations**: Commits all changes including the release file, tags, and pushes

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
