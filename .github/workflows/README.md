# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the TrainLoop Evals project.

## SDK Test Workflows

### sdk-tests-lean.yml (Primary - Runs Automatically)
The main test suite that runs on every PR, PR sync, and push to main:
- **Python SDK**: Tests on Python 3.11 on Ubuntu
- **TypeScript SDK**: Tests on Node.js 20.x on Ubuntu
- Includes linting checks for both SDKs
- Optimized for fast feedback (~2-3 minutes)

### sdk-tests.yml (Full Matrix - Manual/Scheduled)
Comprehensive test suite for cross-platform compatibility:
- **Python SDK**: Tests on Python 3.8-3.12 across Ubuntu, macOS, and Windows
- **TypeScript SDK**: Tests on Node.js 18.x, 20.x, and 22.x across Ubuntu, macOS, and Windows
- **Triggers**:
  - Manual dispatch via GitHub Actions UI
  - Daily schedule (midnight UTC)
  - Pushes to release branches and main

## When Tests Run

- **Every PR**: `sdk-tests-lean.yml` runs automatically
- **Daily**: `sdk-tests.yml` runs the full matrix to catch compatibility issues
- **On Demand**: Run `sdk-tests.yml` manually from the Actions tab
- **Release Branches**: Both workflows run to ensure quality

## Workflow Features

Both workflows include:
- Automatic triggering on PRs and pushes to main
- Path filtering (only runs when SDK files change)
- Dependency caching for faster runs
- Coverage reporting (currently generates reports but doesn't upload them)
- Parallel execution of Python and TypeScript tests

## Running Tests Locally

Before pushing, you can run tests locally:

```bash
# Python SDK
cd sdk/python
poetry run pytest

# TypeScript SDK  
cd sdk/typescript
npm test
```

## Customization

To adjust the test matrix or add new checks:
1. Edit the `matrix` section in the workflow files
2. Add new steps under the respective job
3. Update path filters if testing new directories

## Troubleshooting

- **Tests failing on Windows**: Check for path separator issues
- **Cache misses**: Ensure lock files are committed
- **Slow runs**: Consider using the lean workflow for routine changes
