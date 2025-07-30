#!/usr/bin/env python3
"""
Test script for fit_better CSV and data management operations.

This script tests the CSV manager functionality in fit_better:
- Loading CSV data
- Exporting CSV data
- Column operations
- Set operations on columns
- Data extraction for regression
"""

import os
import sys
import tempfile
import logging
import numpy as np
from pathlib import Path

# Set up paths for importing fit_better
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

# Import CSV manager from fit_better
from fit_better.data.csv_manager import CSVMgr

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_csv():
    """Create a sample CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        # Write header
        f.write("id,x_val,y_val,category\n")

        # Write data
        for i in range(10):
            x = i * 1.5
            y = 2 * x + 1 + np.random.normal(0, 0.5)
            category = "A" if i % 2 == 0 else "B"
            f.write(f"{i},{x:.2f},{y:.2f},{category}\n")

        return f.name


def create_sample_csv_with_missing():
    """Create a sample CSV file with missing values for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        # Write header
        f.write("id,x_val,y_val,category\n")

        # Write data with some missing values
        for i in range(10):
            x_val = f"{i * 1.5:.2f}" if i % 3 != 0 else ""
            y_val = f"{i * 3 + 1:.2f}" if i % 4 != 0 else ""
            category = "A" if i % 2 == 0 else ("" if i % 5 == 0 else "B")

            f.write(f"{i},{x_val},{y_val},{category}\n")

        return f.name


def test_csv_loading():
    """Test loading a CSV file."""
    logger.info("Testing CSV loading...")

    # Create a sample CSV file
    csv_path = create_sample_csv()

    # Initialize CSVMgr and load the file
    csv_mgr = CSVMgr(csv_path)

    # Check if data was loaded correctly
    assert csv_mgr.data is not None, "Data should be loaded"
    assert isinstance(csv_mgr.data, list), "Data should be a list"
    assert len(csv_mgr.data) == 10, "Data should have 10 rows"
    assert csv_mgr.header == [
        "id",
        "x_val",
        "y_val",
        "category",
    ], "Header should match expected values"

    # Clean up
    os.unlink(csv_path)

    logger.info("CSV loading test passed")
    assert True


def test_csv_exporting():
    """Test exporting data to a CSV file."""
    logger.info("Testing CSV exporting...")

    # Create a sample CSV file
    csv_path = create_sample_csv()

    # Initialize CSVMgr and load the file
    csv_mgr = CSVMgr(csv_path)

    # Export to a new file
    output_path = os.path.join(tempfile.gettempdir(), "output.csv")
    csv_mgr.export_csv(output_path)

    # Check if the file was created
    assert os.path.exists(output_path), "Output file should exist"

    # Load the exported file and check content
    exported_csv = CSVMgr(output_path)

    # Check if data matches
    assert len(exported_csv.data) == len(csv_mgr.data), "Data length should match"
    assert exported_csv.header == csv_mgr.header, "Header should match"

    # Clean up
    os.unlink(csv_path)
    os.unlink(output_path)

    logger.info("CSV exporting test passed")
    assert True


def test_column_operations():
    """Test column operations."""
    logger.info("Testing column operations...")

    # Create a sample CSV file with numeric columns only for X and y
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        # Write header
        f.write("id,x_val,y_val\n")

        # Write data (note: no category column for get_X_y test)
        for i in range(10):
            x = i * 1.5
            y = 2 * x + 1 + np.random.normal(0, 0.5)
            f.write(f"{i},{x:.2f},{y:.2f}\n")

        csv_path_numeric = f.name

    # Create a sample CSV file with category column for other tests
    csv_path = create_sample_csv()

    # Initialize CSVMgr and load the file
    csv_mgr = CSVMgr(csv_path)
    csv_mgr_numeric = CSVMgr(csv_path_numeric)

    # Test getting a column by index
    x_col = csv_mgr.get_col(1)  # x_val is at index 1
    assert len(x_col) == 10, "Column length should match data length"

    # Test getting a column by name
    y_col = csv_mgr.get_col_by_name("y_val")
    assert len(y_col) == 10, "Column length should match data length"

    # Test getting X and y for regression (using numeric-only data)
    X, y = csv_mgr_numeric.get_X_y(label_col=2)  # y_val is at index 2
    assert X.shape[0] == 10, "X should have 10 rows"
    assert X.shape[1] == 2, "X should have 2 columns (excluding label column)"
    assert y.shape == (10,), "y should have 10 elements"

    # Test getting a row
    row = csv_mgr.get_row(0)
    assert len(row) == 4, "Row should have 4 columns"

    # Clean up
    os.unlink(csv_path)
    os.unlink(csv_path_numeric)

    logger.info("Column operations test passed")
    assert True


def test_filtering():
    """Test data filtering by column percentile."""
    logger.info("Testing data filtering...")

    # Create a sample CSV file
    csv_path = create_sample_csv()

    # Initialize CSVMgr and load the file
    csv_mgr = CSVMgr(csv_path)

    # Filter to get top 30% by x_val (column index 1)
    filtered_csv = csv_mgr.filter_by_column_percentile(col=1, top=True, percent=30)

    # Check filtered data
    assert len(filtered_csv.data) == 3, "There should be 3 rows (30% of 10)"

    # Filter to get bottom 20% by y_val (column index 2)
    filtered_csv = csv_mgr.filter_by_column_percentile(col=2, top=False, percent=20)

    # Check filtered data
    assert len(filtered_csv.data) == 2, "There should be 2 rows (20% of 10)"

    # Clean up
    os.unlink(csv_path)

    logger.info("Data filtering test passed")
    assert True


def test_set_operations():
    """Test set operations on columns."""
    logger.info("Testing set operations...")

    # Create two sample CSV files
    csv_path1 = create_sample_csv()

    # Create a second CSV with different values in the category column
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        # Write header
        f.write("id,x_val,y_val,category\n")

        # Write data
        for i in range(10):
            x = i * 1.5
            y = 2 * x + 1 + np.random.normal(0, 0.5)
            category = "C" if i % 2 == 0 else "B"  # Different from first CSV
            f.write(f"{i},{x:.2f},{y:.2f},{category}\n")

        csv_path2 = f.name

    # Load both CSV files
    csv_mgr1 = CSVMgr(csv_path1)
    csv_mgr2 = CSVMgr(csv_path2)

    # Test column intersection (common categories - should be 'B')
    intersection = csv_mgr1.column_intersection(
        csv_mgr2, 3, 3
    )  # category is at index 3
    assert "B" in intersection, "Category 'B' should be common to both CSVs"
    assert len(intersection) == 1, "There should be only 1 common category"

    # Test column difference (categories in csv1 but not in csv2 - should be 'A')
    difference = csv_mgr1.column_difference(csv_mgr2, 3, 3)
    assert "A" in difference, "Category 'A' should be in first CSV but not second"
    assert len(difference) == 1, "There should be only 1 category in the difference"

    # Test column union (all unique categories - should be 'A', 'B', 'C')
    union = csv_mgr1.column_union(csv_mgr2, 3, 3)
    assert set(union) == {"A", "B", "C"}, "Union should contain all categories"
    assert len(union) == 3, "There should be 3 unique categories in total"

    # Clean up
    os.unlink(csv_path1)
    os.unlink(csv_path2)

    logger.info("Set operations test passed")
    assert True


def test_csv_handling():
    """Test other CSV handling functionality."""
    logger.info("Testing CSV handling functionality...")

    # Create a sample CSV file
    csv_path = create_sample_csv()

    # Initialize CSVMgr and load the file
    csv_mgr = CSVMgr(csv_path)

    # Test sorting by column
    csv_mgr.sort_by_column(col=1, reverse=True)  # sort by x_val in descending order

    # Check sorting
    x_vals = csv_mgr.get_col(1)
    assert np.all(np.diff(x_vals) <= 0), "Data should be sorted in descending order"

    # Test length operation
    assert len(csv_mgr) == 10, "CSV Manager should report 10 rows"

    # Test indexing
    first_row = csv_mgr[0]
    assert len(first_row) == 4, "First row should have 4 columns"

    # Test creating a copy with new data
    new_data = [["100", "100.0", "200.0", "X"]]
    copied_csv = csv_mgr.copy_with_data(new_data)
    assert len(copied_csv) == 1, "Copied CSV should have 1 row"
    assert copied_csv.header == csv_mgr.header, "Copied CSV should have same header"

    # Clean up
    os.unlink(csv_path)

    logger.info("CSV handling test passed")
    assert True


def main():
    """Run all CSV operations tests."""
    logger.info("Starting CSV operations tests")

    # Run all tests
    test_functions = [
        test_csv_loading,
        test_csv_exporting,
        test_column_operations,
        test_filtering,
        test_set_operations,
        test_csv_handling,
    ]

    results = []
    for test_func in test_functions:
        try:
            test_func()
            results.append(True)
            logger.info(f"{test_func.__name__}: PASS")
        except Exception as e:
            logger.error(f"{test_func.__name__} failed with error: {str(e)}")
            results.append(False)

    # Print overall summary
    n_passed = sum(results)
    n_total = len(results)
    logger.info(f"Test Summary: {n_passed}/{n_total} tests passed")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
