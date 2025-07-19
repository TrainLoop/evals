---
sidebar_position: 9
---

# trainloop upgrade

Upgrade the TrainLoop project to the latest release and refresh generated files.

## Synopsis

```bash
trainloop upgrade
```

## Description

The `trainloop upgrade` command pulls the newest TrainLoop CLI, updates auto-generated
files like `README.md`, `.gitignore`, and `trainloop.config.yaml`, recreates the
local `.venv`, and records the CLI version in your configuration.

## Examples

```bash
# Upgrade the current project
trainloop upgrade
```
