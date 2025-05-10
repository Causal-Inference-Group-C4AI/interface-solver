#!/bin/bash
# filepath: c:\Users\lucas\OneDrive\Documentos\IC\GitHub\interface-solver\run_bracis_tests.sh

# Set the directory where test files are stored
TEST_DIR="tests"

# Find all BRACIS test files
BRACIS_TESTS=$(find $TEST_DIR -name "\[BRACIS\]-medium*.txt" | sort)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running all BRACIS tests...${NC}"
echo "--------------------------------------"

# Counter for tests
TOTAL=0
PASSED=0

# Loop through each test file and run it
for test_file in $BRACIS_TESTS; do
    TOTAL=$((TOTAL+1))
    test_name=$(basename "$test_file" .txt)

    echo -e "${YELLOW}Running test: ${test_name}${NC}"
    
    # Run docker compose and capture output while showing it in terminal
    docker compose run --remove-orphans main_interface -v "$test_file" | tee ./test_output.log
    
    # Check if the output contains [ERROR]
    if grep -q "\[ERROR\]" ./test_output.log; then
        echo -e "${RED}✗ Test $test_name failed${NC}"
    else
        echo -e "${GREEN}✓ Test $test_name passed${NC}"
        PASSED=$((PASSED+1))
    fi
    
    echo "--------------------------------------"
done

# Print summary
echo -e "${YELLOW}Test Summary:${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC} / $TOTAL"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi