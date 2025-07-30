#!/usr/bin/env python3
"""
Author: hi@xlindo.com
Create Time: 2025-05-15
Description: Example script demonstrating best practices for logging in fit-better tests

Usage:
    python logging_example.py [options]

This script demonstrates how to implement standardized logging for fit-better tests,
including process tracking, results formatting with ASCII tables, and proper summary reporting.

Options:
    --output-dir DIR    Directory to save results (default: logging_example_results)
    --n-samples N       Number of samples to generate (default: 1000)
    --function FUNC     Function type to generate (linear, sine, complex) (default: sine)
    --log-level LEVEL   Logging level (DEBUG, INFO, WARNING, ERROR) (default: INFO)
"""

import os
import sys
import argparse
import time
import numpy as np
from pathlib import Path
import logging

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import fit_better components
from fit_better import (
    RegressionFlow,
    calc_regression_statistics,
    generate_synthetic_data,
    plot_predictions_vs_actual,
    plot_error_distribution,
    save_model,
    RegressorType,
    PartitionMode,
)

# Import logging utilities
from fit_better.utils.logging_utils import (
    ProcessTracker,
    log_model_results,
    log_summary,
)
from fit_better.utils.ascii import print_ascii_table
from tests.utils import setup_test_logging, log_test_results


def generate_test_data(n_samples=1000, function_type="sine", noise_level=0.5):
    """Generate synthetic test data based on function type"""
    with ProcessTracker(logger, f"Generating {function_type} test data") as tracker:
        if function_type == "linear":
            X = np.linspace(-10, 10, n_samples).reshape(-1, 1)
            y = 2 * X.ravel() + 3 + noise_level * np.random.randn(n_samples)
        elif function_type == "sine":
            X = np.linspace(-3 * np.pi, 3 * np.pi, n_samples).reshape(-1, 1)
            y = np.sin(X.ravel()) + noise_level * np.random.randn(n_samples)
        elif function_type == "complex":
            X = np.linspace(-5, 5, n_samples).reshape(-1, 1)
            y = (
                0.2 * X.ravel() ** 3
                - 0.5 * X.ravel() ** 2
                + X.ravel()
                + noise_level * np.random.randn(n_samples)
            )
        else:
            tracker.update(
                f"Unknown function type '{function_type}', defaulting to sine"
            )
            X = np.linspace(-3 * np.pi, 3 * np.pi, n_samples).reshape(-1, 1)
            y = np.sin(X.ravel()) + noise_level * np.random.randn(n_samples)

        # Split into train/test sets (70%/30%)
        split_idx = int(0.7 * n_samples)
        X_train, y_train = X[:split_idx], y[:split_idx]
        X_test, y_test = X[split_idx:], y[split_idx:]

        tracker.update(
            f"Generated {len(X_train)} training samples and {len(X_test)} test samples"
        )

        return X_train, y_train, X_test, y_test


def run_regression_analysis(X_train, y_train, X_test, y_test, output_dir):
    """Run regression analysis with different configurations"""
    results = {}
    all_metrics = {}

    # Define regression configurations to test
    configurations = [
        {
            "name": "LinearRegression",
            "regressor": RegressorType.LINEAR,
            "partitions": 1,
        },
        {
            "name": "LinearRegression_5_partitions",
            "regressor": RegressorType.LINEAR,
            "partitions": 5,
        },
        {
            "name": "RandomForest",
            "regressor": RegressorType.RANDOM_FOREST,
            "partitions": 1,
        },
        {"name": "LightGBM", "regressor": RegressorType.LIGHTGBM, "partitions": 1},
        {"name": "ElasticNet", "regressor": RegressorType.ELASTIC_NET, "partitions": 3},
    ]

    # Test each configuration
    for config in configurations:
        name = config["name"]
        regressor_type = config["regressor"]
        n_partitions = config["partitions"]

        with ProcessTracker(
            logger, f"Training {name} with {n_partitions} partitions"
        ) as tracker:
            # Create regression flow
            flow = RegressionFlow()

            # Find best strategy with constrained configuration
            if n_partitions > 1:
                tracker.update(f"Using partitioning with {n_partitions} partitions")
                result = flow.find_best_strategy(
                    X_train=X_train,
                    y_train=y_train,
                    X_test=X_test,
                    y_test=y_test,
                    partition_modes=[PartitionMode.KMEANS],
                    regressor_types=[regressor_type],
                    n_partitions=n_partitions,
                    n_jobs=-1,
                )
            else:
                tracker.update("Using single model without partitioning")
                result = flow.find_best_strategy(
                    X_train=X_train,
                    y_train=y_train,
                    X_test=X_test,
                    y_test=y_test,
                    partition_modes=[PartitionMode.NONE],
                    regressor_types=[regressor_type],
                    n_jobs=-1,
                )

            # Make predictions using the best model
            y_pred = flow.predict(X_test)

            # Calculate detailed metrics
            metrics = calc_regression_statistics(
                y_test, y_pred, residual_percentiles=[1, 2, 5, 10, 15, 20]
            )

            # Save results
            results[name] = result
            all_metrics[name] = metrics

            # Log individual model results
            log_model_results(logger, name, metrics)

            # Generate plots for this model
            plots_dir = os.path.join(output_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)

            plot_path = os.path.join(plots_dir, f"{name}_predictions.png")
            plot_predictions_vs_actual(
                y_test, y_pred, title=f"{name} Predictions", save_path=plot_path
            )
            logger.info(f"Saved predictions plot to {plot_path}")

            error_plot_path = os.path.join(plots_dir, f"{name}_errors.png")
            plot_error_distribution(
                y_test,
                y_pred,
                title=f"{name} Error Distribution",
                save_path=error_plot_path,
            )
            logger.info(f"Saved error distribution plot to {error_plot_path}")

            # Save model
            model_path = os.path.join(output_dir, f"{name}.model")
            save_model(result, model_path, overwrite=True)
            logger.info(f"Saved model to {model_path}")

    # Compare all models
    logger.info("\nModel Comparison:")

    # Create comparison table
    headers = ["Model", "MAE", "RMSE", "R²", "Within 5%", "Training Time (s)"]
    rows = []

    for name, metrics in all_metrics.items():
        row = [
            name,
            f"{metrics['mae']:.4f}",
            f"{metrics['rmse']:.4f}",
            f"{metrics['r2']:.4f}",
            f"{metrics.get('pct_within_5pct', 0):.1f}%",
            f"{metrics.get('training_time', 0):.2f}",
        ]
        rows.append(row)

    # Sort by R² (higher is better)
    rows.sort(key=lambda x: float(x[3]), reverse=True)
    print_ascii_table(headers, rows, to_log=True)

    # Find best model
    best_model_name = max(all_metrics.items(), key=lambda x: x[1]["r2"])[0]
    best_model = results[best_model_name]
    best_metrics = all_metrics[best_model_name]

    return best_model, best_metrics, all_metrics


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Example script for fit-better logging"
    )

    # Get the tests directory path
    tests_dir = Path(__file__).resolve().parent.parent

    parser.add_argument(
        "--output-dir",
        default=str(tests_dir / "data_gen" / "logging_example_results"),
        help="Directory to save results",
    )
    parser.add_argument(
        "--n-samples", type=int, default=1000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--function",
        choices=["linear", "sine", "complex"],
        default="sine",
        help="Function type to generate",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.log_level)
    global logger
    logger = setup_test_logging(
        test_name="logging_example",
        log_dir=os.path.join(args.output_dir, "logs"),
        log_level=log_level,
    )

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Start measuring full execution time
    start_time = time.time()

    try:
        # Generate test data
        X_train, y_train, X_test, y_test = generate_test_data(
            n_samples=args.n_samples, function_type=args.function
        )

        # Run regression analysis
        best_model, best_metrics, all_metrics = run_regression_analysis(
            X_train, y_train, X_test, y_test, args.output_dir
        )

        # Calculate overall execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Log summary of results
        best_model_name = max(all_metrics.items(), key=lambda x: x[1]["r2"])[0]
        summary = {
            "Test Function": args.function,
            "Number of Samples": args.n_samples,
            "Best Model": best_model_name,
            "Best R²": best_metrics["r2"],
            "Best MAE": best_metrics["mae"],
            "Best RMSE": best_metrics["rmse"],
            "Total Models Tested": len(all_metrics),
            "Execution Time (s)": execution_time,
        }

        # Log test results using standard format
        log_test_results(logger, summary)

        logger.info("Testing completed successfully! 🎉")
        return 0

    except Exception as e:
        logger.exception(f"Error during testing: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
