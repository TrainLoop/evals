#!/bin/bash
# Simple bash wrapper for setup.py
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 TrainLoop Monorepo Quick Setup${NC}"
echo ""

# Check if we're in a Docker container
if [ -f /.dockerenv ]; then
    echo -e "${YELLOW}📦 Running in Docker container${NC}"
fi

# Run the Python setup script
exec python3 "$(dirname "$0")/setup.py" "$@"