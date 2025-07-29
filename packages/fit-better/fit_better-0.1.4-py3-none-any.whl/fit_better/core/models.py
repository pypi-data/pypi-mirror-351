"""
Author: xlindo
Create Time: 2025-04-29
Description: Model fitting utilities for various regression algorithms and transformers.

Usage:
    from fit_better.core.models import fit_one_model, fit_all_regressors, select_best_model

    # Train all regressors on your data
    results = fit_all_regressors(X_train, y_train, n_jobs=4)

    # Select the best model based on MAE
    best_model = select_best_model(results, metric=Metric.MAE)

    # Train a specific regressor type
    results = fit_all_regressors(X_train, y_train, regressor_type=RegressorType.GRADIENT_BOOSTING)

This module provides utilities for training and evaluating regression models,
with support for parallel processing and diverse model types.
"""

# Standard library imports
import os
import logging
from importlib import import_module
from enum import Enum, auto

# Add import for our new logging utilities
from ..utils.logging_utils import get_logger, setup_worker_logging

# Create a module-level logger
logger = get_logger(__name__)

# Third-party imports
import numpy as np
from joblib import Parallel, delayed

# scikit-learn imports
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    HuberRegressor,
    Lasso,
    ElasticNet,
    LogisticRegression,
)
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
    BaggingRegressor,
)

# Conditional imports
try:
    from xgboost import XGBRegressor

    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMRegressor

    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False


class Metric(Enum):
    """Enum defining the different metrics for model evaluation."""

    MAE = "mae"
    RMSE = "rmse"
    MSE = "mse"
    R2 = "r2"
    PCT_WITHIN_1 = "pct_within_1pct"
    PCT_WITHIN_3 = "pct_within_3pct"
    PCT_WITHIN_5 = "pct_within_5pct"
    PCT_WITHIN_10 = "pct_within_10pct"
    PCT_WITHIN_20 = "pct_within_20pct"

    def __str__(self):
        return self.value


class RegressorType(Enum):
    """\n    Enum defining the types of regression algorithms available in `fit_better`.\n\n    Each member represents a specific regression model, primarily from scikit-learn,\n    XGBoost, or LightGBM. This enum provides a standardized way to specify and\n    instantiate regressors throughout the package.\n\n    The `create_regressor(regressor_type)` function can be used to get an instance\n    of the specified model with default parameters suitable for general use.\n    Users can further customize these models using scikit-learn's `set_params` method\n    or by directly instantiating them with desired parameters.\n\n    Attributes:\n        ALL: A special value used to indicate that all available regressors should be considered.\n             Not a specific model type itself.\n        LINEAR: Standard Ordinary Least Squares Linear Regression.\n            - Theory: Fits a linear model \(y = X\beta + c\) by minimizing the residual sum of squares\n              between the observed targets and the targets predicted by the linear approximation.\n            - Formula: \(\min_{\beta} ||X\beta - y||_2^2\)
    - Pros: Simple, interpretable, fast to train, no hyperparameters to tune.\n            - Cons: Assumes a linear relationship, sensitive to outliers, may underfit complex data.\n        POLYNOMIAL_2, POLYNOMIAL_3, POLYNOMIAL_4: Polynomial Regression of specified degree.\n            - Theory: Extends linear regression by adding polynomial terms of the features.\n              Transforms features \(x\) into \([x, x^2, ..., x^d]\) and then fits a linear model.\n            - Formula: \(y = \beta_0 + \beta_1 x + \beta_2 x^2 + ... + \beta_d x^d + \epsilon\)
    - Pros: Can model non-linear relationships, still relatively interpretable for low degrees.\n            - Cons: Prone to overfitting with high degrees, feature scaling is important, can be computationally intensive.\n        RIDGE: Ridge Regression (Linear Regression with L2 regularization).\n            - Theory: Adds a penalty equal to the square of the magnitude of coefficients to the loss function.\n              Shrinks coefficients and helps reduce model complexity and multicollinearity.\n            - Formula: \(\min_{\beta} ||X\beta - y||_2^2 + \alpha||eta||_2^2\)
    - Pros: Reduces overfitting, improves stability when features are correlated.\n            - Cons: Introduces bias, \(\alpha\) (regularization strength) needs tuning.\n        HUBER: Huber Regressor, robust to outliers.\n            - Theory: Combines aspects of MSE (for small errors) and MAE (for large errors) by using a quadratic loss for errors smaller\n              than a threshold \(\epsilon\) and linear loss for errors larger than \(\epsilon\).\n            - Pros: Less sensitive to outliers than OLS, provides a good balance between MSE and MAE.\n            - Cons: Requires tuning of \(\epsilon\), can be slower than OLS.\n        RANDOM_FOREST: Random Forest Regressor.\n            - Theory: An ensemble learning method that fits a number of decision tree regressors on various sub-samples of the dataset\n              and uses averaging to improve predictive accuracy and control overfitting.\n            - Pros: Powerful, handles non-linearities and interactions well, robust to outliers, requires less feature scaling.\n            - Cons: Less interpretable than linear models, can be computationally expensive, prone to overfitting on noisy data if not tuned.\n        LASSO: Lasso Regression (Linear Regression with L1 regularization).\n            - Theory: Adds a penalty equal to the absolute value of the magnitude of coefficients.\n              Can lead to sparse models where some feature coefficients become exactly zero.\n            - Formula: \(\min_{\beta} ||X\beta - y||_2^2 + \alpha||eta||_1\)
    - Pros: Performs feature selection by shrinking some coefficients to zero, helps with high-dimensional data.\n            - Cons: \(\alpha\) needs tuning, can be unstable with highly correlated features (may arbitrarily pick one).\n        ELASTIC_NET: ElasticNet Regression (Linear Regression with combined L1 and L2 regularization).\n            - Theory: Combines penalties from Lasso and Ridge regression.\n            - Formula: \(\min_{\beta} ||X\beta - y||_2^2 + \alpha \rho ||eta||_1 + \frac{\alpha(1-\rho)}{2} ||eta||_2^2\)
    - Pros: Combines benefits of Lasso (sparsity) and Ridge (stability with correlated features).\n            - Cons: Two hyperparameters (\(\alpha\) and \(\rho\)) to tune.\n        SVR_RBF: Support Vector Regression with Radial Basis Function (RBF) kernel.\n            - Theory: Finds a function that deviates from \(y\) by a value no greater than \(\epsilon\) for each training point,\n              and at the same time is as flat as possible. The RBF kernel allows modeling non-linear relationships.\n            - Pros: Effective in high-dimensional spaces, can model complex non-linearities.\n            - Cons: Computationally intensive, sensitive to hyperparameter choices (C, gamma, epsilon), less interpretable.\n        KNEIGHBORS: K-Neighbors Regressor.\n            - Theory: Predicts the target for a new data point based on the average target values of its k nearest neighbors in the feature space.\n            - Pros: Simple, non-parametric, can capture complex local relationships.\n            - Cons: Computationally expensive for large datasets, performance depends on distance metric and k, sensitive to irrelevant features (curse of dimensionality).\n        DECISION_TREE: Decision Tree Regressor.\n            - Theory: Builds a tree-like model of decisions. Each internal node represents a test on a feature, each branch represents an outcome, and each leaf node represents a target value (mean of samples in the leaf).\n            - Pros: Interpretable, handles non-linear data, requires little data preparation.\n            - Cons: Prone to overfitting (can be mitigated by pruning or ensemble methods), can be unstable (small changes in data can lead to different trees).\n        EXTRA_TREES: Extremely Randomized Trees Regressor.\n            - Theory: Similar to Random Forest, but randomness goes one step further in the way splits are computed. Thresholds are drawn at random for each candidate feature and the best of these randomly-generated thresholds is picked as the splitting rule.\n            - Pros: Generally faster to train than Random Forest, can reduce variance.\n            - Cons: May sometimes lead to slightly higher bias.\n        GRADIENT_BOOSTING: Gradient Boosting Regressor.\n            - Theory: An ensemble technique that builds models sequentially. Each new model attempts to correct the errors made by the previous ones.\n            - Pros: Highly accurate, can optimize various loss functions, handles complex data well.\n            - Cons: Prone to overfitting if not carefully tuned, can be slow to train due to sequential nature.\n        ADABOOST: AdaBoost Regressor.\n            - Theory: A boosting algorithm that fits a sequence of weak learners (e.g., decision trees) on repeatedly modified versions of the data. Predictions are combined through a weighted majority vote (or sum).\n            - Pros: Simple to implement, often performs well.\n            - Cons: Sensitive to noisy data and outliers.\n        BAGGING: Bagging Regressor.\n            - Theory: An ensemble method that fits base regressors each on random subsets of the original dataset (with replacement) and then aggregates their individual predictions (by averaging) to form a final prediction.\n            - Pros: Reduces variance, helps prevent overfitting.\n            - Cons: May not improve performance significantly if the base learner is already stable.\n        XGBOOST: XGBoost Regressor (Extreme Gradient Boosting).\n            - Theory: An optimized distributed gradient boosting library designed for speed and performance. Implements regularization and other advanced features.\n            - Pros: Highly efficient, state-of-the-art performance in many cases, handles missing values, built-in cross-validation.\n            - Cons: More hyperparameters to tune, can be complex.\n        LIGHTGBM: LightGBM Regressor (Light Gradient Boosting Machine).\n            - Theory: A gradient boosting framework that uses tree-based learning algorithms. It is designed to be distributed and efficient with faster training speed and lower memory usage.\n            - Pros: Very fast training, lower memory usage than XGBoost, good accuracy, supports categorical features directly.\n            - Cons: Can overfit on small datasets, sensitive to parameters.\n        LOGISTIC: Logistic Regression (classification algorithm, despite the name).\n            - Theory: Models the probability that an instance belongs to a particular class using the logistic function.\n              Particularly useful for binary classification tasks but can be extended to multi-class problems.\n            - Formula: \(P(y=1|X) = \frac{1}{1+e^{-(\beta_0 + \beta_1 x_1 + ... + \beta_n x_n)}}\)\n            - Pros: Interpretable, outputs probabilities, efficient to train, less prone to overfitting compared to complex models.\n            - Cons: Limited to linear decision boundaries, may underfit complex relationships, assumes features are independent.
    """

    ALL = "All Regressors"  # Special value to try all available regressors
    LINEAR = "Linear Regression"
    POLYNOMIAL_2 = "Polynomial Regression (deg=2)"
    POLYNOMIAL_3 = "Polynomial Regression (deg=3)"
    POLYNOMIAL_4 = "Polynomial Regression (deg=4)"
    RIDGE = "Ridge Regression"
    HUBER = "Huber Regressor"
    RANDOM_FOREST = "Random Forest Regression"
    LASSO = "Lasso Regression"
    ELASTIC_NET = "ElasticNet Regression"
    SVR_RBF = "SVR (RBF)"
    KNEIGHBORS = "KNeighbors Regressor"
    DECISION_TREE = "Decision Tree Regressor"
    EXTRA_TREES = "Extra Trees Regressor"
    GRADIENT_BOOSTING = "Gradient Boosting Regressor"
    ADABOOST = "AdaBoost Regressor"
    BAGGING = "Bagging Regressor"
    XGBOOST = "XGBoost Regressor"
    LIGHTGBM = "LightGBM Regressor"
    MLP = "MLP Regressor"
    LOGISTIC = "Logistic Regression"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, string_value):
        """Convert a string to the corresponding RegressorType enum.

        Args:
            string_value: String value to convert

        Returns:
            RegressorType enum value

        Raises:
            ValueError: If the string doesn't match any enum value
        """
        try:
            return cls(string_value)
        except ValueError:
            # Try a case-insensitive match on the enum names
            for enum_value in cls:
                if enum_value.name.lower().replace("_", " ") == string_value.lower():
                    return enum_value
            # If no match found, raise ValueError with available options
            valid_values = [f"{rt.name} ('{rt.value}')" for rt in cls]
            raise ValueError(
                f"Invalid regressor type: {string_value}. Valid values are: {valid_values}"
            )

    @classmethod
    def available_types(cls):
        """Return list of available regressor types, filtering out unavailable ones."""
        available = list(cls)
        # Always filter out the ALL type since it's a special case
        available = [r for r in available if r != cls.ALL]
        if not HAS_XGB:
            available = [r for r in available if r != cls.XGBOOST]
        if not HAS_LGBM:
            available = [r for r in available if r != cls.LIGHTGBM]
        return available


def _setup_subprocess_logging():
    """
    Configure logging for subprocesses by reading settings from environment variables.
    This ensures consistent logging across the main process and all worker processes.
    """
    # Use our centralized worker logging setup
    setup_worker_logging()


def _setup_worker_environment():
    """
    Set up environment variables that will be passed to worker processes.
    These variables allow worker processes to configure their logging correctly.
    """
    # Find the log file path from any existing file handler
    log_path = None
    for handler in logging.getLogger().handlers:
        if hasattr(handler, "baseFilename"):
            log_path = handler.baseFilename
            break

    # Set environment variables for worker processes
    if log_path:
        os.environ["LOG_PATH"] = log_path


def create_regressor(regressor_type):
    """
    Create and return a regressor instance with appropriate parameters based on type.

    Args:
        regressor_type: The RegressorType enum value

    Returns:
        An instance of the specified regressor with appropriate parameters
    """
    if regressor_type == RegressorType.LINEAR:
        return LinearRegression()
    elif regressor_type == RegressorType.RIDGE:
        return Ridge(alpha=1.0, random_state=42)
    elif regressor_type == RegressorType.HUBER:
        return HuberRegressor(epsilon=1.35)
    elif regressor_type == RegressorType.RANDOM_FOREST:
        return RandomForestRegressor(n_estimators=100, random_state=42)
    elif regressor_type == RegressorType.LASSO:
        return Lasso(alpha=0.1, random_state=42)
    elif regressor_type == RegressorType.ELASTIC_NET:
        return ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42)
    elif regressor_type == RegressorType.SVR_RBF:
        return SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)
    elif regressor_type == RegressorType.KNEIGHBORS:
        return KNeighborsRegressor(n_neighbors=5)
    elif regressor_type == RegressorType.DECISION_TREE:
        return DecisionTreeRegressor(random_state=42)
    elif regressor_type == RegressorType.EXTRA_TREES:
        return ExtraTreesRegressor(n_estimators=100, random_state=42)
    elif regressor_type == RegressorType.GRADIENT_BOOSTING:
        return GradientBoostingRegressor(n_estimators=100, random_state=42)
    elif regressor_type == RegressorType.ADABOOST:
        return AdaBoostRegressor(n_estimators=100, random_state=42)
    elif regressor_type == RegressorType.BAGGING:
        return BaggingRegressor(n_estimators=10, random_state=42)
    elif regressor_type == RegressorType.LOGISTIC:
        return LogisticRegression(
            C=1.0,  # Inverse of regularization strength (smaller value = stronger regularization)
            solver="lbfgs",  # Algorithm to use in the optimization problem
            max_iter=200,  # Maximum number of iterations
            multi_class="auto",  # Auto-detect whether the problem is binary or multi-class
            penalty="l2",  # L2 regularization
            random_state=42,  # For reproducible results
            n_jobs=-1,  # Use all available cores
            tol=1e-4,  # Tolerance for stopping criteria
        )
    elif regressor_type == RegressorType.MLP:
        return MLPRegressor(
            hidden_layer_sizes=(100, 50),  # Two hidden layers with 100 and 50 neurons
            activation="relu",  # ReLU activation function
            solver="adam",  # Adam optimizer
            alpha=0.0001,  # L2 regularization parameter
            batch_size="auto",  # Automatic batch size
            learning_rate="adaptive",  # Adaptive learning rate
            learning_rate_init=0.001,  # Initial learning rate
            max_iter=500,  # Maximum number of iterations
            tol=1e-4,  # Tolerance for optimization
            early_stopping=True,  # Use early stopping
            validation_fraction=0.1,  # Validation fraction for early stopping
            beta_1=0.9,
            beta_2=0.999,  # Adam parameters
            epsilon=1e-8,  # Adam parameter
            n_iter_no_change=10,  # Stop training if no improvement after 10 iterations
            random_state=42,  # Random state for reproducibility
        )
    elif regressor_type == RegressorType.XGBOOST and HAS_XGB:
        return XGBRegressor(n_estimators=100, random_state=42)
    elif regressor_type == RegressorType.LIGHTGBM and HAS_LGBM:
        # Configure LightGBM with parameters to reduce warnings and improve small partition handling
        return LGBMRegressor(
            n_estimators=100,
            min_child_samples=5,  # Reduce minimum samples in leaf nodes
            min_split_gain=0,  # Allow splits with minimal gain
            subsample=0.8,  # Use subsampling to reduce overfitting
            verbosity=-1,  # Reduce verbosity of output
            random_state=42,
            force_row_wise=True,  # Avoid auto-selection warnings
            feature_name="auto",  # Automatically handle feature names
        )
    else:
        # Default to LinearRegression if the type is not recognized
        logger.warning(
            f"Unknown regressor type: {regressor_type}, using LinearRegression"
        )
        return LinearRegression()


def fit_one_model(X, y, regressor_type, verbose=0):
    """
    Fit a single regressor model on the provided training data.

    Args:
        X (numpy.ndarray): Features array of shape (n_samples, n_features)
        y (numpy.ndarray): Target array of shape (n_samples,)
        regressor_type (RegressorType): Type of regressor to fit
        verbose (int, optional): Verbosity level (0=silent, 1=info). Defaults to 0.

    Returns:
        dict: Dictionary containing the fitted model and performance statistics
            {
                'model': fitted scikit-learn model,
                'model_name': string name of the model,
                'stats': {
                    'mae': mean absolute error,
                    'mse': mean squared error,
                    'rmse': root mean squared error,
                    'r2': R² score
                }
            }
    """
    if verbose > 0:
        logger.info(f"Fitting {regressor_type.value} regressor...")

    try:
        # Create the regressor instance
        model = create_regressor(regressor_type)

        # Fit the model to the training data
        model.fit(X, y)

        # Make predictions on the training data
        y_pred = model.predict(X)

        # Calculate performance metrics
        stats = {
            "mae": np.mean(np.abs(y_pred - y)),
            "mse": np.mean((y_pred - y) ** 2),
            "rmse": np.sqrt(np.mean((y_pred - y) ** 2)),
        }

        # Calculate R² score if possible (not always applicable, e.g., for classification)
        try:
            stats["r2"] = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        except:
            stats["r2"] = float("nan")

        return {"model": model, "model_name": regressor_type.value, "stats": stats}
    except Exception as e:
        if verbose > 0:
            logger.error(f"Error fitting {regressor_type.value}: {str(e)}")
        return None


def fit_all_regressors(X, y, n_jobs=1, regressor_type=None, verbose=0):
    """
    Fit multiple regressors on the provided training data.

    Args:
        X (numpy.ndarray): Features array of shape (n_samples, n_features)
        y (numpy.ndarray): Target array of shape (n_samples,)
        n_jobs (int, optional): Number of parallel jobs to run. Defaults to 1.
        regressor_type (RegressorType, optional): If specified, only fit this regressor type.
            If None, fit all available regressor types. Defaults to None.
        verbose (int, optional): Verbosity level (0=silent, 1=info). Defaults to 0.

    Returns:
        list: List of dictionaries, each containing a fitted model and performance statistics
    """
    if verbose > 0:
        logger.info(f"Fitting regressors with n_jobs={n_jobs}")

    # Determine which regressor types to fit
    regressor_types = []
    if regressor_type is None:
        # Use all available regressor types
        regressor_types = RegressorType.available_types()
    elif regressor_type == RegressorType.ALL:
        # Use all available regressor types
        regressor_types = RegressorType.available_types()
    else:
        # Use only the specified regressor type
        regressor_types = [regressor_type]

    if verbose > 0:
        logger.info(
            f"Will fit {len(regressor_types)} regressor types: {[rt.value for rt in regressor_types]}"
        )

    # Set up parallel processing if n_jobs != 1
    if n_jobs != 1:
        # Fit models in parallel
        results = Parallel(n_jobs=n_jobs, verbose=verbose)(
            delayed(_fit_model_worker)(X, y, rt, verbose) for rt in regressor_types
        )
    else:
        # Fit models sequentially
        results = [fit_one_model(X, y, rt, verbose) for rt in regressor_types]

    # Filter out any None results (failed model fits)
    results = [r for r in results if r is not None]

    if verbose > 0:
        logger.info(f"Successfully fitted {len(results)} regressors")

    return results


def _fit_model_worker(X, y, regressor_type, verbose=0):
    """
    Worker function for parallel model fitting to ensure proper logging.

    Args:
        X (numpy.ndarray): Features array
        y (numpy.ndarray): Target array
        regressor_type (RegressorType): Type of regressor to fit
        verbose (int, optional): Verbosity level. Defaults to 0.

    Returns:
        dict: Dictionary with fitted model and stats, or None if fitting failed
    """
    # Configure worker logging
    _setup_subprocess_logging()

    # Fit the model
    return fit_one_model(X, y, regressor_type, verbose)


def select_best_model(results, metric=Metric.MAE):
    """
    Select the best model from a list of fitted models based on the specified metric.

    Args:
        results (list): List of dictionaries, each containing a fitted model and performance statistics
        metric (Metric, optional): Metric to use for model selection. Defaults to Metric.MAE.

    Returns:
        dict: Dictionary containing the best model and its performance statistics
    """
    if not results:
        logger.warning("No models to select from")
        return None

    metric_name = metric.value

    # For R2, higher is better
    if metric == Metric.R2:
        best_idx = max(
            range(len(results)),
            key=lambda i: results[i]["stats"].get(metric_name, float("-inf")),
        )
    else:
        # For other metrics (MAE, MSE, RMSE), lower is better
        best_idx = min(
            range(len(results)),
            key=lambda i: results[i]["stats"].get(metric_name, float("inf")),
        )

    logger.info(
        f"Selected best model: {results[best_idx]['model_name']} with {metric_name}={results[best_idx]['stats'].get(metric_name):.4f}"
    )

    return results[best_idx]
