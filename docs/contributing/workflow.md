# Contributor Workflow

This guide summarizes how to work on TrainLoop Evals. It complements the
in‑depth guides in `docs/docs/development`.

## Local Development Setup

1. Clone the repository and install dependencies with `./scripts/setup.py`.
2. Use Python 3.9+, Node.js 20 and Go 1.21+ if you are working on the Go SDK.
3. Create a `.env` file with API keys and `TRAINLOOP_DATA_FOLDER`.
4. For IDE setup and optional tooling see the `development/local-development.md`
document.

## Testing and Linting

- Run `task test` to execute the full suite. Use `task test:simple` for a
  lighter run.
- Lint TypeScript and React code from `ui/` with `npm run lint`.
- Format Python code with `black` and check style with `flake8`.

## Release Workflow

1. Add release notes under `releases/` starting with `Summary:`.
2. Run `npm run release <major|minor|patch> "message"` to bump versions and build
   packages.
3. GitHub Actions publishes the release when merged into `main`.
4. Use `npm run pulumi:bump` after the version bump if infrastructure values need
   to be updated.

See `development/release-process.md` for details.

## Merge Conflict Hygiene

Always rebase onto the latest `main` before submitting a pull request:

```bash
git fetch origin
git rebase origin/main
```

Resolve conflicts locally, run tests again and force‑push with
`--force-with-lease`.
