# Building the Runner

## Prerequisites

- Node.js 18 or newer
- Python 3.9 for helper scripts

## Steps

1. Install repo dependencies
   ```bash
   ./scripts/setup.py
   ```
2. Build the Studio bundle
   ```bash
   npm run build:studio
   ```
3. The bundled files appear in `runner/_bundle/`.
