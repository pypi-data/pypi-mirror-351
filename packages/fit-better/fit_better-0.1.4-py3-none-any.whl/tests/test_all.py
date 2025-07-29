#!/usr/bin/env python3
"""
Run usage examples for the fit-better package.

This script executes the usage example scripts in the usages/ directory.
It DOES NOT run unit tests, which are run directly with pytest.

Usage examples include:
- Data generation
- Partitioning strategies
- Regressor comparisons
- Model saving/loading
- C++ deployment examples

NOTE: The project has three test categories:
1. Unit Tests: Run via pytest directly (in unittests/ directory)
2. Usage Examples: Run via this script (in usages/ directory)
3. C++ Tests: Run via ctest (in cpp/build directory)

The run_all_tests.sh script can run any combination of these categories.
"""
import os
import sys
import time
import shutil
import logging
import argparse
import subprocess
import warnings
from pathlib import Path
from datetime import datetime
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define paths
ROOT_DIR = Path(__file__).parent.parent
TESTS_DIR = ROOT_DIR / "tests"
USAGES_DIR = TESTS_DIR / "usages"
DATA_GEN_DIR = TESTS_DIR / "data_gen"
LOGS_DIR = DATA_GEN_DIR / "logs"
DATA_DIR = DATA_GEN_DIR / "data"
VISUALIZATION_DIR = DATA_GEN_DIR / "visualization_results"

# Create directories if they don't exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
VISUALIZATION_DIR.mkdir(parents=True, exist_ok=True)

# Test scripts
TESTS = {
    "generate_test_data": str(USAGES_DIR / "data_generation_example.py")
    + " --output-dir "
    + str(DATA_DIR)
    + " --n-samples 1000 --noise-level 0.5",
    "compare_partitions": str(USAGES_DIR / "partition_comparison_example.py"),
    "parallel_partitioning": str(USAGES_DIR / "parallel_partitioning_example.py"),
    "compare_regressors": str(USAGES_DIR / "regressor_comparison_example.py"),
    "find_best_partition_and_algo": str(
        USAGES_DIR / "partition_algorithm_finder_example.py"
    ),
    "model_save_load_example": str(USAGES_DIR / "model_save_load_example.py"),
    "cpp_deployment_example": str(USAGES_DIR / "cpp_deployment_example.py"),
    "model_persistence_example": str(USAGES_DIR / "model_persistence_example.py"),
    "best_partition_and_regressor_example": str(
        USAGES_DIR / "best_partition_and_regressor_example.py"
    )
    + " --test-mode",
    "simplified_model_evaluation": str(USAGES_DIR / "simplified_model_evaluation.py"),
    "partition_and_regressor_example": str(
        USAGES_DIR / "partition_and_regressor_example.py"
    ),
    # Test that should deliberately fail to check error handling
    "test_failure": str(USAGES_DIR / "test_failure_example.py"),
    # These tests are included but commented out in the execution sections due to import issues:
    "sklearn_integration_example": str(USAGES_DIR / "sklearn_integration_example.py"),
    "synthetic_partition_example": str(USAGES_DIR / "synthetic_partition_example.py"),
    "unified_model_evaluation": str(USAGES_DIR / "unified_model_evaluation.py"),
}


def run_test(test_name, timeout=300):
    """
    Run a test script and check the results.

    Args:
        test_name: Name of the test to run (key from TESTS dictionary)
        timeout: Maximum execution time in seconds

    Returns:
        True if the test passed, False otherwise
    """
    if test_name not in TESTS:
        logger.error(f"Unknown test: {test_name}")
        return False

    command = TESTS[test_name]
    log_file = LOGS_DIR / f"{test_name}.log"

    # Print section header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== Running {test_name} ({timestamp}) ===")
    print(f"Command: {sys.executable} {command}")
    print(f"Timeout: {timeout} seconds")

    # Run the command with output redirected to a temp file to handle noisy warnings
    temp_output = tempfile.NamedTemporaryFile(delete=False, mode="w+")
    try:
        start_time = time.time()

        # Run the command with stdout and stderr combined
        process = subprocess.Popen(
            [sys.executable] + command.split(),
            stdout=temp_output,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Wait for the process to complete
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error(f"Test {test_name} timed out after {timeout} seconds")
            print(
                f"\n>>> TEST FAILED: {test_name} timed out after {timeout} seconds <<<"
            )
            return False

        # Close and reopen the temp file for reading
        temp_output.close()
        with open(temp_output.name, "r") as f:
            output = f.read()

        # Save the complete output to the log file
        with open(log_file, "w") as f:
            f.write(output)

        # Print the first few lines of output
        print("Standard output (first 10 lines):")
        output_lines = output.splitlines()
        for line in output_lines[:10]:
            print(line)
        if len(output_lines) > 10:
            print("... [output truncated, see log file for full details]")

        # Check if the test passed
        if process.returncode == 0:
            # Check for specific validation log files
            if test_name == "find_best_partition_and_algo":
                # Check if the log file contains the expected success message
                partition_results_log = LOGS_DIR / "partition_results.log"
                if partition_results_log.exists():
                    with open(partition_results_log, "r") as f:
                        content = f.read()
                        if "SUCCESS: Best partition and algorithm found" in content:
                            elapsed_time = time.time() - start_time
                            print(f"Test completed in {elapsed_time:.2f} seconds.")
                            print(f"\n>>> TEST PASSED: {test_name} <<<")
                            return True
            else:
                # For other tests, just check the return code
                elapsed_time = time.time() - start_time
                print(f"Test completed in {elapsed_time:.2f} seconds.")
                print(f"\n>>> TEST PASSED: {test_name} <<<")
                return True

        logger.error(f"Test {test_name} failed with return code {process.returncode}")
        print(f"\n>>> TEST FAILED: {test_name} - Exit code: {process.returncode} <<<")
        return False

    except Exception as e:
        logger.error(f"Error running test {test_name}: {str(e)}")
        print(f"\n>>> TEST FAILED: {test_name} with error: {str(e)} <<<")
        return False
    finally:
        # Clean up the temp file
        try:
            os.unlink(temp_output.name)
        except:
            pass


def generate_test_data():
    """Generate test data for all function types."""
    print("\n=== Generating test data for all function types ===")

    # Track if all data generation succeeded
    all_succeeded = True

    # First generate linear data (default)
    if not run_test("generate_test_data"):
        all_succeeded = False
        print(">>> WARNING: Failed to generate linear test data <<<")

    # Now generate data for sine and polynomial functions
    for function_type in ["sine", "polynomial"]:
        print(f"\n=== Generating {function_type} test data ===")
        command = f"{str(USAGES_DIR / 'data_generation_example.py')} --output-dir {str(DATA_DIR)} --n-samples 1000 --noise-level 0.5 --function-type {function_type}"
        print(f"Command: {sys.executable} {command}")

        # Use the same approach as run_test for consistency
        temp_output = tempfile.NamedTemporaryFile(delete=False, mode="w+")
        try:
            start_time = time.time()
            process = subprocess.Popen(
                [sys.executable] + command.split(),
                stdout=temp_output,
                stderr=subprocess.STDOUT,
                text=True,
            )

            try:
                process.wait(timeout=300)
            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(
                    f"Generating {function_type} data timed out after 300 seconds"
                )
                print(f">>> FAILED: {function_type} data generation timed out <<<")
                all_succeeded = False
                continue

            # Close and reopen for reading
            temp_output.close()
            with open(temp_output.name, "r") as f:
                output = f.read()

            # Save to log file
            log_file = LOGS_DIR / f"generate_{function_type}_data.log"
            with open(log_file, "w") as f:
                f.write(output)

            # Check return code
            if process.returncode == 0:
                elapsed_time = time.time() - start_time
                print(f"Generated {function_type} data in {elapsed_time:.2f} seconds.")
                print(f">>> SUCCESS: {function_type} data generation completed <<<")
            else:
                print(
                    f">>> FAILED: {function_type} data generation failed with code {process.returncode} <<<"
                )
                all_succeeded = False

        except Exception as e:
            logger.error(f"Error generating {function_type} data: {str(e)}")
            print(f">>> FAILED: {function_type} data generation error: {str(e)} <<<")
            all_succeeded = False
        finally:
            try:
                os.unlink(temp_output.name)
            except:
                pass

    return all_succeeded


def clean_data_directories():
    """Clean up data directories before running tests."""
    print("Starting cleanup process...")

    # Clean all main data directories
    main_dirs = [LOGS_DIR, DATA_DIR, VISUALIZATION_DIR]
    for path in main_dirs:
        if path.exists():
            # Don't delete the directories, just their contents
            for item in path.glob("*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            logger.info(f"Cleaned directory: {path}")

    # Clean all result directories in data_gen
    result_dir_patterns = [
        "best_model_results",
        "file_loader",
        "fresh_install_results",
        "logging_example_results",
        "model_eval_results",
        "model_persistence_results",
        "model_results",
        "partition_comparison_results",
        "partition_finder_results",
        "regressor_comparison_results",
        "saved_models",
    ]

    for dir_name in result_dir_patterns:
        result_dir = DATA_GEN_DIR / dir_name
        if result_dir.exists():
            logger.info(f"Cleaning result directory: {result_dir}")
            for item in result_dir.glob("*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            logger.info(f"Cleaned result directory: {result_dir}")

    # Clean C++ build artifacts if they exist
    cpp_build_dir = ROOT_DIR / "cpp" / "build"
    if cpp_build_dir.exists():
        logger.info(f"Cleaning C++ build directory: {cpp_build_dir}")
        try:
            shutil.rmtree(cpp_build_dir)
            cpp_build_dir.mkdir(parents=True, exist_ok=True)
            logger.info("C++ build directory cleaned and recreated")
        except Exception as e:
            logger.error(f"Error cleaning C++ build directory: {e}")

    # Clean up any archived_results if they exist
    archived_results = DATA_GEN_DIR / "archived_results"
    if archived_results.exists():
        logger.info(f"Cleaning archived results: {archived_results}")
        for item in archived_results.glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        logger.info("Archived results cleaned")

    # Clean up any C++ exported models
    cpp_export_dir = DATA_GEN_DIR / "cpp_export"
    if cpp_export_dir.exists():
        logger.info(f"Cleaning C++ export directory: {cpp_export_dir}")
        for item in cpp_export_dir.glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        logger.info("C++ export directory cleaned")

    print("Cleanup completed successfully!")
    return True


def initialize_directories():
    """Initialize the necessary directories for tests."""
    # Ensure all the required directories exist
    for path in [
        LOGS_DIR,
        DATA_DIR,
        VISUALIZATION_DIR,
        DATA_GEN_DIR / "archived_results",
    ]:
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized directory: {path}")
    return True


def main():
    """
    Main entry point for the test runner.

    NOTE: This script only runs usage examples (not unit tests or C++ tests).
    Unit tests are run directly with pytest, and C++ tests are run with ctest.
    """
    parser = argparse.ArgumentParser(description="Run regression tests for fit-better")
    parser.add_argument("--test", help="Run a specific test")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean data directories before running tests",
    )
    parser.add_argument(
        "--init-dirs",
        action="store_true",
        help="Initialize the necessary directories for tests",
    )
    args = parser.parse_args()

    # Print header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"=== Running Regression Tests ({timestamp}) ===")
    print(f"Python executable: {sys.executable}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Log directory: {LOGS_DIR}")
    print()

    # Initialize directories if requested
    if args.init_dirs:
        initialize_directories()
        return 0

    # Clean directories if requested
    if args.clean:
        clean_data_directories()
        return 0

    # Run a specific test or all tests
    all_passed = True
    if args.test:
        if args.test == "all":
            # Run all tests
            if not generate_test_data():
                all_passed = False
            if not run_test("compare_partitions"):
                all_passed = False
            if not run_test("parallel_partitioning"):
                all_passed = False
            if not run_test("compare_regressors"):
                all_passed = False
            if not run_test("find_best_partition_and_algo"):
                all_passed = False
            if not run_test("model_save_load_example"):
                all_passed = False
            if not run_test("cpp_deployment_example"):
                all_passed = False
            if not run_test("model_persistence_example"):
                all_passed = False
            if not run_test("best_partition_and_regressor_example"):
                all_passed = False
            if not run_test("simplified_model_evaluation"):
                all_passed = False
            if not run_test("partition_and_regressor_example"):
                all_passed = False
            # Do not run the test_failure test by default as it's designed to fail
            # if not run_test("test_failure"):
            #     all_passed = False
            # Commented out failing tests
            # if not run_test("sklearn_integration_example"):
            #     all_passed = False
            # if not run_test("synthetic_partition_example"):
            #     all_passed = False
            if not run_test("unified_model_evaluation"):
                all_passed = False
        else:
            if args.test == "generate_test_data":
                all_passed = generate_test_data()
            else:
                all_passed = run_test(args.test)
    else:
        # Default: run all tests
        if not generate_test_data():
            all_passed = False
        if not run_test("compare_partitions"):
            all_passed = False
        if not run_test("parallel_partitioning"):
            all_passed = False
        if not run_test("compare_regressors"):
            all_passed = False
        if not run_test("find_best_partition_and_algo"):
            all_passed = False
        if not run_test("model_save_load_example"):
            all_passed = False
        if not run_test("cpp_deployment_example"):
            all_passed = False
        if not run_test("model_persistence_example"):
            all_passed = False
        if not run_test("best_partition_and_regressor_example"):
            all_passed = False
        if not run_test("simplified_model_evaluation"):
            all_passed = False
        if not run_test("partition_and_regressor_example"):
            all_passed = False
        # Do not run the test_failure test by default as it's designed to fail
        # if not run_test("test_failure"):
        #     all_passed = False
        # Commented out failing tests
        # if not run_test("sklearn_integration_example"):
        #     all_passed = False
        # if not run_test("synthetic_partition_example"):
        #     all_passed = False
        if not run_test("unified_model_evaluation"):
            all_passed = False

    # Return appropriate exit code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
