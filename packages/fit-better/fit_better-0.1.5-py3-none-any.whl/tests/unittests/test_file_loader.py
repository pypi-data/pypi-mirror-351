#!/usr/bin/env python
"""
Unit tests for the file_loader module.

This test suite validates:
- Loading data from various file formats
- Loading paired X/y data
- Handling CSV files with headers
- Ensuring correct array shapes
- Using the data cache
"""

import os
import sys
import pytest
import tempfile
import numpy as np
import time
import random
import pandas as pd
from pathlib import Path

# Add parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import modules to test
from fit_better.data.file_loader import (
    load_file_to_array,
    load_data_from_files,
    match_xy_by_key,
    load_dataset,
    save_data_to_files,
    enable_cache,
    clear_cache,
)


@pytest.fixture
def sample_data():
    """Create sample data for testing file operations."""
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
    y = np.array([10, 20, 30, 40])
    # Sample names for string-based key testing
    names = ["Alice", "Bob", "Charlie", "Diana"]
    return X, y, names


@pytest.fixture
def sample_csv_files(sample_data):
    """Create sample CSV files for testing file operations."""
    X, y, names = sample_data

    # Use the specified directory for test data
    test_data_dir = "/mnt/d/repos/fit-better/tests/data_gen/file_loader"
    os.makedirs(test_data_dir, exist_ok=True)

    # Create file pairs with both _example and _test suffixes
    files_dict = {}

    # List of file configurations
    file_configs = [
        (
            "x_data",
            "feature1,feature2,feature3",
            lambda i, row: f"{row[0]},{row[1]},{row[2]}",
        ),
        ("y_data", "target", lambda i, val: f"{val}"),
        (
            "x_key_data",
            "id,feature1,feature2",
            lambda i, row: f"{i+1},{row[0]},{row[1]}",
        ),
        ("y_key_data", "id,target", lambda i, val: f"{i+1},{val}"),
        (
            "x_string_key_data",
            "name,feature1,feature2",
            lambda i, row: f"{names[i]},{row[0]},{row[1]}",
        ),
        ("y_string_key_data", "name,target", lambda i, val: f"{names[i]},{val}"),
        (
            "combined_data",
            "feature1,feature2,feature3,target",
            lambda i, _: f"{X[i][0]},{X[i][1]},{X[i][2]},{y[i]}",
        ),
    ]

    for file_base, header, row_formatter in file_configs:
        for suffix in ["_example", "_test"]:
            filename = f"{file_base}{suffix}.csv"
            filepath = os.path.join(test_data_dir, filename)

            with open(filepath, "w") as f:
                f.write(header + "\n")

                if file_base == "x_data":
                    for row in X:
                        f.write(row_formatter(None, row) + "\n")
                elif file_base == "y_data":
                    for val in y:
                        f.write(row_formatter(None, val) + "\n")
                elif file_base == "x_key_data":
                    for i, row in enumerate(X[:, :2]):
                        f.write(row_formatter(i, row) + "\n")
                elif file_base == "y_key_data":
                    for i, val in enumerate(y):
                        f.write(row_formatter(i, val) + "\n")
                elif file_base == "x_string_key_data":
                    for i, row in enumerate(X[:, :2]):
                        f.write(row_formatter(i, row) + "\n")
                elif file_base == "y_string_key_data":
                    for i, val in enumerate(y):
                        f.write(row_formatter(i, val) + "\n")
                elif file_base == "combined_data":
                    for i in range(len(X)):
                        f.write(row_formatter(i, None) + "\n")

            # Store both example and test versions
            files_dict[f"{file_base}{suffix}"] = filepath

    # Return dictionary with both example and test file paths
    # For backward compatibility, also include the original keys pointing to _test versions
    return {
        "x_file": files_dict["x_data_test"],
        "y_file": files_dict["y_data_test"],
        "x_key_file": files_dict["x_key_data_test"],
        "y_key_file": files_dict["y_key_data_test"],
        "x_string_key_file": files_dict["x_string_key_data_test"],
        "y_string_key_file": files_dict["y_string_key_data_test"],
        "combined_file": files_dict["combined_data_test"],
        "dir": test_data_dir,
        # Include all generated files for more flexibility
        **files_dict,
    }


class TestFileLoader:
    """Tests for the file_loader module."""

    def test_load_file_to_array(self, sample_csv_files):
        """Test loading a single file into a numpy array."""
        # Load X data with header
        X_loaded = load_file_to_array(
            sample_csv_files["x_file"], delimiter=",", header="infer"
        )

        assert isinstance(X_loaded, np.ndarray)
        assert X_loaded.shape[1] == 3  # 3 features
        assert X_loaded.shape[0] == 4  # 4 samples

        # Load y data with header
        y_loaded = load_file_to_array(
            sample_csv_files["y_file"], delimiter=",", header="infer"
        )

        assert isinstance(y_loaded, np.ndarray)
        assert y_loaded.shape[0] == 4  # 4 samples

        # Load specific column by index
        feature2 = load_file_to_array(
            sample_csv_files["x_file"], delimiter=",", header="infer", target_column=1
        )

        assert feature2.shape == (4,)

        # Load specific column by name
        feature1 = load_file_to_array(
            sample_csv_files["x_file"],
            delimiter=",",
            header="infer",
            target_column="feature1",
        )

        assert feature1.shape == (4,)

    def test_load_data_from_files(self, sample_csv_files):
        """Test loading X and y data from separate files."""
        X_train, y_train, X_test, y_test = load_data_from_files(
            input_dir=sample_csv_files["dir"],
            x_train_file="x_data_test.csv",
            y_train_file="y_data_test.csv",
            x_test_file="x_data_test.csv",  # Using same file for test data in this example
            y_test_file="y_data_test.csv",
            delimiter=",",
        )

        assert X_train.shape == (4, 3)
        assert y_train.shape == (4,)
        assert X_test.shape == (4, 3)
        assert y_test.shape == (4,)

    def test_example_files_exist(self, sample_csv_files):
        """Test that example files are properly created alongside test files."""
        expected_example_files = [
            "x_data_example.csv",
            "y_data_example.csv",
            "x_key_data_example.csv",
            "y_key_data_example.csv",
            "combined_data_example.csv",
        ]

        for filename in expected_example_files:
            filepath = os.path.join(sample_csv_files["dir"], filename)
            assert os.path.exists(filepath), f"Example file {filename} should exist"

        # Test that example files have the same structure as test files
        X_example = load_file_to_array(
            sample_csv_files["x_data_example"], delimiter=",", header="infer"
        )
        X_test = load_file_to_array(
            sample_csv_files["x_file"], delimiter=",", header="infer"
        )

        np.testing.assert_array_equal(X_example, X_test)

    def test_match_xy_by_key(self, sample_csv_files):
        """Test matching X and y based on key columns."""
        X, y, keys = match_xy_by_key(
            X_path=sample_csv_files["x_key_data_test"],
            y_path=sample_csv_files["y_key_data_test"],
            x_key_column="id",
            y_key_column="id",
            x_value_columns=["feature1", "feature2"],
            y_value_column="target",
            delimiter=",",
        )

        assert X.shape == (4, 2)  # 4 samples, 2 features (excluding key)
        assert y.shape == (4,)
        assert keys.shape == (4,)  # 4 matched keys
        # Keys should be sorted: [1, 2, 3, 4]
        assert list(keys) == ["1", "2", "3", "4"]

        # Test with different key ordering by creating files with shuffled keys
        test_data_dir = sample_csv_files["dir"]

        # Create shuffled key files
        x_shuffled = os.path.join(test_data_dir, "x_shuffled.csv")
        with open(x_shuffled, "w") as f:
            f.write("id,feature1,feature2\n")
            f.write("3,7,8\n")
            f.write("1,1,2\n")
            f.write("4,10,11\n")
            f.write("2,4,5\n")

        y_shuffled = os.path.join(test_data_dir, "y_shuffled.csv")
        with open(y_shuffled, "w") as f:
            f.write("id,target\n")
            f.write("2,20\n")
            f.write("4,40\n")
            f.write("1,10\n")
            f.write("3,30\n")

        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_shuffled,
            y_path=y_shuffled,
            x_key_column="id",
            y_key_column="id",
            delimiter=",",
        )

        assert X_matched.shape[0] == 4
        assert y_matched.shape[0] == 4

        # First row should be id=1
        assert X_matched[0][0] == 1  # feature1 value for id=1

    def test_match_xy_by_string_key(self, sample_csv_files):
        """Test matching X and y based on string key columns (name-based matching)."""
        X, y, keys = match_xy_by_key(
            X_path=sample_csv_files["x_string_key_data_test"],
            y_path=sample_csv_files["y_string_key_data_test"],
            x_key_column="name",
            y_key_column="name",
            x_value_columns=["feature1", "feature2"],
            y_value_column="target",
            delimiter=",",
        )

        assert X.shape == (4, 2)  # 4 samples, 2 features (excluding key)
        assert y.shape == (4,)

        # Test with shuffled string keys to validate optimized algorithm
        test_data_dir = sample_csv_files["dir"]

        # Create shuffled key files with string names
        x_shuffled = os.path.join(test_data_dir, "x_string_shuffled.csv")
        with open(x_shuffled, "w") as f:
            f.write("name,feature1,feature2\n")
            f.write("Charlie,7,8\n")
            f.write("Alice,1,2\n")
            f.write("Diana,10,11\n")
            f.write("Bob,4,5\n")

        y_shuffled = os.path.join(test_data_dir, "y_string_shuffled.csv")
        with open(y_shuffled, "w") as f:
            f.write("name,target\n")
            f.write("Bob,20\n")
            f.write("Diana,40\n")
            f.write("Alice,10\n")
            f.write("Charlie,30\n")

        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_shuffled,
            y_path=y_shuffled,
            x_key_column="name",
            y_key_column="name",
            delimiter=",",
        )

        assert X_matched.shape[0] == 4
        assert y_matched.shape[0] == 4

        # First row should match Alice (first row in x_shuffled after reordering)
        # With the optimized algorithm, order is preserved for matched keys
        assert X_matched[0][0] == 1  # feature1 value for Alice

    def test_match_xy_by_key_performance(self, sample_csv_files):
        """Test performance of key matching with larger dataset including mismatched keys."""
        # Use the designated test data directory
        test_data_dir = sample_csv_files["dir"]

        # Create larger test files (1000 rows) to test optimization
        x_large = os.path.join(test_data_dir, "x_large.csv")
        y_large = os.path.join(test_data_dir, "y_large.csv")

        # Create names with some mismatches
        x_names = [f"Person_{i:04d}" for i in range(1000)]  # 1000 names in X
        # Y will have 800 matching names + 200 unique names (total 1000)
        y_matching_names = x_names[:800]  # First 800 match with X
        y_unique_names = [f"Unique_{i:04d}" for i in range(200)]  # 200 unique to Y
        y_names = y_matching_names + y_unique_names

        with open(x_large, "w") as f:
            f.write("name,feature1,feature2\n")
            for i, name in enumerate(x_names):
                f.write(f"{name},{i},{i*2}\n")

        with open(y_large, "w") as f:
            f.write("name,target\n")
            # Shuffle the order to test matching performance
            shuffled_y_names = y_names.copy()
            random.shuffle(shuffled_y_names)
            for name in shuffled_y_names:
                if name.startswith("Person_"):
                    # Extract original index for target value
                    orig_idx = int(name.split("_")[1])
                    f.write(f"{name},{orig_idx * 10}\n")
                else:
                    # Unique names get arbitrary target values
                    unique_idx = int(name.split("_")[1])
                    f.write(f"{name},{unique_idx + 9000}\n")

        # Time the operation
        start_time = time.time()
        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_large,
            y_path=y_large,
            x_key_column="name",
            y_key_column="name",
            delimiter=",",
        )
        end_time = time.time()

        # Should match 800 rows (only the overlapping keys)
        # X has 1000 keys, Y has 800 matching + 200 unique = 800 matches
        assert (
            X_matched.shape[0] == 800
        ), f"Expected 800 matches, got {X_matched.shape[0]}"
        assert (
            y_matched.shape[0] == 800
        ), f"Expected 800 matches, got {y_matched.shape[0]}"

        # Should complete in reasonable time (much less than 1 second for 1000 rows)
        assert (
            end_time - start_time < 1.0
        ), f"Key matching took too long: {end_time - start_time:.2f} seconds"

        print(
            f"Performance test: Matched {X_matched.shape[0]} out of 1000 X keys and 1000 Y keys"
        )
        print(f"Execution time: {end_time - start_time:.3f} seconds")
        print(f"X keys without matches: 200 (Person_0800 to Person_0999)")
        print(f"Y keys without matches: 200 (Unique_0000 to Unique_0199)")

    def test_load_dataset(self, sample_csv_files):
        """Test loading a dataset from a single file with automatic splitting."""
        # Test with default test split
        X_train, X_test, y_train, y_test = load_dataset(
            file_path=sample_csv_files["combined_data_test"],
            target_column="target",
            test_size=0.5,  # Use 50% split for predictable results with small test data
            random_state=42,
        )

        assert X_train.shape[1] == 3  # 3 features
        assert X_test.shape[1] == 3
        assert X_train.shape[0] + X_test.shape[0] == 4  # 4 total samples
        assert len(y_train) + len(y_test) == 4

        # Test with validation split
        X_train, X_val, X_test, y_train, y_val, y_test = load_dataset(
            file_path=sample_csv_files["combined_data_test"],
            target_column="target",
            test_size=0.25,
            val_size=0.25,
            random_state=42,
        )

        assert X_train.shape[0] + X_val.shape[0] + X_test.shape[0] == 4

    def test_save_data_to_files(self, sample_data):
        """Test saving data to files in different formats."""
        X, y, _ = sample_data
        output_dir = "/mnt/d/repos/fit-better/tests/data_gen/file_loader/output"
        os.makedirs(output_dir, exist_ok=True)

        # Test saving in numpy format
        save_data_to_files(
            output_dir=output_dir,
            X_train=X,
            y_train=y,
            X_test=X,
            y_test=y,
            format="npy",
        )

        assert os.path.exists(os.path.join(output_dir, "X_train.npy"))
        assert os.path.exists(os.path.join(output_dir, "y_train.npy"))
        assert os.path.exists(os.path.join(output_dir, "X_test.npy"))
        assert os.path.exists(os.path.join(output_dir, "y_test.npy"))

        # Test saving in CSV format
        save_data_to_files(
            output_dir=output_dir,
            X_train=X,
            y_train=y,
            X_test=X,
            y_test=y,
            format="csv",
            x_train_name="X_train_csv",
            y_train_name="y_train_csv",
        )

        assert os.path.exists(os.path.join(output_dir, "X_train_csv.csv"))
        assert os.path.exists(os.path.join(output_dir, "y_train_csv.csv"))

    def test_cache_functionality(self, sample_csv_files):
        """Test the data caching functionality."""
        # Enable caching
        enable_cache(True)

        # First load should cache the data
        start_time = time.time()
        X1 = load_file_to_array(sample_csv_files["x_data_test"], delimiter=",")
        first_load_time = time.time() - start_time

        # Second load should be faster due to cache
        start_time = time.time()
        X2 = load_file_to_array(sample_csv_files["x_data_test"], delimiter=",")
        second_load_time = time.time() - start_time

        # Test cache correctness
        np.testing.assert_array_equal(X1, X2)

        # Clear cache
        clear_cache()

        # Load again after clearing cache
        start_time = time.time()
        X3 = load_file_to_array(sample_csv_files["x_data_test"], delimiter=",")
        third_load_time = time.time() - start_time

        # Disable cache
        enable_cache(False)

        # Load with cache disabled
        X4 = load_file_to_array(sample_csv_files["x_data_test"], delimiter=",")

        # Verify data correctness
        np.testing.assert_array_equal(X1, X3)
        np.testing.assert_array_equal(X1, X4)

    def test_match_xy_by_string_key_with_mismatches(self, sample_csv_files):
        """Test matching X and y with string keys that include mismatched rows."""
        test_data_dir = sample_csv_files["dir"]

        # Create X file with some keys that won't match in Y
        x_mismatch = os.path.join(test_data_dir, "x_mismatch.csv")
        with open(x_mismatch, "w") as f:
            f.write("name,feature1,feature2\n")
            f.write("Alice,1,2\n")  # Will match
            f.write("Bob,4,5\n")  # Will match
            f.write("Charlie,7,8\n")  # Will match
            f.write("David,10,11\n")  # No match in Y (unique to X)
            f.write("Eve,13,14\n")  # No match in Y (unique to X)

        # Create Y file with some keys that won't match in X
        y_mismatch = os.path.join(test_data_dir, "y_mismatch.csv")
        with open(y_mismatch, "w") as f:
            f.write("name,target\n")
            f.write("Alice,10\n")  # Will match
            f.write("Bob,20\n")  # Will match
            f.write("Charlie,30\n")  # Will match
            f.write("Frank,40\n")  # No match in X (unique to Y)
            f.write("Grace,50\n")  # No match in X (unique to Y)

        # Test the matching with mismatched keys
        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_mismatch,
            y_path=y_mismatch,
            x_key_column="name",
            y_key_column="name",
            x_value_columns=["feature1", "feature2"],
            y_value_column="target",
            delimiter=",",
        )

        # Should only match the 3 common keys: Alice, Bob, Charlie
        assert X_matched.shape[0] == 3, f"Expected 3 matches, got {X_matched.shape[0]}"
        assert y_matched.shape[0] == 3, f"Expected 3 matches, got {y_matched.shape[0]}"
        assert X_matched.shape[1] == 2, "X should have 2 features"

        # Verify the matched data is correct
        # The order should preserve X file order for matched keys
        expected_X = np.array(
            [[1, 2], [4, 5], [7, 8]], dtype=float
        )  # Alice, Bob, Charlie
        expected_y = np.array([10, 20, 30], dtype=float)  # Alice, Bob, Charlie targets

        np.testing.assert_array_equal(X_matched, expected_X)
        np.testing.assert_array_equal(y_matched, expected_y)

        print(f"Successfully matched {X_matched.shape[0]} out of 5 X keys and 5 Y keys")
        print(f"X keys without matches: David, Eve")
        print(f"Y keys without matches: Frank, Grace")

    def test_csv_loading_dimensions(self, sample_csv_files):
        """Test CSV loading dimensions to identify shape mismatch issues."""
        test_data_dir = sample_csv_files["dir"]

        # Test the specific files mentioned in the issue
        x_shuffled = os.path.join(test_data_dir, "x_shuffled.csv")
        y_shuffled = os.path.join(test_data_dir, "y_shuffled.csv")

        # Load files individually using load_file_to_array
        print("Loading individual files with load_file_to_array:")
        x_raw = load_file_to_array(x_shuffled, delimiter=",", header="infer")
        y_raw = load_file_to_array(y_shuffled, delimiter=",", header="infer")

        print(f"x_raw shape: {x_raw.shape}")
        print(f"y_raw shape: {y_raw.shape}")
        print(f"x_raw content:\n{x_raw}")
        print(f"y_raw content:\n{y_raw}")

        # Test load_data_from_files function
        print("\nLoading with load_data_from_files:")
        x, y, x1, y1 = load_data_from_files(
            test_data_dir,
            "x_shuffled.csv",
            "y_shuffled.csv",
            "x_shuffled.csv",
            "y_shuffled.csv",
        )

        print(f"x shape: {x.shape}")
        print(f"y shape: {y.shape}")
        print(f"x1 shape: {x1.shape}")
        print(f"y1 shape: {y1.shape}")

        # Expected behavior:
        # - x_raw should be (4, 3) with columns [id, feature1, feature2]
        # - y_raw should be (4, 2) with columns [id, target]
        # - After load_data_from_files, y should be (4,) containing only target values

        assert x_raw.shape == (4, 3), f"Expected x_raw shape (4, 3), got {x_raw.shape}"
        assert y_raw.shape == (4, 2), f"Expected y_raw shape (4, 2), got {y_raw.shape}"

        # The issue: y should be (4,) not (8,)
        # This suggests ensure_array_shapes is incorrectly flattening the 2D array
        assert y.shape == (4,), f"Expected y shape (4,), got {y.shape}"

        print("CSV loading dimensions test passed!")

    def test_ensure_array_shapes_behavior(self, sample_csv_files):
        """Test the ensure_array_shapes function behavior with 2D y data."""
        from fit_better.data.file_loader import ensure_array_shapes

        # Create test data similar to what comes from CSV loading
        X_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])  # (4, 3)
        y_2d = np.array(
            [[1, 10], [2, 20], [3, 30], [4, 40]]
        )  # (4, 2) - id, target columns

        print(f"Before ensure_array_shapes:")
        print(f"X_2d shape: {X_2d.shape}")
        print(f"y_2d shape: {y_2d.shape}")

        X_shaped, y_shaped = ensure_array_shapes(X_2d, y_2d)

        print(f"After ensure_array_shapes:")
        print(f"X_shaped shape: {X_shaped.shape}")
        print(f"y_shaped shape: {y_shaped.shape}")
        print(f"y_shaped content: {y_shaped}")

        # The problem: ensure_array_shapes flattens y_2d from (4,2) to (8,)
        # This is wrong when y contains multiple columns (id + target)
        assert X_shaped.shape == (4, 3), f"X should remain (4, 3), got {X_shaped.shape}"

        # This assertion will likely fail, showing the bug
        # y_shaped should be (4,) if we only want the target column
        # but ensure_array_shapes doesn't know which column is the target
        print(f"ensure_array_shapes converted y from {y_2d.shape} to {y_shaped.shape}")

        if y_shaped.shape == (8,):
            print("BUG CONFIRMED: ensure_array_shapes incorrectly flattened y_2d to 1D")
            print("This explains why y.shape is (8,) instead of (4,)")

        print("ensure_array_shapes behavior test completed!")

    def test_match_xy_by_key_default_behavior(self, sample_csv_files):
        """Test that match_xy_by_key uses first column as key by default and only returns matched rows."""
        test_data_dir = sample_csv_files["dir"]

        # Use the existing shuffled files which have first column as id
        x_shuffled = os.path.join(test_data_dir, "x_shuffled.csv")
        y_shuffled = os.path.join(test_data_dir, "y_shuffled.csv")

        print("Testing default key matching behavior...")

        # Test with default parameters (should use first column as key)
        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_shuffled,
            y_path=y_shuffled,
            # Using defaults: x_key_column=0, y_key_column=0
            delimiter=",",
            header="infer",
        )

        print(f"X_matched shape: {X_matched.shape}")
        print(f"y_matched shape: {y_matched.shape}")
        print(f"X_matched content:\n{X_matched}")
        print(f"y_matched content: {y_matched}")

        # Should have 4 matched rows (all ids 1,2,3,4 exist in both files)
        assert (
            X_matched.shape[0] == 4
        ), f"Expected 4 matched rows, got {X_matched.shape[0]}"
        assert (
            y_matched.shape[0] == 4
        ), f"Expected 4 matched rows, got {y_matched.shape[0]}"

        # X should have 2 feature columns (excluding the key column)
        assert (
            X_matched.shape[1] == 2
        ), f"Expected 2 feature columns in X, got {X_matched.shape[1]}"

        # y should be 1D with target values only
        assert y_matched.ndim == 1, f"Expected y to be 1D, got {y_matched.ndim}D"

        # Verify the content is correct (sorted by key)
        # After sorting by key: id=1,2,3,4
        expected_X = np.array([[1, 2], [4, 5], [7, 8], [10, 11]], dtype=float)
        expected_y = np.array([10, 20, 30, 40], dtype=float)

        np.testing.assert_array_equal(X_matched, expected_X)
        np.testing.assert_array_equal(y_matched, expected_y)

        print("Default key matching behavior test passed!")

    def test_match_xy_by_key_with_missing_keys(self, sample_csv_files):
        """Test key matching when some keys don't have matches."""
        test_data_dir = sample_csv_files["dir"]

        # Create files with some missing keys
        x_partial = os.path.join(test_data_dir, "x_partial.csv")
        with open(x_partial, "w") as f:
            f.write("id,feature1,feature2\n")
            f.write("1,1,2\n")  # Will match
            f.write("2,4,5\n")  # Will match
            f.write("5,13,14\n")  # No match in y
            f.write("6,16,17\n")  # No match in y

        y_partial = os.path.join(test_data_dir, "y_partial.csv")
        with open(y_partial, "w") as f:
            f.write("id,target\n")
            f.write("1,10\n")  # Will match
            f.write("2,20\n")  # Will match
            f.write("7,70\n")  # No match in X
            f.write("8,80\n")  # No match in X

        # Test matching - should only return the 2 common keys (1 and 2)
        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_partial, y_path=y_partial, delimiter=",", header="infer"
        )

        print(f"Partial matching - X_matched shape: {X_matched.shape}")
        print(f"Partial matching - y_matched shape: {y_matched.shape}")
        print(f"X_matched content:\n{X_matched}")
        print(f"y_matched content: {y_matched}")

        # Should only have 2 matched rows (ids 1 and 2)
        assert (
            X_matched.shape[0] == 2
        ), f"Expected 2 matched rows, got {X_matched.shape[0]}"
        assert (
            y_matched.shape[0] == 2
        ), f"Expected 2 matched rows, got {y_matched.shape[0]}"

        # Verify correct content (sorted by key: id=1,2)
        expected_X = np.array([[1, 2], [4, 5]], dtype=float)
        expected_y = np.array([10, 20], dtype=float)

        np.testing.assert_array_equal(X_matched, expected_X)
        np.testing.assert_array_equal(y_matched, expected_y)

        print("Partial key matching test passed!")

    def test_key_matching_basic_functionality(self, sample_csv_files):
        """Test basic key matching functionality with 3 return values."""
        test_data_dir = sample_csv_files["dir"]

        # Create shuffled test files
        x_shuffled = os.path.join(test_data_dir, "x_shuffled_basic.csv")
        y_shuffled = os.path.join(test_data_dir, "y_shuffled_basic.csv")

        with open(x_shuffled, "w") as f:
            f.write("id,feature1,feature2\n")
            f.write("3,7,8\n")
            f.write("1,1,2\n")
            f.write("4,10,11\n")
            f.write("2,4,5\n")

        with open(y_shuffled, "w") as f:
            f.write("id,target1,target2\n")
            f.write("2,20,21\n")
            f.write("4,40,41\n")
            f.write("1,10,11\n")
            f.write("3,30,31\n")

        # Test with explicit key column specification
        X, y, keys = match_xy_by_key(
            X_path=x_shuffled, y_path=y_shuffled, x_key_column="id", y_key_column="id"
        )

        assert X.shape[0] == 4, f"Expected 4 rows, got {X.shape[0]}"
        assert y.shape[0] == 4, f"Expected 4 rows, got {y.shape[0]}"
        assert keys.shape[0] == 4, f"Expected 4 keys, got {keys.shape[0]}"

        # Verify keys are properly returned
        expected_keys = ["1", "2", "3", "4"]  # Should be sorted
        actual_keys = sorted(list(keys))
        assert (
            actual_keys == expected_keys
        ), f"Expected keys {expected_keys}, got {actual_keys}"

    def test_key_matching_with_string_mismatches(self, sample_csv_files):
        """Test string key matching with rows that don't match between files."""
        test_data_dir = sample_csv_files["dir"]

        # Create mismatch test files
        x_mismatch = os.path.join(test_data_dir, "x_mismatch_test.csv")
        y_mismatch = os.path.join(test_data_dir, "y_mismatch_test.csv")

        with open(x_mismatch, "w") as f:
            f.write("name,feature1,feature2\n")
            f.write("Alice,1,2\n")
            f.write("Bob,4,5\n")
            f.write("Charlie,7,8\n")
            f.write("David,10,11\n")  # No match in y
            f.write("Eve,13,14\n")  # No match in y

        with open(y_mismatch, "w") as f:
            f.write("name,target\n")
            f.write("Alice,10\n")
            f.write("Bob,20\n")
            f.write("Charlie,30\n")
            f.write("Frank,40\n")  # No match in X
            f.write("Grace,50\n")  # No match in X

        X, y, keys = match_xy_by_key(
            X_path=x_mismatch,
            y_path=y_mismatch,
            x_key_column="name",
            y_key_column="name",
            x_value_columns=["feature1", "feature2"],
            y_value_column="target",
            delimiter=",",
        )

        # Should only match 3 rows (Alice, Bob, Charlie)
        assert X.shape == (3, 2), f"Expected X shape (3, 2), got {X.shape}"
        assert y.shape == (3,), f"Expected y shape (3,), got {y.shape}"
        assert keys.shape == (3,), f"Expected keys shape (3,), got {keys.shape}"

        # Verify the data matches expectations
        expected_X = np.array([[1, 2], [4, 5], [7, 8]], dtype=float)
        expected_y = np.array([10, 20, 30], dtype=float)
        expected_keys = ["Alice", "Bob", "Charlie"]

        np.testing.assert_array_equal(
            X, expected_X, "X data doesn't match expected values"
        )
        np.testing.assert_array_equal(
            y, expected_y, "y data doesn't match expected values"
        )
        assert sorted(list(keys)) == sorted(
            expected_keys
        ), f"Keys don't match: expected {expected_keys}, got {list(keys)}"

    def test_key_matching_default_behavior(self, sample_csv_files):
        """Test key matching with default parameters (first column as key)."""
        test_data_dir = sample_csv_files["dir"]

        # Create test files with first column as implicit key
        x_default = os.path.join(test_data_dir, "x_default_key.csv")
        y_default = os.path.join(test_data_dir, "y_default_key.csv")

        with open(x_default, "w") as f:
            f.write("id,feature1,feature2\n")
            f.write("1,1,2\n")
            f.write("2,4,5\n")
            f.write("3,7,8\n")

        with open(y_default, "w") as f:
            f.write("id,target\n")
            f.write("3,30\n")
            f.write("1,10\n")
            f.write("2,20\n")

        # Test with default parameters (should use first column as key)
        X_matched, y_matched, keys_matched = match_xy_by_key(
            X_path=x_default, y_path=y_default, delimiter=",", header="infer"
        )

        assert (
            X_matched.shape[0] == 3
        ), f"Expected 3 matched rows, got {X_matched.shape[0]}"
        assert (
            y_matched.shape[0] == 3
        ), f"Expected 3 matched targets, got {y_matched.shape[0]}"
        assert (
            keys_matched.shape[0] == 3
        ), f"Expected 3 matched keys, got {keys_matched.shape[0]}"

        # Keys should be ['1', '2', '3'] when sorted
        expected_keys = ["1", "2", "3"]
        actual_keys = sorted(list(keys_matched))
        assert (
            actual_keys == expected_keys
        ), f"Expected keys {expected_keys}, got {actual_keys}"

    def test_key_type_preservation(self, sample_csv_files):
        """Test that string keys are preserved as strings and don't become floats."""
        test_data_dir = sample_csv_files["dir"]

        # Create test files with string IDs that could be mistaken for numbers
        x_types = os.path.join(test_data_dir, "x_key_types.csv")
        y_types = os.path.join(test_data_dir, "y_key_types.csv")

        with open(x_types, "w") as f:
            f.write("id,feature1,feature2\n")
            f.write("101,1,2\n")  # Should stay as '101', not become '101.0'
            f.write("102,4,5\n")
            f.write("103,7,8\n")

        with open(y_types, "w") as f:
            f.write("id,target\n")
            f.write("103,30\n")
            f.write("101,10\n")

        X_matched, y_matched, matched_keys = match_xy_by_key(
            X_path=x_types,
            y_path=y_types,
            x_key_column="id",
            y_key_column="id",
            x_value_columns=["feature1", "feature2"],
            y_value_column="target",
            delimiter=",",
        )

        # Keys should be strings, not floats
        assert all(
            isinstance(key, str) for key in matched_keys
        ), f"All keys should be strings, got types: {[type(k) for k in matched_keys]}"

        # Should be exactly ['101', '103'], not ['101.0', '103.0']
        expected_keys = ["101", "103"]
        actual_keys = list(matched_keys)
        assert (
            actual_keys == expected_keys
        ), f"Expected string keys {expected_keys}, got {actual_keys}"

        # Verify no ".0" suffix on keys
        for key in matched_keys:
            assert not key.endswith(".0"), f"Key {key} should not have '.0' suffix"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
