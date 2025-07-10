# Pull Request Process

This guide covers the complete pull request workflow for contributing to TrainLoop Evals, from preparation to merge.

## Overview

TrainLoop Evals follows a structured pull request process to ensure code quality, maintainability, and consistency across the project. All changes must go through this process before being merged.

## Before You Start

### Prerequisites

- [ ] You have a GitHub account and have forked the repository
- [ ] You have set up your local development environment ([Local Development](./local-development.md))
- [ ] You have read the [Contributing Guide](./contributing.md)
- [ ] You understand the [Code Style](./code-style.md) guidelines

### Choose Your Contribution Type

- **Bug Fix** - Fixes a specific issue or bug
- **Feature Addition** - Adds new functionality
- **Enhancement** - Improves existing functionality
- **Documentation** - Updates or improves documentation
- **Refactoring** - Improves code structure without changing functionality
- **Performance** - Optimizes code for better performance

## Step 1: Planning

### For Bug Fixes

1. **Check existing issues** to see if the bug is already reported
2. **Reproduce the bug** locally and document steps
3. **Identify the root cause** before implementing a fix
4. **Consider edge cases** that might be affected

### For New Features

1. **Open a feature request** issue first to discuss the approach
2. **Wait for maintainer approval** before starting implementation
3. **Break down large features** into smaller, manageable chunks
4. **Consider backwards compatibility** and migration paths

### For Documentation

1. **Check for existing documentation** on the same topic
2. **Follow the documentation style guide** (Google Developer Style Guide principles)
3. **Include practical examples** where relevant
4. **Update related documentation** as needed

## Step 2: Preparation

### Create a Feature Branch

```bash
# Sync with upstream
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/descriptive-name

# Or for bug fixes
git checkout -b fix/issue-description

# Or for documentation
git checkout -b docs/topic-name
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `perf/` - Performance improvements
- `test/` - Test additions or improvements

Examples:
- `feature/add-custom-metrics-support`
- `fix/cli-config-loading-error`
- `docs/update-sdk-installation-guide`
- `refactor/simplify-event-processing`

## Step 3: Development

### Code Quality Checklist

- [ ] **Follow code style guidelines** ([Code Style](./code-style.md))
- [ ] **Write comprehensive tests** for new functionality
- [ ] **Update existing tests** if behavior changes
- [ ] **Add documentation** for user-facing changes
- [ ] **Consider backwards compatibility**
- [ ] **Optimize for performance** where relevant

### Testing Requirements

```bash
# Run relevant tests during development
task test:unit      # Fast unit tests
task test:cli       # CLI-specific tests
task test:sdk       # SDK-specific tests

# Run full test suite before submitting
task test
```

### Documentation Updates

For user-facing changes:

- [ ] Update relevant documentation in `docs/docs/`
- [ ] Add code examples to demonstrate usage
- [ ] Update API documentation if applicable
- [ ] Add changelog entry if significant change

## Step 4: Commit Your Changes

### Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

#### Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (no functional changes)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `perf` - Performance improvements
- `ci` - CI/CD changes
- `build` - Build system changes
- `chore` - Maintenance tasks

#### Scopes
- `cli` - CLI-related changes
- `sdk` - SDK-related changes
- `ui` - Studio UI changes
- `registry` - Registry system changes
- `docs` - Documentation changes
- `tests` - Test-related changes

#### Examples

```bash
# Good commit messages
git commit -m "feat(cli): add benchmark command for model comparison"
git commit -m "fix(sdk): resolve memory leak in event buffering"
git commit -m "docs(guides): add comprehensive testing guide"
git commit -m "refactor(ui): simplify dashboard data loading logic"

# Include breaking changes
git commit -m "feat(cli): redesign config file format

BREAKING CHANGE: Config file format has changed from YAML to TOML.
Migration guide available in docs/migration/v2.md"
```

### Commit Best Practices

- **Make atomic commits** - Each commit should represent a single logical change
- **Write descriptive messages** - Explain what and why, not just what
- **Keep commits focused** - Don't mix unrelated changes
- **Test each commit** - Each commit should pass tests independently

## Step 5: Pre-submission Checks

### Automated Checks

```bash
# Format code
cd cli && poetry run black .
cd sdk/python && poetry run black .
cd sdk/typescript && npm run format

# Lint code
cd cli && poetry run flake8 .
cd ui && npm run lint

# Run tests
task test

# Check for common issues
task check:mocks
```

### Manual Review

- [ ] **Review your changes** - Use `git diff` to check all modifications
- [ ] **Test manually** - Verify functionality works as expected
- [ ] **Check documentation** - Ensure all docs are accurate and complete
- [ ] **Verify backwards compatibility** - Test with existing configurations
- [ ] **Review for security issues** - Check for potential vulnerabilities

## Step 6: Submit Pull Request

### Push Your Branch

```bash
# Push to your fork
git push origin feature/your-feature-name

# Or set upstream for future pushes
git push -u origin feature/your-feature-name
```

### Create Pull Request

1. **Navigate to GitHub** and click "New Pull Request"
2. **Select your branch** as the source
3. **Choose the target branch** (usually `main`)
4. **Fill out the PR template** completely

### Pull Request Template

```markdown
## Description

Brief description of the changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Documentation

- [ ] Documentation updated
- [ ] API documentation updated (if applicable)
- [ ] Examples added/updated
- [ ] Migration guide provided (if breaking change)

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues

Closes #123
Related to #456

## Screenshots (if applicable)

[Add screenshots for UI changes]

## Additional Notes

[Any additional information or context]
```

### Title and Description Guidelines

#### Title Format
- Use clear, descriptive titles
- Start with conventional commit type
- Keep under 72 characters
- Use imperative mood

Examples:
- `feat(cli): add benchmark command for model comparison`
- `fix(sdk): resolve Python 3.9 compatibility issue`
- `docs: add comprehensive contributing guide`

#### Description Content
- **What**: Describe what changes were made
- **Why**: Explain the motivation behind the changes
- **How**: Briefly describe the approach taken
- **Impact**: Note any breaking changes or performance implications

## Step 7: Review Process

### What to Expect

1. **Automated checks** will run (CI/CD pipeline)
2. **Maintainer review** will be assigned
3. **Feedback and discussion** may occur
4. **Changes may be requested**
5. **Final approval** and merge

### Addressing Feedback

#### Common Review Comments

- **Code style issues** - Fix formatting and linting issues
- **Test coverage** - Add missing tests or improve existing ones
- **Documentation** - Update or add missing documentation
- **Performance concerns** - Optimize critical paths
- **Breaking changes** - Provide migration path or reconsider approach

#### Responding to Feedback

```bash
# Make requested changes
# ... edit files ...

# Commit changes
git add .
git commit -m "address review feedback: add missing tests"

# Push updates
git push origin feature/your-feature-name
```

#### Review Etiquette

- **Be responsive** - Address feedback promptly
- **Be open to suggestions** - Maintainers know the codebase well
- **Ask questions** - If feedback is unclear, ask for clarification
- **Stay professional** - Keep discussions focused on the code

### Continuous Integration

All PRs must pass:

- **Unit tests** - All existing and new tests must pass
- **Integration tests** - End-to-end functionality must work
- **Code quality checks** - Linting and formatting must pass
- **Security scans** - No security vulnerabilities introduced
- **Performance regression** - No significant performance degradation

## Step 8: After Merge

### Cleanup

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name

# Delete remote branch
git push origin --delete feature/your-feature-name
```

### Follow-up Tasks

- [ ] **Monitor for issues** - Watch for any problems after merge
- [ ] **Update documentation** - If follow-up docs are needed
- [ ] **Close related issues** - Link and close any related GitHub issues
- [ ] **Share the change** - Announce significant features to the community

## Special Considerations

### Breaking Changes

For changes that break backwards compatibility:

1. **Discuss with maintainers** before implementing
2. **Provide migration guide** in the PR description
3. **Update version appropriately** (major version bump)
4. **Deprecate old functionality** before removing (if possible)
5. **Document breaking changes** in changelog

### Large Features

For significant features:

1. **Break into smaller PRs** when possible
2. **Create feature branch** for coordination
3. **Use draft PRs** for work-in-progress
4. **Coordinate with maintainers** for timing
5. **Consider feature flags** for gradual rollout

### Security Fixes

For security-related changes:

1. **Report security issues privately** first
2. **Coordinate with maintainers** on disclosure
3. **Follow security disclosure process**
4. **Test security fixes thoroughly**
5. **Update security documentation** if needed

## Troubleshooting

### Common Issues

#### PR Cannot Be Merged

```bash
# Sync with upstream
git checkout main
git pull upstream main

# Rebase feature branch
git checkout feature/your-feature-name
git rebase main

# Force push (if needed)
git push --force-with-lease origin feature/your-feature-name
```

#### Tests Failing

```bash
# Run tests locally
task test

# Check specific failures
pytest tests/failing_test.py -v

# Fix issues and commit
git add .
git commit -m "fix failing tests"
git push origin feature/your-feature-name
```

#### Merge Conflicts

```bash
# Rebase to resolve conflicts
git checkout feature/your-feature-name
git rebase main

# Resolve conflicts manually
# Edit conflicted files
git add resolved_file.py
git rebase --continue

# Push resolved changes
git push --force-with-lease origin feature/your-feature-name
```

## Resources

- **[Contributing Guide](./contributing.md)** - General contribution guidelines
- **[Code Style](./code-style.md)** - Coding standards and conventions
- **[Testing Guide](./testing.md)** - Testing requirements and practices
- **[Local Development](./local-development.md)** - Development environment setup
- **[Architecture Guide](./architecture.md)** - System architecture overview

## Getting Help

### For Contributors

- **Questions about the process**: Open a [GitHub Discussion](https://github.com/trainloop/evals/discussions)
- **Technical questions**: Comment on your PR or open an issue
- **Urgent issues**: Tag maintainers in your PR

### For Maintainers

- **Review guidelines**: [Maintainer Guide](./maintainer-guide.md)
- **Release process**: [Release Process](./release-process.md)
- **Governance**: [Governance](./governance.md)

---

Thank you for contributing to TrainLoop Evals! Following this process helps ensure high-quality, maintainable code that benefits the entire community.