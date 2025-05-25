# 🤖📊 TrainLoop Evals (ALPHA)

TrainLoop Evals is a framework for automating the collection and evaluation of LLM outputs. The core tenants of this are

- *Simplicity First* – one environment variable, one function call, one folder of JSON files.
- *Vendor Independence* – everything stored as newline-delimited JSON; no databases required.
- *Meet developers where they are* – accepts our simple declarative flow or existing bespoke loops.
- *Type-safe, In-code Tests* – all code present in codebase
- *Composable, Extensible System* – helper generators mimic shadcn patterns. (`trainloop add` coming soon!)

<p align="center">
  <img src="images/drake_evals.png" alt="Evals Meme" width="400" height="auto" />
</p>

## Demo

- Demo repo: https://github.com/TrainLoop/chat-ui-demo
- Demo deployment: https://evals.trainloop.ai


## Getting started

### Prerequisites

We rely on `pipx` to install the CLI. If you don't have it, follow the [instructions](https://pipx.pypa.io/stable/).

### Installation

Install the TrainLoop CLI using pipx:

```bash
pipx install trainloop-cli
```

Alternatively, you can install with pip:

```bash
pip install trainloop-cli
```

Or run directly without installation:

```bash
pipx run trainloop-cli --help
```

### Quick Start

1. **Create a workspace:**
   ```bash
   trainloop init
   ```

2. **Set the data path** where your data will be written or use the default (inside the trainloop folder) – this is where the SDKs write events.

3. **Instrument your app:**
   - **Node**: `NODE_OPTIONS="--require=trainloop-evals-sdk" <your start script>`
   - **Python**: `from trainloop_evals import collect; collect(<your config path>)`

4. **Write metrics and suites** in `trainloop/eval/`

5. **Run the evals:**
   ```bash
   trainloop eval
   ```

6. **Visualize results** in the Studio UI:
   ```bash
   trainloop studio
   ```

## CLI Reference

The TrainLoop CLI provides three main commands for managing your evaluation workflow:

### `trainloop init`

Scaffolds data/ and eval/ directories, creates sample metrics and suites.

```bash
trainloop init
```

This command creates a `trainloop/` workspace with the following structure:
- `trainloop/data/` - Where event and result data is stored
- `trainloop/eval/` - Where metrics and test suites are defined
- `trainloop.config.yaml` - Configuration file

### `trainloop eval`

Discovers suites, applies metrics to new events, and appends verdicts to data/results/.

```bash
trainloop eval [OPTIONS]
```

**Options:**
- `--suite <suite_name>` - Run only the specified suite instead of all suites

**Examples:**
```bash
# Run all evaluation suites
trainloop eval

# Run only a specific suite
trainloop eval --suite my_test_suite
```

### `trainloop studio`

Launches the TrainLoop Studio UI for visualizing and analyzing your evaluation data.

```bash
trainloop studio [OPTIONS]
```

**Options:**
- `--config <path>` - Path to the trainloop config file (overrides auto-discovery)
- `--local <path>` - Path to a local studio tar file (for development)

**Examples:**
```bash
# Launch studio with auto-discovery (default behavior)
trainloop studio

# Use custom config file
trainloop studio --config /path/to/trainloop.config.yaml

# Use local development build
trainloop studio --local /path/to/trainloop-studio-runner-0.4.0.tgz

# Combine both options
trainloop studio --config /custom/config.yaml --local /local/build.tgz

```

### Default Behavior

Running `trainloop` without any command automatically launches the Studio UI:

```bash
trainloop  # Same as: trainloop studio
```

### Global Options

- `--version` - Show the version and exit
- `-h, --help` - Show help message and exit

## About the TrainLoop Folder

The TrainLoop folder is where all your TrainLoop-specific files live and is created via `trainloop init`. It is structured by default as a data directory, evals directory, and config file.

You can find more information about it in [the Scaffold README](cli/scaffold/trainloop/README.md).

## About this repository
The repository is split into several packages:

- **cli/** – command line tool to scaffold workspaces, run suites and launch the Studio.
- **evals-sdk/typescript/** – Node SDK that logs LLM calls automatically.
- **evals-sdk/python/** – Python SDK for the same purpose.
- **ui/** and **runner/** – TrainLoop Studio web interface and its small runner.
- **infra/** – Pulumi config to deploy the Studio demo.

## More information

- [CLI README](cli/README.md)
- [TypeScript SDK](evals-sdk/typescript/README.md)
- [Python SDK](evals-sdk/python/README.md)
- [Studio UI](ui/README.md)
- [Studio Runner](runner/README.md)
- [Infrastructure](infra/README.md)
- [Contributing](CONTRIBUTING.md)
- [Versioning](VERSIONING.md)
- [Changelog](CHANGELOG.md)

## License

MIT
