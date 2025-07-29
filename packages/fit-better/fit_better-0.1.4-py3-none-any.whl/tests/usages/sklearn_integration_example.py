#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-05-10
Description: Example script demonstrating integration between fit-better and scikit-learn.

Usage:
    python sklearn_integration_example.py [options]

This script shows how to use fit-better's models and functions within scikit-learn's
ecosystem, including cross-validation, pipelines, and grid search capabilities.

Options:
    --n-samples N       Number of samples to generate (default: 1000)
    --noise-level N     Standard deviation of noise to add (default: 0.5)
    --n-jobs N          Number of parallel jobs (default: 1)
    --output-dir DIR    Directory to save results (default: sklearn_integration_results)
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
    generate_synthetic_data_by_function,
    save_model,
    load_model,
)
from fit_better.models.sklearn import FitBetterRegressor, FitBetterPartitionedRegressor

# Import scikit-learn functionality
from sklearn.model_selection import cross_val_score, GridSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def demonstrate_sklearn_integration(X, y, n_jobs=1, output_dir=None):
    """
    Demonstrate integration between fit-better and scikit-learn.

    Args:
        X: Input features
        y: Target values
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 1. Example: Using FitBetterRegressor with scikit-learn cross-validation
    demonstrate_cross_validation(X, y, n_jobs)

    # 2. Example: Using FitBetterRegressor in a scikit-learn pipeline
    demonstrate_pipeline(X, y, n_jobs, output_dir)

    # 3. Example: Using FitBetterRegressor with GridSearchCV
    demonstrate_grid_search(X, y, n_jobs, output_dir)

    # 4. Example: Using FitBetterPartitionedRegressor
    demonstrate_partitioned_regressor(X, y, n_jobs, output_dir)


def demonstrate_cross_validation(X, y, n_jobs):
    """
    Demonstrate using fit-better regressors with scikit-learn cross-validation.

    Args:
        X: Input features
        y: Target values
        n_jobs: Number of parallel jobs
    """
    logger.info("\n=== Cross-Validation with fit-better Regressors ===")

    # Create a fit-better regressor with different underlying algorithms
    regressor_types = [
        RegressorType.LINEAR,
        RegressorType.POLYNOMIAL_3,
        RegressorType.GRADIENT_BOOSTING,
        RegressorType.RANDOM_FOREST,
    ]

    # Perform 5-fold cross-validation for each regressor type
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    for regressor_type in regressor_types:
        regressor = FitBetterRegressor(regressor_type=regressor_type)

        # Calculate cross-validated R² scores
        cv_scores = cross_val_score(regressor, X, y, cv=cv, scoring="r2", n_jobs=n_jobs)

        logger.info(
            f"{regressor_type}: CV R² = {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}"
        )


def demonstrate_pipeline(X, y, n_jobs, output_dir):
    """
    Demonstrate using fit-better regressor in a scikit-learn pipeline.

    Args:
        X: Input features
        y: Target values
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
    """
    logger.info("\n=== Using fit-better in scikit-learn Pipeline ===")

    # Split data into train and test sets
    np.random.seed(42)
    indices = np.random.permutation(len(X))
    split = int(0.8 * len(X))
    train_idx, test_idx = indices[:split], indices[split:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Create pipeline with:
    # 1. StandardScaler: Standardize features
    # 2. PolynomialFeatures: Generate polynomial features
    # 3. FitBetterRegressor: Fit a model using fit-better
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("poly", PolynomialFeatures(degree=2)),
            ("regressor", FitBetterRegressor(regressor_type=RegressorType.RIDGE)),
        ]
    )

    # Train the pipeline
    pipeline.fit(X_train, y_train)

    # Make predictions
    y_pred = pipeline.predict(X_test)

    # Evaluate the pipeline
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    logger.info(f"Pipeline Test MSE: {mse:.4f}")
    logger.info(f"Pipeline Test R²: {r2:.4f}")

    # Save the trained pipeline using fit-better's save_model function
    if output_dir:
        pipeline_path = os.path.join(output_dir, "sklearn_pipeline.joblib")
        save_model(pipeline, pipeline_path)
        logger.info(f"Saved pipeline to {pipeline_path}")

        # Load the pipeline back
        loaded_pipeline = load_model(pipeline_path)["model"]
        y_pred_loaded = loaded_pipeline.predict(X_test)

        # Verify that loaded pipeline gives same results
        assert np.allclose(y_pred, y_pred_loaded)
        logger.info("Verified loaded pipeline produces identical predictions")


def demonstrate_grid_search(X, y, n_jobs, output_dir):
    """
    Demonstrate using fit-better regressors with GridSearchCV.

    Args:
        X: Input features
        y: Target values
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
    """
    logger.info("\n=== Grid Search with fit-better Regressors ===")

    # Split data into train and test sets
    np.random.seed(42)
    indices = np.random.permutation(len(X))
    split = int(0.8 * len(X))
    train_idx, test_idx = indices[:split], indices[split:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Create a pipeline with a fit-better regressor
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("poly", PolynomialFeatures()),
            ("regressor", FitBetterRegressor()),
        ]
    )

    # Define parameter grid for grid search
    param_grid = {
        "poly__degree": [1, 2, 3],
        "regressor__regressor_type": [
            RegressorType.LINEAR,
            RegressorType.RIDGE,
            RegressorType.HUBER,
            RegressorType.RANDOM_FOREST,
        ],
    }

    # Create grid search with cross-validation
    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=3,
        scoring="neg_mean_squared_error",
        n_jobs=n_jobs,
        verbose=1,
    )

    # Run grid search
    grid_search.fit(X_train, y_train)

    # Get best parameters and model
    best_params = grid_search.best_params_
    best_estimator = grid_search.best_estimator_

    # Make predictions with the best model
    y_pred = best_estimator.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    logger.info(f"Best parameters: {best_params}")
    logger.info(f"Best model Test MSE: {mse:.4f}")
    logger.info(f"Best model Test R²: {r2:.4f}")

    # Visualize grid search results
    if output_dir:
        visualize_grid_search_results(grid_search, output_dir)


def demonstrate_partitioned_regressor(X, y, n_jobs, output_dir):
    """
    Demonstrate using FitBetterPartitionedRegressor with scikit-learn.

    Args:
        X: Input features
        y: Target values
        n_jobs: Number of parallel jobs
        output_dir: Directory to save results
    """
    logger.info("\n=== Using FitBetterPartitionedRegressor ===")

    # Split data into train and test sets
    np.random.seed(42)
    indices = np.random.permutation(len(X))
    split = int(0.8 * len(X))
    train_idx, test_idx = indices[:split], indices[split:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Create a partitioned regressor
    partitioned_regressor = FitBetterPartitionedRegressor(
        n_partitions=5, regressor_type=RegressorType.GRADIENT_BOOSTING, n_jobs=n_jobs
    )

    # Train the regressor
    partitioned_regressor.fit(X_train, y_train)

    # Make predictions
    y_pred = partitioned_regressor.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    logger.info(f"Partitioned regressor Test MSE: {mse:.4f}")
    logger.info(f"Partitioned regressor Test R²: {r2:.4f}")

    # Visualize partitioning and predictions
    if output_dir:
        visualize_partitioned_predictions(
            partitioned_regressor, X_train, y_train, X_test, y_test, output_dir
        )


def visualize_grid_search_results(grid_search, output_dir):
    """
    Visualize grid search results.

    Args:
        grid_search: Fitted GridSearchCV object
        output_dir: Directory to save plots
    """
    # Extract results from grid search
    results = grid_search.cv_results_

    # Get unique values for each parameter
    degrees = sorted(set([params["poly__degree"] for params in results["params"]]))
    regressor_types = sorted(
        set([str(params["regressor__regressor_type"]) for params in results["params"]])
    )

    # Create a 2D grid of mean scores
    scores = np.zeros((len(degrees), len(regressor_types)))

    for i, degree in enumerate(degrees):
        for j, regressor_type in enumerate(regressor_types):
            # Find matching parameter combination
            for k, params in enumerate(results["params"]):
                if (
                    params["poly__degree"] == degree
                    and str(params["regressor__regressor_type"]) == regressor_type
                ):
                    # Convert negative MSE to positive MSE for visualization
                    scores[i, j] = -results["mean_test_score"][k]
                    break

    # Create heatmap
    plt.figure(figsize=(10, 6))
    im = plt.imshow(scores, cmap="viridis")

    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label("Mean Squared Error")

    # Set axis labels
    plt.xticks(
        np.arange(len(regressor_types)),
        [rt.split(".")[-1] for rt in regressor_types],
        rotation=45,
    )
    plt.yticks(np.arange(len(degrees)), [f"Degree {d}" for d in degrees])

    plt.xlabel("Regressor Type")
    plt.ylabel("Polynomial Features")
    plt.title("Grid Search Results: MSE by Parameter Combination")

    # Add text annotations
    for i in range(len(degrees)):
        for j in range(len(regressor_types)):
            plt.text(
                j, i, f"{scores[i, j]:.2f}", ha="center", va="center", color="white"
            )

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grid_search_results.png"))
    plt.close()


def visualize_partitioned_predictions(
    model, X_train, y_train, X_test, y_test, output_dir
):
    """
    Visualize predictions from a partitioned regressor.

    Args:
        model: Trained FitBetterPartitionedRegressor
        X_train: Training features
        y_train: Training targets
        X_test: Test features
        y_test: Test targets
        output_dir: Directory to save plots
    """
    # Get partition boundaries
    boundaries = model.boundaries_

    # Combine train and test data for visualization
    X_all = np.vstack([X_train, X_test])
    y_all = np.concatenate([y_train, y_test])

    # Create points for prediction curve
    X_curve = np.linspace(X_all.min(), X_all.max(), 1000).reshape(-1, 1)
    y_curve = model.predict(X_curve)

    # Sort by X for plotting
    idx = np.argsort(X_curve.flatten())
    X_curve_sorted = X_curve[idx]
    y_curve_sorted = y_curve[idx]

    # Create figure
    plt.figure(figsize=(12, 8))

    # Plot data points
    plt.scatter(X_train, y_train, alpha=0.5, label="Training Data")
    plt.scatter(X_test, y_test, alpha=0.7, label="Test Data")

    # Plot prediction curve
    plt.plot(X_curve_sorted, y_curve_sorted, "r-", linewidth=2, label="Prediction")

    # Add partition boundaries
    for b in boundaries:
        plt.axvline(x=b, linestyle="--", color="gray")

    # Add labels and legend
    plt.title("Partitioned Regressor Predictions")
    plt.xlabel("X")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "partitioned_predictions.png"))
    plt.close()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Demonstrate scikit-learn integration")

    parser.add_argument(
        "--n-samples", type=int, default=1000, help="Number of samples to generate"
    )
    parser.add_argument(
        "--noise-level", type=float, default=0.5, help="Standard deviation of noise"
    )
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")

    # Output directory - default to a subdirectory in tests/data_gen
    tests_dir = Path(__file__).resolve().parent.parent
    default_output_dir = str(tests_dir / "data_gen" / "sklearn_integration_results")

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help="Directory to save results",
    )

    args = parser.parse_args()

    # Generate synthetic data (complex function should show benefits of partitioning)
    logger.info(f"Generating complex data with {args.n_samples} samples...")
    X, y = generate_synthetic_data_by_function(
        function_type="complex", n_samples=args.n_samples, noise_std=args.noise_level
    )[
        0:2
    ]  # Only take X_train, y_train from the returned tuple

    # Demonstrate sklearn integration
    logger.info("Demonstrating scikit-learn integration...")
    demonstrate_sklearn_integration(
        X, y, n_jobs=args.n_jobs, output_dir=args.output_dir
    )

    # Print final message
    logger.info(f"Results and visualizations saved to {args.output_dir}")


if __name__ == "__main__":
    main()
