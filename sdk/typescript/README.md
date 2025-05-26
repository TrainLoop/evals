# TrainLoop Evals SDK (TypeScript)

Patches Node HTTP libraries so every LLM request is logged for evaluation.

## Install

```bash
npm install trainloop-llm-logging
```

## Usage

```bash
export TRAINLOOP_DATA_FOLDER=./trainloop/data # optional, otherwise will use the path at trainloop/trainloop.config.yaml
NODE_OPTIONS="--require=trainloop-llm-logging" next dev
```

Tag individual calls when needed:

```ts
openai.chat.completions.create(..., { headers: { ...trainloopTag("checkout") } })
```

Logs are written under `$TRAINLOOP_DATA_FOLDER`.

See the [project README](../../README.md) for context.
