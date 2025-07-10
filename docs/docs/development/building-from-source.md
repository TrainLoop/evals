# Building from Source

This guide covers building TrainLoop Evals from source code, including all components and their dependencies.

## Overview

TrainLoop Evals consists of multiple components that can be built independently or together:

- **CLI Tool** - Python package with Poetry
- **Python SDK** - Python package with Poetry
- **TypeScript SDK** - Node.js package with npm
- **Go SDK** - Go module
- **Studio UI** - Next.js application
- **Documentation** - Docusaurus site

## Build System

The project uses a combination of build tools:

- **Poetry** for Python package management and building
- **npm** for Node.js package management and building
- **Go** modules for Go dependency management
- **Python scripts** for orchestrating multi-component builds

## Prerequisites

### System Requirements

- **Python 3.9+** with Poetry
- **Node.js 20.0+** with npm
- **Go 1.21+** (for Go SDK)
- **Git** for version control

### Build Tools

```bash
# Install Poetry
pipx install poetry

# Install pipx if not available
python -m pip install --user pipx
pipx ensurepath

# Verify installations
poetry --version
node --version
npm --version
go version
```

## Quick Build

### Build All Components

```bash
# Using npm scripts (recommended)
npm run build

# Using Python script directly
pipx run scripts/build.py
```

### Build Specific Components

```bash
# Build CLI and SDKs only (skip Studio UI)
npm run build:docker

# Build Studio UI only
npm run build:studio
```

## Component-Specific Builds

### CLI Tool

The CLI is built as a Python package using Poetry:

```bash
cd cli

# Install dependencies
poetry install

# Build wheel and source distribution
poetry build

# Output: cli/dist/trainloop_cli-*.whl and cli/dist/trainloop_cli-*.tar.gz
```

#### CLI Build Options

```bash
# Build with specific Python version
poetry env use python3.11
poetry build

# Build for development (editable install)
poetry install --no-dev

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
```

### Python SDK

The Python SDK is built similarly to the CLI:

```bash
cd sdk/python

# Install dependencies
poetry install

# Build package
poetry build

# Output: sdk/python/dist/trainloop_llm_logging-*.whl and *.tar.gz
```

#### Python SDK Build Configuration

The SDK build is configured in `sdk/python/pyproject.toml`:

```toml
[tool.poetry]
name = "trainloop-llm-logging"
version = "0.8.0"
description = "TrainLoop LLM Logging SDK"

[tool.poetry.dependencies]
python = "^3.9"
fsspec = ">=2023.1.0"
```

### TypeScript SDK

The TypeScript SDK is built as a Node.js package:

```bash
cd sdk/typescript

# Install dependencies
npm install

# Build TypeScript to JavaScript
npm run build

# Output: sdk/typescript/dist/
```

#### TypeScript Build Configuration

Build settings in `sdk/typescript/package.json`:

```json
{
  "scripts": {
    "build": "tsc",
    "build:watch": "tsc --watch",
    "clean": "rm -rf dist/"
  }
}
```

TypeScript configuration in `sdk/typescript/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
```

### Go SDK

The Go SDK is built as a Go module:

```bash
cd sdk/go/trainloop-llm-logging

# Download dependencies
go mod download

# Build the module
go build ./...

# Run tests (includes build validation)
go test ./...

# Build for different architectures
GOOS=linux GOARCH=amd64 go build ./...
GOOS=darwin GOARCH=arm64 go build ./...
```

#### Go Build Configuration

Module configuration in `sdk/go/trainloop-llm-logging/go.mod`:

```go
module github.com/TrainLoop/evals/sdk/go/trainloop-llm-logging

go 1.21

require (
    // Dependencies listed here
)
```

### Studio UI

The Studio UI is built as a Next.js application:

```bash
cd ui

# Install dependencies
npm install

# Build for production
npm run build

# Output: ui/.next/ and ui/out/ (if using static export)
```

#### Studio UI Build Configuration

Build settings in `ui/package.json`:

```json
{
  "scripts": {
    "build": "next build",
    "build:analyze": "ANALYZE=true next build",
    "build:static": "next build && next export"
  }
}
```

Next.js configuration in `ui/next.config.mjs`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    outputFileTracingRoot: path.join(__dirname, '../')
  }
};
```

### Documentation

Build the documentation site:

```bash
cd docs

# Install dependencies
npm install

# Build static site
npm run build

# Output: docs/build/
```

## Advanced Build Options

### Development Builds

For development with hot reloading:

```bash
# CLI development
cd cli && poetry install

# UI development
cd ui && npm run dev

# Documentation development
cd docs && npm start
```

### Production Builds

For production deployment:

```bash
# Build all components for production
npm run build

# Build with optimization
cd ui && npm run build:analyze
```

### Docker Builds

Build Docker images for deployment:

```bash
# Build Studio UI Docker image
cd ui
docker build -t trainloop-studio .

# Build with specific tag
docker build -t trainloop-studio:latest .
```

## Build Scripts

### Main Build Script

The main build script (`scripts/build.py`) orchestrates building all components:

```python
#!/usr/bin/env python3
"""
Build script for TrainLoop Evals
Builds CLI, SDKs, and Studio UI
"""

import subprocess
import sys
from pathlib import Path

def build_cli():
    """Build CLI package"""
    subprocess.run(["poetry", "build"], cwd="cli", check=True)

def build_python_sdk():
    """Build Python SDK package"""
    subprocess.run(["poetry", "build"], cwd="sdk/python", check=True)

def build_typescript_sdk():
    """Build TypeScript SDK"""
    subprocess.run(["npm", "run", "build"], cwd="sdk/typescript", check=True)

def build_studio_ui():
    """Build Studio UI"""
    subprocess.run(["npm", "run", "build"], cwd="ui", check=True)
```

### Build Options

```bash
# Build with specific options
pipx run scripts/build.py --help

# Skip specific components
pipx run scripts/build.py --skip-studio
pipx run scripts/build.py --skip-docker

# Build with verbose output
pipx run scripts/build.py --verbose
```

## Build Artifacts

### CLI Artifacts

- **Location**: `cli/dist/`
- **Files**: 
  - `trainloop_cli-*.whl` - Wheel package
  - `trainloop_cli-*.tar.gz` - Source distribution

### Python SDK Artifacts

- **Location**: `sdk/python/dist/`
- **Files**:
  - `trainloop_llm_logging-*.whl` - Wheel package
  - `trainloop_llm_logging-*.tar.gz` - Source distribution

### TypeScript SDK Artifacts

- **Location**: `sdk/typescript/dist/`
- **Files**:
  - JavaScript files transpiled from TypeScript
  - Type definition files (`.d.ts`)

### Go SDK Artifacts

- **Location**: Module built in place
- **Files**: Compiled Go binaries (when building executables)

### Studio UI Artifacts

- **Location**: `ui/.next/`
- **Files**:
  - `standalone/` - Self-contained Node.js application
  - `static/` - Static assets

## Troubleshooting

### Common Build Issues

#### Poetry Build Fails

```bash
# Clear poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache

# Update poetry itself
pipx upgrade poetry
```

#### Node.js Build Fails

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Use specific Node.js version
nvm use 20
```

#### Go Build Fails

```bash
# Clean module cache
go clean -modcache

# Update dependencies
go get -u ./...

# Verify module integrity
go mod verify
```

#### Next.js Build Fails

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Build with verbose output
npm run build -- --debug
```

### Build Performance

#### Speeding Up Builds

```bash
# Use parallel builds where possible
npm run build:parallel

# Use build cache
export POETRY_CACHE_DIR=~/.cache/poetry
export npm_config_cache=~/.npm
```

#### Reducing Build Size

```bash
# Build production-only dependencies
poetry install --no-dev
npm ci --only=production

# Use build optimization
npm run build:analyze
```

### Build Validation

#### Verify Build Artifacts

```bash
# Check CLI build
cd cli && poetry run trainloop --version

# Check Python SDK
cd sdk/python && poetry run python -c "import trainloop_llm_logging; print('SDK OK')"

# Check TypeScript SDK
cd sdk/typescript && npm test

# Check Go SDK
cd sdk/go/trainloop-llm-logging && go test ./...

# Check Studio UI
cd ui && npm run build && npm start
```

#### Integration Testing

```bash
# Run integration tests against built artifacts
task test:integration

# Test CLI installation
pipx install ./cli/dist/trainloop_cli-*.whl
trainloop --version
```

## Continuous Integration

### GitHub Actions

The project uses GitHub Actions for automated builds:

```yaml
name: Build and Test
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Build all components
        run: npm run build
```

### Local CI Simulation

```bash
# Run the same steps as CI locally
act -j build  # Using act tool

# Or manually simulate
npm run build
npm test
```

## Release Builds

### Preparation

```bash
# Update version numbers
npm run bump

# Update changelog
# Edit CHANGELOG.md

# Run full test suite
task test
```

### Build Release

```bash
# Build release artifacts
npm run build

# Run release script
npm run release
```

### Verification

```bash
# Verify all components
task test:integration

# Check artifact integrity
ls -la */dist/
```

## Next Steps

- Review the [Testing Guide](./testing.md) for build validation
- Check the [Release Process](./release-process.md) for deployment
- See the [Local Development](./local-development.md) guide for development builds