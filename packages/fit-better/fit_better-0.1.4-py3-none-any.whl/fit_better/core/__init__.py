"""
Core Functionality for Fit Better
==================================

The `fit_better.core` module provides the central components for orchestrating
regression tasks, managing data partitioning, defining regressor types, and
conducting structured experiments.

Key Components:
---------------

*   **`RegressionFlow`**: A class that encapsulates the entire process of performing
    a regression analysis, from data input to model training and result generation.
    It handles partitioning, model selection, and execution.

*   **`RegressionResult`**: A data structure (often a `NamedTuple` or `dataclass`)
    to store the outcomes of a regression run, including the trained model,
    performance metrics, and any partitioning information.

*   **`PartitionMode` (Enum)**: Defines the available strategies for partitioning
    the data before model training. Examples might include `NONE` (no partitioning),
    `SIMPLE_SPLIT`, `K_MEANS`, `DECISION_TREE_BASED`, etc. This allows for
    applying different models to different subsets of data, potentially improving
    overall predictive accuracy on heterogeneous datasets.

*   **`RegressorType` (Enum)**: Specifies the type of regression algorithm to be used.
    This enum lists all supported regressors, such as `LINEAR`, `POLYNOMIAL`,
    `RANDOM_FOREST`, `GRADIENT_BOOSTING`, etc., providing a standardized way to
    select models.

*   **`DataDimension` (Enum)**: Indicates the dimensionality of the input data (e.g., `ONE_D`, `MULTI_D`).

*   **`Metric` (Enum)**: Defines the performance metrics used for model evaluation (e.g., `MSE`, `R2`, `MAE`).

*   **Core Functions**:
    *   `fit_all_regressors()`: A utility to train multiple types of regressors on given data.
    *   `select_best_model()`: A function to evaluate and select the best performing model
        from a set of trained models based on specified metrics.
    *   `train_models_on_partitions()`: Handles the logic of training models on different
        data partitions created by a chosen `PartitionMode`.
    *   `predict_with_partitioned_models()`: Generates predictions using a set of models
        trained on partitioned data.

*   **`RegressionExperiment`**: (from `fit_better.core.experiment`) A class to manage
    and automate regression experiments, allowing for systematic comparison of
    different configurations (e.g., regressors, partition strategies).

This module forms the backbone of the `fit_better` package, integrating various
components to deliver a flexible and powerful regression modeling toolkit.
"""

# Re-export key components from submodules
from .experiment import ExperimentConfig, RegressionExperiment, setup_logging, demo
from .models import (
    RegressorType,
    create_regressor,
    fit_one_model,
    fit_all_regressors,
    select_best_model,
)
from .partitioning import PartitionMode, get_partitioner_by_mode
from .regression import (
    RegressionFlow,
    RegressionResult,
    Metric,
    DataDimension,
    train_models_on_partitions,
    predict_with_partitioned_models,
)


__all__ = [
    "RegressionFlow",
    "RegressionResult",
    "PartitionMode",
    "RegressorType",
    "DataDimension",
    "Metric",
    "fit_all_regressors",
    "select_best_model",
    "train_models_on_partitions",
    "predict_with_partitioned_models",
    "get_partitioner_by_mode",
    "create_regressor",
    # Experiment related
    "ExperimentConfig",
    "RegressionExperiment",
    "setup_logging",
    "demo",
]
