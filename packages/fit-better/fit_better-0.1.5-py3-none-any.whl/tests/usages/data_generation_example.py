#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Generate test data for regression model evaluation.

Usage:
    python data_generation_example.py [options]

This script generates synthetic test data for evaluating different regression
strategies and partitioning approaches. It creates both training and test datasets
with configurable function types and noise levels.

Options:
    --function-type TYPE   Type of function to generate: linear, sine, polynomial, complex (default: linear)
    --n-samples N          Number of samples to generate (default: 1000)
    --noise-level N        Level of noise to add to the data (default: 0.5)
    --test-size RATIO      Proportion of data to use for testing (default: 0.2)
    --random-state N       Random seed for reproducibility (default: 42)
    --output-dir DIR       Directory to save the generated data (default: tests/data_gen/data)
"""
import os
import sys
import logging
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import data generation functions from fit_better
from fit_better import generate_synthetic_data, generate_train_test_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_synthetic_data_by_function(
    function_type: str = "linear",
    n_samples: int = 1000,
    noise_level: float = 0.5,
    test_size: float = 0.2,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate test data with the specified function type."""
    if random_state is not None:
        np.random.seed(random_state)

    # Generate X values
    X = np.linspace(0, 10, n_samples).reshape(-1, 1)

    # Generate y values based on the function type
    if function_type == "linear":
        slope = 2.0
        intercept = 1.0
        y = slope * X.flatten() + intercept + noise_level * np.random.randn(n_samples)
    elif function_type == "sine":
        y = np.sin(X.flatten()) + noise_level * np.random.randn(n_samples)
    elif function_type == "polynomial":
        y = (
            0.1 * X.flatten() ** 3
            - 0.5 * X.flatten() ** 2
            + X.flatten()
            + noise_level * np.random.randn(n_samples)
        )
    elif function_type == "complex":
        y = np.sin(X.flatten()) * np.exp(
            -0.1 * X.flatten()
        ) + noise_level * np.random.randn(n_samples)
    else:
        raise ValueError(f"Unknown function type: {function_type}")

    # Split into train and test sets
    split_idx = int(n_samples * (1 - test_size))
    X_train = X[:split_idx]
    y_train = y[:split_idx]
    X_test = X[split_idx:]
    y_test = y[split_idx:]

    return X_train, y_train, X_test, y_test


def save_data(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    output_dir: str,
    function_type: str = "linear",
) -> None:
    """Save the generated data to files."""
    from fit_better.data.csv_manager import CSVMgr

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Format data with IDs for consistent output
    X_train_with_id = np.column_stack(
        (np.arange(1, len(X_train) + 1), X_train.flatten())
    )
    y_train_with_id = np.column_stack(
        (np.arange(1, len(y_train) + 1), y_train.flatten())
    )
    X_test_with_id = np.column_stack((np.arange(1, len(X_test) + 1), X_test.flatten()))
    y_test_with_id = np.column_stack((np.arange(1, len(y_test) + 1), y_test.flatten()))

    # Create headers
    headers = ["id", "value"]

    # Use CSVMgr to save the data
    # Save training data
    CSVMgr.from_array(
        array=X_train_with_id, header=headers, has_header=True, delimiter=" "
    ).export_array_csv(
        filepath=str(output_dir / f"{function_type}_X.txt"),
        include_header=True,
        delimiter=" ",
        header_prefix="# ",  # Add comment character before header
    )

    CSVMgr.from_array(
        array=y_train_with_id, header=headers, has_header=True, delimiter=" "
    ).export_array_csv(
        filepath=str(output_dir / f"{function_type}_y.txt"),
        include_header=True,
        delimiter=" ",
        header_prefix="# ",  # Add comment character before header
    )

    # Save test data
    CSVMgr.from_array(
        array=X_test_with_id, header=headers, has_header=True, delimiter=" "
    ).export_array_csv(
        filepath=str(output_dir / f"{function_type}_X_test.txt"),
        include_header=True,
        delimiter=" ",
        header_prefix="# ",  # Add comment character before header
    )

    CSVMgr.from_array(
        array=y_test_with_id, header=headers, has_header=True, delimiter=" "
    ).export_array_csv(
        filepath=str(output_dir / f"{function_type}_y_test.txt"),
        include_header=True,
        delimiter=" ",
        header_prefix="# ",  # Add comment character before header
    )

    logger.info(f"Data saved to {output_dir}")
    logger.info(f"Training data shape: X={X_train.shape}, y={y_train.shape}")
    logger.info(f"Test data shape: X={X_test.shape}, y={y_test.shape}")


def main():
    """Main function to generate test data."""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate test data for regression evaluation"
    )
    parser.add_argument(
        "--n-samples", type=int, default=1000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--noise-level", type=float, default=0.5, help="Level of noise to add"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of data to use for testing",
    )
    parser.add_argument(
        "--random-state", type=int, default=42, help="Random seed for reproducibility"
    )

    # Always ensure the output directory is in tests/data_gen/data regardless of execution directory
    tests_dir = Path(__file__).resolve().parent.parent
    default_output_dir = str(tests_dir / "data_gen" / "data")

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help=f"Directory to save the data (default: {default_output_dir})",
    )

    parser.add_argument(
        "--function-type",
        type=str,
        default="linear",
        choices=["linear", "sine", "polynomial", "complex"],
        help="Type of function to generate data for",
    )
    args = parser.parse_args()

    # Ensure the output directory is absolute and exists
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate data
    logger.info(f"Generating {args.function_type} test data...")
    X_train, y_train, X_test, y_test = generate_synthetic_data_by_function(
        function_type=args.function_type,
        n_samples=args.n_samples,
        noise_level=args.noise_level,
        test_size=args.test_size,
        random_state=args.random_state,
    )

    # Save data
    save_data(X_train, y_train, X_test, y_test, output_dir, args.function_type)


if __name__ == "__main__":
    main()
