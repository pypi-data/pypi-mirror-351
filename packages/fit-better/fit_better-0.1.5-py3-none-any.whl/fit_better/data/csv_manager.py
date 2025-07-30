"""\nComprehensive CSV Management for Data Workflows\n=================================================\n\nAuthor: hi@xlindo.com\nCreate Time: 2025-04-29\n\nThis module provides the `CSVMgr` class, a robust and versatile tool for reading,\nwriting, manipulating, and analyzing CSV (Comma Separated Values) files. It is designed\nto simplify common data handling tasks in regression workflows and general data processing pipelines.\n\nThe `CSVMgr` class can be used as an instance to manage a specific CSV file's data in memory,\nor its static methods can be used for direct file operations without loading all data into an object.\n
Key Features of `CSVMgr`:\n--------------------------
\n*   **Loading and Initialization**: Load data from a CSV file upon instantiation or create an instance from an existing NumPy array.\n*   **Data Access**: Retrieve headers, full data (as list of lists), specific rows/columns (by index or name), or data as a NumPy array.\n*   **X, y Splitting**: Easily extract features (X) and target (y) arrays for machine learning tasks.\n*   **Saving and Exporting**: Save in-memory data to a CSV file, or export X and y arrays to separate files.\n    Static methods `array_to_csv` and `arrays_to_csv` allow direct saving of NumPy arrays.\n*   **In-place Manipulation**: Sort data by column values.\n*   **Filtering**: Filter rows based on percentile values in a specified column (`filter_by_column_percentile`).\n    Static method `filter_csv` allows more complex filtering based on column values.\n*   **Columnar Set Operations**: Perform intersection, union, difference, and symmetric difference on columns\n    between two `CSVMgr` instances (or CSV files if adapted to static methods).\n*   **File-Level Operations (Static Methods)**:\n    *   `csv_to_array`: Read a CSV directly into a NumPy array.\n    *   `save_xy_data`: Save X features and y target NumPy arrays to separate CSVs.\n    *   `load_from_csv`: Low-level static method to load raw data and header from a CSV.\n    *   `from_csv`: Class method to create a `CSVMgr` instance directly from a CSV file.\n    *   `import_xy_data`: Load X and y data from separate CSV files into NumPy arrays.\n    *   `from_xy_data`: Class method to create a `CSVMgr` instance from X and y data files.\n    *   `merge_csv_files`: Combine multiple CSV files into a single output file.\n    *   `split_csv_file`: Split a large CSV file into smaller chunks.\n    *   `convert_delimiter`: Change the delimiter of a CSV file (e.g., comma to tab).\n    *   `validate_csv`: Perform basic validation checks on a CSV file (e.g., expected columns, min rows).\n    *   `analyze_csv`: Compute descriptive statistics (mean, median, std, min, max, missing values) for numeric columns.\n    *   `transpose_csv`: Transpose rows and columns of a CSV file.\n    *   `column_operation`: Apply a specified operation (e.g., mathematical formula, custom function) to one or more columns.\n*   **Customization**: Control over delimiters, header presence/absence, and data types during read/write operations.\n*   **Pythonic Interface**: Supports standard Python protocols like `len()`, `__getitem__` (row access), iteration (over rows), and `in` operator (check for row presence).\n
Usage Example (Instance):\n--------------------------\n```python
from fit_better.data.csv_manager import CSVMgr
import numpy as np

# Create a dummy CSV file for demonstration
with open("sample_data.csv", "w") as f:
    f.write("ID,Feature1,Feature2,Target\n")
    f.write("1,0.5,1.2,3.0\n")
    f.write("2,0.8,1.5,3.8\n")
    f.write("3,0.2,0.9,2.1\n")

# Initialize CSVMgr with a filepath
mgr = CSVMgr(filepath="sample_data.csv")

# Get header and data
print(f"Header: {mgr.get_header()}")
# Header: ['ID', 'Feature1', 'Feature2', 'Target']
print(f"Data (first row): {mgr.get_data()[0]}")
# Data (first row): ['1', '0.5', '1.2', '3.0']

# Get data as NumPy array
np_data = mgr.to_array(dtype=float)
print(f"NumPy data (first row): {np_data[0]}")
# NumPy data (first row): [1.  0.5 1.2 3. ]

# Get X and y for ML
X, y = mgr.get_X_y(label_col=mgr.get_header().index('Target')) # Use header to find target column index
print(f"X (first row): {X[0]}, y (first value): {y[0]}")
# X (first row): [1.  0.5 1.2], y (first value): 3.0

# Sort data by 'Feature1' (column index 1)
mgr.sort_by_column(col=1)
print(f"Sorted data (first row by Feature1): {mgr.get_data()[0]}")
# Sorted data (first row by Feature1): ['3', '0.2', '0.9', '2.1']

# Clean up dummy file
import os
os.remove("sample_data.csv")
```

Usage Example (Static Methods):\n-------------------------------\n```python
from fit_better.data.csv_manager import CSVMgr
import numpy as np

# Create dummy data
feature_data = np.array([[1, 0.5], [2, 0.8], [3, 0.2]])
target_data = np.array([3.0, 3.8, 2.1])

# Save X and y data to separate files
CSVMgr.save_xy_data(feature_data, target_data, "features.csv", "target.csv",
                    x_headers=["ID", "Feature1"], y_header="TargetVal")

# Load data from a CSV into a NumPy array
loaded_features = CSVMgr.csv_to_array("features.csv", has_header=True)
print(f"Loaded features:\n{loaded_features}")
# Loaded features:
# [[1.  0.5]
#  [2.  0.8]
#  [3.  0.2]]

# Analyze a CSV
analysis_results = CSVMgr.analyze_csv("features.csv", numeric_columns=["Feature1"])
print(f"Analysis of Feature1: {analysis_results['Feature1']}")
# Analysis of Feature1: {'count': 3, 'mean': 0.5, ..., 'missing': 0}

# Clean up
import os
os.remove("features.csv")
os.remove("target.csv")
```
"""

import csv
import os
import numpy as np
from typing import List, Optional, Tuple, Any, Union, Dict


class CSVMgr:
    @staticmethod
    def array_to_csv(
        data: np.ndarray,
        filepath: str,
        headers: Optional[List[str]] = None,
        include_header: bool = True,
        delimiter: str = ",",
        header_prefix: str = "",
    ):
        """
        Save a numpy array to a CSV file with optional headers.

        Args:
            data: The numpy array to save
            filepath: The path to save the CSV file
            headers: Column headers to use (if None and include_header is True,
                    default column names will be generated)
            include_header: Whether to include header row
            delimiter: Delimiter character to use
            header_prefix: Optional prefix to add before the header row (e.g., '# ' for comments)
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        # Generate default headers if needed
        if headers is None and include_header:
            if len(data.shape) == 1:
                headers = ["Value"]
            else:
                headers = [f"Column_{i+1}" for i in range(data.shape[1])]

        # Handle 1D arrays by reshaping
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter)

            if include_header and headers is not None:
                if header_prefix:
                    # If header prefix is requested, write it directly to the file
                    csvfile.write(f"{header_prefix}{delimiter.join(headers)}\n")
                else:
                    writer.writerow(headers)

            for row in data:
                writer.writerow(row)

    @staticmethod
    def arrays_to_csv(
        arrays: List[np.ndarray],
        filepath: str,
        headers: Optional[List[str]] = None,
        include_header: bool = True,
        delimiter: str = ",",
    ):
        """
        Save multiple numpy arrays as columns in a CSV file.

        Args:
            arrays: List of numpy arrays, each representing a column
            filepath: The path to save the CSV file
            headers: Column headers to use (if None and include_header is True,
                    default column names will be generated)
            include_header: Whether to include header row
            delimiter: Delimiter character to use
        """
        # Ensure all arrays have the same length
        array_lengths = [len(arr) for arr in arrays]
        if len(set(array_lengths)) != 1:
            raise ValueError("All arrays must have the same length")

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        # Generate default headers if needed
        if headers is None and include_header:
            headers = [f"Column_{i+1}" for i in range(len(arrays))]

        # Reshape 1D arrays to column vectors
        reshaped_arrays = []
        for arr in arrays:
            if len(arr.shape) == 1:
                reshaped_arrays.append(arr.reshape(-1, 1))
            else:
                reshaped_arrays.append(arr)

        # Combine arrays into a single matrix
        combined_data = np.hstack(reshaped_arrays)

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter)

            if include_header and headers is not None:
                writer.writerow(headers)

            for row in combined_data:
                writer.writerow(row)

    @staticmethod
    def csv_to_array(
        filepath: str,
        delimiter: str = ",",
        has_header: bool = True,
        dtype: Any = float,
    ):
        """
        Read a CSV file into a numpy array.

        Args:
            filepath: Path to the CSV file
            delimiter: Delimiter character
            has_header: Whether the file has a header row
            dtype: Data type to use for the array

        Returns:
            Numpy array containing the data
        """
        with open(filepath, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)

            if has_header:
                next(reader)  # Skip header row

            data = []
            for row in reader:
                if row:  # Skip empty rows
                    try:
                        data.append([dtype(val) for val in row])
                    except ValueError:
                        # If conversion fails, append strings
                        data.append(row)

        return np.array(data)

    @staticmethod
    def save_xy_data(
        X: np.ndarray,
        y: np.ndarray,
        x_filepath: str,
        y_filepath: str,
        x_headers: Optional[List[str]] = None,
        y_header: Optional[str] = "Target",
        include_header: bool = True,
        delimiter: str = ",",
    ):
        """
        Save X features and y target arrays to separate CSV files.

        Args:
            X: Feature array
            y: Target array
            x_filepath: Path to save X features
            y_filepath: Path to save y target
            x_headers: Headers for X features
            y_header: Header for y target
            include_header: Whether to include headers
            delimiter: Delimiter character
        """
        # Save X features
        CSVMgr.array_to_csv(
            data=X,
            filepath=x_filepath,
            headers=x_headers,
            include_header=include_header,
            delimiter=delimiter,
        )

        # Save y target
        CSVMgr.array_to_csv(
            data=y,
            filepath=y_filepath,
            headers=[y_header] if y_header else None,
            include_header=include_header,
            delimiter=delimiter,
        )

    def __init__(
        self,
        filepath: str = "",
        has_header: bool = True,
        delimiter: str = ",",
        header: Optional[list] = None,
        data: Optional[list] = None,
    ):
        self.filepath = filepath
        self.has_header = has_header
        self.delimiter = delimiter
        self.header: Optional[List[str]] = header
        self.data: List[List[Any]] = data if data is not None else []
        if self.filepath and not self.data:
            self._load_csv()

    def _load_csv(self):
        try:
            self.header, self.data = self.load_from_csv(
                filepath=self.filepath,
                has_header=self.has_header,
                delimiter=self.delimiter,
            )
        except FileNotFoundError as e:
            self.header = None
            self.data = []
            # Re-raise FileNotFoundError for proper error handling
            raise
        except IOError as e:
            self.header = None
            self.data = []
            print(f"[CSVMgr] Warning: {str(e)}")

    def get_header(self) -> Optional[List[str]]:
        return self.header

    def get_data(self) -> List[List[Any]]:
        return self.data

    def get_X_y(self, label_col: int = -1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns features (X) and labels (y) as numpy arrays.
        label_col: index of the label column (default: last column)
        """
        arr = np.array(self.data)
        y = arr[:, label_col].astype(float)
        X = np.delete(arr, label_col, axis=1).astype(float)
        return X, y

    def sort_by_column(self, col: int = 0, reverse: bool = False):
        """
        Sort data in-place by the values in the specified column.

        Args:
            col: Column index to sort by
            reverse: If True, sort in descending order
        """
        self.data.sort(key=lambda row: self._try_float(row[col]), reverse=reverse)

    def export_csv(self, filepath: str, include_header: bool = True):
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter)
            if include_header and self.header:
                writer.writerow(self.header)
            for row in self.data:
                writer.writerow(row)

    def get_row(self, idx: int) -> list:
        return self.data[idx]

    def get_col(self, col: int) -> np.ndarray:
        """
        Get a specific column as a numpy array.

        Args:
            col: Index of the column to get

        Returns:
            Numpy array containing the column values

        Raises:
            IndexError: If the column index is out of bounds
        """
        if not self.data:
            return np.array([])

        if col >= len(self.data[0]) or col < -len(self.data[0]):
            raise IndexError(
                f"Column index {col} out of bounds for data with {len(self.data[0])} columns"
            )

        return np.array([self._try_float(row[col]) for row in self.data])

    def get_col_by_name(self, col_name: str) -> np.ndarray:
        if self.header is None:
            raise ValueError("No header available to get column by name.")
        try:
            col_idx = self.header.index(col_name)
        except ValueError:
            raise ValueError(f"Column name '{col_name}' not found in header.")
        return self.get_col(col_idx)

    def copy_with_data(self, data: list) -> "CSVMgr":
        """
        Return a new CSVMgr with the same header and delimiter, but with provided data (filepath is empty).
        """
        return CSVMgr(
            filepath="",
            has_header=self.has_header,
            delimiter=self.delimiter,
            header=self.header,
            data=data,
        )

    def filter_by_column_percentile(
        self, col: int, top: bool = True, percent: float = 10.0
    ) -> "CSVMgr":
        """
        Return a new CSVMgr with only the top or bottom percentage of rows by the specified column value.
        The new CSVMgr shares the same header and delimiter, but data is filtered. The filepath will be empty if not loaded from a file.
        """
        if not (0 < percent <= 100):
            raise ValueError("percent must be in (0, 100]")
        n = len(self.data)
        if n == 0:
            return self.copy_with_data([])
        k = max(1, int(np.ceil(n * percent / 100.0)))
        arr = np.array(self.data)
        col_vals = arr[:, col].astype(float)
        idx_sorted = np.argsort(col_vals)[:: -1 if top else None]
        idx_selected = idx_sorted[:k]
        filtered_data = arr[idx_selected].tolist()
        return self.copy_with_data(filtered_data)

    def column_difference(self, other: "CSVMgr", col_self: int, col_other: int) -> list:
        """
        Return a list of values that are in self's column col_self but not in other's column col_other (set difference).
        Handles any type (not just float).
        """
        vals_self = set(self.get_col(col_self))
        vals_other = set(other.get_col(col_other))
        return list(vals_self - vals_other)

    def column_intersection(
        self, other: "CSVMgr", col_self: int, col_other: int
    ) -> list:
        """
        Return a list of values that are in both self's column col_self and other's column col_other (set intersection).
        Handles any type (not just float).
        """
        vals_self = set(self.get_col(col_self))
        vals_other = set(other.get_col(col_other))
        return list(vals_self & vals_other)

    def column_union(self, other: "CSVMgr", col_self: int, col_other: int) -> list:
        """
        Return a list of values that are in either self's column col_self or other's column col_other (set union).
        Handles any type (not just float).
        """
        vals_self = set(self.get_col(col_self))
        vals_other = set(other.get_col(col_other))
        return list(vals_self | vals_other)

    def column_symmetric_difference(
        self, other: "CSVMgr", col_self: int, col_other: int
    ) -> list:
        """
        Return a list of values that are in self's column col_self or other's column col_other, but not in both (set symmetric difference).
        Handles any type (not just float).
        """
        vals_self = set(self.get_col(col_self))
        vals_other = set(other.get_col(col_other))
        return list(vals_self ^ vals_other)

    def to_array(self, dtype=float) -> np.ndarray:
        """
        Convert the entire data into a numpy array.

        Args:
            dtype: Data type for the numpy array (default: float)

        Returns:
            Numpy array containing the data

        Raises:
            ValueError: If data cannot be converted to the specified dtype
        """
        try:
            return np.array(self.data, dtype=dtype)
        except ValueError:
            # Try a more forgiving approach for mixed data
            arr = np.array(self.data, dtype=object)
            # Attempt to convert each element individually
            for i in range(arr.shape[0]):
                for j in range(arr.shape[1]):
                    try:
                        arr[i, j] = dtype(arr[i, j])
                    except (ValueError, TypeError):
                        pass  # Keep as string if conversion fails
            return arr

    @classmethod
    def from_array(
        cls,
        array: np.ndarray,
        header: Optional[List[str]] = None,
        has_header: bool = True,
        delimiter: str = ",",
    ) -> "CSVMgr":
        """
        Create a CSVMgr instance from a numpy array.

        Args:
            array: Numpy array to convert
            header: Column headers (if None and has_header is True,
                   default headers will be generated)
            has_header: Whether headers should be included
            delimiter: Delimiter character to use

        Returns:
            A new CSVMgr instance containing the array data

        Raises:
            ValueError: If array is empty or None
        """
        if array is None or array.size == 0:
            raise ValueError("Cannot create CSVMgr from empty array")

        # Generate default headers if needed
        if header is None and has_header:
            if len(array.shape) == 1:
                header = ["Value"]
            else:
                header = [f"Column_{i+1}" for i in range(array.shape[1])]

        # Handle 1D arrays
        if len(array.shape) == 1:
            data = [[x] for x in array]
        else:
            data = array.tolist()

        return cls(
            filepath="",  # No filepath as this is created from an array
            has_header=has_header,
            delimiter=delimiter,
            header=header,
            data=data,
        )

    def export_array_csv(
        self,
        filepath: str,
        include_header: bool = True,
        delimiter: str = None,
        header_prefix: str = "",
    ):
        """
        Export the data to a CSV file using the array_to_csv static method.
        This provides enhanced functionality compared to the basic export_csv method.

        Args:
            filepath: Path to save the CSV file
            include_header: Whether to include headers
            delimiter: Delimiter character (uses self.delimiter if None)
            header_prefix: Optional prefix to add before the header row (e.g., '# ' for comments)

        Raises:
            ValueError: If the data is empty
            IOError: If there are issues writing to the file
        """
        if not self.data:
            raise ValueError("Cannot export empty data")

        try:
            # Convert the data to a numpy array
            array_data = self.to_array(dtype=object)

            # Use the delimiter from the instance if not specified
            if delimiter is None:
                delimiter = self.delimiter

            # Ensure output directory exists
            output_dir = os.path.dirname(os.path.abspath(filepath))
            os.makedirs(output_dir, exist_ok=True)

            # Use CSVMgr's static array_to_csv method
            CSVMgr.array_to_csv(
                data=array_data,
                filepath=filepath,
                headers=self.header if include_header else None,
                include_header=include_header,
                delimiter=delimiter,
                header_prefix=header_prefix,
            )
        except Exception as e:
            raise IOError(f"Error exporting data to CSV: {str(e)}")

    def export_xy_data(
        self,
        x_filepath: str,
        y_filepath: str,
        label_col: int = -1,
        include_header: bool = True,
        delimiter: str = None,
    ):
        """
        Export the data as separate X features and y target files.

        Args:
            x_filepath: Path to save X features
            y_filepath: Path to save y target
            label_col: Index of the label column (default: last column)
            include_header: Whether to include headers
            delimiter: Delimiter character (uses self.delimiter if None)

        Raises:
            ValueError: If the data is empty or cannot be split into X and y
            IOError: If there are issues writing the files
        """
        if not self.data:
            raise ValueError("Cannot export empty data")

        try:
            # Get X and y data
            X, y = self.get_X_y(label_col=label_col)

            # Use the delimiter from the instance if not specified
            if delimiter is None:
                delimiter = self.delimiter

            # Generate appropriate headers if available
            if self.header and include_header:
                if label_col < 0:
                    adjusted_label_col = len(self.header) + label_col
                else:
                    adjusted_label_col = label_col

                y_header = self.header[adjusted_label_col]
                x_headers = (
                    self.header[:adjusted_label_col]
                    + self.header[adjusted_label_col + 1 :]
                )
            else:
                y_header = "Target"
                x_headers = None

            # Use CSVMgr's static save_xy_data method
            CSVMgr.save_xy_data(
                X=X,
                y=y,
                x_filepath=x_filepath,
                y_filepath=y_filepath,
                x_headers=x_headers,
                y_header=y_header,
                include_header=include_header,
                delimiter=delimiter,
            )
        except Exception as e:
            raise IOError(f"Error exporting X/y data: {str(e)}")

    @staticmethod
    def load_from_csv(
        filepath: str, has_header: bool = True, delimiter: str = ","
    ) -> Tuple[Optional[List[str]], List[List[Any]]]:
        """
        Static method to load data from a CSV file without creating a CSVMgr instance.

        Args:
            filepath: Path to the CSV file
            has_header: Whether the CSV file has a header row
            delimiter: Delimiter character used in the CSV file

        Returns:
            Tuple of (header, data) where header is None if has_header is False

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there are issues reading the file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        header = None
        data = []

        try:
            with open(filepath, "r", newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)
                if has_header:
                    try:
                        header = next(reader)
                    except StopIteration:
                        # Empty file
                        return None, []
                data = [row for row in reader if row]
        except IOError as e:
            raise IOError(f"Error reading CSV file '{filepath}': {str(e)}")

        return header, data

    @classmethod
    def from_csv(
        cls, filepath: str, has_header: bool = True, delimiter: str = ","
    ) -> "CSVMgr":
        """
        Create a CSVMgr instance from a CSV file.

        Args:
            filepath: Path to the CSV file
            has_header: Whether the CSV file has a header row
            delimiter: Delimiter character used in the CSV file

        Returns:
            A new CSVMgr instance containing the CSV data

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there are issues reading the file
        """
        header, data = cls.load_from_csv(filepath, has_header, delimiter)
        return cls(
            filepath=filepath,
            has_header=has_header,
            delimiter=delimiter,
            header=header,
            data=data,
        )

    @staticmethod
    def import_xy_data(
        x_filepath: str, y_filepath: str, has_header: bool = True, delimiter: str = ","
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Static method to import X features and y target from separate CSV files.

        Args:
            x_filepath: Path to the X features CSV file
            y_filepath: Path to the y target CSV file
            has_header: Whether the CSV files have header rows
            delimiter: Delimiter character used in the CSV files

        Returns:
            Tuple of (X, y) arrays

        Raises:
            FileNotFoundError: If either file does not exist
            ValueError: If the files have incompatible dimensions
        """
        # Use csv_utils function if available, otherwise use numpy
        try:
            X = CSVMgr.csv_to_array(
                filepath=x_filepath,
                delimiter=delimiter,
                has_header=has_header,
                dtype=float,
            )

            y = CSVMgr.csv_to_array(
                filepath=y_filepath,
                delimiter=delimiter,
                has_header=has_header,
                dtype=float,
            )

            # Ensure y is 1D if it's a single column
            if y.ndim > 1 and y.shape[1] == 1:
                y = y.ravel()

            # Check that X and y have the same number of samples
            if len(X) != len(y):
                raise ValueError(
                    f"X and y have different number of samples: {len(X)} vs {len(y)}"
                )

            return X, y

        except Exception as e:
            raise ValueError(f"Error importing X/y data: {str(e)}")

    @classmethod
    def from_xy_data(
        cls,
        x_filepath: str,
        y_filepath: str,
        has_header: bool = True,
        delimiter: str = ",",
    ) -> "CSVMgr":
        """
        Create a CSVMgr instance by combining X features and y target from separate CSV files.

        Args:
            x_filepath: Path to the X features CSV file
            y_filepath: Path to the y target CSV file
            has_header: Whether the CSV files have header rows
            delimiter: Delimiter character used in the CSV files

        Returns:
            A new CSVMgr instance with the combined data

        Raises:
            FileNotFoundError: If either file does not exist
            ValueError: If the files have incompatible dimensions
        """
        X, y = cls.import_xy_data(x_filepath, y_filepath, has_header, delimiter)

        # Get headers if needed
        x_header = None
        y_header = None

        if has_header:
            # Attempt to read headers from files
            try:
                with open(x_filepath, "r", newline="") as f:
                    x_header = next(csv.reader(f, delimiter=delimiter))
            except (StopIteration, FileNotFoundError):
                x_header = [f"X_{i+1}" for i in range(X.shape[1])]

            try:
                with open(y_filepath, "r", newline="") as f:
                    y_header = next(csv.reader(f, delimiter=delimiter))
                    # Take only the first element if y_header is a list
                    if isinstance(y_header, list):
                        y_header = y_header[0] if y_header else "Target"
            except (StopIteration, FileNotFoundError):
                y_header = "Target"

            header = x_header + [y_header]
        else:
            header = None

        # Combine X and y
        if y.ndim == 1:
            y_reshaped = y.reshape(-1, 1)
        else:
            y_reshaped = y

        combined = np.hstack((X, y_reshaped))

        return cls(
            filepath="",  # No filepath as this is created from combined data
            has_header=has_header,
            delimiter=delimiter,
            header=header,
            data=combined.tolist(),
        )

    @staticmethod
    def merge_csv_files(
        filepaths: List[str],
        output_filepath: str,
        has_header: bool = True,
        keep_first_header: bool = True,
        delimiter: str = ",",
    ) -> bool:
        """
        Static method to merge multiple CSV files into a single file.

        Args:
            filepaths: List of paths to CSV files to merge
            output_filepath: Path to output the merged CSV file
            has_header: Whether the CSV files have header rows
            keep_first_header: If True, only keep the header from the first file
            delimiter: Delimiter character used in the CSV files

        Returns:
            True if successful, False otherwise

        Raises:
            FileNotFoundError: If any input file does not exist
            ValueError: If no files are provided or they have incompatible headers
        """
        if not filepaths:
            raise ValueError("No input files provided")

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_filepath))
        os.makedirs(output_dir, exist_ok=True)

        # Write to output file
        with open(output_filepath, "w", newline="") as outfile:
            writer = csv.writer(outfile, delimiter=delimiter)

            # Process each input file
            for i, filepath in enumerate(filepaths):
                if not os.path.exists(filepath):
                    raise FileNotFoundError(f"Input file not found: {filepath}")

                with open(filepath, "r", newline="") as infile:
                    reader = csv.reader(infile, delimiter=delimiter)

                    # Handle header row
                    if has_header:
                        header = next(reader, None)
                        if i == 0 or not keep_first_header:
                            if header:
                                writer.writerow(header)

                    # Write all data rows
                    for row in reader:
                        if row:  # Skip empty rows
                            writer.writerow(row)

        return True

    @staticmethod
    def split_csv_file(
        filepath: str,
        output_dir: str,
        split_size: int,
        has_header: bool = True,
        include_header_each: bool = True,
        delimiter: str = ",",
    ) -> List[str]:
        """
        Static method to split a large CSV file into smaller files.

        Args:
            filepath: Path to the CSV file to split
            output_dir: Directory to output the split files
            split_size: Number of rows per split file
            has_header: Whether the CSV file has a header row
            include_header_each: Whether to include the header in each split file
            delimiter: Delimiter character used in the CSV file

        Returns:
            List of paths to the generated split files

        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If split_size is less than 1
        """
        if split_size < 1:
            raise ValueError("split_size must be at least 1")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        base_filename = os.path.basename(filepath)
        name, ext = os.path.splitext(base_filename)

        header_row = None
        output_files = []

        with open(filepath, "r", newline="") as infile:
            reader = csv.reader(infile, delimiter=delimiter)

            # Read header if needed
            if has_header:
                header_row = next(reader, None)

            file_count = 0
            row_count = 0
            current_outfile = None
            current_writer = None

            for row in reader:
                # Start a new file if needed
                if row_count % split_size == 0:
                    # Close previous file if open
                    if current_outfile:
                        current_outfile.close()

                    # Create new file
                    file_count += 1
                    output_path = os.path.join(output_dir, f"{name}_{file_count}{ext}")
                    output_files.append(output_path)

                    current_outfile = open(output_path, "w", newline="")
                    current_writer = csv.writer(current_outfile, delimiter=delimiter)

                    # Write header if needed
                    if include_header_each and header_row:
                        current_writer.writerow(header_row)

                # Write data row
                if row:  # Skip empty rows
                    current_writer.writerow(row)
                    row_count += 1

            # Close the last file
            if current_outfile:
                current_outfile.close()

        return output_files

    @staticmethod
    def convert_delimiter(
        input_filepath: str,
        output_filepath: str,
        input_delimiter: str = ",",
        output_delimiter: str = "\t",
        has_header: bool = True,
    ) -> bool:
        """
        Static method to convert a CSV file from one delimiter to another.

        Args:
            input_filepath: Path to input CSV file
            output_filepath: Path to output CSV file
            input_delimiter: Delimiter character in input file
            output_delimiter: Delimiter character for output file
            has_header: Whether the CSV file has a header row

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If the input file does not exist
            IOError: If there are issues reading or writing files
        """
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file not found: {input_filepath}")

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_filepath))
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Read the input file
            with open(input_filepath, "r", newline="") as infile:
                reader = csv.reader(infile, delimiter=input_delimiter)

                # Write to output file with new delimiter
                with open(output_filepath, "w", newline="") as outfile:
                    writer = csv.writer(outfile, delimiter=output_delimiter)

                    # Write all rows, including header if present
                    for row in reader:
                        if row:  # Skip empty rows
                            writer.writerow(row)

            return True

        except Exception as e:
            raise IOError(f"Error converting delimiter: {str(e)}")

    @staticmethod
    def validate_csv(
        filepath: str,
        expected_columns: Optional[List[str]] = None,
        required_columns: Optional[List[str]] = None,
        delimiter: str = ",",
        min_rows: int = 1,
    ) -> Dict[str, Any]:
        """
        Static method to validate a CSV file against expected structure and content.

        Args:
            filepath: Path to the CSV file
            expected_columns: List of column names that should be present (order matters)
            required_columns: List of column names that must be present (order doesn't matter)
            delimiter: Delimiter character used in the CSV file
            min_rows: Minimum number of data rows required (excluding header)

        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'row_count': int,
                'column_count': int,
                'header': Optional[List[str]]
            }

        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "row_count": 0,
            "column_count": 0,
            "header": None,
        }

        try:
            with open(filepath, "r", newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)

                # Check header
                try:
                    header = next(reader)
                    result["header"] = header
                    result["column_count"] = len(header)
                except StopIteration:
                    result["valid"] = False
                    result["errors"].append("Empty file or failed to read header")
                    return result

                # Validate columns if expected_columns is provided
                if expected_columns:
                    if header != expected_columns:
                        result["valid"] = False
                        result["errors"].append(
                            f"Header mismatch. Expected: {expected_columns}, Got: {header}"
                        )

                # Validate required columns if provided
                if required_columns:
                    missing_columns = [
                        col for col in required_columns if col not in header
                    ]
                    if missing_columns:
                        result["valid"] = False
                        result["errors"].append(
                            f"Missing required columns: {missing_columns}"
                        )

                # Count data rows and check consistency
                row_widths = set()
                for row in reader:
                    if row:  # Skip empty rows
                        result["row_count"] += 1
                        row_widths.add(len(row))

                # Check if we have minimum required rows
                if result["row_count"] < min_rows:
                    result["valid"] = False
                    result["errors"].append(
                        f"Insufficient data rows: {result['row_count']} (min: {min_rows})"
                    )

                # Check for inconsistent row widths
                if len(row_widths) > 1:
                    result["valid"] = False
                    result["errors"].append(
                        f"Inconsistent row widths: {sorted(row_widths)}"
                    )

                # Check if row width matches header width
                if row_widths and header and len(header) not in row_widths:
                    result["valid"] = False
                    result["errors"].append(
                        f"Row width ({sorted(row_widths)}) doesn't match header width ({len(header)})"
                    )

            return result

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error validating CSV: {str(e)}")
            return result

    @staticmethod
    def analyze_csv(
        filepath: str,
        numeric_columns: Optional[List[Union[int, str]]] = None,
        has_header: bool = True,
        delimiter: str = ",",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Static method to perform basic statistical analysis on CSV data.

        Args:
            filepath: Path to the CSV file
            numeric_columns: List of column indices or names to analyze (if None, all columns are analyzed)
            has_header: Whether the CSV file has a header row
            delimiter: Delimiter character used in the CSV file

        Returns:
            Dictionary with column statistics:
            {
                'column_name_1': {
                    'mean': float,
                    'median': float,
                    'std': float,
                    'min': float,
                    'max': float,
                    'count': int,
                    'missing': int,
                    'unique_count': int
                },
                ...
            }

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If numeric_columns contains invalid column names or indices
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        # Load data
        header, data = CSVMgr.load_from_csv(filepath, has_header, delimiter)

        # Convert to numpy array for analysis
        try:
            # First convert to object array to handle mixed types
            np_data = np.array(data, dtype=object)
        except Exception as e:
            raise ValueError(f"Error converting data to array: {str(e)}")

        if np_data.size == 0:
            return {}

        # Determine column indices to analyze
        column_indices = []
        if numeric_columns is None:
            # Analyze all columns
            column_indices = list(range(np_data.shape[1]))
        else:
            # Map column names to indices if needed
            for col in numeric_columns:
                if isinstance(col, str):
                    if not has_header or header is None:
                        raise ValueError("Cannot use column names without headers")
                    try:
                        idx = header.index(col)
                        column_indices.append(idx)
                    except ValueError:
                        raise ValueError(f"Column name '{col}' not found in header")
                elif isinstance(col, int):
                    if col >= 0 and col < np_data.shape[1]:
                        column_indices.append(col)
                    else:
                        raise ValueError(f"Column index {col} out of bounds")

        results = {}

        # Analyze each column
        for idx in column_indices:
            col_name = header[idx] if has_header and header else f"Column_{idx+1}"
            col_data = np_data[:, idx]

            # Convert values to float where possible for analysis
            numeric_values = []
            missing = 0

            for val in col_data:
                try:
                    if (
                        val is None
                        or val == ""
                        or (isinstance(val, str) and val.strip() == "")
                    ):
                        missing += 1
                    else:
                        numeric_values.append(float(val))
                except (ValueError, TypeError):
                    missing += 1

            # Skip columns with no numeric values
            if not numeric_values:
                results[col_name] = {
                    "mean": None,
                    "median": None,
                    "std": None,
                    "min": None,
                    "max": None,
                    "count": len(col_data),
                    "missing": missing,
                    "unique_count": len(set([str(x) for x in col_data])),
                }
                continue

            # Convert to numpy array for statistics
            numeric_array = np.array(numeric_values)

            # Calculate statistics
            results[col_name] = {
                "mean": float(np.mean(numeric_array)),
                "median": float(np.median(numeric_array)),
                "std": float(np.std(numeric_array)),
                "min": float(np.min(numeric_array)),
                "max": float(np.max(numeric_array)),
                "count": len(col_data),
                "missing": missing,
                "unique_count": len(set([str(x) for x in col_data])),
            }

        return results

    @staticmethod
    def _try_float(val):
        """
        Try to convert a value to float, return the original value if conversion fails.

        Args:
            val: Value to convert

        Returns:
            Float value if conversion succeeds, original value otherwise
        """
        try:
            return float(val)
        except Exception:
            return val

    @staticmethod
    def transpose_csv(
        input_filepath: str,
        output_filepath: str,
        has_header: bool = True,
        input_delimiter: str = ",",
        output_delimiter: str = None,
    ) -> bool:
        """
        Static method to transpose a CSV file (rows become columns, columns become rows).

        Args:
            input_filepath: Path to input CSV file
            output_filepath: Path to output CSV file
            has_header: Whether the input CSV file has a header row
            input_delimiter: Delimiter character used in the input CSV file
            output_delimiter: Delimiter character for output CSV file (defaults to input_delimiter)

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If the input file does not exist
            IOError: If there are issues reading or writing files
        """
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file not found: {input_filepath}")

        # Set output delimiter to input delimiter if not specified
        if output_delimiter is None:
            output_delimiter = input_delimiter

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_filepath))
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Read the input data
            header, data = CSVMgr.load_from_csv(
                input_filepath, has_header, input_delimiter
            )

            # Create the transposed data structure
            transposed = []
            if data:
                if has_header and header:
                    # If has header, prepare transposed data with header as first column
                    for i in range(len(header)):
                        transposed.append(
                            [header[i]] + [row[i] for row in data if i < len(row)]
                        )
                else:
                    # If no header, just transpose the data
                    col_count = max(len(row) for row in data) if data else 0
                    for i in range(col_count):
                        transposed.append([row[i] for row in data if i < len(row)])

            # Write the transposed data
            with open(output_filepath, "w", newline="") as outfile:
                writer = csv.writer(outfile, delimiter=output_delimiter)
                for row in transposed:
                    writer.writerow(row)

            return True

        except Exception as e:
            raise

    @staticmethod
    def filter_csv(
        input_filepath: str,
        output_filepath: str,
        column_filter: Dict[Union[int, str], Any],
        has_header: bool = True,
        delimiter: str = ",",
        case_sensitive: bool = True,
    ) -> int:
        """
        Static method to filter rows in a CSV file based on column values.

        Args:
            input_filepath: Path to input CSV file
            output_filepath: Path to output CSV file
            column_filter: Dictionary mapping column indices or names to filter values
                           e.g., {0: "value"} or {"name": "value"}
            has_header: Whether the CSV file has a header row
            delimiter: Delimiter character used in the CSV file
            case_sensitive: Whether string comparisons should be case-sensitive

        Returns:
            Number of rows written to output file (excluding header)

        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If column_filter contains invalid column names or indices
        """
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file not found: {input_filepath}")

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_filepath))
        os.makedirs(output_dir, exist_ok=True)

        # Convert column names to indices if needed
        column_indices = {}

        try:
            with open(input_filepath, "r", newline="") as infile:
                reader = csv.reader(infile, delimiter=delimiter)

                # Process header if present
                header = None
                if has_header:
                    try:
                        header = next(reader)

                        # Convert column names to indices
                        for col, val in column_filter.items():
                            if isinstance(col, str):
                                try:
                                    idx = header.index(col)
                                    column_indices[idx] = val
                                except ValueError:
                                    raise ValueError(
                                        f"Column name '{col}' not found in header"
                                    )
                            elif isinstance(col, int):
                                if col >= 0 and col < len(header):
                                    column_indices[col] = val
                                else:
                                    raise ValueError(
                                        f"Column index {col} out of bounds"
                                    )
                    except StopIteration:
                        # Empty file
                        with open(output_filepath, "w", newline="") as outfile:
                            if header:
                                writer = csv.writer(outfile, delimiter=delimiter)
                                writer.writerow(header)
                        return 0
                else:
                    # For files without header, only accept numeric indices
                    for col, val in column_filter.items():
                        if isinstance(col, int) and col >= 0:
                            column_indices[col] = val
                        else:
                            raise ValueError(
                                f"Only numeric indices allowed without header: {col}"
                            )

                # Write output file
                row_count = 0
                with open(output_filepath, "w", newline="") as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter)

                    # Write header if present
                    if has_header and header:
                        writer.writerow(header)

                    # Filter and write data rows
                    for row in reader:
                        if not row:  # Skip empty rows
                            continue

                        # Check if row matches all filters
                        match = True
                        for col_idx, filter_val in column_indices.items():
                            if col_idx >= len(row):
                                match = False
                                break

                            cell_val = row[col_idx]

                            # Handle string comparison
                            if isinstance(cell_val, str) and isinstance(
                                filter_val, str
                            ):
                                if not case_sensitive:
                                    if cell_val.lower() != filter_val.lower():
                                        match = False
                                        break
                                elif cell_val != filter_val:
                                    match = False
                                    break
                            # Handle other types
                            elif cell_val != filter_val:
                                match = False
                                break

                        if match:
                            writer.writerow(row)
                            row_count += 1

                return row_count

        except Exception as e:
            raise IOError(f"Error filtering CSV: {str(e)}")

    @staticmethod
    def column_operation(
        input_filepath: str,
        output_filepath: str,
        operations: Dict[Union[int, str], Union[str, callable]],
        has_header: bool = True,
        delimiter: str = ",",
        add_operation_to_header: bool = False,
    ) -> bool:
        """
        Static method to perform operations on columns in a CSV file.

        Args:
            input_filepath: Path to input CSV file
            output_filepath: Path to output CSV file
            operations: Dictionary mapping column indices or names to operations,
                       where an operation can be:
                       - A string formula with 'x' as placeholder (e.g., "x*2", "x+10")
                       - A callable function that takes a single value
            has_header: Whether the CSV file has a header row
            delimiter: Delimiter character used in the CSV file
            add_operation_to_header: Whether to add operation info to the header names

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If operations contains invalid column references or operations
        """
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file not found: {input_filepath}")

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_filepath))
        os.makedirs(output_dir, exist_ok=True)

        # Convert string formulas to callables
        operation_funcs = {}

        try:
            # Process header and prepare operations
            with open(input_filepath, "r", newline="") as infile:
                reader = csv.reader(infile, delimiter=delimiter)

                # Read header if needed
                header = None
                if has_header:
                    try:
                        header = next(reader)
                    except StopIteration:
                        # Empty file
                        with open(output_filepath, "w", newline="") as outfile:
                            if header:
                                writer = csv.writer(outfile, delimiter=delimiter)
                                writer.writerow(header)
                        return True

                # Map column references to indices and create callable functions
                for col_ref, op in operations.items():
                    # Convert column name to index if needed
                    col_idx = None
                    op_name = None

                    if isinstance(col_ref, str):
                        if not has_header or not header:
                            raise ValueError("Cannot use column names without header")
                        try:
                            col_idx = header.index(col_ref)
                            op_name = str(op) if not callable(op) else "custom_func"
                        except ValueError:
                            raise ValueError(
                                f"Column name '{col_ref}' not found in header"
                            )
                    else:
                        col_idx = col_ref
                        op_name = str(op) if not callable(op) else "custom_func"

                    # Create callable for the operation
                    if callable(op):
                        operation_funcs[col_idx] = op
                    elif isinstance(op, str):
                        # Create a function that evaluates the formula
                        # This uses eval which could be unsafe in some contexts
                        try:
                            op_name = op
                            formula = op.replace("x", "float(x)")

                            # Using a closure to capture the formula
                            def make_op_func(f=formula):
                                def op_func(x):
                                    try:
                                        return eval(f)
                                    except:
                                        return x

                                return op_func

                            operation_funcs[col_idx] = make_op_func()
                        except Exception as e:
                            raise ValueError(
                                f"Invalid operation formula '{op}': {str(e)}"
                            )
                    else:
                        raise ValueError(
                            f"Operation must be a string formula or callable function, got {type(op)}"
                        )

                    # Update header if needed
                    if header and add_operation_to_header and col_idx < len(header):
                        header[col_idx] = f"{header[col_idx]}_{op_name}"

                # Process the data rows
                data = list(reader)

                # Apply operations to data
                for row_idx, row in enumerate(data):
                    if not row:  # Skip empty rows
                        continue

                    # Apply operations to specified columns
                    for col_idx, op_func in operation_funcs.items():
                        if col_idx < len(row):
                            try:
                                # Apply the operation to the cell value
                                cell_val = row[col_idx]
                                if cell_val.strip():  # Skip empty cells
                                    row[col_idx] = str(op_func(cell_val))
                            except Exception as e:
                                # On error, leave the original value
                                pass

            # Write output file
            with open(output_filepath, "w", newline="") as outfile:
                writer = csv.writer(outfile, delimiter=delimiter)

                # Write header if exists
                if header:
                    writer.writerow(header)

                # Write data rows
                for row in data:
                    if row:  # Skip empty rows
                        writer.writerow(row)

            return True

        except Exception as e:
            raise IOError(f"Error performing column operations: {str(e)}")

    def __len__(self) -> int:
        """
        Return the number of rows in the data.
        This allows using len(csv_mgr) to get the number of rows.

        Returns:
            Number of rows in the data
        """
        return len(self.data)

    def __getitem__(self, idx: int) -> list:
        """
        Return the row at the specified index.
        This allows using csv_mgr[idx] to get a specific row.

        Args:
            idx: Index of the row to get

        Returns:
            Row at the specified index

        Raises:
            IndexError: If the index is out of bounds
        """
        return self.data[idx]

    def __iter__(self):
        """
        Return an iterator over the rows in the data.
        This allows using for row in csv_mgr.

        Returns:
            Iterator over the rows
        """
        return iter(self.data)

    def __contains__(self, item) -> bool:
        """
        Check if a row is in the data.
        This allows using row in csv_mgr.

        Args:
            item: Row to check for

        Returns:
            True if the row is in the data, False otherwise
        """
        return item in self.data

    def __str__(self) -> str:
        """
        Return a string representation of the CSVMgr instance.

        Returns:
            String representation showing file path, number of rows, and header
        """
        return f"CSVMgr('{self.filepath}', rows={len(self)}, header={self.header})"

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the CSVMgr instance.

        Returns:
            Detailed string representation with file path, header, and first few rows
        """
        preview = str(self.data[:3]) if self.data else "[]"
        if len(self.data) > 3:
            preview = preview[:-1] + ", ...]"
        return (
            f"CSVMgr(filepath='{self.filepath}', header={self.header}, data={preview})"
        )
