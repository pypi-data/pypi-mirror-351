import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score


def load_and_match_data(features_file, target_file):
    """
    Load features and target from separate CSV files and match by identifier in first column.
    Only keeps rows that exist in both feature and target files.

    Parameters:
    features_file (str): Path to CSV file containing features
    target_file (str): Path to CSV file containing target values

    Returns:
    tuple: (X, y) - matched features and targets
    """
    # Load data files
    features_df = pd.read_csv(features_file)
    target_df = pd.read_csv(target_file)

    # Get column names
    id_col = features_df.columns[0]  # First column is identifier
    target_id_col = target_df.columns[0]  # First column in target file

    # Print information about the original datasets
    print(
        f"Features dataset: {features_df.shape[0]} rows, {features_df.shape[1]} columns"
    )
    print(f"Target dataset: {target_df.shape[0]} rows, {target_df.shape[1]} columns")

    # Ensure the ID columns have the same name for merging
    if id_col != target_id_col:
        print(f"Renaming ID column in target from '{target_id_col}' to '{id_col}'")
        target_df = target_df.rename(columns={target_id_col: id_col})

    # Merge dataframes on identifier column (inner join keeps only matching rows)
    merged_df = pd.merge(features_df, target_df, on=id_col, how="inner")

    # Calculate and print information about unmatched rows
    features_unmatched = features_df.shape[0] - merged_df.shape[0]
    target_unmatched = target_df.shape[0] - merged_df.shape[0]

    print(f"Matching complete:")
    print(f"  - Rows in features not matched: {features_unmatched}")
    print(f"  - Rows in target not matched: {target_unmatched}")
    print(f"  - Total matched rows: {merged_df.shape[0]}")

    # Check if there are any matched rows
    if merged_df.shape[0] == 0:
        raise ValueError("No matching rows found between feature and target files!")

    # Extract feature columns (all except the ID column)
    X = merged_df.iloc[:, 1 : features_df.shape[1]]

    # Extract target column(s)
    if target_df.shape[1] == 2:  # If target file has just ID and one value column
        y = merged_df.iloc[:, features_df.shape[1]]
    else:  # If target file has multiple columns
        y = merged_df.iloc[:, features_df.shape[1] :].iloc[
            :, 0
        ]  # Take the first target column
        print(
            f"Multiple target columns found. Using first column: {target_df.columns[1]}"
        )

    return X, y, merged_df[id_col]  # Also return the IDs for reference


def train_mlp_regressor(X, y, test_size=0.2, random_state=42):
    """
    Train MLPRegressor model on the given data.

    Parameters:
    X (DataFrame): Features
    y (Series): Target values
    test_size (float): Proportion of data to use for testing
    random_state (int): Random seed for reproducibility

    Returns:
    tuple: (model, X_train, X_test, y_train, y_test, scaler)
    """
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Create and train MLPRegressor
    mlp = MLPRegressor(
        hidden_layer_sizes=(100, 50),  # Two hidden layers with 100 and 50 neurons
        activation="relu",
        solver="adam",
        alpha=0.0001,
        batch_size="auto",
        learning_rate="adaptive",
        max_iter=1000,
        random_state=random_state,
        verbose=True,
    )

    # Train the model
    mlp.fit(X_train_scaled, y_train)

    return mlp, X_train_scaled, X_test_scaled, y_train, y_test, scaler


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance.

    Parameters:
    model: Trained model
    X_test: Test features
    y_test: True target values

    Returns:
    dict: Performance metrics
    """
    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # Print metrics
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
    print(f"R² Score: {r2:.4f}")

    return {"mse": mse, "rmse": rmse, "r2": r2, "y_test": y_test, "y_pred": y_pred}


def plot_results(y_test, y_pred):
    """
    Plot actual vs predicted values.
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.7)

    # Plot perfect prediction line
    min_val = min(min(y_test), min(y_pred))
    max_val = max(max(y_test), max(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], "r--")

    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title("MLPRegressor: Actual vs Predicted")
    plt.grid(True)

    # Add R² to the plot
    r2 = r2_score(y_test, y_pred)
    plt.text(
        0.05,
        0.95,
        f"R² = {r2:.4f}",
        transform=plt.gca().transAxes,
        fontsize=12,
        verticalalignment="top",
    )

    plt.tight_layout()
    plt.savefig("prediction_results.png")
    plt.show()


def save_matched_data(X, y, ids, output_file="matched_data.csv"):
    """
    Save the matched data to a CSV file.

    Parameters:
    X (DataFrame): Features
    y (Series or array): Target values
    ids (Series): IDs for each row
    output_file (str): File path to save the matched data
    """
    # Create a DataFrame with IDs, features, and target
    result_df = pd.DataFrame(ids)
    result_df = pd.concat([result_df, X], axis=1)
    result_df["target"] = y

    # Save to CSV
    result_df.to_csv(output_file, index=False)
    print(f"Matched data saved to {output_file}")

    return result_df


def main():
    # File paths
    features_file = "features.csv"
    target_file = "target.csv"

    # Load and match data
    print("Loading and matching data...")
    X, y, ids = load_and_match_data(features_file, target_file)

    # Save matched data to CSV
    print("\nSaving matched data...")
    save_matched_data(X, y, ids, "matched_data.csv")

    print("\nFeature columns:", X.columns.tolist())
    print("Number of features:", X.shape[1])
    print("Number of matched samples:", X.shape[0])

    # Train model
    print("\nTraining MLPRegressor model...")
    mlp, X_train, X_test, y_train, y_test, scaler = train_mlp_regressor(X, y)

    # Evaluate model
    print("\nEvaluating model performance...")
    results = evaluate_model(mlp, X_test, y_test)

    # Plot results
    print("\nPlotting results...")
    plot_results(results["y_test"], results["y_pred"])


if __name__ == "__main__":
    main()
