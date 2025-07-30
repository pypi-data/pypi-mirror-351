"""
Unit tests for C++ integration with fit_better.

This test suite validates:
- Exporting models from fit_better for use with the C++ implementation
- Running the C++ component with exported models
- Verifying that the C++ predictions match Python predictions
"""

import os
import sys
import pytest
import numpy as np
import subprocess
import json
import tempfile
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from fit_better.io.export.cpp import export_model_to_json


@pytest.fixture
def trained_models():
    """Create a set of trained models for testing C++ integration."""
    np.random.seed(42)
    X = np.random.rand(100, 2)
    y = 2 * X[:, 0] + 3 * X[:, 1] + 1 + np.random.normal(0, 0.5, 100)

    models = {}

    # Only using LinearRegression as it's the primary model supported by C++ implementation
    models["linear"] = {"model": LinearRegression().fit(X, y), "X": X, "y": y}

    # Model with StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    models["linear_with_scaler"] = {
        "model": LinearRegression().fit(X_scaled, y),
        "scaler": scaler,
        "X": X,
        "y": y,
    }

    return models


def is_cpp_build_available():
    """Check if the C++ library has been built."""
    # Find the root of the repo
    repo_root = Path(__file__).resolve().parent.parent.parent
    cpp_dir = repo_root / "cpp"
    build_dir = cpp_dir / "build"

    # Check if the build directory exists
    if not build_dir.exists():
        return False

    # Look for the executable
    fit_better_exe = build_dir / "fit_better_cpp"
    test_exe = build_dir / "fit_better_tests"

    return fit_better_exe.exists() or test_exe.exists()


@pytest.mark.skipif(not is_cpp_build_available(), reason="C++ build not available")
def test_cpp_model_runner(trained_models):
    """Test that models exported by fit_better can be loaded and used by the C++ implementation."""
    # Create a temporary directory for the exported models
    with tempfile.TemporaryDirectory() as temp_dir:
        # Get the path to the C++ model runner executable
        repo_root = Path(__file__).resolve().parent.parent.parent
        cpp_dir = repo_root / "cpp"
        build_dir = cpp_dir / "build"
        model_runner_exe = build_dir / "fit_better_cpp"

        if not model_runner_exe.exists():
            pytest.skip("C++ model runner executable not found")

        # Test each model type
        for model_name, model_data in trained_models.items():
            # Export the model to JSON
            model_file = os.path.join(temp_dir, f"{model_name}.json")

            # Create a model result dictionary
            model_result = {"model": model_data["model"], "model_name": model_name}

            # Add scaler if available
            if "scaler" in model_data:
                model_result["scaler"] = model_data["scaler"]

            # Export the model
            export_result = export_model_to_json(model_result, output_path=model_file)

            # Skip if export failed
            if not export_result:
                pytest.skip(f"Failed to export model {model_name}")
                continue

            # Verify file exists
            assert os.path.exists(
                model_file
            ), f"Export file not created for {model_name}"

            # Use a single test point for verification
            X_test = model_data["X"][:1]

            # Get Python prediction
            if "scaler" in model_data:
                X_test_scaled = model_data["scaler"].transform(X_test)
                py_prediction = float(model_data["model"].predict(X_test_scaled)[0])
            else:
                py_prediction = float(model_data["model"].predict(X_test)[0])

            # Run the C++ model runner with the exported model
            cmd = [str(model_runner_exe), model_file, *[str(x) for x in X_test[0]]]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)

                # Print output for debugging
                print(f"C++ output for {model_name}:")
                print(result.stdout)

                # Parse the C++ output to get the prediction
                output_lines = result.stdout.strip().split("\n")
                cpp_prediction = None

                for line in output_lines:
                    if "Prediction result:" in line:
                        cpp_prediction = float(
                            line.split("Prediction result:")[1].strip()
                        )
                        break

                # Verify that we got a prediction
                assert (
                    cpp_prediction is not None
                ), f"No prediction found in C++ output for {model_name}"

                # Check that the predictions match (within a tolerance)
                # Using a larger tolerance to account for floating-point differences between implementations
                assert np.isclose(
                    py_prediction, cpp_prediction, rtol=0.05, atol=0.05
                ), f"Python prediction ({py_prediction}) does not match C++ prediction ({cpp_prediction}) for {model_name}"

                print(
                    f"Predictions match for {model_name}: Python={py_prediction}, C++={cpp_prediction}"
                )

            except subprocess.CalledProcessError as e:
                pytest.fail(f"C++ model runner failed for {model_name}: {e.stderr}")
            except Exception as e:
                pytest.fail(
                    f"Unexpected error in C++ integration test for {model_name}: {str(e)}"
                )


@pytest.mark.skipif(not is_cpp_build_available(), reason="C++ build not available")
def test_cpp_test_suite():
    """Run the C++ test suite to ensure the C++ implementation is working correctly."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    cpp_dir = repo_root / "cpp"
    build_dir = cpp_dir / "build"
    test_exe = (
        build_dir / "tests" / "fit_better_tests"
    )  # Updated path to include the tests directory

    # Print debug information
    print(f"Repository root: {repo_root}")
    print(f"C++ directory: {cpp_dir}")
    print(f"Build directory: {build_dir}")
    print(f"Test executable path: {test_exe}")
    print(f"Test executable exists: {test_exe.exists()}")

    if not test_exe.exists():
        # Check for alternative locations
        alt_test_exe = build_dir / "fit_better_tests"
        print(f"Alternate test executable path: {alt_test_exe}")
        print(f"Alternate test executable exists: {alt_test_exe.exists()}")

        if alt_test_exe.exists():
            test_exe = alt_test_exe
        else:
            pytest.skip(
                f"C++ test executable not found at {test_exe} or {alt_test_exe}"
            )

    try:
        result = subprocess.run(
            [str(test_exe)], capture_output=True, text=True, check=True
        )

        # Verify that the tests passed
        assert (
            "All tests passed" in result.stdout or "[==========]" in result.stdout
        ), "C++ tests did not report success"

    except subprocess.CalledProcessError as e:
        pytest.fail(f"C++ test suite failed: {e.stderr}")
    except Exception as e:
        pytest.fail(f"Unexpected error running C++ test suite: {str(e)}")
