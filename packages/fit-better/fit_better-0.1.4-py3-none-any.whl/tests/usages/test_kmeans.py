import sys

print(f"Python version: {sys.version}")

import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Test file paths
print("Checking for test files")
for path in [
    "/mnt/d/repos/fit-better/data/train_features.csv",
    "/mnt/d/repos/fit-better/data/train_target.csv",
]:
    print(f"File {path} exists: {os.path.exists(path)}")

# Load a small dataset
try:
    print("Loading sample data")
    X = np.random.rand(100, 5)

    # Test KMeans with n_jobs parameter
    print("Testing KMeans with n_jobs")

    try:
        # First try with n_jobs
        kmeans = KMeans(n_clusters=3, n_jobs=2, random_state=42)
        kmeans.fit(X)
        print("KMeans with n_jobs works!")
    except TypeError as e:
        print(f"Error with n_jobs: {e}")

        # Try without n_jobs
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(X)
        print("KMeans without n_jobs works!")

    print("Test completed successfully")
except Exception as e:
    print(f"Unexpected error: {e}")
