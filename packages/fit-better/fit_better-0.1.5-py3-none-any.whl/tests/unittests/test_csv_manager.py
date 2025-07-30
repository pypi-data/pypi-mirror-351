"""
Unit tests for CSV manager functionality.

This test suite validates:
- CSV reading and writing
- Header handling
- Column selection and filtering
- Data format conversion
- Error handling
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
import tempfile

from fit_better.data.csv_manager import CSVMgr


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    # Create a simple CSV file with test data
    file_path = os.path.join(tmp_path, "test_data.csv")

    # Create test data with a header row and data rows
    with open(file_path, "w", newline="") as f:
        f.write("id,x_val,y_val,category\n")
        f.write("1,1.0,2.0,A\n")
        f.write("2,2.0,4.0,B\n")
        f.write("3,3.0,6.0,A\n")
        f.write("4,4.0,8.0,B\n")
        f.write("5,5.0,10.0,C\n")

    return file_path


@pytest.fixture
def sample_csv_with_missing(tmp_path):
    """Create a sample CSV file with missing values for testing."""
    # Create a CSV file with missing data
    file_path = os.path.join(tmp_path, "test_data_missing.csv")

    # Create test data with missing values
    with open(file_path, "w", newline="") as f:
        f.write("id,x_val,y_val,category\n")
        f.write("1,1.0,2.0,A\n")
        f.write("2,,4.0,\n")  # Missing x_val and category
        f.write("3,3.0,,A\n")  # Missing y_val
        f.write("4,4.0,8.0,B\n")
        f.write("5,,10.0,\n")  # Missing x_val and category

    return file_path


@pytest.mark.unit
@pytest.mark.data
class TestCSVManager:
    """Test suite for CSV manager functionality."""

    def test_init_and_load(self, sample_csv_file):
        """Test initializing CSVMgr and loading a file."""
        # Initialize with file path
        csv_mgr = CSVMgr(sample_csv_file)

        # Check that data was loaded
        assert csv_mgr.data is not None, "Data should be loaded"
        assert isinstance(csv_mgr.data, list), "Data should be a list"
        assert len(csv_mgr.data) > 0, "Data should not be empty"

        # Check header
        expected_header = ["id", "x_val", "y_val", "category"]
        assert csv_mgr.header == expected_header, "Header should match expected columns"

    def test_load_with_header(self, sample_csv_file):
        """Test loading a CSV file with header handling."""
        # Initialize with explicit header flag
        csv_mgr = CSVMgr(sample_csv_file, has_header=True)

        # Check that data was loaded with headers
        assert csv_mgr.header is not None, "Header should be loaded"
        assert "id" in csv_mgr.header, "Column 'id' should be present in header"
        assert "x_val" in csv_mgr.header, "Column 'x_val' should be present in header"

        # Test loading without header
        csv_mgr_no_header = CSVMgr(sample_csv_file, has_header=False)
        assert csv_mgr_no_header.header is None, "Header should be None"
        assert (
            len(csv_mgr_no_header.data) == 6
        ), "Data should include header row as data"

    def test_save_csv(self, sample_csv_file, tmp_path):
        """Test saving data to a CSV file."""
        # Load the sample CSV
        csv_mgr = CSVMgr(sample_csv_file)

        # Save to a new file
        output_file = os.path.join(tmp_path, "output.csv")
        csv_mgr.export_csv(output_file)

        # Check that the file was created
        assert os.path.exists(output_file), "Output file should exist"

        # Load the saved file and check content
        saved_csv = CSVMgr(output_file)

        # Check that all data was preserved
        assert len(saved_csv.data) == len(
            csv_mgr.data
        ), "Data length should be preserved"
        assert saved_csv.header == csv_mgr.header, "Header should be preserved"

    def test_get_column(self, sample_csv_file):
        """Test retrieving a specific column."""
        csv_mgr = CSVMgr(sample_csv_file)

        # Get the x_val column
        x_val_index = csv_mgr.header.index("x_val")
        x_col = csv_mgr.get_col(x_val_index)

        # Check the column data
        assert len(x_col) == 5, "Column length should match data length"
        assert x_col[0] == 1.0, "First value should be 1.0"
        assert x_col[4] == 5.0, "Last value should be 5.0"

        # Try using get_col_by_name
        x_col_by_name = csv_mgr.get_col_by_name("x_val")
        assert np.array_equal(
            x_col, x_col_by_name
        ), "get_col and get_col_by_name should return the same data"

    def test_get_xy(self, sample_csv_file):
        """Test retrieving X and y data for regression."""
        # Create a copy of the CSV file with only numeric columns for X/y testing
        csv_mgr = CSVMgr(sample_csv_file)

        # Create a new CSV file with only numeric columns
        tmp_dir = os.path.dirname(sample_csv_file)
        numeric_csv_path = os.path.join(tmp_dir, "numeric_data.csv")

        with open(numeric_csv_path, "w", newline="") as f:
            f.write("id,x_val,y_val\n")
            f.write("1,1.0,2.0\n")
            f.write("2,2.0,4.0\n")
            f.write("3,3.0,6.0\n")
            f.write("4,4.0,8.0\n")
            f.write("5,5.0,10.0\n")

        # Load the numeric-only CSV
        num_csv_mgr = CSVMgr(numeric_csv_path)

        # Get X and y data
        y_val_index = num_csv_mgr.header.index("y_val")
        X, y = num_csv_mgr.get_X_y(label_col=y_val_index)

        # Check shapes
        assert X.ndim == 2, "X should be a 2D array"
        assert X.shape[0] == 5, "X should have 5 rows"
        assert X.shape[1] == 2, "X should have 2 columns (id and x_val)"
        assert y.shape == (5,), "y should have 5 elements"

        # Check values
        assert y[0] == 2.0, "First y value should be 2.0"
        assert y[4] == 10.0, "Last y value should be 10.0"

    def test_get_row(self, sample_csv_file):
        """Test retrieving a specific row."""
        csv_mgr = CSVMgr(sample_csv_file)

        # Get the first row
        row = csv_mgr.get_row(0)

        # Check row content
        assert len(row) == 4, "Row should have 4 elements"
        assert row[0] == "1", "First element should be '1'"
        assert row[1] == "1.0", "Second element should be '1.0'"

    def test_sort_data(self, sample_csv_file):
        """Test sorting data by column."""
        csv_mgr = CSVMgr(sample_csv_file)

        # Sort by y_val column in descending order
        y_val_index = csv_mgr.header.index("y_val")
        csv_mgr.sort_by_column(col=y_val_index, reverse=True)

        # Check sorted data
        assert (
            csv_mgr.data[0][y_val_index] == "10.0"
        ), "First row should have y_val = 10.0"
        assert (
            csv_mgr.data[-1][y_val_index] == "2.0"
        ), "Last row should have y_val = 2.0"

    def test_filtering(self, sample_csv_file):
        """Test filtering data by column percentile."""
        csv_mgr = CSVMgr(sample_csv_file)

        # Get top 40% by x_val
        x_val_index = csv_mgr.header.index("x_val")
        filtered_mgr = csv_mgr.filter_by_column_percentile(
            col=x_val_index, top=True, percent=40
        )

        # Should get 2 rows (40% of 5 = 2)
        assert len(filtered_mgr.data) == 2, "Should get 2 rows (40% of 5)"

        # Check that we got the highest values
        filtered_x_vals = [float(row[x_val_index]) for row in filtered_mgr.data]
        assert all(
            val >= 4.0 for val in filtered_x_vals
        ), "Should only get rows with x_val >= 4.0"

    def test_set_operations(self, sample_csv_file, tmp_path):
        """Test set operations on columns."""
        # Create two CSV managers with different data
        csv_mgr1 = CSVMgr(sample_csv_file)

        # Create a second CSV file
        file_path2 = os.path.join(tmp_path, "test_data2.csv")
        with open(file_path2, "w", newline="") as f:
            f.write("id,x_val,y_val,category\n")
            f.write("3,3.0,6.0,A\n")
            f.write("4,4.0,8.0,B\n")
            f.write("6,6.0,12.0,D\n")

        csv_mgr2 = CSVMgr(file_path2)

        # Test column intersection
        id_index = csv_mgr1.header.index("id")
        intersection = csv_mgr1.column_intersection(csv_mgr2, id_index, id_index)
        assert sorted(intersection) == [
            3.0,
            4.0,
        ], "Intersection should contain IDs 3 and 4"

        # Test column difference
        difference = csv_mgr1.column_difference(csv_mgr2, id_index, id_index)
        assert sorted(difference) == [
            1.0,
            2.0,
            5.0,
        ], "Difference should contain IDs 1, 2, and 5"

        # Test column union
        union = csv_mgr1.column_union(csv_mgr2, id_index, id_index)
        assert sorted(union) == [
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
        ], "Union should contain all IDs"

    def test_error_handling(self, tmp_path):
        """Test error handling for invalid files and operations."""
        # Test loading non-existent file
        nonexistent_file = os.path.join(tmp_path, "nonexistent.csv")
        with pytest.raises(FileNotFoundError):
            CSVMgr(nonexistent_file)

        # Test getting non-existent column by name
        csv_mgr = CSVMgr()
        csv_mgr.header = ["a"]
        csv_mgr.data = [["1"], ["2"], ["3"]]
        with pytest.raises(ValueError):
            csv_mgr.get_col_by_name("non_existent")
