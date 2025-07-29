"""\nData Preprocessing Utilities for Regression\n===========================================\n\nAuthor: hi@xlindo.com\nCreate Time: 2025-04-29\n\nThis module provides a collection of functions for common data preprocessing tasks\nessential for preparing datasets for regression modeling. These tasks include\nscaling, normalization, handling missing values, and splitting data.\n
While some of these functionalities might overlap with scikit-learn's preprocessing\nmodule, these utilities are often tailored for direct use with NumPy arrays and\nthe specific workflows within the `fit_better` package, sometimes offering simpler\interfaces for common operations or integration with `CSVMgr` for keyed data.\n
Key Functionalities:\n--------------------\n\n*   **`load_key_value_arrays`**: (More of a data loading utility that also preprocesses by matching and filtering)\n    Loads feature (X) and target (y) data from separate files, assuming a key-value format\n    (e.g., two columns: ID and Value). It matches X and y pairs based on common keys,\n    optionally filters data based on a value range in one of the columns, and returns\n    aligned NumPy arrays for X and y.\n    This is particularly useful when X and y are not perfectly aligned or need pre-filtering.\n
*   **Scaling and Normalization**:\n    *   `normalize_data(X)`: Normalizes features to a [0, 1] range (Min-Max scaling).\n        Formula: \(X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}\)
        Pros: Scales data to a fixed range, useful for algorithms sensitive to feature magnitudes (e.g., neural networks, KNN).\n        Cons: Affected by outliers (min/max values dictate the range).\n    *   `standardize_data(X)`: Standardizes features by removing the mean and scaling to unit variance (Z-score normalization).\n        Formula: \(X_{std} = \frac{X - \mu}{\sigma}\)
        Pros: Results in data with zero mean and unit variance, common requirement for many ML algorithms.\n        Cons: Not bounded to a specific range.\n    *   `scale_features(X, feature_range=(-1, 1))`: Scales features to an arbitrary custom range.\n        Pros: Flexible scaling to any desired range.
        Cons: Like Min-Max, affected by outliers if the original min/max are used without clipping.

*   **`handle_missing_values(X, strategy='mean')`**: Imputes missing values (NaNs) in a NumPy array.\n    Supported strategies:\n    *   `'mean'`: Replace NaNs with the mean of the respective column.
    *   `'median'`: Replace NaNs with the median of the respective column (more robust to outliers).
    Pros: Simple way to handle missing data and allow algorithms to run.\n    Cons: Can introduce bias, may not be appropriate for all data types or distributions (e.g., categorical data, time series).\n
*   **`train_test_split_with_indices(X, y, ...)`**: Splits X and y arrays into training and testing sets\n    while also returning the original indices of the samples in each split. This is useful for tracking\n    specific data points or for aligning with external metadata.\n    (Note: `sklearn.model_selection.train_test_split` is the standard for this, this function might offer a convenience for index tracking.)

(The `generate_synthetic_data` function seems to be a duplicate or an older version of functionality now primarily in `fit_better.data.synthetic`. It should ideally be consolidated or removed if redundant to avoid confusion.)

Usage Example:\n--------------
```python
import numpy as np
from fit_better.data.preprocessing import normalize_data, standardize_data, handle_missing_values

# Sample data with missing values and varied scales
X_sample = np.array([[1., 10., np.nan], [2., 20., 300.],[3., 15., 250.]])

# Handle missing values using median imputation
X_imputed = handle_missing_values(X_sample, strategy='median')
print(f"Imputed X:\n{X_imputed}")
# Expected: [[ 1.  10. 275.] [ 2.  20. 300.] [ 3.  15. 250.]] (median of [nan,300,250] for last col)

# Normalize data
X_normalized, norm_params = normalize_data(X_imputed)
print(f"Normalized X (to [0,1]):\n{X_normalized}")

# Standardize data
X_standardized, std_params = standardize_data(X_imputed)
print(f"Standardized X (zero mean, unit variance):\n{X_standardized}")
```

These utilities aid in the critical preprocessing phase of a machine learning pipeline.
"""

import os
import numpy as np
from .csv_manager import CSVMgr
import logging
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def generate_synthetic_data(
    X_path, y_path, n=100_000, a=2.5, b=-3.0, noise_std=0.2, seed=42, header=False
):
    logger.info(
        f"Generating synthetic data: X_path={X_path}, y_path={y_path}, n={n}, a={a}, b={b}, noise_std={noise_std}, seed={seed}, header={header}"
    )
    os.makedirs(os.path.dirname(X_path), exist_ok=True)
    rng = np.random.default_rng(seed)
    ids = np.arange(1, n + 1)
    X_vals = np.round(np.linspace(2.5, 10.0, n) + rng.normal(0, noise_std, n), 2)
    y_vals = np.round(a * X_vals + b + rng.normal(0, noise_std, n), 2)
    with open(X_path, "w") as fx:
        if header:
            fx.write("# id value\n")
        for i, x in zip(ids, X_vals):
            fx.write(f"{i} {x}\n")
    with open(y_path, "w") as fy:
        if header:
            fy.write("# id value\n")
        for i, y in zip(ids, y_vals):
            fy.write(f"{i} {y}\n")


def load_key_value_arrays(
    X_path,
    y_path,
    has_header=False,
    delimiter=" ",
    x_key_col=0,
    x_val_col=1,
    y_key_col=0,
    y_val_col=1,
    filter_range=None,
):
    logger.info(
        f"Loading key-value arrays: X_path={X_path}, y_path={y_path}, has_header={has_header}, delimiter='{delimiter}', filter_range={filter_range}"
    )

    def apply_range_filter(mgr, col, rng):
        if rng is not None and isinstance(rng, tuple) and len(rng) == 2:
            minv, maxv = rng
            logger.info(f"Filtering by value range: [{minv}, {maxv}] on col {col}")
            return mgr.filter(lambda row: minv <= float(row[col]) <= maxv)
        return mgr

    X_mgr = CSVMgr(X_path, has_header=has_header, delimiter=delimiter)
    y_mgr = CSVMgr(y_path, has_header=has_header, delimiter=delimiter)
    orig_X_len = len(X_mgr.get_data())
    orig_y_len = len(y_mgr.get_data())
    if filter_range:
        X_mgr = apply_range_filter(X_mgr, x_val_col, filter_range)
        y_mgr = apply_range_filter(y_mgr, y_val_col, filter_range)
    X_dict = {str(row[x_key_col]): float(row[x_val_col]) for row in X_mgr.get_data()}
    y_dict = {str(row[y_key_col]): float(row[y_val_col]) for row in y_mgr.get_data()}

    def key_sorter(k):
        try:
            return (0, float(k))
        except Exception:
            return (1, k)

    common_keys = sorted(
        set(X_dict.keys()).intersection(set(y_dict.keys())), key=key_sorter
    )
    X = np.array([X_dict[k] for k in common_keys]).reshape(-1, 1)
    y = np.array([y_dict[k] for k in common_keys])
    logger.info(
        f"Original X: {orig_X_len}, Original y: {orig_y_len}, After intersection: {len(common_keys)}"
    )
    logger.info(f"Loaded arrays: X.shape={X.shape}, y.shape={y.shape}")
    return X, y


def normalize_data(X):
    """
    Normalize data to [0,1] range.

    Args:
        X: Input data as numpy array

    Returns:
        Tuple of (normalized_data, normalization_params)
    """
    min_vals = np.min(X, axis=0)
    max_vals = np.max(X, axis=0)
    X_norm = (X - min_vals) / (max_vals - min_vals)
    return X_norm, {"min": min_vals, "max": max_vals}


def standardize_data(X):
    """
    Standardize data (zero mean, unit variance).

    Args:
        X: Input data as numpy array

    Returns:
        Tuple of (standardized_data, standardization_params)
    """
    mean_vals = np.mean(X, axis=0)
    std_vals = np.std(X, axis=0)
    X_std = (X - mean_vals) / std_vals
    return X_std, {"mean": mean_vals, "std": std_vals}


def scale_features(X, feature_range=(-1, 1)):
    """
    Scale features to a custom range.

    Args:
        X: Input data as numpy array
        feature_range: Target range as tuple (min, max)

    Returns:
        Tuple of (scaled_data, scaling_params)
    """
    min_vals = np.min(X, axis=0)
    max_vals = np.max(X, axis=0)
    X_scaled = (X - min_vals) / (max_vals - min_vals)
    X_scaled = X_scaled * (feature_range[1] - feature_range[0]) + feature_range[0]
    return X_scaled, {"min": min_vals, "max": max_vals, "feature_range": feature_range}


def handle_missing_values(X, strategy="mean"):
    """
    Handle missing values in data.

    Args:
        X: Input data as numpy array
        strategy: Strategy for handling missing values ('mean', 'median', 'most_frequent')

    Returns:
        Array with imputed missing values
    """
    X_imputed = X.copy()

    if strategy == "mean":
        col_mean = np.nanmean(X, axis=0)
        inds = np.where(np.isnan(X))
        X_imputed[inds] = np.take(col_mean, inds[1])
    elif strategy == "median":
        col_median = np.nanmedian(X, axis=0)
        inds = np.where(np.isnan(X))
        X_imputed[inds] = np.take(col_median, inds[1])

    return X_imputed


def train_test_split_with_indices(X, y, test_size=0.2, random_state=None):
    """
    Split data into train and test sets with index tracking.

    Args:
        X: Input features
        y: Target values
        test_size: Proportion of data for test set
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (X_train, X_test, y_train, y_test, train_indices, test_indices)
    """
    indices = np.arange(X.shape[0])
    X_train, X_test, y_train, y_test, train_indices, test_indices = train_test_split(
        X, y, indices, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test, train_indices, test_indices
