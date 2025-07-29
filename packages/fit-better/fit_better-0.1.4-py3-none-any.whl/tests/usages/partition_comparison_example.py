#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Example script comparing different data partition strategies for regression.

Usage:
    python partition_comparison_example.py [options]

This script demonstrates how different partitioning strategies affect regression performance.
It compares various partition modes (equal width, percentile, KMeans, KMedoids) on synthetic
datasets to visualize and quantify partition effectiveness.

Options:
    --n-samples N       Number of samples to generate (default: 1000)
    --noise-level N     Standard deviation of noise to add (default: 0.5)
    --n-parts N         Number of partitions to use (default: 5)
    --n-jobs N          Number of parallel jobs (default: 1)
    --output-dir DIR    Directory to save visualization results (default: partition_comparison_results)
    --function-type STR Type of function for synthetic data: linear, sine, polynomial, complex (default: sine)
    --no-visualize      Disable visualization generation
"""
import os
import sys
import time
import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import from fit_better
from fit_better import (
    PartitionMode,
    train_models_on_partitions,
    predict_with_partitioned_models,
    generate_train_test_data,
)
from fit_better.utils.statistics import calc_regression_statistics
from fit_better.core.partitioning import get_partition_boundaries, get_partition_masks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def compare_partition_strategies(
    X, y, X_test, y_test, n_parts=5, n_jobs=1, output_dir=None, visualize=True
):
    """
    Compare different partition strategies on the same dataset.

    Args:
        X: Training features
        y: Training targets
        X_test: Test features
        y_test: Test targets
        n_parts: Number of partitions to use
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        visualize: Whether to generate visualizations

    Returns:
        Dictionary with performance metrics for each strategy
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Ensure X is 2D
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    if X_test.ndim == 1:
        X_test = X_test.reshape(-1, 1)

    # Partition modes to compare
    partition_modes = [
        PartitionMode.RANGE,
        PartitionMode.PERCENTILE,
        PartitionMode.KMEANS,
    ]

    # Try to add KMedoids if available
    try:
        from sklearn_extra.cluster import KMedoids

        partition_modes.append(PartitionMode.KMEDOIDS)
        has_kmedoids = True
    except ImportError:
        logger.warning(
            "sklearn_extra not installed. KMedoids partitioning will be skipped."
        )
        has_kmedoids = False

    results = {}
    boundaries_by_mode = {}

    # Train models for each partition mode
    for mode in partition_modes:
        logger.info(f"Training with partition mode: {mode}")
        start_time = time.time()

        # Get boundaries for visualization
        boundaries = get_partition_boundaries(
            X, mode, n_parts, min_size=10, n_jobs=n_jobs
        )
        boundaries_by_mode[mode] = boundaries

        # Train models on partitions
        models = train_models_on_partitions(
            X, y, partition_mode=mode, n_parts=n_parts, n_jobs=n_jobs
        )

        if models is None:
            logger.warning(f"Failed to train models with partition mode {mode}")
            continue

        # Make predictions
        y_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

        # Calculate metrics
        metrics = calc_regression_statistics(y_test, y_pred)
        metrics["execution_time"] = time.time() - start_time
        metrics["n_partitions"] = len(boundaries) + 1

        # Store results
        results[mode] = {"metrics": metrics, "models": models, "boundaries": boundaries}

        # Log results
        logger.info(
            f"{mode}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, "
            f"R²={metrics['r2']:.4f}, Time={metrics['execution_time']:.2f}s"
        )

    # Generate visualizations if requested
    if visualize and output_dir:
        plot_partition_boundaries(X, boundaries_by_mode, output_dir)
        plot_performance_comparison(results, output_dir)
        plot_predictions(X_test, y_test, results, output_dir)

    return results


def plot_partition_boundaries(X, boundaries_by_mode, output_dir):
    """
    Plot data distribution with partition boundaries for each mode.

    Args:
        X: Input features
        boundaries_by_mode: Dictionary mapping partition modes to boundary lists
        output_dir: Directory to save the plots
    """
    fig, axes = plt.subplots(
        len(boundaries_by_mode), 1, figsize=(10, 3 * len(boundaries_by_mode))
    )
    if len(boundaries_by_mode) == 1:
        axes = [axes]

    X_flat = X.flatten()

    for i, (mode, boundaries) in enumerate(boundaries_by_mode.items()):
        ax = axes[i]

        # Plot data distribution
        ax.hist(X_flat, bins=50, alpha=0.5, color="blue")

        # Plot partition boundaries
        for b in boundaries:
            ax.axvline(x=b, color="red", linestyle="--", linewidth=1)

        ax.set_title(f"Partition Boundaries: {mode}")
        ax.set_xlabel("X")
        ax.set_ylabel("Frequency")

        # Add partition counts as text
        for j, (left, right) in enumerate(
            zip([-np.inf] + list(boundaries), list(boundaries) + [np.inf])
        ):
            mask = (
                (X_flat > left) & (X_flat <= right)
                if not np.isneginf(left)
                else X_flat <= right
            )
            count = np.sum(mask)

            # Calculate x-position for the text (middle of partition)
            if np.isneginf(left) and not np.isposinf(right):
                x_pos = right - 0.1 * (X_flat.max() - X_flat.min())
            elif np.isposinf(right) and not np.isneginf(left):
                x_pos = left + 0.1 * (X_flat.max() - X_flat.min())
            elif np.isneginf(left) and np.isposinf(right):
                x_pos = np.median(X_flat)
            else:
                x_pos = (left + right) / 2

            # Add count as text
            y_pos = ax.get_ylim()[1] * 0.8
            ax.text(
                x_pos,
                y_pos,
                f"n={count}",
                ha="center",
                va="center",
                bbox=dict(facecolor="white", alpha=0.7),
            )

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "partition_boundaries.png"))
    plt.close()


def plot_performance_comparison(results, output_dir):
    """
    Plot performance comparison between different partition strategies.

    Args:
        results: Dictionary with results for each partition mode
        output_dir: Directory to save the plots
    """
    # Extract metrics
    modes = list(results.keys())
    metrics = ["mae", "rmse", "r2", "pct_within_3pct", "execution_time"]
    metric_labels = ["MAE", "RMSE", "R²", "Within 3%", "Time (s)"]

    # Create figure with subplots for each metric
    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 3 * len(metrics)))

    # Convert partition modes to strings for plotting
    mode_labels = [str(mode) for mode in modes]

    # Plot each metric
    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        values = [results[mode]["metrics"].get(metric, 0) for mode in modes]

        # For R², higher is better, so invert the bar chart
        if metric == "r2":
            values = [
                max(v, 0) for v in values
            ]  # Ensure non-negative for visualization

        axes[i].bar(mode_labels, values)
        axes[i].set_title(f"{label} Comparison")
        axes[i].set_ylabel(label)

        # Add value labels on top of the bars
        for j, v in enumerate(values):
            axes[i].text(j, v, f"{v:.4f}", ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "performance_comparison.png"))
    plt.close()


def plot_predictions(X_test, y_test, results, output_dir):
    """
    Plot predictions from each partition strategy against ground truth.

    Args:
        X_test: Test features
        y_test: Test targets
        results: Dictionary with results for each partition mode
        output_dir: Directory to save the plots
    """
    X_flat = X_test.flatten()

    # Get sorted indices for plotting
    sort_idx = np.argsort(X_flat)
    X_sorted = X_flat[sort_idx]
    y_sorted = y_test[sort_idx]

    plt.figure(figsize=(12, 8))

    # Plot ground truth
    plt.scatter(
        X_sorted, y_sorted, s=10, alpha=0.5, label="Ground Truth", color="black"
    )

    # Plot predictions for each mode
    colors = ["red", "blue", "green", "purple", "orange"]
    for i, (mode, data) in enumerate(results.items()):
        # Get models and make predictions
        models = data["models"]
        y_pred = predict_with_partitioned_models(models, X_test)
        y_pred_sorted = y_pred[sort_idx]

        # Plot predictions
        plt.plot(
            X_sorted,
            y_pred_sorted,
            label=f"{mode} (MAE={data['metrics']['mae']:.4f})",
            color=colors[i % len(colors)],
        )

    plt.title("Predictions Comparison")
    plt.xlabel("X")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "predictions_comparison.png"))
    plt.close()


def evaluate_partition_mode(
    X_train, y_train, X_test, y_test, partition_mode, n_parts=3, n_jobs=1
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

    Returns:
        An object with metrics and model information
    """
    from types import SimpleNamespace
    import numpy as np

    # Try to train models with the given partition mode
    models = train_models_on_partitions(
        X_train,
        y_train,
        partition_mode=partition_mode,
        n_parts=n_parts,
        n_jobs=n_jobs,
    )

    if models is None:
        return SimpleNamespace(
            best_rmse=np.inf,
            best_r2=-np.inf,
            best_mae=np.inf,
            best_model=None,
            boundaries=[],
        )

    # Get boundary info
    boundaries = get_partition_boundaries(
        X_train, partition_mode, n_parts, min_size=10, n_jobs=n_jobs
    )

    # Make predictions
    y_pred = predict_with_partitioned_models(models, X_test, n_jobs=n_jobs)

    # Calculate metrics
    metrics = calc_regression_statistics(y_test, y_pred)

    # Return result as an object
    return SimpleNamespace(
        best_rmse=metrics["rmse"],
        best_r2=metrics["r2"],
        best_mae=metrics["mae"],
        best_model=models,
        boundaries=boundaries,
    )


def load_test_data(data_dir):
    """
    Load test data from a directory.

    Args:
        data_dir: Directory containing test data files

    Returns:
        X_train, y_train, X_test, y_test arrays
    """
    import numpy as np
    import os

    # Try to load from .npy files first
    X_train_path = os.path.join(data_dir, "X_train.npy")
    y_train_path = os.path.join(data_dir, "y_train.npy")
    X_test_path = os.path.join(data_dir, "X_test.npy")
    y_test_path = os.path.join(data_dir, "y_test.npy")

    try:
        X_train = np.load(X_train_path)
        y_train = np.load(y_train_path)
        X_test = np.load(X_test_path)
        y_test = np.load(y_test_path)
    except (FileNotFoundError, IOError):
        # If .npy files don't exist, generate synthetic data
        from fit_better.data.synthetic import generate_synthetic_data_by_function

        X, y = generate_synthetic_data_by_function(
            n_samples=200, function_type="complex", random_state=42
        )

        # Split into train/test
        train_size = int(0.8 * len(X))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Save generated data for future use
        os.makedirs(data_dir, exist_ok=True)
        np.save(X_train_path, X_train)
        np.save(y_train_path, y_train)
        np.save(X_test_path, X_test)
        np.save(y_test_path, y_test)

    # Ensure data is in the right shape
    if X_train.ndim == 1:
        X_train = X_train.reshape(-1, 1)
    if X_test.ndim == 1:
        X_test = X_test.reshape(-1, 1)

    return X_train, y_train, X_test, y_test


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Compare partition strategies for regression"
    )

    parser.add_argument(
        "--n-samples", type=int, default=1000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--noise-level", type=float, default=0.5, help="Standard deviation of noise"
    )
    parser.add_argument("--n-parts", type=int, default=5, help="Number of partitions")
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")
    parser.add_argument(
        "--function-type",
        type=str,
        default="sine",
        choices=["linear", "sine", "polynomial", "complex"],
        help="Type of function for synthetic data",
    )

    # Output directory - default to a subdirectory in tests/data_gen
    tests_dir = Path(__file__).resolve().parent.parent
    default_output_dir = str(tests_dir / "data_gen" / "partition_comparison_results")

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help="Directory to save results",
    )

    parser.add_argument(
        "--no-visualize", action="store_true", help="Disable visualization generation"
    )

    args = parser.parse_args()

    # Generate synthetic data
    logger.info(
        f"Generating {args.function_type} data with {args.n_samples} samples..."
    )
    X_train, y_train, X_test, y_test = generate_train_test_data(
        function_type=args.function_type,
        n_samples_train=int(args.n_samples * 0.8),  # Use 80% for training
        n_samples_test=int(args.n_samples * 0.2),  # Use 20% for testing
        noise_std=args.noise_level,
        random_state=42,
    )

    # Compare partition strategies
    logger.info(f"Comparing partition strategies with {args.n_parts} partitions...")
    results = compare_partition_strategies(
        X_train,
        y_train,
        X_test,
        y_test,
        n_parts=args.n_parts,
        n_jobs=args.n_jobs,
        output_dir=args.output_dir,
        visualize=not args.no_visualize,
    )

    # Print summary
    logger.info("\nPerformance Summary:")
    for mode, data in results.items():
        metrics = data["metrics"]
        logger.info(
            f"{mode}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, "
            f"R²={metrics['r2']:.4f}, Within 3%={metrics.get('pct_within_3pct', 0):.2f}%"
        )

    best_mode = min(results.items(), key=lambda x: x[1]["metrics"]["mae"])[0]
    logger.info(f"\nBest partition strategy by MAE: {best_mode}")

    if not args.no_visualize:
        logger.info(f"Visualizations saved to {args.output_dir}")


if __name__ == "__main__":
    main()
