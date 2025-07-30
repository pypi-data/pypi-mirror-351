# Usage Examples Documentation

This directory contains example scripts that demonstrate how to use the fit-better package for various regression tasks. These examples serve as both functional tests and documentation for users.

## Overview

Each example showcases specific functionality of the fit-better package, demonstrating best practices and common usage patterns.

## Example Files

| Example File | Description |
|--------------|-------------|
| `data_generation_example.py` | Demonstrates how to generate synthetic data for testing and experimentation |
| `partition_comparison_example.py` | Shows how to compare different data partitioning strategies |
| `regressor_comparison_example.py` | Illustrates comparing different regression algorithms |
| `partition_algorithm_finder_example.py` | Demonstrates the automatic best strategy finder |
| `parallel_partitioning_example.py` | Shows how to use parallel processing for partitioning |
| `model_save_load_example.py` | Demonstrates saving and loading trained models |
| `model_persistence_example.py` | Shows advanced model persistence with versioning |
| `cpp_deployment_example.py` | Illustrates how to export models for C++ deployment |
| `sklearn_integration_example.py` | Shows integration with scikit-learn pipelines and API |

## Running Examples

You can run any example directly from the command line:

```bash
cd tests
python usages/regressor_comparison_example.py
```

Most examples accept command-line arguments for customization:

```bash
python usages/regressor_comparison_example.py --visualize --n-jobs 4
```

## Visualization Output

Many examples support the `--visualize` flag, which generates plots and visualizations in the relevant results directory:

- `partition_results/` - For partition comparison visualizations
- `regressor_results/` - For regressor comparison visualizations
- `visualization_results/` - For general visualizations

## Generated Data

All examples generate test data in the `data_gen/data/` directory if needed, and log output to the `data_gen/logs/` directory.

## Common Command-Line Arguments

| Argument | Description |
|----------|-------------|
| `--visualize` | Generate visualization plots |
| `--output-dir DIR` | Directory to save results |
| `--n-jobs N` | Number of parallel jobs to use |
| `--parts N` | Number of partitions to create |
| `--n-samples N` | Number of samples to generate |

## Using Examples as Templates

These examples can be used as templates for your own regression tasks:

1. Copy the most relevant example to your project
2. Modify the data loading section to use your own data
3. Adjust the parameters to suit your specific use case
4. Use the output to determine the best regression strategy

## Advanced Usage

For more advanced usage, refer to the following examples:

- `sklearn_integration_example.py` - For integration with scikit-learn workflows
- `cpp_deployment_example.py` - For deploying models in C++ applications
- `partition_algorithm_finder_example.py` - For automatic strategy selection 