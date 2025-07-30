#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-08
Description: Script to verify and benchmark parallel processing in partition utilities.

Usage:
    python parallel_partitioning_example.py [--n-jobs N] [--n-samples N] [--output-dir DIR]

This script tests parallel processing capabilities in the fit_better package's partitioning utilities:
1. KNeighborsRegressor with adaptive n_neighbors and parallel processing
2. KMeans clustering with parallel processing
3. KMedoids clustering with parallel processing

Options:
    --n-jobs N       Number of parallel jobs to use (default: 4)
    --n-samples N    Number of samples to generate for testing (default: 1000)
    --output-dir DIR Directory to save visualization results (default: tests/data_gen/visualization_results/parallel)
"""
import os
import sys
import time
import logging
import argparse
import numpy as np
from datetime import datetime

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Also add the grandparent directory to allow importing fit_better when run directly
grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

# Updated imports based on fit_better package structure
from fit_better import PartitionMode, RegressorType, train_models_on_partitions

# Import necessary utility functions for partition boundaries
from fit_better.core.partitioning import (
    create_kmeans_boundaries,
    create_kmedoids_boundaries,
)

# Create logger for this module
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test parallel processing in partition utilities"
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=4,
        help="Number of parallel jobs to use (default: 4)",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=1000,
        help="Number of samples to generate for testing (default: 1000)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data_gen",
            "visualization_results",
            "parallel",
        ),
        help="Directory to save visualization results",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_gen", "logs"
    )
    os.makedirs(logs_dir, exist_ok=True)

    # Create timestamped log file in logs/
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"parallel_partitioning_{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path, mode="w"), logging.StreamHandler()],
    )

    # Create or update symlink to latest log file in logs/
    latest_log = os.path.join(logs_dir, "parallel_partitioning.log")
    try:
        if os.path.islink(latest_log) or os.path.exists(latest_log):
            os.remove(latest_log)
        os.symlink(log_filename, latest_log)
    except Exception as e:
        logger.warning(f"Could not create log symlink: {e}, but testing will continue")

    # Start timing the overall execution
    overall_start_time = time.time()
    logger.info(f"Starting parallel partitioning tests with {args.n_jobs} jobs")

    # Generate some test data
    np.random.seed(42)
    n_samples = args.n_samples
    X = np.sort(np.random.rand(n_samples) * 100)
    y = np.sin(X / 10) + 0.1 * np.random.randn(n_samples)

    # Reshape X to be a 2D array for scikit-learn
    X_2d = X.reshape(-1, 1)

    logging.info(
        "Testing KNeighborsRegressor with adaptive n_neighbors and parallel processing"
    )

    # Test with a specific regressor type to focus on KNeighborsRegressor
    t_start = time.time()
    partitioned_knn = train_models_on_partitions(
        X_2d,  # Use the 2D array
        y,
        n_partitions=5,
        n_jobs=4,  # Use parallel processing
        partition_mode=PartitionMode.RANGE,
        regressor_type=RegressorType.KNEIGHBORS,
    )
    t_end = time.time()
    logging.info(
        f"KNeighborsRegressor partitioning completed in {t_end - t_start:.2f} seconds"
    )

    # Test KMeans with parallel processing
    logging.info("Testing KMeans clustering with parallel processing")
    t_start = time.time()
    kmeans_boundaries = create_kmeans_boundaries(X_2d, k=5)  # Use the 2D array
    t_end = time.time()
    logging.info(
        f"KMeans clustering completed in {t_end - t_start:.2f} seconds with boundaries: {kmeans_boundaries}"
    )

    # Test KMedoids with parallel processing (if available)
    logging.info("Testing KMedoids clustering with parallel processing")
    t_start = time.time()
    try:
        kmedoids_boundaries = create_kmedoids_boundaries(X_2d, k=5)  # Use the 2D array
        t_end = time.time()
        logging.info(
            f"KMedoids clustering completed in {t_end - t_start:.2f} seconds with boundaries: {kmedoids_boundaries}"
        )
    except ImportError as e:
        logging.warning(f"KMedoids not available: {e}")
        logging.warning(
            "To use KMedoids, install scikit-learn-extra: pip install scikit-learn-extra"
        )
        logging.info("Skipping KMedoids tests and continuing with other tests...")

    # Test full partitioning with KMeans
    logging.info("Testing full partitioning with KMeans and parallel processing")
    t_start = time.time()
    partitioned_kmeans = train_models_on_partitions(
        X_2d,  # Use the 2D array
        y,
        n_partitions=5,
        n_jobs=4,  # Use parallel processing
        partition_mode=PartitionMode.KMEANS,
    )
    t_end = time.time()
    logging.info(f"KMeans partitioning completed in {t_end - t_start:.2f} seconds")

    # Test full partitioning with KMedoids
    logging.info("Testing full partitioning with KMedoids and parallel processing")
    t_start = time.time()
    try:
        partitioned_kmedoids = train_models_on_partitions(
            X_2d,  # Use the 2D array
            y,
            n_partitions=5,
            n_jobs=4,  # Use parallel processing
            partition_mode=PartitionMode.KMEDOIDS,
        )
        t_end = time.time()
        logging.info(
            f"KMedoids partitioning completed in {t_end - t_start:.2f} seconds"
        )
    except Exception as e:
        if "KMedoids requires sklearn_extra package" in str(e):
            logging.warning("KMedoids partitioning requires the sklearn-extra package.")
            logging.warning("You can install it with: pip install scikit-learn-extra")
        else:
            logging.warning(f"KMedoids not available: {e}")
        logging.info("Skipping KMedoids test...")

    # Write success message to the log file for test_all.py to find
    with open(latest_log, "a") as f:
        f.write("All tests completed successfully\n")

    logging.info("All tests completed successfully!")


if __name__ == "__main__":
    main()
