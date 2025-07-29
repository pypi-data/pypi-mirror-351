"""
Unit tests for synthetic data generation.

This test suite validates:
- Linear data generation
- Sine data generation
- Polynomial data generation
- Complex data generation
- Train/test data splitting
- Custom noise levels
"""

import os
import sys
import pytest
import numpy as np

from fit_better.data.synthetic import (
    generate_synthetic_data_by_function,
    generate_train_test_data,
    add_noise,
    save_data,
)


@pytest.mark.unit
@pytest.mark.data
class TestSyntheticData:
    """Test suite for synthetic data generation functionality."""

    def test_linear_data_generation(self):
        """Test generating linear synthetic data."""
        # Generate data
        X, y = generate_synthetic_data_by_function(
            function_type="linear", n_samples=100, noise_std=0.5
        )

        # Check shapes
        assert X.shape == (100, 1), "X should have shape (100, 1)"
        assert y.shape == (100,), "y should have shape (100,)"

        # Check linear relationship
        # Extract a linear model from the data
        X_flat = X.flatten()
        A = np.vstack([X_flat, np.ones(len(X_flat))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]

        # Correlation coefficient should be high for linear data
        correlation = np.corrcoef(X_flat, y)[0, 1]
        assert correlation > 0.8, "Linear data should have high correlation coefficient"

    def test_sine_data_generation(self):
        """Test generating sine wave synthetic data."""
        # Generate data
        X, y = generate_synthetic_data_by_function(
            function_type="sine", n_samples=200, noise_std=0.5
        )

        # Check shapes
        assert X.shape == (200, 1), "X should have shape (200, 1)"
        assert y.shape == (200,), "y should have shape (200,)"

        # Check sine wave pattern
        # Fourier transform would be a proper test, but it's complex for a unit test
        # So we'll check for oscillation by looking at sign changes
        y_diff = np.diff(y)
        sign_changes = np.sum(np.diff(np.signbit(y_diff)))

        # Sine wave should have multiple sign changes
        assert sign_changes > 3, "Sine data should have multiple oscillations"

    def test_polynomial_data_generation(self):
        """Test generating polynomial synthetic data."""
        # Generate data
        X, y = generate_synthetic_data_by_function(
            function_type="polynomial", n_samples=100, noise_std=0.5
        )

        # Check shapes
        assert X.shape == (100, 1), "X should have shape (100, 1)"
        assert y.shape == (100,), "y should have shape (100,)"

        # Fit polynomial and check fit quality
        X_flat = X.flatten()
        coeffs = np.polyfit(X_flat, y, 2)  # Fit 2nd degree polynomial

        # Generate predictions from the fitted polynomial
        y_pred = np.polyval(coeffs, X_flat)

        # Calculate R-squared
        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)
        r_squared = 1 - (ss_residual / ss_total)

        # Polynomial should fit well with R² > 0.8
        assert r_squared > 0.8, "Polynomial fit should have high R²"

    def test_complex_data_generation(self):
        """Test generating complex synthetic data."""
        # Generate data
        X, y = generate_synthetic_data_by_function(
            function_type="complex", n_samples=150, noise_std=0.5
        )

        # Check shapes
        assert X.shape == (150, 1), "X should have shape (150, 1)"
        assert y.shape == (150,), "y should have shape (150,)"

        # Complex data should have low linear correlation
        X_flat = X.flatten()
        correlation = np.corrcoef(X_flat, y)[0, 1]

        # The correlation could be moderate or low depending on the complexity
        # This is more of a sanity check
        assert (
            -0.95 < correlation < 0.95
        ), "Complex data correlation should not be too extreme"

    def test_train_test_data_generation(self):
        """Test generating train and test datasets."""
        # Generate training and test data
        X_train, y_train, X_test, y_test = generate_train_test_data(
            function_type="linear",
            n_samples_train=150,
            n_samples_test=50,
            noise_std=0.5,
        )

        # Check shapes
        assert X_train.shape == (150, 1), "X_train should have shape (150, 1)"
        assert y_train.shape == (150,), "y_train should have shape (150,)"
        assert X_test.shape == (50, 1), "X_test should have shape (50, 1)"
        assert y_test.shape == (50,), "y_test should have shape (50,)"

        # Check that test data is different from training data
        X_train_set = set(tuple(map(float, x)) for x in X_train)
        X_test_set = set(tuple(map(float, x)) for x in X_test)
        intersection = X_train_set.intersection(X_test_set)

        # There shouldn't be many overlapping points (ideally none)
        assert len(intersection) < 5, "Training and test data should be mostly distinct"

    def test_noise_addition(self):
        """Test adding noise to data."""
        # Create clean data
        X = np.linspace(0, 10, 100).reshape(-1, 1)
        y_clean = 2 * X.flatten() + 3  # Linear function without noise

        # Add noise with different levels
        y_low_noise = add_noise(y_clean, noise_level=0.1)
        y_high_noise = add_noise(y_clean, noise_level=1.0)

        # Calculate standard deviations
        std_low = np.std(y_low_noise - y_clean)
        std_high = np.std(y_high_noise - y_clean)

        # Check that higher noise level results in higher standard deviation
        assert (
            std_high > std_low
        ), "Higher noise level should result in higher standard deviation"

        # Check that noise is zero-centered (mean close to zero)
        assert (
            abs(np.mean(y_low_noise - y_clean)) < 0.2
        ), "Noise should be approximately zero-centered"
        assert (
            abs(np.mean(y_high_noise - y_clean)) < 0.5
        ), "Noise should be approximately zero-centered"

    def test_data_saving(self, tmp_path):
        """Test saving synthetic data to files."""
        # Generate data
        X_train, y_train, X_test, y_test = generate_train_test_data(
            function_type="linear",
            n_samples_train=100,
            n_samples_test=30,
            noise_std=0.5,
        )

        # Save data
        paths = save_data(X_train, y_train, X_test, y_test, tmp_path)

        # Check that files exist
        assert os.path.exists(paths["X_train"]), "X_train output file should exist"
        assert os.path.exists(paths["y_train"]), "y_train output file should exist"
        assert os.path.exists(paths["X_test"]), "X_test output file should exist"
        assert os.path.exists(paths["y_test"]), "y_test output file should exist"

        # Load data and check consistency
        X_train_loaded = np.loadtxt(paths["X_train"]).reshape(
            -1, 1
        )  # Reshape to match original
        y_train_loaded = np.loadtxt(paths["y_train"])

        assert X_train_loaded.shape == (
            100,
            1,
        ), "Loaded X_train should have shape (100, 1)"
        assert y_train_loaded.shape == (100,), "Loaded y_train should have shape (100,)"
        assert np.allclose(
            X_train, X_train_loaded
        ), "Loaded X_train should match original"
        assert np.allclose(
            y_train, y_train_loaded
        ), "Loaded y_train should match original"

    def test_reproducibility(self):
        """Test that data generation is reproducible with seed."""
        # Generate data with seed
        X1, y1 = generate_synthetic_data_by_function(
            function_type="linear", n_samples=100, random_state=42
        )
        X2, y2 = generate_synthetic_data_by_function(
            function_type="linear", n_samples=100, random_state=42
        )

        # Check that data is identical
        assert np.array_equal(X1, X2), "Data with same seed should be identical"
        assert np.array_equal(y1, y2), "Data with same seed should be identical"

        # Generate data with different seed
        X3, y3 = generate_synthetic_data_by_function(
            function_type="linear", n_samples=100, random_state=43
        )

        # Check that data is different
        assert not np.array_equal(X1, X3), "Data with different seeds should differ"
