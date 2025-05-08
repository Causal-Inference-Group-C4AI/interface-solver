#!/bin/bash
# filepath: c:\Users\lucas\OneDrive\Documentos\IC\GitHub\interface-solver\run_bracis_tests.sh

# Set the directory where test files are stored
TEST_DIR="tests"

# Find all BRACIS test files
BRACIS_TESTS=$(find $TEST_DIR -name "\[BRACIS\]*.txt" | sort)

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
    
    # Use docker compose to run the test
    docker compose run main_interface -v "$test_file"
    
    # Check if the test was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test $test_name passed${NC}"
        PASSED=$((PASSED+1))
    else
        echo -e "${RED}✗ Test $test_name failed${NC}"
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