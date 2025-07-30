#!/usr/bin/env python3
"""
Author: hi@xlindo.com
Create Time: 2025-05-10
Description: Unified script for evaluating models with various partition strategies and regressor types.

Usage:
    python unified_model_evaluation.py [options]

This script combines functionality from partition_and_regressor_example.py and best_partition_and_regressor_example.py
to provide a single entry point for model evaluation, with options to test a specific model configuration
or automatically find the best combination of partition strategy and regressor type.

Options:
    --input-dir DIR        Directory containing input data files (default: data)
    --x-train FILE         Filename for X_train data (default: X_train.npy)
    --y-train FILE         Filename for y_train data (default: y_train.npy)
    --x-test FILE          Filename for X_test data (default: X_test.npy)
    --y-test FILE          Filename for y_test data (default: y_test.npy)
    --delimiter CHAR       Delimiter character for CSV or TXT files (default: ' ' for TXT, ',' for CSV)
    --header OPTION        How to handle headers in CSV/TXT files: 'infer' or 'none' (default: 'infer')
    --evaluation-mode      Evaluation mode: 'single' (one configuration) or 'find_best' (try multiple) (default: single)
    --partition-mode       Partition mode to use (default: KMEANS)
    --n-partitions INT     Number of partitions to create (default: 5)
    --regressor-type       Regressor type to use (default: RANDOM_FOREST)
    --n-jobs N             Number of parallel jobs (default: 1)
    --output-dir DIR       Directory to save results (default: model_results)
    --save-predictions     Save training and evaluation predictions to CSV files
    --use-regression-flow  Use RegressionFlow for a more streamlined workflow
    --test-mode            Run in test mode with fewer combinations for faster testing (only for find_best mode)
"""
import os
import sys
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from time import time

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import from fit_better
from fit_better import (
    PartitionMode,
    RegressorType,
    RegressionFlow,
    Metric,
    setup_logging,
    generate_train_test_data,
    save_data,
    load_data_from_files,
    calc_regression_statistics,
    print_partition_statistics,
    format_statistics_table,
    create_regression_report_plots,
    plot_predictions_vs_actual,
    plot_error_distribution,
    plot_performance_comparison,
    compare_model_statistics,
)

# Logger will be configured in main function using setup_logging
logger = None


def main():
    # Parse command line arguments using argparse
    import argparse

    # Get the tests directory path
    tests_dir = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(
        description="Unified script for evaluating models with various partition strategies and regressor types"
    )

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
        "--evaluation-mode",
        type=str,
        choices=["single", "find_best"],
        default="single",
        help="Evaluation mode: 'single' (one configuration) or 'find_best' (try multiple)",
    )
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
    tests_dir = Path(__file__).resolve().parent.parent

    parser.add_argument(
        "--output-dir",
        default=str(tests_dir / "data_gen" / "model_results"),
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

    # Misc options
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with fewer combinations for faster testing",
    )
    parser.add_argument(
        "--use-regression-flow",
        action="store_true",
        help="Use RegressionFlow for a more streamlined workflow",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualization plots",
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

        logger.info(f"Starting unified model evaluation in {args.evaluation_mode} mode")
        logger.info(f"Configuration: {vars(args)}")

        # Ensure output directories exist
        os.makedirs(args.output_dir, exist_ok=True)

        # Check for existing data or generate synthetic data
        input_files = [args.x_train, args.y_train, args.x_test, args.y_test]
        input_paths = [os.path.join(args.input_dir, f) for f in input_files]

        if not all(os.path.exists(p) for p in input_paths):
            logger.info(
                "One or more input files not found, generating synthetic data..."
            )
            os.makedirs(args.input_dir, exist_ok=True)

            # Generate synthetic data
            # Use different functions depending on evaluation mode to provide appropriate test data
            if args.evaluation_mode == "find_best":
                # More complex function for testing different strategies
                X_train, y_train, X_test, y_test = generate_train_test_data(
                    function=lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5)
                    + 1.5 * np.cos(X[:, 1]) * X[:, 2] ** 2,
                    n_samples_train=5000,
                    n_samples_test=1000,
                    n_features=3,
                    noise_std=0.7,
                    add_outliers=True,
                    random_state=42,
                )
            else:
                # Simpler function for single model evaluation
                X_train, y_train, X_test, y_test = generate_train_test_data(
                    function=lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5)
                    + 1.5 * np.cos(X[:, 1])
                    - X[:, 2],
                    n_samples_train=5000,
                    n_samples_test=1000,
                    n_features=3,
                    noise_std=0.5,
                    add_outliers=True,
                    random_state=42,
                )

            # Save the generated data in both formats
            formats = ["csv", "npy"]
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
            # Load data from files
            logger.info(f"Loading data from {args.input_dir}...")

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

        # Use RegressionFlow for both evaluation modes
        flow = RegressionFlow()
        metric_to_optimize = Metric[args.metric]

        if args.evaluation_mode == "single":
            # Single model evaluation mode
            partition_mode = PartitionMode[args.partition_mode]
            regressor_type = RegressorType[args.regressor_type]

            logger.info(
                f"Evaluating {regressor_type} with {partition_mode} partitioning (n={args.n_partitions})"
            )

            # Use RegressionFlow's find_best_strategy with specific configuration
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

            # Display results
            logger.info("Model evaluation completed")
            logger.info(f"Partition mode: {result.partition_mode}")
            logger.info(f"Number of partitions: {result.n_partitions}")
            logger.info(f"Regressor type: {result.model_type}")

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
                    {
                        "y_true": y_test,
                        "y_pred": y_test_pred,
                        "error": y_test - y_test_pred,
                    }
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

        else:  # "find_best" mode
            # Determine partitioning modes and regressor types to evaluate
            if args.test_mode:
                # Reduced set for faster testing
                partition_modes = [
                    PartitionMode.NONE,
                    PartitionMode.KMEANS,
                    PartitionMode.DECISION_TREE,
                ]
                regressor_types = [
                    RegressorType.LINEAR,
                    RegressorType.RANDOM_FOREST,
                    RegressorType.GRADIENT_BOOSTING,
                ]
                n_partitions = 3
            else:
                # Full evaluation
                partition_modes = list(PartitionMode)
                regressor_types = list(RegressorType)
                n_partitions = args.n_partitions

            logger.info(
                f"Finding best model among {len(partition_modes)} partition modes and {len(regressor_types)} regressor types"
            )

            # Use RegressionFlow to find best strategy
            result = flow.find_best_strategy(
                X_train,
                y_train,
                X_test,
                y_test,
                partition_modes=partition_modes,
                regressor_types=regressor_types,
                n_partitions=n_partitions,
                n_jobs=args.n_jobs,
                metrics_to_optimize=metric_to_optimize,
            )

            # Display results
            logger.info("Model evaluation completed")
            logger.info(f"Best strategy found:")
            logger.info(f"Partition mode: {result.partition_mode}")
            logger.info(f"Number of partitions: {result.n_partitions}")
            logger.info(f"Regressor type: {result.model_type}")

            # Print formatted metrics
            metrics_table = format_statistics_table(result.metrics)
            logger.info(f"Best model performance metrics:\n{metrics_table}")

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
                    {
                        "y_true": y_test,
                        "y_pred": y_test_pred,
                        "error": y_test - y_test_pred,
                    }
                )

                train_df.to_csv(
                    os.path.join(predictions_dir, "best_model_train_predictions.csv"),
                    index=False,
                )
                test_df.to_csv(
                    os.path.join(predictions_dir, "best_model_test_predictions.csv"),
                    index=False,
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
                    title=f"Best Model: {result.model_type.name} with {result.partition_mode.name}",
                    output_dir=viz_dir,
                )
                logger.info(f"Generated visualizations in {viz_dir}")

        # Print execution time
        elapsed_time = time() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds")

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
