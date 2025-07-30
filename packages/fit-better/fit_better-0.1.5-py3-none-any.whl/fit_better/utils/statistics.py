"""
Regression Statistics and Model Evaluation Utilities
====================================================

This module provides a collection of utility functions for calculating,
displaying, and comparing various regression performance metrics. It helps in
evaluating the effectiveness of regression models and understanding their error
characteristics.

Key Functionalities:
--------------------

*   **Standard Regression Metrics (`calc_regression_statistics`)**:
    Calculates common metrics:
    *   Mean Absolute Error (MAE)
    *   Mean Squared Error (MSE)
    *   Root Mean Squared Error (RMSE)
    *   R-squared (R²)
    *   Percentage of predictions within specified relative error thresholds (e.g., within 1%, 3%, 5% of the true value).

*   **Partition-Specific Statistics (`print_partition_statistics`)**:
    For models trained on partitioned data, this function displays performance
    metrics for each individual partition, helping to understand how well
    the model performs on different segments of the data.

*   **Aggregated Performance (`calculate_total_performance`)**:
    Computes overall performance metrics when predictions are made by multiple
    models (e.g., an ensemble or partitioned models), allowing for weighted
    or simple averaging of predictions before evaluation.

*   **Error Percentiles (`get_error_percentiles`)**:
    Determines the magnitude of prediction errors at various percentile levels
    (e.g., 90th percentile error), providing insights into the distribution
    of errors.

*   **Formatted Output (`format_statistics_table`, `compare_model_statistics`)**:
    Utilities to present statistical results in human-readable ASCII tables,
    suitable for logging or console output. This includes comparing metrics
    across multiple models side-by-side.

The metrics calculated align with standard practices in regression analysis and
are based on scikit-learn's metrics module where applicable.

Usage Example:
--------------
```python
from fit_better.utils.statistics import calc_regression_statistics, format_statistics_table
import numpy as np

y_true = np.array([10, 12, 15, 11, 13])
y_pred = np.array([10.5, 11.5, 14.5, 11.2, 12.8])

stats = calc_regression_statistics(y_true, y_pred, residual_percentiles=[1, 5, 10])
print(format_statistics_table(stats, title="My Model Performance"))

# Output might look like:
# +---------------------+---------+
# | Regression Statistics (My Model Performance) |
# +---------------------+---------+
# | Metric              | Value   |
# +---------------------+---------+
# | mae                 | 0.4400  |
# | rmse                | 0.4775  |
# | r2                  | 0.8568  |
# | pct_within_3pct     | 60.0000 |
# | pct_within_5pct     | 100.0000|
# | pct_within_10pct    | 100.0000|
# | pct_within_1pct     | 0.0000  | # From residual_percentiles
# +---------------------+---------+
```

This module is crucial for quantitative assessment of models developed using the
`fit_better` package.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Union, Optional
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Import ASCII table printing if available
try:
    from .ascii import print_ascii_table
except ImportError:

    def print_ascii_table(headers, rows):
        """Fallback ASCII table printing if .ascii module is not available."""
        # Print headers
        print("| " + " | ".join(headers) + " |")
        print("|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|")

        # Print rows
        for row in rows:
            print("| " + " | ".join(str(cell) for cell in row) + " |")


def calc_regression_statistics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    residual_percentiles: Tuple[int, ...] = (1, 3, 5, 10, 20),
) -> Dict[str, float]:
    """
    Calculate standard regression performance statistics and relative error percentages.

    This function computes several common metrics to evaluate the performance
    of a regression model.

    Metrics Calculated:
    -------------------
    *   **MAE (Mean Absolute Error)**:
        *   Formula: \\( \\frac{1}{n} \\sum_{i=1}^{n} |y_i - \\hat{y}_i| \\)
        *   Interpretation: Average absolute difference between predicted and actual values.
            Lower is better. Robust to outliers. Same units as the target.
        *   Range: \\([0, \\infty)\\)
    *   **MSE (Mean Squared Error)**:
        *   Formula: \\( \\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2 \\)
        *   Interpretation: Average of the squares of the errors. Penalizes larger errors
            more heavily. Units are the square of the target's units.
        *   Range: \\([0, \\infty)\\)
    *   **RMSE (Root Mean Squared Error)**:
        *   Formula: \\( \\sqrt{\\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2} \\)
        *   Interpretation: Square root of MSE. Easier to interpret than MSE as it's in
            the same units as the target. Sensitive to outliers.
        *   Range: \\([0, \\infty)\\)
    *   **R² (Coefficient of Determination)**:
        *   Formula: \\( 1 - \\frac{\\sum (y_i - \\hat{y}_i)^2}{\\sum (y_i - \\bar{y})^2} = 1 - \\frac{SS_{res}}{SS_{tot}} \\)
        *   Interpretation: Proportion of the variance in the dependent variable that
            is predictable from the independent variable(s).
        *   Range: \\((-\\infty, 1]\\). Higher is better. 1 indicates perfect fit.
            0 indicates the model performs no better than the mean. Negative values
            indicate the model performs worse than the mean.
    *   **Percentage Within Thresholds (e.g., `pct_within_3pct`)**:
        *   Formula: For a threshold \\( T \\) (e.g., 0.03 for 3%), it's
            \\( \\frac{100}{n} \\sum_{i=1}^{n} \\mathbf{1}\\left( \\frac{|y_i - \\hat{y}_i|}{|y_i| + \\epsilon} \\le T \\right) \\),
            where \\( \\mathbf{1}(\\cdot) \\) is the indicator function and \\( \\epsilon \\) is a small constant to avoid division by zero.
        *   Interpretation: Percentage of predictions where the relative error
            is within a certain threshold (e.g., prediction is within +/- 3% of the true value).
            Higher is better.
        *   Range: \\([0, 100]\\)

    Args:
        y_true: Numpy array of true target values.
        y_pred: Numpy array of predicted target values.
        residual_percentiles: A tuple of integer percentages (e.g., (1, 3, 5, 10))
            for which to calculate the 'percentage of predictions within X% relative error'.
            These are in addition to the hardcoded 3%, 5%, 10%.

    Returns:
        A dictionary where keys are metric names (e.g., 'mae', 'rmse', 'r2', 'pct_within_3pct')
        and values are the calculated statistics (floats).
    """
    if len(y_true) == 0 or len(y_pred) == 0:
        # Prepare a dictionary with NaN for core metrics and 0.0 for percentage metrics
        nan_stats = {
            "mae": float("nan"),
            "mse": float("nan"),  # Added MSE to the NaN return
            "rmse": float("nan"),
            "r2": float("nan"),
        }
        # Add default percentile metrics with 0.0
        for p_val in [3, 5, 10] + list(residual_percentiles):
            nan_stats[f"pct_within_{p_val}pct"] = 0.0
        return nan_stats

    # Convert to numpy arrays and flatten
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()

    if y_true.shape != y_pred.shape:
        raise ValueError(
            f"y_true and y_pred must have the same shape. Got {y_true.shape} and {y_pred.shape}"
        )

    # Calculate basic metrics
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    # Calculate percentage of predictions within tolerance
    # Adding a small epsilon to the denominator to prevent division by zero for y_true = 0
    epsilon = 1e-10
    rel_errors = np.abs((y_pred - y_true) / (np.abs(y_true) + epsilon))

    stats = {
        "mae": float(mae),
        "mse": float(mse),  # Store MSE
        "rmse": float(rmse),
        "r2": float(r2),
    }
    # Calculate for default and custom percentiles
    all_percentiles_to_calc = sorted(list(set([3, 5, 10] + list(residual_percentiles))))
    for p in all_percentiles_to_calc:
        stats[f"pct_within_{p}pct"] = float(np.mean(rel_errors <= (p / 100.0)) * 100.0)
    return stats


def print_partition_statistics(
    models: List[Dict[str, Any]],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    partition_mode: Any,  # Typically PartitionMode Enum
    regressor_type: Optional[Any] = None,  # Typically RegressorType Enum
) -> None:
    """
    Prints performance statistics for each partition of a trained partitioned model.

    This function iterates through models trained on different data partitions,
    identifies the data points (both training and testing) belonging to each
    partition, and calculates regression statistics for them. It's useful for
    diagnosing how well a partitioned modeling strategy is performing on various
    segments of the dataset.

    The method for determining which data points belong to a partition can be complex,
    especially if the original partitioner object (e.g., a KMeans model) is not
    directly available. This function may use approximations or rely on information
    stored within the `models` list (e.g., 'partition_range').

    Args:
        models: A list of dictionaries, where each dictionary represents a trained
            model for a partition. Expected to contain at least the model object
            (key 'model') and potentially partition range information. This is
            typically the output from `fit_better.core.partitioning.train_models_on_partitions`.
        X_train: Training features (numpy array).
        y_train: Training targets (numpy array).
        X_test: Test features (numpy array).
        y_test: Test targets (numpy array).
        partition_mode: The partitioning mode used (e.g., an instance of
            `fit_better.core.partitioning.PartitionMode`). This helps in
            determining how to assign data points to partitions if explicit
            assignments aren't available.
        regressor_type: The type of regressor used within each partition (e.g., an
            instance of `fit_better.core.models.RegressorType`). Used for display purposes.

    Outputs:
        Prints an ASCII table to the console, summarizing statistics (MAE, RMSE, R²,
        sample counts) for each partition on both training and test sets.
    """
    # Ensure X_train and X_test are 2D, primarily for X[:, 0] access
    if X_train.ndim == 1:
        X_train = X_train.reshape(-1, 1)
    if X_test.ndim == 1:
        X_test = X_test.reshape(-1, 1)

    partition_info = []
    for idx, model_info in enumerate(models):
        p_range_str = "N/A"
        p_min, p_max = None, None

        if (
            "partition_range" in model_info
            and model_info["partition_range"] is not None
        ):
            p_min, p_max = model_info["partition_range"]
            if p_min is None and p_max is not None:
                p_range_str = f"<= {p_max:.2f}"
            elif p_max is None and p_min is not None:
                p_range_str = f"> {p_min:.2f}"
            elif p_min is not None and p_max is not None:
                p_range_str = f"({p_min:.2f}, {p_max:.2f}]"
        elif "lower_boundary" in model_info and "upper_boundary" in model_info:
            # This case is for models from the newer train_models_on_partitions
            lb = model_info["lower_boundary"]
            ub = model_info["upper_boundary"]
            p_min = lb if lb != -np.inf else None
            p_max = ub if ub != np.inf else None

            if p_min is None and p_max is not None:
                p_range_str = f"<= {p_max:.2f}"
            elif p_max is None and p_min is not None:
                p_range_str = f"> {p_min:.2f}"
            elif p_min is not None and p_max is not None:
                p_range_str = f"({p_min:.2f}, {p_max:.2f}]"
            else:
                p_range_str = "Full Range"

        model_name = str(regressor_type) if regressor_type else "Unknown"
        current_model = model_info.get("model")
        if hasattr(current_model, "__class__"):
            model_name = current_model.__class__.__name__

        # Add scaler if available
        scaler = model_info.get("scaler")
        transformer = model_info.get("transformer")

        partition_info.append(
            {
                "idx": idx,
                "range_str": p_range_str,
                "p_min": p_min,
                "p_max": p_max,
                "model": current_model,
                "model_name": model_name,
                "transformer": transformer,  # Store transformer
                "scaler": scaler,  # Store scaler
            }
        )

    partition_info.sort(key=lambda x: x["idx"])
    consolidated_stats_rows = []
    headers = [
        "Part #",
        "Range (X_train[:,0])",
        "Model",
        "Train N",
        "Train MAE",
        "Train R²",
        "Test N",
        "Test MAE",
        "Test R²",
    ]

    for info in partition_info:
        p_min, p_max = info["p_min"], info["p_max"]

        # Determine masks for training and testing data based on partition range
        # This assumes partitioning is primarily on the first feature of X
        if X_train.shape[1] == 0:  # Handle empty X
            train_mask = np.zeros(len(y_train), dtype=bool)
            test_mask = np.zeros(len(y_test), dtype=bool)
        elif p_min is None and p_max is not None:
            train_mask = X_train[:, 0] <= p_max
            test_mask = X_test[:, 0] <= p_max
        elif p_max is None and p_min is not None:
            train_mask = X_train[:, 0] > p_min
            test_mask = X_test[:, 0] > p_min
        elif p_min is not None and p_max is not None:
            train_mask = (X_train[:, 0] > p_min) & (X_train[:, 0] <= p_max)
            test_mask = (X_test[:, 0] > p_min) & (X_test[:, 0] <= p_max)
        else:  # Full range (e.g. NoPartitioner or if range is not defined)
            train_mask = np.ones(len(y_train), dtype=bool)
            test_mask = np.ones(len(y_test), dtype=bool)

        X_part_train, y_part_train = X_train[train_mask], y_train[train_mask]
        X_part_test, y_part_test = X_test[test_mask], y_test[test_mask]

        train_n = len(y_part_train)
        test_n = len(y_part_test)
        train_mae, train_r2 = float("nan"), float("nan")
        test_mae, test_r2 = float("nan"), float("nan")

        # Preprocess data for prediction if scaler/transformer exist
        X_pred_train = X_part_train
        X_pred_test = X_part_test

        if info["transformer"]:
            X_pred_train = info["transformer"].transform(X_part_train)
            X_pred_test = info["transformer"].transform(X_part_test)

        if info["scaler"]:
            # Ensure X_pred is 2D before scaling
            if X_pred_train.ndim == 1:
                X_pred_train = X_pred_train.reshape(-1, 1)
            if X_pred_test.ndim == 1:
                X_pred_test = X_pred_test.reshape(-1, 1)

            X_pred_train = info["scaler"].transform(X_pred_train)
            X_pred_test = info["scaler"].transform(X_pred_test)

        if info["model"] is not None:
            if train_n > 0:
                try:
                    y_train_pred = info["model"].predict(X_pred_train)
                    train_stats = calc_regression_statistics(y_part_train, y_train_pred)
                    train_mae, train_r2 = train_stats["mae"], train_stats["r2"]
                except Exception:
                    pass  # Keep NaN
            if test_n > 0:
                try:
                    y_test_pred = info["model"].predict(X_pred_test)
                    test_stats = calc_regression_statistics(y_part_test, y_test_pred)
                    test_mae, test_r2 = test_stats["mae"], test_stats["r2"]
                except Exception:
                    pass  # Keep NaN

        consolidated_stats_rows.append(
            [
                info["idx"],
                info["range_str"],
                info["model_name"],
                train_n,
                f"{train_mae:.3f}",
                f"{train_r2:.3f}",
                test_n,
                f"{test_mae:.3f}",
                f"{test_r2:.3f}",
            ]
        )

    title = f"Partition Statistics (Mode: {str(partition_mode)}, Regressor: {str(regressor_type or 'Mixed')})"
    print_ascii_table(headers, consolidated_stats_rows, title=title)


def calculate_total_performance(
    y_true: np.ndarray,
    y_pred_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
) -> Dict[str, float]:
    """
    Calculates overall performance metrics from a list of prediction arrays.

    This is useful when multiple models (e.g., from an ensemble or different
    partitions) make predictions, and an aggregated performance score is needed.
    Predictions can be combined either by simple averaging or weighted averaging.

    Args:
        y_true: Numpy array of true target values.
        y_pred_list: A list of numpy arrays, where each array contains predictions
            from a different source (e.g., a model in an ensemble). All prediction
            arrays must have the same length as `y_true`.
        weights: An optional list of floats representing the weights to apply to
            each prediction array in `y_pred_list`. If None, a simple average
            is performed (all predictions weighted equally). If provided, the
            number of weights must match the number of prediction arrays.

    Returns:
        A dictionary of overall performance statistics, calculated after aggregating
        the predictions. The keys and structure are the same as returned by
        `calc_regression_statistics`.

    Raises:
        ValueError: If `y_pred_list` is empty, or if prediction arrays have
            inconsistent lengths, or if the number of weights does not match
            the number of prediction arrays.
    """
    if not y_pred_list:
        raise ValueError("y_pred_list cannot be empty.")

    y_true = np.array(y_true).flatten()
    num_samples = len(y_true)

    processed_preds = []
    for i, y_p in enumerate(y_pred_list):
        y_p_flat = np.array(y_p).flatten()
        if len(y_p_flat) != num_samples:
            raise ValueError(
                f"Prediction array at index {i} has length {len(y_p_flat)}, "
                f"expected {num_samples} (length of y_true)."
            )
        processed_preds.append(y_p_flat)

    if weights:
        if len(weights) != len(processed_preds):
            raise ValueError(
                f"Number of weights ({len(weights)}) must match number of "
                f"prediction arrays ({len(processed_preds)})."
            )
        # Ensure weights sum to 1 for a true weighted average, or normalize
        weights_arr = np.array(weights, dtype=float)
        if not np.isclose(np.sum(weights_arr), 1.0):
            weights_arr = weights_arr / np.sum(weights_arr)

        final_y_pred = np.zeros(num_samples)
        for w, y_p_arr in zip(weights_arr, processed_preds):
            final_y_pred += w * y_p_arr
    else:
        # Simple average
        final_y_pred = np.mean(np.array(processed_preds), axis=0)

    return calc_regression_statistics(y_true, final_y_pred)


def get_error_percentiles(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    percentiles: Tuple[int, ...] = (1, 5, 10, 25, 50, 75, 90, 95, 99),
) -> Dict[str, float]:
    """
    Calculates the absolute prediction error values at specified percentiles.

    This function helps in understanding the distribution of prediction errors.
    For example, the 95th percentile error indicates that 95% of the predictions
    have an absolute error less than or equal to this value.

    Args:
        y_true: Numpy array of true target values.
        y_pred: Numpy array of predicted target values.
        percentiles: A tuple of integer percentiles (0-100) for which to calculate
            the absolute error.

    Returns:
        A dictionary where keys are percentile labels (e.g., 'error_p95' for 95th
        percentile) and values are the corresponding absolute error magnitudes.
    """
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()

    if y_true.shape != y_pred.shape:
        raise ValueError(
            f"y_true and y_pred must have the same shape. Got {y_true.shape} and {y_pred.shape}"
        )

    if len(y_true) == 0:
        return {f"error_p{p}": float("nan") for p in percentiles}

    absolute_errors = np.abs(y_true - y_pred)
    error_percentile_values = np.percentile(absolute_errors, percentiles)

    results = {}
    for p, val in zip(percentiles, error_percentile_values):
        results[f"error_p{p}"] = float(val)

    return results


def format_statistics_table(
    stats_dict: Dict[str, float], title: str = "Regression Statistics"
) -> str:
    """
    Formats a dictionary of regression statistics into a human-readable ASCII table string.

    Args:
        stats_dict: A dictionary of statistics, typically from `calc_regression_statistics`.
            Keys are metric names (str) and values are their corresponding numeric values.
        title: Optional title for the table.

    Returns:
        A string representing the ASCII formatted table.
    """
    if not stats_dict:
        return f"{title}\\n(No statistics available)"

    headers = ["Metric", "Value"]
    # Ensure consistent order for display, prioritizing common metrics
    common_metrics = ["mae", "mse", "rmse", "r2"]
    percentile_metrics = sorted(
        [k for k in stats_dict if k.startswith("pct_within_") and k.endswith("pct")],
        key=lambda x: int(x.split("_")[-1][:-3]),
    )  # Sort by percentile number
    error_p_metrics = sorted(
        [k for k in stats_dict if k.startswith("error_p")],
        key=lambda x: int(x.split("_p")[-1]),
    )  # Sort by error percentile number

    other_metrics = sorted(
        [
            k
            for k in stats_dict
            if k not in common_metrics
            and k not in percentile_metrics
            and k not in error_p_metrics
        ]
    )

    ordered_keys = common_metrics + percentile_metrics + error_p_metrics + other_metrics

    rows = []
    for key in ordered_keys:
        if key in stats_dict:
            value = stats_dict[key]
            if isinstance(value, float):
                # Format floats to 4 decimal places, unless they are percentages
                if (
                    "pct_within" in key or "r2" == key
                ):  # R2 is also often shown with fewer decimals
                    rows.append([key, f"{value:.4f}"])  # Percentages and R2
                else:
                    rows.append([key, f"{value:.4f}"])  # MAE, RMSE, MSE
            else:
                rows.append([key, str(value)])

    # Use the imported or fallback print_ascii_table by capturing its output
    # This is a bit of a workaround as print_ascii_table directly prints.
    # A better approach would be for ascii.py to provide a function that returns the table string.

    # For now, let's build the string manually for direct return
    if not rows:
        return f"{title}\\n(No data to display in table)"

    # Determine column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Create table string
    table_str = []

    # Title (optional)
    if title:
        table_str.append(f"+{'-' * (sum(col_widths) + 3 * len(col_widths) -1)}+")
        table_str.append(
            f"| {title.center(sum(col_widths) + 2 * len(col_widths) -1)} |"
        )

    # Header
    header_line = (
        "| "
        + " | ".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)])
        + " |"
    )
    separator_line = "|-" + "-|-".join(["-" * w for w in col_widths]) + "-|"

    table_str.append(
        separator_line.replace("|", "+", 2)
    )  # Top border for the table itself
    table_str.append(header_line)
    table_str.append(separator_line)

    # Rows
    for row in rows:
        row_line = (
            "| "
            + " | ".join([str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)])
            + " |"
        )
        table_str.append(row_line)

    table_str.append(separator_line.replace("|", "+", 2))  # Bottom border

    return "\\n".join(table_str)


def compare_model_statistics(
    stats_list: List[Dict[str, float]],
    model_names: Optional[List[str]] = None,
    metrics_to_compare: Optional[List[str]] = None,
    title: str = "Model Comparison",
) -> str:
    """
    Compares statistics from multiple models and returns an ASCII table string.

    Args:
        stats_list: A list of statistics dictionaries. Each dictionary is expected
            to be in the format returned by `calc_regression_statistics`.
        model_names: An optional list of names for the models, corresponding to
            the `stats_list`. If None, models will be named "Model 1", "Model 2", etc.
        metrics_to_compare: An optional list of specific metric names (strings)
            to include in the comparison table. If None, all common metrics found
            in the first model's statistics will be used.
        title: Optional title for the comparison table.

    Returns:
        A string representing the ASCII formatted comparison table.

    Raises:
        ValueError: If `stats_list` is empty or if `model_names` is provided
            and its length does not match `stats_list`.
    """
    if not stats_list:
        raise ValueError("stats_list cannot be empty.")

    num_models = len(stats_list)
    if model_names:
        if len(model_names) != num_models:
            raise ValueError(
                f"Length of model_names ({len(model_names)}) must match "
                f"length of stats_list ({num_models})."
            )
    else:
        model_names = [f"Model {i+1}" for i in range(num_models)]

    if metrics_to_compare is None:
        # Use common metrics from the first model's stats as default
        metrics_to_compare = ["mae", "mse", "rmse", "r2"]
        # Add any pct_within metrics present
        for k in stats_list[0].keys():
            if k.startswith("pct_within_") and k.endswith("pct"):
                if k not in metrics_to_compare:
                    metrics_to_compare.append(k)
        # Sort percentile metrics for consistent display
        pct_metrics = sorted(
            [m for m in metrics_to_compare if m.startswith("pct_within_")],
            key=lambda x: int(x.split("_")[-1][:-3]),
        )
        non_pct_metrics = [
            m for m in metrics_to_compare if not m.startswith("pct_within_")
        ]
        metrics_to_compare = non_pct_metrics + pct_metrics

    headers = ["Metric"] + model_names
    rows = []

    for metric in metrics_to_compare:
        row_data = [metric]
        for i in range(num_models):
            value = stats_list[i].get(
                metric, float("nan")
            )  # Get value or NaN if metric missing
            if isinstance(value, float):
                row_data.append(f"{value:.4f}")
            else:
                row_data.append(str(value))
        rows.append(row_data)

    # Use format_statistics_table logic to build the string
    # Manual string building for direct return:
    if not rows:
        return f"{title}\\n(No data to display in table)"

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    table_str = []
    if title:
        table_str.append(f"+{'-' * (sum(col_widths) + 3 * len(col_widths) -1)}+")
        table_str.append(
            f"| {title.center(sum(col_widths) + 2 * len(col_widths) -1)} |"
        )

    header_line = (
        "| "
        + " | ".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)])
        + " |"
    )
    separator_line = "|-" + "-|-".join(["-" * w for w in col_widths]) + "-|"

    table_str.append(separator_line.replace("|", "+", 2))
    table_str.append(header_line)
    table_str.append(separator_line)

    for row in rows:
        row_line = (
            "| "
            + " | ".join([str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)])
            + " |"
        )
        table_str.append(row_line)

    table_str.append(separator_line.replace("|", "+", 2))
    return "\\n".join(table_str)


# Example of how print_ascii_table might be used if it were in this module
# and returned a string instead of printing.
# For now, format_statistics_table and compare_model_statistics build their own strings.
# If .ascii.print_ascii_table is updated to return a string, these can be simplified.
#
# def example_usage_of_hypothetical_ascii_table_string_func():
#     from .ascii import get_ascii_table_string # Hypothetical function
#     headers = ["Name", "Age", "City"]
#     data = [["Alice", 30, "New York"], ["Bob", 24, "Paris"]]
#     table_string = get_ascii_table_string(headers, data, title="User Data")
#     print(table_string)
