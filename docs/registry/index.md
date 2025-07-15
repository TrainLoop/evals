---
title: Registry Overview
---

# TrainLoop Registry

The registry contains reusable metrics and suites that you can share across projects. Each component lives in the `registry/` folder and exposes a `config.py` file.

## Registering Components

1. Create a new folder under `registry/metrics/` or `registry/suites/`.
2. Define your metric or suite logic in a Python file.
3. Add a `config.py` with a `MetricConfig` or `SuiteConfig` object.
4. Commit the folder so others can import it.

Use `tags` and `description` fields in the config to label the component’s purpose. That makes discovery easier when you run `trainloop add --list`.

## Config Discovery

The CLI automatically imports every `config.py` found in the registry. Your project can reference these components by name. If a component requires another metric, list it in the `dependencies` field.

## YAML Schema

The registry’s config objects map cleanly to YAML. When you run `trainloop add`, the CLI exports the config file as YAML in your project. Here is a minimal metric configuration:

```yaml
name: always_pass
min_version: "0.5.0"
description: A simple metric that always passes
dependencies: []
author: TrainLoop Team
tags:
  - testing
```

## Data Folder Warning

The registry does not store data. However, your evaluation runs will use the `data_folder` setting from `trainloop.config.yaml`. Set the `TRAINLOOP_DATA_FOLDER` environment variable or the `data_folder` key in your config file to keep results organized. Avoid writing to system directories by mistake.

## Configuration Cascade

TrainLoop looks for configuration in this order:

1. `--config` option on the command line
2. `TRAINLOOP_CONFIG_PATH` environment variable
3. `trainloop.config.yaml` in your current directory
4. `trainloop/trainloop.config.yaml` in your current directory
5. The same search in parent directories

Explicit paths always win. Environment variables provide defaults for multiple projects.

