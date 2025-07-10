---
sidebar_position: 8
---

# Release Process

This document describes the TrainLoop Evals release process, including version bumping, changelog management, and publication workflows.

## Overview

TrainLoop Evals uses a semi-automated release process that combines manual release note creation with automated version bumping, building, and publishing.

## Release Workflow

### Step 1: Create Release Notes

Before bumping the version, create a release notes file in the `releases/` directory. The file **must** start with a `Summary:` line that briefly describes the release.

```bash
# For example, if releasing version 0.5.0, create releases/0.5.0.md
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

### Step 2: Run the Release Script

**Automated (recommended):**
```bash
# Use the automated release script:
npm run release minor "Brief description of the release"
```

**Manual bump (advanced users):**
```bash
npm run bump minor
```

### Step 3: GitHub Actions Handles Publishing

When merged to the main branch, GitHub Actions automatically:
1. Creates a git tag
2. Builds all packages (CLI, SDKs, Studio)
3. Publishes to package repositories (PyPI, NPM)
4. Updates deployment infrastructure

## Version Bump Script

The version bump script performs the following operations:

1. **Updates all package files** with the new version:
   - `package.json` files (root and components)
   - `pyproject.toml` files (Python packages)
   - Lock files (`package-lock.json`, `poetry.lock`)

2. **Updates CHANGELOG.md** with a link to the release notes

3. **Creates a git commit** with the version changes

4. **Pushes to the current branch** (no tag creation - handled by GitHub Actions)

## Release File Format

Release files must follow this format:

```markdown
Summary: Brief description of the release

[Rest of your detailed release notes in markdown format]

### 🚀 New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 📚 Documentation
- Documentation improvements

### 🔧 Internal
- Internal changes
```

**Important Requirements:**
- The file **must** start with `Summary: <message>`
- The summary is used for git commit messages and tags
- Release files should be markdown formatted for readability
- Use emojis and clear categorization for better readability

## Changelog Output

The changelog will contain links to the full release notes:

```markdown
# Changelog

## 0.5.0 (2025-05-27)
[Release Notes](releases/0.5.0.md)

## 0.4.0 (2025-05-22)
• Public Release
```

## Build and Publishing

### Automated Publishing (Production)

GitHub Actions handles all publishing when code is merged to main:

```yaml
# .github/workflows/release.yml
- name: Build all packages
  run: npm run build

- name: Publish CLI to PyPI
  run: npm run publish:cli

- name: Publish SDKs to PyPI and NPM
  run: npm run publish:sdk

- name: Publish Studio to NPM
  run: npm run publish:studio
```

### Manual Publishing (Development)

For testing releases:

```bash
# Build all components
npm run build

# Publish individual components
npm run publish:cli        # CLI to PyPI
npm run publish:sdk        # SDKs to PyPI and NPM
npm run publish:studio     # Studio to NPM

# Or publish everything
npm run publish
```

## Version Management

### Semantic Versioning

TrainLoop Evals follows [semantic versioning](https://semver.org/):

- **MAJOR** version: Breaking changes
- **MINOR** version: New features, backwards compatible
- **PATCH** version: Bug fixes, backwards compatible

### Monorepo Version Synchronization

All packages in the monorepo share the same version number:
- CLI (`trainloop-cli`)
- Python SDK (`trainloop-llm-logging`)
- TypeScript SDK (`trainloop-llm-logging`)
- Go SDK (`trainloop-llm-logging`)
- Studio UI (`trainloop-studio`)

This ensures compatibility across all components.

## Testing Releases

### Pre-release Testing

Before creating a release:

```bash
# Run all tests
npm test

# Build all packages
npm run build

# Test CLI locally
cd cli && poetry run trainloop --help

# Test Studio locally
cd ui && npm run dev
```

### Post-release Verification

After publishing:

```bash
# Test CLI installation
pipx install trainloop-cli
trainloop --version

# Test SDK installation
pip install trainloop-llm-logging
npm install trainloop-llm-logging
```

## Rollback Process

If a release needs to be rolled back:

1. **Identify the issue** and create a hotfix
2. **Create a patch release** with the fix
3. **Update package repositories** to mark the problematic version as deprecated
4. **Communicate** the issue and resolution to users

## Infrastructure Updates

Release deployments may also update infrastructure:

```bash
# Update Pulumi infrastructure after release
npm run pulumi:bump
```

This ensures that any infrastructure changes required for the new version are deployed.

## Release Checklist

- [ ] Create release notes file in `releases/`
- [ ] Release notes start with `Summary:` line
- [ ] Run `npm run release [major|minor|patch]`
- [ ] Verify all tests pass
- [ ] Create pull request
- [ ] Merge to main branch
- [ ] Verify GitHub Actions deployment succeeds
- [ ] Test published packages
- [ ] Announce release in appropriate channels

## Common Issues

### Build Failures

If the build fails during release:
1. Fix the issue in a separate commit
2. Re-run the release process
3. Ensure all package.json files are updated consistently

### Publishing Failures

If publishing fails:
1. Check API tokens for PyPI and NPM
2. Verify package names and versions
3. Check for network connectivity issues
4. Retry publishing individual components

### Version Conflicts

If version conflicts occur:
1. Ensure all package files have consistent versions
2. Run `npm run bump` again to fix inconsistencies
3. Check for uncommitted changes that might interfere

## Support

For questions about the release process:
- Check the [development documentation](./local-development.md)
- Open an issue on GitHub
- Contact the maintainers via GitHub discussions