# Set OpenBLAS thread limit to prevent segmentation faults
# This should be done before importing scikit-learn
import os

# Limit OpenBLAS to use a reasonable number of threads
os.environ["OMP_NUM_THREADS"] = "4"  # Limit OpenMP threads
os.environ["OPENBLAS_NUM_THREADS"] = "4"  # Limit OpenBLAS threads
os.environ["MKL_NUM_THREADS"] = "4"  # Limit MKL threads if used
os.environ["NUMEXPR_NUM_THREADS"] = "4"  # Limit numexpr threads
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"  # Limit vecLib threads if on Mac

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KMeansRegressorPipeline:
    """
    A machine learning pipeline that combines KMeans++ clustering with regression models (XGBoost or MLP).
    """

    def __init__(
        self,
        n_clusters=3,
        random_state=42,
        min_samples_per_cluster=2,
        n_jobs=-1,
        regressor_type="xgboost",
    ):
        """
        Initialize the KMeans++ Regressor pipeline.

        Args:
            n_clusters (int): Number of clusters for KMeans++
            random_state (int): Random state for reproducibility
            min_samples_per_cluster (int): Minimum samples required per cluster to train regressor
            n_jobs (int): Number of parallel jobs for models (-1 uses all available cores)
            regressor_type (str): Type of regressor to use ('xgboost', 'mlp', or 'linear')
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.min_samples_per_cluster = min_samples_per_cluster
        self.n_jobs = n_jobs
        self.regressor_type = regressor_type.lower()

        if self.regressor_type not in ["xgboost", "mlp", "linear"]:
            raise ValueError("regressor_type must be 'xgboost', 'mlp', or 'linear'")

        self.kmeans = KMeans(
            n_clusters=n_clusters,
            init="k-means++",
            random_state=random_state,
            n_init=10,
        )
        self.scaler = StandardScaler()
        self.regressor_models = (
            {}
        )  # Dictionary to store regression models for each cluster
        self.is_fitted = False

    def load_csv_files(
        self, X_train_path, y_train_path, X_eval_path, y_eval_path, has_header=False
    ):
        """
        Load CSV files and match X-y pairs based on names in the first column.

        Args:
            X_train_path (str): Path to X_train.csv
            y_train_path (str): Path to y_train.csv
            X_eval_path (str): Path to X_eval.csv
            y_eval_path (str): Path to y_eval.csv
            has_header (bool): Whether CSV files have header row (default: False)

        Returns:
            tuple: (X_train, y_train, X_eval, y_eval) as pandas DataFrames
        """
        logger.info("Loading CSV files...")

        # Load CSV files with or without headers
        if has_header:
            X_train_df = pd.read_csv(X_train_path)
            y_train_df = pd.read_csv(y_train_path)
            X_eval_df = pd.read_csv(X_eval_path)
            y_eval_df = pd.read_csv(y_eval_path)
        else:
            # No headers - create generic column names
            X_train_df = pd.read_csv(X_train_path, header=None)
            y_train_df = pd.read_csv(y_train_path, header=None)
            X_eval_df = pd.read_csv(X_eval_path, header=None)
            y_eval_df = pd.read_csv(y_eval_path, header=None)

            # Create column names: first column is 'name', rest are features/targets
            n_features = X_train_df.shape[1] - 1
            n_targets = y_train_df.shape[1] - 1

            X_train_df.columns = ["name"] + [
                f"feature_{i+1}" for i in range(n_features)
            ]
            X_eval_df.columns = ["name"] + [f"feature_{i+1}" for i in range(n_features)]
            y_train_df.columns = ["name"] + [f"target_{i+1}" for i in range(n_targets)]
            y_eval_df.columns = ["name"] + [f"target_{i+1}" for i in range(n_targets)]

        logger.info(
            f"Loaded files - X_train: {X_train_df.shape}, y_train: {y_train_df.shape}"
        )
        logger.info(f"X_eval: {X_eval_df.shape}, y_eval: {y_eval_df.shape}")

        # Extract names (first column) and features/targets
        X_train_names = X_train_df.iloc[:, 0]
        X_train_features = X_train_df.iloc[:, 1:]

        y_train_names = y_train_df.iloc[:, 0]
        y_train_targets = y_train_df.iloc[:, 1:]

        X_eval_names = X_eval_df.iloc[:, 0]
        X_eval_features = X_eval_df.iloc[:, 1:]

        y_eval_names = y_eval_df.iloc[:, 0]
        y_eval_targets = y_eval_df.iloc[:, 1:]

        # Create temporary DataFrames for merging
        X_train_temp = pd.DataFrame(
            {
                "name": X_train_names,
                **{col: X_train_features[col] for col in X_train_features.columns},
            }
        )
        y_train_temp = pd.DataFrame(
            {
                "name": y_train_names,
                **{col: y_train_targets[col] for col in y_train_targets.columns},
            }
        )

        X_eval_temp = pd.DataFrame(
            {
                "name": X_eval_names,
                **{col: X_eval_features[col] for col in X_eval_features.columns},
            }
        )
        y_eval_temp = pd.DataFrame(
            {
                "name": y_eval_names,
                **{col: y_eval_targets[col] for col in y_eval_targets.columns},
            }
        )

        # Match X-y pairs for training data
        train_merged = pd.merge(X_train_temp, y_train_temp, on="name", how="inner")

        # Match X-y pairs for evaluation data
        eval_merged = pd.merge(X_eval_temp, y_eval_temp, on="name", how="inner")

        # Extract matched features and targets
        feature_cols = X_train_features.columns.tolist()
        target_cols = y_train_targets.columns.tolist()

        X_train_matched = train_merged[feature_cols]
        y_train_matched = train_merged[target_cols]

        X_eval_matched = eval_merged[feature_cols]
        y_eval_matched = eval_merged[target_cols]

        # Store names for later use
        self.train_names = train_merged["name"]
        self.eval_names = eval_merged["name"]

        logger.info(
            f"Matched data - Train: {X_train_matched.shape}, Eval: {X_eval_matched.shape}"
        )

        return X_train_matched, y_train_matched, X_eval_matched, y_eval_matched

    def fit(self, X_train, y_train):
        """
        Fit the KMeans++ clustering and regression models.

        Args:
            X_train (pd.DataFrame): Training features
            y_train (pd.DataFrame): Training targets
        """
        logger.info(f"Starting model training with {self.regressor_type} regressor...")

        # Convert to numpy arrays and handle target shape properly
        X_train_np = X_train.values
        if y_train.shape[1] == 1:
            y_train_np = y_train.values.ravel()
        else:
            # If multiple target columns, use the first one or handle accordingly
            y_train_np = y_train.iloc[:, 0].values

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_np)

        # Perform KMeans++ clustering
        logger.info(
            f"Performing KMeans++ clustering with {self.n_clusters} clusters..."
        )
        cluster_labels = self.kmeans.fit_predict(X_train_scaled)

        # Train regressor for each cluster
        for cluster_id in range(self.n_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_X = X_train_np[cluster_mask]
            cluster_y = y_train_np[cluster_mask]

            if (
                len(cluster_X) >= self.min_samples_per_cluster
            ):  # Only train if cluster has enough data points
                logger.info(
                    f"Training {self.regressor_type.upper()} for cluster {cluster_id} with {len(cluster_X)} samples"
                )

                if self.regressor_type == "xgboost":
                    model = xgb.XGBRegressor(
                        objective="reg:squarederror",
                        n_estimators=100,
                        max_depth=6,
                        learning_rate=0.1,
                        random_state=self.random_state,
                        n_jobs=self.n_jobs,
                        verbosity=0,  # Reduce XGBoost verbosity
                    )
                elif self.regressor_type == "mlp":
                    # Configure MLP based on cluster size to avoid early stopping issues
                    cluster_size = len(cluster_X)
                    if cluster_size < 20:
                        # Small cluster: disable early stopping, use simple architecture
                        model = MLPRegressor(
                            hidden_layer_sizes=(min(50, cluster_size * 2),),
                            activation="relu",
                            solver="adam",
                            alpha=0.001,  # Higher regularization for small datasets
                            max_iter=300,
                            random_state=self.random_state,
                            early_stopping=False,  # Disable to avoid validation issues
                        )
                    else:
                        # Larger cluster: use early stopping with appropriate validation fraction
                        val_fraction = min(
                            0.2, max(0.1, 10.0 / cluster_size)
                        )  # At least 10 samples for validation
                        model = MLPRegressor(
                            hidden_layer_sizes=(100, 50),
                            activation="relu",
                            solver="adam",
                            alpha=0.0001,
                            batch_size="auto",
                            learning_rate="constant",
                            learning_rate_init=0.001,
                            max_iter=500,
                            random_state=self.random_state,
                            early_stopping=True,
                            validation_fraction=val_fraction,
                            n_iter_no_change=10,
                        )
                elif self.regressor_type == "linear":
                    model = LinearRegression(
                        n_jobs=self.n_jobs if self.n_jobs != -1 else None
                    )

                model.fit(cluster_X, cluster_y)
                self.regressor_models[cluster_id] = model
            else:
                logger.warning(
                    f"Cluster {cluster_id} has only {len(cluster_X)} samples (minimum required: {self.min_samples_per_cluster})"
                )

        # If no models were trained, create a fallback model using all data
        if not self.regressor_models:
            logger.warning(
                "No clusters had enough samples. Training a single model on all data."
            )

            if self.regressor_type == "xgboost":
                fallback_model = xgb.XGBRegressor(
                    objective="reg:squarederror",
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=self.random_state,
                    n_jobs=self.n_jobs,
                    verbosity=0,
                )
            elif self.regressor_type == "mlp":
                fallback_model = MLPRegressor(
                    hidden_layer_sizes=(100, 50),
                    activation="relu",
                    solver="adam",
                    alpha=0.0001,
                    max_iter=500,
                    random_state=self.random_state,
                    early_stopping=False,  # Disable early stopping for fallback model
                )
            elif self.regressor_type == "linear":
                fallback_model = LinearRegression(
                    n_jobs=self.n_jobs if self.n_jobs != -1 else None
                )

            fallback_model.fit(X_train_np, y_train_np)
            self.regressor_models[0] = fallback_model  # Store as cluster 0

        self.is_fitted = True
        logger.info("Model training completed!")

    def predict(self, X_eval):
        """
        Make predictions on evaluation data.

        Args:
            X_eval (pd.DataFrame): Evaluation features

        Returns:
            np.ndarray: Predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        logger.info("Making predictions on evaluation data...")

        # Convert to numpy array and scale
        X_eval_np = X_eval.values
        X_eval_scaled = self.scaler.transform(X_eval_np)

        # Predict cluster assignments
        cluster_labels = self.kmeans.predict(X_eval_scaled)

        # Initialize predictions array
        predictions = np.zeros(len(X_eval_np))

        # Make predictions for each cluster
        for cluster_id in range(self.n_clusters):
            cluster_mask = cluster_labels == cluster_id

            if cluster_id in self.regressor_models and np.any(cluster_mask):
                cluster_X = X_eval_np[cluster_mask]
                cluster_predictions = self.regressor_models[cluster_id].predict(
                    cluster_X
                )
                predictions[cluster_mask] = cluster_predictions
            elif np.any(cluster_mask):
                # If no model for this cluster, use fallback prediction
                logger.warning(
                    f"No model for cluster {cluster_id}, using fallback prediction"
                )
                if "fallback" in self.regressor_models:
                    # Use the fallback model
                    cluster_X = X_eval_np[cluster_mask]
                    cluster_predictions = self.regressor_models["fallback"].predict(
                        cluster_X
                    )
                    predictions[cluster_mask] = cluster_predictions
                elif self.regressor_models:
                    # Use average prediction from available models
                    cluster_X = X_eval_np[cluster_mask]
                    fallback_predictions = []
                    for model in self.regressor_models.values():
                        if model != self.regressor_models.get("fallback"):
                            fallback_predictions.append(model.predict(cluster_X))
                    if fallback_predictions:
                        predictions[cluster_mask] = np.mean(
                            fallback_predictions, axis=0
                        )
                else:
                    # Last resort: use mean of training targets
                    logger.warning("No models available, using mean prediction")
                    predictions[cluster_mask] = 0  # Will be handled by calling code

        logger.info("Predictions completed!")
        return predictions

    def evaluate(self, y_true, y_pred, X_eval=None):
        """
        Evaluate model performance overall and per cluster.

        Args:
            y_true (np.ndarray): True values
            y_pred (np.ndarray): Predicted values
            X_eval (pd.DataFrame, optional): Evaluation features for cluster-wise analysis

        Returns:
            dict: Overall and cluster-wise evaluation metrics
        """
        # Overall metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        overall_metrics = {"MSE": mse, "RMSE": rmse, "MAE": mae, "R2": r2}

        results = {"overall": overall_metrics, "cluster_wise": {}}

        # Cluster-wise metrics if X_eval is provided
        if X_eval is not None and self.is_fitted:
            # Get cluster assignments for evaluation data
            X_eval_scaled = self.scaler.transform(X_eval.values)
            cluster_labels = self.kmeans.predict(X_eval_scaled)

            logger.info("Overall evaluation metrics:")
            for metric, value in overall_metrics.items():
                logger.info(f"  {metric}: {value:.4f}")

            logger.info("\nCluster-wise evaluation metrics:")

            for cluster_id in range(self.n_clusters):
                cluster_mask = cluster_labels == cluster_id

                if np.any(cluster_mask):
                    cluster_y_true = y_true[cluster_mask]
                    cluster_y_pred = y_pred[cluster_mask]

                    if (
                        len(cluster_y_true) >= 2
                    ):  # Need at least 2 samples for meaningful metrics
                        cluster_mse = mean_squared_error(cluster_y_true, cluster_y_pred)
                        cluster_rmse = np.sqrt(cluster_mse)
                        cluster_mae = mean_absolute_error(
                            cluster_y_true, cluster_y_pred
                        )

                        # Calculate R² only if we have enough variance in true values
                        y_var = np.var(cluster_y_true)
                        if (
                            y_var > 1e-10
                        ):  # Avoid division by zero or near-zero variance
                            cluster_r2 = r2_score(cluster_y_true, cluster_y_pred)
                        else:
                            cluster_r2 = np.nan  # Use NaN for undefined R²
                            logger.warning(
                                f"    Cluster {cluster_id}: R² undefined due to zero variance in true values"
                            )

                        cluster_metrics = {
                            "samples": len(cluster_y_true),
                            "MSE": cluster_mse,
                            "RMSE": cluster_rmse,
                            "MAE": cluster_mae,
                            "R2": cluster_r2,
                            "has_model": cluster_id in self.regressor_models,
                            "regressor_type": self.regressor_type,
                        }

                        results["cluster_wise"][cluster_id] = cluster_metrics

                        logger.info(
                            f"  Cluster {cluster_id} ({len(cluster_y_true)} samples, Model: {self.regressor_type.upper()} {'Yes' if cluster_id in self.regressor_models else 'Fallback'}):"
                        )
                        logger.info(f"    MSE: {cluster_mse:.4f}")
                        logger.info(f"    RMSE: {cluster_rmse:.4f}")
                        logger.info(f"    MAE: {cluster_mae:.4f}")
                        if not np.isnan(cluster_r2):
                            logger.info(f"    R2: {cluster_r2:.4f}")
                        else:
                            logger.info(f"    R2: undefined (zero variance)")
                    else:
                        logger.info(
                            f"  Cluster {cluster_id}: Only {len(cluster_y_true)} sample(s) - skipping detailed metrics"
                        )
                        results["cluster_wise"][cluster_id] = {
                            "samples": len(cluster_y_true),
                            "note": "Insufficient samples for detailed metrics",
                            "regressor_type": self.regressor_type,
                        }
                else:
                    logger.info(
                        f"  Cluster {cluster_id}: No samples in evaluation data"
                    )
        else:
            logger.info("Evaluation metrics:")
            for metric, value in overall_metrics.items():
                logger.info(f"  {metric}: {value:.4f}")

        return results


def main():
    """
    Main function to run the complete ML pipeline.
    """
    # File paths (modify these paths according to your file locations)
    X_train_path = "X_train_no_header.csv"
    y_train_path = "y_train_no_header.csv"
    X_eval_path = "X_eval_no_header.csv"
    y_eval_path = "y_eval_no_header.csv"
    output_path = "y_pred.csv"

    try:
        # Initialize the model with fewer clusters for small dataset and parallel processing
        # You can change regressor_type to:
        # - 'xgboost': XGBoost regressor (default)
        # - 'mlp': Multi-Layer Perceptron neural network
        # - 'linear': Linear Regression
        model = KMeansRegressorPipeline(
            n_clusters=3, random_state=42, n_jobs=-1, regressor_type="xgboost"
        )

        # Load and match CSV files (assumes no header by default)
        X_train, y_train, X_eval, y_eval = model.load_csv_files(
            X_train_path, y_train_path, X_eval_path, y_eval_path, has_header=False
        )

        # Train the model
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_eval)

        # Evaluate the model
        if y_eval.shape[1] == 1:
            y_eval_np = y_eval.values.ravel()
        else:
            # If multiple target columns, use the first one
            y_eval_np = y_eval.iloc[:, 0].values
        metrics = model.evaluate(y_eval_np, y_pred, X_eval)

        # Save predictions to CSV
        predictions_df = pd.DataFrame({"name": model.eval_names, "prediction": y_pred})
        predictions_df.to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")

        # Display results
        print("\n" + "=" * 60)
        print("MACHINE LEARNING PIPELINE RESULTS")
        print("=" * 60)
        print(f"Training data shape: {X_train.shape}")
        print(f"Evaluation data shape: {X_eval.shape}")
        print(f"Number of clusters used: {model.n_clusters}")
        print(f"Regressor type: {model.regressor_type.upper()}")

        print("\nOverall Evaluation Metrics:")
        for metric, value in metrics["overall"].items():
            print(f"  {metric}: {value:.4f}")

        if "cluster_wise" in metrics and metrics["cluster_wise"]:
            print("\nCluster-wise Performance Summary:")
            for cluster_id, cluster_metrics in metrics["cluster_wise"].items():
                if "MSE" in cluster_metrics:
                    model_type = (
                        "Dedicated" if cluster_metrics["has_model"] else "Fallback"
                    )
                    print(
                        f"  Cluster {cluster_id} ({cluster_metrics['samples']} samples, {model_type} model):"
                    )
                    print(
                        f"    R²: {cluster_metrics['R2']:.4f}, RMSE: {cluster_metrics['RMSE']:.4f}"
                    )
                else:
                    print(
                        f"  Cluster {cluster_id}: {cluster_metrics.get('note', 'No data')}"
                    )

        print(f"\nPredictions saved to: {output_path}")
        print("=" * 60)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
