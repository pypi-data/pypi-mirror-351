"""\nData Handling and Preprocessing for Fit Better\n==============================================\n\nThe `fit_better.data` module is responsible for all aspects of data management\nwithin the `fit_better` package. This includes loading data from various sources,\ngenerating synthetic datasets for testing and experimentation, preprocessing data\nto make it suitable for regression models, and saving processed data or results.\n\nKey Submodules and Functionalities:\n-----------------------------------\n\n*   **`csv_manager.py` (`CSVMgr` class)**: Provides robust utilities for reading and writing data in CSV format.\n    It handles various dialects, type inference, and can manage large CSV files efficiently.\n    Includes features for reading specific columns, chunking, and data type conversion.\n
*   **`file_loader.py`**: Contains functions for loading data from different file types (not just CSVs,\n    though CSV is a primary focus). This includes loading raw files into numpy arrays,\n    matching features (X) and targets (y) based on common keys from separate files,\n    and caching loaded data to speed up repeated access.\n    Key functions often include `load_data_from_files`, `load_file_to_array`, `match_xy_by_key`, `load_dataset`.\n
*   **`synthetic.py`**: Offers tools to generate synthetic datasets with controlled characteristics.\n    This is invaluable for testing regression algorithms, understanding model behavior under specific\n    conditions (e.g., different noise levels, underlying functions like linear, polynomial, sine), and\n    benchmarking partitioning strategies. Functions typically allow specifying the number of samples,\n    noise level, feature distributions, and the true underlying functional form.\n    Key functions: `generate_synthetic_data`, `generate_synthetic_data_by_function`.

*   **`preprocessing.py`**: Includes functions for common data preprocessing steps required before\n    feeding data into regression models. This might involve tasks like:\n    *   Handling missing values (imputation).
    *   Feature scaling (e.g., standardization, normalization) - although `StandardScaler` is often applied directly in the core flow.\n    *   Encoding categorical features (if applicable, though `fit_better` primarily focuses on numerical regression inputs).
    *   Ensuring correct data shapes and types (e.g., converting lists to NumPy arrays, ensuring X is 2D).
    Key functions: `preprocess_data_for_regression`, `ensure_array_shapes`.

*   **Caching Utilities**: (Often in `file_loader.py` or a dedicated cache module if complex)\n    Mechanisms to cache loaded and/or preprocessed data in memory or on disk to avoid redundant computations\n    during experimentation or repeated runs. `enable_cache`, `clear_cache` are typical interfaces.\n
This module aims to provide a flexible and efficient set of tools for preparing data for\nthe regression tasks performed by `fit_better.core` and `fit_better.models`.
"""

# Re-export key components from submodules
from .csv_manager import CSVMgr
from .file_loader import (
    load_data_from_files,
    load_file_to_array,
    match_xy_by_key,
    load_dataset,
    ensure_array_shapes,
    save_data_to_files,
    enable_cache,
    clear_cache,
    save_data,
    preprocess_data_for_regression,
)
from .synthetic import (
    generate_synthetic_data,
    generate_synthetic_data_by_function,
    generate_train_test_data,
)

__all__ = [
    "CSVMgr",
    "load_data_from_files",
    "load_file_to_array",
    "match_xy_by_key",
    "load_dataset",
    "ensure_array_shapes",
    "save_data_to_files",
    "enable_cache",
    "clear_cache",
    "save_data",
    "preprocess_data_for_regression",
    "generate_synthetic_data",
    "generate_synthetic_data_by_function",
    "generate_train_test_data",
]
