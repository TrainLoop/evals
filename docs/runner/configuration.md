# Configuring the Runner

Set environment variables before starting the wrapper.

- `TRAINLOOP_DATA_FOLDER` – path to your `trainloop/` data folder. **Must exist.**
- `PORT` – port for the internal server (defaults to `8888`).

Run the executable:
```bash
node runner/bin/run.js
```

### Warning

Config values cascade. CLI flags override env vars. Env vars override `trainloop.config.yaml`.
Make sure the data folder path is correct or Studio will fail to start.
