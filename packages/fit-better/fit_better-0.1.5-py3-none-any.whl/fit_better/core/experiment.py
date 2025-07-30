"""
Author: xlindo
Create Time: 2025-04-29
Description: Main script for running regression experiments, including data generation, model fitting, evaluation, and plotting.
Usage:
    python regression_experiment.py
"""

# Standard library imports
import os
import logging
import datetime
from typing import Dict, List, Tuple, Any, Optional, Union

# Third-party imports
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import joblib

# Updated local imports to use the new module structure
from fit_better.data.synthetic import generate_synthetic_data
from fit_better.data.preprocessing import load_key_value_arrays
from fit_better.core.models import (
    RegressorType,
    fit_one_model,
    fit_all_regressors,
    select_best_model,
    Metric,
)
from fit_better.utils.statistics import calc_regression_statistics
from fit_better.utils.plotting import plot_versus
from fit_better.core.partitioning import (
    train_models_on_partitions,
    predict_with_partitioned_models,
    PartitionMode,
)
from fit_better.utils.ascii import print_ascii_table, ascii_table_lines
from fit_better.evaluation.metrics import (
    key_statistics,
    EVAL_STAT_KEYS,
    make_eval_row,
    evaluate_model_on_data,
)
from fit_better.io.model_io import save_model, load_model, predict_with_model


class ExperimentConfig:
    def __init__(
        self,
        orig_X_path=None,
        orig_y_path=None,
        new_X_path=None,
        new_y_path=None,
        n_parts=2,
        n_jobs=1,
        base_dir=os.path.dirname(
            os.path.abspath(__file__)
        ),  # Default: this file's directory
        data_dir=None,  # Optional: user-specified data directory
        partition_mode=PartitionMode.PERCENTILE,  # Using enum for partition mode
        log_level=logging.INFO,
        regressor_type=RegressorType.ALL,  # Optional specific regressor type to use
        enable_plotting=False,  # Enable visualization plots (disabled by default)
    ):
        self.base_dir = base_dir
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Find the project root and set paths relative to tests/data_gen
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        tests_data_gen_dir = os.path.join(project_root, "tests", "data_gen")

        self.data_dir = data_dir or os.path.join(tests_data_gen_dir, f"data_{now_str}")
        self.log_path = os.path.join(tests_data_gen_dir, "logs", f"log_{now_str}.log")

        # Configurable file paths
        self.orig_X_path = orig_X_path or os.path.join(self.data_dir, "X.txt")
        self.orig_y_path = orig_y_path or os.path.join(self.data_dir, "y.txt")
        self.new_X_path = new_X_path or os.path.join(self.data_dir, "X_new.txt")
        self.new_y_path = new_y_path or os.path.join(self.data_dir, "y_new.txt")
        self.n_parts = n_parts
        self.n_jobs = n_jobs
        self.enable_plotting = enable_plotting

        # Convert partition_mode string to enum if necessary
        if isinstance(partition_mode, str):
            try:
                self.partition_mode = PartitionMode(partition_mode)
            except ValueError:
                raise ValueError(
                    f"Invalid partition_mode: {partition_mode}. Valid values are {[mode.value for mode in PartitionMode]}"
                )
        else:
            self.partition_mode = partition_mode

        # Handle regressor_type if provided
        from .model_utils import RegressorType

        if regressor_type is None:
            # Default to ALL if None is provided
            self.regressor_type = RegressorType.ALL
        elif isinstance(regressor_type, str):
            try:
                # Convert string to enum value
                self.regressor_type = RegressorType(regressor_type)
            except ValueError:
                valid_regressors = [rt.value for rt in RegressorType]
                raise ValueError(
                    f"Invalid regressor_type: {regressor_type}. Valid values are {valid_regressors}"
                )
        else:
            self.regressor_type = regressor_type

        self.log_level = log_level

    def ensure_dirs(self):
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)


def setup_logging(log_path: str, level: int = logging.INFO):
    """
    Set up logging configuration for the application.

    Args:
        log_path: Path to the log file
        level: Logging level (e.g., logging.DEBUG, logging.INFO)

    Returns:
        Logger instance configured with the specified settings
    """
    # Import the new centralized logging utility
    from fit_better.utils.logging_utils import (
        setup_logging as setup_centralized_logging,
    )

    # Use the centralized logging setup
    setup_centralized_logging(log_path, level)

    # Return a logger for this module
    logger = logging.getLogger(__name__)
    return logger


class RegressionExperiment:
    def __init__(self, config: ExperimentConfig, logger):
        self.config = config
        self.logger = logger

    def run(
        self, X_txt, y_txt, X_new_txt, y_new_txt, plotting=False, n_parts=1, n_jobs=1
    ):
        """
        Run the regression experiment using provided file paths for X, y, X_new, y_new.
        Assumes no header in the input files by default.
        n_parts: number of partitions for piecewise model training (default 1, i.e., no partitioning)
        Logs all key statistics and clearly separates each experiment in the log.
        """
        os.makedirs(self.config.data_dir, exist_ok=True)
        self.logger.info("=" * 60)
        self.logger.info("====================== NEW EXPERIMENT ======================")
        self.logger.info("=" * 60)
        self.logger.info(f"== Step 1: Load Original Data: X_txt={X_txt}, y_txt={y_txt}")
        print("[WoW] Loading original data...")
        X, y = load_key_value_arrays(X_txt, y_txt, has_header=False, delimiter=" ")
        self.logger.info(f"Loaded original data: X.shape={X.shape}, y.shape={y.shape}")

        self.logger.info("=" * 60)
        self.logger.info("== Step 2: Fit, Plot, and Save Best Model")
        print("[WoW] Fitting models and saving best model...")
        self.logger.info(f"[Config] n_jobs for joblib: {n_jobs}")
        results = fit_all_regressors(X, y, n_jobs=n_jobs)
        col_labels = [
            "Model",
            "MAE",
            "RMSE",
            "R2",
            "Std(Res)",
            "Max(Res)",
            "Min(Res)",
            "<=3%",
            "<=5%",
            "<=10%",
        ]
        row_data = key_statistics(y, X, results)
        self.logger.info("Regression statistics for all algorithms (ASCII table):")
        self.logger.info("\n" + "\n".join(ascii_table_lines(col_labels, row_data)))

        best = select_best_model(results)
        best_model_path = os.path.join(self.config.data_dir, "best_model.joblib")
        save_model(best["model"], best_model_path, transformer=best["transformer"])

        # Display best model info in a table
        best_headers = ["Property", "Value"]
        best_data = [
            ["Model Name", best["name"]],
            ["Model Type", type(best["model"]).__name__],
            ["Save Path", best_model_path],
        ]
        # Add key metrics from the best model
        for metric in ["mae", "rmse", "r2", "pct_within_3pct"]:
            if metric in best["stats"]:
                value = best["stats"][metric]
                formatted = (
                    f"{value:.2f}%" if metric.startswith("pct") else f"{value:.6f}"
                )
                best_data.append([metric, formatted])

        self.logger.info("Best model details:")
        self.logger.info("\n" + "\n".join(ascii_table_lines(best_headers, best_data)))

        # Also print to console for user feedback
        print(f"[WoW] Best model saved: {best['name']}")

        self.logger.info("=" * 60)
        self.logger.info("== Step 3: Load Model")
        loaded_model = load_model(best_model_path)

        self.logger.info("=" * 60)
        self.logger.info("== Step 4: Predict Original Data and Plot Versus")
        y_pred = predict_with_model(loaded_model, X)

        # Display first few predictions as ASCII table
        self.logger.debug("Predictions for X_txt (first 10):")
        pred_headers = ["Index", "X Value", "Predicted y", "True y", "Error"]
        pred_data = []

        for i in range(min(10, len(y_pred))):
            error = abs(y_pred[i] - y[i])
            error_pct = error / abs(y[i]) * 100 if abs(y[i]) > 0 else float("nan")
            pred_data.append(
                [
                    f"{i}",
                    f"{X[i,0]:.4f}",
                    f"{y_pred[i]:.4f}",
                    f"{y[i]:.4f}",
                    f"{error:.4f} ({error_pct:.2f}%)",
                ]
            )

        self.logger.debug("\n" + "\n".join(ascii_table_lines(pred_headers, pred_data)))
        stats_orig = evaluate_model_on_data(loaded_model, X, y, print_stats=False)
        self.logger.info("Statistics for best model on original data:")

        # Format stats as ASCII table instead of individual lines
        col_labels = ["Metric", "Value"]
        table_data = []
        for k, v in stats_orig.items():
            if isinstance(v, float):
                if k.startswith("pct_within"):
                    table_data.append([k, f"{v:.2f}%"])
                else:
                    table_data.append([k, f"{v:.6f}"])

        print_ascii_table(col_labels, table_data, to_log=True)

        eval_col_labels = ["Comparison"]
        for key, label in EVAL_STAT_KEYS:
            # Keep the original label without modifications
            eval_col_labels.append(label)
        eval_row_data = [
            make_eval_row("X vs y_true", calc_regression_statistics(y, X.flatten())),
            make_eval_row(
                "y_pred vs y_true (train)", calc_regression_statistics(y, y_pred)
            ),
        ]

        self.logger.info("=" * 60)
        self.logger.info(
            f"== Step 5: Load Evaluation Data: X_new_txt={X_new_txt}, y_new_txt={y_new_txt}"
        )
        print("[WoW] Loading evaluation data for prediction demo...")
        X_new, y_new = load_key_value_arrays(
            X_new_txt, y_new_txt, has_header=False, delimiter=" "
        )
        self.logger.info(
            f"Loaded evaluation data: X_new.shape={X_new.shape}, y_new.shape={y_new.shape}"
        )

        # Add evaluation for single model on evaluation data
        y_new_pred = predict_with_model(loaded_model, X_new)
        eval_row_data.append(
            make_eval_row(
                "y_pred vs y_true (eval)", calc_regression_statistics(y_new, y_new_pred)
            )
        )

        self.logger.info("Model evaluation (versus table, ASCII):")
        self.logger.info(
            "\n" + "\n".join(ascii_table_lines(eval_col_labels, eval_row_data))
        )

        if plotting:
            plot_versus(
                y,
                X.flatten(),
                title="X vs True y (from X_txt)",
                golden_label="True y",
                compared_label="X",
            )
            plot_versus(
                y,
                y_pred,
                title="Predicted y vs True y (from X_txt)",
                golden_label="True y",
                compared_label="Predicted y",
            )

        self.logger.info("=" * 60)
        self.logger.info(
            f"== Step 6: Partitioned Model Training and Prediction Demo (n_parts={n_parts})"
        )
        print(f"[WoW] Training and evaluating partitioned model (n_parts={n_parts})...")
        partitioned_model_path = os.path.join(
            self.config.data_dir, f"partitioned_model_{n_parts}.joblib"
        )
        partitioned = train_models_on_partitions(
            X,
            y,
            n_parts=n_parts,
            metric=Metric.MAE,  # Using Metric enum instead of string
            n_jobs=n_jobs,
            save_path=partitioned_model_path,
            DATA_DIR=self.config.data_dir,
            partition_mode=self.config.partition_mode,
            regressor_type=self.config.regressor_type,
        )
        self.logger.debug(f"Partitioned model saved to {partitioned_model_path}")
        y_pred_partitioned = predict_with_partitioned_models(
            partitioned, X, log_prefix="[train]", n_jobs=n_jobs
        )

        # Display partitioned model predictions as ASCII table
        self.logger.debug("Partitioned model predictions (first 10):")
        part_pred_headers = [
            "Index",
            "X Value",
            "Partitioned Pred",
            "Single Model Pred",
            "True y",
            "Difference",
        ]
        part_pred_data = []

        for i in range(min(10, len(y_pred_partitioned))):
            # Calculate difference between partitioned and single model prediction
            diff = y_pred_partitioned[i] - y_pred[i]
            diff_pct = (
                abs(diff / y_pred[i] * 100) if abs(y_pred[i]) > 0 else float("nan")
            )
            part_pred_data.append(
                [
                    f"{i}",
                    f"{X[i,0]:.4f}",
                    f"{y_pred_partitioned[i]:.4f}",
                    f"{y_pred[i]:.4f}",
                    f"{y[i]:.4f}",
                    f"{diff:+.4f} ({diff_pct:.2f}%)",
                ]
            )

        self.logger.debug(
            "\n" + "\n".join(ascii_table_lines(part_pred_headers, part_pred_data))
        )
        self.logger.info("Partitioned model evaluation:")
        # Predict on evaluation data and print numbers in each range
        y_pred_partitioned_new = predict_with_partitioned_models(
            partitioned, X_new, log_prefix="[eval]", n_jobs=n_jobs
        )
        pct3_train_rows = []
        pct3_pred_rows = []
        for i, m in enumerate(partitioned["models"]):
            left, right = m["X_range"]
            # Training data mask
            if np.isneginf(left):
                mask_train = X.flatten() <= right
            elif np.isposinf(right):
                mask_train = X.flatten() > left
            else:
                mask_train = (X.flatten() > left) & (X.flatten() <= right)
            X_part = X[mask_train]
            y_part = y[mask_train]
            # Evaluation data mask
            if np.isneginf(left):
                mask_pred = X_new.flatten() <= right
            elif np.isposinf(right):
                mask_pred = X_new.flatten() > left
            else:
                mask_pred = (X_new.flatten() > left) & (X_new.flatten() <= right)
            X_new_part = X_new[mask_pred]
            y_new_part = y_new[mask_pred]
            # Training stats
            stats_part = evaluate_model_on_data(
                m["model"], X_part, y_part, print_stats=False
            )
            pct3_train = stats_part.get("pct_within_3pct", float("nan"))
            # Prediction stats (on new data)
            if len(X_new_part) > 0:
                y_new_pred = predict_with_model(
                    (m["transformer"], m["model"]), X_new_part
                )
                stats_pred = calc_regression_statistics(y_new_part, y_new_pred)
                pct3_pred = stats_pred.get("pct_within_3pct", float("nan"))
            else:
                pct3_pred = float("nan")
            # Create a small summary table for each partition
            summary_headers = ["Metric", "Value"]
            summary_data = [
                ["Partition", f"{i+1}"],
                ["Range", f"[{left:.4f}, {right:.4f}]"],
                ["Train samples", f"{len(X_part)}"],
                ["Eval samples", f"{len(X_new_part)}"],
                ["pct_within_3pct (train)", f"{pct3_train:.2f}%"],
                ["pct_within_3pct (eval)", f"{pct3_pred:.2f}%"],
            ]
            self.logger.debug("Partition summary:")
            self.logger.debug(
                "\n" + "\n".join(ascii_table_lines(summary_headers, summary_data))
            )
            pct3_train_rows.append(
                [
                    f"{i+1}",
                    f"[{left:.4f}, {right:.4f}]",
                    f"{len(X_part)}",
                    f"{pct3_train:.2f}%",
                ]
            )
            pct3_pred_rows.append(
                [
                    f"{i+1}",
                    f"[{left:.4f}, {right:.4f}]",
                    f"{len(X_new_part)}",
                    f"{pct3_pred:.2f}%",
                ]
            )
            # Prepare ASCII table for this partition
            col_labels = ["Metric", "Value"]
            stat_keys = [
                "mean_true",
                "std_true",
                "mean_pred",
                "std_pred",
                "mean_residual",
                "std_residual",
                "mae",
                "rmse",
                "max_abs_residual",
                "min_residual",
                "max_residual",
                "r2",
                "pct_within_3pct",
                "pct_within_5pct",
                "pct_within_10pct",
                "pct_within_20pct",
            ]
            row_data = []
            for k in stat_keys:
                if k in stats_part:
                    if not k.startswith("pct_within"):
                        row_data.append([k, f"{stats_part[k]:.6f}"])
                    else:
                        row_data.append([k, f"{stats_part[k]:.2f}%"])
            self.logger.debug(f"Model index: {i+1}")
            self.logger.debug(f"Range: [{left:.4f}, {right:.4f}]")
            self.logger.debug("\n" + "\n".join(ascii_table_lines(col_labels, row_data)))
        # Print merged summary table for pct_within_3pct (combining train and evaluation data)
        self.logger.info(
            "\nSummary: pct_within_3pct for each partition (train and evaluation data):"
        )

        # Create a merged table with both train and predict information
        merged_headers = [
            "Partition",
            "Range",
            "#Train",
            "pct_within_3pct (train)",
            "#Eval",
            "pct_within_3pct (eval)",
        ]
        merged_rows = []

        for i, (train_row, pred_row) in enumerate(zip(pct3_train_rows, pct3_pred_rows)):
            # Each row contains [partition_num, range, count, percentage]
            # We need to merge them into [partition_num, range, train_count, train_pct, pred_count, pred_pct]
            merged_row = [
                train_row[0],  # Partition number
                train_row[1],  # Range
                train_row[2],  # Train count
                train_row[3],  # Train percentage
                pred_row[2],  # Predict count
                pred_row[3],  # Predict percentage
            ]
            merged_rows.append(merged_row)

        self.logger.info(
            "\n" + "\n".join(ascii_table_lines(merged_headers, merged_rows))
        )

        # Calculate overall percentage metrics for partitioned models on both train and evaluation data
        partitioned_train_stats = calc_regression_statistics(y, y_pred_partitioned)
        partitioned_new_stats = calc_regression_statistics(
            y_new, y_pred_partitioned_new
        )

        # Add stats for partitioned model on training data
        eval_row_data.append(
            make_eval_row(
                "partitioned_pred vs y_true (train)",
                partitioned_train_stats,
            )
        )

        # Add evaluation for partitioned model on evaluation data
        eval_row_data.append(
            make_eval_row(
                "partitioned_pred vs y_true (eval)",
                partitioned_new_stats,
            )
        )

        # We already calculated single model stats when we called make_eval_row for "y_pred vs y_true (eval)" above
        # Use those values directly from eval_row_data[2] which contains the stats for single model on evaluation data

        # Log detailed percentage metrics for both single model and partitioned model on evaluation data
        self.logger.info(
            "\nDetailed percentage metrics for model predictions on evaluation data:"
        )
        metrics_headers = ["Model Type", "<=3%", "<=5%", "<=10%", "MAE", "RMSE", "R2"]
        metrics_rows = [
            [
                "Single model (eval data)",
                f"{eval_row_data[2][7]}",  # <=3% from the single model evaluation
                f"{eval_row_data[2][8]}",  # <=5% from the single model evaluation
                f"{eval_row_data[2][9]}",  # <=10% from the single model evaluation
                f"{eval_row_data[2][1]}",  # MAE from the single model evaluation
                f"{eval_row_data[2][2]}",  # RMSE from the single model evaluation
                f"{eval_row_data[2][3]}",  # R2 from the single model evaluation
            ],
            [
                "Partitioned model (eval data)",
                f"{partitioned_new_stats.get('pct_within_3pct', 0):.2f}%",
                f"{partitioned_new_stats.get('pct_within_5pct', 0):.2f}%",
                f"{partitioned_new_stats.get('pct_within_10pct', 0):.2f}%",
                f"{partitioned_new_stats.get('mae', 0):.4f}",
                f"{partitioned_new_stats.get('rmse', 0):.4f}",
                f"{partitioned_new_stats.get('r2', 0):.4f}",
            ],
        ]
        self.logger.info(
            "\n" + "\n".join(ascii_table_lines(metrics_headers, metrics_rows))
        )

        self.logger.info("Overall partitioned model vs true y (ASCII):")
        self.logger.info(
            "\n" + "\n".join(ascii_table_lines(eval_col_labels, eval_row_data))
        )
        if plotting:
            # Plot for training data
            plot_versus(
                y,
                y_pred_partitioned,
                title="Partitioned Model: Predicted y vs True y (Training Data)",
                golden_label="True y",
                compared_label="Partitioned Predicted y",
            )

            # Also plot for new data
            plot_versus(
                y_new,
                y_pred_partitioned_new,
                title="Partitioned Model: Predicted y vs True y (Evaluation Data)",
                golden_label="True y (Eval)",
                compared_label="Partitioned Predicted y (Eval)",
            )

    def full_flow(self, plotting=None):
        # Use the config setting for plotting if not explicitly provided
        plotting = self.config.enable_plotting if plotting is None else plotting

        if not (
            os.path.exists(self.config.orig_X_path)
            and os.path.exists(self.config.orig_y_path)
        ):
            raise FileNotFoundError(
                f"Original data files not found: {self.config.orig_X_path}, {self.config.orig_y_path}"
            )
        if not (
            os.path.exists(self.config.new_X_path)
            and os.path.exists(self.config.new_y_path)
        ):
            raise FileNotFoundError(
                f"Evaluation data files not found: {self.config.new_X_path}, {self.config.new_y_path}"
            )
        self.logger.info(
            f"Using local data files: {self.config.orig_X_path}, {self.config.orig_y_path}, {self.config.new_X_path}, {self.config.new_y_path}"
        )
        print("[WoW] Running experiment...")
        if plotting:
            self.logger.info("Plotting is enabled, visualizations will be generated")
            print("[WoW] Plotting enabled, visualizations will be generated")
        else:
            self.logger.info(
                "Plotting is disabled, no visualizations will be generated"
            )

        self.run(
            self.config.orig_X_path,
            self.config.orig_y_path,
            self.config.new_X_path,
            self.config.new_y_path,
            plotting=plotting,
            n_parts=self.config.n_parts,
            n_jobs=self.config.n_jobs,
        )


def demo():
    import datetime

    # Use gen_DATE for data generation, run_DATE for runtime files/models
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Find the project root and set paths relative to tests/data_gen
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    tests_data_gen_dir = os.path.join(project_root, "tests", "data_gen")

    gen_dir = os.path.join(tests_data_gen_dir, f"gen_{now_str}")
    run_dir = os.path.join(tests_data_gen_dir, f"run_{now_str}")
    os.makedirs(gen_dir, exist_ok=True)
    os.makedirs(run_dir, exist_ok=True)
    orig_X_path = os.path.join(gen_dir, "X.txt")
    orig_y_path = os.path.join(gen_dir, "y.txt")
    new_X_path = os.path.join(gen_dir, "X_new.txt")
    new_y_path = os.path.join(gen_dir, "X_new.txt")
    generate_synthetic_data(orig_X_path, orig_y_path, n=10000)
    generate_synthetic_data(
        new_X_path, new_y_path, n=2000, a=2.5, b=-3.0, noise_std=0.2, seed=123
    )
    config = ExperimentConfig(
        orig_X_path=orig_X_path,
        orig_y_path=orig_y_path,
        new_X_path=new_X_path,
        new_y_path=new_y_path,
        n_parts=2,
        base_dir=project_root,  # Using project root instead of script_dir
        data_dir=run_dir,  # Use run_DATE for runtime files/models
        partition_mode=PartitionMode.RANGE,  # Use enum for partition mode
        enable_plotting=False,  # Disable plotting by default
    )
    config.ensure_dirs()
    logger = setup_logging(config.log_path)
    experiment = RegressionExperiment(config, logger)
    experiment.full_flow()
