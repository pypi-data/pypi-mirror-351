#!/bin/bash
# Run the full regression test suite for fit_better
# 
# Usage:
#   ./run_all_tests.sh [options]
#
# Options:
#   -c, --cleanup        Clean up generated files
#   -u, --unit-tests     Run ONLY unit tests (using pytest directly)
#   -s, --usages         Run ONLY usage examples (via test_all.py)
#   -p, --cpp            Run ONLY C++ tests
#   -i, --individual SCRIPT  Run a specific script (without .py extension)
#   -v, --verbose        Show verbose output
#   -w, --wheel          Run tests on installed wheel package
#   -h, --help           Show this help message
#
# Test Categories:
#   1. Unit Tests: Run via pytest (in unittests/ directory)
#   2. Usage Examples: Run via test_all.py (in usages/ directory)  
#   3. C++ Tests: Run via ctest (in cpp/build directory)
#   4. Wheel Tests: Build wheel, install in venv, and run tests from unittests/test_fresh_install.py
#
# If no options are specified, ALL test categories will be run (unit tests, usages, and C++).
# If specific categories are selected, ONLY those will run (e.g., -u will ONLY run unit tests).

#
# Initialize variables
#
CLEANUP=false
RUN_UNIT_TESTS=false
RUN_USAGES=false
RUN_CPP_TESTS=false
RUN_WHEEL_TESTS=false
SCRIPT_NAME=""
VERBOSE=false
PROJECT_ROOT="$(realpath $(dirname "$0")/../)"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Track overall execution time
overall_start_time=$(date +%s)

# Track total test results
total_tests=0
total_passed=0
total_failed=0

#
# Parse command line arguments
#
while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--cleanup)
      CLEANUP=true
      shift
      ;;
    -u|--unit-tests)
      RUN_UNIT_TESTS=true
      shift
      ;;
    -s|--usages)
      RUN_USAGES=true
      shift
      ;;
    -p|--cpp)
      RUN_CPP_TESTS=true
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -w|--wheel)
      RUN_WHEEL_TESTS=true
      shift
      ;;
    -i|--individual)
      if [ -n "$2" ]; then
        SCRIPT_NAME="$2"
        shift 2
      else
        echo -e "${RED}Error: No script name provided after -i/--individual${NC}"
        exit 1
      fi
      ;;
    -h|--help)
      echo "Usage: ./run_all_tests.sh [options]"
      echo "Options:"
      echo "  -c, --cleanup        Clean up generated files"
      echo "  -u, --unit-tests     Run ONLY unit tests (using pytest directly)"
      echo "  -s, --usages         Run ONLY usage examples (via test_all.py)"
      echo "  -p, --cpp            Run ONLY C++ tests"
      echo "  -i, --individual SCRIPT  Run a specific script (without .py extension)"
      echo "  -v, --verbose        Show verbose output"
      echo "  -w, --wheel          Run tests on installed wheel package"
      echo "  -h, --help           Show this help message"
      echo ""
      echo "Test Categories:"
      echo "  1. Unit Tests: Run via pytest (in unittests/ directory)"
      echo "  2. Usage Examples: Run via test_all.py (in usages/ directory)"
      echo "  3. C++ Tests: Run via ctest (in cpp/build directory)"
      echo "  4. Wheel Tests: Build wheel, install in venv, and run tests"
      echo ""
      echo "If no options are specified, ALL test categories will be run (unit tests, usages, and C++)."
      echo "If specific categories are selected, ONLY those will run (e.g., -u will ONLY run unit tests)."
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help to see available options."
      exit 1
      ;;
  esac
done

#
# Handle cleanup operation if requested
#
if [ "$CLEANUP" = "true" ]; then
  echo "Cleaning up all generated test content..."
  
  # Ask for confirmation
  read -p "This will remove all test data, results, and archives. Continue? [y/N] " -r confirm < /dev/tty
  
  if [[ "$confirm" != [yY] ]]; then
    echo "Cleanup cancelled."
    exit 0
  fi
  
  # Do full cleanup using test_all.py --clean
  python test_all.py --clean
  clean_status=$?
  
  if [ $clean_status -eq 0 ]; then
    echo -e "${GREEN}Cleanup completed successfully.${NC}"
  else
    echo -e "${RED}Cleanup failed with status $clean_status${NC}"
  fi
  
  # Clean C++ build artifacts if they exist
  cpp_build_dir="$PROJECT_ROOT/cpp/build"
  if [ -d "$cpp_build_dir" ]; then
    echo -e "${YELLOW}Cleaning C++ build directory...${NC}"
    rm -rf "$cpp_build_dir"
    mkdir -p "$cpp_build_dir"
    echo -e "${GREEN}C++ build directory cleaned.${NC}"
  fi
  
  exit $clean_status
fi

#
# Set up environment
#

# Change to the tests directory
cd "$(dirname "$0")" || exit 1

# Add parent directory (project root) and current directory (tests) to Python path
# This allows finding fit_better and modules within tests/
export PYTHONPATH="$(realpath ../):$PYTHONPATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo -e "${CYAN}Using current Python environment: $(which python)${NC}"

# Create required directories
python -c "
import os
from pathlib import Path
# Use current directory since __file__ doesn't work in -c context
script_dir = os.getcwd()
dirs = ['data_gen/logs', 'data_gen/data', 'data_gen/visualization_results', 'data_gen/archived_results']
for d in dirs:
    dir_path = os.path.join(script_dir, d)
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f'Created directory: {dir_path}')
"

# Arrays to store test results
declare -a test_names
declare -a test_results
declare -a test_durations

#
# Define helper functions
#

# Print test statistics
print_test_stats() {
  local test_type="$1"
  local passed=0
  local failed=0
  local total_duration=0
  
  echo -e "\n${YELLOW}=== $test_type Summary ===${NC}"
  echo "----------------------------------------"
  
  for i in "${!test_names[@]}"; do
    if [ ${test_results[$i]} -eq 0 ]; then
      echo -e "${GREEN}✓ PASSED:${NC} ${test_names[$i]} (took ${test_durations[$i]}s)"
      passed=$((passed + 1))
    else
      echo -e "${RED}✗ FAILED:${NC} ${test_names[$i]} (took ${test_durations[$i]}s)"
      failed=$((failed + 1))
    fi
    total_duration=$((total_duration + test_durations[$i]))
  done
  
  local total=$((passed + failed))
  local pass_percentage=0
  
  if [ $total -gt 0 ]; then
    pass_percentage=$((passed * 100 / total))
  fi
  
  echo "----------------------------------------"
  echo -e "${CYAN}Results: ${passed}/${total} tests passed (${pass_percentage}%)${NC}"
  
  # Return 0 if all tests passed, 1 otherwise
  if [ $failed -eq 0 ]; then
    return 0
  else
    return 1
  fi
}

# If no specific test categories were selected, run all by default
if [ "$RUN_UNIT_TESTS" = "false" ] && [ "$RUN_USAGES" = "false" ] && [ "$RUN_CPP_TESTS" = "false" ] && [ "$RUN_WHEEL_TESTS" = "false" ] && [ -z "$SCRIPT_NAME" ]; then
  echo -e "${YELLOW}No specific test category selected. Running all test categories.${NC}"
  RUN_UNIT_TESTS=true
  RUN_USAGES=true
  RUN_CPP_TESTS=true
fi

#
# Run Unit Tests (Python)
#
if [ "$RUN_UNIT_TESTS" = "true" ]; then
  echo -e "\n${YELLOW}==== Running Python Unit Tests ====${NC}"
  
  # Clear test results array
  test_names=()
  test_results=()
  test_durations=()
  
  # Run pytest on the unittests directory
  unit_test_start=$(date +%s)
  
  if [ "$VERBOSE" = "true" ]; then
    python -m pytest unittests/ -v
  else
    python -m pytest unittests/
  fi
  
  unit_test_status=$?
  unit_test_end=$(date +%s)
  unit_test_duration=$((unit_test_end - unit_test_start))
  
  test_names+=("Python Unit Tests")
  test_results+=($unit_test_status)
  test_durations+=($unit_test_duration)
  
  # Print test statistics
  print_test_stats "Python Unit Tests"
  unit_test_overall_status=$?
  
  # Update total counts
  if [ $unit_test_overall_status -eq 0 ]; then
    total_passed=$((total_passed + 1))
  else
    total_failed=$((total_failed + 1))
  fi
  total_tests=$((total_tests + 1))
fi

#
# Run Usage Examples
#
if [ "$RUN_USAGES" = "true" ]; then
  echo -e "\n${YELLOW}==== Running Usage Examples ====${NC}"
  
  # Clear test results array
  test_names=()
  test_results=()
  test_durations=()
  
  if [ -n "$SCRIPT_NAME" ]; then
    echo -e "${CYAN}Running individual script: $SCRIPT_NAME${NC}"
    
    usage_start=$(date +%s)
    
    if [ "$VERBOSE" = "true" ]; then
      python test_all.py --test "$SCRIPT_NAME" --verbose
    else
      python test_all.py --test "$SCRIPT_NAME"
    fi
    
    usage_status=$?
    usage_end=$(date +%s)
    usage_duration=$((usage_end - usage_start))
    
    test_names+=("$SCRIPT_NAME")
    test_results+=($usage_status)
    test_durations+=($usage_duration)
    
  else
    echo -e "${CYAN}Running all usage examples${NC}"
    
    usage_start=$(date +%s)
    
    if [ "$VERBOSE" = "true" ]; then
      python test_all.py --verbose
    else
      python test_all.py
    fi
    
    usage_status=$?
    usage_end=$(date +%s)
    usage_duration=$((usage_end - usage_start))
    
    test_names+=("All Usage Examples")
    test_results+=($usage_status)
    test_durations+=($usage_duration)
  fi
  
  # Print test statistics
  print_test_stats "Usage Examples"
  usage_overall_status=$?
  
  # Update total counts
  if [ $usage_overall_status -eq 0 ]; then
    total_passed=$((total_passed + 1))
  else
    total_failed=$((total_failed + 1))
  fi
  total_tests=$((total_tests + 1))
fi

#
# Run C++ Tests
#
if [ "$RUN_CPP_TESTS" = "true" ]; then
  echo -e "\n${YELLOW}==== Running C++ Tests ====${NC}"
  
  # Clear test results array
  test_names=()
  test_results=()
  test_durations=()
  
  # Make sure build directory exists
  cpp_build_dir="$PROJECT_ROOT/cpp/build"
  if [ ! -d "$cpp_build_dir" ]; then
    echo -e "${CYAN}Creating C++ build directory...${NC}"
    mkdir -p "$cpp_build_dir"
  fi
  
  # Change to build directory and run cmake + ctest
  cd "$cpp_build_dir" || exit 1
  
  # Configure and build C++ tests
  echo -e "${CYAN}Configuring and building C++ tests...${NC}"
  cmake_start=$(date +%s)
  
  if [ "$VERBOSE" = "true" ]; then
    cmake .. -DBUILD_TESTS=ON
    make -j$(nproc)
  else
    cmake .. -DBUILD_TESTS=ON > /dev/null
    make -j$(nproc) > /dev/null
  fi
  
  cmake_status=$?
  cmake_end=$(date +%s)
  cmake_duration=$((cmake_end - cmake_start))
  
  test_names+=("C++ Build")
  test_results+=($cmake_status)
  test_durations+=($cmake_duration)
  
  # Only run tests if build succeeded
  if [ $cmake_status -eq 0 ]; then
    echo -e "${CYAN}Running C++ tests with CTest...${NC}"
    ctest_start=$(date +%s)
    
    if [ "$VERBOSE" = "true" ]; then
      ctest --output-on-failure
    else
      ctest --output-on-failure > /dev/null
    fi
    
    ctest_status=$?
    ctest_end=$(date +%s)
    ctest_duration=$((ctest_end - ctest_start))
    
    test_names+=("C++ Tests")
    test_results+=($ctest_status)
    test_durations+=($ctest_duration)
  fi
  
  # Return to tests directory
  cd "$PROJECT_ROOT/tests" || exit 1
  
  # Print test statistics
  print_test_stats "C++ Tests"
  cpp_test_overall_status=$?
  
  # Update total counts
  if [ $cpp_test_overall_status -eq 0 ]; then
    total_passed=$((total_passed + 1))
  else
    total_failed=$((total_failed + 1))
  fi
  total_tests=$((total_tests + 1))
fi

#
# Print overall summary
#
overall_end_time=$(date +%s)
overall_duration=$((overall_end_time - overall_start_time))

echo -e "\n${YELLOW}===== Overall Test Summary =====${NC}"
echo -e "Total Duration: ${overall_duration}s"
echo -e "Overall Results: ${total_passed}/${total_tests} test categories passed"

if [ $total_failed -eq 0 ]; then
  echo -e "${GREEN}✓ ALL TEST CATEGORIES PASSED${NC}"
  exit 0
else
  echo -e "${RED}✗ SOME TEST CATEGORIES FAILED${NC}"
  exit 1
fi

# Run wheel tests if requested
if [ "$RUN_WHEEL_TESTS" = "true" ]; then
  echo -e "\n${YELLOW}==== Running Wheel Package Tests ====${NC}"
  
  wheel_test_start=$(date +%s)
  
  echo -e "${CYAN}========================================${NC}"
  echo -e "${CYAN}= Testing fit_better with fresh install =${NC}"
  echo -e "${CYAN}========================================${NC}"
  
  # Detect which python to use
  PYTHON_CMD="python"
  if command -v python3 &> /dev/null; then
      PYTHON_CMD="python3"
  fi
  
  echo -e "${YELLOW}Using Python: $(which ${PYTHON_CMD})${NC}"
  echo -e "${YELLOW}Python version: $(${PYTHON_CMD} --version)${NC}"
  
  # Install pytest if needed
  if ! ${PYTHON_CMD} -c "import pytest" &> /dev/null; then
      echo -e "${YELLOW}Installing pytest...${NC}"
      ${PYTHON_CMD} -m pip install pytest
  fi
  
  # Check that pytest is installed
  if ! ${PYTHON_CMD} -c "import pytest" &> /dev/null; then
      echo -e "${YELLOW}Installing pytest...${NC}"
      ${PYTHON_CMD} -m pip install pytest
  fi

  # Check that build is installed
  if ! ${PYTHON_CMD} -c "import build" &> /dev/null; then
      echo -e "${YELLOW}Installing build package...${NC}"
      ${PYTHON_CMD} -m pip install build
  fi

  # Execute the fresh install test
  echo -e "${YELLOW}\nRunning fresh install test...${NC}"
  
  if [ "$VERBOSE" = "true" ]; then
      ${PYTHON_CMD} -m pytest unittests/test_fresh_install.py -v --no-header --tb=native
  else
      ${PYTHON_CMD} -m pytest unittests/test_fresh_install.py --no-header
  fi
  
  wheel_test_status=$?
  wheel_test_end=$(date +%s)
  wheel_test_duration=$((wheel_test_end - wheel_test_start))
  
  if [ $wheel_test_status -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED: All wheel package tests (${wheel_test_duration}s)${NC}"
    total_passed=$((total_passed + 1))
    
    echo -e "${CYAN}\nCheck test results in: ${PROJECT_ROOT}/tests/data_gen/fresh_install_results/${NC}"
  else
    echo -e "${RED}✗ FAILED: Some wheel package tests failed (${wheel_test_duration}s)${NC}"
    total_failed=$((total_failed + 1))
    
    # Show common failure reasons
    echo -e "\n${YELLOW}Common failure reasons:${NC}"
    echo -e "1. Missing 'build' package: ${CYAN}pip install build${NC}"
    echo -e "2. Missing setuptools-scm: ${CYAN}pip install setuptools-scm${NC}"
    echo -e "3. Project setup issues: Check pyproject.toml or setup.py"
    echo -e "4. Environment issues: Try using a clean virtual environment"
    
    echo -e "${CYAN}\nCheck test results and logs in: ${PROJECT_ROOT}/tests/data_gen/fresh_install_results/${NC}"
  fi
  total_tests=$((total_tests + 1))
fi
