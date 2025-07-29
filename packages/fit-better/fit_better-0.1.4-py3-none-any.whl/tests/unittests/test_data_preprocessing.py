"""
Unit tests for data preprocessing functionality.

This test suite validates:
- Data normalization
- Data standardization
- Feature scaling
- Handling missing values
- Data splitting
"""

import os
import sys
import pytest
import numpy as np
from fit_better.data.preprocessing import (
    normalize_data,
    standardize_data,
    scale_features,
    handle_missing_values,
    train_test_split_with_indices,
)


@pytest.mark.unit
@pytest.mark.data
class TestDataPreprocessing:
    """Test suite for data preprocessing functionalities."""

    @pytest.fixture
    def sample_data(self):
        """Create a sample dataset with some outliers."""
        np.random.seed(42)
        X = np.random.rand(100, 3) * 10  # 3 features
        # Add some outliers
        X[0, 0] = 100
        X[1, 1] = -50
        X[2, 2] = 200
        return X

    @pytest.fixture
    def data_with_missing(self):
        """Create a sample dataset with missing values."""
        np.random.seed(42)
        X = np.random.rand(100, 3) * 10
        # Add some NaN values
        X[0, 0] = np.nan
        X[1, 1] = np.nan
        X[2, 2] = np.nan
        return X

    def test_normalize_data(self, sample_data):
        """Test data normalization to [0,1] range."""
        X = sample_data

        # Normalize the data
        X_norm, normalization_params = normalize_data(X)

        # Check if normalized data is in [0,1] range
        assert np.all(X_norm >= 0) and np.all(
            X_norm <= 1
        ), "Normalized data should be in [0,1] range"

        # Check if normalization parameters are correct
        assert "min" in normalization_params, "Missing min in normalization parameters"
        assert "max" in normalization_params, "Missing max in normalization parameters"

        # Check if normalization can be reversed
        X_denorm = (
            X_norm * (normalization_params["max"] - normalization_params["min"])
            + normalization_params["min"]
        )
        assert np.allclose(X, X_denorm), "Denormalized data should match original data"

    def test_standardize_data(self, sample_data):
        """Test data standardization (zero mean, unit variance)."""
        X = sample_data

        # Standardize the data
        X_std, standardization_params = standardize_data(X)

        # Check if standardized data has zero mean and unit variance
        assert np.allclose(
            np.mean(X_std, axis=0), 0, atol=1e-10
        ), "Standardized data should have zero mean"
        assert np.allclose(
            np.std(X_std, axis=0), 1, atol=1e-10
        ), "Standardized data should have unit variance"

        # Check if standardization parameters are correct
        assert (
            "mean" in standardization_params
        ), "Missing mean in standardization parameters"
        assert (
            "std" in standardization_params
        ), "Missing std in standardization parameters"

        # Check if standardization can be reversed
        X_destd = X_std * standardization_params["std"] + standardization_params["mean"]
        assert np.allclose(X, X_destd), "Destandardized data should match original data"

    def test_scale_features(self, sample_data):
        """Test feature scaling with custom range."""
        X = sample_data

        # Scale features to [-1, 1] range
        X_scaled, scaling_params = scale_features(X, feature_range=(-1, 1))

        # Check if scaled data is in [-1, 1] range
        assert np.all(X_scaled >= -1) and np.all(
            X_scaled <= 1
        ), "Scaled data should be in [-1, 1] range"

        # Check if scaling parameters are correct
        assert "min" in scaling_params, "Missing min in scaling parameters"
        assert "max" in scaling_params, "Missing max in scaling parameters"
        assert (
            "feature_range" in scaling_params
        ), "Missing feature_range in scaling parameters"

        # Check if scaling can be reversed
        min_val, max_val = scaling_params["min"], scaling_params["max"]
        feature_min, feature_max = scaling_params["feature_range"]
        X_descaled = ((X_scaled - feature_min) / (feature_max - feature_min)) * (
            max_val - min_val
        ) + min_val
        assert np.allclose(X, X_descaled), "Descaled data should match original data"

    def test_handle_missing_values(self, data_with_missing):
        """Test handling missing values in the data."""
        X = data_with_missing

        # Count missing values before handling
        missing_before = np.isnan(X).sum()
        assert missing_before > 0, "Test data should have missing values"

        # Handle missing values with mean imputation
        X_imputed = handle_missing_values(X, strategy="mean")

        # Check if all missing values are handled
        missing_after = np.isnan(X_imputed).sum()
        assert missing_after == 0, "There should be no missing values after imputation"

        # Handle missing values with median imputation
        X_imputed_median = handle_missing_values(X, strategy="median")

        # Check if all missing values are handled
        missing_after_median = np.isnan(X_imputed_median).sum()
        assert (
            missing_after_median == 0
        ), "There should be no missing values after median imputation"

    def test_train_test_split_with_indices(self, sample_data):
        """Test train-test split with index tracking."""
        X = sample_data
        y = np.random.rand(X.shape[0])

        # Split data with 80% train, 20% test
        (
            X_train,
            X_test,
            y_train,
            y_test,
            train_indices,
            test_indices,
        ) = train_test_split_with_indices(X, y, test_size=0.2, random_state=42)

        # Check if shapes are correct
        assert X_train.shape[0] == int(0.8 * X.shape[0]), "Training set size incorrect"
        assert X_test.shape[0] == int(0.2 * X.shape[0]), "Test set size incorrect"
        assert y_train.shape[0] == X_train.shape[0], "y_train size should match X_train"
        assert y_test.shape[0] == X_test.shape[0], "y_test size should match X_test"

        # Check if indices are within bounds
        assert np.all(train_indices < X.shape[0]), "Train indices out of bounds"
        assert np.all(test_indices < X.shape[0]), "Test indices out of bounds"

        # Check if indices are non-overlapping
        assert (
            len(np.intersect1d(train_indices, test_indices)) == 0
        ), "Train and test indices should not overlap"

        # Check if indices can reconstruct original data
        X_train_from_indices = X[train_indices]
        X_test_from_indices = X[test_indices]

        assert np.array_equal(
            X_train, X_train_from_indices
        ), "X_train should match data from train indices"
        assert np.array_equal(
            X_test, X_test_from_indices
        ), "X_test should match data from test indices"
