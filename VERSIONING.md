# TrainLoop Evals - Versioning

TrainLoop Evals follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH) with a simple workflow for versioning, building, and publishing packages.

## Quick Reference

```bash
# Bump version (updates VERSION file, package.json files, and changelog)
npm run bump patch "Bug fix description"
npm run bump minor "New feature description"
npm run bump major "Breaking change description"

# Build packages
npm run build             # Build all components
npm run build:docker      # Build only Docker image
npm run build:studio      # Build only Studio package

# Publish packages
npm run publish           # Publish all components
npm run publish:sdk       # Publish only SDK packages
npm run publish:cli       # Publish only CLI package
npm run publish:studio    # Publish only Studio package

# Pulumi (infrastructure)
npm run pulumi:bump       # Update Pulumi config with new version
```

## How Versioning Works

The system uses a central `VERSION` file as the source of truth. When you run the bump command, it:

1. Updates the version in the `VERSION` file
2. Updates all package.json files and pyproject.toml files
3. Updates the CHANGELOG.md with your provided message
4. Commits changes, creates a git tag, and pushes to the main branch

## Workflow Examples

### Typical Release Process

```bash
# 1. Bump version with changelog entry
npm run bump minor "Added new evaluation metrics"

# 2. Build all components
npm run build

# 3. Publish packages
npm run publish

# 4. Update infrastructure (if needed)
npm run pulumi:bump
cd infra && pulumi up
```

### Partial Updates

If you only need to update specific components:

```bash
# Only publish the SDK
npm run publish:sdk

# Only build Docker image
npm run build:docker
```

## Technical Details

- The `VERSION` file contains the current semantic version
- Python scripts in the `scripts/` directory handle the version management
- All components (UI, SDK, CLI, etc.) are versioned together
- The system automatically updates package-lock.json files where needed
- Docker images are tagged with the version number

For detailed information on the implementation, see the scripts in the `scripts/` directory.
