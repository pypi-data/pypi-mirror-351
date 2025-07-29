#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Example script for training and evaluating models with a specific partition strategy and regressor type.

Usage:
    python partition_and_regressor_example.py [options]

This script demonstrates how to use fit-better to train models with a specified
partition mode and regressor type. It loads X_train, y_train, X_test, y_test from files,
trains models, makes predictions, and visualizes the results.

Options:
    --input-dir DIR      Directory containing input data files (default: data)
    --x-train FILE       Filename for X_train data (default: X_train.npy)
    --y-train FILE       Filename for y_train data (default: y_train.npy)
    --x-test FILE        Filename for X_test data (default: X_test.npy)
    --y-test FILE        Filename for y_test data (default: y_test.npy)
    --delimiter CHAR     Delimiter character for CSV or TXT files (default: ' ' for TXT, ',' for CSV)
    --header OPTION      How to handle headers in CSV/TXT files: 'infer' or 'none' (default: 'infer')
    --partition-mode     Partition mode to use (default: KMEANS)
    --n-partitions INT   Number of partitions to create (default: 5)
    --regressor-type     Regressor type to use (default: RANDOM_FOREST)
    --n-jobs N           Number of parallel jobs (default: 1)
    --output-dir DIR     Directory to save results (default: model_results)
    --save-predictions   Save training and evaluation predictions to CSV files
    --impute-strategy    Strategy for imputing missing values: 'mean', 'median', 'most_frequent', 'constant' (default: 'mean')
    --impute-value       Value to use with 'constant' imputation strategy (default: 0)
    --drop-na            Drop rows with any NaN values instead of imputing
    --use-regression-flow Use RegressionFlow for a more streamlined workflow
"""
import os
import sys
import argparse
import logging
import numpy as np
import pandas as pd
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
    train_models_on_partitions,
    predict_with_partitioned_models,
    save_model,
    setup_logging,
    preprocess_data_for_regression,
    generate_synthetic_data_by_function,
    save_data,
    load_data_from_files,
    calc_regression_statistics,
    create_regression_report_plots,
    CSVMgr,
)
from fit_better.utils.statistics import print_partition_statistics
from fit_better.utils.ascii import print_ascii_table
from fit_better.utils.plotting import (
    visualize_partition_boundaries,
    visualize_partitioned_data,
)

# Import utilities for argument parsing
from tests.utils.argparse_utils import get_default_parser

# Import scikit-learn preprocessing modules
from sklearn.impute import SimpleImputer

# Logger will be configured in main function using setup_logging
logger = None


def preprocess_data(
    X_train,
    y_train,
    X_test,
    y_test,
    impute_strategy="mean",
    impute_value=0,
    drop_na=False,
):
    """
    Preprocess the data by handling missing values and scaling features.
    """
    # First check for string/categorical features using fit_better's utility
    logger.info("Preprocessing data...")
    X_train_processed, X_test_processed, encoder = preprocess_data_for_regression(
        X_train, X_test, categorical_encode_method="onehot"
    )

    # If we had categorical features, use the processed data
    if encoder is not None:
        logger.info(f"Processed categorical features with {type(encoder).__name__}")
        X_train = X_train_processed
        X_test = X_test_processed

    # Handle NaN values
    train_nas = np.isnan(X_train).sum().sum()
    test_nas = np.isnan(X_test).sum().sum()
    train_y_nas = np.isnan(y_train).sum()
    test_y_nas = np.isnan(y_test).sum()

    if train_nas > 0 or test_nas > 0 or train_y_nas > 0 or test_y_nas > 0:
        logger.info(
            f"Found NaN values: X_train: {train_nas}, X_test: {test_nas}, y_train: {train_y_nas}, y_test: {test_y_nas}"
        )

    if drop_na:
        # Drop rows with NaN values
        logger.info("Dropping rows with NaN values...")
        train_mask = ~np.isnan(X_train).any(axis=1) & ~np.isnan(y_train).any(axis=1)
        test_mask = ~np.isnan(X_test).any(axis=1) & ~np.isnan(y_test).any(axis=1)

        X_train = X_train[train_mask]
        y_train = y_train[train_mask]
        X_test = X_test[test_mask]
        y_test = y_test[test_mask]

        logger.info(
            f"After dropping: X_train {X_train.shape}, y_train {y_train.shape}, X_test {X_test.shape}, y_test {y_test.shape}"
        )
    else:
        # Impute missing values
        logger.info(f"Imputing missing values using '{impute_strategy}' strategy...")

        # Impute X_train and X_test
        if impute_strategy == "constant":
            imputer = SimpleImputer(strategy=impute_strategy, fill_value=impute_value)
        else:
            imputer = SimpleImputer(strategy=impute_strategy)

        if train_nas > 0 or test_nas > 0:
            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

        # Impute y_train and y_test if needed
        if train_y_nas > 0 or test_y_nas > 0:
            y_imputer = SimpleImputer(strategy=impute_strategy)
            y_train = y_imputer.fit_transform(y_train.reshape(-1, 1)).ravel()
            y_test = y_imputer.transform(y_test.reshape(-1, 1)).ravel()

    # Check if we still have NaN values after preprocessing
    if np.isnan(X_train).sum().sum() > 0 or np.isnan(X_test).sum().sum() > 0:
        raise ValueError(
            "Still found NaN values after preprocessing. Please check your data or preprocessing steps."
        )

    if np.isnan(y_train).sum() > 0 or np.isnan(y_test).sum() > 0:
        raise ValueError(
            "Still found NaN values in target data after preprocessing. Please check your data or preprocessing steps."
        )

    return X_train, y_train, X_test, y_test


def train_and_evaluate_models(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_mode,
    n_partitions,
    regressor_type,
    n_jobs=1,
    output_dir=None,
    save_predictions=False,
    use_regression_flow=False,
    **preprocessing_params,
):
    """
    Train models with the specified partition mode and regressor type, and evaluate them.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_mode: Partition mode to use
        n_partitions: Number of partitions to create
        regressor_type: Regressor type to use
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        save_predictions: Whether to save predictions to CSV files
        use_regression_flow: Whether to use RegressionFlow for training
        **preprocessing_params: Parameters for preprocessing

    Returns:
        Dictionary with models, predictions, and metrics
    """
    # For KMEANS partitioning, we need to ensure we have enough data for clustering
    if partition_mode == PartitionMode.KMEANS and len(X_train) < n_partitions * 10:
        logger.info(
            f"KMEANS partitioning requires more data points. Duplicating training data."
        )
        # Duplicate the data to ensure we have enough for KMEANS
        repeat_factor = max(2, int(np.ceil(n_partitions * 10 / len(X_train))))
        X_train = np.vstack([X_train] * repeat_factor)
        y_train = np.hstack([y_train] * repeat_factor)
        logger.info(
            f"Training data expanded from {len(y_train) // repeat_factor} to {len(y_train)} points"
        )

    if output_dir:
        # Ensure the output_dir is under tests/data_gen
        tests_dir = Path(__file__).resolve().parent.parent

        # If output_dir is not absolute or doesn't start with the tests path,
        # place it under tests/data_gen
        if not os.path.isabs(output_dir) or not str(output_dir).startswith(
            str(tests_dir)
        ):
            output_dir = str(tests_dir / "data_gen" / output_dir)

        os.makedirs(output_dir, exist_ok=True)
        plots_dir = os.path.join(output_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        logger.info(f"Using output directory: {output_dir}")

    # Preprocess the data
    X_train, y_train, X_test, y_test = preprocess_data(
        X_train, y_train, X_test, y_test, **preprocessing_params
    )

    results = {}

    if use_regression_flow:
        logger.info("Using RegressionFlow API for training and evaluation")

        # Initialize RegressionFlow
        regression_flow = RegressionFlow()

        # Find best strategy using the specified partition mode and regressor type
        start_time = time()
        flow_result = regression_flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            partition_modes=[partition_mode],  # Use as a list
            regressor_types=[regressor_type],  # Use as a list
            n_partitions=n_partitions,
            n_jobs=n_jobs,
        )
        training_time = time() - start_time

        # Make predictions on test data
        start_time = time()
        y_pred_test = regression_flow.predict(X_test)
        prediction_time = time() - start_time

        # Make predictions on training data (for thoroughness)
        y_pred_train = regression_flow.predict(X_train)

        # Store the results
        results = {
            "model": flow_result.model,
            "model_type": flow_result.model_type,
            "partitioner_details": flow_result.partitioner_details,
            "partition_mode": flow_result.partition_mode,
            "n_partitions": flow_result.n_partitions,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
            "y_train": y_train,
            "y_test": y_test,
            "metrics": flow_result.metrics,
            "training_time": training_time,
            "prediction_time": prediction_time,
        }

        logger.info("RegressionFlow trained and evaluated successfully")
    else:
        # Train the models using the original approach
        logger.info(
            f"Training models with {partition_mode.value} partitioning and {regressor_type.value} regressor"
        )
        start_time = time()
        models_result = train_models_on_partitions(
            X_train,
            y_train,
            partition_mode=partition_mode,
            n_partitions=n_partitions,
            regressor_type=regressor_type,
            n_jobs=n_jobs,
        )
        training_time = time() - start_time

        # Extract the trained models and partitioner
        if isinstance(models_result, tuple) and len(models_result) >= 2:
            # Updated API returns (models, partitioner)
            trained_models, partitioner = models_result
        else:
            # Fallback for older API
            trained_models = models_result.get("models", [])
            partitioner = models_result.get("partitioner", None)

        if not trained_models:
            logger.error("No models were trained successfully")
            raise ValueError("Failed to train models with the specified configuration")

        # Make predictions on test data
        start_time = time()
        y_pred_test = predict_with_partitioned_models(
            trained_models, X_test, partitioner
        )
        prediction_time = time() - start_time

        # Make predictions on training data
        y_pred_train = predict_with_partitioned_models(
            trained_models, X_train, partitioner
        )

        # Calculate regression metrics
        metrics = calc_regression_statistics(y_test, y_pred_test)

        # Store the results
        results = {
            "models": trained_models,
            "partitioner": partitioner,
            "partition_mode": partition_mode,
            "regressor_type": regressor_type,
            "n_partitions": n_partitions,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
            "y_train": y_train,
            "y_test": y_test,
            "metrics": metrics,
            "training_time": training_time,
            "prediction_time": prediction_time,
        }

        logger.info("Models trained and evaluated successfully")

    # Log performance metrics
    logger.info(
        f"Performance: "
        f"R²={results['metrics']['r2']:.4f}, "
        f"RMSE={results['metrics']['rmse']:.4f}, "
        f"MAE={results['metrics']['mae']:.4f}"
    )

    # Save predictions if requested
    if save_predictions and output_dir:
        logger.info("Saving predictions to CSV files")
        train_predictions_df = pd.DataFrame({"y_true": y_train, "y_pred": y_pred_train})
        test_predictions_df = pd.DataFrame({"y_true": y_test, "y_pred": y_pred_test})

        train_predictions_path = os.path.join(output_dir, "train_predictions.csv")
        test_predictions_path = os.path.join(output_dir, "test_predictions.csv")

        train_predictions_df.to_csv(train_predictions_path, index=False)
        test_predictions_df.to_csv(test_predictions_path, index=False)

        logger.info(
            f"Predictions saved to {train_predictions_path} and {test_predictions_path}"
        )

    # Create visualizations
    if output_dir:
        logger.info("Creating visualization plots")
        try:
            plots_count = 0

            # Use the official visualize_partitioned_data function
            if X_train.shape[1] <= 2:  # Only plot for 1D or 2D data
                partition_plot_path = os.path.join(plots_dir, "partitioned_data.png")

                # Use the proper visualization function
                visualize_partitioned_data(
                    X=X_train,
                    y=y_train,
                    partition_mode=partition_mode,
                    n_parts=n_partitions,
                    save_path=partition_plot_path,
                    title=f"Data with {partition_mode.value} partitioning ({n_partitions} partitions)",
                )

                logger.info(f"Data visualization saved to {partition_plot_path}")
                plots_count += 1

            # Create regression report plots
            report_plots = create_regression_report_plots(
                y_true=y_test,
                y_pred=y_pred_test,
                output_dir=plots_dir,
                model_name=f"{partition_mode.value}_{regressor_type.value}",
            )

            plots_count += len(report_plots)
            logger.info(f"Created {plots_count} plots in {plots_dir}")

        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            logger.info("Continuing without visualizations")

    return results


def main():
    # Parse command line arguments using the utility function
    parser = get_default_parser(
        description="Train and evaluate models with a specific partition strategy and regressor type"
    )

    # No need to add --use-regression-flow here since it's already included in the default parser

    args = parser.parse_args()

    # Set up logging
    global logger
    partition_name = args.partition_mode
    regressor_name = args.regressor_type
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create logs directory if it doesn't exist
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir, exist_ok=True)

    log_file = os.path.join(
        args.log_dir, f"{partition_name}_{regressor_name}_{timestamp}.log"
    )
    logger = setup_logging(log_file)

    logger.info(
        f"Starting partition_and_regressor_example with {partition_name} and {regressor_name}"
    )
    logger.info(f"Configuration: {vars(args)}")

    try:
        # Load data
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

        logger.info(
            f"Data shapes: X_train {X_train.shape}, y_train {y_train.shape}, X_test {X_test.shape}, y_test {y_test.shape}"
        )

        # Convert partition mode and regressor type strings to enum values
        partition_mode = PartitionMode[args.partition_mode]
        regressor_type = RegressorType[args.regressor_type]

        # Train and evaluate the models
        start_time = time()
        results = train_and_evaluate_models(
            X_train,
            y_train,
            X_test,
            y_test,
            partition_mode=partition_mode,
            n_partitions=args.n_partitions,
            regressor_type=regressor_type,
            n_jobs=args.n_jobs,
            output_dir=args.output_dir,
            save_predictions=args.save_predictions,
            impute_strategy=args.impute_strategy,
            impute_value=args.impute_value,
            drop_na=args.drop_na,
        )
        total_time = time() - start_time

        # Log overall execution time
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        logger.info(f"Training time: {results['training_time']:.2f} seconds")
        logger.info(f"Prediction time: {results['prediction_time']:.2f} seconds")

        # Print final performance metrics
        logger.info("\n=== Performance Summary ===")
        col_labels = ["Metric", "Value"]
        row_data = [
            ["R²", f"{results['metrics']['r2']:.4f}"],
            ["RMSE", f"{results['metrics']['rmse']:.4f}"],
            ["MAE", f"{results['metrics']['mae']:.4f}"],
            ["MSE", f"{results['metrics']['mse']:.4f}"],
            ["Training Time", f"{results['training_time']:.2f} seconds"],
            ["Prediction Time", f"{results['prediction_time']:.2f} seconds"],
        ]
        print_ascii_table(col_labels, row_data)

        # Log where to find results
        if args.output_dir:
            logger.info(f"Results saved to: {os.path.abspath(args.output_dir)}")

        logger.info(f"Log file: {os.path.abspath(log_file)}")
        logger.info("Execution completed successfully!")

        return 0

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
