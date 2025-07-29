"""\nScikit-learn Integrated Models and Utilities for Fit Better\n=========================================================\n\nThis module provides `fit_better` functionalities integrated with scikit-learn's\npipeline, meta-estimator, and model selection features. It aims to offer a more\n`sklearn`-idiomatic way to use partitioning and adaptive modeling concepts.\n\nKey Components:\n---------------\n\n*   **`RegressorType` (Enum, re-exported)**: Defines the types of regression algorithms\n    available, such as `LINEAR`, `RANDOM_FOREST`, `GRADIENT_BOOSTING`, etc.\n    Each type corresponds to a specific scikit-learn regressor.\n    See `fit_better.core.models.RegressorType` for detailed algorithm descriptions,\n    theory, pros, and cons.\n\n*   **`PartitionMode` (Enum, re-exported)**: Defines strategies for partitioning data,\n    like `KMEANS`, `PERCENTILE`. See `fit_better.core.partitioning.PartitionMode`\n    for detailed algorithm descriptions, theory, pros, and cons for each mode.\n\n*   **`PartitionTransformer(BaseEstimator, TransformerMixin)`**: A scikit-learn compatible\n    transformer that partitions input data based on specified features (typically the first one)\n    and a chosen `partition_mode`. It determines partition boundaries during `fit` and adds a\n    new column with partition indices during `transform`. This can be used as a preprocessing\n    step in a scikit-learn `Pipeline`. Supports a `random_state` parameter for reproducible clustering results, particularly important for KMeans and KMeans++ partition modes.

*   **`AdaptivePartitionRegressor(BaseEstimator)`**: A meta-estimator that implements the core\n    `fit_better` idea of fitting different models to different partitions of the data.\n    It uses `PartitionTransformer` (or similar logic) to divide the data and then trains a\n    `base_estimator` (or a selection of estimators if `base_estimator` is None) on each partition.\n    During prediction, it routes new data points to the appropriate partition-specific model.\n
    *   **Theory**: Combines data partitioning with model specialization. It assumes that different\n        underlying data-generating processes may exist in different regions of the feature space.\n        By training separate, potentially simpler, models on these more homogeneous partitions,\n        the overall predictive performance can be improved compared to a single global model.\n    *   **Pros**: Can capture complex, non-linear relationships that a single global model might miss.\n        Improved accuracy on heterogeneous datasets. Allows using the best-suited regressor type for each partition.\n    *   **Cons**: More complex to train and manage than a single model. Risk of overfitting if partitions are too small\n        or if partition boundaries are poorly chosen. Increased number of models to maintain.\n        Interpretability can be more challenging.\n
*   **Helper Functions** (e.g., `train_adaptive_model`, `create_ensemble_model`, `create_stacking_model`):\n    These functions provide convenient wrappers to set up and train specific configurations of\n    adaptive or ensemble models using partitioning.\n
*   **`PolyPartitionPipeline`**: An example of a custom pipeline class that combines polynomial feature\n    generation with partitioning and regression. This demonstrates how to build more complex custom\n    workflows using the provided components.\n
*   **`evaluate_model`**: A utility function to calculate and print common regression metrics (R², MSE, RMSE, MAE)\n    for a given model and test data.\n
This module bridges `fit_better`'s advanced regression strategies with the familiar scikit-learn API,
allowing for easier integration into existing `sklearn`-based machine learning workflows.\n
Author: hi@xlindo.com
Create Time: 2025-05-10
"""

import numpy as np
import logging
from enum import Enum
from typing import Dict, List, Union, Optional, Tuple, Any

from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.cluster import KMeans, DBSCAN, OPTICS
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    VotingRegressor,
    StackingRegressor,
)
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

# Re-export the existing Enum classes for compatibility
from fit_better.core.models import Metric, RegressorType
from fit_better.core.partitioning import PartitionMode


class PartitionTransformer(BaseEstimator, TransformerMixin):
    """
    A transformer that partitions data based on X values and fits a separate model for each partition.
    This is a scikit-learn compatible transformer that implements the core partitioning functionality.
    """

    def __init__(
        self,
        n_parts: int = 3,
        partition_mode: Union[str, PartitionMode] = "kmeans",
        min_samples_per_partition: int = 50,
        random_state: Optional[int] = 42,
    ):
        """
        Initialize the PartitionTransformer.

        Args:
            n_parts: Number of partitions to create
            partition_mode: Method to use for partitioning ('kmeans', 'percentile', etc.)
            min_samples_per_partition: Minimum samples required in each partition
            random_state: Random state for reproducibility
        """
        self.n_parts = n_parts
        self.partition_mode = (
            partition_mode if isinstance(partition_mode, str) else partition_mode.value
        )
        self.min_samples_per_partition = min_samples_per_partition
        self.random_state = random_state
        self.boundaries_ = None
        self.models_ = None

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        """
        Fit the partitioning transformer by determining partition boundaries.

        Args:
            X: Features array, first column used for partitioning
            y: Target values (not used for boundary determination)

        Returns:
            self
        """
        # Extract the first column for partitioning if X is multidimensional
        X_part = X[:, 0] if X.ndim > 1 else X

        # Create boundaries based on partition mode
        if (
            self.partition_mode == "kmeans"
            or self.partition_mode == PartitionMode.KMEANS.value
        ):
            self._create_kmeans_boundaries(X_part)
        elif (
            self.partition_mode == "kmeans++"
            or self.partition_mode == PartitionMode.KMEANS_PLUS_PLUS.value
        ):
            self._create_kmeans_plus_plus_boundaries(X_part)
        elif (
            self.partition_mode == "percentile"
            or self.partition_mode == PartitionMode.PERCENTILE.value
        ):
            self._create_percentile_boundaries(X_part)
        elif (
            self.partition_mode == "range"
            or self.partition_mode == PartitionMode.RANGE.value
        ):
            self._create_range_boundaries(X_part)
        else:
            raise ValueError(f"Unsupported partition mode: {self.partition_mode}")

        # Enforce minimum partition size
        self._enforce_min_partition_size(X_part)

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform the data by adding partition indicators.

        Args:
            X: Features array

        Returns:
            X with an additional column indicating partition membership
        """
        # Extract the first column for partitioning if X is multidimensional
        X_part = X[:, 0] if X.ndim > 1 else X

        # Create partition indicators
        partition_indicators = np.zeros(len(X_part), dtype=int)

        if self.boundaries_ is not None and len(self.boundaries_) > 0:
            for i in range(len(self.boundaries_) + 1):
                if i == 0:
                    mask = X_part <= self.boundaries_[0]
                elif i == len(self.boundaries_):
                    mask = X_part > self.boundaries_[-1]
                else:
                    mask = (X_part > self.boundaries_[i - 1]) & (
                        X_part <= self.boundaries_[i]
                    )
                partition_indicators[mask] = i

        # Add partition indicators as a new column
        if X.ndim > 1:
            return np.column_stack((X, partition_indicators))
        else:
            return np.column_stack((X.reshape(-1, 1), partition_indicators))

    def _create_kmeans_boundaries(self, X: np.ndarray):
        """Create boundaries using KMeans clustering."""
        X_reshaped = X.reshape(-1, 1)
        kmeans = KMeans(n_clusters=self.n_parts, random_state=self.random_state)
        kmeans.fit(X_reshaped)

        # Get cluster centers and sort them
        centers = sorted(kmeans.cluster_centers_.ravel())

        # Create boundaries as midpoints between adjacent cluster centers
        self.boundaries_ = [
            (centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)
        ]

    def _create_kmeans_plus_plus_boundaries(self, X: np.ndarray):
        """Create boundaries using KMeans++ clustering."""
        X_reshaped = X.reshape(-1, 1)
        kmeans = KMeans(
            n_clusters=self.n_parts, init="k-means++", random_state=self.random_state
        )
        kmeans.fit(X_reshaped)

        # Get cluster centers and sort them
        centers = sorted(kmeans.cluster_centers_.ravel())

        # Create boundaries as midpoints between adjacent cluster centers
        self.boundaries_ = [
            (centers[i] + centers[i + 1]) / 2 for i in range(len(centers) - 1)
        ]

    def _create_percentile_boundaries(self, X: np.ndarray):
        """Create boundaries using percentiles."""
        percentiles = np.linspace(0, 100, self.n_parts + 1)[1:-1]
        self.boundaries_ = np.percentile(X, percentiles).tolist()

    def _create_range_boundaries(self, X: np.ndarray):
        """Create boundaries by dividing the range into equal parts."""
        min_val, max_val = np.min(X), np.max(X)
        step = (max_val - min_val) / self.n_parts
        self.boundaries_ = [min_val + step * (i + 1) for i in range(self.n_parts - 1)]

    def _enforce_min_partition_size(self, X: np.ndarray):
        """Ensure each partition has at least min_samples_per_partition samples."""
        if self.boundaries_ is None or len(self.boundaries_) == 0:
            return

        boundaries = list(self.boundaries_)

        while True:
            # Count samples in each partition
            counts = []
            for i in range(len(boundaries) + 1):
                if i == 0:
                    mask = X <= boundaries[0]
                elif i == len(boundaries):
                    mask = X > boundaries[-1]
                else:
                    mask = (X > boundaries[i - 1]) & (X <= boundaries[i])
                counts.append(np.sum(mask))

            # Find small partitions
            small_idxs = [
                i
                for i, count in enumerate(counts)
                if count < self.min_samples_per_partition
            ]

            if not small_idxs:
                break

            # Merge a small partition
            for idx in small_idxs:
                if len(boundaries) == 0:
                    break
                if idx == 0:
                    # Merge first partition with second
                    boundaries.pop(0)
                elif idx == len(boundaries):
                    # Merge last partition with second-to-last
                    boundaries.pop(-1)
                else:
                    # Merge with larger neighbor
                    left_count = counts[idx - 1]
                    right_count = counts[idx + 1] if idx < len(counts) - 1 else 0
                    if left_count >= right_count:
                        boundaries.pop(idx - 1)
                    else:
                        boundaries.pop(idx)
                break

        self.boundaries_ = boundaries


class AdaptivePartitionRegressor(BaseEstimator):
    """
    A meta-estimator that fits different models to different partitions of the data.
    This is a scikit-learn compatible regressor that implements fit_better's core functionality.
    """

    def __init__(
        self,
        base_estimator=None,
        n_parts: int = 3,
        partition_mode: Union[str, PartitionMode] = "kmeans",
        cv: int = 5,
        scoring: str = "neg_mean_absolute_error",
        n_jobs: int = 1,
        partitioner=None,
        random_state: Optional[int] = 42,
    ):
        """
        Initialize the AdaptivePartitionRegressor.

        Args:
            base_estimator: The base estimator to use for each partition (if None, will try multiple)
            n_parts: Number of partitions to create
            partition_mode: Method for partitioning ('kmeans', 'percentile', etc.)
            cv: Cross-validation folds for model selection
            scoring: Scoring metric for model selection
            n_jobs: Number of parallel jobs
            partitioner: A custom partitioner to use instead of the default PartitionTransformer
                        (must implement fit and transform methods)
            random_state: Random state for reproducibility in clustering-based partitioning
        """
        self.base_estimator = base_estimator
        self.n_parts = n_parts
        self.partition_mode = partition_mode
        self.cv = cv
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.partitioner = partitioner
        self.random_state = random_state
        self.models_ = None
        self.partitioner_ = None
        self.boundaries_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit the adaptive partition regressor.

        Args:
            X: Features array
            y: Target values

        Returns:
            self
        """
        # Step 1: Create the partitioner and find boundaries
        if self.partitioner is not None:
            # Use the provided custom partitioner
            self.partitioner_ = self.partitioner
            X_with_part = self.partitioner_.fit_transform(X)
            # Try to get boundaries if available
            self.boundaries_ = (
                self.partitioner_.boundaries_
                if hasattr(self.partitioner_, "boundaries_")
                else None
            )
        else:
            # Use the default PartitionTransformer
            self.partitioner_ = PartitionTransformer(
                n_parts=self.n_parts,
                partition_mode=self.partition_mode,
                random_state=self.random_state,
            )
            X_with_part = self.partitioner_.fit_transform(X)
            self.boundaries_ = self.partitioner_.boundaries_

        # Step 2: Fit a model for each partition
        unique_partitions = np.unique(X_with_part[:, -1])
        self.models_ = {}

        for part_idx in unique_partitions:
            # Get data for this partition
            mask = X_with_part[:, -1] == part_idx
            X_part, y_part = X[mask], y[mask]

            if len(X_part) == 0:
                continue

            # If base_estimator is provided, use it
            if self.base_estimator is not None:
                model = clone(self.base_estimator)
                model.fit(X_part, y_part)
                self.models_[part_idx] = model
            else:
                # Try multiple regressors and select the best one
                regressors = {
                    "linear": LinearRegression(),
                    "ridge": Ridge(),
                    "lasso": Lasso(),
                    "svr": SVR(),
                    "knn": KNeighborsRegressor(),
                    "rf": RandomForestRegressor(n_estimators=100, n_jobs=self.n_jobs),
                    "dt": DecisionTreeRegressor(),
                    "gb": GradientBoostingRegressor(),
                }

                pipeline = Pipeline(
                    [
                        ("scaler", StandardScaler()),
                        ("model", None),  # Placeholder, will be set by GridSearchCV
                    ]
                )

                param_grid = [
                    {"model": [regressor] for regressor in regressors.values()}
                ]

                grid_search = GridSearchCV(
                    pipeline,
                    param_grid,
                    cv=min(self.cv, len(X_part)),
                    scoring=self.scoring,
                    n_jobs=self.n_jobs,
                )

                grid_search.fit(X_part, y_part)
                self.models_[part_idx] = grid_search.best_estimator_

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict using the adaptive partition regressor.

        Args:
            X: Features array

        Returns:
            Predicted values
        """
        if self.partitioner_ is None or self.models_ is None:
            raise ValueError("Estimator not fitted. Call 'fit' first.")

        # Transform to get partition indicators
        X_with_part = self.partitioner_.transform(X)

        # Make predictions
        y_pred = np.zeros(len(X))

        for part_idx, model in self.models_.items():
            mask = X_with_part[:, -1] == part_idx
            if np.any(mask):
                y_pred[mask] = model.predict(X[mask])

        return y_pred

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate the coefficient of determination (R^2) of the prediction.

        Args:
            X: Features array
            y: True target values

        Returns:
            R^2 score (coefficient of determination)
        """
        y_pred = self.predict(X)
        return r2_score(y, y_pred)


def train_adaptive_model(
    X, y, n_parts=3, partition_mode="kmeans", n_jobs=1, cv=5, random_state=42
):
    """
    Train an adaptive partition model using scikit-learn features.
    This is a simplified alternative to train_models_on_partitions.

    Args:
        X: Features array
        y: Target values
        n_parts: Number of partitions
        partition_mode: Method for partitioning
        n_jobs: Number of parallel jobs
        cv: Cross-validation folds
        random_state: Random state for reproducibility in clustering-based partitioning

    Returns:
        Fitted AdaptivePartitionRegressor
    """
    model = AdaptivePartitionRegressor(
        n_parts=n_parts,
        partition_mode=partition_mode,
        cv=cv,
        n_jobs=n_jobs,
        random_state=random_state,
    )
    model.fit(X, y)
    return model


def create_ensemble_model(
    X, y, n_parts=3, partition_mode="kmeans", n_jobs=1, random_state=42
):
    """
    Create an ensemble model that combines predictions from different partitioning strategies.

    Args:
        X: Features array
        y: Target values
        n_parts: Number of partitions
        partition_mode: Method for partitioning (if 'auto', tries multiple methods)
        n_jobs: Number of parallel jobs
        random_state: Random state for reproducibility in clustering-based partitioning

    Returns:
        Fitted VotingRegressor combining multiple partition-based models
    """
    # Define partition modes to try
    if partition_mode == "auto":
        partition_modes = ["kmeans", "percentile", "range"]
    else:
        partition_modes = [partition_mode]

    # Create a model for each partition mode
    estimators = []

    for mode in partition_modes:
        model = AdaptivePartitionRegressor(
            n_parts=n_parts,
            partition_mode=mode,
            n_jobs=n_jobs,
            random_state=random_state,
        )
        name = f"{mode}_{n_parts}parts"
        estimators.append((name, model))

    # Create a voting ensemble
    ensemble = VotingRegressor(estimators=estimators, n_jobs=n_jobs)
    ensemble.fit(X, y)

    return ensemble


def create_stacking_model(
    X, y, n_parts=3, partition_mode="kmeans", n_jobs=1, cv=5, random_state=42
):
    """
    Create a stacking ensemble model that combines predictions from different models.

    Args:
        X: Features array
        y: Target values
        n_parts: Number of partitions
        partition_mode: Method for partitioning
        n_jobs: Number of parallel jobs
        cv: Cross-validation folds
        random_state: Random state for reproducibility in clustering-based partitioning

    Returns:
        Fitted StackingRegressor
    """
    # Create base estimators
    base_estimators = [
        ("linear", LinearRegression()),
        (
            "rf",
            RandomForestRegressor(
                n_estimators=100, n_jobs=n_jobs, random_state=random_state
            ),
        ),
        ("gb", GradientBoostingRegressor(random_state=random_state)),
        ("svr", SVR()),
    ]

    # Create the partition transformer
    partitioner = PartitionTransformer(
        n_parts=n_parts, partition_mode=partition_mode, random_state=random_state
    )

    # Create the stacking ensemble with a meta-regressor
    stacking = StackingRegressor(
        estimators=base_estimators, final_estimator=Ridge(), cv=cv, n_jobs=n_jobs
    )

    # Create a pipeline with the partitioner and stacking ensemble
    pipeline = Pipeline([("partitioner", partitioner), ("stacking", stacking)])

    # Fit the pipeline
    pipeline.fit(X, y)

    return pipeline


class PolyPartitionPipeline:
    """
    A utility class that creates a pipeline combining polynomial features and partitioning.
    This offers a simplified interface for the most common use case in fit_better.
    """

    def __init__(
        self,
        poly_degree=2,
        n_parts=3,
        partition_mode="kmeans",
        n_jobs=1,
        random_state=42,
    ):
        """
        Initialize the pipeline.

        Args:
            poly_degree: Polynomial degree
            n_parts: Number of partitions
            partition_mode: Method for partitioning
            n_jobs: Number of parallel jobs
            random_state: Random state for reproducibility in clustering-based partitioning
        """
        self.poly_degree = poly_degree
        self.n_parts = n_parts
        self.partition_mode = partition_mode
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.pipeline = None

    def fit(self, X, y):
        """
        Fit the pipeline on the data.

        Args:
            X: Features array
            y: Target values

        Returns:
            self
        """
        # Create the pipeline
        self.pipeline = Pipeline(
            [
                (
                    "poly",
                    PolynomialFeatures(degree=self.poly_degree, include_bias=False),
                ),
                ("scaler", StandardScaler()),
                (
                    "model",
                    AdaptivePartitionRegressor(
                        n_parts=self.n_parts,
                        partition_mode=self.partition_mode,
                        n_jobs=self.n_jobs,
                        random_state=self.random_state,
                    ),
                ),
            ]
        )

        # Fit the pipeline
        self.pipeline.fit(X, y)

        return self

    def predict(self, X):
        """
        Make predictions with the fitted pipeline.

        Args:
            X: Features array

        Returns:
            Predicted values
        """
        if self.pipeline is None:
            raise ValueError("Pipeline not fitted. Call 'fit' first.")

        return self.pipeline.predict(X)

    def score(self, X, y):
        """
        Score the pipeline on test data.

        Args:
            X: Features array
            y: Target values

        Returns:
            R² score
        """
        if self.pipeline is None:
            raise ValueError("Pipeline not fitted. Call 'fit' first.")

        return self.pipeline.score(X, y)


def evaluate_model(model, X, y_true, prefix="Model"):
    """
    Evaluate a model and return performance metrics.

    Args:
        model: Fitted model with predict method
        X: Features array
        y_true: True target values
        prefix: Prefix for logging output

    Returns:
        Dictionary of metrics
    """
    # Make predictions
    y_pred = model.predict(X)

    # Calculate metrics
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    # Calculate percentage within thresholds
    eps = 1e-10  # To avoid division by zero
    abs_pct_errors = 100.0 * np.abs(y_pred - y_true) / (np.abs(y_true) + eps)
    pct_within_1 = 100.0 * np.mean(abs_pct_errors <= 1.0)
    pct_within_3 = 100.0 * np.mean(abs_pct_errors <= 3.0)
    pct_within_5 = 100.0 * np.mean(abs_pct_errors <= 5.0)
    pct_within_10 = 100.0 * np.mean(abs_pct_errors <= 10.0)

    # Log results
    logging.info(f"{prefix} evaluation: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")
    logging.info(
        f"{prefix} within % thresholds: 1%={pct_within_1:.2f}%, 5%={pct_within_5:.2f}%, 10%={pct_within_10:.2f}%"
    )

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "pct_within_1pct": pct_within_1,
        "pct_within_3pct": pct_within_3,
        "pct_within_5pct": pct_within_5,
        "pct_within_10pct": pct_within_10,
    }


class DBSCANPartitionTransformer(BaseEstimator, TransformerMixin):
    """
    A transformer that partitions data using DBSCAN density-based clustering.

    DBSCAN (Density-Based Spatial Clustering of Applications with Noise) is a density-based
    clustering algorithm that groups together points that are closely packed together,
    marking as outliers points that lie alone in low-density regions.

    This transformer is compatible with scikit-learn pipelines and can be used in conjunction
    with AdaptivePartitionRegressor for flexible, density-based adaptive modeling.
    """

    def __init__(
        self,
        eps=0.5,
        min_samples=5,
        metric="euclidean",
        algorithm="auto",
        leaf_size=30,
        n_jobs=None,
    ):
        """
        Initialize the DBSCANPartitionTransformer.

        Args:
            eps: The maximum distance between two samples for one to be considered
                 as in the neighborhood of the other.
            min_samples: The number of samples in a neighborhood for a point to be
                         considered as a core point (from which a cluster can be expanded).
            metric: The metric to use when calculating distance between instances.
            algorithm: The algorithm to be used ('auto', 'ball_tree', 'kd_tree', or 'brute').
            leaf_size: Leaf size passed to BallTree or KDTree if those algorithms are used.
            n_jobs: The number of parallel jobs to run for neighbors search.
        """
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.n_jobs = n_jobs
        self.dbscan_ = None
        self.labels_ = None
        self.n_clusters_ = 0

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        """
        Fit the DBSCAN transformer by determining cluster assignments.

        Args:
            X: Features array
            y: Target values (not used for clustering)

        Returns:
            self
        """
        # Fit DBSCAN
        self.dbscan_ = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric=self.metric,
            algorithm=self.algorithm,
            leaf_size=self.leaf_size,
            n_jobs=self.n_jobs,
        )
        self.labels_ = self.dbscan_.fit_predict(X)

        # Handle noise points (labeled as -1)
        unique_labels = np.unique(self.labels_)

        # If all points are noise, create a single partition
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            logging.warning(
                "DBSCAN classified all points as noise. Using a single partition."
            )
            self.labels_ = np.zeros(len(X), dtype=int)

        # Get the number of clusters found (excluding noise)
        self.n_clusters_ = len([label for label in unique_labels if label != -1])

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform the data by adding cluster membership indicators.

        Args:
            X: Features array

        Returns:
            X with an additional column indicating cluster membership
        """
        if self.dbscan_ is None:
            raise ValueError("DBSCANPartitionTransformer has not been fitted yet.")

        # Predict cluster labels for new data
        if hasattr(self.dbscan_, "predict"):
            # Some implementations might provide a predict method
            labels = self.dbscan_.predict(X)
        else:
            # Otherwise, refit DBSCAN with the new data (less accurate)
            # This is a limitation of DBSCAN which doesn't have a native predict method
            temp_dbscan = DBSCAN(
                eps=self.eps,
                min_samples=self.min_samples,
                metric=self.metric,
                algorithm=self.algorithm,
                leaf_size=self.leaf_size,
                n_jobs=self.n_jobs,
            )
            labels = temp_dbscan.fit_predict(X)

        # Add cluster indicators as a new column
        return np.column_stack((X, labels))

    def get_n_clusters(self):
        """Get the number of clusters found by DBSCAN, excluding noise points."""
        return self.n_clusters_


class OPTICSPartitionTransformer(BaseEstimator, TransformerMixin):
    """
    A transformer that partitions data using OPTICS density-based clustering.

    OPTICS (Ordering Points To Identify the Clustering Structure) is a density-based
    clustering algorithm that creates an augmented ordering of the data points
    based on their reachability distance. It addresses some limitations of DBSCAN,
    particularly the difficulty in detecting clusters of varying densities.

    This transformer is compatible with scikit-learn pipelines and can be used in conjunction
    with AdaptivePartitionRegressor for flexible, density-based adaptive modeling.
    """

    def __init__(
        self,
        min_samples=5,
        max_eps=float("inf"),
        metric="euclidean",
        p=2,
        algorithm="auto",
        leaf_size=30,
        cluster_method="xi",
        xi=0.05,
        n_jobs=None,
    ):
        """
        Initialize the OPTICSPartitionTransformer.

        Args:
            min_samples: The number of samples in a neighborhood for a point to be
                         considered as a core point.
            max_eps: The maximum distance between two samples for one to be considered
                     as in the neighborhood of the other. Default=np.inf.
            metric: The metric to use when calculating distance between instances.
            p: Parameter for the Minkowski metric.
            algorithm: The algorithm to be used ('auto', 'ball_tree', 'kd_tree', or 'brute').
            leaf_size: Leaf size passed to BallTree or KDTree if those algorithms are used.
            cluster_method: The method used to extract clusters from the OPTICS ordering.
                           Options are 'xi' or 'dbscan'.
            xi: Parameter for the 'xi' cluster extraction method.
            n_jobs: The number of parallel jobs to run for neighbors search.
        """
        self.min_samples = min_samples
        self.max_eps = max_eps
        self.metric = metric
        self.p = p
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.cluster_method = cluster_method
        self.xi = xi
        self.n_jobs = n_jobs
        self.optics_ = None
        self.labels_ = None
        self.n_clusters_ = 0
        self.reachability_ = None

    def fit(self, X: np.ndarray, y: np.ndarray = None):
        """
        Fit the OPTICS transformer by determining cluster assignments.

        Args:
            X: Features array
            y: Target values (not used for clustering)

        Returns:
            self
        """
        # Fit OPTICS
        self.optics_ = OPTICS(
            min_samples=self.min_samples,
            max_eps=self.max_eps,
            metric=self.metric,
            p=self.p,
            algorithm=self.algorithm,
            leaf_size=self.leaf_size,
            cluster_method=self.cluster_method,
            xi=self.xi,
            n_jobs=self.n_jobs,
        )
        self.labels_ = self.optics_.fit_predict(X)
        self.reachability_ = self.optics_.reachability_

        # Handle noise points (labeled as -1)
        unique_labels = np.unique(self.labels_)

        # If all points are noise, create a single partition
        if len(unique_labels) == 1 and unique_labels[0] == -1:
            logging.warning(
                "OPTICS classified all points as noise. Using a single partition."
            )
            self.labels_ = np.zeros(len(X), dtype=int)

        # Get the number of clusters found (excluding noise)
        self.n_clusters_ = len([label for label in unique_labels if label != -1])

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform the data by adding cluster membership indicators.

        Args:
            X: Features array

        Returns:
            X with an additional column indicating cluster membership
        """
        if self.optics_ is None:
            raise ValueError("OPTICSPartitionTransformer has not been fitted yet.")

        # Predict cluster labels for new data
        if hasattr(self.optics_, "predict"):
            # Some implementations might provide a predict method
            labels = self.optics_.predict(X)
        else:
            # Use a simpler approach for prediction with OPTICS
            # OPTICS doesn't have a native predict method or core_sample_indices_
            # We'll fit a new OPTICS instance with the same parameters
            # and then perform a nearest neighbor assignment
            from sklearn.neighbors import NearestNeighbors

            # We'll use all points from the original data with their assigned labels
            # First, we need to get the original data used to fit the model
            if hasattr(self.optics_, "components_"):
                original_data = self.optics_.components_
            else:
                # If components_ attribute doesn't exist, we have to use a different approach
                # We'll refit OPTICS on the new data
                temp_optics = OPTICS(
                    min_samples=self.min_samples,
                    max_eps=self.max_eps,
                    metric=self.metric,
                    p=self.p,
                    algorithm=self.algorithm,
                    leaf_size=self.leaf_size,
                    cluster_method=self.cluster_method,
                    xi=self.xi,
                    n_jobs=self.n_jobs,
                )
                labels = temp_optics.fit_predict(X)
                return np.column_stack((X, labels))

            # Fit a nearest neighbor model on all the data with their OPTICS labels
            nn_model = NearestNeighbors(
                n_neighbors=1,
                algorithm=self.algorithm,
                leaf_size=self.leaf_size,
                metric=self.metric,
                p=self.p,
            ).fit(original_data)

            # Find the nearest neighbor for each new point
            neighbor_indices = nn_model.kneighbors(X, return_distance=False).ravel()

            # Assign labels based on nearest neighbors
            labels = np.array([self.labels_[idx] for idx in neighbor_indices])

        # Add cluster indicators as a new column
        return np.column_stack((X, labels))

    def get_n_clusters(self):
        """Get the number of clusters found by OPTICS, excluding noise points."""
        return self.n_clusters_

    def get_reachability(self):
        """Get the reachability plot data for visualization."""
        return self.reachability_
