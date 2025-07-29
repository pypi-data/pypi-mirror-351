#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-06-01
Description: Example script demonstrating model saving and loading in fit-better.
Usage:
    python model_save_load_example.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

# Add fit_better to path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from fit_better import RegressorType, fit_all_regressors, select_best_model
from fit_better.io import save_model, load_model, predict_with_model
from fit_better.data import generate_synthetic_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    print("\nModel Save/Load Example")
    print("=" * 50)

    # Create output directory
    tests_dir = Path(__file__).resolve().parent.parent
    output_dir = tests_dir / "data_gen" / "saved_models"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic data
    print("Generating synthetic data...")
    n_samples = 200
    X = np.linspace(-5, 5, n_samples).reshape(-1, 1)
    y = 0.5 * X.ravel() + 2 + np.sin(X.ravel()) + np.random.normal(0, 0.5, n_samples)

    # Split data into train and test sets
    train_size = int(0.8 * n_samples)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Train multiple model types
    print("\nTraining multiple regression models...")
    model_types = [
        RegressorType.LINEAR,
        RegressorType.RIDGE,
        RegressorType.LASSO,
        RegressorType.ELASTIC_NET,
        RegressorType.RANDOM_FOREST,
        RegressorType.GRADIENT_BOOSTING,
    ]

    model_results = {}
    for model_type in model_types:
        print(f"Training {model_type}...")
        results = fit_all_regressors(
            X_train, y_train, n_jobs=1, regressor_type=model_type
        )
        if results:
            best_model = select_best_model(results)
            model_results[model_type] = best_model

    # Save each model and then load it back
    print("\nSaving and loading models...")
    for model_type, model_result in model_results.items():
        # Save model
        model_path = output_dir / f"{model_type.name.lower()}_model.joblib"
        print(f"Saving {model_type} to {model_path}...")
        save_model(
            model_result, str(model_path), overwrite=True
        )  # Added overwrite=True

        # Load model back
        loaded_model = load_model(str(model_path))

        # Make predictions with both original and loaded model
        orig_preds = predict_with_model(model_result, X_test)
        loaded_preds = predict_with_model(loaded_model, X_test)

        # Verify predictions match
        prediction_match = np.allclose(orig_preds, loaded_preds)
        print(
            f"Predictions match between original and loaded model: {prediction_match}"
        )
        if not prediction_match:
            print(f"  Max difference: {np.max(np.abs(orig_preds - loaded_preds))}")

    # Example of different ways to save/load models
    print("\nDemonstrating different model saving/loading approaches:")

    # 1. Saving a bare model (no preprocessors)
    simple_model = model_results[RegressorType.LINEAR]["model"]
    simple_path = output_dir / "simple_linear.joblib"
    save_model(simple_model, str(simple_path), overwrite=True)  # Added overwrite=True
    print(f"1. Saved simple model to {simple_path}")

    # 2. Saving a model with metadata
    rf_model = model_results[RegressorType.RANDOM_FOREST]
    rf_path = output_dir / "rf_with_metadata.joblib"
    save_model(rf_model, str(rf_path), overwrite=True)
    print(f"2. Saved model with metadata to {rf_path}")

    # 3. Loading and making predictions - standard approach
    loaded_simple = load_model(str(simple_path))
    simple_preds = predict_with_model(loaded_simple, X_test[:5])
    print(f"3. Loaded simple model and made predictions: {simple_preds[:3]}...")

    # 4. Loading and making predictions - model with preprocessors
    loaded_rf = load_model(str(rf_path))
    rf_preds = predict_with_model(loaded_rf, X_test[:5])
    print(f"4. Loaded RF model with metadata and made predictions: {rf_preds[:3]}...")

    # 5. Direct prediction with model path
    direct_preds = predict_with_model(str(rf_path), X_test[:5])
    print(f"5. Direct prediction using model path: {direct_preds[:3]}...")

    # Plot a comparison of original vs loaded predictions for one model
    plt.figure(figsize=(10, 6))
    plt.scatter(X_test, y_test, alpha=0.5, label="Ground truth")

    for model_type in [RegressorType.LINEAR, RegressorType.RANDOM_FOREST]:
        model_path = output_dir / f"{model_type.name.lower()}_model.joblib"
        loaded_model = load_model(str(model_path))
        loaded_preds = predict_with_model(loaded_model, X_test)

        plt.plot(
            X_test, loaded_preds, linewidth=2, label=f"Loaded {model_type} Predictions"
        )

    plt.title("Comparing Loaded Model Predictions")
    plt.xlabel("Feature")
    plt.ylabel("Target")
    plt.legend()

    # Save the plot
    plot_path = output_dir / "model_predictions.png"
    plt.savefig(plot_path)
    print(f"\nSaved comparison plot to {plot_path}")

    print("\nDone! Saved models are in the 'tests/data_gen/saved_models' directory.")
    print("You can load these models using fit_better.io.load_model() function.")


if __name__ == "__main__":
    main()
