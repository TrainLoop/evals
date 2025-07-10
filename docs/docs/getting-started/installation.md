---
sidebar_position: 1
---

# Installation

Get started with TrainLoop Evals by installing the CLI tool and SDKs. This guide covers all installation methods and platform-specific requirements.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or later (for CLI and Python SDK)
- **Node.js**: 16 or later (for TypeScript/JavaScript SDK)
- **Go**: 1.19 or later (for Go SDK)

### Required Tools

TrainLoop Evals uses **pipx** for CLI installation, which provides better isolation and dependency management than pip.

#### Install pipx

If you don't have pipx installed, follow these steps:

**macOS/Linux:**
```bash
# Using pip
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Using Homebrew (macOS)
brew install pipx
pipx ensurepath

# Using apt (Ubuntu/Debian)
sudo apt install pipx
pipx ensurepath
```

**Windows:**
```powershell
# Using pip
python -m pip install --user pipx
python -m pipx ensurepath

# Using Scoop
scoop install pipx
pipx ensurepath
```

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS with zsh
```

## CLI Installation

### Method 1: pipx (Recommended)

Install the TrainLoop CLI using pipx for the best experience:

```bash
pipx install trainloop-cli
```

Verify the installation:
```bash
trainloop --version
```

### Method 2: pip

If you prefer using pip directly:

```bash
pip install trainloop-cli
```

:::warning
Installing with pip may cause dependency conflicts with other packages. We recommend using pipx for better isolation.
:::

### Method 3: Run Without Installation

You can run TrainLoop CLI directly without installing it:

```bash
pipx run trainloop-cli --help
```

This is useful for trying out the tool or running in CI/CD environments.

## SDK Installation

Choose the SDK that matches your application's programming language:

### Python SDK

Install the Python SDK for instrumenting Python applications:

```bash
pip install trainloop-llm-logging
```

For Poetry users:
```bash
poetry add trainloop-llm-logging
```

For Conda users:
```bash
conda install -c conda-forge trainloop-llm-logging
```

### TypeScript/JavaScript SDK

Install the TypeScript/JavaScript SDK for Node.js applications:

```bash
npm install trainloop-llm-logging
```

Or with Yarn:
```bash
yarn add trainloop-llm-logging
```

Or with pnpm:
```bash
pnpm add trainloop-llm-logging
```

### Go SDK

Install the Go SDK for Go applications:

```bash
go get github.com/trainloop/evals/sdk/go/trainloop-llm-logging
```

## Verification

After installation, verify that everything is working correctly:

### CLI Verification

```bash
# Check CLI version
trainloop --version

# Get help
trainloop --help

# Test initialization (creates a test workspace)
mkdir test-trainloop
cd test-trainloop
trainloop init
```

### SDK Verification

#### Python SDK
```python
# test_python_sdk.py
from trainloop_llm_logging import collect

# This should not raise any errors
collect()
print("Python SDK installed successfully!")
```

#### TypeScript/JavaScript SDK
```javascript
// test_js_sdk.js
const { trainloopTag } = require('trainloop-llm-logging');

// This should not raise any errors
console.log("JavaScript SDK installed successfully!");
console.log("Tag example:", trainloopTag("test"));
```

#### Go SDK
```go
// test_go_sdk.go
package main

import (
    "fmt"
    trainloop "github.com/trainloop/evals/sdk/go/trainloop-llm-logging"
)

func main() {
    // This should not raise any errors
    fmt.Println("Go SDK installed successfully!")
}
```

## Troubleshooting

### Common Issues

#### pipx not found

**Error**: `pipx: command not found`

**Solution**: Ensure pipx is installed and in your PATH:
```bash
# Check if pipx is in PATH
which pipx

# If not found, try installing pipx again
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

#### Python version compatibility

**Error**: `Python 3.8 or later required`

**Solution**: Upgrade your Python version:
```bash
# Check current Python version
python --version

# Install Python 3.8+ using your system package manager
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Windows: Download from python.org
```

#### Permission errors

**Error**: `Permission denied` during installation

**Solution**: Use user installation or virtual environment:
```bash
# For pip
pip install --user trainloop-cli

# For pipx (already installs in user space)
pipx install trainloop-cli
```

#### Node.js version issues

**Error**: `Node.js 16 or later required`

**Solution**: Upgrade Node.js:
```bash
# Check current Node.js version
node --version

# Install latest Node.js
# Using nvm (recommended)
nvm install node
nvm use node

# Or download from nodejs.org
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Most commands have `--verbose` or `--debug` flags for detailed output
2. **GitHub Issues**: [Report bugs or request features](https://github.com/trainloop/evals/issues)
3. **Community**: Join our community discussions

## Next Steps

Once you have TrainLoop Evals installed:

1. **[Follow the Quick Start Guide](./quick-start.md)** - Create your first evaluation
2. **[Explore the Guides](../guides/)** - Learn advanced features
3. **[Check the Reference](../reference/)** - Detailed API documentation

## Updating

Keep your TrainLoop installation up to date:

### Update CLI
```bash
# With pipx
pipx upgrade trainloop-cli

# With pip
pip install --upgrade trainloop-cli
```

### Update SDKs
```bash
# Python SDK
pip install --upgrade trainloop-llm-logging

# JavaScript SDK
npm update trainloop-llm-logging

# Go SDK
go get -u github.com/trainloop/evals/sdk/go/trainloop-llm-logging
```

## Development Installation

For contributors or those who want to use the latest development version:

```bash
# Clone the repository
git clone https://github.com/trainloop/evals.git
cd evals

# Install CLI from source
cd cli
poetry install
poetry run trainloop --help

# Install Python SDK from source
cd ../sdk/python
poetry install

# Install JavaScript SDK from source
cd ../typescript
npm install
npm run build
```

:::tip
Development installation gives you access to the latest features but may be less stable than released versions.
:::