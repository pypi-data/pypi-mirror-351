"""
Utility functions for model evaluation in test scripts.

This module provides reusable model evaluation functions to reduce code duplication
across test scripts. It includes functions for:
- Calculating standard regression metrics
- Evaluating models with partitioned data
- Generating performance reports

Usage:
    from tests.utils.eval_utils import evaluate_model, print_evaluation_report
"""

import os
import numpy as np
import pandas as pd
import logging
from time import time

from fit_better import (
    train_models_on_partitions,
    predict_with_partitioned_models,
    save_model,
    calc_regression_statistics,
)
from fit_better.utils.ascii import print_ascii_table
from fit_better.utils.statistics import print_partition_statistics

logger = logging.getLogger(__name__)


def evaluate_model(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_mode,
    n_partitions,
    regressor_type,
    n_jobs=1,
    output_dir=None,
    save_model_file=True,
    verbose=True,
):
    """
    Train and evaluate a model with the specified configuration.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_mode: Partition mode to use
        n_partitions: Number of partitions
        regressor_type: Regressor type to use
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results (optional)
        save_model_file: Whether to save the trained model to a file
        verbose: Whether to print detailed output

    Returns:
        Dictionary with evaluation results
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    start_time = time()

    # Train models on partitions
    if verbose:
        logger.info(
            f"Training with {partition_mode.name} partitioning, {n_partitions} partitions, and {regressor_type.name} regressor..."
        )

    models = train_models_on_partitions(
        X_train,
        y_train,
        partition_mode=partition_mode,
        n_partitions=n_partitions,
        regressor_type=regressor_type,
        n_jobs=n_jobs,
    )

    # Get actual number of partitions
    actual_n_parts = len(models)

    if verbose:
        logger.info(f"Created {actual_n_parts} partitions")
        print_partition_statistics(
            models, X_train, y_train, X_test, y_test, partition_mode, regressor_type
        )

    # Make predictions
    y_train_pred = predict_with_partitioned_models(models, X_train, n_jobs=n_jobs)
    y_test_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

    # Calculate metrics
    train_metrics = calc_regression_statistics(y_train, y_train_pred)
    test_metrics = calc_regression_statistics(y_test, y_test_pred)

    training_time = time() - start_time

    # Save model if requested
    if output_dir and save_model_file:
        model_filepath = os.path.join(
            output_dir,
            f"{partition_mode.name}_{regressor_type.name}_{n_partitions}_parts.joblib",
        )
        save_model(
            {"models": models},
            model_filepath,
            metadata={
                "partition_mode": str(partition_mode),
                "n_partitions": actual_n_parts,
                "regressor_type": str(regressor_type),
                "metrics": {
                    "train_mae": train_metrics["mae"],
                    "train_rmse": train_metrics["rmse"],
                    "train_r2": train_metrics["r2"],
                    "test_mae": test_metrics["mae"],
                    "test_rmse": test_metrics["rmse"],
                    "test_r2": test_metrics["r2"],
                },
            },
            overwrite=True,
        )
        if verbose:
            logger.info(f"Saved model to {model_filepath}")

    # Compile results
    results = {
        "partition_mode": partition_mode.name,
        "n_partitions": n_partitions,
        "actual_n_partitions": actual_n_parts,
        "regressor_type": regressor_type.name,
        "train_mae": train_metrics["mae"],
        "train_rmse": train_metrics["rmse"],
        "train_r2": train_metrics["r2"],
        "train_pct_within_3pct": train_metrics.get("pct_within_3pct", 0.0),
        "test_mae": test_metrics["mae"],
        "test_rmse": test_metrics["rmse"],
        "test_r2": test_metrics["r2"],
        "test_pct_within_3pct": test_metrics.get("pct_within_3pct", 0.0),
        "training_time": training_time,
        "models": models,
        "train_predictions": y_train_pred,
        "test_predictions": y_test_pred,
    }

    if verbose:
        print_evaluation_report(results)

    return results


def print_evaluation_report(results):
    """
    Print a standardized evaluation report.

    Args:
        results: Dictionary with evaluation results
    """
    headers = ["Metric", "Training", "Testing"]
    rows = [
        ["MAE", f"{results['train_mae']:.4f}", f"{results['test_mae']:.4f}"],
        ["RMSE", f"{results['train_rmse']:.4f}", f"{results['test_rmse']:.4f}"],
        ["R²", f"{results['train_r2']:.4f}", f"{results['test_r2']:.4f}"],
        [
            "Within 3%",
            f"{results['train_pct_within_3pct']:.2f}%",
            f"{results['test_pct_within_3pct']:.2f}%",
        ],
    ]

    print(
        f"\nEvaluation Report for {results['partition_mode']} partitioning with {results['regressor_type']} regressor"
    )
    print(
        f"Partitions: {results['actual_n_partitions']} (requested: {results['n_partitions']})"
    )
    print(f"Training time: {results['training_time']:.2f} seconds")
    print_ascii_table(headers, rows)


def evaluate_multiple_configurations(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_modes,
    regressor_types,
    partition_counts,
    n_jobs=1,
    output_dir=None,
    verbose=False,
):
    """
    Evaluate multiple model configurations and return the results.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_modes: List of partition modes to evaluate
        regressor_types: List of regressor types to evaluate
        partition_counts: List of partition counts to evaluate
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results (optional)
        verbose: Whether to print detailed output for each configuration

    Returns:
        List of dictionaries with evaluation results
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    results = []
    total_configs = len(partition_modes) * len(regressor_types) * len(partition_counts)
    current_config = 0

    logger.info(f"Evaluating {total_configs} configurations...")
    logger.info(f"Partition modes: {[mode.name for mode in partition_modes]}")
    logger.info(f"Regressor types: {[reg.name for reg in regressor_types]}")
    logger.info(f"Partition counts: {partition_counts}")

    # Evaluate all combinations
    for partition_mode in partition_modes:
        for n_partitions in partition_counts:
            for regressor_type in regressor_types:
                current_config += 1

                logger.info(
                    f"Configuration {current_config}/{total_configs}: {partition_mode.name}, {n_partitions} partitions, {regressor_type.name}"
                )

                try:
                    # Create subdirectory for this configuration if saving results
                    config_dir = None
                    if output_dir:
                        config_dir = os.path.join(
                            output_dir,
                            f"{partition_mode.name}_{n_partitions}_{regressor_type.name}",
                        )
                        os.makedirs(config_dir, exist_ok=True)

                    # Evaluate model
                    result = evaluate_model(
                        X_train,
                        y_train,
                        X_test,
                        y_test,
                        partition_mode=partition_mode,
                        n_partitions=n_partitions,
                        regressor_type=regressor_type,
                        n_jobs=n_jobs,
                        output_dir=config_dir,
                        verbose=verbose,
                    )

                    results.append(result)

                except Exception as e:
                    logger.error(
                        f"Error with {partition_mode.name} partitioning, {n_partitions} partitions, "
                        f"and {regressor_type.name} regressor: {str(e)}"
                    )

    # Find the best configuration based on test R²
    if results:
        best_result = max(results, key=lambda x: x["test_r2"])

        logger.info("\nBest configuration:")
        logger.info(f"Partition mode: {best_result['partition_mode']}")
        logger.info(f"Number of partitions: {best_result['n_partitions']}")
        logger.info(f"Regressor type: {best_result['regressor_type']}")
        logger.info(f"Test R²: {best_result['test_r2']:.4f}")

        # Save best model if output directory provided
        if output_dir:
            model_filepath = os.path.join(output_dir, "best_model.joblib")
            logger.info(f"Saving best model to {model_filepath}")

            save_model(
                {"models": best_result["models"]},
                model_filepath,
                metadata={
                    "partition_mode": best_result["partition_mode"],
                    "n_partitions": best_result["actual_n_partitions"],
                    "regressor_type": best_result["regressor_type"],
                    "metrics": {
                        "train_mae": best_result["train_mae"],
                        "train_rmse": best_result["train_rmse"],
                        "train_r2": best_result["train_r2"],
                        "test_mae": best_result["test_mae"],
                        "test_rmse": best_result["test_rmse"],
                        "test_r2": best_result["test_r2"],
                    },
                },
                overwrite=True,
            )

    return results
