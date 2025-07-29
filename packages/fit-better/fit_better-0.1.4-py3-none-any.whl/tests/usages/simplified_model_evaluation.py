#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Simplified script for model evaluation using utility modules.

Usage:
    python simplified_model_evaluation.py --evaluation-mode single --partition-mode KMEANS --regressor-type RANDOM_FOREST
    python simplified_model_evaluation.py --evaluation-mode best --test-mode
    python simplified_model_evaluation.py --evaluation-mode multiple --n-jobs 4

This script demonstrates how to use the utility modules to simplify model evaluation.
It leverages the RegressionFlow class to reduce code duplication and provide a standardized
interface for training and evaluating regression models with different partitioning strategies.
"""
import os
import sys
import logging
from datetime import datetime
from time import time
from pathlib import Path
import numpy as np
import argparse

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import from fit_better - directly use the built-in functionality
from fit_better import (
    PartitionMode,
    RegressorType,
    RegressionFlow,
    Metric,
    setup_logging,
    load_data_from_files,
    generate_synthetic_data_by_function,
    save_data,
    format_statistics_table,
    create_regression_report_plots,
    plot_predictions_vs_actual,
    plot_error_distribution,
)

# Logger will be configured in main function
logger = None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Simplified model evaluation script for fit-better"
    )

    # Get the tests directory for proper path resolution
    tests_dir = Path(__file__).resolve().parent.parent

    # Data input options
    parser.add_argument(
        "--input-dir",
        default=str(tests_dir / "data_gen" / "data"),
        help="Directory containing input data files",
    )
    parser.add_argument(
        "--x-train", default="X_train.npy", help="Filename for X_train data"
    )
    parser.add_argument(
        "--y-train", default="y_train.npy", help="Filename for y_train data"
    )
    parser.add_argument(
        "--x-test", default="X_test.npy", help="Filename for X_test data"
    )
    parser.add_argument(
        "--y-test", default="y_test.npy", help="Filename for y_test data"
    )
    parser.add_argument("--delimiter", default=None, help="Delimiter for CSV/TXT files")
    parser.add_argument(
        "--header", default="infer", help="How to handle headers in CSV/TXT files"
    )

    # Evaluation options
    parser.add_argument(
        "--partition-mode",
        default="KMEANS",
        choices=[mode.name for mode in PartitionMode],
        help="Partition mode to use",
    )
    parser.add_argument(
        "--n-partitions", type=int, default=5, help="Number of partitions to create"
    )
    parser.add_argument(
        "--regressor-type",
        default="RANDOM_FOREST",
        choices=[reg.name for reg in RegressorType],
        help="Regressor type to use",
    )
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")

    # Output options
    parser.add_argument(
        "--output-dir",
        default=str(tests_dir / "data_gen" / "model_eval_results"),
        help="Directory to save results",
    )
    parser.add_argument(
        "--log-dir",
        default=str(tests_dir / "data_gen" / "logs"),
        help="Directory to save log files",
    )
    parser.add_argument(
        "--save-predictions",
        action="store_true",
        help="Save training and evaluation predictions",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualization plots",
    )

    # Misc options
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with reduced configurations",
    )
    parser.add_argument(
        "--evaluation-mode",
        choices=["single", "multiple", "best"],
        default="single",
        help="Evaluation mode: single (one configuration), multiple (test several), best (find optimal)",
    )
    parser.add_argument(
        "--metric",
        default="R2",
        choices=[metric.name for metric in Metric],
        help="Metric to optimize for",
    )

    args = parser.parse_args()

    try:
        # Set up logging
        global logger
        os.makedirs(args.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(args.log_dir, f"model_evaluation_{timestamp}.log")
        logger = setup_logging(log_file)

        logger.info(
            f"Starting simplified model evaluation in {args.evaluation_mode} mode"
        )
        logger.info(f"Configuration: {vars(args)}")

        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)

        # Check for existing data or generate synthetic data
        input_files = [args.x_train, args.y_train, args.x_test, args.y_test]
        input_paths = [os.path.join(args.input_dir, f) for f in input_files]

        if not all(os.path.exists(p) for p in input_paths):
            logger.info(
                "One or more input files not found, generating synthetic data..."
            )
            os.makedirs(args.input_dir, exist_ok=True)

            # Generate synthetic sine data
            X_train, y_train = generate_synthetic_data_by_function(
                function=lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5)
                + 1.5 * np.cos(X[:, 1])
                - X[:, 2],
                n_samples=5000,
                n_features=3,
                noise_std=0.5,
                add_outliers=True,
                random_state=42,
            )

            X_test, y_test = generate_synthetic_data_by_function(
                function=lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5)
                + 1.5 * np.cos(X[:, 1])
                - X[:, 2],
                n_samples=1000,
                n_features=3,
                noise_std=0.5,
                add_outliers=True,
                random_state=43,  # Different seed for test data
            )

            # Save the generated data in both formats
            formats = ["npy", "csv"]
            for fmt in formats:
                save_data(
                    X_train,
                    y_train,
                    X_test,
                    y_test,
                    output_dir=args.input_dir,
                    base_name="data",
                    format=fmt,
                )

            logger.info(f"Generated and saved synthetic data to {args.input_dir}")
            logger.info(
                f"Data shapes: X_train {X_train.shape}, y_train {y_train.shape}, X_test {X_test.shape}, y_test {y_test.shape}"
            )
        else:
            # Load data
            logger.info("Loading data...")
            # Set default delimiter based on file type if not specified
            if args.delimiter is None:
                if args.x_train.endswith(".txt"):
                    args.delimiter = " "
                else:
                    args.delimiter = ","
                logger.info(
                    f"Using default delimiter: '{args.delimiter}' based on file type"
                )

            X_train, y_train, X_test, y_test = load_data_from_files(
                args.input_dir,
                args.x_train,
                args.y_train,
                args.x_test,
                args.y_test,
                delimiter=args.delimiter,
                header=args.header,
            )

        start_time = time()

        # Create the RegressionFlow instance for all evaluation modes
        flow = RegressionFlow()
        metric_to_optimize = Metric[args.metric]

        # Determine which evaluation mode to use
        if args.evaluation_mode == "single":
            # Evaluate a single model configuration
            partition_mode = PartitionMode[args.partition_mode]
            regressor_type = RegressorType[args.regressor_type]

            logger.info(
                f"Training a single model: {regressor_type.name} with {partition_mode.name} partitioning"
            )

            # Use find_best_strategy with specific configuration
            result = flow.find_best_strategy(
                X_train,
                y_train,
                X_test,
                y_test,
                partition_modes=[partition_mode],
                regressor_types=[regressor_type],
                n_partitions=args.n_partitions,
                n_jobs=args.n_jobs,
                metrics_to_optimize=metric_to_optimize,
            )

            # Log results
            logger.info(
                f"Evaluation completed: {result.model_type.name} with {result.partition_mode.name}"
            )
            logger.info(
                f"Test metrics: R² = {result.metrics['r2']:.4f}, MAE = {result.metrics['mae']:.4f}"
            )

        elif args.evaluation_mode == "multiple":
            # Test multiple model configurations
            logger.info("Evaluating multiple model configurations")

            # Define a set of models to test
            regressor_types = [
                RegressorType.LINEAR,
                RegressorType.RANDOM_FOREST,
                RegressorType.GRADIENT_BOOSTING,
            ]
            partition_modes = [PartitionMode.NONE, PartitionMode.KMEANS]

            # Test each combination and store results
            results = []
            for p_mode in partition_modes:
                for r_type in regressor_types:
                    logger.info(f"Testing {r_type.name} with {p_mode.name}")

                    result = flow.find_best_strategy(
                        X_train,
                        y_train,
                        X_test,
                        y_test,
                        partition_modes=[p_mode],
                        regressor_types=[r_type],
                        n_partitions=args.n_partitions,
                        n_jobs=args.n_jobs,
                        metrics_to_optimize=metric_to_optimize,
                    )

                    results.append(
                        {
                            "regressor": r_type.name,
                            "partition": p_mode.name,
                            "mae": result.metrics["mae"],
                            "r2": result.metrics["r2"],
                            "result": result,
                        }
                    )

            # Find best model by selected metric
            best_idx = 0
            best_value = (
                -float("inf") if metric_to_optimize == Metric.R2 else float("inf")
            )

            for i, res in enumerate(results):
                metric_value = (
                    res["r2"] if metric_to_optimize == Metric.R2 else res["mae"]
                )
                if (metric_to_optimize == Metric.R2 and metric_value > best_value) or (
                    metric_to_optimize != Metric.R2 and metric_value < best_value
                ):
                    best_value = metric_value
                    best_idx = i

            # Use the best model for predictions
            best_result = results[best_idx]["result"]

            # Display results table
            logger.info("Results for all tested configurations:")
            for res in results:
                logger.info(
                    f"{res['regressor']} + {res['partition']}: R² = {res['r2']:.4f}, MAE = {res['mae']:.4f}"
                )

            logger.info(
                f"Best configuration: {results[best_idx]['regressor']} with {results[best_idx]['partition']}"
            )

            # Use the best model for subsequent operations
            result = best_result

        else:  # "best" mode - find optimal model automatically
            # Define configuration based on test mode
            if args.test_mode:
                # Limited set for testing
                partition_modes = [PartitionMode.NONE, PartitionMode.KMEANS]
                regressor_types = [RegressorType.LINEAR, RegressorType.RANDOM_FOREST]
            else:
                # Full search
                partition_modes = list(PartitionMode)
                regressor_types = list(RegressorType)

            logger.info(
                f"Finding best model among {len(partition_modes)} partition modes and {len(regressor_types)} regressor types"
            )

            # Find best strategy
            result = flow.find_best_strategy(
                X_train,
                y_train,
                X_test,
                y_test,
                partition_modes=partition_modes,
                regressor_types=regressor_types,
                n_partitions=args.n_partitions,
                n_jobs=args.n_jobs,
                metrics_to_optimize=metric_to_optimize,
            )

            logger.info(
                f"Found best model: {result.model_type.name} with {result.partition_mode.name}"
            )
            logger.info(
                f"Test metrics: R² = {result.metrics['r2']:.4f}, MAE = {result.metrics['mae']:.4f}"
            )

        # Common post-processing steps for all modes
        # Print formatted metrics
        metrics_table = format_statistics_table(result.metrics)
        logger.info(f"Model performance metrics:\n{metrics_table}")

        # Save predictions if requested
        if args.save_predictions:
            predictions_dir = os.path.join(args.output_dir, "predictions")
            os.makedirs(predictions_dir, exist_ok=True)

            # Generate predictions
            y_train_pred = flow.predict(X_train)
            y_test_pred = flow.predict(X_test)

            # Save to CSV
            import pandas as pd

            train_df = pd.DataFrame(
                {
                    "y_true": y_train,
                    "y_pred": y_train_pred,
                    "error": y_train - y_train_pred,
                }
            )
            test_df = pd.DataFrame(
                {"y_true": y_test, "y_pred": y_test_pred, "error": y_test - y_test_pred}
            )

            train_df.to_csv(
                os.path.join(predictions_dir, "train_predictions.csv"), index=False
            )
            test_df.to_csv(
                os.path.join(predictions_dir, "test_predictions.csv"), index=False
            )
            logger.info(f"Saved predictions to {predictions_dir}")

        # Generate visualizations if requested
        if args.visualize:
            viz_dir = os.path.join(args.output_dir, "visualizations")
            os.makedirs(viz_dir, exist_ok=True)

            # Generate comprehensive plots using fit_better's utility
            create_regression_report_plots(
                y_test,
                flow.predict(X_test),
                title=f"{result.model_type.name} with {result.partition_mode.name}",
                output_dir=viz_dir,
            )
            logger.info(f"Generated visualizations in {viz_dir}")

        # Display execution time
        elapsed_time = time() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds")

        # Print summary to console
        print("\nResults Summary:")
        print(f"Evaluation mode: {args.evaluation_mode}")
        print(f"Best model: {result.model_type.name}")
        print(
            f"Partitioning: {result.partition_mode.name} with {result.n_partitions or 'N/A'} partitions"
        )
        print(
            f"Test metrics: R² = {result.metrics['r2']:.4f}, MAE = {result.metrics['mae']:.4f}"
        )
        print(f"Execution time: {elapsed_time:.2f} seconds")

        if args.visualize:
            print(
                f"Visualizations saved to: {os.path.join(args.output_dir, 'visualizations')}"
            )
        if args.save_predictions:
            print(
                f"Predictions saved to: {os.path.join(args.output_dir, 'predictions')}"
            )

    except Exception as e:
        if logger:
            logger.exception(f"Error in model evaluation: {e}")
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
