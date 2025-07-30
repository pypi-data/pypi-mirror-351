#!/usr/bin/env python3
"""
Author: xlindo
Create Time: 2025-06-01
Description: Example script demonstrating model export to C++ in fit-better.
Usage:
    python cpp_deployment_example.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add fit_better to path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from fit_better import RegressorType, fit_all_regressors, select_best_model
from fit_better.io import export_model_to_json
from fit_better.data import generate_synthetic_data


def main():
    print("C++ Deployment Example")
    print("=" * 50)

    # Create output directory
    tests_dir = Path(__file__).resolve().parent.parent
    output_dir = tests_dir / "data_gen" / "cpp_export"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic data
    print("Generating synthetic data...")
    n_samples = 200
    X = np.linspace(-5, 5, n_samples).reshape(-1, 1)
    y = 0.5 * X.ravel() + 2 + np.sin(X.ravel()) + np.random.normal(0, 0.5, n_samples)

    # Save some test data for C++ testing
    test_data = np.hstack([X[150:170], y[150:170].reshape(-1, 1)])
    np.savetxt(
        output_dir / "test_data.csv",
        test_data,
        delimiter=",",
        header="x,y",
        comments="",
    )
    print(f"Test data saved to {output_dir / 'test_data.csv'}")

    # Train models supported by C++ implementation
    print("Training regression models for C++ deployment...")

    # List of models supported in C++
    supported_models = [
        RegressorType.LINEAR,
        RegressorType.RIDGE,
        RegressorType.LASSO,
        RegressorType.ELASTIC_NET,
        RegressorType.DECISION_TREE,
        RegressorType.RANDOM_FOREST,
        RegressorType.GRADIENT_BOOSTING,
    ]

    all_results = []
    for model_type in supported_models:
        print(f"Training {model_type}...")
        results = fit_all_regressors(X, y, n_jobs=1, regressor_type=model_type)
        if results:
            all_results.extend(results)

    # Export each model to JSON for C++
    for i, result in enumerate(all_results):
        model_type = result["model_name"]
        json_path = output_dir / f"{model_type.lower().replace(' ', '_')}.json"

        print(f"Exporting {model_type} to {json_path}...")
        export_model_to_json(result, str(json_path))

        # Print C++ usage example for this model
        print(f"\nC++ example code for {model_type}:")
        print(
            f"""
        #include "model_runner.h"
        #include <iostream>
        #include <vector>

        int main() {{
            // Load the {model_type} model
            fit_better::ModelRunner model("{json_path.name}");
            
            // Prepare input features
            std::vector<double> input = {{1.0}};  // Single feature example
            
            // Make prediction
            double prediction = model.predict(input);
            
            // Print result
            std::cout << "Prediction: " << prediction << std::endl;
            
            return 0;
        }}
        """
        )

    # Create a C++ batch prediction example
    cpp_example = """
    // Example C++ code for batch prediction
    #include "model_runner.h"
    #include <iostream>
    #include <vector>
    #include <string>
    #include <fstream>
    
    // Read test data from CSV
    std::vector<std::vector<double>> read_csv(const std::string& filename) {
        std::vector<std::vector<double>> data;
        std::ifstream file(filename);
        
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return data;
        }
        
        // Skip header line
        std::string line;
        std::getline(file, line);
        
        // Read data lines
        while (std::getline(file, line)) {
            std::vector<double> row;
            std::stringstream ss(line);
            std::string cell;
            
            while (std::getline(ss, cell, ',')) {
                row.push_back(std::stod(cell));
            }
            
            if (!row.empty()) {
                data.push_back(row);
            }
        }
        
        return data;
    }
    
    int main() {
        // Load the model
        fit_better::ModelRunner model("linear_regression.json");
        
        // Load test data
        auto data = read_csv("test_data.csv");
        if (data.empty()) {
            std::cerr << "No data loaded!" << std::endl;
            return 1;
        }
        
        std::cout << "Processing " << data.size() << " samples..." << std::endl;
        
        // Prepare inputs and make predictions
        for (const auto& row : data) {
            if (row.size() >= 2) {
                // Extract feature (first column)
                std::vector<double> input = {row[0]};
                
                // Make prediction
                double prediction = model.predict(input);
                
                // Compare with actual value (second column)
                std::cout << "Feature: " << row[0]
                          << ", Actual: " << row[1]
                          << ", Predicted: " << prediction
                          << ", Error: " << (prediction - row[1])
                          << std::endl;
            }
        }
        
        return 0;
    }
    """

    with open(output_dir / "batch_prediction_example.cpp", "w") as f:
        f.write(cpp_example)
    print(
        f"\nC++ batch prediction example saved to {output_dir / 'batch_prediction_example.cpp'}"
    )

    # Create a bash script to compile and run the C++ examples
    bash_script = """#!/bin/bash
# Script to compile and run the C++ examples

# Navigate to the C++ build directory
cd ../../cpp/build

# Compile the examples
cmake ..
make

# Run predictions with each model
echo "Running predictions with all models..."

for model in ../../tests/data_gen/cpp_export/*.json; do
    if [ -f "$model" ]; then
        echo "==================================="
        echo "Testing with model: $model"
        ./fit_better_cpp "$model" 1.0
        echo "==================================="
        echo ""
    fi
done

echo "Done!"
"""

    with open(output_dir / "run_cpp_examples.sh", "w") as f:
        f.write(bash_script)
    os.chmod(output_dir / "run_cpp_examples.sh", 0o755)
    print(
        f"Bash script to run C++ examples saved to {output_dir / 'run_cpp_examples.sh'}"
    )

    print("\nDone! You can now use these models with the C++ implementation.")
    print("Follow these steps:")
    print(
        "1. Build the C++ library: `cd ../../cpp && mkdir -p build && cd build && cmake .. && make`"
    )
    print(
        "2. Run the examples: `cd ../../tests/data_gen/cpp_export && ./run_cpp_examples.sh`"
    )


if __name__ == "__main__":
    main()
