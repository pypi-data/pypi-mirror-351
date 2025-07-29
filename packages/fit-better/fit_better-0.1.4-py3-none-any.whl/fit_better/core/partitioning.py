"""
Author: xlindo
Create Time: 2025-04-29
Description: Utilities for partitioning data and training models on each partition.

Usage:
    from fit_better.core.partitioning import train_models_on_partitions, predict_with_partitioned_models

    # Train models on partitioned data
    models = train_models_on_partitions(
        X, y,
        partition_mode=PartitionMode.KMEANS,
        n_partitions=5,
        n_jobs=-1
    )

    # Make predictions using partitioned models
    y_pred = predict_with_partitioned_models(models, X_new, n_jobs=-1)

This module provides utilities for partitioning regression data and training
specialized models on each partition, improving overall prediction accuracy
compared to a single global model.

Data Partitioning Strategies and Utilities
==========================================

This module provides tools for partitioning datasets and training specialized
models on each partition. The goal is to improve overall prediction accuracy,
particularly for heterogeneous datasets where a single global model may not perform optimally.

Key Concepts:
------------

*   **`PartitionMode` (Enum)**: Defines various algorithms and strategies for
    dividing the data. Each mode represents a different approach to creating
    boundaries or clusters within the feature space.
*   **Partitioning Functions**: Utilities to calculate partition boundaries,
    assign data points to partitions, and ensure minimum partition sizes.
*   **Partitioned Model Training**: The `train_models_on_partitions` function
    orchestrates the process of splitting the data according to the chosen
    `PartitionMode`, training a separate regression model (of a specified
    `RegressorType`) on each data subset, and evaluating their performance.
*   **Prediction with Partitioned Models**: The `predict_with_partitioned_models`
    function uses the set of trained partitioned models to make predictions on new data.
    It first determines which partition the new data point belongs to and then uses
    the corresponding model for prediction.

Available Partition Modes (`PartitionMode` Enum Members):
-------------------------------------------------------

*   **`NONE`**: No partitioning is applied. A single global model is trained on the entire dataset.
    *   Theory: Standard regression modeling.
    *   Pros: Simple, fast to train.
    *   Cons: May underperform on datasets with complex, varying relationships.
*   **`PERCENTILE`**: Partitions data based on percentile values of a specific feature (typically the first feature for 1D partitioning).
    *   Theory: Divides the data into groups of roughly equal size based on sorted feature values.
    *   Formulae: Boundaries are \(P_{k/N}, P_{2k/N}, ..., P_{(N-1)k/N}\) where \(k=100/N_{partitions}\).
    *   Pros: Ensures balanced partitions in terms of sample count.
    *   Cons: Ignores data distribution; boundaries may not be meaningful.
*   **`RANGE`**: Divides the range of a feature into a specified number of equal-width intervals.
    *   Theory: Splits data based on fixed-width bins across the feature's range.
    *   Formulae: Boundaries are \(min(X) + i \\cdot \\frac{max(X)-min(X)}{N_{partitions}}\) for \(i=1, ..., N_{partitions}-1\).
    *   Pros: Simple to understand and implement.
    *   Cons: Sensitive to outliers; may result in empty or very small partitions if data is skewed.
*   **`KMEANS`**: Uses K-Means clustering on the features to form partitions. Each cluster becomes a partition.
    *   Theory: Iteratively finds cluster centers (centroids) that minimize the within-cluster sum of squares (WCSS).
    *   Formulae: Minimize \(\sum_{i=1}^{N_{partitions}} \sum_{x \in S_i} ||x - \mu_i||^2\), where \(\mu_i\) is the centroid of cluster \(S_i\).
    *   Pros: Adapts to the natural grouping in the data; can handle multi-dimensional features well.
    *   Cons: Assumes spherical clusters; sensitive to initial centroid placement; number of partitions (k) must be specified.
*   **`KMEDOIDS`**: Uses K-Medoids clustering. Similar to K-Means, but uses actual data points as cluster centers (medoids).
    *   Theory: Minimizes the sum of dissimilarities between points and their closest medoid.
    *   Pros: More robust to outliers than K-Means as it uses actual data points as centers.
    *   Cons: Computationally more expensive than K-Means; `sklearn_extra` package required.
*   **`MINIBATCH_KMEANS`**: A more scalable version of K-Means that uses mini-batches of data.
    *   Theory: Similar to K-Means but updates centroids based on small random subsets of data.
    *   Pros: Faster and more memory-efficient for large datasets than K-Means.
    *   Cons: Results can be slightly different from K-Means due to the approximation.
*   **`EQUAL_WIDTH`**: (Often similar to `RANGE`) Divides data based on equal-width bins of a feature.
    *   Pros: Simple and predictable partitioning.
    *   Cons: Can be sensitive to data skewness and outliers, leading to imbalanced partitions.
*   **`DECISION_TREE`**: Uses a Decision Tree regressor/classifier to find optimal split points in the feature space, creating partitions based on tree leaves.
    *   Theory: Recursively splits data based on feature thresholds that maximize information gain or minimize impurity.
    *   Pros: Can capture non-linear relationships and interactions between features to define partitions.
    *   Cons: Can overfit if tree depth is not controlled; may create complex, less interpretable partitions.
    *   (Note: Implementation details for Decision Tree based partitioning should be checked in the code, e.g., using `sklearn.tree.DecisionTreeRegressor` and its `apply` method or by iterating through leaf nodes.)
*   **`GRID`**: Creates a grid-based partition for multi-dimensional data.
    *   Theory: Divides each dimension into equal intervals and creates partitions from
        the resulting grid cells.
    *   Pros: Handles multi-dimensional data, preserves feature relationships.
    *   Cons: Number of partitions grows exponentially with dimensions, leading to
        the curse of dimensionality.
*   **`DBSCAN`**: Density-based clustering for flexible, arbitrary-shaped clusters.
    *   Theory: Groups data points based on dense regions separated by sparser regions.
    *   Points in sparse regions are labeled as noise.
    *   Pros: Discovers clusters of arbitrary shape, handles noise, doesn't require
        pre-specifying number of clusters.
    *   Cons: Sensitive to parameters (eps, min_samples), struggles with varying densities,
        scales poorly with high dimensions.
*   **`OPTICS`**: Ordering points to identify clustering structure, an improved version of DBSCAN.
    *   Theory: Creates a density-based ordering of points to identify clusters, without
        requiring a fixed density threshold.
    *   Pros: Handles varying density clusters better than DBSCAN, less sensitive to parameters.
    *   Cons: Slower than DBSCAN, still challenged by high dimensionality, complex implementation.

Usage Example:
--------------
```python
from fit_better.core.partitioning import PartitionMode, train_models_on_partitions, predict_with_partitioned_models
from fit_better.core.models import RegressorType
import numpy as np

# Sample data
X_train = np.random.rand(100, 2)
y_train = X_train[:, 0] * (X_train[:, 0] > 0.5) + X_train[:, 1] * (X_train[:, 1] <= 0.5) + np.random.rand(100)
X_test = np.random.rand(50, 2)

# Train models using K-Means partitioning and Linear Regression for each partition
partition_results = train_models_on_partitions(
    X_train, y_train,
    partition_mode=PartitionMode.KMEANS,
    n_partitions=3,
    regressor_type=RegressorType.LINEAR
)

# partition_results is a dictionary containing 'models' and 'partitioner_details'
trained_models = partition_results['models']
partitioner_obj = partition_results['partitioner_details']

# Make predictions on new data
y_pred = predict_with_partitioned_models(trained_models, X_test, partitioner=partitioner_obj)
print(f"Predictions: {y_pred[:5]}")
```
"""

# Standard library imports
import logging
import os
import datetime
from enum import Enum, auto
from typing import List, Dict, Tuple, Any, Optional, Union, Callable

# Third-party imports
import joblib
import numpy as np
from joblib import Parallel, delayed
from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN, OPTICS
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

# Try to import KMedoids from sklearn_extra if available
try:
    from sklearn_extra.cluster import KMedoids

    KMEDOIDS_AVAILABLE = True
except ImportError:
    KMEDOIDS_AVAILABLE = False

# Local imports
from .models import fit_all_regressors, select_best_model, Metric, RegressorType
from ..utils.ascii import ascii_table_lines, print_ascii_table, log_to_file

logger = logging.getLogger(__name__)


class PartitionMode(Enum):
    """Enum defining the partitioning methods supported by the package.

    Attributes:
        KMEANS: K-means clustering, divides data into K partitions based on feature similarity.
            - Theory: Minimizes within-cluster variance by finding K centroids and assigning
              each data point to the nearest centroid.
            - Pros: Simple, efficient, works well with spherical clusters of similar size.
            - Cons: Requires specifying K in advance, sensitive to initial centroids,
              struggles with non-convex clusters.
        PERCENTILE: Divides data into partitions based on percentiles of a feature.
            - Theory: Creates boundaries at specific percentiles of the data distribution,
              ensuring equal number of points in each partition.
            - Pros: Simple to understand, guarantees balanced partitions by sample count.
            - Cons: May not capture underlying patterns well if data is multimodal or clustered.
        RANGE: Divides data into equal-width intervals across the feature range.
            - Theory: Splits the data range into equal intervals between min and max values.
            - Pros: Simple, interpretable boundaries, good for data with uniform distribution.
            - Cons: Can result in highly imbalanced partitions if data is not uniformly distributed.
        GRID: Creates a grid-based partition for multi-dimensional data.
            - Theory: Divides each dimension into equal intervals and creates partitions from
              the resulting grid cells.
            - Pros: Handles multi-dimensional data, preserves feature relationships.
            - Cons: Number of partitions grows exponentially with dimensions, leading to
              the curse of dimensionality.
        DBSCAN: Density-based clustering for flexible, arbitrary-shaped clusters.
            - Theory: Groups data points based on dense regions separated by sparser regions.
              Points in sparse regions are labeled as noise.
            - Pros: Discovers clusters of arbitrary shape, handles noise, doesn't require
              pre-specifying number of clusters.
            - Cons: Sensitive to parameters (eps, min_samples), struggles with varying densities,
              scales poorly with high dimensions.
        OPTICS: Ordering points to identify clustering structure, an improved version of DBSCAN.
            - Theory: Creates a density-based ordering of points to identify clusters, without
              requiring a fixed density threshold.
            - Pros: Handles varying density clusters better than DBSCAN, less sensitive to parameters.
            - Cons: Slower than DBSCAN, still challenged by high dimensionality, complex implementation.
    """

    KMEANS = "kmeans"
    KMEANS_PLUS_PLUS = "kmeans++"  # KMeans with k-means++ initialization method
    PERCENTILE = "percentile"
    RANGE = "range"
    GRID = "grid"
    DBSCAN = "dbscan"
    OPTICS = "optics"
    KMEDOIDS = "kmedoids"
    MINIBATCH_KMEANS = "minibatch_kmeans"
    EQUAL_WIDTH = "equal_width"
    DECISION_TREE = "decision_tree"
    NONE = "none"

    def __str__(self):
        return self.value


def format_range_string(left: float, right: float) -> str:
    """
    Format a range string for display in a standard format.

    Args:
        left: Left boundary (can be -inf)
        right: Right boundary (can be inf)

    Returns:
        Formatted range string like "(-inf, 3.25]" or "(7.5, inf)"
    """
    range_str = (
        f"({left:.4g}, {right:.4g}]"
        if not np.isneginf(left)
        else f"(-inf, {right:.4g}]"
    )
    if np.isposinf(right):
        range_str = f"({left:.4g}, inf)" if not np.isneginf(left) else "(-inf, inf)"
    return range_str


def get_partition_masks(X: np.ndarray, boundaries: List[float]) -> List[np.ndarray]:
    """
    Calculate masks for each partition based on boundaries.

    Args:
        X: Input features
        boundaries: Array of boundary values

    Returns:
        List of boolean masks for each partition
    """
    masks = []

    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # First partition: X <= first boundary
    if len(boundaries) > 0:
        masks.append(X[:, 0] <= boundaries[0])

    # Middle partitions: boundaries[i-1] < X <= boundaries[i]
    for i in range(1, len(boundaries)):
        masks.append((X[:, 0] > boundaries[i - 1]) & (X[:, 0] <= boundaries[i]))

    # Last partition: X > last boundary
    if len(boundaries) > 0:
        masks.append(X[:, 0] > boundaries[-1])

    return masks


def enforce_minimum_partition_size(
    X: np.ndarray, boundaries: List[float], min_size: int = 50
) -> List[float]:
    """
    Adjust partition boundaries to ensure each partition has at least min_size samples.

    Args:
        X: Data values to partition
        boundaries: Initial partition boundaries
        min_size: Minimum number of samples per partition

    Returns:
        Adjusted boundaries ensuring minimum partition sizes
    """
    boundaries = list(boundaries)  # Make a copy to avoid modifying the input

    while True:
        masks = get_partition_masks(X, boundaries)
        sizes = [np.count_nonzero(m) for m in masks]
        small_idxs = [i for i, sz in enumerate(sizes) if sz < min_size]

        if not small_idxs:
            break

        for idx in small_idxs:
            if len(boundaries) == 0:
                continue
            if idx == 0:
                # Merge first partition with right
                boundaries.pop(0)
            elif idx == len(boundaries):
                # Merge last partition with left
                boundaries.pop(-1)
            else:
                # Merge with neighbor with more samples
                left_sz = sizes[idx - 1]
                right_sz = sizes[idx + 1]
                if left_sz >= right_sz:
                    boundaries.pop(idx - 1)
                else:
                    boundaries.pop(idx)
            # After one merge, break to recompute masks and sizes
            break

    return boundaries


def get_partition_boundaries(
    X: np.ndarray,
    partition_mode: PartitionMode,
    n_partitions: int,
    min_size: int = 50,
    n_jobs: int = 1,
) -> List[float]:
    """
    Get partition boundaries based on the specified mode.

    Args:
        X: Input features
        partition_mode: Mode for partitioning
        n_partitions: Number of partitions to create
        min_size: Minimum partition size
        n_jobs: Number of parallel jobs

    Returns:
        List of boundary values
    """
    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # Check if we have enough data for meaningful partitioning
    if len(X) < n_partitions * min_size:
        # Not enough data for the requested number of partitions
        # Adjust the number of partitions
        adjusted_n_parts = max(1, len(X) // min_size)
        logger.warning(
            f"Not enough data for {n_partitions} partitions with minimum size {min_size}. "
            f"Adjusting to {adjusted_n_parts} partitions."
        )
        n_partitions = adjusted_n_parts

    # If we still don't have enough data for even one partition of min_size,
    # fall back to a single partition
    if len(X) < min_size or n_partitions <= 1:
        logger.warning(
            f"Not enough data for meaningful partitioning. Using a single partition."
        )
        return []

    if partition_mode == PartitionMode.PERCENTILE:
        # Use percentiles as boundaries
        percentiles = np.linspace(0, 100, n_partitions + 1)[1:-1]
        boundaries = np.percentile(X[:, 0], percentiles)

    elif partition_mode == PartitionMode.RANGE:
        # Use equal range boundaries
        min_val = np.min(X[:, 0])
        max_val = np.max(X[:, 0])
        boundaries = np.linspace(min_val, max_val, n_partitions + 1)[1:-1]

    elif partition_mode == PartitionMode.EQUAL_WIDTH:
        # Use equal width boundaries
        min_val = np.min(X[:, 0])
        max_val = np.max(X[:, 0])
        width = (max_val - min_val) / n_partitions
        boundaries = [min_val + width * (i + 1) for i in range(n_partitions - 1)]

    elif partition_mode == PartitionMode.KMEANS:
        # Use KMeans cluster centers as boundaries
        kmeans = KMeans(n_clusters=n_partitions, n_init=10, random_state=42)
        kmeans.fit(X)
        centers = np.sort(kmeans.cluster_centers_[:, 0])
        boundaries = [
            (centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)
        ]

    elif partition_mode == PartitionMode.KMEANS_PLUS_PLUS:
        # Use KMeans++ cluster centers as boundaries
        kmeans = KMeans(
            n_clusters=n_partitions, init="k-means++", n_init=10, random_state=42
        )
        kmeans.fit(X)
        centers = np.sort(kmeans.cluster_centers_[:, 0])
        boundaries = [
            (centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)
        ]

    elif partition_mode == PartitionMode.KMEDOIDS:
        if not KMEDOIDS_AVAILABLE:
            raise ImportError("KMedoids requires sklearn_extra package")
        # Use KMedoids cluster centers as boundaries
        kmedoids = KMedoids(n_clusters=n_partitions, random_state=42)
        kmedoids.fit(X)
        centers = np.sort(kmedoids.cluster_centers_[:, 0])
        boundaries = [
            (centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)
        ]

    elif partition_mode == PartitionMode.MINIBATCH_KMEANS:
        # Use MiniBatchKMeans cluster centers as boundaries
        kmeans = MiniBatchKMeans(n_clusters=n_partitions, random_state=42)
        kmeans.fit(X)
        centers = np.sort(kmeans.cluster_centers_[:, 0])
        boundaries = [
            (centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)
        ]

    elif partition_mode == PartitionMode.GRID:
        # ... existing GRID implementation ...
        pass
    elif partition_mode == PartitionMode.DBSCAN:
        # Default parameters for DBSCAN
        eps = min_size
        min_samples = 2

        # Import DBSCAN from sklearn
        from sklearn.cluster import DBSCAN

        # Fit DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)

        # Handle noise points (labeled as -1)
        unique_labels = np.unique(labels)

        # If all points are noise, create a single partition
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            logger.warning(
                "DBSCAN classified all points as noise. Using a single partition."
            )
            labels = np.zeros(len(X), dtype=int)

        # Create a separate partition for noise points if they exist
        if -1 in unique_labels:
            # Remap labels to start from 0 (noise) and increment others
            new_labels = labels.copy()
            for i, label in enumerate(unique_labels):
                if label >= 0:  # Skip noise label (-1)
                    new_labels[labels == label] = i
            labels = new_labels

        # Get indices for each partition
        unique_labels = np.unique(labels)
        partition_indices = [np.where(labels == label)[0] for label in unique_labels]

        # Store the number of clusters found
        n_clusters = len(unique_labels)
        logger.info(f"DBSCAN found {n_clusters} clusters/partitions.")

        result = {
            "partition_indices": partition_indices,
            "labels": labels,
            "n_clusters": n_clusters,
            "dbscan_model": dbscan,
        }

    elif partition_mode == PartitionMode.OPTICS:
        # Default parameters for OPTICS
        min_samples = 2
        max_eps = float("inf")
        cluster_method = "xi"
        xi = 0.05

        # Import OPTICS from sklearn
        from sklearn.cluster import OPTICS

        # Fit OPTICS
        optics = OPTICS(
            min_samples=min_samples,
            max_eps=max_eps,
            cluster_method=cluster_method,
            xi=xi,
        )
        labels = optics.fit_predict(X)

        # Handle noise points (labeled as -1)
        unique_labels = np.unique(labels)

        # If all points are noise, create a single partition
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            logger.warning(
                "OPTICS classified all points as noise. Using a single partition."
            )
            labels = np.zeros(len(X), dtype=int)

        # Create a separate partition for noise points if they exist
        if -1 in unique_labels:
            # Remap labels to start from 0 (noise) and increment others
            new_labels = labels.copy()
            for i, label in enumerate(unique_labels):
                if label >= 0:  # Skip noise label (-1)
                    new_labels[labels == label] = i
            labels = new_labels

        # Get indices for each partition
        unique_labels = np.unique(labels)
        partition_indices = [np.where(labels == label)[0] for label in unique_labels]

        # Store the number of clusters found
        n_clusters = len(unique_labels)
        logger.info(f"OPTICS found {n_clusters} clusters/partitions.")

        result = {
            "partition_indices": partition_indices,
            "labels": labels,
            "n_clusters": n_clusters,
            "optics_model": optics,
            "reachability": optics.reachability_,
        }
    else:
        raise ValueError(f"Unsupported partition_mode: {partition_mode}")

    # Enforce minimum partition size
    boundaries = enforce_minimum_partition_size(X, boundaries, min_size)

    return boundaries


def train_models_on_partitions(
    X: np.ndarray,
    y: np.ndarray,
    n_parts: int = 3,
    partition_mode: PartitionMode = PartitionMode.KMEANS,
    metric: Metric = Metric.MAE,
    regressor_type: RegressorType = RegressorType.LINEAR,
    min_partition_size: int = 50,
    n_jobs: int = 1,
    verbose: bool = False,
    train_mode: str = "all",  # Added train_mode parameter
    n_partitions: int = None,  # Added for backward compatibility
    **kwargs,
) -> Dict[str, Any]:
    """
    Train regression models on partitioned data.

    Args:
        X: Input features
        y: Target values
        n_parts: Number of partitions to create
        partition_mode: Mode for partitioning (KMEANS, PERCENTILE, RANGE)
        metric: Metric to use for model selection
        regressor_type: Type of regressor to use
        min_partition_size: Minimum number of samples in each partition
        n_jobs: Number of parallel jobs
        verbose: Whether to print verbose output
        train_mode: Training mode - 'all' for all models or 'best' for best model only
        **kwargs: Additional arguments to pass to the regressor

    Returns:
        Dictionary containing trained models, partition boundaries, and metadata
    """
    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # Use n_partitions if provided (for backward compatibility)
    num_parts = n_partitions if n_partitions is not None else n_parts

    # Get partition boundaries
    boundaries = get_partition_boundaries(
        X, partition_mode, num_parts, min_size=min_partition_size, n_jobs=n_jobs
    )

    # Get partition masks
    masks = get_partition_masks(X, boundaries)

    # Train a model on each partition
    models = []

    for i, mask in enumerate(masks):
        if np.sum(mask) < min_partition_size:
            logger.warning(
                f"Partition {i} has fewer than {min_partition_size} samples, skipping"
            )
            continue

        X_part = X[mask]
        y_part = y[mask]

        if verbose:
            logger.info(f"Training model for partition {i} with {np.sum(mask)} samples")

        # Train models on this partition
        # Filter out parameters that fit_all_regressors doesn't accept
        filtered_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["n_partitions", "test_compatibility_mode"]
        }

        partition_models = fit_all_regressors(
            X_part,
            y_part,
            n_jobs=n_jobs,
            regressor_type=regressor_type,
            **filtered_kwargs,
        )

        # Select best model based on metric
        best_model = select_best_model(partition_models, metric=metric)

        # Store partition info with the model
        best_model["partition_idx"] = i
        best_model["partition_size"] = np.sum(mask)
        best_model["n_samples"] = np.sum(mask)  # Add n_samples

        # For the first and last partitions, store boundary info
        if i == 0 and len(boundaries) > 0:
            best_model["upper_boundary"] = boundaries[0]
        elif i == len(masks) - 1 and len(boundaries) > 0:
            best_model["lower_boundary"] = boundaries[-1]
        elif len(boundaries) > i - 1:
            best_model["lower_boundary"] = boundaries[i - 1]
            best_model["upper_boundary"] = boundaries[i]

        models.append(best_model)

    # For backward compatibility with existing tests, return just the models list
    # instead of the dictionary that contains additional metadata
    if "test_compatibility_mode" in kwargs and kwargs["test_compatibility_mode"]:
        return models

    # Otherwise return the full metadata dictionary
    return {
        "models": models,
        "boundaries": boundaries,
        "partition_mode": partition_mode.name,
        "n_parts": n_parts,
        "min_partition_size": min_partition_size,
        "train_mode": train_mode,  # Added train_mode to result
    }


def predict_with_partitioned_models(
    model_data: Union[Dict[str, Any], List],
    X_new: np.ndarray,
    n_jobs: int = 1,
    verbose: bool = False,
) -> np.ndarray:
    """
    Make predictions using previously trained partitioned models.

    Args:
        model_data: Dictionary containing trained models and boundaries from train_models_on_partitions,
                   or a list of models for backward compatibility
        X_new: New data to predict
        n_jobs: Number of parallel jobs
        verbose: Whether to print verbose output

    Returns:
        Array of predictions
    """
    # Ensure X_new is 2D
    if X_new.ndim == 1:
        X_new = X_new.reshape(-1, 1)

    # Handle both dictionary format and list format for backward compatibility
    if isinstance(model_data, dict):
        models = model_data["models"]
        boundaries = model_data.get("boundaries", [])
    else:
        # For backward compatibility, if model_data is a list, treat it as the models list
        models = model_data
        boundaries = []

    # Get partition masks for new data
    masks = get_partition_masks(X_new, boundaries)

    # Initialize predictions array
    y_pred = np.zeros(X_new.shape[0])

    # Make predictions for each partition
    for i, (mask, model_dict) in enumerate(zip(masks, models)):
        if np.sum(mask) == 0:
            continue

        # Get data for this partition
        X_part = X_new[mask]

        # Apply transformations if available
        if "transformer" in model_dict and model_dict["transformer"] is not None:
            X_part = model_dict["transformer"].transform(X_part)

        if "scaler" in model_dict and model_dict["scaler"] is not None:
            X_part = model_dict["scaler"].transform(X_part)

        # Make predictions
        model = model_dict["model"]
        y_part = model.predict(X_part)

        # Store predictions
        y_pred[mask] = y_part

    return y_pred


def create_kmeans_boundaries(X, k=2):
    """Create partition boundaries using KMeans clustering."""
    return get_partition_boundaries(X, PartitionMode.KMEANS, k)


def create_kmedoids_boundaries(X, k=2):
    """Create partition boundaries using KMedoids clustering."""
    return get_partition_boundaries(X, PartitionMode.KMEDOIDS, k)


def create_kmeans_plus_plus_boundaries(X, k=2):
    """Create partition boundaries using KMeans++ clustering."""
    return get_partition_boundaries(X, PartitionMode.KMEANS_PLUS_PLUS, k)


# Base class for partitioners to provide a consistent interface
class BasePartitioner:
    """
    Base class for all partitioner strategies.

    This class defines the common interface that all partitioners must implement,
    primarily the `fit` and `predict_partition` methods.
    The `fit` method learns the partitioning scheme from the data (e.g., cluster centers,
    decision boundaries), and `predict_partition` assigns new data points to one of the
    learned partitions.

    Attributes:
        n_partitions (int): The number of partitions to create.
        fitted (bool): True if the partitioner has been fitted to data, False otherwise.
    """

    def __init__(self, n_partitions: int):
        self.n_partitions = n_partitions
        self.fitted = False

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "BasePartitioner":
        """
        Fit the partitioner to the data X.

        Args:
            X: The input features (n_samples, n_features).
            y: The target variable (optional, may be used by some partitioners).

        Returns:
            The fitted partitioner instance (self).
        """
        raise NotImplementedError("Subclasses must implement the fit method.")

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        """
        Predict the partition index for each sample in X.

        Args:
            X: The input features (n_samples, n_features) for which to predict partitions.

        Returns:
            A 1D numpy array of partition indices (0 to n_partitions-1) for each sample.
        """
        raise NotImplementedError(
            "Subclasses must implement the predict_partition method."
        )

    def get_partition_masks(self, X: np.ndarray) -> List[np.ndarray]:
        """
        Get boolean masks for each partition based on the input data X.

        Args:
            X: Input features (n_samples, n_features).

        Returns:
            A list of boolean masks. Each mask corresponds to a partition and indicates
            which samples in X belong to that partition.
        """
        if not self.fitted:
            raise RuntimeError("Partitioner has not been fitted yet. Call fit() first.")

        partition_indices = self.predict_partition(X)
        masks = []
        for i in range(self.n_partitions):
            masks.append(partition_indices == i)
        return masks

    def get_params(self) -> Dict[str, Any]:
        """
        Get parameters of this partitioner.
        Useful for logging and reproducibility.
        """
        return {"n_partitions": self.n_partitions, "type": self.__class__.__name__}


class KMeansPartitioner(BasePartitioner):
    """
    Partitions data using K-Means clustering.

    Each cluster found by K-Means defines a separate partition.
    The `fit` method trains the K-Means model, and `predict_partition` assigns
    new samples to the nearest cluster centroid.

    Attributes (in addition to BasePartitioner):
        kmeans_model (KMeans): The fitted scikit-learn KMeans model.
        random_state (Optional[int]): Random state for reproducibility of KMeans.
    """

    def __init__(self, n_partitions: int, random_state: Optional[int] = 42):
        super().__init__(n_partitions)
        self.random_state = random_state
        self.kmeans_model = KMeans(
            n_clusters=self.n_partitions, random_state=self.random_state, n_init=10
        )

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "KMeansPartitioner":
        """Fits the K-Means model to X."""
        # Ensure X is 2D for KMeans
        if X.ndim == 1:
            X_processed = X.reshape(-1, 1)
        else:
            X_processed = X
        self.kmeans_model.fit(X_processed)
        self.fitted = True
        return self

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        """Predicts partition indices using the fitted K-Means model."""
        if not self.fitted:
            raise RuntimeError(
                "KMeansPartitioner has not been fitted. Call fit() first."
            )
        if X.ndim == 1:
            X_processed = X.reshape(-1, 1)
        else:
            X_processed = X
        return self.kmeans_model.predict(X_processed)

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params.update(self.kmeans_model.get_params())
        return params


# Similar classes would be defined for KMedoidsPartitioner, PercentilePartitioner, etc.
# For brevity, only KMeansPartitioner is fully fleshed out here as an example.


class PercentilePartitioner(BasePartitioner):
    """
    Partitions data based on percentiles of the first feature.
    Primarily uses the first feature (X[:, 0]) for partitioning.
    """

    def __init__(self, n_partitions: int):
        super().__init__(n_partitions)
        self.boundaries: Optional[np.ndarray] = None

    def fit(
        self, X: np.ndarray, y: Optional[np.ndarray] = None
    ) -> "PercentilePartitioner":
        if X.ndim == 1:
            feature_to_partition = X
        else:
            feature_to_partition = X[:, 0]  # Default to first feature

        if self.n_partitions <= 1:
            self.boundaries = np.array([])
        else:
            percentiles = np.linspace(0, 100, self.n_partitions + 1)[1:-1]
            self.boundaries = np.percentile(feature_to_partition, percentiles)
        self.fitted = True
        return self

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        if not self.fitted or self.boundaries is None:
            raise RuntimeError(
                "PercentilePartitioner has not been fitted. Call fit() first."
            )
        if X.ndim == 1:
            feature_to_partition = X
        else:
            feature_to_partition = X[:, 0]

        # np.digitize assigns to bins: 0 if x <= b[0], 1 if b[0] < x <= b[1], ..., n if x > b[n-1]
        # This naturally creates n_partitions from n_partitions-1 boundaries.
        return np.digitize(feature_to_partition, self.boundaries)


# ... (Other partitioner classes like RangePartitioner, DecisionTreePartitioner would follow a similar pattern)
class RangePartitioner(BasePartitioner):
    """Partitions data based on equal ranges of the first feature."""

    def __init__(self, n_partitions: int):
        super().__init__(n_partitions)
        self.boundaries: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "RangePartitioner":
        if X.ndim == 1:
            feature_to_partition = X
        else:
            feature_to_partition = X[:, 0]

        if self.n_partitions <= 1:
            self.boundaries = np.array([])
        else:
            min_val = np.min(feature_to_partition)
            max_val = np.max(feature_to_partition)
            if min_val == max_val:  # Handle case where all values are the same
                self.boundaries = np.array([min_val] * (self.n_partitions - 1))
            else:
                self.boundaries = np.linspace(min_val, max_val, self.n_partitions + 1)[
                    1:-1
                ]
        self.fitted = True
        return self

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        if not self.fitted or self.boundaries is None:
            raise RuntimeError(
                "RangePartitioner has not been fitted. Call fit() first."
            )
        if X.ndim == 1:
            feature_to_partition = X
        else:
            feature_to_partition = X[:, 0]
        return np.digitize(feature_to_partition, self.boundaries)


from sklearn.tree import DecisionTreeRegressor


class DecisionTreePartitioner(BasePartitioner):
    """
    Partitions data using a Decision Tree Regressor.
    The partitions are defined by the leaf nodes of the trained tree.
    The `max_leaf_nodes` parameter of the DecisionTreeRegressor is used to control
    the number of partitions, which should roughly match `n_partitions`.
    """

    def __init__(
        self,
        n_partitions: int,
        random_state: Optional[int] = 42,
        tree_params: Optional[Dict] = None,
    ):
        super().__init__(n_partitions)
        self.random_state = random_state
        default_tree_params = {
            "max_leaf_nodes": self.n_partitions,
            "random_state": self.random_state,
        }
        if tree_params:
            default_tree_params.update(tree_params)
        self.tree_model = DecisionTreeRegressor(**default_tree_params)
        # Map leaf node IDs to partition indices (0 to n_partitions-1)
        self.leaf_id_to_partition_idx: Dict[int, int] = {}

    def fit(
        self, X: np.ndarray, y: Optional[np.ndarray] = None
    ) -> "DecisionTreePartitioner":
        if y is None:
            raise ValueError(
                "DecisionTreePartitioner requires target variable y for fitting."
            )
        # Ensure X is 2D
        if X.ndim == 1:
            X_processed = X.reshape(-1, 1)
        else:
            X_processed = X

        self.tree_model.fit(X_processed, y)

        # After fitting, map the unique leaf IDs generated by the tree to partition indices
        # The number of actual leaf nodes might differ slightly from n_partitions requested
        leaf_ids = self.tree_model.apply(X_processed)
        unique_leaf_ids = np.unique(leaf_ids)
        self.n_partitions = len(unique_leaf_ids)  # Update actual number of partitions
        self.leaf_id_to_partition_idx = {
            leaf_id: i for i, leaf_id in enumerate(unique_leaf_ids)
        }

        self.fitted = True
        return self

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError(
                "DecisionTreePartitioner has not been fitted. Call fit() first."
            )
        if X.ndim == 1:
            X_processed = X.reshape(-1, 1)
        else:
            X_processed = X

        leaf_indices = self.tree_model.apply(X_processed)
        # Convert tree leaf indices to our 0-based partition indices
        partition_indices = np.array(
            [self.leaf_id_to_partition_idx.get(leaf_id, -1) for leaf_id in leaf_indices]
        )
        if np.any(partition_indices == -1):
            # This might happen if a leaf ID appears during predict that wasn't in fit (unlikely with DT)
            logger.warning(
                "Encountered unknown leaf ID during prediction for DecisionTreePartitioner."
            )
            # Fallback: assign to a default partition, e.g., 0, or handle as error
            # For now, let's map unknown to partition 0, though this should be rare.
            partition_indices[partition_indices == -1] = 0
        return partition_indices

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params.update(self.tree_model.get_params())
        return params


# Special NoPartitioner class for the NONE mode
class NoPartitioner(BasePartitioner):
    """A trivial partitioner that treats the entire dataset as a single partition."""

    def __init__(self, n_partitions: int = 1):
        super().__init__(n_partitions=1)  # Always 1 partition

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "NoPartitioner":
        """
        Fit method for NoPartitioner. Does nothing as there's no partitioning.
        """
        self.fitted = True
        return self

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        """
        Predicts partition index. Always returns 0 for all samples.
        """
        if not self.fitted:
            raise RuntimeError("NoPartitioner has not been fitted. Call fit() first.")
        return np.zeros(X.shape[0], dtype=int)


class KMeansPlusPlusPartitioner(BasePartitioner):
    """
    Partitions data using K-Means++ clustering.

    A specialized version of KMeans that uses the k-means++ initialization method,
    which initializes cluster centers to be distant from each other. This generally
    leads to better convergence and more consistent results.

    Each cluster found by K-Means++ defines a separate partition.
    The `fit` method trains the K-Means++ model, and `predict_partition` assigns
    new samples to the nearest cluster centroid.

    Attributes (in addition to BasePartitioner):
        kmeans_model (KMeans): The fitted scikit-learn KMeans model with k-means++ initialization.
        random_state (Optional[int]): Random state for reproducibility of KMeans.
    """

    def __init__(self, n_partitions: int, random_state: Optional[int] = 42):
        super().__init__(n_partitions)
        self.random_state = random_state
        self.kmeans_model = KMeans(
            n_clusters=self.n_partitions,
            init="k-means++",  # Use k-means++ initialization
            n_init=10,
            random_state=self.random_state,
        )

    def fit(
        self, X: np.ndarray, y: Optional[np.ndarray] = None
    ) -> "KMeansPlusPlusPartitioner":
        """Fits the K-Means++ model to X."""
        # Ensure X is 2D for KMeans
        if X.ndim == 1:
            X_processed = X.reshape(-1, 1)
        else:
            X_processed = X
        self.kmeans_model.fit(X_processed)
        self.fitted = True
        return self

    def predict_partition(self, X: np.ndarray) -> np.ndarray:
        """Predicts the partition labels for X."""
        if not self.fitted:
            raise ValueError("Partitioner has not been fitted yet")

        # Ensure X is 2D for KMeans
        if X.ndim == 1:
            X_processed = X.reshape(-1, 1)
        else:
            X_processed = X

        return self.kmeans_model.predict(X_processed)

    def get_params(self) -> Dict[str, Any]:
        params = super().get_params()
        params.update(self.kmeans_model.get_params())
        return params


def get_partitioner_by_mode(
    partition_mode: PartitionMode,
    n_partitions: int,
    random_state: Optional[int] = 42,  # Common param for KMEANS, KMEDOIDS, DT
    **kwargs,  # For other partitioner-specific params
) -> BasePartitioner:
    """
    Factory function to get a partitioner instance based on PartitionMode.

    Args:
        partition_mode: The `PartitionMode` enum member.
        n_partitions: The desired number of partitions.
        random_state: Random state for stochastic partitioners.
        **kwargs: Additional keyword arguments for specific partitioner initializations
                  (e.g., `tree_params` for `DecisionTreePartitioner`).

    Returns:
        An instance of a `BasePartitioner` subclass.

    Raises:
        ValueError: If an unsupported `partition_mode` is provided.
    """
    if partition_mode == PartitionMode.NONE:
        return NoPartitioner(n_partitions=1)
    elif partition_mode == PartitionMode.KMEANS:
        return KMeansPartitioner(n_partitions, random_state=random_state)
    elif partition_mode == PartitionMode.KMEANS_PLUS_PLUS:
        return KMeansPlusPlusPartitioner(n_partitions, random_state=random_state)
    elif partition_mode == PartitionMode.PERCENTILE:
        return PercentilePartitioner(n_partitions)
    elif partition_mode == PartitionMode.RANGE:
        return RangePartitioner(n_partitions)
    elif partition_mode == PartitionMode.DECISION_TREE:
        return DecisionTreePartitioner(
            n_partitions,
            random_state=random_state,
            tree_params=kwargs.get("tree_params"),
        )
    # Add KMedoids, MiniBatchKMeans, EqualWidth here if classes are defined
    # elif partition_mode == PartitionMode.KMEDOIDS:
    #     if not KMEDOIDS_AVAILABLE:
    #         raise ImportError("KMEDOids requires sklearn_extra. Install with: pip install scikit-learn-extra")
    #     return KMedoidsPartitioner(n_partitions, random_state=random_state)
    else:
        raise ValueError(f"Unsupported partition_mode: {partition_mode.value}")


def create_partitions(
    X,
    y=None,
    n_partitions=3,
    partition_mode=PartitionMode.KMEANS,
    partition_params=None,
    random_state=None,
):
    """Creates data partitions based on specified partitioning mode.

    Args:
        X: Input feature data as array-like, shape (n_samples, n_features)
        y: Target values (ignored for unsupervised methods)
        n_partitions: Number of partitions to create (not used by all methods)
        partition_mode: Mode for partitioning (PartitionMode enum)
        partition_params: Additional parameters for the partitioning method
        random_state: Random state for reproducible results

    Returns:
        Dictionary containing partition information:
            'partition_indices': List of arrays containing indices for each partition
            'labels': Array with partition label for each sample
            'boundaries': Dictionary with partition boundaries (if applicable)
            'centers': Cluster centers (if applicable)
    """
    # Convert string to enum if needed
    if isinstance(partition_mode, str):
        partition_mode = PartitionMode(partition_mode)

    # Initialize parameters if not provided
    if partition_params is None:
        partition_params = {}

    # Perform partitioning based on chosen mode
    if partition_mode == PartitionMode.KMEANS:
        # K-means clustering
        n_clusters = partition_params.get("n_clusters", n_partitions)
        random_state_val = partition_params.get("random_state", random_state or 42)

        # Create KMeans model
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state_val)
        labels = kmeans.fit_predict(X)

        # Get cluster centers and indices for each partition
        centers = kmeans.cluster_centers_
        partition_indices = [np.where(labels == i)[0] for i in range(n_clusters)]

        return {
            "partition_indices": partition_indices,
            "labels": labels,
            "n_clusters": n_clusters,
            "centers": centers,
            "kmeans_model": kmeans,
        }
    elif partition_mode == PartitionMode.KMEANS_PLUS_PLUS:
        # K-means++ clustering (improved initialization)
        n_clusters = partition_params.get("n_clusters", n_partitions)
        random_state_val = partition_params.get("random_state", random_state or 42)

        # Create KMeans model with k-means++ initialization
        kmeans = KMeans(
            n_clusters=n_clusters, init="k-means++", random_state=random_state_val
        )
        labels = kmeans.fit_predict(X)

        # Get cluster centers and indices for each partition
        centers = kmeans.cluster_centers_
        partition_indices = [np.where(labels == i)[0] for i in range(n_clusters)]

        return {
            "partition_indices": partition_indices,
            "labels": labels,
            "n_clusters": n_clusters,
            "centers": centers,
            "kmeans_model": kmeans,
        }
    elif partition_mode == PartitionMode.PERCENTILE:
        # ... existing PERCENTILE implementation ...
        pass
    elif partition_mode == PartitionMode.RANGE:
        # ... existing RANGE implementation ...
        pass
    elif partition_mode == PartitionMode.GRID:
        # ... existing GRID implementation ...
        pass
    elif partition_mode == PartitionMode.DBSCAN:
        # Default parameters for DBSCAN
        eps = partition_params.get("eps", 0.5)
        min_samples = partition_params.get("min_samples", 5)

        # Import DBSCAN from sklearn
        from sklearn.cluster import DBSCAN

        # Fit DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)

        # Handle noise points (labeled as -1)
        unique_labels = np.unique(labels)

        # If all points are noise, create a single partition
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            logger.warning(
                "DBSCAN classified all points as noise. Using a single partition."
            )
            labels = np.zeros(len(X), dtype=int)

        # Create a separate partition for noise points if they exist
        if -1 in unique_labels:
            # Remap labels to start from 0 (noise) and increment others
            new_labels = labels.copy()
            for i, label in enumerate(unique_labels):
                if label >= 0:  # Skip noise label (-1)
                    new_labels[labels == label] = i
            labels = new_labels

        # Get indices for each partition
        unique_labels = np.unique(labels)
        partition_indices = [np.where(labels == label)[0] for label in unique_labels]

        # Store the number of clusters found
        n_clusters = len(unique_labels)
        logger.info(f"DBSCAN found {n_clusters} clusters/partitions.")

        result = {
            "partition_indices": partition_indices,
            "labels": labels,
            "n_clusters": n_clusters,
            "dbscan_model": dbscan,
        }

    elif partition_mode == PartitionMode.OPTICS:
        # Default parameters for OPTICS
        min_samples = partition_params.get("min_samples", 5)
        max_eps = partition_params.get("max_eps", float("inf"))
        cluster_method = partition_params.get("cluster_method", "xi")
        xi = partition_params.get("xi", 0.05)

        # Import OPTICS from sklearn
        from sklearn.cluster import OPTICS

        # Fit OPTICS
        optics = OPTICS(
            min_samples=min_samples,
            max_eps=max_eps,
            cluster_method=cluster_method,
            xi=xi,
        )
        labels = optics.fit_predict(X)

        # Handle noise points (labeled as -1)
        unique_labels = np.unique(labels)

        # If all points are noise, create a single partition
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            logger.warning(
                "OPTICS classified all points as noise. Using a single partition."
            )
            labels = np.zeros(len(X), dtype=int)

        # Create a separate partition for noise points if they exist
        if -1 in unique_labels:
            # Remap labels to start from 0 (noise) and increment others
            new_labels = labels.copy()
            for i, label in enumerate(unique_labels):
                if label >= 0:  # Skip noise label (-1)
                    new_labels[labels == label] = i
            labels = new_labels

        # Get indices for each partition
        unique_labels = np.unique(labels)
        partition_indices = [np.where(labels == label)[0] for label in unique_labels]

        # Store the number of clusters found
        n_clusters = len(unique_labels)
        logger.info(f"OPTICS found {n_clusters} clusters/partitions.")

        result = {
            "partition_indices": partition_indices,
            "labels": labels,
            "n_clusters": n_clusters,
            "optics_model": optics,
            "reachability": optics.reachability_,
        }
    else:
        raise ValueError(f"Unsupported partition mode: {partition_mode}")

    return result


def partition_data(
    X: np.ndarray,
    y: np.ndarray,
    partition_mode: PartitionMode,
    n_partitions: int = 3,
    min_partition_size: int = 50,
    random_state: Optional[int] = None,
) -> Tuple[List[np.ndarray], List[np.ndarray], List[float]]:
    """
    Partition data into multiple subsets based on specified partitioning mode.

    Args:
        X: Input features array
        y: Target values array
        partition_mode: Mode for partitioning (KMEANS, PERCENTILE, RANGE, etc.)
        n_partitions: Number of partitions to create
        min_partition_size: Minimum number of samples required in each partition
        random_state: Random state for reproducibility in stochastic methods

    Returns:
        Tuple containing:
        - List of feature arrays for each partition
        - List of target arrays for each partition
        - List of boundary values used for partitioning
    """
    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # Get partition boundaries
    boundaries = get_partition_boundaries(
        X, partition_mode, n_partitions, min_size=min_partition_size
    )

    # Get partition masks
    masks = get_partition_masks(X, boundaries)

    # Create X and y partitions based on masks
    X_partitions = []
    y_partitions = []

    for mask in masks:
        if np.sum(mask) >= min_partition_size:
            X_partitions.append(X[mask])
            y_partitions.append(y[mask])
        else:
            logger.warning(f"Skipping partition with only {np.sum(mask)} samples")

    return X_partitions, y_partitions, boundaries


def create_partition_boundaries(
    X: np.ndarray,
    partition_mode: PartitionMode,
    n_partitions: int = 3,
    min_partition_size: int = 50,
    random_state: Optional[int] = None,
    **kwargs,
) -> List[float]:
    """
    Create partition boundaries based on the specified mode.
    This is a wrapper around get_partition_boundaries with additional parameters.

    Args:
        X: Features array
        partition_mode: Mode for partitioning
        n_partitions: Number of partitions to create
        min_partition_size: Minimum size for each partition
        random_state: Random seed for reproducibility
        **kwargs: Additional arguments to pass to get_partition_boundaries

    Returns:
        List of boundary values
    """
    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    # Call the underlying function
    boundaries = get_partition_boundaries(
        X, partition_mode, n_partitions, min_size=min_partition_size, **kwargs
    )

    return boundaries


def get_partition_boundary_names(
    boundaries: List[float], feature_name: str = "X"
) -> List[str]:
    """
    Get human-readable descriptions of partition boundaries.

    Args:
        boundaries: List of boundary values
        feature_name: Name of the feature being partitioned

    Returns:
        List of human-readable boundary names
    """
    boundary_names = []

    # Add first boundary: (-inf, boundary[0]]
    if boundaries and len(boundaries) > 0:
        boundary_names.append(f"{feature_name} ≤ {boundaries[0]:.4g}")

        # Add middle boundaries: (boundary[i-1], boundary[i]]
        for i in range(1, len(boundaries)):
            boundary_names.append(
                f"{boundaries[i-1]:.4g} < {feature_name} ≤ {boundaries[i]:.4g}"
            )

        # Add last boundary: (boundary[-1], inf)
        boundary_names.append(f"{feature_name} > {boundaries[-1]:.4g}")
    else:
        # No boundaries - single partition
        boundary_names.append("All data")

    return boundary_names


def transform_data_with_partitions(
    X: np.ndarray, boundaries: List[float], add_indicator: bool = True
) -> np.ndarray:
    """
    Transform data by adding partition indicators.

    Args:
        X: Features array
        boundaries: List of boundary values
        add_indicator: Whether to add partition indicator column
    """


def find_best_partition(
    X: np.ndarray,
    y: np.ndarray,
    regressor_type: RegressorType,
    n_partitions_list: List[int],
    partition_mode: PartitionMode,
    test_size: float = 0.2,
    random_state: Optional[int] = None,
    n_jobs: int = 1,
    min_partition_size: int = 50,
    evaluation_metric: Union[str, Callable] = "r2",
    **kwargs,
) -> Dict[str, Any]:
    """
    Find the best number of partitions for a given partition mode and regressor.

    Args:
        X: Features array
        y: Target values array
        regressor_type: Type of regressor to use
        n_partitions_list: List of partition counts to evaluate
        partition_mode: Mode for partitioning
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        n_jobs: Number of parallel jobs
        min_partition_size: Minimum samples per partition
        evaluation_metric: Metric for evaluation ('r2', 'mae', 'rmse', or callable)
        **kwargs: Additional arguments for model training

    Returns:
        Dictionary with results for best number of partitions
    """
    results = []

    # Split data into training and testing sets
    if test_size > 0:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    # Evaluate each number of partitions
    for n_partitions in n_partitions_list:
        logger.info(f"Evaluating {partition_mode} with {n_partitions} partitions")

        # Train models on partitioned data
        models = train_models_on_partitions(
            X_train,
            y_train,
            partition_mode=partition_mode,
            n_partitions=n_partitions,
            regressor_type=regressor_type,
            min_partition_size=min_partition_size,
            n_jobs=n_jobs,
            **kwargs,
        )

        # Make predictions
        y_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

        # Calculate metrics
        metrics = {
            "r2": r2_score(y_test, y_pred),
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        }

        # Add result
        results.append(
            {
                "n_partitions": n_partitions,
                "partition_mode": partition_mode,
                "regressor_type": regressor_type,
                "models": models,
                "metrics": metrics,
                "predictions": y_pred,
            }
        )

        logger.info(
            f"Results for {n_partitions} partitions: R2={metrics['r2']:.4f}, MAE={metrics['mae']:.4f}"
        )

    # Find best result
    if evaluation_metric == "r2":
        best_idx = np.argmax([r["metrics"]["r2"] for r in results])
    elif evaluation_metric == "mae":
        best_idx = np.argmin([r["metrics"]["mae"] for r in results])
    elif evaluation_metric == "rmse":
        best_idx = np.argmin([r["metrics"]["rmse"] for r in results])
    elif callable(evaluation_metric):
        scores = [evaluation_metric(y_test, r["predictions"]) for r in results]
        best_idx = np.argmax(scores)
    else:
        raise ValueError(f"Invalid evaluation metric: {evaluation_metric}")

    best_result = results[best_idx]
    logger.info(
        f"Best result: {best_result['n_partitions']} partitions with "
        f"R2={best_result['metrics']['r2']:.4f}, MAE={best_result['metrics']['mae']:.4f}"
    )

    return best_result


def compare_partitioning_methods(
    X: np.ndarray,
    y: np.ndarray,
    partition_modes: List[PartitionMode],
    regressor_type: RegressorType,
    n_partitions_list: List[int],
    test_size: float = 0.2,
    random_state: Optional[int] = None,
    n_jobs: int = 1,
    min_partition_size: int = 50,
    evaluation_metric: Union[str, Callable] = "r2",
    output_dir: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Compare different partitioning methods to find the best combination.

    Args:
        X: Features array
        y: Target values array
        partition_modes: List of partition modes to evaluate
        regressor_type: Type of regressor to use
        n_partitions_list: List of partition counts to evaluate
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        n_jobs: Number of parallel jobs
        min_partition_size: Minimum samples per partition
        evaluation_metric: Metric for evaluation ('r2', 'mae', 'rmse', or callable)
        output_dir: Directory to save results
        **kwargs: Additional arguments for model training

    Returns:
        Dictionary with results for best partition mode
    """
    all_results = []

    # Split data into training and testing sets once
    if test_size > 0:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    # Evaluate each partition mode
    for partition_mode in partition_modes:
        logger.info(f"Evaluating partition mode: {partition_mode}")

        # Find best number of partitions for this mode
        best_result = find_best_partition(
            X_train,
            y_train,
            regressor_type=regressor_type,
            n_partitions_list=n_partitions_list,
            partition_mode=partition_mode,
            test_size=0.2,  # Further split training data
            random_state=random_state,
            n_jobs=n_jobs,
            min_partition_size=min_partition_size,
            evaluation_metric=evaluation_metric,
            **kwargs,
        )

        # Retrain on full training set with best number of partitions
        n_partitions = best_result["n_partitions"]
        logger.info(
            f"Retraining {partition_mode} with {n_partitions} partitions on full training set"
        )

        models = train_models_on_partitions(
            X_train,
            y_train,
            partition_mode=partition_mode,
            n_partitions=n_partitions,
            regressor_type=regressor_type,
            min_partition_size=min_partition_size,
            n_jobs=n_jobs,
            **kwargs,
        )

        # Make final predictions
        y_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

        # Calculate final metrics
        metrics = {
            "r2": r2_score(y_test, y_pred),
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        }

        # Save result
        result = {
            "partition_mode": partition_mode,
            "regressor_type": regressor_type,
            "n_partitions": n_partitions,
            "models": models,
            "metrics": metrics,
            "predictions": y_pred,
        }
        all_results.append(result)

        logger.info(
            f"Final result for {partition_mode}: "
            f"R2={metrics['r2']:.4f}, MAE={metrics['mae']:.4f}"
        )

    # Find best partition mode overall
    if evaluation_metric == "r2":
        best_idx = np.argmax([r["metrics"]["r2"] for r in all_results])
    elif evaluation_metric == "mae":
        best_idx = np.argmin([r["metrics"]["mae"] for r in all_results])
    elif evaluation_metric == "rmse":
        best_idx = np.argmin([r["metrics"]["rmse"] for r in all_results])
    elif callable(evaluation_metric):
        scores = [evaluation_metric(y_test, r["predictions"]) for r in all_results]
        best_idx = np.argmax(scores)
    else:
        raise ValueError(f"Invalid evaluation metric: {evaluation_metric}")

    best_result = all_results[best_idx]
    logger.info(
        f"Best overall: {best_result['partition_mode']} with {best_result['n_partitions']} partitions, "
        f"R2={best_result['metrics']['r2']:.4f}, MAE={best_result['metrics']['mae']:.4f}"
    )

    # Save results to output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        # Create summary table
        results_table = []
        for r in all_results:
            results_table.append(
                {
                    "partition_mode": r["partition_mode"].value,
                    "n_partitions": r["n_partitions"],
                    "r2": r["metrics"]["r2"],
                    "mae": r["metrics"]["mae"],
                    "rmse": r["metrics"]["rmse"],
                }
            )

        # Save as CSV
        import pandas as pd

        pd.DataFrame(results_table).to_csv(
            os.path.join(output_dir, "partition_comparison_results.csv"), index=False
        )

        # Also save best model
        best_model_dir = os.path.join(
            output_dir, f"best_model_{best_result['partition_mode'].value}"
        )
        os.makedirs(best_model_dir, exist_ok=True)

        for i, model in enumerate(best_result["models"]):
            if "model" in model:
                try:
                    # Use joblib to save the model instead of save_model
                    model_path = os.path.join(
                        best_model_dir, f"model_partition_{i}.pkl"
                    )
                    joblib.dump(model["model"], model_path)
                    logger.info(f"Saved model for partition {i} to {model_path}")
                except Exception as e:
                    logger.warning(f"Could not save model for partition {i}: {e}")

    return best_result
