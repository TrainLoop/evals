# Local Development

This guide walks you through setting up a complete development environment for TrainLoop Evals on your local machine.

## Prerequisites

### Required Software

- **Python 3.9+** with Poetry package manager
- **Node.js 20.0+** with npm
- **Go 1.21+** (for Go SDK development)
- **Git** for version control

### Optional Tools

- **Docker** for containerized development
- **go-task** for task automation
- **pipx** for Python tool installation

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/trainloop/evals.git
cd evals
```

### 2. Install Python Dependencies

#### Install Poetry (if not already installed)

```bash
# Using pipx (recommended)
pipx install poetry

# Or using pip
pip install poetry
```

#### Install CLI Dependencies

```bash
cd cli
poetry install
cd ..
```

#### Install Python SDK Dependencies

```bash
cd sdk/python
poetry install
cd ../..
```

### 3. Install Node.js Dependencies

#### Install UI Dependencies

```bash
cd ui
npm install
cd ..
```

#### Install TypeScript SDK Dependencies

```bash
cd sdk/typescript
npm install
cd ../..
```

### 4. Install Go Dependencies (Optional)

If you plan to work on the Go SDK:

```bash
cd sdk/go/trainloop-llm-logging
go mod tidy
cd ../../..
```

### 5. Install Documentation Dependencies

```bash
cd docs
npm install
cd ..
```

## Development Environment Configuration

### Environment Variables

Create a `.env` file in your project root for development:

```bash
# .env
TRAINLOOP_DATA_FOLDER=./trainloop/data
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Optional: Install go-task

For easier task management, install go-task:

```bash
# Using go
go install github.com/go-task/task/v3/cmd/task@latest

# Or using homebrew (macOS/Linux)
brew install go-task/tap/go-task

# Or download from releases
curl -sL https://taskfile.dev/install.sh | sh
```

## Development Workflows

### CLI Development

#### Running the CLI locally

```bash
cd cli
poetry run trainloop --help
```

#### Installing CLI in development mode

```bash
cd cli
poetry install
```

Now you can use `trainloop` commands directly from anywhere in your terminal.

#### CLI Development Commands

```bash
# Run CLI tests
cd cli
poetry run pytest

# Run with specific markers
poetry run pytest -m unit
poetry run pytest -m integration

# Format code
poetry run black .
poetry run flake8 .

# Run specific CLI command
poetry run trainloop init
poetry run trainloop eval --help
```

### SDK Development

#### Python SDK

```bash
cd sdk/python

# Run SDK tests
poetry run pytest

# Run integration tests (requires API keys)
poetry run pytest tests/integration/

# Run specific test categories
poetry run pytest -m unit
poetry run pytest -m integration

# Format code
poetry run black .
poetry run flake8 .
```

#### TypeScript SDK

```bash
cd sdk/typescript

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build the SDK
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

#### Go SDK

```bash
cd sdk/go/trainloop-llm-logging

# Run tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Build the module
go build ./...

# Format code
go fmt ./...
```

### UI Development

#### Start development server

```bash
cd ui
npm run dev
```

The development server will start at `http://localhost:3000`.

#### UI Development Commands

```bash
cd ui

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npm run type-check
```

### Documentation Development

#### Start documentation server

```bash
cd docs
npm start
```

The documentation will be available at `http://localhost:3000`.

#### Documentation Commands

```bash
cd docs

# Build documentation
npm run build

# Serve built documentation
npm run serve

# Deploy documentation (maintainers only)
npm run deploy
```

## Task Automation

If you have go-task installed, you can use predefined tasks:

### Running Tests

```bash
# Run all tests
task test

# Run simplified tests (recommended for limited disk space)
task test:simple

# Run component-specific tests
task test:cli
task test:sdk
task test:ui

# Run specific test types
task test:unit
task test:integration
task test:fsspec
```

### Development Tasks

```bash
# Show all available tasks
task --list

# Clean up test artifacts
task clean:all

# Check for issues
task check:mocks
```

## IDE Configuration

### VS Code

Recommended extensions:

- **Python** by Microsoft
- **Go** by Google
- **TypeScript Importer** by pmneo
- **Prettier** by Prettier
- **ESLint** by Microsoft
- **Tailwind CSS IntelliSense** by Tailwind Labs

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./cli/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Open the project root directory
2. Configure Python interpreter:
   - Go to **File → Settings → Project → Python Interpreter**
   - Choose **Poetry Environment**
   - Select `./cli/pyproject.toml`

## Common Development Tasks

### Setting up a new TrainLoop project

```bash
# Create a new project
poetry run trainloop init

# Or use the installed CLI
trainloop init
```

### Testing SDK integration

```bash
# Python SDK
cd sdk/python
poetry run python -c "
from trainloop_llm_logging import collect
collect('./test_config.yaml')
print('Python SDK initialized')
"

# TypeScript SDK
cd sdk/typescript
npm run test:integration
```

### Running the full development stack

```bash
# Terminal 1: Start UI development server
cd ui && npm run dev

# Terminal 2: Start documentation server
cd docs && npm start

# Terminal 3: Run CLI commands
cd cli && poetry run trainloop studio
```

## Troubleshooting

### Common Issues

#### Poetry installation fails

```bash
# Clear poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

#### Node.js version conflicts

```bash
# Use nvm to manage Node.js versions
nvm install 20
nvm use 20
```

#### Python import errors

```bash
# Ensure you're in the correct poetry environment
cd cli && poetry shell

# Or run commands with poetry
poetry run python your_script.py
```

#### Go module issues

```bash
# Clean module cache
go clean -modcache

# Download dependencies
go mod download
```

### Test Failures

#### MagicMock directory issues

```bash
# Clean up MagicMock directories
task clean:mocks
```

#### Integration test failures

1. Ensure API keys are set in your environment
2. Check network connectivity
3. Run tests individually to isolate issues

```bash
# Run individual integration tests
poetry run pytest tests/integration/test_openai_sdk.py -v
```

### Performance Issues

#### Slow test execution

```bash
# Run simplified test suite
task test:simple

# Run only unit tests
task test:unit
```

#### UI development server slow

```bash
# Clear Next.js cache
cd ui && rm -rf .next

# Restart development server
npm run dev
```

## Development Best Practices

### Code Organization

- Keep components focused and single-purpose
- Use proper type hints in Python code
- Follow established patterns in each language
- Write comprehensive tests for new features

### Testing Strategy

- Write unit tests for individual functions
- Create integration tests for component interactions
- Add end-to-end tests for user workflows
- Use appropriate test markers for categorization

### Documentation

- Update documentation alongside code changes
- Include code examples in documentation
- Write clear commit messages
- Add inline comments for complex logic

## Contributing Your Changes

Once you've made your changes:

1. **Run the test suite**
   ```bash
   task test
   ```

2. **Format your code**
   ```bash
   # Python
   poetry run black .
   
   # TypeScript
   npm run format
   
   # Go
   go fmt ./...
   ```

3. **Create a pull request**
   See our [Pull Request Process](./pull-request-process.md) for detailed guidelines.

## Getting Help

- **Development questions**: Open a [GitHub Discussion](https://github.com/trainloop/evals/discussions)
- **Bug reports**: Use the [bug report template](https://github.com/trainloop/evals/issues/new?template=bug_report.md)
- **Feature requests**: Use the [feature request template](https://github.com/trainloop/evals/issues/new?template=feature_request.md)

## Next Steps

- Review the [Architecture Guide](./architecture.md) to understand the system design
- Check the [Testing Guide](./testing.md) for comprehensive testing practices
- Read the [Code Style](./code-style.md) guide for coding standards
- Follow the [Contributing Guide](./contributing.md) for contribution workflows