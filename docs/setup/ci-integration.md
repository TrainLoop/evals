---
sidebar_position: 2
---

# CI Integration

Run evaluations automatically in your CI pipeline.

## Tutorial

1. Install dependencies in your CI job:
   ```yaml
   - run: ./scripts/setup.py
   ```
2. Execute the eval command:
   ```yaml
   - run: trainloop eval
   ```
3. Upload results as artifacts if needed.

## How-tos

- [GitHub Actions example](../docs/reference/integration/github-actions.md)
- [GitLab CI example](../docs/reference/integration/gitlab-ci.md)
- [Jenkins example](../docs/reference/integration/jenkins.md)

## Pitfalls

- Set `TRAINLOOP_DATA_FOLDER` so data persists between steps.
- Flush events after tests to capture final timing.
- Label builds with commit SHAs for easy tracking.
- Use the same config file locally and in CI to avoid cascade surprises.
