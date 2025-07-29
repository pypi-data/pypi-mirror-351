#!/usr/bin/env python3
"""
Verify that test_all.py properly handles test failures and returns correct exit codes.
"""
import subprocess
import sys
import os
from pathlib import Path
import time


def main():
    """Run a deliberately failing test and check if it's handled correctly."""
    # Create a log file
    log_file = Path(__file__).parent / "verification_results.log"

    with open(log_file, "w") as f:
        f.write("=== Testing failure handling in test_all.py ===\n\n")

        # Set environment
        os.chdir(Path(__file__).parent)
        env = os.environ.copy()
        env["PYTHONPATH"] = (
            str(Path(__file__).parent.parent) + ":" + env.get("PYTHONPATH", "")
        )

        # Run the test_failure test
        cmd = [sys.executable, "test_all.py", "--test", "test_failure"]
        f.write(f"Running command: {' '.join(cmd)}\n\n")

        start_time = time.time()
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        duration = time.time() - start_time

        # Log command output
        f.write("=== Command Output ===\n")
        f.write(result.stdout)
        f.write("\n")

        if result.stderr:
            f.write("=== Error Output ===\n")
            f.write(result.stderr)
            f.write("\n")

        # Check return code
        f.write(f"=== Result ===\n")
        f.write(f"Return code: {result.returncode}\n")
        f.write(f"Duration: {duration:.2f} seconds\n\n")

        success = result.returncode != 0
        if success:
            f.write(
                "SUCCESS: test_all.py correctly returned non-zero exit code for failing test\n"
            )
        else:
            f.write("FAILURE: test_all.py did not return error code for failing test\n")

        # Also run a known-good test for comparison
        f.write("\n\n=== COMPARISON: Testing passing test handling ===\n\n")
        cmd = [sys.executable, "test_all.py", "--test", "model_save_load_example"]
        f.write(f"Running command: {' '.join(cmd)}\n\n")

        start_time = time.time()
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        duration = time.time() - start_time

        # Log basic info without full output (would be too large)
        f.write(f"Return code: {result.returncode}\n")
        f.write(f"Duration: {duration:.2f} seconds\n\n")

        success_passing = result.returncode == 0
        if success_passing:
            f.write(
                "SUCCESS: test_all.py correctly returned zero exit code for passing test\n"
            )
        else:
            f.write(
                "FAILURE: test_all.py returned non-zero exit code for passing test\n"
            )

        # Overall conclusion
        f.write("\n=== OVERALL CONCLUSION ===\n")
        if success and success_passing:
            f.write(
                "✓ PASSED: The testing framework correctly handles both passing and failing tests.\n"
            )
            conclusion = 0
        else:
            f.write(
                "✗ FAILED: The testing framework does not correctly handle test results.\n"
            )
            f.write(
                f"  - Failing test handled correctly: {'Yes' if success else 'No'}\n"
            )
            f.write(
                f"  - Passing test handled correctly: {'Yes' if success_passing else 'No'}\n"
            )
            conclusion = 1

    # Print a brief summary to console
    print(f"Verification complete. Results written to {log_file}")

    with open(log_file, "r") as f:
        conclusion_lines = f.readlines()[-5:]
        for line in conclusion_lines:
            print(line.strip())

    return conclusion


if __name__ == "__main__":
    sys.exit(main())
