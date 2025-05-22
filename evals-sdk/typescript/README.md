# TrainLoop Evals SDK (TypeScript)

Patches Node HTTP libraries so every LLM request is logged for evaluation.

## Install

```bash
npm install trainloop-evals-sdk
```

## Usage

```bash
export TRAINLOOP_DATA_FOLDER=./trainloop/data
NODE_OPTIONS="--require=trainloop-evals-sdk" node app.js
```

Tag individual calls when needed:

```ts
openai.chat.completions.create(..., { headers: { ...trainloopTag("checkout") } })
```

Logs are written under `$TRAINLOOP_DATA_FOLDER`.

See the [project README](../../README.md) for context.
