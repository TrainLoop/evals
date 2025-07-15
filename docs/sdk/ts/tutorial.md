# TypeScript SDK Tutorial

Install the package and require it before other imports:
```bash
npm install trainloop-llm-logging
NODE_OPTIONS="--require=trainloop-llm-logging" node index.js
```
Set the data folder path:
```bash
export TRAINLOOP_DATA_FOLDER="$(pwd)/trainloop/data"
```
Collection happens only when HTTP calls occur.
