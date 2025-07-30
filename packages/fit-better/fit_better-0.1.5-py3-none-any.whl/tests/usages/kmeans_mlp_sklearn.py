import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set OpenBLAS thread limit to prevent segmentation faults
# This should be done before importing scikit-learn
import os

# Limit OpenBLAS to use a reasonable number of threads
os.environ["OMP_NUM_THREADS"] = "4"  # Limit OpenMP threads
os.environ["OPENBLAS_NUM_THREADS"] = "4"  # Limit OpenBLAS threads
os.environ["MKL_NUM_THREADS"] = "4"  # Limit MKL threads if used
os.environ["NUMEXPR_NUM_THREADS"] = "4"  # Limit numexpr threads
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"  # Limit vecLib threads if on Mac

from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans, OPTICS
import xgboost as xgb
from datetime import datetime
import os
import gc
from collections import defaultdict
import joblib
import argparse
import traceback
import warnings
from joblib import Parallel, delayed
import tempfile
import pkg_resources

# Check if KMeans supports n_jobs parameter by testing it directly
SKLEARN_KMEANS_SUPPORTS_NJOBS = False
try:
    # Try to create a KMeans model with n_jobs parameter
    test_kmeans = KMeans(n_clusters=2, n_jobs=1)
    SKLEARN_KMEANS_SUPPORTS_NJOBS = True
except TypeError:
    # If we get a TypeError, n_jobs is not supported
    SKLEARN_KMEANS_SUPPORTS_NJOBS = False
    print(
        "Note: Your scikit-learn version does not support n_jobs parameter for KMeans."
    )

# Configure joblib's temporary folder to use a single location
# This helps prevent resource leaks when using parallel processing
temp_folder = os.path.join(tempfile.gettempdir(), "joblib_temp")
os.makedirs(temp_folder, exist_ok=True)

# Try to import tqdm for progress bars, but continue if not available
try:
    from tqdm import tqdm

    tqdm_available = True
except ImportError:
    tqdm_available = False
    print(
        "Warning: tqdm not available. Install with 'pip install tqdm' for progress bars."
    )

# Suppress sklearn feature name warnings
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="X does not have valid feature names, but .* was fitted with feature names",
)


def load_and_match_data(features_file, target_file):
    """
    Load features and target from separate CSV files
    and match by identifier in first column.
    Only keeps rows that exist in both files.

    Parameters:
    features_file (str): Path to CSV file containing features
    target_file (str): Path to CSV file containing target values

    Returns:
    tuple: (X, y, ids, target_col_name, original_features_df)
    """
    # Load data files
    features_df = pd.read_csv(features_file)
    target_df = pd.read_csv(target_file)

    # Store original features dataframe for later use
    original_features_df = features_df.copy()

    # Get column names for IDs
    id_col = features_df.columns[0]  # First column is identifier
    target_id_col = target_df.columns[0]  # First column in target file

    # Print information about the original datasets
    print(
        f"Features dataset: {features_df.shape[0]} rows, {features_df.shape[1]} columns"
    )
    print(f"Target dataset: {target_df.shape[0]} rows, {target_df.shape[1]} columns")

    # Ensure the ID columns have the same name for merging
    if target_id_col != id_col:
        print(f"Renaming ID column in target from '{target_id_col}' to '{id_col}'")
        target_df = target_df.rename(columns={target_id_col: id_col})

    # Merge dataframes on identifier column (inner join keeps only matching rows)
    merged_df = pd.merge(features_df, target_df, on=id_col, how="inner")

    # Calculate and print information about matching
    only_in_features = set(features_df[id_col]) - set(merged_df[id_col])
    only_in_target = set(target_df[id_col]) - set(merged_df[id_col])

    print(f"\nMatching complete:")
    print(f"  - IDs only in features file: {len(only_in_features)}")
    print(f"  - IDs only in target file: {len(only_in_target)}")
    print(f"  - Total matched rows: {merged_df.shape[0]}")

    # Check if there are any matched rows
    if merged_df.shape[0] == 0:
        raise ValueError("No matching rows found between feature and target files!")

    # Extract feature columns (all columns from features_df except the ID column)
    feature_columns = [col for col in features_df.columns if col != id_col]
    X = merged_df[feature_columns]

    # Extract target column(s)
    # Assuming the first column after ID in target_df is the target
    target_col_name = target_df.columns[1]
    y = merged_df[target_col_name]

    # Save the IDs of matched rows
    ids = merged_df[id_col]

    return X, y, ids, target_col_name, original_features_df


def load_comparison_data(additional_file, ids, id_col):
    """
    Load comparison data and match against existing IDs.

    Parameters:
    additional_file (str): Path to CSV file containing comparison values
    ids (Series): IDs from matched data
    id_col (str): Name of the ID column

    Returns:
    tuple: (comparison_values, comparison_col_name)
    """
    # Load additional data
    additional_df = pd.read_csv(additional_file)
    print(
        f"Additional dataset: {additional_df.shape[0]} rows, {additional_df.shape[1]} columns"
    )

    # Ensure the ID column has the same name
    additional_id_col = additional_df.columns[0]
    if additional_id_col != id_col:
        print(
            f"Renaming ID column in additional file from '{additional_id_col}' to '{id_col}'"
        )
        additional_df = additional_df.rename(columns={additional_id_col: id_col})

    # Create a dataframe with the matched IDs
    ids_df = pd.DataFrame({id_col: ids})

    # Merge with additional data
    merged_df = pd.merge(ids_df, additional_df, on=id_col, how="left")

    # Calculate matching statistics
    matched_ids = set(ids) & set(additional_df[id_col])
    only_in_additional = set(additional_df[id_col]) - set(ids)
    missing_in_additional = set(ids) - set(additional_df[id_col])

    print(f"\nAdditional data matching:")
    print(f"  - IDs matched with additional file: {len(matched_ids)}")
    print(f"  - IDs only in additional file: {len(only_in_additional)}")
    print(f"  - IDs missing from additional file: {len(missing_in_additional)}")

    # Extract comparison column (assuming the first column after ID)
    comparison_col_name = additional_df.columns[1]
    comparison_values = merged_df[comparison_col_name]

    # If additional_df has more than 2 columns, print a warning
    if len(additional_df.columns) > 2:
        print(
            f"Warning: Additional file has multiple columns. Using '{comparison_col_name}' for comparison."
        )

    return comparison_values, comparison_col_name


def perform_clustering(
    X, n_clusters=3, method="kmeans", random_state=42, max_jobs=0, **kwargs
):
    """
    Perform clustering on the feature data.

    Parameters:
    X (DataFrame): Features
    n_clusters (int): Number of clusters (used for KMeans)
    method (str): Clustering method ('kmeans' or 'optics')
    random_state (int): Random seed for reproducibility
    max_jobs (int): Maximum number of parallel jobs (0 for auto-detect)
    **kwargs: Additional parameters for the clustering algorithm

    Returns:
    tuple: (clustering_model, cluster_labels, scaled_data, scaler)
    """
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if method.lower() == "optics":
        # Extract OPTICS-specific parameters from kwargs
        min_samples = kwargs.get("min_samples", 5)
        xi = kwargs.get("xi", 0.05)
        min_cluster_size = kwargs.get("min_cluster_size", 0.05)

        # Performance optimization for OPTICS
        # Calculate the optimal eps value to limit neighborhood searches (major speed improvement)
        from sklearn.neighbors import NearestNeighbors

        n_neighbors = min(
            min_samples * 2, len(X) - 1
        )  # Double min_samples for better estimation
        nbrs = NearestNeighbors(n_neighbors=n_neighbors).fit(X_scaled)
        distances, _ = nbrs.kneighbors(X_scaled)
        # Use the mean distance to the nth neighbor as a heuristic for eps
        eps = np.mean(distances[:, -1]) * 1.5  # Multiply by a factor for safety margin

        # Specify algorithm='kd_tree' for better performance with euclidean distance
        # and specify max_eps to limit search radius

        # Determine optimal n_jobs
        n_jobs_param = kwargs.get("n_jobs", -1)  # Default to all cores
        if max_jobs > 0:
            n_jobs_param = max_jobs

        print(
            f"Using OPTICS with eps={eps:.4f}, min_samples={min_samples}, n_jobs={n_jobs_param}"
        )

        # Check for data size and potentially use sample-based approach for very large datasets
        if len(X) > 10000:
            print(
                f"Large dataset detected ({len(X)} samples). Using optimized OPTICS approach."
            )

            # For very large datasets, consider a two-step approach:
            # 1. Run OPTICS on a sample of the data
            # 2. Use a nearest neighbor classifier to assign remaining points
            sample_size = min(5000, len(X) // 2)  # Cap at 5000 samples

            # Take a stratified sample if we have enough clusters from KMeans
            if n_clusters >= 2:
                # Run quick KMeans to get stratified sampling
                quick_kmeans = KMeans(
                    n_clusters=n_clusters,
                    n_init=1,
                    max_iter=20,
                    random_state=random_state,
                )
                quick_labels = quick_kmeans.fit_predict(X_scaled)

                # Stratified sampling from each quick cluster
                sample_indices = []
                for i in range(n_clusters):
                    cluster_indices = np.where(quick_labels == i)[0]
                    if len(cluster_indices) > 0:
                        cluster_sample_size = int(
                            sample_size * len(cluster_indices) / len(X)
                        )
                        if cluster_sample_size > 0:
                            cluster_sample = np.random.choice(
                                cluster_indices,
                                size=min(cluster_sample_size, len(cluster_indices)),
                                replace=False,
                            )
                            sample_indices.extend(cluster_sample)

                # Ensure we have enough samples
                if len(sample_indices) < sample_size // 2:
                    sample_indices = np.random.choice(
                        len(X), size=sample_size, replace=False
                    )
            else:
                # Simple random sampling if we don't have enough initial clusters
                sample_indices = np.random.choice(
                    len(X), size=sample_size, replace=False
                )

            # Run OPTICS on the sample
            X_sample = X_scaled[sample_indices]
            clustering_model = OPTICS(
                min_samples=min(
                    min_samples, len(X_sample) // 20
                ),  # Adjust for sample size
                xi=xi,
                min_cluster_size=min(min_cluster_size, 0.1),  # Adjust for sample size
                metric="euclidean",
                algorithm="kd_tree",  # More efficient for euclidean
                max_eps=eps,  # Limit search radius for better performance
                n_jobs=n_jobs_param,
            )

            sample_labels = clustering_model.fit_predict(X_sample)

            # If all points in sample are assigned to noise, create a single cluster
            if np.all(sample_labels == -1):
                print(
                    "Warning: OPTICS assigned all sampled points to noise. Creating a single cluster."
                )
                cluster_labels = np.zeros(len(X), dtype=int)
            else:
                # Assign remaining points using a quick nearest neighbor approach
                valid_sample_indices = np.where(sample_labels != -1)[0]
                if len(valid_sample_indices) > 0:
                    # Only use non-noise points as training data
                    X_train = X_sample[valid_sample_indices]
                    y_train = sample_labels[valid_sample_indices]

                    # Use a small k for efficiency
                    classifier = NearestNeighbors(
                        n_neighbors=1, algorithm="kd_tree", n_jobs=n_jobs_param
                    )
                    classifier.fit(X_train)

                    # Process remaining points in batches for memory efficiency
                    remaining_indices = np.setdiff1d(
                        np.arange(len(X_scaled)), sample_indices
                    )
                    batch_size = 1000
                    cluster_labels = np.zeros(len(X_scaled), dtype=int)

                    # Assign the sample points their original labels
                    for i, idx in enumerate(sample_indices):
                        cluster_labels[idx] = max(
                            0, sample_labels[i]
                        )  # Ensure no -1 labels

                    # Process remaining points in batches
                    for i in range(0, len(remaining_indices), batch_size):
                        batch_indices = remaining_indices[i : i + batch_size]
                        batch_data = X_scaled[batch_indices]

                        # Find nearest neighbor among valid sample points
                        distances, indices = classifier.kneighbors(batch_data)

                        # Assign the same label as the nearest neighbor
                        for j, (idx, nn_idx) in enumerate(
                            zip(batch_indices, indices.flatten())
                        ):
                            cluster_labels[idx] = y_train[nn_idx]
                else:
                    # All sample points are noise, create a single cluster
                    cluster_labels = np.zeros(len(X), dtype=int)
        else:
            # For smaller datasets, use standard OPTICS with optimized parameters
            clustering_model = OPTICS(
                min_samples=min_samples,
                xi=xi,
                min_cluster_size=min_cluster_size,
                metric="euclidean",
                algorithm="kd_tree",  # More efficient for euclidean
                max_eps=eps,  # Limit search radius for better performance
                n_jobs=n_jobs_param,
            )

            # Fit the model and get cluster labels
            cluster_labels = clustering_model.fit_predict(X_scaled)

            # If all points are assigned to noise (-1), create a single cluster
            if np.all(cluster_labels == -1):
                print(
                    "Warning: OPTICS assigned all points to noise. Creating a single cluster."
                )
                cluster_labels = np.zeros(len(X), dtype=int)

        # Remap cluster indices to be consecutive integers starting from 0
        # This ensures compatibility with the rest of the code
        unique_clusters = np.unique(cluster_labels)
        if -1 in unique_clusters:
            # Handle noise points (assigned to cluster -1)
            # Map noise points to a new cluster after all valid clusters
            valid_clusters = unique_clusters[unique_clusters != -1]
            new_max_label = len(valid_clusters)

            # Create mapping
            mapping = {-1: new_max_label}
            mapping.update({c: i for i, c in enumerate(valid_clusters)})

            # Apply mapping
            new_labels = np.array([mapping[label] for label in cluster_labels])
            cluster_labels = new_labels
    else:
        # Default to KMeans++
        # Perform k-means++ clustering
        n_jobs_param = -1  # Default to all cores
        if max_jobs > 0:
            n_jobs_param = max_jobs

        # Create KMeans model with appropriate parameters based on sklearn version
        kmeans_params = {
            "n_clusters": n_clusters,
            "init": "k-means++",  # Use k-means++ initialization
            "n_init": 10,
            "max_iter": 300,
            "random_state": random_state,
        }

        # Only add n_jobs parameter if the sklearn version supports it
        if SKLEARN_KMEANS_SUPPORTS_NJOBS:
            kmeans_params["n_jobs"] = n_jobs_param

        clustering_model = KMeans(**kmeans_params)

        # Fit the model and get cluster labels
        cluster_labels = clustering_model.fit_predict(X_scaled)

    # Print cluster sizes
    unique_labels, counts = np.unique(cluster_labels, return_counts=True)
    print("\nCluster sizes:")
    for label, count in zip(unique_labels, counts):
        print(f"  Cluster {label}: {count} samples ({count/len(X)*100:.1f}%)")

    # Return the clustering model, labels, scaled data, and scaler
    return clustering_model, cluster_labels, X_scaled, scaler


def train_regressor(
    X, y, regressor_type="mlp", test_size=0.2, random_state=42, max_jobs=0
):
    """
    Train a regressor model on the given data.

    Parameters:
    X (DataFrame or array): Features
    y (Series or array): Target values
    regressor_type (str): Type of regressor ('mlp', 'xgboost', or 'logistic')
    test_size (float): Proportion of data to use for testing
    random_state (int): Random seed for reproducibility
    max_jobs (int): Maximum number of parallel jobs (0 for auto-detect)

    Returns:
    tuple: (model, X_train, X_test, y_train, y_test, scaler, train_indices, test_indices)
    """
    # If X is already scaled, don't scale again
    is_already_scaled = isinstance(X, np.ndarray)

    # For very small datasets, use the entire dataset for training
    if len(X) < 10:
        test_size = 0.0

    # Split data into training and testing sets
    if test_size > 0:
        (
            X_train,
            X_test,
            y_train,
            y_test,
            train_indices,
            test_indices,
        ) = train_test_split(
            X, y, np.arange(len(X)), test_size=test_size, random_state=random_state
        )
    else:
        # Use all data for training
        X_train, y_train = X, y
        X_test, y_test = np.empty((0, X.shape[1])), np.empty(0)
        train_indices, test_indices = np.arange(len(X)), np.empty(0, dtype=int)

    if is_already_scaled:
        X_train_scaled = X_train
        X_test_scaled = X_test if test_size > 0 else np.empty((0, X_train.shape[1]))
        scaler = None
    else:
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = (
            scaler.transform(X_test)
            if test_size > 0
            else np.empty((0, X_train.shape[1]))
        )

    if regressor_type.lower() == "xgboost":
        # Configure XGBoost regressor
        if len(X) < 10:
            # For very small datasets, use simple model with more regularization
            model = xgb.XGBRegressor(
                n_estimators=50,
                max_depth=2,
                learning_rate=0.01,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=10,  # L1 regularization
                reg_lambda=10,  # L2 regularization
                random_state=random_state,
                n_jobs=1,
                verbosity=0,
            )
        else:
            # Standard configuration
            n_jobs_param = -1  # Default to all cores
            if max_jobs > 0:
                n_jobs_param = max_jobs

            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=1,
                reg_lambda=1,
                random_state=random_state,
                n_jobs=n_jobs_param,
                verbosity=0,
            )
    elif regressor_type.lower() == "logistic":
        # Configure Logistic Regression
        from sklearn.linear_model import LogisticRegression

        # Determine the appropriate n_jobs parameter
        n_jobs_param = -1  # Default to all cores
        if max_jobs > 0:
            n_jobs_param = max_jobs

        # For very small datasets, use stronger regularization
        if len(X) < 10:
            model = LogisticRegression(
                C=0.5,  # Stronger regularization
                solver="lbfgs",
                max_iter=200,
                multi_class="auto",
                penalty="l2",
                random_state=random_state,
                n_jobs=n_jobs_param,
                tol=1e-4,
            )
        else:
            # Configure model with appropriate parameters for larger datasets
            model = LogisticRegression(
                C=1.0,  # Inverse of regularization strength
                solver="lbfgs",  # Algorithm to use in the optimization
                max_iter=200,  # Maximum number of iterations
                multi_class="auto",  # Auto-detect binary/multi-class
                penalty="l2",  # L2 regularization
                random_state=random_state,
                n_jobs=n_jobs_param,
                tol=1e-4,  # Tolerance for stopping criteria
            )

        print("Using LogisticRegression classifier")
    else:
        # Default to MLPRegressor
        if len(X) < 10:
            # For very small datasets, use simpler model
            model = MLPRegressor(
                hidden_layer_sizes=(3,),  # Single small hidden layer
                activation="relu",
                solver="adam",
                alpha=0.01,  # Increase regularization
                batch_size="auto",
                learning_rate="adaptive",
                max_iter=2000,
                random_state=random_state,
                verbose=False,
            )
        else:
            # For larger datasets, use default complexity
            model = MLPRegressor(
                hidden_layer_sizes=(
                    100,
                    50,
                ),  # Two hidden layers with 100 and 50 neurons
                activation="relu",
                solver="adam",
                alpha=0.0001,
                batch_size="auto",
                learning_rate="adaptive",
                max_iter=1000,
                random_state=random_state,
                verbose=False,
            )

    # Train the model
    model.fit(X_train_scaled, y_train)

    return (
        model,
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test,
        scaler,
        train_indices,
        test_indices,
    )


def evaluate_model(model, X_test, y_test, prefix=""):
    """
    Evaluate model performance.

    Parameters:
    model: Trained model
    X_test: Test features
    y_test: True target values
    prefix: Optional prefix for printing (e.g., cluster name)

    Returns:
    dict: Performance metrics and predictions
    """
    if len(y_test) == 0:
        print(f"{prefix}No test samples available for evaluation")
        return {
            "mse": np.nan,
            "rmse": np.nan,
            "r2": np.nan,
            "pct_rel_error_lt_3pct": np.nan,
            "y_test": [],
            "y_pred": [],
        }

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred) if len(np.unique(y_test)) > 1 else np.nan

    # Calculate percentage of samples with relative error < 3%
    y_test_array = np.array(y_test)
    y_pred_array = np.array(y_pred)

    # Calculate relative error with handling for zero values
    abs_error = np.abs(y_test_array - y_pred_array)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel_error = abs_error / np.abs(y_test_array)
        # Replace infinity and NaN with a large number
        rel_error[~np.isfinite(rel_error)] = 1.0

    # Calculate percentage within threshold
    pct_within_3pct = np.mean(rel_error < 0.03) * 100

    # Print metrics
    print(f"{prefix}Model Performance:")
    print(f"{prefix}  Mean Squared Error: {mse:.4f}")
    print(f"{prefix}  Root Mean Squared Error: {rmse:.4f}")
    print(f"{prefix}  R² Score: {r2:.4f}")
    print(f"{prefix}  Percentage with Relative Error < 3%: {pct_within_3pct:.2f}%")

    return {
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "pct_rel_error_lt_3pct": pct_within_3pct,
        "y_test": y_test,
        "y_pred": y_pred,
    }


def predict_on_original_features(
    original_features_df,
    clustering_model,
    kmeans_scaler,
    cluster_models,
    id_col,
    target_col_name,
):
    """
    Make predictions on the original feature dataset using the trained models.

    Parameters:
    original_features_df (DataFrame): Original features dataframe
    clustering_model: Trained clustering model (KMeans or OPTICS)
    kmeans_scaler (StandardScaler): Scaler used for clustering
    cluster_models (dict): Dictionary of trained regressor models for each cluster
    id_col (str): Name of the ID column
    target_col_name (str): Name of the target column to predict

    Returns:
    DataFrame: Original features with predictions added
    """
    print("\nMaking predictions on original feature dataset...")

    # Create a copy of the original features DataFrame
    result_df = original_features_df.copy()

    # If the target column exists in the original features, use it
    # (this can happen when training on the same dataset)
    if target_col_name in original_features_df.columns:
        result_df[target_col_name] = original_features_df[target_col_name]

    # Extract features (all columns except ID)
    feature_cols = [col for col in original_features_df.columns if col != id_col]
    X_orig = original_features_df[feature_cols].values

    # Scale the features using the same scaler used for clustering
    X_orig_scaled = kmeans_scaler.transform(X_orig)

    # Predict clusters for each data point
    clusters = clustering_model.predict(X_orig_scaled)

    # Add cluster assignments to the result DataFrame
    result_df["Cluster"] = clusters

    # Initialize prediction column
    result_df[f"Predicted_{target_col_name}"] = np.nan

    # Make predictions for each cluster
    for cluster_idx, model in cluster_models.items():
        # Select data points in this cluster
        cluster_mask = clusters == cluster_idx
        if sum(cluster_mask) == 0:
            continue

        # Get features for this cluster
        X_cluster = X_orig_scaled[cluster_mask]

        # Make predictions
        y_pred_cluster = model.predict(X_cluster)

        # Store predictions in result DataFrame
        result_df.loc[cluster_mask, f"Predicted_{target_col_name}"] = y_pred_cluster

    # Count predictions made
    n_predicted = result_df[f"Predicted_{target_col_name}"].notna().sum()
    print(f"Made predictions for {n_predicted} out of {len(result_df)} samples")

    # Check for any missing predictions (could happen if a cluster had no model)
    n_missing = result_df[f"Predicted_{target_col_name}"].isna().sum()
    if n_missing > 0:
        print(
            f"Warning: {n_missing} samples have no predictions (possibly in clusters with too few training samples)"
        )

    return result_df


def plot_cluster_predictions(cluster_results, output_dir="cluster_plots"):
    """
    Create scatter plots of actual vs predicted values for each cluster.

    Parameters:
    cluster_results (dict): Dictionary of cluster results
    output_dir (str): Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create plot for each cluster
    for cluster_idx, results in cluster_results.items():
        if len(results["test"]["y_test"]) == 0:
            continue

        plt.figure(figsize=(10, 6))
        plt.scatter(results["test"]["y_test"], results["test"]["y_pred"], alpha=0.7)

        # Plot perfect prediction line
        min_val = min(min(results["test"]["y_test"]), min(results["test"]["y_pred"]))
        max_val = max(max(results["test"]["y_test"]), max(results["test"]["y_pred"]))
        plt.plot([min_val, max_val], [min_val, max_val], "r--")

        # Calculate percentage of samples with relative error < 3%
        y_test = np.array(results["test"]["y_test"])
        y_pred = np.array(results["test"]["y_pred"])

        # Calculate relative error with handling for zero values
        abs_error = np.abs(y_test - y_pred)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel_error = abs_error / np.abs(y_test)
            # Replace infinity and NaN with a large number
            rel_error[~np.isfinite(rel_error)] = 1.0

        # Calculate percentage within threshold
        pct_within_3pct = np.mean(rel_error < 0.03) * 100

        # Get existing r2 score
        r2 = results["test"]["r2"]

        # Add metrics annotation with more prominence
        plt.annotate(
            f"R² = {r2:.4f}\nPct Error < 3% = {pct_within_3pct:.2f}%",
            xy=(0.05, 0.95),
            xycoords="axes fraction",
            fontsize=12,
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.5", facecolor="white", alpha=0.8, edgecolor="gray"
            ),
            verticalalignment="top",
        )

        plt.xlabel("Actual Values")
        plt.ylabel("Predicted Values")
        plt.title(
            f"Cluster {cluster_idx}: Model Predictions vs Actual (Pct Error < 3%: {pct_within_3pct:.2f}%)"
        )
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/cluster_{cluster_idx}_predictions.png")
        plt.close()

    # Create overall plot combining all clusters
    all_y_test = []
    all_y_pred = []
    colors = ["b", "g", "r", "c", "m", "y", "k"]

    plt.figure(figsize=(12, 8))

    for i, (cluster_idx, results) in enumerate(cluster_results.items()):
        if len(results["test"]["y_test"]) == 0:
            continue

        color_idx = i % len(colors)

        # Calculate percentage of samples with relative error < 3%
        y_test = np.array(results["test"]["y_test"])
        y_pred = np.array(results["test"]["y_pred"])

        # Calculate relative error with handling for zero values
        abs_error = np.abs(y_test - y_pred)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel_error = abs_error / np.abs(y_test)
            # Replace infinity and NaN with a large number
            rel_error[~np.isfinite(rel_error)] = 1.0

        # Calculate percentage within threshold
        pct_within_3pct = np.mean(rel_error < 0.03) * 100

        plt.scatter(
            results["test"]["y_test"],
            results["test"]["y_pred"],
            alpha=0.7,
            color=colors[color_idx],
            label=f"Cluster {cluster_idx} (Pct<3%: {pct_within_3pct:.1f}%)",
        )

        all_y_test.extend(results["test"]["y_test"])
        all_y_pred.extend(results["test"]["y_pred"])

    # Plot perfect prediction line
    if all_y_test and all_y_pred:
        min_val = min(min(all_y_test), min(all_y_pred))
        max_val = max(max(all_y_test), max(all_y_pred))
        plt.plot([min_val, max_val], [min_val, max_val], "r--")

        # Calculate overall R²
        overall_r2 = r2_score(all_y_test, all_y_pred)

        # Calculate percentage of samples with relative error < 3%
        y_test_array = np.array(all_y_test)
        y_pred_array = np.array(all_y_pred)

        # Calculate relative error with handling for zero values
        abs_error = np.abs(y_test_array - y_pred_array)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel_error = abs_error / np.abs(y_test_array)
            # Replace infinity and NaN with a large number
            rel_error[~np.isfinite(rel_error)] = 1.0

        # Calculate percentage within threshold
        overall_pct_within_3pct = np.mean(rel_error < 0.03) * 100

        plt.text(
            0.05,
            0.95,
            f"Overall R² = {overall_r2:.4f}\nPct Error < 3% = {overall_pct_within_3pct:.2f}%",
            transform=plt.gca().transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.7),
        )

    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title(
        "All Clusters: Model Predictions vs Actual (Pct Error < 3%: {:.2f}%)".format(
            overall_pct_within_3pct
        )
    )
    plt.grid(True)
    plt.legend(title="Cluster (Pct Error < 3%)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/all_clusters_predictions.png")
    plt.close()


def make_cluster_predictions_and_compare(
    cluster_models,
    cluster_data,
    comparison_values,
    ids,
    target_col_name,
    comparison_col_name,
):
    """
    Make predictions for each cluster and compare with values from additional file.

    Parameters:
    cluster_models (dict): Dictionary of trained models for each cluster
    cluster_data (dict): Dictionary of data for each cluster
    comparison_values (Series): Values from additional file to compare with
    ids (Series): IDs for all data
    target_col_name (str): Name of the target column
    comparison_col_name (str): Name of the comparison column

    Returns:
    DataFrame: Results with predictions and comparisons
    """
    # Create dataframe to store results
    results_df = pd.DataFrame(
        {
            ids.name: ids,
            f"Actual_{target_col_name}": cluster_data["all"]["y"],
            f"Cluster": cluster_data["all"]["cluster_labels"],
        }
    )

    # Add comparison values if available
    if comparison_values is not None:
        results_df[f"Compare_{comparison_col_name}"] = comparison_values

    # Make predictions for each cluster
    for cluster_idx, model in cluster_models.items():
        # Get data for this cluster
        cluster_mask = cluster_data["all"]["cluster_labels"] == cluster_idx
        if sum(cluster_mask) == 0:
            continue

        # Get features for this cluster
        X_cluster = cluster_data["all"]["X_scaled"][cluster_mask]

        # Make predictions
        y_pred_cluster = model.predict(X_cluster)

        # Store predictions in results dataframe
        results_df.loc[cluster_mask, f"Predicted_{target_col_name}"] = y_pred_cluster

    # Calculate model error metrics
    results_df["Model_Absolute_Error"] = np.abs(
        results_df[f"Actual_{target_col_name}"]
        - results_df[f"Predicted_{target_col_name}"]
    )

    # Calculate percentage errors (handling zero values)
    with np.errstate(divide="ignore", invalid="ignore"):
        model_pct = (
            results_df["Model_Absolute_Error"] / results_df[f"Actual_{target_col_name}"]
        ) * 100

        # Replace infinities and NaNs
        results_df["Model_Percent_Error"] = np.where(
            np.isfinite(model_pct), model_pct, np.nan
        )

    # If comparison values are available, calculate comparison metrics
    if comparison_values is not None:
        results_df["Comparison_Absolute_Error"] = np.abs(
            results_df[f"Actual_{target_col_name}"]
            - results_df[f"Compare_{comparison_col_name}"]
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            comp_pct = (
                results_df["Comparison_Absolute_Error"]
                / results_df[f"Actual_{target_col_name}"]
            ) * 100

            # Replace infinities and NaNs
            results_df["Comparison_Percent_Error"] = np.where(
                np.isfinite(comp_pct), comp_pct, np.nan
            )

        # Calculate performance metrics by cluster with comparison
        print("\nPerformance by Cluster:")
        print(
            f"{'Cluster':10} {'Model MSE':15} {'Comparison MSE':15} {'Model R²':15} {'Comparison R²':15}"
        )
        print(f"{'-'*70}")

        for cluster_idx in sorted(cluster_data["clusters"].keys()):
            cluster_mask = results_df[f"Cluster"] == cluster_idx
            if sum(cluster_mask) == 0:
                continue

            actual = results_df.loc[cluster_mask, f"Actual_{target_col_name}"]
            predicted = results_df.loc[cluster_mask, f"Predicted_{target_col_name}"]
            comparison = results_df.loc[cluster_mask, f"Compare_{comparison_col_name}"]

            model_mse = mean_squared_error(actual, predicted)
            comp_mse = mean_squared_error(actual, comparison)

            model_r2 = (
                r2_score(actual, predicted) if len(np.unique(actual)) > 1 else np.nan
            )
            comp_r2 = (
                r2_score(actual, comparison) if len(np.unique(actual)) > 1 else np.nan
            )

            print(
                f"{cluster_idx:10} {model_mse:15.4f} {comp_mse:15.4f} "
                f"{model_r2:15.4f} {comp_r2:15.4f}"
            )

        # Calculate overall metrics with comparison
        actual_all = results_df[f"Actual_{target_col_name}"]
        predicted_all = results_df[f"Predicted_{target_col_name}"]
        comparison_all = results_df[f"Compare_{comparison_col_name}"]

        model_mse_all = mean_squared_error(actual_all, predicted_all)
        comp_mse_all = mean_squared_error(actual_all, comparison_all)

        model_rmse_all = np.sqrt(model_mse_all)
        comp_rmse_all = np.sqrt(comp_mse_all)

        model_r2_all = r2_score(actual_all, predicted_all)
        comp_r2_all = r2_score(actual_all, comparison_all)

        print(f"\nOverall Performance:")
        print(f"{'':20} {'Model':15} {'Comparison Values':15} {'Difference':15}")
        print(f"{'-'*70}")
        print(
            f"{'MSE':20} {model_mse_all:.4f}{' '*(15-len(f'{model_mse_all:.4f}'))} "
            f"{comp_mse_all:.4f}{' '*(15-len(f'{comp_mse_all:.4f}'))} "
            f"{model_mse_all - comp_mse_all:.4f}"
        )

        print(
            f"{'RMSE':20} {model_rmse_all:.4f}{' '*(15-len(f'{model_rmse_all:.4f}'))} "
            f"{comp_rmse_all:.4f}{' '*(15-len(f'{comp_rmse_all:.4f}'))} "
            f"{model_rmse_all - comp_rmse_all:.4f}"
        )

        print(
            f"{'R²':20} {model_r2_all:.4f}{' '*(15-len(f'{model_r2_all:.4f}'))} "
            f"{comp_r2_all:.4f}{' '*(15-len(f'{comp_r2_all:.4f}'))} "
            f"{model_r2_all - comp_r2_all:.4f}"
        )

        metrics = {
            "model": {"mse": model_mse_all, "rmse": model_rmse_all, "r2": model_r2_all},
            "comparison": {
                "mse": comp_mse_all,
                "rmse": comp_rmse_all,
                "r2": comp_r2_all,
            },
        }
    else:
        # Calculate performance metrics by cluster without comparison
        print("\nPerformance by Cluster:")
        print(f"{'Cluster':10} {'Model MSE':15} {'Model R²':15}")
        print(f"{'-'*40}")

        for cluster_idx in sorted(cluster_data["clusters"].keys()):
            cluster_mask = results_df[f"Cluster"] == cluster_idx
            if sum(cluster_mask) == 0:
                continue

            actual = results_df.loc[cluster_mask, f"Actual_{target_col_name}"]
            predicted = results_df.loc[cluster_mask, f"Predicted_{target_col_name}"]

            model_mse = mean_squared_error(actual, predicted)
            model_r2 = (
                r2_score(actual, predicted) if len(np.unique(actual)) > 1 else np.nan
            )

            print(f"{cluster_idx:10} {model_mse:15.4f} {model_r2:15.4f}")

        # Calculate overall metrics without comparison
        actual_all = results_df[f"Actual_{target_col_name}"]
        predicted_all = results_df[f"Predicted_{target_col_name}"]

        model_mse_all = mean_squared_error(actual_all, predicted_all)
        model_rmse_all = np.sqrt(model_mse_all)
        model_r2_all = r2_score(actual_all, predicted_all)

        print(f"\nOverall Performance:")
        print(f"{'':20} {'Model':15}")
        print(f"{'-'*35}")
        print(f"{'MSE':20} {model_mse_all:.4f}")
        print(f"{'RMSE':20} {model_rmse_all:.4f}")
        print(f"{'R²':20} {model_r2_all:.4f}")

        metrics = {
            "model": {"mse": model_mse_all, "rmse": model_rmse_all, "r2": model_r2_all},
            "comparison": None,
        }

    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"clustered_prediction_results_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\nPrediction results saved to {output_file}")

    return results_df, metrics


def plot_comparison_by_cluster(
    results_df, target_col_name, comparison_col_name=None, output_dir="cluster_plots"
):
    """
    Create comparison plots for each cluster.

    Parameters:
    results_df (DataFrame): Results including predictions and comparison values
    target_col_name (str): Name of target column
    comparison_col_name (str, optional): Name of comparison column
    output_dir (str): Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get unique clusters
    clusters = sorted(results_df["Cluster"].unique())

    has_comparison = (
        comparison_col_name is not None
        and f"Compare_{comparison_col_name}" in results_df.columns
    )

    for cluster_idx in clusters:
        cluster_data = results_df[results_df["Cluster"] == cluster_idx]
        if len(cluster_data) == 0:
            continue

        actual = cluster_data[f"Actual_{target_col_name}"]
        predicted = cluster_data[f"Predicted_{target_col_name}"]

        # Determine how many plots to create
        n_plots = 3 if has_comparison else 1

        fig, axes = plt.subplots(1, n_plots, figsize=(n_plots * 6, 6))

        if n_plots == 1:
            # Single plot: Model vs Actual
            axes.scatter(actual, predicted, alpha=0.7, color="blue")
            min_val = min(min(actual), min(predicted))
            max_val = max(max(actual), max(predicted))
            axes.plot([min_val, max_val], [min_val, max_val], "r--")
            axes.set_xlabel("Actual Values")
            axes.set_ylabel("Model Predictions")
            axes.set_title(f"Cluster {cluster_idx}: Model vs Actual")
            axes.grid(True)
            r2_model = r2_score(actual, predicted)
            axes.text(
                0.05,
                0.95,
                f"R² = {r2_model:.4f}",
                transform=axes.transAxes,
                fontsize=12,
                verticalalignment="top",
            )
        else:
            # Three plots if comparison values are available
            comparison = cluster_data[f"Compare_{comparison_col_name}"]

            # Plot 1: Model vs Actual
            axes[0].scatter(actual, predicted, alpha=0.7, color="blue")
            min_val = min(min(actual), min(predicted))
            max_val = max(max(actual), max(predicted))
            axes[0].plot([min_val, max_val], [min_val, max_val], "r--")
            axes[0].set_xlabel("Actual Values")
            axes[0].set_ylabel("Model Predictions")
            axes[0].set_title(f"Cluster {cluster_idx}: Model vs Actual")
            axes[0].grid(True)
            r2_model = r2_score(actual, predicted)
            axes[0].text(
                0.05,
                0.95,
                f"R² = {r2_model:.4f}",
                transform=axes[0].transAxes,
                fontsize=12,
                verticalalignment="top",
            )

            # Plot 2: Comparison vs Actual
            axes[1].scatter(actual, comparison, alpha=0.7, color="green")
            min_val = min(min(actual), min(comparison))
            max_val = max(max(actual), max(comparison))
            axes[1].plot([min_val, max_val], [min_val, max_val], "r--")
            axes[1].set_xlabel("Actual Values")
            axes[1].set_ylabel(f"{comparison_col_name}")
            axes[1].set_title(f"Cluster {cluster_idx}: {comparison_col_name} vs Actual")
            axes[1].grid(True)
            r2_comp = r2_score(actual, comparison)
            axes[1].text(
                0.05,
                0.95,
                f"R² = {r2_comp:.4f}",
                transform=axes[1].transAxes,
                fontsize=12,
                verticalalignment="top",
            )

            # Plot 3: Model vs Comparison
            axes[2].scatter(comparison, predicted, alpha=0.7, color="purple")
            min_val = min(min(comparison), min(predicted))
            max_val = max(max(comparison), max(predicted))
            axes[2].plot([min_val, max_val], [min_val, max_val], "r--")
            axes[2].set_xlabel(f"{comparison_col_name}")
            axes[2].set_ylabel("Model Predictions")
            axes[2].set_title(f"Cluster {cluster_idx}: Model vs {comparison_col_name}")
            axes[2].grid(True)
            r2_model_comp = r2_score(comparison, predicted)
            axes[2].text(
                0.05,
                0.95,
                f"R² = {r2_model_comp:.4f}",
                transform=axes[2].transAxes,
                fontsize=12,
                verticalalignment="top",
            )

        fig.tight_layout()
        fig.savefig(f"{output_dir}/cluster_{cluster_idx}_comparisons.png")
        plt.close(fig)


def save_models(models, output_dir):
    """
    Save trained models to files.

    Parameters:
    models (dict): Dictionary of models to save
    output_dir (str): Directory to save models
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save clustering method info
    with open(f"{output_dir}/clustering_method.txt", "w") as f:
        f.write(models["clustering_method"])

    # Save regressor type info
    with open(f"{output_dir}/regressor_type.txt", "w") as f:
        f.write(models["regressor_type"])

    # Save clustering model
    joblib.dump(models["clustering_model"], f"{output_dir}/clustering_model.joblib")

    # Save scaler
    joblib.dump(models["kmeans_scaler"], f"{output_dir}/kmeans_scaler.joblib")

    # Save regressor models for each cluster
    cluster_models_dir = f"{output_dir}/cluster_models"
    os.makedirs(cluster_models_dir, exist_ok=True)

    for cluster_idx, model in models["cluster_models"].items():
        joblib.dump(
            model, f"{cluster_models_dir}/regressor_cluster_{cluster_idx}.joblib"
        )

    # Save cluster indices
    with open(f"{output_dir}/cluster_indices.txt", "w") as f:
        f.write(",".join(str(idx) for idx in models["cluster_models"].keys()))

    print(f"Models saved to {output_dir}")


def load_models(model_dir):
    """
    Load trained models from files.

    Parameters:
    model_dir (str): Directory containing saved models

    Returns:
    dict: Dictionary of loaded models
    """
    print(f"Loading models from {model_dir}")

    # Determine clustering method and regressor type
    clustering_method = "kmeans"  # Default for backward compatibility
    if os.path.exists(f"{model_dir}/clustering_method.txt"):
        with open(f"{model_dir}/clustering_method.txt", "r") as f:
            clustering_method = f.read().strip()

    regressor_type = "mlp"  # Default for backward compatibility
    if os.path.exists(f"{model_dir}/regressor_type.txt"):
        with open(f"{model_dir}/regressor_type.txt", "r") as f:
            regressor_type = f.read().strip()

    print(
        f"Model type: {clustering_method.upper()} clustering with {regressor_type.upper()} regressor"
    )

    # Load clustering model
    clustering_model_path = f"{model_dir}/clustering_model.joblib"
    # For backward compatibility
    if not os.path.exists(clustering_model_path) and os.path.exists(
        f"{model_dir}/kmeans_model.joblib"
    ):
        clustering_model_path = f"{model_dir}/kmeans_model.joblib"

    clustering_model = joblib.load(clustering_model_path)

    # Load scaler
    kmeans_scaler = joblib.load(f"{model_dir}/kmeans_scaler.joblib")

    # Load cluster indices
    with open(f"{model_dir}/cluster_indices.txt", "r") as f:
        content = f.read().strip()
        if content:
            cluster_indices = [int(idx) for idx in content.split(",")]
        else:
            # No cluster models were saved
            cluster_indices = []

    print(f"Found {len(cluster_indices)} cluster models")

    # Load regressor models for each cluster
    cluster_models = {}
    for cluster_idx in cluster_indices:
        # Try new naming convention first
        model_path = (
            f"{model_dir}/cluster_models/regressor_cluster_{cluster_idx}.joblib"
        )
        # If not found, try old naming convention
        if not os.path.exists(model_path):
            model_path = f"{model_dir}/cluster_models/mlp_cluster_{cluster_idx}.joblib"

        if os.path.exists(model_path):
            print(f"  Loading model for cluster {cluster_idx}")
            try:
                cluster_models[cluster_idx] = joblib.load(model_path)
            except Exception as e:
                print(f"  Error loading model for cluster {cluster_idx}: {str(e)}")

    print(f"Successfully loaded {len(cluster_models)} cluster models")

    return {
        "clustering_method": clustering_method,
        "clustering_model": clustering_model,
        "kmeans_scaler": kmeans_scaler,
        "regressor_type": regressor_type,
        "cluster_models": cluster_models,
    }


def process_batch(
    batch_df, feature_cols, clustering_model, kmeans_scaler, cluster_models
):
    """
    Process a batch of samples for prediction.

    Parameters:
    batch_df (DataFrame): Batch of data to process
    feature_cols (list): List of feature column names
    clustering_model: Trained clustering model
    kmeans_scaler (StandardScaler): Scaler used for clustering
    cluster_models (dict): Dictionary of trained regressor models for each cluster

    Returns:
    numpy.ndarray: Array of predictions
    """
    try:
        # Extract features for the batch
        X_batch = batch_df[feature_cols].values

        # Scale the features
        X_batch_scaled = kmeans_scaler.transform(X_batch)

        # Predict clusters for all samples in batch
        clusters = clustering_model.predict(X_batch_scaled)

        # Initialize predictions array
        batch_predictions = np.full(len(batch_df), np.nan)

        # Get unique clusters in this batch for more efficient processing
        unique_clusters = np.unique(clusters)

        # Process each cluster in the batch
        for cluster_idx in unique_clusters:
            if cluster_idx not in cluster_models:
                continue

            # Create mask for this cluster
            cluster_mask = clusters == cluster_idx

            # Skip if no samples in this cluster
            if not np.any(cluster_mask):
                continue

            # Get the model for this cluster
            model = cluster_models[cluster_idx]

            # Get samples for this cluster
            X_cluster = X_batch_scaled[cluster_mask]

            # Make predictions for this cluster (in one batch operation)
            cluster_preds = model.predict(X_cluster)

            # Assign predictions to the correct positions in the batch
            batch_predictions[cluster_mask] = cluster_preds

        return batch_predictions

    except Exception as e:
        print(f"Error processing batch: {str(e)}")
        return np.full(len(batch_df), np.nan)


def make_predictions(
    features_df,
    clustering_model,
    kmeans_scaler,
    cluster_models,
    id_col,
    batch_size=5000,
    n_jobs=None,
    max_jobs=0,
):
    """
    Make predictions on features using saved models.
    Process data in parallel batches to maximize speed.

    Parameters:
    features_df (DataFrame): Features dataframe
    clustering_model: Trained clustering model
    kmeans_scaler (StandardScaler): Scaler used for clustering
    cluster_models (dict): Dictionary of trained regressor models for each cluster
    id_col (str): Name of the ID column
    batch_size (int): Number of samples to process in each batch
    n_jobs (int): Number of parallel jobs to use (None for auto-detect)
    max_jobs (int): Maximum number of parallel jobs (0 for auto-detect)

    Returns:
    DataFrame: Predictions with IDs in the same format as the input
    """
    print("\nMaking predictions using loaded models...")

    # Extract features (all columns except ID)
    feature_cols = [col for col in features_df.columns if col != id_col]

    # Initialize an empty dataframe for results with the same ID column
    result_df = pd.DataFrame({id_col: features_df[id_col].copy(), "y_pred": np.nan})

    # Check if we have any trained models
    if not cluster_models:
        print(
            "Warning: No trained cluster models available. All predictions will be NaN."
        )
        return result_df

    # Get total samples
    n_samples = len(features_df)

    # Determine optimal batch size and number of jobs
    # For very large datasets, use smaller batches
    if n_samples > 100000:
        batch_size = min(batch_size, 2000)

    # Calculate number of batches
    num_batches = (n_samples + batch_size - 1) // batch_size

    print(
        f"Processing {n_samples} samples in {num_batches} batches of size {batch_size}"
    )

    # Determine the number of jobs for parallel processing if not specified
    if n_jobs is None:
        # Use fewer jobs for very large datasets to avoid memory issues
        available_jobs = min(
            joblib.cpu_count(), 4 if n_samples > 100000 else joblib.cpu_count()
        )
        # Apply max_jobs limit if specified
        if max_jobs > 0:
            n_jobs = min(available_jobs, max_jobs)
        else:
            n_jobs = available_jobs
    else:
        # If n_jobs is specified but max_jobs is also specified, take the minimum
        if max_jobs > 0:
            n_jobs = min(n_jobs, max_jobs)

    print(f"Using {n_jobs} parallel jobs")

    start_time = datetime.now()

    # Process batches in parallel
    predictions = np.full(n_samples, np.nan)

    try:
        # Split data into batches
        batches = [
            features_df.iloc[i : i + batch_size]
            for i in range(0, n_samples, batch_size)
        ]

        # Process batches in parallel with explicit memory management
        with Parallel(
            n_jobs=n_jobs, verbose=10, max_nbytes=None, temp_folder=temp_folder
        ) as parallel:
            batch_results = parallel(
                delayed(process_batch)(
                    batch, feature_cols, clustering_model, kmeans_scaler, cluster_models
                )
                for batch in batches
            )

        # Force garbage collection after parallel execution
        gc.collect()

        # Combine batch results
        for i, batch_pred in enumerate(batch_results):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, n_samples)
            predictions[start_idx:end_idx] = batch_pred

        # Clean up batch data
        del batches
        del batch_results

    except Exception as e:
        print(f"Error in parallel processing: {str(e)}")
        print("Falling back to sequential processing...")

        # Fallback to sequential processing if parallel fails
        for i in range(0, n_samples, batch_size):
            if i % (batch_size * 10) == 0:
                elapsed = datetime.now() - start_time
                progress = i / n_samples
                if progress > 0:
                    total_time = elapsed.total_seconds() / progress
                    remaining = total_time - elapsed.total_seconds()
                    print(
                        f"  Processing batch {i//batch_size + 1}/{num_batches} - "
                        f"{progress*100:.1f}% complete, "
                        f"est. remaining: {remaining//60:.0f}m {remaining%60:.0f}s"
                    )

            end_idx = min(i + batch_size, n_samples)
            batch_df = features_df.iloc[i:end_idx]
            batch_predictions = process_batch(
                batch_df, feature_cols, clustering_model, kmeans_scaler, cluster_models
            )
            predictions[i:end_idx] = batch_predictions

    # Transfer predictions to the result dataframe
    result_df["y_pred"] = predictions

    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    print(
        f"Prediction completed in {total_time:.1f} seconds "
        f"({n_samples/total_time:.1f} samples/second)"
    )

    # Count predictions made
    n_predicted = np.sum(~np.isnan(predictions))
    print(f"Made predictions for {n_predicted} out of {len(result_df)} samples")

    # Check for any missing predictions
    n_missing = np.sum(np.isnan(predictions))
    if n_missing > 0:
        print(
            f"Warning: {n_missing} samples have no predictions (possibly in clusters with no model)"
        )

    return result_df


def evaluate_predictions(
    y_pred_df,
    y_true_df,
    clustering_model=None,
    kmeans_scaler=None,
    feature_cols=None,
    features_df=None,
):
    """
    Evaluate predictions against true values.

    Parameters:
    y_pred_df (DataFrame): Predictions dataframe with IDs
    y_true_df (DataFrame): True values dataframe with IDs
    clustering_model (optional): Clustering model to assign clusters for per-cluster evaluation
    kmeans_scaler (StandardScaler, optional): Scaler used for clustering
    feature_cols (list, optional): List of feature columns
    features_df (DataFrame, optional): Features dataframe

    Returns:
    tuple: (metrics, merged_df, cluster_metrics)
    """
    # Get ID column names - we'll use the first column of each dataframe
    pred_id_col = y_pred_df.columns[0]
    true_id_col = y_true_df.columns[0]

    print(f"  - Predictions ID column: '{pred_id_col}'")
    print(f"  - True values ID column: '{true_id_col}'")

    # Only merge if the column names are different
    if true_id_col != pred_id_col:
        print(f"  - ID columns have different names, merging on values")
        # Create a copy with renamed column to avoid modifying the original
        y_true_df_copy = y_true_df.copy()
        y_true_df_copy.rename(columns={true_id_col: pred_id_col}, inplace=True)
        merged_df = pd.merge(y_pred_df, y_true_df_copy, on=pred_id_col, how="inner")
    else:
        # Directly merge if column names are the same
        merged_df = pd.merge(y_pred_df, y_true_df, on=pred_id_col, how="inner")

    print(f"\nEvaluation metrics:")
    print(f"  - Total predictions: {len(y_pred_df)}")
    print(f"  - Total true values: {len(y_true_df)}")
    print(f"  - Matched for evaluation: {len(merged_df)}")

    if len(merged_df) == 0:
        print("  - No matching IDs found for evaluation")
        return None, merged_df, None

    # Get true values column name (assuming it's the second column in y_true_df)
    y_true_col = y_true_df.columns[1]
    print(f"  - Using '{y_true_col}' as ground truth values")

    # Check for NaN values in predictions
    nan_mask = merged_df["y_pred"].isna()
    if nan_mask.any():
        print(
            f"  - Warning: {nan_mask.sum()} predictions are NaN and will be excluded from evaluation"
        )
        if nan_mask.all():
            print("  - All predictions are NaN, cannot calculate metrics")
            return None, merged_df, None

        # Filter out NaN predictions for evaluation
        eval_df = merged_df[~nan_mask].copy()
    else:
        eval_df = merged_df

    # Calculate metrics
    mse = mean_squared_error(eval_df[y_true_col], eval_df["y_pred"])
    rmse = np.sqrt(mse)
    r2 = r2_score(eval_df[y_true_col], eval_df["y_pred"])

    # Calculate additional error statistics
    error_stats = calculate_error_stats(eval_df[y_true_col], eval_df["y_pred"])

    print(f"  - Mean Squared Error: {mse:.4f}")
    print(f"  - Root Mean Squared Error: {rmse:.4f}")
    print(f"  - R² Score: {r2:.4f}")
    print(
        f"  - Percentage of samples with relative error < 3%: {error_stats['pct_rel_error_lt_3pct']:.2f}%"
    )
    print(f"  - Mean Absolute Error: {error_stats['mae']:.4f}")
    print(f"  - Mean Absolute Percentage Error: {error_stats['mape']:.2f}%")

    # Calculate per-cluster metrics if clustering model is provided
    cluster_metrics = None
    if (
        clustering_model is not None
        and kmeans_scaler is not None
        and feature_cols is not None
        and features_df is not None
    ):
        print("\nCalculating per-cluster evaluation metrics:")

        # Merge features with evaluation dataframe to get features for each evaluated sample
        eval_features_df = pd.merge(
            eval_df[[pred_id_col, "y_pred", y_true_col]],
            features_df,
            on=pred_id_col,
            how="inner",
        )

        # Extract features for clustering
        X_eval = eval_features_df[feature_cols].values

        # Scale features and assign clusters
        X_eval_scaled = kmeans_scaler.transform(X_eval)
        clusters = clustering_model.predict(X_eval_scaled)

        # Add cluster assignments to evaluation dataframe
        eval_df["cluster"] = np.nan
        eval_df.loc[
            eval_df[pred_id_col].isin(eval_features_df[pred_id_col]), "cluster"
        ] = clusters

        # Calculate metrics for each cluster
        cluster_metrics = {}
        unique_clusters = np.unique(clusters)

        print(f"  - Computing metrics for {len(unique_clusters)} clusters")
        for cluster_idx in unique_clusters:
            cluster_mask = eval_df["cluster"] == cluster_idx
            cluster_count = cluster_mask.sum()

            if cluster_count == 0:
                continue

            cluster_actual = eval_df.loc[cluster_mask, y_true_col]
            cluster_pred = eval_df.loc[cluster_mask, "y_pred"]

            cluster_mse = mean_squared_error(cluster_actual, cluster_pred)
            cluster_rmse = np.sqrt(cluster_mse)
            cluster_r2 = (
                r2_score(cluster_actual, cluster_pred)
                if len(np.unique(cluster_actual)) > 1
                else np.nan
            )

            print(
                f"  - Cluster {cluster_idx}: {cluster_count} samples, MSE={cluster_mse:.4f}, RMSE={cluster_rmse:.4f}, R²={cluster_r2:.4f}"
            )

            cluster_metrics[cluster_idx] = {
                "count": cluster_count,
                "mse": cluster_mse,
                "rmse": cluster_rmse,
                "r2": cluster_r2,
            }

    return (
        {
            "mse": mse,
            "rmse": rmse,
            "r2": r2,
            "pct_rel_error_lt_3pct": error_stats["pct_rel_error_lt_3pct"],
            "mae": error_stats["mae"],
            "mape": error_stats["mape"],
        },
        merged_df,
        cluster_metrics,
    )


def plot_prediction_clusters(
    merged_df, y_true_col, cluster_col="cluster", output_dir="."
):
    """
    Create a scatter plot of predictions vs true values, colored by cluster.

    Parameters:
    merged_df (DataFrame): DataFrame with predictions, true values and cluster assignments
    y_true_col (str): Column name for true values
    cluster_col (str): Column name for cluster assignments
    output_dir (str): Directory to save the plot
    """
    if cluster_col not in merged_df.columns or merged_df[cluster_col].isna().all():
        print("No cluster information available for visualization")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get unique clusters for coloring
    clusters = merged_df[cluster_col].dropna().unique()

    plt.figure(figsize=(12, 10))

    # Create a colormap with distinct colors
    colors = plt.cm.tab10(np.linspace(0, 1, len(clusters)))

    # Plot each cluster with a different color
    for i, cluster_idx in enumerate(clusters):
        mask = merged_df[cluster_col] == cluster_idx
        plt.scatter(
            merged_df.loc[mask, y_true_col],
            merged_df.loc[mask, "y_pred"],
            color=colors[i],
            alpha=0.7,
            label=f"Cluster {int(cluster_idx)}",
        )

    # Plot perfect prediction line
    min_val = min(merged_df[y_true_col].min(), merged_df["y_pred"].min())
    max_val = max(merged_df[y_true_col].max(), merged_df["y_pred"].max())
    plt.plot([min_val, max_val], [min_val, max_val], "k--", alpha=0.5)

    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title("Predictions vs Actual Values by Cluster")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Save the figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"cluster_predictions_{timestamp}.png")
    plt.savefig(filename)
    plt.close()

    print(f"Cluster prediction visualization saved to {filename}")


def generate_summary_report(
    metrics,
    n_clusters,
    output_dir,
    comparison_available=False,
    comparison_col_name=None,
    cluster_metrics=None,
):
    """
    Generate a summary report with key metrics.

    Parameters:
    metrics (dict): Performance metrics
    n_clusters (int): Number of clusters
    output_dir (str): Directory to save the report
    comparison_available (bool): Whether comparison values are available
    comparison_col_name (str, optional): Name of comparison column
    cluster_metrics (dict, optional): Per-cluster evaluation metrics
    """
    with open(f"{output_dir}/summary_report.txt", "w") as f:
        f.write(f"KMeans++ Clustering with MLPRegressor Models\n")
        f.write(f"=========================================\n\n")
        f.write(f"Analysis run on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write(f"Dataset Summary:\n")
        # Use sample count from metrics if cluster_data is not available
        f.write(f"- Number of clusters: {n_clusters}\n\n")

        f.write(f"Overall Performance:\n")
        f.write(f"- Model MSE: {metrics['model']['mse']:.4f}\n")
        f.write(f"- Model RMSE: {metrics['model']['rmse']:.4f}\n")
        f.write(f"- Model R²: {metrics['model']['r2']:.4f}\n")

        # Add the new statistics if available
        if "pct_rel_error_lt_3pct" in metrics["model"]:
            f.write(
                f"- Percentage of samples with relative error < 3%: {metrics['model']['pct_rel_error_lt_3pct']:.2f}%\n"
            )
        if "mae" in metrics["model"]:
            f.write(f"- Mean Absolute Error: {metrics['model']['mae']:.4f}\n")
        if "mape" in metrics["model"]:
            f.write(
                f"- Mean Absolute Percentage Error: {metrics['model']['mape']:.2f}%\n"
            )

        if comparison_available and metrics["comparison"] is not None:
            f.write(f"- Comparison MSE: {metrics['comparison']['mse']:.4f}\n")
            f.write(f"- Comparison RMSE: {metrics['comparison']['rmse']:.4f}\n")
            f.write(f"- Comparison R²: {metrics['comparison']['r2']:.4f}\n")
        f.write("\n")

        # Add per-cluster metrics if available
        if cluster_metrics:
            f.write("Per-Cluster Performance:\n")
            for cluster_idx, cluster_metric in sorted(cluster_metrics.items()):
                f.write(
                    f"- Cluster {cluster_idx} ({cluster_metric['count']} samples):\n"
                )
                f.write(f"  - MSE: {cluster_metric['mse']:.4f}\n")
                f.write(f"  - RMSE: {cluster_metric['rmse']:.4f}\n")
                f.write(f"  - R²: {cluster_metric['r2']:.4f}\n")


def predict_and_evaluate(
    features_file,
    target_file,
    model_dir,
    output_file="y_pred.csv",
    batch_size=5000,
    n_jobs=0,
    max_jobs=0,
):
    """
    Load models, make predictions on features file, and optionally evaluate against target file.

    Parameters:
    features_file (str): Path to features CSV file
    target_file (str): Path to target CSV file to evaluate against (optional)
    model_dir (str): Directory containing saved models
    output_file (str): Path to save predictions
    batch_size (int): Number of samples to process in each batch
    n_jobs (int): Number of parallel jobs (0 for auto-detect)
    max_jobs (int): Maximum number of parallel jobs (0 for auto-detect)
    """
    print(f"Loading models from {model_dir}")

    # Load models
    models = load_models(model_dir)

    # Get information about features without loading everything
    sample_df = pd.read_csv(features_file, nrows=5)
    feature_cols = [col for col in sample_df.columns if col != sample_df.columns[0]]
    id_col = sample_df.columns[0]

    # Count total rows
    total_rows = sum(1 for _ in open(features_file)) - 1  # subtract header

    print(f"Features file: {features_file}")
    print(f"  - Total rows: {total_rows}")
    print(f"  - ID column: '{id_col}'")
    print(f"  - Feature columns: {len(feature_cols)}")

    # Set optimal parameters for large datasets
    # Use larger chunks for reading
    chunk_size = min(batch_size * 4, 50000)

    # Override jobs if specified
    if n_jobs <= 0:
        # Auto-detect: use fewer jobs for very large datasets
        available_jobs = min(
            joblib.cpu_count(), 4 if total_rows > 100000 else joblib.cpu_count()
        )
        # Apply max_jobs limit if specified
        if max_jobs > 0:
            n_jobs = min(available_jobs, max_jobs)
        else:
            n_jobs = available_jobs
    else:
        # If n_jobs is specified but max_jobs is also specified, take the minimum
        if max_jobs > 0:
            n_jobs = min(n_jobs, max_jobs)

    print(f"Using {n_jobs} parallel jobs for prediction")
    print(f"Reading and processing data in chunks of {chunk_size} rows")
    print(f"Using batch size of {batch_size} for prediction")

    # Initialize results dataframe with the same ID column as input
    result_df = pd.DataFrame(columns=[id_col, "y_pred"])

    # Process in chunks
    chunk_reader = pd.read_csv(features_file, chunksize=chunk_size)

    # Calculate total number of chunks for progress reporting
    total_chunks = (total_rows + chunk_size - 1) // chunk_size

    print(f"Processing data in {total_chunks} chunks...")
    start_time = datetime.now()

    for chunk_idx, chunk in enumerate(chunk_reader):
        chunk_start = datetime.now()
        print(f"Processing chunk {chunk_idx+1}/{total_chunks}: {len(chunk)} rows")

        # Make predictions on this chunk
        chunk_results = make_predictions(
            chunk,
            models["clustering_model"],
            models["kmeans_scaler"],
            models["cluster_models"],
            id_col,
            batch_size=batch_size,
            n_jobs=n_jobs,
            max_jobs=max_jobs,
        )

        # Append to results, keeping the exact same ID column
        result_df = pd.concat([result_df, chunk_results], ignore_index=True)

        # Free memory
        del chunk, chunk_results

        # Force garbage collection
        gc.collect()

        # Force garbage collection
        import gc

        gc.collect()

        # Report progress
        chunk_time = datetime.now() - chunk_start
        elapsed = datetime.now() - start_time
        estimated_total = (elapsed.total_seconds() / (chunk_idx + 1)) * total_chunks
        remaining = estimated_total - elapsed.total_seconds()

        print(f"  Chunk {chunk_idx+1} completed in {chunk_time.total_seconds():.1f}s")
        print(f"  Progress: {(chunk_idx+1)/total_chunks*100:.1f}% complete")
        print(
            f"  Elapsed: {elapsed.total_seconds()//60:.0f}m {elapsed.total_seconds()%60:.0f}s"
        )
        print(f"  Estimated remaining: {remaining//60:.0f}m {remaining%60:.0f}s")

    # Save predictions using the exact same ID column from the input file
    print(f"Saving predictions to {output_file}...")
    result_df.to_csv(output_file, index=False)
    print(f"Predictions saved with {len(result_df)} rows to {output_file}")

    # If target file exists, evaluate predictions
    cluster_metrics = None
    if target_file and os.path.exists(target_file):
        print(f"Evaluating predictions against {target_file}")
        y_true_df = pd.read_csv(target_file)
        print(
            f"Loaded true values: {y_true_df.shape[0]} rows, {y_true_df.shape[1]} columns"
        )

        # Load a small batch of features for clustering
        features_sample = pd.read_csv(features_file)

        # Evaluate predictions and get per-cluster metrics
        metrics, merged_df, cluster_metrics = evaluate_predictions(
            result_df,
            y_true_df,
            clustering_model=models["clustering_model"],
            kmeans_scaler=models["kmeans_scaler"],
            feature_cols=feature_cols,
            features_df=features_sample,
        )

        if merged_df is not None and "cluster" in merged_df.columns:
            # Visualize predictions by cluster
            plot_prediction_clusters(
                merged_df,
                y_true_col=y_true_df.columns[1],
                output_dir=os.path.dirname(output_file) or ".",
            )

            # Create versus plot and save top 100 errors to CSV
            plot_top_errors(
                merged_df,
                actual_col=y_true_df.columns[1],
                pred_col="y_pred",
                id_col=result_df.columns[0],
                n=100,
                output_dir=os.path.dirname(output_file) or ".",
            )

        # Generate summary report with cluster metrics
        if metrics:
            n_clusters = len(models["cluster_models"])
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            report_path = os.path.join(
                os.path.dirname(output_file) or ".", "summary_report.txt"
            )

            generate_summary_report(
                {"model": metrics},
                n_clusters,
                os.path.dirname(output_file) or ".",
                cluster_metrics=cluster_metrics,
            )

            print(f"Summary report generated at {report_path}")


def train_models(
    features_file,
    target_file,
    output_dir,
    n_clusters=3,
    clustering_method="kmeans",
    regressor_type="mlp",
    random_state=42,
    max_jobs=0,
    **kwargs,
):
    """
    Train clustering models with regressors for each cluster.

    Parameters:
    features_file (str): Path to features CSV file
    target_file (str): Path to target CSV file
    output_dir (str): Directory to save models
    n_clusters (int): Number of clusters to create (used for KMeans)
    clustering_method (str): Method for clustering ('kmeans' or 'optics')
    regressor_type (str): Type of regressor to use ('mlp' or 'xgboost')
    random_state (int): Random seed for reproducibility
    max_jobs (int): Maximum number of parallel jobs (0 for auto-detect)
    **kwargs: Additional parameters for clustering algorithm

    Returns:
    dict: Dictionary containing trained models and related information
    """
    print(f"Training models using {features_file} and {target_file}")
    print(
        f"Clustering method: {clustering_method.upper()}, Regressor: {regressor_type.upper()}"
    )

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load and match data from features and target files
    start_time = datetime.now()
    print(f"Loading and matching data...")
    X, y, ids, target_col_name, original_features_df = load_and_match_data(
        features_file, target_file
    )

    n_samples, n_features = X.shape
    print(f"Loaded {n_samples} samples with {n_features} features")

    # Adjust clusters for small datasets
    if n_samples < 100:
        n_clusters = min(n_clusters, max(2, n_samples // 20))
        print(f"Small dataset detected, reducing to {n_clusters} clusters")

    if n_samples < 20:
        print(f"Dataset too small for effective clustering, using a single cluster")
        n_clusters = 1

    # Perform clustering
    print(f"\nPerforming {clustering_method.upper()} clustering...")

    # If max_jobs is specified, adjust the clustering parameters
    if max_jobs > 0:
        if clustering_method.lower() == "optics":
            kwargs["n_jobs"] = max_jobs
        else:
            # For KMeans, we'll set the n_jobs parameter when creating the model
            pass

    clustering_model, cluster_labels, X_scaled, scaler = perform_clustering(
        X,
        n_clusters=n_clusters,
        method=clustering_method,
        random_state=random_state,
        max_jobs=max_jobs,
        **kwargs,
    )

    # Train models for each cluster
    print(f"\nTraining {regressor_type.upper()} models for each cluster...")
    cluster_models = {}
    cluster_results = {}
    cluster_data = {
        "all": {"X": X, "y": y, "X_scaled": X_scaled, "cluster_labels": cluster_labels}
    }

    # Train a model for each cluster
    for cluster_idx in range(n_clusters):
        # Get data for this cluster
        cluster_mask = cluster_labels == cluster_idx
        cluster_size = sum(cluster_mask)

        print(f"\nTraining model for Cluster {cluster_idx} ({cluster_size} samples)")

        # Skip clusters with too few samples
        if cluster_size < 5:
            print(f"  Skipping Cluster {cluster_idx}: too few samples ({cluster_size})")
            continue

        # Get data for this cluster
        X_cluster = X_scaled[cluster_mask]
        y_cluster = y[cluster_mask]

        # Store cluster data for later use
        cluster_data[f"clusters"] = cluster_data.get("clusters", {})
        cluster_data["clusters"][cluster_idx] = {
            "X": X[cluster_mask],
            "y": y[cluster_mask],
            "X_scaled": X_cluster,
            "indices": np.where(cluster_mask)[0],
        }

        # Train model for this cluster
        (
            model,
            X_train,
            X_test,
            y_train,
            y_test,
            _,  # scaler not needed as X is already scaled
            train_indices,
            test_indices,
        ) = train_regressor(
            X_cluster,
            y_cluster,
            regressor_type=regressor_type,
            test_size=0.2,
            random_state=random_state,
            max_jobs=max_jobs,
        )

        # Store trained model
        cluster_models[cluster_idx] = model

        # Evaluate the model
        print(f"  Evaluating model for Cluster {cluster_idx}")
        train_results = evaluate_model(model, X_train, y_train, prefix="  Training ")
        test_results = evaluate_model(model, X_test, y_test, prefix="  Testing ")

        # Store results
        cluster_results[cluster_idx] = {
            "train": train_results,
            "test": test_results,
            "size": cluster_size,
        }

    # Save models
    models_to_save = {
        "clustering_method": clustering_method,
        "clustering_model": clustering_model,
        "kmeans_scaler": scaler,  # Keep name for backward compatibility
        "regressor_type": regressor_type,
        "cluster_models": cluster_models,
    }
    save_models(models_to_save, output_dir)

    # Create result plots directory
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Generate plots
    print("\nGenerating visualization plots...")
    plot_cluster_predictions(cluster_results, output_dir=plots_dir)

    # Make predictions on the full dataset for evaluation
    results_df = predict_on_original_features(
        original_features_df,
        clustering_model,
        scaler,
        cluster_models,
        ids.name,
        target_col_name,
    )

    # Create a versus plot and save top 100 errors to CSV
    if target_col_name in results_df.columns:
        plot_top_errors(
            results_df,
            actual_col=target_col_name,
            pred_col=f"Predicted_{target_col_name}",
            id_col=ids.name,
            n=100,
            output_dir=plots_dir,
        )

    # Save the worst 100 training predictions to a CSV file with features
    try:
        csv_file = save_worst_training_predictions(
            cluster_data,
            cluster_models,
            original_features_df,
            ids.name,
            target_col_name,
            n=100,
            output_dir=output_dir,
        )
        if csv_file:
            print(f"Successfully saved worst training predictions to {csv_file}")
    except Exception as e:
        print(f"Error saving worst training predictions: {str(e)}")
        traceback.print_exc()
        print("Continuing with training process despite the error...")

    # Save results
    results_file = os.path.join(output_dir, "training_predictions.csv")
    results_df.to_csv(results_file, index=False)
    print(f"\nSaved prediction results to {results_file}")

    # Calculate training time
    training_time = (datetime.now() - start_time).total_seconds()
    print(f"Training completed in {training_time:.1f} seconds")

    # Generate and save a summary report
    with open(f"{output_dir}/training_report.txt", "w") as f:
        f.write(f"Training Report\n")
        f.write(f"==============\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Data Summary:\n")
        f.write(f"- Features file: {features_file}\n")
        f.write(f"- Target file: {target_file}\n")
        f.write(f"- Samples: {n_samples}\n")
        f.write(f"- Features: {n_features}\n")
        f.write(f"- Clustering: {clustering_method.upper()}\n")
        f.write(f"- Number of clusters: {n_clusters}\n")
        f.write(f"- Regressor type: {regressor_type.upper()}\n")
        f.write(f"- Training time: {training_time:.1f} seconds\n")
        f.write(f"- Worst 100 training predictions saved to CSV\n")
        if max_jobs > 0:
            f.write(f"- Maximum parallel jobs: {max_jobs}\n")
        f.write(f"\n")

        # Calculate and add error statistics
        if (
            target_col_name in results_df.columns
            and f"Predicted_{target_col_name}" in results_df.columns
        ):
            error_stats = calculate_error_stats(
                results_df[target_col_name], results_df[f"Predicted_{target_col_name}"]
            )
            f.write(f"Error Statistics:\n")
            f.write(
                f"- Percentage of samples with relative error < 3%: {error_stats['pct_rel_error_lt_3pct']:.2f}%\n"
            )
            f.write(f"- Mean Absolute Error: {error_stats['mae']:.4f}\n")
            f.write(f"- Mean Absolute Percentage Error: {error_stats['mape']:.2f}%\n\n")

        f.write(f"Cluster Information:\n")
        for cluster_idx in sorted(cluster_results.keys()):
            size = cluster_results[cluster_idx]["size"]
            test_r2 = cluster_results[cluster_idx]["test"]["r2"]
            f.write(f"- Cluster {cluster_idx}: {size} samples, R² = {test_r2:.4f}\n")

    print(f"\nTraining complete. Models and visualizations saved to {output_dir}")

    return {
        "clustering_method": clustering_method,
        "clustering_model": clustering_model,
        "kmeans_scaler": scaler,
        "regressor_type": regressor_type,
        "cluster_models": cluster_models,
        "cluster_data": cluster_data,
        "cluster_results": cluster_results,
    }


def calculate_error_stats(actual, predicted, threshold=0.03):
    """
    Calculate error statistics including percentage of samples with relative error < threshold.

    Parameters:
    actual (array-like): Actual values
    predicted (array-like): Predicted values
    threshold (float): Threshold for relative error (default: 0.03 which is 3%)

    Returns:
    dict: Dictionary containing various error statistics
    """
    # Convert to numpy arrays
    actual = np.array(actual)
    predicted = np.array(predicted)

    # Calculate absolute error
    abs_error = np.abs(actual - predicted)

    # Calculate relative error with handling for zero values
    with np.errstate(divide="ignore", invalid="ignore"):
        rel_error = abs_error / np.abs(actual)
        # Replace infinity and NaN with a large number
        rel_error[~np.isfinite(rel_error)] = 1.0

    # Calculate percentage of samples with relative error < threshold
    pct_within_threshold = np.mean(rel_error < threshold) * 100

    # Calculate other statistics
    mae = np.mean(abs_error)
    mape = np.mean(rel_error) * 100  # Mean absolute percentage error

    return {
        f"pct_rel_error_lt_{int(threshold*100)}pct": pct_within_threshold,
        "mae": mae,
        "mape": mape,
        "rel_error": rel_error,
        "abs_error": abs_error,
    }


def plot_top_errors(results_df, actual_col, pred_col, id_col, n=100, output_dir="."):
    """
    Create a plot showing the top N samples with the highest relative errors.
    Also saves a CSV file with the details of these samples.

    Parameters:
    results_df (DataFrame): DataFrame with predictions and actual values
    actual_col (str): Column name for actual values
    pred_col (str): Column name for predicted values
    id_col (str): Column name for sample IDs
    n (int): Number of top errors to highlight (default: 100)
    output_dir (str): Directory to save the plot and CSV file

    Returns:
    str: Path to the saved CSV file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Copy the input dataframe to avoid modifying it
    df = results_df.copy()

    # Calculate relative error
    df["abs_error"] = np.abs(df[actual_col] - df[pred_col])
    with np.errstate(divide="ignore", invalid="ignore"):
        df["rel_error"] = df["abs_error"] / np.abs(df[actual_col])
        # Replace infinity and NaN with a large number
        df["rel_error"] = df["rel_error"].replace([np.inf, -np.inf, np.nan], 1.0)

    # Sort by relative error in descending order
    df_sorted = df.sort_values("rel_error", ascending=False)

    # Get the top N samples with highest relative errors
    top_errors = df_sorted.head(n)

    # Create a versus plot
    plt.figure(figsize=(12, 8))

    # Plot all points with low opacity
    plt.scatter(
        df[actual_col], df[pred_col], color="blue", alpha=0.2, label="All samples"
    )

    # Highlight the top N errors
    plt.scatter(
        top_errors[actual_col],
        top_errors[pred_col],
        color="red",
        alpha=0.8,
        label=f"Top {n} relative errors",
    )

    # Plot perfect prediction line
    min_val = min(df[actual_col].min(), df[pred_col].min())
    max_val = max(df[actual_col].max(), df[pred_col].max())
    plt.plot([min_val, max_val], "k--", alpha=0.5)

    # Add labels and title
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title(f"Top {n} Samples with Highest Relative Error")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Save the figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = os.path.join(output_dir, f"top_{n}_errors_{timestamp}.png")
    plt.savefig(plot_filename)
    plt.close()

    print(f"Plot of top {n} errors saved to {plot_filename}")

    # Save the details of these samples to a CSV file
    csv_filename = os.path.join(output_dir, f"top_{n}_errors_{timestamp}.csv")

    # Make sure to include all feature columns in the output
    top_errors_to_save = top_errors.copy()

    # Save to CSV with proper handling of header
    with open(csv_filename, "w", newline="") as f:
        # First write the header row
        header = ",".join(top_errors_to_save.columns) + "\n"
        f.write(header)
        # Then write the data without header
        top_errors_to_save.to_csv(f, index=False, header=False)

    print(f"Details of top {n} errors saved to {csv_filename}")

    return csv_filename


def save_worst_training_predictions(
    cluster_data,
    cluster_models,
    original_features_df,
    id_col,
    target_col_name,
    n=100,
    output_dir=".",
):
    """
    Save the worst 100 predictions from the training data to a CSV file.
    Uses a heap-based approach to maintain only the top N worst predictions across all clusters.

    Parameters:
    cluster_data (dict): Dictionary containing cluster data
    cluster_models (dict): Dictionary of trained models for each cluster
    original_features_df (DataFrame): Original features dataframe with all columns
    id_col (str): Column name for sample IDs
    target_col_name (str): Name of the target column
    n (int): Number of worst predictions to save (default: 100)
    output_dir (str): Directory to save the CSV file

    Returns:
    str: Path to the saved CSV file
    """
    print(f"\nFinding worst {n} training predictions...")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Print some diagnostic information about cluster indices
    print(f"Cluster models keys: {list(cluster_models.keys())}")
    if "clusters" in cluster_data:
        print(f"Cluster data keys: {list(cluster_data['clusters'].keys())}")

    # Initialize a min-heap to store the worst n predictions (using negative error for max-heap behavior)
    import heapq

    worst_predictions_heap = []
    total_processed = 0

    # For each cluster, get predictions on training data
    for cluster_idx, model in cluster_models.items():
        try:
            # Convert cluster_idx to ensure type consistency
            # Handle both string and integer cluster indices
            cluster_key = cluster_idx  # Keep original for accessing models

            # Get data for this cluster
            if (
                "clusters" not in cluster_data
                or cluster_key not in cluster_data["clusters"]
            ):
                print(f"Warning: No data found for cluster {cluster_idx}. Skipping.")
                continue

            # Get training data for this cluster
            cluster_info = cluster_data["clusters"][cluster_key]

            if (
                "X_scaled" not in cluster_info
                or "y" not in cluster_info
                or "indices" not in cluster_info
            ):
                print(
                    f"Warning: Missing required data for cluster {cluster_idx}. Skipping."
                )
                continue

            X_scaled = cluster_info["X_scaled"]
            y_true = cluster_info["y"]
            indices = cluster_info["indices"]

            # Convert pandas Series to numpy arrays for safer indexing
            if isinstance(y_true, pd.Series):
                print(
                    f"Converting y_true for cluster {cluster_idx} from pandas Series to numpy array"
                )
                y_true = y_true.values

            if len(indices) == 0 or len(X_scaled) == 0:
                print(f"Warning: Empty data for cluster {cluster_idx}. Skipping.")
                continue

            # Make predictions on training data
            y_pred = model.predict(X_scaled)

            # Print some debugging information
            print(
                f"Cluster {cluster_idx}: X_scaled shape: {X_scaled.shape}, y_true length: {len(y_true)}, y_pred length: {len(y_pred)}, indices length: {len(indices)}"
            )

            if len(y_pred) != len(y_true):
                print(
                    f"Warning: Prediction length mismatch for cluster {cluster_idx}. Expected {len(y_true)}, got {len(y_pred)}. Skipping."
                )
                continue

            # Make sure indices array doesn't contain any invalid indices
            valid_indices = np.where(indices < len(original_features_df))[0]
            if len(valid_indices) < len(indices):
                print(
                    f"Warning: Found {len(indices) - len(valid_indices)} invalid indices in cluster {cluster_idx}. Using only valid indices."
                )
                indices = indices[valid_indices]
                # Also subset y_true and y_pred accordingly if needed
                if len(valid_indices) < len(y_true):
                    y_true = y_true[valid_indices]
                    y_pred = y_pred[valid_indices]

            # Process each prediction in this cluster
            for i in range(len(indices)):
                idx = indices[i]

                # Check that the index is within the bounds of the original dataframe
                if idx >= len(original_features_df):
                    print(
                        f"Warning: Index {idx} is out of bounds for original features dataframe (size: {len(original_features_df)}). Skipping."
                    )
                    continue

                try:
                    sample_id = original_features_df.iloc[idx][id_col]

                    # Get all feature values for this sample
                    features = {}
                    for col in original_features_df.columns:
                        if col != id_col:
                            features[col] = original_features_df.iloc[idx][col]
                except Exception as e:
                    print(
                        f"Error accessing index {idx} in original features dataframe: {str(e)}. Skipping."
                    )
                    continue

                # Calculate error metrics
                try:
                    # Debug info
                    if i >= len(y_true):
                        print(
                            f"Error: Index {i} out of bounds for y_true (length: {len(y_true)}) in cluster {cluster_idx}"
                        )
                        continue
                    if i >= len(y_pred):
                        print(
                            f"Error: Index {i} out of bounds for y_pred (length: {len(y_pred)}) in cluster {cluster_idx}"
                        )
                        continue

                    true_val = y_true[i]
                    pred_val = y_pred[i]

                    abs_error = np.abs(true_val - pred_val)
                    rel_error = (
                        abs_error / np.abs(true_val) if true_val != 0 else float("inf")
                    )

                    # Create record
                    record = {
                        id_col: sample_id,
                        "Cluster": f"cluster_{cluster_idx}",  # More descriptive cluster label with consistent format
                        "Cluster_Index": cluster_idx,  # Preserve original cluster index without conversion
                        "True_Value": true_val,
                        "Predicted_Value": pred_val,
                        "Absolute_Error": abs_error,
                        "Relative_Error": rel_error,
                    }
                    # Add all feature values
                    record.update(features)

                    # Use the heap to maintain only the worst n predictions
                    # The heap stores tuples of (negative relative error, record index, record)
                    # Using negative error because heapq is a min-heap, but we want max errors
                    if len(worst_predictions_heap) < n:
                        # If we have fewer than n predictions, just add this one
                        heapq.heappush(
                            worst_predictions_heap,
                            (-rel_error, total_processed, record),
                        )
                    elif -rel_error < worst_predictions_heap[0][0]:
                        # If this error is worse than the smallest error in our heap, replace it
                        heapq.heappushpop(
                            worst_predictions_heap,
                            (-rel_error, total_processed, record),
                        )

                    total_processed += 1

                except Exception as e:
                    print(
                        f"Error processing prediction at index {i} in cluster {cluster_idx}: {str(e)}"
                    )
        except Exception as e:
            print(f"Error processing cluster {cluster_idx}: {str(e)}")
            traceback.print_exc()

    print(f"Processed {total_processed} predictions across all clusters")
    print(
        f"Collected the worst {len(worst_predictions_heap)} predictions based on relative error"
    )

    # Check if we have any data
    if not worst_predictions_heap:
        print(
            "Warning: No valid training predictions found. Skipping worst predictions export."
        )
        return None

    try:
        # Convert the heap to a sorted list of records (extract the record from each heap entry)
        sorted_records = [
            entry[2] for entry in sorted(worst_predictions_heap, key=lambda x: x[0])
        ]

        # Create DataFrame from the worst predictions
        worst_predictions = pd.DataFrame(sorted_records)

        # Replace infinity values with a large number for CSV export
        worst_predictions = worst_predictions.replace([np.inf, -np.inf], 1e10)

        # Rename feature columns to standardized format (feat1, feat2, etc.)
        feature_cols = [
            col
            for col in worst_predictions.columns
            if col
            not in [
                id_col,
                "Cluster",
                "Cluster_Index",
                "True_Value",
                "Predicted_Value",
                "Absolute_Error",
                "Relative_Error",
            ]
        ]

        # Create a mapping for column renaming
        rename_map = {}
        for i, col in enumerate(feature_cols):
            rename_map[col] = f"feat{i+1}"

        # Apply the renaming
        if rename_map:
            worst_predictions = worst_predictions.rename(columns=rename_map)
            print(
                f"Renamed {len(rename_map)} feature columns to standardized format (feat1, feat2, etc.)"
            )

        # Reorder columns to ensure important columns appear first
        important_cols = [
            id_col,
            "Cluster",
            "Cluster_Index",
            "True_Value",
            "Predicted_Value",
            "Absolute_Error",
            "Relative_Error",
        ]
        feature_cols = [
            col for col in worst_predictions.columns if col not in important_cols
        ]
        ordered_cols = important_cols + feature_cols
        worst_predictions = worst_predictions[ordered_cols]

        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(
            output_dir,
            f"worst_{len(worst_predictions)}_training_predictions_{timestamp}.csv",
        )
        worst_predictions.to_csv(csv_filename, index=False)

        print(
            f"Saved worst {len(worst_predictions)} training predictions to {csv_filename}"
        )
        print(f"Cluster distribution in worst predictions:")
        cluster_counts = worst_predictions["Cluster"].value_counts()
        for cluster, count in cluster_counts.items():
            print(f"  {cluster}: {count} samples")

        return csv_filename
    except Exception as e:
        print(f"Error during worst predictions processing: {str(e)}")
        traceback.print_exc()
        return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="KMeans++ clustering with MLPRegressor models"
    )

    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")

    # Train mode
    train_parser = subparsers.add_parser("train", help="Train models")
    train_parser.add_argument(
        "--features", required=True, help="Path to features CSV file"
    )
    train_parser.add_argument("--target", required=True, help="Path to target CSV file")
    train_parser.add_argument(
        "--output-dir", default="model", help="Directory to save models"
    )
    train_parser.add_argument(
        "--n-clusters",
        type=int,
        default=3,
        help="Number of clusters for KMeans (default: 3)",
    )
    train_parser.add_argument(
        "--clustering-method",
        choices=["kmeans", "optics"],
        default="kmeans",
        help="Clustering method to use (default: kmeans)",
    )
    train_parser.add_argument(
        "--regressor-type",
        choices=["mlp", "xgboost", "logistic"],
        default="mlp",
        help="Regressor type to use (default: mlp)",
    )
    train_parser.add_argument(
        "--min-samples",
        type=int,
        default=5,
        help="OPTICS min_samples parameter (default: 5)",
    )
    train_parser.add_argument(
        "--xi", type=float, default=0.05, help="OPTICS xi parameter (default: 0.05)"
    )
    train_parser.add_argument(
        "--min-cluster-size",
        type=float,
        default=0.05,
        help="OPTICS min_cluster_size parameter (default: 0.05)",
    )
    train_parser.add_argument(
        "--max-jobs",
        type=int,
        default=0,
        help="Maximum number of parallel jobs to use (0 for auto-detect, default is auto-detect)",
    )

    # Predict mode
    predict_parser = subparsers.add_parser("predict", help="Make predictions")
    predict_parser.add_argument(
        "--features", required=True, help="Path to features CSV file"
    )
    predict_parser.add_argument(
        "--target",
        required=False,
        help="Optional path to target CSV file for evaluation",
    )
    predict_parser.add_argument(
        "--model-dir", required=True, help="Directory containing saved models"
    )
    predict_parser.add_argument(
        "--output", default="y_pred.csv", help="Path to save predictions"
    )
    predict_parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Batch size for processing large datasets",
    )
    predict_parser.add_argument(
        "--jobs",
        type=int,
        default=0,
        help="Number of parallel jobs (0 for auto-detect, default is auto-detect)",
    )
    predict_parser.add_argument(
        "--max-jobs",
        type=int,
        default=0,
        help="Maximum number of parallel jobs to use (0 for auto-detect, default is auto-detect)",
    )

    args = parser.parse_args()

    try:
        # Run appropriate mode
        if args.mode == "train":
            # Prepare additional kwargs for clustering algorithms
            kwargs = {}
            if args.clustering_method == "optics":
                kwargs = {
                    "min_samples": args.min_samples,
                    "xi": args.xi,
                    "min_cluster_size": args.min_cluster_size,
                }
                if args.max_jobs > 0:
                    kwargs["n_jobs"] = args.max_jobs

            train_models(
                args.features,
                args.target,
                args.output_dir,
                n_clusters=args.n_clusters,
                clustering_method=args.clustering_method,
                regressor_type=args.regressor_type,
                max_jobs=args.max_jobs,
                **kwargs,
            )
        elif args.mode == "predict":
            predict_and_evaluate(
                args.features,
                args.target,
                args.model_dir,
                args.output,
                args.batch_size,
                args.jobs,
                args.max_jobs,
            )
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error during {args.mode} operation: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # Clean up temporary resources
        gc.collect()
        # Clean up joblib's temporary folder if it exists
        if os.path.exists(temp_folder):
            try:
                import shutil

                print("Cleaning up temporary joblib resources...")
                for item in os.listdir(temp_folder):
                    item_path = os.path.join(temp_folder, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.unlink(item_path)
                    except Exception as e:
                        print(f"Error cleaning up {item_path}: {e}")
            except Exception as e:
                print(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()
