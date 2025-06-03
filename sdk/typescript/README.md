# TrainLoop Evals SDK (TypeScript/JavaScript)

Patches Node HTTP libraries so every LLM request is logged for evaluation. Works with both TypeScript and JavaScript projects.

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

**TypeScript:**
```ts
import { trainloopTag } from 'trainloop-llm-logging';

openai.chat.completions.create(..., { headers: { ...trainloopTag("checkout") } })
```

**JavaScript:**
```js
const { trainloopTag } = require('trainloop-llm-logging');

openai.chat.completions.create(..., { headers: { ...trainloopTag("checkout") } })
```

Logs are written under `$TRAINLOOP_DATA_FOLDER`.

See the [project README](../../README.md) for context.
