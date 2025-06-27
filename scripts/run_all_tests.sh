#!/bin/bash
# Run all tests for the TrainLoop project

set -e  # Exit on first error

# Get the directory of this script and change to the workspace root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}TrainLoop Test Suite${NC}"
echo "Running all tests..."
echo

# Function to run tests
run_test() {
    local description="$1"
    local directory="$2"
    local command="$3"
    
    echo -e "${BLUE}${BOLD}============================================================${NC}"
    echo -e "${BLUE}${BOLD}${description}${NC}"
    echo -e "${BLUE}${BOLD}============================================================${NC}"
    echo "Directory: ${directory}"
    echo "Command: ${command}"
    echo
    
    cd "${directory}"
    if eval "${command}"; then
        echo -e "${GREEN}✓ ${description} - PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ ${description} - FAILED${NC}"
        return 1
    fi
}

# Track failures
FAILED=0

# 1. CLI FSSpec Integration Tests
run_test "CLI FSSpec Integration Tests" \
    "cli" \
    "poetry run pytest ../tests/unit/test_fsspec_integration.py -v" || ((FAILED++))

# 2. SDK FSSpec Tests  
run_test "SDK FSSpec Tests" \
    "sdk/python" \
    "poetry run pytest tests/unit/test_fsspec_store.py -v" || ((FAILED++))

# 3. SDK Store Tests
run_test "SDK Store Tests" \
    "sdk/python" \
    "poetry run pytest tests/unit/test_store.py -v" || ((FAILED++))

# 4. Init Command Tests
run_test "Init Command Integration Tests" \
    "cli" \
    "poetry run pytest ../tests/integration/init_flow/test_init_command.py -v" || ((FAILED++))

# 5. All CLI Unit Tests
run_test "All CLI Unit Tests" \
    "cli" \
    "poetry run pytest -m unit -v" || ((FAILED++))

# 6. All SDK Unit Tests
run_test "All SDK Unit Tests" \
    "sdk/python" \
    "poetry run pytest -m unit -v" || ((FAILED++))

# 7. Check for MagicMock directories
echo -e "${BLUE}${BOLD}============================================================${NC}"
echo -e "${BLUE}${BOLD}Checking for MagicMock directories${NC}"
echo -e "${BLUE}${BOLD}============================================================${NC}"

cd "${WORKSPACE_ROOT:-/workspace}"
MOCK_COUNT=$(find . -name "*MagicMock*" -type d 2>/dev/null | wc -l)
if [ "$MOCK_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No MagicMock directories found${NC}"
else
    echo -e "${RED}✗ Found ${MOCK_COUNT} MagicMock directories:${NC}"
    find . -name "*MagicMock*" -type d 2>/dev/null
    ((FAILED++))
fi

# Summary
echo
echo -e "${BOLD}============================================================${NC}"
echo -e "${BOLD}Test Summary${NC}"
echo -e "${BOLD}============================================================${NC}"

TOTAL=7
PASSED=$((TOTAL - FAILED))

echo "Total: ${TOTAL} test suites"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
if [ "$FAILED" -gt 0 ]; then
    echo -e "${RED}Failed: ${FAILED}${NC}"
    echo -e "${RED}${BOLD}✗ Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}${BOLD}✓ All tests passed!${NC}"
    exit 0
fi