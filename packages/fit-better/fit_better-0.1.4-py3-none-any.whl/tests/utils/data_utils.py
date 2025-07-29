"""
Data utility functions for test scripts.

This module provides reusable functions for data operations in tests:
- Loading test data from files
- Generating synthetic test data
- Saving data in multiple formats
"""

import os
import numpy as np
from pathlib import Path
from fit_better import (
    load_data_from_files,
    generate_synthetic_data_by_function,
    save_data,
)


def load_test_data(
    data_dir,
    x_train_file="X_train.npy",
    y_train_file="y_train.npy",
    x_test_file="X_test.npy",
    y_test_file="y_test.npy",
    delimiter=None,
    header="infer",
):
    """
    Load test data from files in the specified directory.

    Args:
        data_dir: Directory containing the data files
        x_train_file: X train data filename
        y_train_file: y train data filename
        x_test_file: X test data filename
        y_test_file: y test data filename
        delimiter: Delimiter for text files (default: ' ' for .txt, ',' for .csv)
        header: How to handle headers: 'infer' or 'none'

    Returns:
        X_train, y_train, X_test, y_test arrays
    """
    # Set default delimiter based on file extension if not specified
    if delimiter is None:
        if x_train_file.endswith(".txt"):
            delimiter = " "
        else:
            delimiter = ","

    return load_data_from_files(
        data_dir=data_dir,
        x_train_file=x_train_file,
        y_train_file=y_train_file,
        x_test_file=x_test_file,
        y_test_file=y_test_file,
        delimiter=delimiter,
        header=header,
    )


def generate_synthetic_data(
    n_samples_train=5000,
    n_samples_test=1000,
    n_features=3,
    noise_std=0.5,
    add_outliers=True,
    random_state=42,
):
    """
    Generate synthetic data for testing.

    Args:
        n_samples_train: Number of training samples
        n_samples_test: Number of test samples
        n_features: Number of features
        noise_std: Standard deviation of noise
        add_outliers: Whether to add outliers to the data
        random_state: Random state for reproducibility

    Returns:
        X_train, y_train, X_test, y_test arrays
    """
    # Default function: sine wave + cosine + linear term
    function = (
        lambda X: 3.0 * np.sin(2.0 * X[:, 0] + 0.5) + 1.5 * np.cos(X[:, 1]) - X[:, 2]
    )

    return generate_synthetic_data_by_function(
        function=function,
        n_samples_train=n_samples_train,
        n_samples_test=n_samples_test,
        n_features=n_features,
        noise_std=noise_std,
        add_outliers=add_outliers,
        random_state=random_state,
    )


def save_data_multiple_formats(
    X_train, y_train, X_test, y_test, output_dir, base_name="data"
):
    """
    Save data in multiple formats (CSV, NPY, TXT).

    Args:
        X_train: Training feature data
        y_train: Training target data
        X_test: Test feature data
        y_test: Test target data
        output_dir: Directory to save the files
        base_name: Base name for the files

    Returns:
        Dictionary with paths to the saved files
    """
    os.makedirs(output_dir, exist_ok=True)
    result_files = {}

    # Save in multiple formats
    for fmt in ["csv", "npy"]:
        result = save_data(
            X_train,
            y_train,
            X_test,
            y_test,
            output_dir=output_dir,
            base_name=base_name,
            format=fmt,
        )
        result_files[fmt] = result

    return result_files
