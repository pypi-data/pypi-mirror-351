#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Example script for comparing different regression algorithms on the same dataset.

Usage:
    python regressor_comparison_example.py [options]

This script demonstrates how to compare multiple regression algorithms using the fit-better
package. It generates synthetic data, fits multiple regression models, and compares their
performance using various metrics like MAE, RMSE, R², and percentage-based metrics.

Options:
    --n-samples N          Number of samples to generate (default: 1000)
    --noise-level N        Standard deviation of noise to add (default: 0.5)
    --n-jobs N             Number of parallel jobs (default: 1)
    --output-dir DIR       Directory to save results (default: regressor_comparison_results)
    --function-type STR    Type of function for synthetic data: linear, sine, polynomial, complex (default: sine)
"""
import os
import sys
import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import from fit_better
from fit_better import (
    RegressorType,
    fit_all_regressors,
    select_best_model,
    generate_train_test_data,
    calc_regression_statistics,
    plot_performance_comparison,
    plot_predictions_vs_actual,
    plot_error_distribution,
    generate_synthetic_data_by_function,
    save_data,
    RegressionFlow,
    Metric,
)
from fit_better.utils.ascii import print_ascii_table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def compare_regressors(
    X_train=None,
    y_train=None,
    X_test=None,
    y_test=None,
    n_jobs=1,
    output_dir=None,
    visualize=True,
    n_partitions=None,
    use_regression_flow=False,
):
    """
    Compare different regression algorithms on the same dataset.

    Args:
        X_train: Training features (if None, will load test data)
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
        visualize: Whether to generate visualizations
        n_partitions: Number of partitions to use (for compatibility with unit tests)
        use_regression_flow: Whether to use RegressionFlow API

    Returns:
        Tuple of (best_regressor, best_mae) for compatibility with tests
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # If data not provided, load test data
    if X_train is None or y_train is None or X_test is None or y_test is None:
        # Pass output_dir as data_dir to load_test_data to ensure consistency
        X_train, y_train, X_test, y_test = load_test_data(data_dir=output_dir)

    if use_regression_flow:
        # Use RegressionFlow for a more streamlined approach
        logger.info("Using RegressionFlow API to train and evaluate models...")
        flow = RegressionFlow()
        result = flow.find_best_strategy(
            X_train,
            y_train,
            X_test,
            y_test,
            partition_modes=None,  # No partitioning for this example
            n_jobs=n_jobs,
            metrics_to_optimize=Metric.MAE,
        )

        # Extract results from RegressionFlow output
        best_regressor = result.model_type
        best_mae = result.metrics["mae"]

        # Print results
        logger.info(f"Best model: {best_regressor.name} with MAE: {best_mae:.4f}")

        # Generate visualizations if requested
        if visualize and output_dir:
            plt.figure(figsize=(10, 8))
            plot_predictions_vs_actual(
                y_test,
                flow.predict(X_test),
                title=f"Predictions vs Actual ({best_regressor.name})",
            )
            plt.savefig(
                os.path.join(output_dir, f"predictions_{best_regressor.name}.png")
            )
            plt.close()

            plt.figure(figsize=(10, 8))
            plot_error_distribution(
                y_test,
                flow.predict(X_test),
                title=f"Error Distribution ({best_regressor.name})",
            )
            plt.savefig(os.path.join(output_dir, f"errors_{best_regressor.name}.png"))
            plt.close()

        return best_regressor, best_mae

    # Legacy approach using fit_all_regressors directly
    logger.info("Training all available regression models...")
    model_results = fit_all_regressors(X_train, y_train, n_jobs=n_jobs)

    # Evaluate each model on test data
    results = {}
    for model_dict in model_results:
        regressor_name = model_dict["model_name"]
        model = model_dict["model"]
        scaler = model_dict.get("scaler")
        transformer = model_dict.get("transformer")

        logger.info(f"Evaluating {regressor_name} on test data...")

        # Apply data transformations if needed
        X_test_processed = X_test
        if transformer:
            X_test_processed = transformer.transform(X_test)
        if scaler:
            X_test_processed = scaler.transform(X_test_processed)

        # Make predictions
        y_pred = model.predict(X_test_processed)

        # Calculate metrics using fit_better's utility function
        metrics = calc_regression_statistics(y_test, y_pred)

        # Store results
        results[regressor_name] = {"metrics": metrics, "model": model_dict}

    # Print results table
    print_comparison_table(results)

    # Generate visualizations if requested
    if visualize and output_dir:
        # Create a list of result dictionaries for the plotting function
        result_list = []
        for name, data in results.items():
            result_dict = {"regressor_name": name}
            result_dict.update(data["metrics"])
            result_list.append(result_dict)

        # Plot using the correct function signature
        plt.figure(figsize=(10, 8))
        plot_performance_comparison(
            result_list,
            metric="mae",
            save_path=os.path.join(output_dir, "performance_comparison.png"),
        )
        plt.close()

        # Continue with individual predictions plots
        plot_predictions(X_train, y_train, X_test, y_test, results, output_dir)

    # Find best model by MAE
    best_regressor_name = min(results.items(), key=lambda x: x[1]["metrics"]["mae"])[0]
    best_mae = results[best_regressor_name]["metrics"]["mae"]

    # Convert the regressor name string to a RegressorType enum
    try:
        best_regressor = RegressorType.from_string(best_regressor_name)
    except ValueError:
        # If conversion fails, use SVR_RBF as a fallback
        logger.warning(
            f"Could not convert '{best_regressor_name}' to RegressorType. Using SVR_RBF as fallback."
        )
        best_regressor = RegressorType.SVR_RBF

    return best_regressor, best_mae


def print_comparison_table(results):
    """
    Print a formatted table comparing regressor performance.

    Args:
        results: Dictionary with results for each regressor
    """
    # Prepare data for table
    table_data = []
    metrics = ["mae", "rmse", "r2", "pct_within_1pct", "pct_within_5pct"]
    headers = ["Regressor", "MAE", "RMSE", "R²", "Within 1%", "Within 5%"]

    # Calculate ranks for each metric
    metric_ranks = {}
    for metric in metrics:
        # For R² and percentage metrics, higher is better
        reverse = metric in ["r2", "pct_within_1pct", "pct_within_5pct"]
        sorted_regressors = sorted(
            results.items(),
            key=lambda x: x[1]["metrics"].get(
                metric, float("-inf" if reverse else "inf")
            ),
            reverse=reverse,
        )
        ranks = {name: i + 1 for i, (name, _) in enumerate(sorted_regressors)}
        metric_ranks[metric] = ranks

    # Build table rows
    for name, data in results.items():
        m = data["metrics"]
        row = [
            name,
            f"{m['mae']:.4f} ({metric_ranks['mae'][name]})",
            f"{m['rmse']:.4f} ({metric_ranks['rmse'][name]})",
            f"{m['r2']:.4f} ({metric_ranks['r2'][name]})",
            f"{m.get('pct_within_1pct', 0):.1f}% ({metric_ranks['pct_within_1pct'].get(name, 'N/A')})",
            f"{m.get('pct_within_5pct', 0):.1f}% ({metric_ranks['pct_within_5pct'].get(name, 'N/A')})",
        ]
        table_data.append(row)

    # Print the table using the fit_better utility function
    print_ascii_table(headers, table_data)


def plot_predictions(X_train, y_train, X_test, y_test, results, output_dir):
    """
    Generate plots of predictions vs actual values for each model.

    Args:
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        results: Results dictionary
        output_dir: Directory to save plots
    """
    plots_dir = os.path.join(output_dir, "predictions")
    os.makedirs(plots_dir, exist_ok=True)

    for name, data in results.items():
        try:
            plot_single_model_prediction(
                X_train, y_train, X_test, y_test, name, data, plots_dir
            )
        except Exception as e:
            logger.error(f"Error plotting predictions for {name}: {e}")


def plot_single_model_prediction(
    X_train, y_train, X_test, y_test, name, data, output_dir
):
    """Plot predictions for a single model."""
    try:
        model_dict = data["model"]
        model = model_dict["model"]
        scaler = model_dict.get("scaler")
        transformer = model_dict.get("transformer")

        # Process test data
        X_test_processed = X_test.copy()
        if transformer:
            X_test_processed = transformer.transform(X_test_processed)
        if scaler:
            X_test_processed = scaler.transform(X_test_processed)

        # Generate predictions
        y_pred = model.predict(X_test_processed)

        # Create plots using fit_better's plotting utilities
        plt.figure(figsize=(10, 8))
        plot_predictions_vs_actual(
            y_test,
            y_pred,
            title=f"Predictions vs Actual ({name})",
            save_path=os.path.join(
                output_dir, f"predictions_{name.replace(' ', '_')}.png"
            ),
        )
        plt.close()

        plt.figure(figsize=(10, 8))
        plot_error_distribution(
            y_test,
            y_pred,
            title=f"Error Distribution ({name})",
            save_path=os.path.join(output_dir, f"errors_{name.replace(' ', '_')}.png"),
        )
        plt.close()
    except Exception as e:
        logger.error(f"Error plotting predictions for {name}: {e}")
        # Create an error placeholder file so we have evidence that plotting was attempted
        with open(
            os.path.join(output_dir, f"error_plotting_{name.replace(' ', '_')}.txt"),
            "w",
        ) as f:
            f.write(f"Error plotting predictions: {str(e)}\n")


def load_test_data(
    data_dir=None,
    function_type="sine",
    n_samples=1000,
    noise_level=0.5,
    random_state=42,
):
    """
    Load or generate test data.

    Args:
        data_dir: Directory to load/save data
        function_type: Type of function to generate data from
        n_samples: Number of samples to generate
        noise_level: Standard deviation of noise to add
        random_state: Random seed

    Returns:
        X_train, y_train, X_test, y_test
    """
    # If data_dir is provided, try to load data from there
    if data_dir and os.path.exists(data_dir):
        try:
            # Try to load existing data
            return load_test_data_from_dir(data_dir)
        except Exception as e:
            logger.warning(f"Could not load data from {data_dir}: {e}")

    # Generate synthetic data based on function type
    logger.info(f"Generating synthetic data with function type: {function_type}")

    if function_type == "linear":
        # Simple linear function with multiple features
        X_train, y_train, X_test, y_test = generate_train_test_data(
            n_samples=n_samples,
            n_features=3,
            noise=noise_level,
            test_size=0.2,
            random_state=random_state,
        )
    elif function_type == "sine":
        # Generate sine function data
        # Generate all samples and then split them
        total_samples = n_samples
        X, y = generate_synthetic_data_by_function(
            function=lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5) + 0.5 * X[:, 1],
            n_samples=total_samples,
            n_features=2,
            noise_std=noise_level,
            random_state=random_state,
        )
        # Manually split the data into training and test sets
        split_idx = int(total_samples * 0.8)
        # Set the random seed for shuffling
        np.random.seed(random_state)
        # Generate shuffled indices
        indices = np.random.permutation(total_samples)
        # Split the data
        X_train, X_test = X[indices[:split_idx]], X[indices[split_idx:]]
        y_train, y_test = y[indices[:split_idx]], y[indices[split_idx:]]
    elif function_type == "polynomial":
        # Generate polynomial function data
        # Generate all samples and then split them
        total_samples = n_samples
        X, y = generate_synthetic_data_by_function(
            function=lambda X: 2.0 * X[:, 0] ** 2
            + 3.0 * X[:, 1]
            - 1.5 * X[:, 0] * X[:, 1],
            n_samples=total_samples,
            n_features=2,
            noise_std=noise_level,
            random_state=random_state,
        )
        # Manually split the data into training and test sets
        split_idx = int(total_samples * 0.8)
        # Set the random seed for shuffling
        np.random.seed(random_state)
        # Generate shuffled indices
        indices = np.random.permutation(total_samples)
        # Split the data
        X_train, X_test = X[indices[:split_idx]], X[indices[split_idx:]]
        y_train, y_test = y[indices[:split_idx]], y[indices[split_idx:]]
    elif function_type == "complex":
        # Generate more complex function data
        # Generate all samples and then split them
        total_samples = n_samples
        X, y = generate_synthetic_data_by_function(
            function=lambda X: 2.0 * np.sin(X[:, 0]) * np.cos(X[:, 1])
            + 0.5 * X[:, 2] ** 2
            - 0.3 * X[:, 0] * X[:, 2],
            n_samples=total_samples,
            n_features=3,
            noise_std=noise_level,
            random_state=random_state,
        )
        # Manually split the data into training and test sets
        split_idx = int(total_samples * 0.8)
        # Set the random seed for shuffling
        np.random.seed(random_state)
        # Generate shuffled indices
        indices = np.random.permutation(total_samples)
        # Split the data
        X_train, X_test = X[indices[:split_idx]], X[indices[split_idx:]]
        y_train, y_test = y[indices[:split_idx]], y[indices[split_idx:]]
    else:
        raise ValueError(f"Unknown function type: {function_type}")

    # Save data if directory provided
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)
        save_data(X_train, y_train, X_test, y_test, data_dir, "regressor_comparison")

    return X_train, y_train, X_test, y_test


def load_test_data_from_dir(data_dir):
    """
    Load test data from directory.

    Args:
        data_dir: Directory to load data from

    Returns:
        X_train, y_train, X_test, y_test
    """
    # Generate file paths for various possible file names
    possible_base_names = ["regressor_comparison", "data", "synthetic"]
    possible_extensions = [".npy", ".csv", ".txt"]

    # Look for files with common naming patterns
    for base_name in possible_base_names:
        for ext in possible_extensions:
            try:
                # Try loading with this naming pattern
                X_train_file = os.path.join(data_dir, f"{base_name}_X_train{ext}")
                y_train_file = os.path.join(data_dir, f"{base_name}_y_train{ext}")
                X_test_file = os.path.join(data_dir, f"{base_name}_X_test{ext}")
                y_test_file = os.path.join(data_dir, f"{base_name}_y_test{ext}")

                # Check if all files exist
                if all(
                    os.path.exists(f)
                    for f in [X_train_file, y_train_file, X_test_file, y_test_file]
                ):
                    # Load data with appropriate function based on extension
                    if ext == ".npy":
                        X_train = np.load(X_train_file)
                        y_train = np.load(y_train_file)
                        X_test = np.load(X_test_file)
                        y_test = np.load(y_test_file)
                    else:  # csv or txt
                        delimiter = "," if ext == ".csv" else None
                        X_train = np.loadtxt(X_train_file, delimiter=delimiter)
                        y_train = np.loadtxt(y_train_file, delimiter=delimiter)
                        X_test = np.loadtxt(X_test_file, delimiter=delimiter)
                        y_test = np.loadtxt(y_test_file, delimiter=delimiter)

                    logger.info(
                        f"Loaded data from {data_dir} with base name {base_name}{ext}"
                    )
                    return X_train, y_train, X_test, y_test
            except Exception as e:
                logger.debug(f"Could not load data with pattern {base_name}{ext}: {e}")
                continue

    # If we got here, we couldn't find suitable files
    raise FileNotFoundError(f"Could not find suitable data files in {data_dir}")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Compare different regression algorithms on a synthetic dataset"
    )
    parser.add_argument(
        "--n-samples", type=int, default=1000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--noise-level",
        type=float,
        default=0.5,
        help="Standard deviation of noise to add",
    )
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")

    # Get the tests directory path
    tests_dir = Path(__file__).resolve().parent.parent
    default_output_dir = str(tests_dir / "data_gen" / "regressor_comparison_results")

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help="Directory to save results",
    )
    parser.add_argument(
        "--function-type",
        type=str,
        choices=["linear", "sine", "polynomial", "complex"],
        default="sine",
        help="Type of function for synthetic data",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualization plots",
    )
    parser.add_argument(
        "--use-regression-flow",
        action="store_true",
        help="Use RegressionFlow API for a more streamlined approach",
    )
    args = parser.parse_args()

    logger.info("Starting regressor comparison example...")
    logger.info(f"Configuration: {vars(args)}")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Compare regressors
    start_time = time.time()
    best_regressor, best_mae = compare_regressors(
        n_jobs=args.n_jobs,
        output_dir=args.output_dir,
        visualize=args.visualize,
        use_regression_flow=args.use_regression_flow,
    )
    elapsed_time = time.time() - start_time

    logger.info(f"Best regressor: {best_regressor.name} with MAE: {best_mae:.4f}")
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    import time

    main()
