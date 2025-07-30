"""
Author: xlindo
Create Time: 2025-05-10
Description: Generate synthetic data for testing regression models.

Usage:
    # As a module
    from fit_better.data.synthetic import generate_synthetic_data
    X, y = generate_synthetic_data(X_path, y_path, model_type="sine")

    # As a command-line tool
    python -m fit_better.data.synthetic --model sine --n-samples 10000 --output-dir ./data

This module provides utilities for generating synthetic data with various
relationships to test regression algorithms. Supports multiple model types
including linear, sine, and polynomial relationships.

Synthetic Data Generation for Regression Testing
==============================================

This module provides comprehensive utilities for generating synthetic datasets
with various underlying relationships (linear, polynomial, sine waves, etc.),\nnoise characteristics, and complexities. Such datasets are crucial for:\n
*   Testing the correctness and robustness of regression algorithms.\n*   Evaluating the performance of data partitioning strategies.\n*   Understanding model behavior under controlled conditions.\n*   Benchmarking different model configurations.\n\nKey Features:\n-------------\n\n*   **Multiple Model Types**: Generate data based on predefined functional forms:\n    *   `linear`: \(y = ax + b + \epsilon\)
    *   `sine`: \(y = A \sin(2\pi fx + \phi) + \epsilon\)
    *   `polynomial`: \(y = c_0 + c_1 x + c_2 x^2 + ... + c_k x^k + \epsilon\)
    *   Custom functions can also be used via `generate_synthetic_data_by_function`.
*   **Noise Control**: Add Gaussian noise with configurable standard deviation (`noise_std`).\n    Supports heteroscedastic noise (noise level dependent on X values or segments).\n*   **Complexity Injection**: Options to add non-linear components, multiple sine waves,\n    or oscillatory patterns to basic functional forms, making the data harder to fit\n    and better reflecting real-world scenarios (`add_complexity` parameter).\n*   **Outlier Generation**: Introduce a percentage of outliers to the target variable `y`\n    and/or feature `X` to test model robustness and partitioning effectiveness under\n    such conditions (`add_outliers` parameter).\n*   **Data Splitting**: Functions to generate separate training and test sets, potentially\n    with slightly different generating parameters or noise characteristics to simulate\n    distribution shift (`generate_train_test_data`).\n*   **Reproducibility**: Use of random seeds (`seed` or `random_state`) ensures that data\n    generation is reproducible.\n*   **File Output**: Generated data (features X, target y, and sample IDs) can be saved\n    to text files (e.g., CSV-like format) for later use or sharing.\n*   **Command-Line Interface**: Can be run as a script to generate data directly from the\n    command line, specifying model type, number of samples, output directory, etc.\n
Core Functions:\n---------------

*   `generate_synthetic_data(...)`: Generates X and y values based on a specified `model_type`\n    (linear, sine, polynomial), noise level, and complexity options, then saves them to files.\n*   `generate_train_test_data(...)`: A wrapper that calls `generate_synthetic_data` twice\n    to create training and testing datasets, typically with slightly varied parameters for the test set.\n*   `generate_synthetic_data_by_function(...)`: A flexible function that generates data based on a user-provided\n    Python function `f(X)`. This allows for creating datasets with arbitrary custom relationships.\n    It supports multi-dimensional features (`n_features`).\n*   `save_data(...)`: Utility to save generated (or any) X/y train/test splits to files in specified formats.\n
Example (Module Usage):\n------------------------\n```python
from fit_better.data.synthetic import generate_synthetic_data_by_function, save_data
import numpy as np

# Define a custom function for data generation
def custom_func(X):
    return 2 * np.cos(X[:, 0]) + 0.5 * X[:, 1]**2 if X.shape[1] > 1 else 2 * np.cos(X[:, 0])

# Generate 2D feature data
X_train, y_train, X_test, y_test = generate_synthetic_data_by_function(
    function=custom_func,
    n_samples_train=1000,
    n_samples_test=200,
    n_features=2,
    noise_std=0.2,
    random_state=42
)

print(f"Generated training X shape: {X_train.shape}, y shape: {y_train.shape}")
# save_data(X_train, y_train, X_test, y_test, output_dir='./synthetic_data')
```

Example (Command-Line):\n-----------------------\n```bash
python -m fit_better.data.synthetic --model_type sine --n_samples 1000 --output_dir ./my_sine_data --noise_std 0.1
```

This module is essential for robustly testing and validating the components of the `fit_better` package.
"""

import os
import sys
import numpy as np
import logging
from typing import Tuple, Literal, Dict, Any, Optional
import argparse
from datetime import datetime

# Import the new logging utilities
from ..utils.logging_utils import get_logger

# Create module-level logger
logger = get_logger(__name__)

# Define model types and their default parameters
ModelType = Literal["linear", "sine", "polynomial"]

# Default parameters for each model type
DEFAULT_MODEL_PARAMS: Dict[str, Dict[str, Any]] = {
    "linear": {"a": 2.0, "b": 1.0},
    "sine": {"amplitude": 2.0, "frequency": 2.0, "phase": 0.3},
    "polynomial": {"coefficients": [0.5, -1.5, 0.8, -0.2]},  # x^3 - 0.2x^2 + 0.8x + 0.5
}

# Default test data parameters (slightly modified from training)
DEFAULT_TEST_MODEL_PARAMS: Dict[str, Dict[str, Any]] = {
    "linear": {"a": 2.2, "b": 0.8},  # Slightly different slope and intercept
    "sine": {"amplitude": 2.2, "frequency": 1.9, "phase": 0.4},  # Modified parameters
    "polynomial": {
        "coefficients": [0.6, -1.4, 0.7, -0.25]
    },  # Similar but different coefficients
}


def _write_data_file(
    filepath: str, ids: np.ndarray, values: np.ndarray, header: bool = True
) -> None:
    """
    Write data to a file in the standard format.
    Args:
        filepath: Path to save the data
        ids: Array of sample IDs
        values: Array of values to write
        header: Whether to include header in output file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        if header:
            f.write("# id value\n")
        for i, val in zip(ids, values):
            f.write(f"{i} {val:.6f}\n")


def generate_synthetic_data(
    X_path: str,
    y_path: str,
    n: int = 10000,
    model_type: ModelType = "linear",
    params: Optional[dict] = None,
    noise_std: float = 1.0,  # Increased default noise
    seed: int = 42,
    header: bool = True,
    add_complexity: bool = True,  # New parameter to add complexity to data
    add_outliers: bool = True,  # New parameter to add outliers
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic data for regression testing and save to files.
    Args:
        X_path: Path to save X values
        y_path: Path to save y values
        n: Number of samples to generate (default: 10000)
        model_type: Type of model to generate data for ("linear", "sine", "polynomial")
        params: Model-specific parameters:
            - linear: {"a": slope, "b": intercept}
            - sine: {"amplitude": amp, "frequency": freq, "phase": phase}
            - polynomial: {"coefficients": [a0, a1, a2, ...]}
        noise_std: Standard deviation of noise to add (default: 1.0)
        seed: Random seed for reproducibility
        header: Whether to include header in output files
        add_complexity: Whether to add additional complexity to make data harder to fit (default: True)
        add_outliers: Whether to add outliers to the data (default: True)
    Returns:
        Tuple of (X values, y values) as numpy arrays
    """
    # Set default parameters if not provided
    if params is None:
        params = DEFAULT_MODEL_PARAMS[model_type]

    # Set random seed for reproducibility
    rng = np.random.default_rng(seed)

    # Generate sample IDs and X values with more randomness
    ids = np.arange(1, n + 1)
    X = np.linspace(0, 10, n) + rng.normal(0, 0.2, n)  # Increased jitter
    X = np.sort(X)  # Keep monotonically increasing

    # Generate y values based on model type with added complexity
    if model_type == "linear":
        y = params["a"] * X + params["b"]
        # Add some non-linear components to make it harder for models to perfectly fit
        if add_complexity:
            y = (
                y + 0.3 * np.sin(0.5 * X) + 0.2 * np.log1p(X)
            )  # Add non-linear components
    elif model_type == "sine":
        y = params["amplitude"] * np.sin(
            2 * np.pi * params["frequency"] * X + params["phase"]
        )
        # Add another sine component with different frequency to create more complex patterns
        if add_complexity:
            y = y + 0.5 * np.sin(5 * X) + 0.3 * np.cos(2 * X)
    elif model_type == "polynomial":
        coeffs = params["coefficients"]
        y = sum(coef * X**i for i, coef in enumerate(coeffs))
        # Add oscillatory component to make the polynomial harder to fit perfectly
        if add_complexity:
            y = y + 0.4 * np.sin(2 * X) * np.exp(-0.1 * X)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Create regions with different noise characteristics
    # This makes it harder for a single model to fit well across the entire range
    noise_factors = np.ones_like(X)
    segment1 = X < 3.3
    segment2 = (X >= 3.3) & (X < 6.6)
    segment3 = X >= 6.6
    noise_factors[segment1] = 0.8
    noise_factors[segment2] = 1.2
    noise_factors[segment3] = 1.5

    # Add heteroscedastic noise (noise increases with X and varies by segment)
    noise = rng.normal(0, noise_std * noise_factors * (1 + 0.2 * X), n)
    y += noise

    # Add outliers to make partitioning more challenging
    if add_outliers:
        # Add ~1% outliers
        n_outliers = max(int(n * 0.01), 5)
        outlier_indices = rng.choice(n, size=n_outliers, replace=False)

        # Create diverse outliers: some far above, some far below expected values
        outlier_factors = rng.choice([-2.5, -2.0, 2.0, 2.5], size=n_outliers)
        y[outlier_indices] = y[outlier_indices] * outlier_factors

        # Add some extreme X value outliers
        extreme_x_indices = rng.choice(n, size=max(int(n * 0.005), 3), replace=False)
        X[extreme_x_indices] = X[extreme_x_indices] * rng.uniform(
            0.85, 1.15, size=len(extreme_x_indices)
        )

    # Write data files
    _write_data_file(X_path, ids, X, header)
    _write_data_file(y_path, ids, y, header)

    return X, y


def generate_train_test_data(
    output_dir: str,
    n_samples: int = 10000,
    model_type: ModelType = "sine",
    params: Optional[dict] = None,
    test_params: Optional[dict] = None,
    noise_std: float = 1.0,
    seed: int = 42,
    header: bool = True,
    add_complexity: bool = True,
    add_outliers: bool = True,
) -> None:
    """
    Generate both training and test data sets.
    Args:
        output_dir: Directory to save the output files
        n_samples: Number of samples to generate for each dataset
        model_type: Type of model to generate data for
        params: Model-specific parameters (see generate_synthetic_data)
        test_params: Specific parameters for test data (if None, uses slightly modified training params)
        noise_std: Standard deviation of noise to add
        seed: Random seed for reproducibility
        header: Whether to include header in output files
        add_complexity: Whether to add additional complexity to make data harder to fit
        add_outliers: Whether to add outliers to the data
    """
    os.makedirs(output_dir, exist_ok=True)

    # Set up paths for data files
    train_X_path = os.path.join(output_dir, "X.txt")
    train_y_path = os.path.join(output_dir, "y.txt")
    test_X_path = os.path.join(output_dir, "X_new.txt")
    test_y_path = os.path.join(output_dir, "y_new.txt")

    # Generate training data
    logger.info(f"Generating {n_samples} training samples using {model_type} model")
    X_train, y_train = generate_synthetic_data(
        train_X_path,
        train_y_path,
        n=n_samples,
        model_type=model_type,
        params=params,
        noise_std=noise_std,
        seed=seed,
        header=header,
        add_complexity=add_complexity,
        add_outliers=add_outliers,
    )

    # For test data, modify parameters slightly and use a different seed
    if test_params is None:
        test_params = DEFAULT_TEST_MODEL_PARAMS.get(model_type, params)

    # Generate test data with modified parameters
    logger.info(f"Generating {n_samples} test samples using {model_type} model")
    X_test, y_test = generate_synthetic_data(
        test_X_path,
        test_y_path,
        n=n_samples,
        model_type=model_type,
        params=test_params,
        noise_std=noise_std * 1.2,  # Slightly more noise in test data
        seed=seed + 100,  # Different seed for test data
        header=header,
        add_complexity=add_complexity,
        add_outliers=add_outliers,
    )


def generate_linear_data(
    X_path: str,
    y_path: str,
    n: int = 10000,
    params: Optional[dict] = None,
    noise_std: float = 1.0,
    seed: int = 42,
    header: bool = True,
    add_complexity: bool = True,
    add_outliers: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate linear synthetic data for regression testing and save to files.
    This is a convenience wrapper for generate_synthetic_data with model_type='linear'.
    """
    return generate_synthetic_data(
        X_path,
        y_path,
        n=n,
        model_type="linear",
        params=params,
        noise_std=noise_std,
        seed=seed,
        header=header,
        add_complexity=add_complexity,
        add_outliers=add_outliers,
    )


def add_noise(y, noise_level=0.5):
    """
    Add Gaussian noise to the target values.

    Args:
        y: Target values
        noise_level: Standard deviation of the noise

    Returns:
        Array with added noise
    """
    return y + np.random.normal(0, noise_level, size=y.shape)


def save_data_to_file(X, y, X_path, y_path):
    """
    Save data to text files.

    Args:
        X: Feature data
        y: Target data
        X_path: Path to save X data
        y_path: Path to save y data

    Returns:
        True if saving was successful
    """
    np.savetxt(X_path, X)
    np.savetxt(y_path, y)
    return True


# --- CLI functionality ---


def parse_cli_arguments():
    """Parse command line arguments for data generation CLI."""
    parser = argparse.ArgumentParser(
        description="Generate test data for regression tests via CLI"
    )
    parser.add_argument(
        "--n-samples", type=int, default=10000, help="Number of samples to generate"
    )
    # Adjust default path: from fit_better, go up two levels to project root, then to tests/data_gen/data
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_output_dir = os.path.join(project_root, "tests", "data_gen", "data")
    parser.add_argument(
        "--output-dir",
        default=default_output_dir,
        help=f"Directory to save the generated data (default: {default_output_dir})",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["linear", "sine", "polynomial"],
        default="sine",
        help="Type of model to generate data for",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--noise", type=float, default=1.0, help="Standard deviation of noise to add"
    )
    parser.add_argument(
        "--complexity",
        action="store_true",
        default=True,
        help="Add complexity to make data harder to fit perfectly",
    )
    parser.add_argument(
        "--no-complexity",
        action="store_false",
        dest="complexity",
        help="Generate simpler data without additional complexity",
    )
    parser.add_argument(
        "--outliers", action="store_true", default=True, help="Add outliers to the data"
    )
    parser.add_argument(
        "--no-outliers",
        action="store_false",
        dest="outliers",
        help="Generate data without outliers",
    )
    return parser.parse_args()


def setup_cli_logging():
    """Set up logging configuration for data generation CLI."""
    # Adjust path: from fit_better, go up two levels to project root, then to tests/data_gen/logs
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, "tests", "data_gen", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = (
        f"generate_test_data_cli_{timestamp}.log"  # distinguish from other logs
    )
    log_path = os.path.join(logs_dir, log_filename)

    latest_log_symlink = os.path.join(
        logs_dir, "generate_test_data.log"
    )  # Keep original symlink name for test_all.py
    if os.path.islink(latest_log_symlink) or os.path.exists(latest_log_symlink):
        os.remove(latest_log_symlink)

    try:
        os.symlink(
            log_filename, latest_log_symlink
        )  # Symlink to the timestamped CLI log
    except Exception as e:
        # Use print as logging might not be fully set up yet or if it's a symlink permission issue
        print(
            f"Warning: Could not create log symlink '{latest_log_symlink}' -> '{log_filename}': {e}. Generation will continue."
        )

    return log_path


def main_cli_entrypoint():
    """Main command-line entry point for the test data generation script."""
    try:
        args = parse_cli_arguments()
        log_path = setup_cli_logging()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] (%(module)s.main_cli_entrypoint) %(message)s",
            handlers=[logging.FileHandler(log_path, mode="w"), logging.StreamHandler()],
        )

        logger.info("Starting test data generation (via CLI entrypoint):")
        logger.info(f"  - Model type: {args.model}")
        logger.info(f"  - Samples: {args.n_samples}")
        logger.info(f"  - Output directory: {args.output_dir}")
        logger.info(f"  - Random seed: {args.seed}")
        logger.info(f"  - Noise std: {args.noise}")
        logger.info(f"  - Add complexity: {args.complexity}")
        logger.info(f"  - Add outliers: {args.outliers}")

        generate_train_test_data(
            output_dir=args.output_dir,
            n_samples=args.n_samples,
            model_type=args.model,
            noise_std=args.noise,
            seed=args.seed,
            add_complexity=args.complexity,
            add_outliers=args.outliers,
        )

        logger.info("Data generation complete (via CLI entrypoint)!")
    except Exception as e:
        if logging.getLogger().hasHandlers():  # Check if logging was set up
            logger.error(f"Error during data generation (CLI entrypoint): {str(e)}")
        else:  # Fallback to print if logging setup failed
            print(f"CRITICAL ERROR during data generation (CLI entrypoint): {str(e)}")
        # Re-raise to ensure script exits with error status if called programmatically
        # and to allow higher-level error handlers or scripts to catch it.
        raise


if __name__ == "__main__":
    # This allows running synthetic_data.py directly to generate data
    main_cli_entrypoint()


def generate_synthetic_data_by_function(
    function=None,
    function_type: str = "linear",
    n_samples: int = 1000,
    n_features: int = 1,
    noise_std: float = 0.5,
    add_outliers: bool = False,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic data for regression testing.

    Args:
        function: Custom function to generate y values from X (takes X array as input, returns y array)
                 If provided, this overrides the function_type parameter
        function_type: Type of function to generate data for if no custom function provided
                      ("linear", "sine", "polynomial", "complex")
        n_samples: Number of samples to generate
        n_features: Number of input features (columns in X) to generate
        noise_std: Standard deviation of noise to add
        add_outliers: Whether to add outliers to the data
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (X values, y values) as numpy arrays
    """
    # Set random seed for reproducibility
    rng = np.random.RandomState(random_state)

    # Generate X values - multi-feature support
    if n_features == 1:
        # For single feature, maintain backward compatibility
        X_base = np.linspace(0, 10, n_samples)
        # Add some jitter based on the random seed
        X = X_base + rng.normal(0, 0.05, n_samples)
        X = np.sort(X).reshape(-1, 1)  # Ensure it's still sorted and 2D
    else:
        # For multi-feature data, generate values with different ranges
        X = np.zeros((n_samples, n_features))
        for i in range(n_features):
            feature_base = np.linspace(0, 10, n_samples)
            feature = feature_base + rng.normal(0, 0.05, n_samples)
            # Only sort the first feature to maintain structure
            if i == 0:
                sort_idx = np.argsort(feature)
                feature = np.sort(feature)
                # Sort all previously generated features according to the same index
                for j in range(i):
                    X[:, j] = X[sort_idx, j]
            else:
                # Add more variation to additional features
                feature = feature * (1 + 0.1 * i) - (0.2 * i)
            X[:, i] = feature

    # Use custom function if provided
    if function is not None:
        y = function(X)
    else:
        # Generate y values based on function type
        if function_type == "linear":
            if n_features == 1:
                y = 2.0 * X.flatten() + 1.0
            else:
                # Simple linear combination of features with different weights
                y = (
                    np.sum([0.5 * (i + 1) * X[:, i] for i in range(n_features)], axis=0)
                    + 1.0
                )
        elif function_type == "sine":
            if n_features == 1:
                y = 2.0 * np.sin(2.0 * np.pi * X.flatten() + 0.3)
            else:
                # Sine with interaction between features
                y = 2.0 * np.sin(2.0 * np.pi * X[:, 0] + 0.3)
                for i in range(1, n_features):
                    y += 1.0 * np.cos(1.0 * np.pi * X[:, i] + 0.1 * i)
        elif function_type == "polynomial":
            coeffs = [0.5, -1.5, 0.8, -0.2]  # x^3 - 0.2x^2 + 0.8x + 0.5
            if n_features == 1:
                y = sum(coef * X.flatten() ** i for i, coef in enumerate(coeffs))
            else:
                # Different polynomial for each feature
                y = np.zeros(n_samples)
                for i in range(min(n_features, len(coeffs))):
                    y += coeffs[i] * X[:, i] ** (i + 1)
                # Add some cross-terms for interaction
                if n_features >= 2:
                    y += 0.5 * X[:, 0] * X[:, 1]
        elif function_type == "complex":
            # Complex function with multiple components
            if n_features == 1:
                x = X.flatten()
                y = (
                    0.5 * np.sin(5 * x)
                    + 0.3 * np.exp(-0.1 * x) * np.cos(2 * x)
                    + 0.2 * np.log1p(x)
                )
            else:
                # More complex function with interactions
                y = np.zeros(n_samples)
                for i in range(n_features):
                    if i == 0:
                        y += 0.5 * np.sin(5 * X[:, i])
                    elif i == 1:
                        y += 0.3 * np.exp(-0.1 * X[:, i]) * np.cos(2 * X[:, i])
                    else:
                        y += 0.2 * np.log1p(X[:, i]) + 0.1 * i * np.sin(i * X[:, i])

                # Add interaction terms if we have at least 2 features
                if n_features >= 2:
                    y += 0.4 * X[:, 0] * X[:, 1]
        else:
            raise ValueError(f"Unknown function type: {function_type}")

    # Add noise
    y += rng.normal(0, noise_std, size=n_samples)

    # Add outliers if requested
    if add_outliers:
        # Add ~1% outliers
        n_outliers = max(int(n_samples * 0.01), 5)
        outlier_indices = rng.choice(n_samples, size=n_outliers, replace=False)

        # Create diverse outliers: some far above, some far below expected values
        outlier_factors = rng.choice([-3, -2, 2, 3], size=n_outliers)
        y[outlier_indices] = y[outlier_indices] * outlier_factors

        # Add some extreme X value outliers
        if n_features >= 1:
            extreme_x_indices = rng.choice(
                n_samples, size=max(int(n_samples * 0.005), 3), replace=False
            )
            for i in range(n_features):
                X[extreme_x_indices, i] = X[extreme_x_indices, i] * rng.uniform(
                    0.5, 1.5, size=len(extreme_x_indices)
                )

    return X, y


def generate_train_test_data(
    function=None,
    function_type: str = "linear",
    n_samples_train: int = 800,
    n_samples_test: int = 200,
    n_features: int = 1,
    noise_std: float = 0.5,
    add_outliers: bool = False,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate train and test datasets for regression testing.

    Args:
        function: Custom function to generate y values from X (takes X array as input, returns y array)
        function_type: Type of function to generate data for if no custom function provided
        n_samples_train: Number of training samples
        n_samples_test: Number of test samples
        n_features: Number of input features to generate
        noise_std: Standard deviation of noise to add
        add_outliers: Whether to add outliers to the data
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (X_train, y_train, X_test, y_test) as numpy arrays
    """
    # Set random seed for reproducibility
    rng = np.random.RandomState(random_state)

    # Generate X values for training and testing with multiple features
    if n_features == 1:
        X_train = np.linspace(0, 10, n_samples_train).reshape(-1, 1)
        # Make test data slightly different range
        X_test = np.linspace(0.1, 10.1, n_samples_test).reshape(-1, 1)
    else:
        X_train = np.zeros((n_samples_train, n_features))
        X_test = np.zeros((n_samples_test, n_features))

        for i in range(n_features):
            # Generate base values
            train_base = np.linspace(0, 10, n_samples_train)
            test_base = np.linspace(0.1, 10.1, n_samples_test)

            # Add slight variations to each feature
            X_train[:, i] = train_base * (1 + 0.05 * i) - (0.1 * i)
            X_test[:, i] = test_base * (1 + 0.05 * i) - (0.1 * i)

    # Use custom function if provided
    if function is not None:
        y_train = function(X_train)
        y_test = function(X_test)
    else:
        # Generate y values based on function type
        if function_type == "linear":
            if n_features == 1:
                y_train = 2.0 * X_train.flatten() + 1.0
                y_test = 2.0 * X_test.flatten() + 1.0
            else:
                # Simple linear combination of features
                y_train = (
                    np.sum(
                        [0.5 * (i + 1) * X_train[:, i] for i in range(n_features)],
                        axis=0,
                    )
                    + 1.0
                )
                y_test = (
                    np.sum(
                        [0.5 * (i + 1) * X_test[:, i] for i in range(n_features)],
                        axis=0,
                    )
                    + 1.0
                )
        elif function_type == "sine":
            if n_features == 1:
                y_train = 2.0 * np.sin(2.0 * np.pi * X_train.flatten() + 0.3)
                y_test = 2.0 * np.sin(2.0 * np.pi * X_test.flatten() + 0.3)
            else:
                # Sine with interaction between features
                y_train = 2.0 * np.sin(2.0 * np.pi * X_train[:, 0] + 0.3)
                y_test = 2.0 * np.sin(2.0 * np.pi * X_test[:, 0] + 0.3)

                for i in range(1, n_features):
                    y_train += 1.0 * np.cos(1.0 * np.pi * X_train[:, i] + 0.1 * i)
                    y_test += 1.0 * np.cos(1.0 * np.pi * X_test[:, i] + 0.1 * i)
        elif function_type == "polynomial":
            coeffs = [0.5, -1.5, 0.8, -0.2]
            if n_features == 1:
                y_train = sum(
                    coef * X_train.flatten() ** i for i, coef in enumerate(coeffs)
                )
                y_test = sum(
                    coef * X_test.flatten() ** i for i, coef in enumerate(coeffs)
                )
            else:
                # Different polynomial for each feature
                y_train = np.zeros(n_samples_train)
                y_test = np.zeros(n_samples_test)

                for i in range(min(n_features, len(coeffs))):
                    y_train += coeffs[i] * X_train[:, i] ** (i + 1)
                    y_test += coeffs[i] * X_test[:, i] ** (i + 1)

                # Add cross-terms for interaction
                if n_features >= 2:
                    y_train += 0.5 * X_train[:, 0] * X_train[:, 1]
                    y_test += 0.5 * X_test[:, 0] * X_test[:, 1]
        elif function_type == "complex":
            if n_features == 1:
                x_train = X_train.flatten()
                y_train = (
                    0.5 * np.sin(5 * x_train)
                    + 0.3 * np.exp(-0.1 * x_train) * np.cos(2 * x_train)
                    + 0.2 * np.log1p(x_train)
                )

                x_test = X_test.flatten()
                y_test = (
                    0.5 * np.sin(5 * x_test)
                    + 0.3 * np.exp(-0.1 * x_test) * np.cos(2 * x_test)
                    + 0.2 * np.log1p(x_test)
                )
            else:
                # More complex function with interactions
                y_train = np.zeros(n_samples_train)
                y_test = np.zeros(n_samples_test)

                for i in range(n_features):
                    if i == 0:
                        y_train += 0.5 * np.sin(5 * X_train[:, i])
                        y_test += 0.5 * np.sin(5 * X_test[:, i])
                    elif i == 1:
                        y_train += (
                            0.3
                            * np.exp(-0.1 * X_train[:, i])
                            * np.cos(2 * X_train[:, i])
                        )
                        y_test += (
                            0.3 * np.exp(-0.1 * X_test[:, i]) * np.cos(2 * X_test[:, i])
                        )
                    else:
                        y_train += 0.2 * np.log1p(X_train[:, i]) + 0.1 * i * np.sin(
                            i * X_train[:, i]
                        )
                        y_test += 0.2 * np.log1p(X_test[:, i]) + 0.1 * i * np.sin(
                            i * X_test[:, i]
                        )

                # Add interaction terms if we have at least 2 features
                if n_features >= 2:
                    y_train += 0.4 * X_train[:, 0] * X_train[:, 1]
                    y_test += 0.4 * X_test[:, 0] * X_test[:, 1]
        else:
            raise ValueError(f"Unknown function type: {function_type}")

    # Add noise
    y_train += rng.normal(0, noise_std, size=n_samples_train)
    y_test += rng.normal(0, noise_std, size=n_samples_test)

    # Add outliers if requested
    if add_outliers:
        # Add outliers to training data
        n_train_outliers = max(int(n_samples_train * 0.01), 3)
        train_outlier_indices = rng.choice(
            n_samples_train, size=n_train_outliers, replace=False
        )
        train_outlier_factors = rng.choice([-3, -2, 2, 3], size=n_train_outliers)
        y_train[train_outlier_indices] = (
            y_train[train_outlier_indices] * train_outlier_factors
        )

        # Add outliers to test data
        n_test_outliers = max(int(n_samples_test * 0.01), 2)
        test_outlier_indices = rng.choice(
            n_samples_test, size=n_test_outliers, replace=False
        )
        test_outlier_factors = rng.choice([-3, -2, 2, 3], size=n_test_outliers)
        y_test[test_outlier_indices] = (
            y_test[test_outlier_indices] * test_outlier_factors
        )

    return X_train, y_train, X_test, y_test


def save_data(
    X_train, y_train, X_test, y_test, output_dir, base_name="data", format="csv"
):
    """
    Save generated data to files.

    Args:
        X_train: Training feature data
        y_train: Training target data
        X_test: Test feature data
        y_test: Test target data
        output_dir: Directory to save the files
        base_name: Base name for the files
        format: File format ("csv", "txt", "npy" - default is "csv")

    Returns:
        Dictionary with paths to the saved files
    """
    from fit_better.data.csv_manager import CSVMgr

    os.makedirs(output_dir, exist_ok=True)

    # Create paths based on format
    if format.lower() == "csv":
        X_train_path = os.path.join(output_dir, f"{base_name}_X_train.csv")
        y_train_path = os.path.join(output_dir, f"{base_name}_y_train.csv")
        X_test_path = os.path.join(output_dir, f"{base_name}_X_test.csv")
        y_test_path = os.path.join(output_dir, f"{base_name}_y_test.csv")

        # Save as CSV using CSVMgr
        CSVMgr.from_array(array=X_train, has_header=False).export_array_csv(
            filepath=X_train_path, include_header=False
        )
        CSVMgr.from_array(
            array=y_train.reshape(-1, 1), has_header=False
        ).export_array_csv(filepath=y_train_path, include_header=False)
        CSVMgr.from_array(array=X_test, has_header=False).export_array_csv(
            filepath=X_test_path, include_header=False
        )
        CSVMgr.from_array(
            array=y_test.reshape(-1, 1), has_header=False
        ).export_array_csv(filepath=y_test_path, include_header=False)

    elif format.lower() == "txt":
        X_train_path = os.path.join(output_dir, f"{base_name}_X_train.txt")
        y_train_path = os.path.join(output_dir, f"{base_name}_y_train.txt")
        X_test_path = os.path.join(output_dir, f"{base_name}_X_test.txt")
        y_test_path = os.path.join(output_dir, f"{base_name}_y_test.txt")

        # Save as txt using CSVMgr with space delimiter
        CSVMgr.from_array(
            array=X_train, has_header=False, delimiter=" "
        ).export_array_csv(filepath=X_train_path, include_header=False, delimiter=" ")
        CSVMgr.from_array(
            array=y_train.reshape(-1, 1), has_header=False, delimiter=" "
        ).export_array_csv(filepath=y_train_path, include_header=False, delimiter=" ")
        CSVMgr.from_array(
            array=X_test, has_header=False, delimiter=" "
        ).export_array_csv(filepath=X_test_path, include_header=False, delimiter=" ")
        CSVMgr.from_array(
            array=y_test.reshape(-1, 1), has_header=False, delimiter=" "
        ).export_array_csv(filepath=y_test_path, include_header=False, delimiter=" ")

    elif format.lower() == "npy":
        X_train_path = os.path.join(output_dir, f"{base_name}_X_train.npy")
        y_train_path = os.path.join(output_dir, f"{base_name}_y_train.npy")
        X_test_path = os.path.join(output_dir, f"{base_name}_X_test.npy")
        y_test_path = os.path.join(output_dir, f"{base_name}_y_test.npy")

        # Save as npy
        np.save(X_train_path, X_train)
        np.save(y_train_path, y_train)
        np.save(X_test_path, X_test)
        np.save(y_test_path, y_test)

    else:
        raise ValueError(f"Unsupported format: {format}. Use 'csv', 'txt', or 'npy'.")

    return {
        "X_train": X_train_path,
        "y_train": y_train_path,
        "X_test": X_test_path,
        "y_test": y_test_path,
    }
