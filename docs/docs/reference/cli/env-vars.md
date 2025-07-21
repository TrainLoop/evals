---
sidebar_position: 8
---

# Environment Variables

Environment variables that control TrainLoop CLI behavior.

## Core Variables

### TRAINLOOP_DATA_FOLDER

**Description**: Location where event data and results are stored

**Default**: `./trainloop/data`

**Usage**:
```bash
export TRAINLOOP_DATA_FOLDER="/path/to/data"
trainloop eval
```

### TRAINLOOP_CONFIG_FILE

**Description**: Path to configuration file

**Default**: `trainloop.config.yaml` (with discovery cascade)

**Usage**:
```bash
export TRAINLOOP_CONFIG_FILE="/path/to/config.yaml"
trainloop eval
```

### TRAINLOOP_LOG_LEVEL

**Description**: Logging level

**Values**: `debug`, `info`, `warn`, `error`

**Default**: `info`

**Usage**:
```bash
export TRAINLOOP_LOG_LEVEL="debug"
trainloop eval
```

## LLM Provider API Keys

### OPENAI_API_KEY

**Description**: OpenAI API key for LLM calls and LLM Judge

**Usage**:
```bash
export OPENAI_API_KEY="sk-..."
trainloop eval
```

### ANTHROPIC_API_KEY

**Description**: Anthropic API key for Claude models

**Usage**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
trainloop eval
```

### GOOGLE_API_KEY

**Description**: Google API key for Gemini models

**Usage**:
```bash
export GOOGLE_API_KEY="AIza..."
trainloop eval
```

## SDK-Specific Variables

### TRAINLOOP_FLUSH_IMMEDIATELY

**Description**: Force immediate flushing of events (disables buffering)

**Values**: `true`, `false`

**Default**: `false`

**Usage**:
```bash
export TRAINLOOP_FLUSH_IMMEDIATELY=true
python your_app.py
```

### TRAINLOOP_TAGS

**Description**: Default tags to apply to all events

**Usage**:
```bash
export TRAINLOOP_TAGS="production,v1.0"
python your_app.py
```

## Advanced Configuration

### TRAINLOOP_JUDGE_MODELS

**Description**: Override LLM Judge models

**Usage**:
```bash
export TRAINLOOP_JUDGE_MODELS="openai/gpt-4o-mini,anthropic/claude-3-haiku"
trainloop eval
```

### TRAINLOOP_PARALLEL_EVALUATIONS

**Description**: Number of parallel evaluation processes

**Default**: `10`

**Usage**:
```bash
export TRAINLOOP_PARALLEL_EVALUATIONS=5
trainloop eval
```

### TRAINLOOP_CACHE_ENABLED

**Description**: Enable/disable result caching

**Values**: `true`, `false`

**Default**: `true`

**Usage**:
```bash
export TRAINLOOP_CACHE_ENABLED=false
trainloop eval
```

## Studio UI Variables

### TRAINLOOP_STUDIO_PORT

**Description**: Default port for Studio UI

**Default**: `3000`

**Usage**:
```bash
export TRAINLOOP_STUDIO_PORT=8080
trainloop studio
```

### TRAINLOOP_STUDIO_HOST

**Description**: Default host for Studio UI

**Default**: `localhost`

**Usage**:
```bash
export TRAINLOOP_STUDIO_HOST="0.0.0.0"
trainloop studio
```

## Development Variables

### TRAINLOOP_DEV_MODE

**Description**: Enable development mode features

**Values**: `true`, `false`

**Default**: `false`

**Usage**:
```bash
export TRAINLOOP_DEV_MODE=true
trainloop eval
```

### TRAINLOOP_REGISTRY_URL

**Description**: Custom registry URL for development

**Default**: `https://registry.trainloop.ai`

**Usage**:
```bash
export TRAINLOOP_REGISTRY_URL="http://localhost:8000"
trainloop add --list
```

## Security Variables

### TRAINLOOP_ENCRYPT_EVENTS

**Description**: Encrypt event data at rest

**Values**: `true`, `false`

**Default**: `false`

**Usage**:
```bash
export TRAINLOOP_ENCRYPT_EVENTS=true
export TRAINLOOP_ENCRYPTION_KEY="your-key-here"
trainloop eval
```

### TRAINLOOP_ANONYMIZE_DATA

**Description**: Anonymize personally identifiable information

**Values**: `true`, `false`

**Default**: `false`

**Usage**:
```bash
export TRAINLOOP_ANONYMIZE_DATA=true
trainloop eval
```

## Complete Environment Setup

### Development Environment

```bash
# ~/.bashrc or ~/.zshrc
export TRAINLOOP_DATA_FOLDER="$HOME/trainloop-data"
export TRAINLOOP_LOG_LEVEL="debug"
export TRAINLOOP_FLUSH_IMMEDIATELY=true
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Production Environment

```bash
# /etc/environment or systemd service
export TRAINLOOP_DATA_FOLDER="/var/lib/trainloop/data"
export TRAINLOOP_LOG_LEVEL="info"
export TRAINLOOP_PARALLEL_EVALUATIONS=20
export TRAINLOOP_CACHE_ENABLED=true
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### CI/CD Environment

```bash
# CI/CD pipeline
export TRAINLOOP_DATA_FOLDER="/tmp/trainloop-ci"
export TRAINLOOP_LOG_LEVEL="warn"
export TRAINLOOP_FLUSH_IMMEDIATELY=true
export TRAINLOOP_CACHE_ENABLED=false
export OPENAI_API_KEY="$OPENAI_API_KEY_CI"
```

## Precedence Order

Configuration values are resolved in this order (highest to lowest precedence):

1. **Command line arguments** (e.g., `--data-folder`)
2. **Environment variables** (e.g., `TRAINLOOP_DATA_FOLDER`)
3. **Configuration file** (e.g., `trainloop.config.yaml`)
4. **Default values**

## Validation

Check current environment variable values:

```bash
# Show all TrainLoop environment variables
env | grep TRAINLOOP

# Validate configuration
trainloop config --show

# Test with specific environment
TRAINLOOP_LOG_LEVEL=debug trainloop eval --dry-run
```

## See Also

- [Configuration](config.md) - Configuration file format
- [CLI Reference](index.md) - Command line interface overview
- [SDK Reference](../sdk/index.md) - SDK-specific variables