"""
Regression flow module for finding optimal regression strategies.

This module provides a high-level interface for finding the best regression
strategy for both 1D and nD data, combining different partitioning approaches
with various regression algorithms.

Regression Flow, Result, and Metric Definitions
===============================================

This module provides the core `RegressionFlow` class for orchestrating regression
tasks, the `RegressionResult` dataclass for storing outcomes, and the `Metric`
enum for defining evaluation metrics.

It integrates partitioning strategies and various regression algorithms to find
optimal models for given datasets.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

from .models import RegressorType, fit_all_regressors, select_best_model
from .partitioning import (
    PartitionMode,
    train_models_on_partitions,
    predict_with_partitioned_models,
    BasePartitioner,
)

logger = logging.getLogger(__name__)


class Metric(Enum):
    """
    Enum for performance metrics used in regression model evaluation.

    Attributes:
        R2: R-squared (coefficient of determination).
            Formula: \(R^2 = 1 - \frac{SS_{res}}{SS_{tot}}\)
            Pros: Represents the proportion of variance explained by the model.
                  Ranges from -inf to 1 (higher is better).
            Cons: Can be misleadingly high for models with many predictors.
        MSE: Mean SquaredError.
            Formula: \(MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2\)
            Pros: Penalizes larger errors more heavily.
            Cons: Units are squared, making it less interpretable directly.
        RMSE: Root Mean Squared Error.
            Formula: \(RMSE = \sqrt{MSE}\)
            Pros: Same units as the target variable, more interpretable than MSE.
            Cons: Still sensitive to outliers due to the squaring.
        MAE: Mean Absolute Error.
            Formula: \(MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|\)
            Pros: Robust to outliers, same units as target variable.
            Cons: Does not penalize large errors as much as MSE/RMSE.
    """

    R2 = "r2"
    MSE = "mse"
    RMSE = "rmse"
    MAE = "mae"

    def __str__(self):
        return self.value


class DataDimension(Enum):
    """Enum defining data dimensionality."""

    ONE_D = "1D"
    MULTI_D = "multi-dimensional"

    def __str__(self):
        return self.value


@dataclass
class RegressionResult:
    """
    Stores the comprehensive results of a regression analysis.

    This dataclass encapsulates all relevant information produced by a
    `RegressionFlow` run or a similar regression task, including the model itself,
    performance metrics, and details about the configuration used.

    Attributes:
        model: The trained regression model or a list of models if partitioning was used.
               Type can be Any scikit-learn compatible regressor or a list of them.
        metrics: A dictionary containing performance metrics (e.g., R², MSE, RMSE, MAE)
                 calculated on a test set or via cross-validation.
                 Example: `{'r2': 0.85, 'mse': 0.12}`
        model_type: The type of regressor used (e.g., `RegressorType.LINEAR`).
        partition_mode: The partitioning strategy employed (e.g., `PartitionMode.KMEANS`).
                        `None` if no partitioning was used.
        n_partitions: The number of partitions created if a partitioning strategy was used.
        partitioner_details: Specific details or the fitted partitioner object if available.
                             This could be, for example, a `KMeans` object or a `DecisionTreePartitioner`.
        scaler: The scaler object (e.g., `StandardScaler`) used to preprocess the data, if any.
        feature_names: Optional list of feature names used for training.
        metadata: Any additional metadata related to the regression run (e.g., execution time, dataset name).
    """

    model: Any
    metrics: Dict[str, float]
    model_type: RegressorType
    partition_mode: Optional[PartitionMode] = None
    n_partitions: Optional[int] = None
    partitioner_details: Optional[Any] = None
    scaler: Optional[Any] = None
    feature_names: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RegressionFlow:
    """
    Orchestrates a complete regression analysis pipeline.

    This class provides a high-level interface to run regression tasks, encompassing
    data validation, preprocessing (scaling), model training (optionally with
    partitioning), and prediction. It aims to simplify the process of finding
    an effective regression strategy for a given dataset.

    The flow can operate with a single global model or explore various partitioning
    strategies combined with different regression algorithms to identify a potentially
    superior composite model.

    Key steps:
    1.  Input validation: Checks data types, shapes, and for NaN/inf values.
    2.  Data scaling: Applies `StandardScaler` to features.
    3.  Strategy exploration:
        *   Trains and evaluates a global model (no partitioning).
        *   If `partition_mode` is not `NONE`, trains and evaluates models on data partitions.
    4.  Prediction: Allows making predictions using the best model found or a specified model.

    Example:
        ```python
        from fit_better.core import RegressionFlow, RegressorType, PartitionMode
        import numpy as np

        # Sample data
        X_train = np.random.rand(100, 2)
        y_train = X_train[:, 0] * 2 + X_train[:, 1] * 3 + np.random.rand(100) * 0.5
        X_test = np.random.rand(50, 2)
        y_test = X_test[:, 0] * 2 + X_test[:, 1] * 3 + np.random.rand(50) * 0.5

        flow = RegressionFlow()
        result = flow.find_best_strategy(
            X_train, y_train, X_test, y_test,
            partition_mode=PartitionMode.KMEANS,
            n_partitions=3,
            regressor_type=RegressorType.LINEAR
        )

        print(f"Best strategy: {result.model_type} with {result.partition_mode}")
        print(f"Metrics: {result.metrics}")

        # Make predictions with the best model
        # Note: The flow's internal state (scaler, best_model) is set by find_best_strategy.
        # For stateless prediction, one might need to manage the model and scaler explicitly.
        # y_pred = flow.predict(X_test)
        # For more direct prediction using RegressionResult:
        if result.scaler:
            X_test_scaled = result.scaler.transform(X_test.reshape(-1, X_train.shape[1]) if X_test.ndim ==1 else X_test)
        else:
            X_test_scaled = X_test.reshape(-1, X_train.shape[1]) if X_test.ndim ==1 else X_test

        if result.partition_mode and result.partition_mode != PartitionMode.NONE:
            y_pred = predict_with_partitioned_models(result.model, X_test_scaled, result.partitioner_details)
        else:
             # Ensure X_test_scaled is 2D for sklearn models
            if X_test_scaled.ndim == 1:
                 X_test_scaled = X_test_scaled.reshape(-1, 1)
            y_pred = result.model.predict(X_test_scaled)
        print(f"Predictions: {y_pred[:5]}")
        ```

    Note:
        The `find_best_strategy` method currently updates the internal state of the
        `RegressionFlow` instance (e.g., `self.best_model`, `self.scaler`).
        For stateless operations, it's recommended to use the components directly
        (e.g., `train_models_on_partitions`, `predict_with_partitioned_models`)
        or manage the `RegressionResult` object.
    """

    def __init__(self):
        """Initialize the regression flow."""
        self.best_model_internal: Optional[Any] = None
        self.best_partition_mode_internal: Optional[PartitionMode] = None
        self.best_regressor_type_internal: Optional[RegressorType] = None
        self.best_partitioner_details_internal: Optional[Any] = None
        self.scaler_internal: Optional[StandardScaler] = None
        self.feature_names_internal: Optional[List[str]] = None

        # Configure logging
        try:
            from fit_better.utils.logging_utils import get_logger

            self.logger = get_logger(__name__)
        except ImportError:
            # Fallback to basic logging
            import logging

            self.logger = logging.getLogger(__name__)

    def _validate_input(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
    ) -> None:
        """Validate input data."""
        if not isinstance(X, np.ndarray) or not isinstance(y, np.ndarray):
            raise TypeError("X and y must be numpy arrays")

        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        elif X.ndim > 2:
            raise ValueError("X must be 1D or 2D")

        if len(X) != len(y):
            raise ValueError("X and y must have the same length")

        if np.isnan(X).any() or np.isnan(y).any():
            raise ValueError("Input data contains NaN values")

        if np.isinf(X).any() or np.isinf(y).any():
            raise ValueError("Input data contains inf values")

        if X_test is not None and y_test is not None:
            if not isinstance(X_test, np.ndarray) or not isinstance(y_test, np.ndarray):
                raise TypeError("X_test and y_test must be numpy arrays")

            # Ensure X_test is 2D
            if X_test.ndim == 1:
                X_test = X_test.reshape(-1, 1)
            elif X_test.ndim > 2:
                raise ValueError("X_test must be 1D or 2D")

            if len(X_test) != len(y_test):
                raise ValueError("X_test and y_test must have the same length")

            if np.isnan(X_test).any() or np.isnan(y_test).any():
                raise ValueError("Test data contains NaN values")

            if np.isinf(X_test).any() or np.isinf(y_test).any():
                raise ValueError("Test data contains inf values")

    def _get_data_dimension(self, X: np.ndarray) -> DataDimension:
        """Determine the dimensionality of the input data."""
        if X.shape[1] == 1:
            return DataDimension.ONE_D
        return DataDimension.MULTI_D

    def find_best_strategy(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        partition_modes: Optional[List[PartitionMode]] = None,
        regressor_types: Optional[List[RegressorType]] = None,
        n_partitions: int = 3,
        n_jobs: int = -1,
        feature_names: Optional[List[str]] = None,
        metrics_to_optimize: Metric = Metric.R2,
    ) -> RegressionResult:
        """
        Finds the best regression strategy by evaluating various partitioning modes and regressor types.

        This method iterates through specified (or default) partitioning strategies and
        regressor types, trains models, evaluates them on the test set, and returns the
        strategy that yields the best performance based on the `metrics_to_optimize`.

        It first evaluates a global model (no partitioning) for each regressor type,
        then proceeds to evaluate partitioned models.

        Args:
            X_train: Training features (numpy array).
            y_train: Training target values (numpy array).
            X_test: Test features (numpy array).
            y_test: Test target values (numpy array).
            partition_modes: A list of `PartitionMode` enums to try. If None, defaults to
                             `[PartitionMode.NONE, PartitionMode.PERCENTILE, PartitionMode.KMEANS]`.
                             `PartitionMode.NONE` implies a global model.
            regressor_types: A list of `RegressorType` enums to try. If None, defaults to
                             `[RegressorType.LINEAR, RegressorType.RANDOM_FOREST]`.
            n_partitions: Number of partitions to create for partitioning modes (default: 3).
            n_jobs: Number of parallel jobs for model training (default: -1, uses all cores).
                    Note: For some partitioners or models, parallel processing might be forced to 1 for stability.
            feature_names: Optional list of feature names for context.
            metrics_to_optimize: The primary `Metric` to use for selecting the best strategy (default: `Metric.R2`).
                                 Higher R2 is better, lower MSE/RMSE/MAE is better.

        Returns:
            A `RegressionResult` object containing the best model, its performance metrics,
            and the configuration that achieved it.

        Raises:
            TypeError: If input data are not numpy arrays.
            ValueError: If data shapes are inconsistent or data contains NaN/inf values.
        """
        # Try to import enhanced logging utilities
        try:
            from fit_better.utils.logging_utils import (
                ProcessTracker,
                log_model_results,
                log_summary,
            )
            from fit_better.utils.ascii import print_ascii_table

            use_enhanced_logging = True
        except ImportError:
            use_enhanced_logging = False

        # Start tracking the overall process
        start_time = time.time()
        process_name = "Finding best regression strategy"

        if use_enhanced_logging:
            tracker = ProcessTracker(self.logger, process_name)
            tracker.__enter__()  # Start the tracker
        else:
            self.logger.info(f"Starting: {process_name}")

        try:
            self._validate_input(X_train, y_train, X_test, y_test)
            self.feature_names_internal = feature_names

            # Ensure X is 2D
            if X_train.ndim == 1:
                X_train = X_train.reshape(-1, 1)
            if X_test.ndim == 1:
                X_test = X_test.reshape(-1, 1)

            self.logger.info(
                f"Data shapes: X_train {X_train.shape}, y_train {y_train.shape}, X_test {X_test.shape}, y_test {y_test.shape}"
            )

            # Data processing phase
            if use_enhanced_logging:
                tracker.update("Scaling input features")
            else:
                self.logger.info("Scaling input features")

            self.scaler_internal = StandardScaler()
            X_train_scaled = self.scaler_internal.fit_transform(X_train)
            X_test_scaled = self.scaler_internal.transform(X_test)

            # Set default partition modes and regressor types if not provided
            if partition_modes is None:
                partition_modes = [
                    PartitionMode.NONE,
                    PartitionMode.PERCENTILE,
                    PartitionMode.KMEANS,
                ]
            elif (
                PartitionMode.NONE not in partition_modes
            ):  # Ensure NONE is always an option
                partition_modes = [PartitionMode.NONE] + partition_modes

            if regressor_types is None:
                regressor_types = [RegressorType.LINEAR, RegressorType.RANDOM_FOREST]

            self.logger.info(
                f"Testing {len(partition_modes)} partition modes and {len(regressor_types)} regressor types"
            )
            if use_enhanced_logging:
                tracker.update(
                    f"Testing {len(partition_modes)*len(regressor_types)} strategy combinations"
                )

            # Strategy evaluation phase
            best_overall_performance_metric = (
                -np.inf if metrics_to_optimize == Metric.R2 else np.inf
            )
            best_result: Optional[RegressionResult] = None
            all_strategy_results = []

            total_strategies = len(partition_modes) * len(regressor_types)
            current_strategy = 0

            for p_mode in partition_modes:
                for r_type in regressor_types:
                    current_strategy += 1
                    if use_enhanced_logging:
                        tracker.update(
                            f"Evaluating strategy {current_strategy}/{total_strategies}: {p_mode.value} with {r_type.value}"
                        )
                    else:
                        self.logger.info(
                            f"Evaluating strategy: Partitioner={p_mode.value}, Regressor={r_type.value}"
                        )

                    current_model: Any = None
                    current_partitioner_details: Any = None
                    y_pred: Optional[np.ndarray] = None
                    strategy_start_time = time.time()

                    try:
                        if p_mode == PartitionMode.NONE:
                            # Global model
                            if use_enhanced_logging:
                                tracker.update(f"Training global {r_type.value} model")

                            model_dict_list = fit_all_regressors(
                                X_train_scaled,
                                y_train,
                                regressor_type=r_type,
                                n_jobs=n_jobs,
                            )
                            if not model_dict_list:
                                self.logger.warning(
                                    f"Failed to train global {r_type.value} model."
                                )
                                continue

                            selected_model_info = select_best_model(model_dict_list)
                            current_model = selected_model_info["model"]
                            y_pred = current_model.predict(X_test_scaled)
                            current_partitioner_details = (
                                None  # No partitioner for global model
                            )
                        else:
                            # Partitioned model
                            if use_enhanced_logging:
                                tracker.update(
                                    f"Training {r_type.value} with {n_partitions} {p_mode.value} partitions"
                                )

                            trained_output = train_models_on_partitions(
                                X_train_scaled,
                                y_train,
                                partition_mode=p_mode,
                                n_partitions=n_partitions,
                                n_jobs=n_jobs,
                                regressor_type=r_type,
                            )
                            if not trained_output or not trained_output[0]:
                                self.logger.warning(
                                    f"No models trained for {p_mode.value} with {r_type.value}."
                                )
                                continue

                            current_model, current_partitioner_details = trained_output

                            # Make predictions with the partitioned model
                            y_pred = predict_with_partitioned_models(
                                current_model,
                                X_test_scaled,
                                current_partitioner_details,
                            )

                        if y_pred is None:
                            self.logger.warning(
                                f"Prediction failed for {p_mode.value} with {r_type.value}."
                            )
                            continue

                        # Calculate all relevant metrics
                        r2 = r2_score(y_test, y_pred)
                        mse = mean_squared_error(y_test, y_pred)
                        rmse = np.sqrt(mse)
                        mae = mean_absolute_error(y_test, y_pred)

                        # Calculate percentage-based metrics for more complete evaluation
                        abs_percent_error = 100.0 * np.abs(
                            (y_pred - y_test) / (np.abs(y_test) + 1e-10)
                        )
                        pct_within_1pct = np.mean(abs_percent_error <= 1.0) * 100.0
                        pct_within_5pct = np.mean(abs_percent_error <= 5.0) * 100.0

                        strategy_training_time = time.time() - strategy_start_time

                        calculated_metrics = {
                            "r2": r2,
                            "mse": mse,
                            "rmse": rmse,
                            "mae": mae,
                            "pct_within_1pct": pct_within_1pct,
                            "pct_within_5pct": pct_within_5pct,
                            "training_time": strategy_training_time,
                        }

                        # Log the results for this strategy
                        strategy_name = f"{r_type.value}"
                        if p_mode != PartitionMode.NONE:
                            strategy_name += (
                                f" with {n_partitions} {p_mode.value} partitions"
                            )

                        if use_enhanced_logging:
                            log_model_results(
                                self.logger, strategy_name, calculated_metrics
                            )
                        else:
                            self.logger.info(
                                f"Strategy: {strategy_name} | "
                                f"R²={r2:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}, "
                                f"Within 1%={pct_within_1pct:.1f}%, Within 5%={pct_within_5pct:.1f}%"
                            )

                        # Save results for later comparison
                        all_strategy_results.append(
                            {
                                "name": strategy_name,
                                "p_mode": p_mode,
                                "r_type": r_type,
                                "metrics": calculated_metrics,
                                "model": current_model,
                                "partitioner_details": current_partitioner_details,
                            }
                        )

                        # Check if this strategy is better
                        current_performance_metric = calculated_metrics[
                            metrics_to_optimize.value
                        ]
                        is_better = False
                        if metrics_to_optimize == Metric.R2:
                            if (
                                current_performance_metric
                                > best_overall_performance_metric
                            ):
                                is_better = True
                        else:  # For MSE, RMSE, MAE, lower is better
                            if (
                                current_performance_metric
                                < best_overall_performance_metric
                            ):
                                is_better = True

                        if is_better:
                            best_overall_performance_metric = current_performance_metric
                            best_result = RegressionResult(
                                model=current_model,
                                metrics=calculated_metrics,
                                model_type=r_type,
                                partition_mode=p_mode,
                                n_partitions=(
                                    n_partitions
                                    if p_mode != PartitionMode.NONE
                                    else None
                                ),
                                partitioner_details=current_partitioner_details,
                                scaler=self.scaler_internal,
                                feature_names=self.feature_names_internal,
                                metadata={
                                    "strategy_description": f"Regressor: {r_type.value}, Partitioner: {p_mode.value}",
                                    "training_time": strategy_training_time,
                                },
                            )
                            # Update internal bests for predict method
                            self.best_model_internal = current_model
                            self.best_partition_mode_internal = p_mode
                            self.best_regressor_type_internal = r_type
                            self.best_partitioner_details_internal = (
                                current_partitioner_details
                            )

                    except Exception as e:
                        self.logger.error(
                            f"Error evaluating strategy {p_mode.value} with {r_type.value}: {e}",
                            exc_info=True,
                        )
                        continue

            # Log the summary comparison table
            if all_strategy_results:
                self.logger.info("\nStrategy Comparison:")

                # Create comparison table
                headers = ["Strategy", "R²", "RMSE", "MAE", "Within 5%", "Time (s)"]
                rows = []

                for result in all_strategy_results:
                    m = result["metrics"]
                    row = [
                        result["name"],
                        f"{m['r2']:.4f}",
                        f"{m['rmse']:.4f}",
                        f"{m['mae']:.4f}",
                        f"{m['pct_within_5pct']:.1f}%",
                        f"{m['training_time']:.2f}",
                    ]
                    rows.append(row)

                # Sort by the optimization metric
                metric_index = 1  # Default to R² (index 1 in headers)
                if metrics_to_optimize == Metric.RMSE:
                    metric_index = 2
                elif metrics_to_optimize == Metric.MAE:
                    metric_index = 3

                reverse_sort = (
                    metrics_to_optimize == Metric.R2
                )  # Higher is better for R²
                rows.sort(key=lambda x: float(x[metric_index]), reverse=reverse_sort)

                if use_enhanced_logging and "print_ascii_table" in locals():
                    print_ascii_table(headers, rows, to_log=True)
                else:
                    # Simple formatted output
                    table_str = "\n" + " | ".join(headers) + "\n" + "-" * 80 + "\n"
                    for row in rows:
                        table_str += " | ".join(row) + "\n"
                    self.logger.info(table_str)

            if not best_result:
                # Fallback if no strategy succeeded
                self.logger.error(
                    "No regression strategy succeeded. Returning a default/error result."
                )
                return RegressionResult(
                    model=None,
                    metrics={},
                    model_type=regressor_types[0],  # Placeholder
                    metadata={"error": "No strategy succeeded"},
                )

            # Log final summary
            total_time = time.time() - start_time
            summary = {
                "Best Strategy": best_result.metadata.get("strategy_description"),
                f"Best {metrics_to_optimize.value.upper()}": best_overall_performance_metric,
                "R²": best_result.metrics.get("r2"),
                "RMSE": best_result.metrics.get("rmse"),
                "MAE": best_result.metrics.get("mae"),
                "Within 5%": f"{best_result.metrics.get('pct_within_5pct', 0):.1f}%",
                "Strategies Tested": len(all_strategy_results),
                "Total Time (s)": total_time,
            }

            if use_enhanced_logging:
                log_summary(
                    self.logger, summary, title="Regression Strategy Selection Results"
                )
            else:
                self.logger.info(
                    f"\nBest strategy found: {best_result.metadata.get('strategy_description')}"
                )
                self.logger.info(
                    f"Best {metrics_to_optimize.value}: {best_overall_performance_metric:.4f}"
                )
                self.logger.info(f"Total evaluation time: {total_time:.2f}s")

            # Add total execution time to metadata
            best_result.metadata["total_execution_time"] = total_time

            return best_result

        except Exception as e:
            self.logger.exception(f"Error in find_best_strategy: {e}")
            raise
        finally:
            if use_enhanced_logging:
                tracker.__exit__(None, None, None)  # Close the tracker
            else:
                self.logger.info(
                    f"Completed: {process_name} in {time.time() - start_time:.2f}s"
                )

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Makes predictions using the best model found by `find_best_strategy`.

        This method relies on the internal state of the `RegressionFlow` instance
        (scaler, best model, partitioning details) which are set during the
        `find_best_strategy` call.

        Args:
            X: Input features (numpy array) for which to make predictions.

        Returns:
            A numpy array of predictions.

        Raises:
            ModelNotFittedError: If `find_best_strategy` has not been called successfully prior to prediction.
            ValueError: If input X has an incompatible shape.
        """
        if self.best_model_internal is None or self.scaler_internal is None:
            raise ModelNotFittedError(
                "The regression flow has not been run or no best model was found. "
                "Call find_best_strategy() first."
            )

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        # Check if X number of features matches training data
        # Assuming scaler_internal was fit on X_train with original number of features
        if X.shape[1] != self.scaler_internal.n_features_in_:
            raise ValueError(
                f"Input X has {X.shape[1]} features, but model was trained on "
                f"{self.scaler_internal.n_features_in_} features."
            )

        X_scaled = self.scaler_internal.transform(X)

        if (
            self.best_partition_mode_internal
            and self.best_partition_mode_internal != PartitionMode.NONE
        ):
            if not self.best_partitioner_details_internal:
                raise ModelNotFittedError(
                    "Partitioning was used but partitioner details are missing."
                )
            y_pred = predict_with_partitioned_models(
                self.best_model_internal,
                X_scaled,
                partitioner=self.best_partitioner_details_internal,
            )
        else:
            # Global model prediction
            y_pred = self.best_model_internal.predict(X_scaled)

        return y_pred
