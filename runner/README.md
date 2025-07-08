# TrainLoop Studio Runner

Simple wrapper used by the CLI to serve the prebuilt Studio UI.

## Usage

```bash
node bin/run.js
```

It expects `TRAINLOOP_DATA_FOLDER` to point to the folder where the SDKs write their files.

## DuckDB Bindings

The runner automatically detects and installs platform-specific DuckDB bindings on first run. This keeps the package size small while ensuring compatibility across different platforms.

Supported platforms:
- macOS (x64, arm64)
- Linux (x64, arm64)
- Windows (x64)

The bindings are installed to the bundle's node_modules directory and do not affect your global npm installation.
