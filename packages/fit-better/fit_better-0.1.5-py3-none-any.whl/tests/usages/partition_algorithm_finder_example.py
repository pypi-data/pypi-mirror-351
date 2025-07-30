#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Example script for finding the optimal partition strategy and regression algorithm.

Usage:
    python partition_algorithm_finder_example.py [options]

This script demonstrates how to use fit-better to automatically find the best combination
of partitioning strategy and regression algorithm for a given dataset. It tests multiple
partition strategies with different regression algorithms to identify the optimal approach.

Options:
    --n-samples N       Number of samples to generate (default: 2000)
    --noise-level N     Standard deviation of noise to add (default: 0.7)
    --n-jobs N          Number of parallel jobs (default: 1)
    --output-dir DIR    Directory to save results (default: partition_finder_results)
    --function-type STR Type of synthetic data to generate (default: complex)
"""
import os
import sys
import time
import argparse
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import from fit_better
from fit_better import (
    PartitionMode,
    RegressorType,
    train_models_on_partitions,
    predict_with_partitioned_models,
    generate_synthetic_data_by_function,
    save_model,
)
from fit_better.utils.statistics import calc_regression_statistics
from fit_better.core.partitioning import get_partition_boundaries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_best_partition_algorithm_combination(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    n_jobs: int = 1,
    output_dir: str = None,
    regressor_types: List[str] = None,
    partition_modes: List[str] = None,
    partition_counts: List[int] = None,
) -> Dict[str, Any]:
    """
    Find the best combination of partition strategy and regression algorithm.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        regressor_types: List of regressor types to test
        partition_modes: List of partition modes to test
        partition_counts: List of number of partitions to test

    Returns:
        Dictionary with results for best combination
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Define partition modes to test
    if partition_modes is None:
        partition_modes = [
            PartitionMode.RANGE,
            PartitionMode.PERCENTILE,
            PartitionMode.EQUAL_WIDTH,
            PartitionMode.KMEANS,
        ]

    # Try to add KMedoids if available
    try:
        from sklearn_extra.cluster import KMedoids

        partition_modes.append(PartitionMode.KMEDOIDS)
    except ImportError:
        logger.warning(
            "sklearn_extra not installed. KMedoids partitioning will be skipped."
        )

    # Define regressor types to test
    if regressor_types is None:
        regressor_types = [
            RegressorType.LINEAR,
            RegressorType.POLYNOMIAL_2,
            RegressorType.POLYNOMIAL_3,
            RegressorType.RIDGE,
            RegressorType.HUBER,
            RegressorType.RANDOM_FOREST,
            RegressorType.GRADIENT_BOOSTING,
        ]

    # Define number of partitions to test
    if partition_counts is None:
        partition_counts = [1, 2, 3, 5, 8, 10]

    # Also test a single global model (no partitioning) for each regressor type
    logger.info("Testing global models (no partitioning)...")
    global_results = test_global_models(
        X_train, y_train, X_test, y_test, regressor_types, n_jobs
    )

    # Store results for all combinations
    all_results = []

    # Track best combination
    best_mae = float("inf")
    best_result = None

    # Test each combination
    total_combinations = (
        len(partition_modes) * len(regressor_types) * len(partition_counts)
    )
    combination_count = 0

    logger.info(f"Testing {total_combinations} partition and algorithm combinations...")
    start_time = time.time()

    for partition_mode in partition_modes:
        for n_parts in partition_counts:
            # Skip n_parts=1 for all but one mode, as they're all equivalent to a global model
            if n_parts == 1 and partition_mode != partition_modes[0]:
                continue

            # Get partition boundaries
            try:
                # First test if the data partitioning is possible
                boundaries = get_partition_boundaries(
                    X_train, partition_mode, n_parts, min_size=10, n_jobs=n_jobs
                )

                # The actual number of partitions might be less than requested due to min_size constraint
                actual_n_parts = len(boundaries) + 1

                if actual_n_parts < 1:
                    logger.warning(
                        f"Could not create partitions with {partition_mode} and n_parts={n_parts}"
                    )
                    continue

                for regressor_type in regressor_types:
                    combination_count += 1
                    logger.info(
                        f"Testing combination {combination_count}/{total_combinations}: "
                        f"{partition_mode} with {actual_n_parts} partitions and {regressor_type}"
                    )

                    # Train and evaluate models for this combination
                    result = evaluate_combination(
                        X_train,
                        y_train,
                        X_test,
                        y_test,
                        partition_mode,
                        n_parts,
                        regressor_type,
                        n_jobs,
                    )

                    if result is not None:
                        # Add result to the list
                        all_results.append(result)

                        # Update best result if this is better
                        if result["metrics"]["mae"] < best_mae:
                            best_mae = result["metrics"]["mae"]
                            best_result = result
                            logger.info(
                                f"New best combination: {partition_mode} with {actual_n_parts} partitions and {regressor_type} "
                                f"(MAE: {best_mae:.4f})"
                            )

            except Exception as e:
                logger.warning(
                    f"Error testing {partition_mode} with {n_parts} partitions: {str(e)}"
                )
                continue

    # Add global model results to all results
    all_results.extend(global_results)

    # Update best result if any global model is better
    for result in global_results:
        if result["metrics"]["mae"] < best_mae:
            best_mae = result["metrics"]["mae"]
            best_result = result
            logger.info(
                f"New best combination: Global {result['regressor_type']} "
                f"(MAE: {best_mae:.4f})"
            )

    total_time = time.time() - start_time
    logger.info(f"Tested {len(all_results)} combinations in {total_time:.2f} seconds")

    # Display and save results table
    results_df = create_results_dataframe(all_results)
    display_results_table(results_df)

    if output_dir:
        # Save results dataframe
        results_df.to_csv(os.path.join(output_dir, "partition_algorithm_results.csv"))

        # Generate visualizations
        generate_results_visualizations(results_df, best_result, output_dir)

        # Save best model with overwrite=True to avoid FileExistsError
        if best_result.get("models") is not None:
            save_model(
                {"models": best_result["models"]},
                os.path.join(output_dir, "best_partitioned_model.joblib"),
                metadata={
                    "partition_mode": str(best_result["partition_mode"]),
                    "n_partitions": best_result["n_partitions"],
                    "regressor_type": str(best_result["regressor_type"]),
                },
                overwrite=True,  # Add this parameter to avoid FileExistsError
            )

    return best_result


def test_global_models(X_train, y_train, X_test, y_test, regressor_types, n_jobs):
    """
    Test global models (no partitioning) for each regressor type.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        regressor_types: List of regressor types to test
        n_jobs: Number of parallel jobs

    Returns:
        List of results for global models
    """
    from fit_better import fit_all_regressors

    results = []

    for regressor_type in regressor_types:
        logger.info(f"Testing global {regressor_type} model...")

        # Train model
        model_results = fit_all_regressors(
            X_train, y_train, n_jobs=n_jobs, regressor_type=regressor_type
        )

        if not model_results:
            logger.warning(f"Failed to train global {regressor_type} model")
            continue

        # Get first (and only) model result
        model_dict = model_results[0]
        model = model_dict["model"]

        # Apply preprocessing if needed
        X_test_processed = X_test
        if "transformer" in model_dict and model_dict["transformer"] is not None:
            X_test_processed = model_dict["transformer"].transform(X_test)

        # Make predictions
        y_pred = model.predict(X_test_processed)

        # Calculate metrics
        metrics = calc_regression_statistics(y_test, y_pred)

        # Store results
        results.append(
            {
                "partition_mode": "GLOBAL",
                "n_partitions": 1,
                "regressor_type": regressor_type,
                "metrics": metrics,
                "model": model_dict,
            }
        )

        logger.info(
            f"Global {regressor_type}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, "
            f"R²={metrics['r2']:.4f}, Within 3%={metrics.get('pct_within_3pct', 0):.2f}%"
        )

    return results


def evaluate_combination(
    X_train, y_train, X_test, y_test, partition_mode, n_parts, regressor_type, n_jobs
):
    """
    Evaluate a specific combination of partition strategy and regressor type.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_mode: Partition mode to use
        n_parts: Number of partitions
        regressor_type: Regressor type to use
        n_jobs: Number of parallel jobs

    Returns:
        Dictionary with results for this combination
    """
    try:
        # Train models on partitions
        models = train_models_on_partitions(
            X_train,
            y_train,
            partition_mode=partition_mode,
            n_partitions=n_parts,
            regressor_type=regressor_type,
            n_jobs=n_jobs,
        )

        if models is None or len(models) == 0:
            logger.warning(
                f"No models were trained for {partition_mode} with {n_parts} partitions and {regressor_type}"
            )
            return None

        # Get actual number of partitions
        actual_n_parts = len(models)

        # Make predictions
        y_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

        # Calculate metrics
        metrics = calc_regression_statistics(y_test, y_pred)

        # Log results
        logger.info(
            f"{partition_mode} with {actual_n_parts} partitions, {regressor_type}: "
            f"MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}"
        )

        # Return results
        return {
            "partition_mode": partition_mode,
            "n_partitions": actual_n_parts,
            "regressor_type": regressor_type,
            "metrics": metrics,
            "models": models,
        }

    except Exception as e:
        logger.warning(
            f"Error evaluating {partition_mode} with {n_parts} partitions and {regressor_type}: {str(e)}"
        )
        return None


def create_results_dataframe(results):
    """
    Create a DataFrame from results for easier analysis and visualization.

    Args:
        results: List of result dictionaries

    Returns:
        Pandas DataFrame with results
    """
    # Extract data for DataFrame
    data = []

    for result in results:
        # Skip incomplete results
        if "metrics" not in result:
            continue

        row = {
            "partition_mode": str(result["partition_mode"]),
            "n_partitions": result["n_partitions"],
            "regressor_type": str(result["regressor_type"]),
            "mae": result["metrics"]["mae"],
            "rmse": result["metrics"]["rmse"],
            "r2": result["metrics"]["r2"],
            "pct_within_1pct": result["metrics"].get("pct_within_1pct", 0),
            "pct_within_3pct": result["metrics"].get("pct_within_3pct", 0),
            "pct_within_5pct": result["metrics"].get("pct_within_5pct", 0),
        }

        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Sort by MAE (best first)
    df = df.sort_values("mae")

    return df


def display_results_table(df):
    """
    Display a formatted table of results.

    Args:
        df: DataFrame with results
    """
    # Select columns to display
    display_df = df[
        ["partition_mode", "n_partitions", "regressor_type", "mae", "rmse", "r2"]
    ]

    # Display only top 10 results
    logger.info("\nTop 10 partition and algorithm combinations:")
    logger.info("\n" + display_df.head(10).to_string())

    # Display summary by partition mode
    logger.info("\nResults by partition mode (average MAE):")
    summary = df.groupby("partition_mode")["mae"].agg(["mean", "min", "count"])
    logger.info("\n" + summary.sort_values("min").to_string())

    # Display summary by regressor type
    logger.info("\nResults by regressor type (average MAE):")
    summary = df.groupby("regressor_type")["mae"].agg(["mean", "min", "count"])
    logger.info("\n" + summary.sort_values("min").to_string())


def generate_results_visualizations(df, best_result, output_dir):
    """
    Generate visualizations of the results.

    Args:
        df: Pandas DataFrame with results
        best_result: Dictionary with best result
        output_dir: Directory to save visualizations
    """
    # 1. Plot MAE by partition mode and regressor type
    plt.figure(figsize=(14, 10))

    # Pivot data for heatmap (using min MAE per combination)
    pivot_df = df.pivot_table(
        index="regressor_type", columns="partition_mode", values="mae", aggfunc="min"
    )

    # Plot heatmap
    im = plt.imshow(pivot_df, cmap="viridis")

    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label("MAE")

    # Add text annotations
    for i in range(pivot_df.shape[0]):
        for j in range(pivot_df.shape[1]):
            value = pivot_df.iloc[i, j]
            if not pd.isna(value):
                plt.text(
                    j,
                    i,
                    f"{value:.4f}",
                    ha="center",
                    va="center",
                    color="white" if value > pivot_df.values.mean() else "black",
                )

    # Set axis labels and title
    plt.xticks(range(pivot_df.shape[1]), pivot_df.columns)
    plt.yticks(range(pivot_df.shape[0]), pivot_df.index)
    plt.title("MAE by Partition Mode and Regressor Type")
    plt.tight_layout()

    # Save figure
    plt.savefig(os.path.join(output_dir, "mae_heatmap.png"))
    plt.close()

    # 2. Plot MAE by number of partitions
    plt.figure(figsize=(12, 8))

    # Group by partition count and get mean, min, max MAE
    partition_stats = (
        df.groupby("n_partitions")["mae"].agg(["mean", "min", "max"]).reset_index()
    )

    # Plot line for mean MAE
    plt.plot(
        partition_stats["n_partitions"],
        partition_stats["mean"],
        marker="o",
        label="Mean MAE",
    )

    # Add error bars for min/max
    plt.fill_between(
        partition_stats["n_partitions"],
        partition_stats["min"],
        partition_stats["max"],
        alpha=0.2,
        label="Min-Max Range",
    )

    # Highlight best number of partitions
    best_n_partitions = best_result["n_partitions"]
    best_partition_row = partition_stats[
        partition_stats["n_partitions"] == best_n_partitions
    ]
    if not best_partition_row.empty:
        best_mae = best_partition_row["min"].values[0]
        plt.scatter(
            [best_n_partitions],
            [best_mae],
            s=100,
            c="red",
            marker="*",
            label=f"Best ({best_n_partitions} partitions)",
        )

    plt.grid(True, alpha=0.3)
    plt.xlabel("Number of Partitions")
    plt.ylabel("MAE")
    plt.title("MAE by Number of Partitions")
    plt.legend()
    plt.tight_layout()

    # Save figure
    plt.savefig(os.path.join(output_dir, "mae_by_partition_count.png"))
    plt.close()

    # 3. Plot top 10 combinations
    top_10 = df.head(10)

    plt.figure(figsize=(14, 8))

    # Create labels for each combination
    labels = [
        f"{row['partition_mode']}\n{row['n_partitions']} parts\n{row['regressor_type']}"
        for _, row in top_10.iterrows()
    ]

    # Plot bars
    bar_width = 0.35
    x = np.arange(len(labels))

    plt.bar(x - bar_width / 2, top_10["mae"], bar_width, label="MAE")
    plt.bar(x + bar_width / 2, top_10["rmse"], bar_width, label="RMSE")

    # Add a secondary y-axis for R²
    ax2 = plt.twinx()
    ax2.plot(x, top_10["r2"], "go-", label="R²")
    ax2.set_ylabel("R²")

    # Set axis labels and title
    plt.xticks(x, labels, rotation=45, ha="right")
    plt.ylabel("Error Metrics")
    plt.title("Top 10 Partition and Algorithm Combinations")

    # Combine legends from both axes
    lines1, labels1 = plt.gca().get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save figure
    plt.savefig(os.path.join(output_dir, "top_10_combinations.png"))
    plt.close()


def find_best_partition_and_algo(
    X_train, y_train, X_test, y_test, n_jobs=1, output_dir=None
):
    """
    Simplified wrapper around find_best_partition_algorithm_combination.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results

    Returns:
        Best combination result
    """
    return find_best_partition_algorithm_combination(
        X_train, y_train, X_test, y_test, n_jobs, output_dir
    )


def load_dataset(dataset_prefix=None, data_dir=None):
    """
    Load dataset from the specified directory.

    Args:
        dataset_prefix: Prefix for the dataset files (e.g., 'linear', 'sine')
        data_dir: Directory containing dataset files

    Returns:
        X_train, y_train, X_test, y_test arrays
    """
    import numpy as np
    import os

    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "../data_gen/data")

    prefix = f"{dataset_prefix}_" if dataset_prefix else ""

    # Try to load from .npy files first
    X_train_path = os.path.join(data_dir, f"{prefix}X_train.npy")
    y_train_path = os.path.join(data_dir, f"{prefix}y_train.npy")
    X_test_path = os.path.join(data_dir, f"{prefix}X_test.npy")
    y_test_path = os.path.join(data_dir, f"{prefix}y_test.npy")

    try:
        X_train = np.load(X_train_path)
        y_train = np.load(y_train_path)
        X_test = np.load(X_test_path)
        y_test = np.load(y_test_path)
        logger.info(f"Successfully loaded dataset from {data_dir}")
    except (FileNotFoundError, IOError):
        # If .npy files don't exist, generate synthetic data
        logger.info(f"Data files not found, generating synthetic data")
        from fit_better import generate_train_test_data

        function_type = (
            dataset_prefix
            if dataset_prefix in ["linear", "sine", "polynomial", "complex"]
            else "complex"
        )

        # Directly use generate_train_test_data which returns 4 values
        X_train, y_train, X_test, y_test = generate_train_test_data(
            function_type=function_type,
            n_samples_train=800,
            n_samples_test=200,
            noise_std=0.5,
            random_state=42,
        )

        # Save generated data for future use
        os.makedirs(data_dir, exist_ok=True)
        np.save(X_train_path, X_train)
        np.save(y_train_path, y_train)
        np.save(X_test_path, X_test)
        np.save(y_test_path, y_test)
        logger.info(f"Generated and saved synthetic data to {data_dir}")

    # Ensure data is in the right shape
    if X_train.ndim == 1:
        X_train = X_train.reshape(-1, 1)
    if X_test.ndim == 1:
        X_test = X_test.reshape(-1, 1)

    return X_train, y_train, X_test, y_test


def evaluate_partition_mode(
    X_train,
    y_train,
    X_test,
    y_test,
    partition_mode,
    n_parts=3,
    n_jobs=1,
    regressor_type=None,
):
    """
    Evaluate a specific partition mode with the given dataset.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        partition_mode: The partition mode to evaluate
        n_parts: Number of partitions to use
        n_jobs: Number of parallel jobs
        regressor_type: Type of regressor to use (optional)

    Returns:
        metrics, partitioned_result tuple
    """
    from fit_better.utils.statistics import calc_regression_statistics
    from fit_better.core.partitioning import get_partition_boundaries
    from fit_better import train_models_on_partitions, predict_with_partitioned_models

    # Try to train models with the given partition mode
    try:
        # If regressor_type provided, pass it to the train function
        kwargs = {}
        if regressor_type is not None:
            kwargs["regressor_type"] = regressor_type

        models = train_models_on_partitions(
            X_train,
            y_train,
            partition_mode=partition_mode,
            n_partitions=n_parts,
            n_jobs=n_jobs,
            **kwargs,
        )

        if models is None:
            return None, None

        # Get boundary info
        boundaries = get_partition_boundaries(
            X_train, partition_mode, n_parts, min_size=10, n_jobs=n_jobs
        )

        # Make predictions
        y_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

        # Calculate metrics
        metrics = calc_regression_statistics(y_test, y_pred)

        # Return metrics and partitioned result
        return metrics, {"models": models, "boundaries": boundaries}

    except Exception as e:
        logger.warning(f"Error evaluating partition mode {partition_mode}: {str(e)}")
        return None, None


def _test_regressor_types(X_train, y_train, X_test, y_test, regressor_types, n_jobs=1):
    """
    Test multiple regressor types on a dataset.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        regressor_types: List of regressor types to test
        n_jobs: Number of parallel jobs

    Returns:
        Dictionary with results for each regressor type
    """
    from fit_better import fit_all_regressors
    from fit_better.utils.statistics import calc_regression_statistics

    results = {}

    for regressor_type in regressor_types:
        try:
            logger.info(f"Testing regressor type: {regressor_type}")

            # Fit the regressor using fit_all_regressors with specific regressor_type
            model_results = fit_all_regressors(
                X_train, y_train, regressor_type=regressor_type, n_jobs=n_jobs
            )

            if not model_results or len(model_results) == 0:
                logger.warning(f"Failed to fit regressor {regressor_type}")
                continue

            # Get the first (and only) model dict
            model_dict = model_results[0]

            # Extract model and any data transformers
            model = model_dict["model"]
            scaler = model_dict.get("scaler")
            transformer = model_dict.get("transformer")

            # Apply any preprocessing
            X_test_processed = X_test.copy()
            if transformer:
                X_test_processed = transformer.transform(X_test_processed)
            if scaler:
                X_test_processed = scaler.transform(X_test_processed)

            # Make predictions
            y_pred = model.predict(X_test_processed)

            # Calculate metrics
            metrics = calc_regression_statistics(y_test, y_pred)

            # Store results
            results[regressor_type] = {"metrics": metrics, "model": model_dict}

        except Exception as e:
            logger.warning(f"Error testing regressor {regressor_type}: {str(e)}")
            continue

    return results


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Find the best partition strategy and regression algorithm combination"
    )

    parser.add_argument(
        "--n-samples", type=int, default=2000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--noise-level", type=float, default=0.7, help="Standard deviation of noise"
    )
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")
    parser.add_argument(
        "--function-type",
        type=str,
        default="complex",
        choices=["linear", "sine", "polynomial", "complex"],
        help="Type of function for synthetic data",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode with fewer combinations for faster testing",
    )

    # Output directory - default to a subdirectory in tests/data_gen
    tests_dir = Path(__file__).resolve().parent.parent
    default_output_dir = str(tests_dir / "data_gen" / "partition_finder_results")

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help="Directory to save results",
    )

    args = parser.parse_args()

    # Generate synthetic data
    logger.info(
        f"Generating {args.function_type} data with {args.n_samples} samples..."
    )

    try:
        # Get training data
        X_train, y_train, X_test, y_test = load_dataset(args.function_type)

        logger.info(
            f"Data shapes: X_train {X_train.shape}, y_train {y_train.shape}, X_test {X_test.shape}, y_test {y_test.shape}"
        )

        # Find best combination
        logger.info(
            "Finding best partition strategy and regression algorithm combination..."
        )

        # If running in test mode, reduce the sample size and limit regressor types
        if args.test_mode or args.n_samples <= 500:
            logger.info(
                "Running in test mode with limited regressor types for faster testing"
            )
            # Limit regressor types to just 3 for test_all.py - use actual enum values
            regressor_types = [
                RegressorType.LINEAR,
                RegressorType.RIDGE,
                RegressorType.RANDOM_FOREST,
            ]
            # Limit partition modes to just 2
            partition_modes = [PartitionMode.RANGE, PartitionMode.KMEANS]
            # Limit number of partitions
            n_parts = [2, 5]
            best_result = find_best_partition_algorithm_combination(
                X_train,
                y_train,
                X_test,
                y_test,
                n_jobs=args.n_jobs,
                output_dir=args.output_dir,
                regressor_types=regressor_types,
                partition_modes=partition_modes,
                partition_counts=n_parts,
            )
        else:
            best_result = find_best_partition_algorithm_combination(
                X_train,
                y_train,
                X_test,
                y_test,
                n_jobs=args.n_jobs,
                output_dir=args.output_dir,
            )

        # Print final result
        if best_result["partition_mode"] == "GLOBAL":
            logger.info(
                f"\nBest approach: Global {best_result['regressor_type']} model"
                f" (MAE: {best_result['metrics']['mae']:.4f})"
            )
        else:
            logger.info(
                f"\nBest approach: {best_result['partition_mode']} with {best_result['n_partitions']} partitions"
                f" using {best_result['regressor_type']} (MAE: {best_result['metrics']['mae']:.4f})"
            )

        logger.info(f"Results and visualizations saved to {args.output_dir}")

        # Write validation log file for test_all.py
        tests_dir = Path(__file__).resolve().parent.parent
        logs_dir = tests_dir / "data_gen" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        validation_log = logs_dir / "partition_results.log"

        with open(validation_log, "w") as f:
            f.write(f"SUCCESS: Best partition and algorithm found\n")
            f.write(
                f"Best approach: {best_result['partition_mode']} with {best_result['n_partitions']} partitions "
            )
            f.write(
                f"using {best_result['regressor_type']} (MAE: {best_result['metrics']['mae']:.4f})\n"
            )

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
