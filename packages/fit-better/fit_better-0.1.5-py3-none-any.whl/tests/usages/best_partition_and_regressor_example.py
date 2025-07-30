#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Example script for finding the optimal partition strategy and regression algorithm using pre-existing data files.

Usage:
    python best_partition_and_regressor_example.py [options]

This script demonstrates how to use fit-better to find the best combination
of partitioning strategy and regression algorithm given pre-existing data files.
It loads X_train, y_train, X_test, y_test from files and evaluates multiple
partition strategies with different regression algorithms to identify the optimal approach.

Options:
    --input-dir DIR      Directory containing input data files (default: data)
    --x-train FILE       Filename for X_train data (default: X_train.npy)
    --y-train FILE       Filename for y_train data (default: y_train.npy)
    --x-test FILE        Filename for X_test data (default: X_test.npy)
    --y-test FILE        Filename for y_test data (default: y_test.npy)
    --delimiter CHAR     Delimiter character for CSV or TXT files (default: ',')
    --header OPTION      How to handle headers in CSV/TXT files: 'infer' or 'none' (default: 'infer')
    --n-jobs N           Number of parallel jobs (default: 1)
    --output-dir DIR     Directory to save results (default: best_model_results)
    --test-mode          Run in test mode with fewer combinations for faster testing
"""
import os
import sys
import argparse
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from time import time
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import from fit_better
from fit_better import (
    PartitionMode,
    RegressorType,
    train_models_on_partitions,
    predict_with_partitioned_models,
    save_model,
    load_data_from_files,
    generate_synthetic_data_by_function,
    save_data,
    setup_logging,
)
from fit_better.utils.statistics import calc_regression_statistics
from fit_better.utils.ascii import print_ascii_table

# Import utilities for argument parsing
from tests.utils.argparse_utils import (
    get_default_parser,
    add_io_args,
    add_model_args,
    add_output_args,
)

# Configure logging
logger = logging.getLogger(__name__)


def find_best_partition_and_regressor(
    X_train, y_train, X_test, y_test, n_jobs=1, output_dir=None, test_mode=False
):
    """
    Find the best combination of partition strategy and regression algorithm.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        test_mode: If True, run with fewer combinations for faster testing

    Returns:
        Dictionary with results of the best combination
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Define partition modes to test
    if test_mode:
        partition_modes = [PartitionMode.RANGE, PartitionMode.KMEANS]
        regressor_types = [
            RegressorType.LINEAR,
            RegressorType.RIDGE,
            RegressorType.RANDOM_FOREST,
        ]
        partition_counts = [2, 5]
    else:
        partition_modes = [
            PartitionMode.RANGE,
            PartitionMode.PERCENTILE,
            PartitionMode.EQUAL_WIDTH,
            PartitionMode.KMEANS,
        ]
        regressor_types = [
            RegressorType.LINEAR,
            RegressorType.POLYNOMIAL_2,
            RegressorType.RIDGE,
            RegressorType.HUBER,
            RegressorType.RANDOM_FOREST,
            RegressorType.GRADIENT_BOOSTING,
            RegressorType.XGBOOST,
        ]
        partition_counts = [2, 3, 5, 8]

    # Try to add KMedoids if available
    try:
        from sklearn_extra.cluster import KMedoids

        if not test_mode:
            partition_modes.append(PartitionMode.KMEDOIDS)
    except ImportError:
        logger.warning(
            "sklearn_extra not installed. KMedoids partitioning will be skipped."
        )

    # Store results for all combinations
    results = []

    logger.info("Evaluating multiple partition strategies and regression algorithms...")
    logger.info(f"Partition modes: {[mode.name for mode in partition_modes]}")
    logger.info(f"Regressor types: {[reg.name for reg in regressor_types]}")
    logger.info(f"Partition counts: {partition_counts}")

    # Evaluate all combinations
    for partition_mode in partition_modes:
        for n_partitions in partition_counts:
            for regressor_type in regressor_types:
                try:
                    logger.info(
                        f"Testing {partition_mode.name} partitioning with {n_partitions} partitions and {regressor_type.name} regressor..."
                    )

                    # Train models on partitions
                    models = train_models_on_partitions(
                        X_train,
                        y_train,
                        partition_mode=partition_mode,
                        n_partitions=n_partitions,
                        regressor_type=regressor_type,
                        n_jobs=n_jobs,
                    )

                    # Make predictions
                    y_train_pred = predict_with_partitioned_models(
                        models, X_train, n_jobs=n_jobs
                    )
                    y_test_pred = predict_with_partitioned_models(
                        models, X_test, n_jobs=n_jobs
                    )

                    # Calculate metrics
                    train_metrics = calc_regression_statistics(y_train, y_train_pred)
                    test_metrics = calc_regression_statistics(y_test, y_test_pred)

                    # Store results
                    results.append(
                        {
                            "partition_mode": partition_mode.name,
                            "n_partitions": n_partitions,
                            "regressor_type": regressor_type.name,
                            "train_mae": train_metrics["mae"],
                            "train_rmse": train_metrics["rmse"],
                            "train_r2": train_metrics["r2"],
                            "test_mae": test_metrics["mae"],
                            "test_rmse": test_metrics["rmse"],
                            "test_r2": test_metrics["r2"],
                            "models": models,
                            "train_predictions": y_train_pred,
                            "test_predictions": y_test_pred,
                        }
                    )

                    logger.info(
                        f"Results: Train MAE={train_metrics['mae']:.4f}, Test MAE={test_metrics['mae']:.4f}, "
                        f"Train R²={train_metrics['r2']:.4f}, Test R²={test_metrics['r2']:.4f}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error with {partition_mode.name} partitioning, {n_partitions} partitions, "
                        f"and {regressor_type.name} regressor: {str(e)}"
                    )

    # Find the best combination based on test R²
    best_result = max(results, key=lambda x: x["test_r2"])

    # Add a metrics key for compatibility with the test
    best_result["metrics"] = {
        "train_mae": best_result["train_mae"],
        "train_rmse": best_result["train_rmse"],
        "train_r2": best_result["train_r2"],
        "test_mae": best_result["test_mae"],
        "test_rmse": best_result["test_rmse"],
        "test_r2": best_result["test_r2"],
        "mae": best_result["test_mae"],  # Add direct mae key for test compatibility
        "rmse": best_result["test_rmse"],  # Add direct rmse key for test compatibility
        "r2": best_result["test_r2"],  # Add direct r2 key for test compatibility
    }

    logger.info("\nBest combination:")
    logger.info(f"Partition mode: {best_result['partition_mode']}")
    logger.info(f"Number of partitions: {best_result['n_partitions']}")
    logger.info(f"Regressor type: {best_result['regressor_type']}")
    logger.info(f"Test R²: {best_result['test_r2']:.4f}")

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Save results
    if output_dir:
        # Save best model
        model_filepath = os.path.join(output_dir, "best_model.joblib")
        logger.info(f"Saving best model to {model_filepath}")

        save_model(
            {"models": best_result["models"]},
            model_filepath,
            metadata={
                "partition_mode": best_result["partition_mode"],
                "n_partitions": best_result["n_partitions"],
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

        # Save all results to CSV
        results_csv = os.path.join(output_dir, "all_results.csv")
        results_df.drop(
            ["models", "train_predictions", "test_predictions"], axis=1
        ).to_csv(results_csv, index=False)

        # Save partition regressor results CSV (for test compatibility)
        partition_regressor_csv = os.path.join(
            output_dir, "partition_regressor_results.csv"
        )
        results_df.drop(
            ["models", "train_predictions", "test_predictions"], axis=1
        ).to_csv(partition_regressor_csv, index=False)

        # Generate visualizations
        generate_visualizations(results_df, best_result, output_dir)

    return best_result


def generate_visualizations(results_df, best_result, output_dir):
    """
    Generate visualizations comparing different partition strategies and regression algorithms.

    Args:
        results_df: DataFrame with results for all combinations
        best_result: Dictionary with results for the best combination
        output_dir: Directory to save visualizations
    """
    # Create a directory for visualizations
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Filter out combinations with poor performance for better visualization
    filtered_df = results_df[results_df["test_r2"] > 0]

    # -------------------- Top Combinations Plot --------------------
    # Bar plot of test R² for different combinations
    plt.figure(figsize=(12, 8))

    # Create a new column for the x-axis labels
    filtered_df["combination"] = filtered_df.apply(
        lambda row: f"{row['partition_mode']}\n{row['n_partitions']} partitions\n{row['regressor_type']}",
        axis=1,
    )

    # Sort by test R²
    filtered_df = filtered_df.sort_values("test_r2", ascending=False)

    # Take top 15 combinations for readability
    top_df = filtered_df.head(15)

    # Create the bar plot
    bars = plt.bar(top_df["combination"], top_df["test_r2"])

    # Highlight the best combination
    best_idx = (
        top_df["combination"]
        .tolist()
        .index(
            f"{best_result['partition_mode']}\n{best_result['n_partitions']} partitions\n{best_result['regressor_type']}"
        )
        if f"{best_result['partition_mode']}\n{best_result['n_partitions']} partitions\n{best_result['regressor_type']}"
        in top_df["combination"].tolist()
        else None
    )

    if best_idx is not None:
        bars[best_idx].set_color("red")

    plt.title("Top 15 Combinations by Test R²")
    plt.ylabel("Test R²")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(plots_dir, "top_combinations_test_r2.png"))
    plt.savefig(
        os.path.join(output_dir, "top_combinations.png")
    )  # For test compatibility
    plt.close()

    # -------------------- Plot MAE by Partition Count --------------------
    # Create plot for MAE by partition count
    plt.figure(figsize=(10, 8))

    # Group by number of partitions and calculate mean test_mae
    partition_mae = filtered_df.groupby("n_partitions")["test_mae"].mean().reset_index()

    plt.plot(
        partition_mae["n_partitions"], partition_mae["test_mae"], "o-", linewidth=2
    )
    plt.xlabel("Number of Partitions")
    plt.ylabel("Mean Absolute Error (MAE)")
    plt.title("MAE by Partition Count")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(plots_dir, "mae_by_partition_count.png"))
    plt.savefig(
        os.path.join(output_dir, "mae_by_partition_count.png")
    )  # For test compatibility
    plt.close()

    # -------------------- Heatmap --------------------
    # Heatmap of test R² for different partition modes and regressor types
    plt.figure(figsize=(12, 8))

    # Calculate mean test R² for each partition mode and regressor type
    pivot_df = filtered_df.pivot_table(
        index="partition_mode",
        columns="regressor_type",
        values="test_r2",
        aggfunc="mean",
    )

    # Create the heatmap
    # Check if pivot_df is empty or has only one unique value to avoid singular transformation
    plt.figure(figsize=(8, 6))
    if pivot_df.empty:
        # Handle empty DataFrame case
        plt.text(
            0.5,
            0.5,
            "No data available for heatmap",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.title("Mean Test R² (no data)")
        im = None
    elif pivot_df.values.size > 0 and len(set(pivot_df.values.flat)) <= 1:
        # Handle case with identical values by using a solid color plot
        value_to_show = pivot_df.values.flat[0] if pivot_df.values.size > 0 else np.nan
        plt.text(
            0.5,
            0.5,
            f"Uniform R² value: {value_to_show:.4f}",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.title("Mean Test R² (uniform values)")
        im = None
    else:
        # Regular case with varying values
        im = plt.imshow(pivot_df.values, cmap="YlGnBu")
        # Add colorbar
        plt.colorbar(im, label="Mean Test R²")

    # Add labels
    plt.xticks(range(len(pivot_df.columns)), pivot_df.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot_df.index)), pivot_df.index)

    # Add a title
    plt.title("Mean Test R² by Partition Mode and Regressor Type")

    # Add values to cells if pivot_df is not empty
    if not pivot_df.empty:
        for i in range(len(pivot_df.index)):
            for j in range(len(pivot_df.columns)):
                try:
                    value = pivot_df.iloc[i, j]
                    if pd.notnull(value):
                        plt.text(
                            j,
                            i,
                            f"{value:.3f}",
                            ha="center",
                            va="center",
                            color="black",
                        )
                except (IndexError, ValueError):
                    # Skip if there's an issue with a particular cell
                    pass

    plt.tight_layout()

    # Save the figure - save with both names for compatibility
    plt.savefig(os.path.join(plots_dir, "mean_test_r2_heatmap.png"))
    plt.savefig(
        os.path.join(output_dir, "partition_regressor_heatmap.png")
    )  # For test compatibility
    plt.close()

    # Scatter plot of train R² vs test R²
    plt.figure(figsize=(10, 8))

    # Create the scatter plot, but only if there's data to plot
    if not filtered_df.empty:
        scatter = plt.scatter(
            filtered_df["train_r2"],
            filtered_df["test_r2"],
            c=filtered_df["partition_mode"].astype("category").cat.codes,
            alpha=0.7,
            s=50,
            cmap="viridis",
        )

        # Add a legend only if there are elements to include
        legend_elements = scatter.legend_elements()[0]
        if len(legend_elements) > 0:
            legend1 = plt.legend(
                legend_elements,
                filtered_df["partition_mode"].unique(),
                title="Partition Mode",
                loc="upper left",
            )
            plt.gca().add_artist(legend1)

    # Add a diagonal line
    lims = [
        np.min([plt.gca().get_xlim(), plt.gca().get_ylim()]),
        np.max([plt.gca().get_xlim(), plt.gca().get_ylim()]),
    ]
    plt.plot(lims, lims, "k--", alpha=0.3, zorder=0)

    # Highlight the best combination
    best_point = plt.scatter(
        best_result["train_r2"],
        best_result["test_r2"],
        c="red",
        s=200,
        marker="*",
        edgecolors="black",
        label="Best Combination",
    )
    plt.legend([best_point], ["Best Combination"], loc="lower right")

    # Add labels and title
    plt.xlabel("Train R²")
    plt.ylabel("Test R²")
    plt.title("Train R² vs Test R² for Different Combinations")

    # Add text for the best combination
    plt.annotate(
        f"{best_result['partition_mode']}, {best_result['n_partitions']} partitions, {best_result['regressor_type']}",
        xy=(best_result["train_r2"], best_result["test_r2"]),
        xytext=(10, -30),
        textcoords="offset points",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.3"),
    )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save the figure
    plt.savefig(os.path.join(plots_dir, "train_vs_test_r2.png"))
    plt.close()


def main():
    # Parse command line arguments using the utility function
    parser = argparse.ArgumentParser(
        description="Find the best combination of partition strategy and regression algorithm"
    )

    # Add argument groups
    add_io_args(parser)
    add_model_args(parser, include_partition=False, include_regressor=False)
    # Use proper path under data_gen for results
    tests_dir = Path(__file__).resolve().parent.parent
    add_output_args(
        parser, default_output_dir=str(tests_dir / "data_gen" / "best_model_results")
    )

    # Add test mode argument
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with fewer combinations for faster testing",
    )

    args = parser.parse_args()

    try:
        # Set up logging
        os.makedirs(args.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(
            args.output_dir, f"best_partition_finder_{timestamp}.log"
        )
        logger = setup_logging(log_file)

        logger.info("Starting best_partition_and_regressor_example")
        logger.info(f"Configuration: {vars(args)}")

        # Check for existing data or generate synthetic data
        input_files = [args.x_train, args.y_train, args.x_test, args.y_test]
        input_paths = [os.path.join(args.input_dir, f) for f in input_files]

        if not all(os.path.exists(p) for p in input_paths):
            logger.info(
                "One or more input files not found, generating synthetic data..."
            )
            os.makedirs(args.input_dir, exist_ok=True)

            # Generate synthetic data with a complex function to give different partition strategies a challenge
            X_train, y_train, X_test, y_test = generate_synthetic_data_by_function(
                function=lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5)
                + 1.5 * np.cos(X[:, 1]) * X[:, 2] ** 2,
                n_samples_train=5000,
                n_samples_test=1000,
                n_features=3,
                noise_std=0.7,
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

            # Create symlinks/copies for backward compatibility
            for target, source in zip(
                input_files,
                [
                    f"data_X_train.npy",
                    f"data_y_train.npy",
                    f"data_X_test.npy",
                    f"data_y_test.npy",
                ],
            ):
                target_path = os.path.join(args.input_dir, target)
                source_path = os.path.join(args.input_dir, source)
                if os.path.exists(source_path) and not os.path.exists(target_path):
                    try:
                        import shutil

                        shutil.copy2(source_path, target_path)
                    except Exception as e:
                        logger.warning(
                            f"Couldn't create file copy from {source_path} to {target_path}: {e}"
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

        # Find the best partition strategy and regression algorithm
        best_result = find_best_partition_and_regressor(
            X_train,
            y_train,
            X_test,
            y_test,
            n_jobs=args.n_jobs,
            output_dir=args.output_dir,
            test_mode=args.test_mode,
        )

        end_time = time()
        logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")
        logger.info(f"Results saved to {args.output_dir}")
        logger.info(f"Log file: {log_file}")

        # Print conclusion
        print("\nBest combination found:")
        print(f"Partition mode: {best_result['partition_mode']}")
        print(f"Number of partitions: {best_result['n_partitions']}")
        print(f"Regressor type: {best_result['regressor_type']}")
        print(f"Test R²: {best_result['test_r2']:.4f}")
        print(f"\nResults saved to {args.output_dir}")
        print(f"Log file: {log_file}")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
