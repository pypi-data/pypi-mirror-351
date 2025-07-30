#!/usr/bin/env python3
"""
CSV Comparator Tool

This script compares two CSV files with key-value pairs, performs statistical analysis,
and generates visualization plots.

Author: hi@xlindo.com
Created: 2025-05-23
"""

import pandas as pd
import numpy as np
import argparse
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Dict, Optional
import warnings

# Try to import optional libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib or seaborn not found. Plotting will be disabled.")

try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    print("Warning: tabulate not found. Using basic text format for tables.")

warnings.filterwarnings("ignore")


class CSVComparator:
    """A class to compare two CSV files with key-value pairs."""

    def __init__(
        self,
        golden_file: str,
        eval_file: str,
        has_header: bool = True,
        golden_delimiter: str = ",",
        eval_delimiter: str = ",",
    ):
        """
        Initialize the CSV comparator.

        Args:
            golden_file: Path to the golden/reference CSV file
            eval_file: Path to the CSV file to be evaluated/compared
            has_header: Whether the CSV files have headers
            golden_delimiter: Delimiter for the golden file (default: ',')
            eval_delimiter: Delimiter for the eval file (default: ',')
        """
        self.golden_file = golden_file
        self.eval_file = eval_file
        self.has_header = has_header
        self.golden_delimiter = golden_delimiter
        self.eval_delimiter = eval_delimiter
        self.golden_df = None
        self.eval_df = None
        self.merged_df = None
        self.stats = {}

    def load_data(self) -> None:
        """Load and validate the CSV files."""
        try:
            # Load CSV files
            header_param = 0 if self.has_header else None
            self.golden_df = pd.read_csv(
                self.golden_file, header=header_param, delimiter=self.golden_delimiter
            )
            self.eval_df = pd.read_csv(
                self.eval_file, header=header_param, delimiter=self.eval_delimiter
            )

            # Try to automatically detect delimiter if reading fails
            if self.golden_df.shape[1] == 1:
                for delim in [",", ";", "\t", " "]:
                    try:
                        test_df = pd.read_csv(
                            self.golden_file, header=header_param, delimiter=delim
                        )
                        if test_df.shape[1] > 1:
                            self.golden_df = test_df
                            self.golden_delimiter = delim
                            print(f"Auto-detected delimiter for golden file: '{delim}'")
                            break
                    except:
                        pass

            if self.eval_df.shape[1] == 1:
                for delim in [",", ";", "\t", " "]:
                    try:
                        test_df = pd.read_csv(
                            self.eval_file, header=header_param, delimiter=delim
                        )
                        if test_df.shape[1] > 1:
                            self.eval_df = test_df
                            self.eval_delimiter = delim
                            print(f"Auto-detected delimiter for eval file: '{delim}'")
                            break
                    except:
                        pass

        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {str(e)}")
        except pd.errors.EmptyDataError as e:
            raise ValueError(f"Empty CSV file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error reading CSV files: {str(e)}")

        # Validate column count
        if self.golden_df.shape[1] != 2:
            raise ValueError(
                f"Golden file must have exactly 2 columns, got {self.golden_df.shape[1]}"
            )
        if self.eval_df.shape[1] != 2:
            raise ValueError(
                f"Eval file must have exactly 2 columns, got {self.eval_df.shape[1]}"
            )

        # Set column names if no header
        if not self.has_header:
            self.golden_df.columns = ["key", "value"]
            self.eval_df.columns = ["key", "value"]
        else:
            # Rename columns to standard names
            self.golden_df.columns = ["key", "value"]
            self.eval_df.columns = ["key", "value"]

        try:
            # Convert value columns to numeric
            self.golden_df["value"] = pd.to_numeric(
                self.golden_df["value"], errors="coerce"
            )
            self.eval_df["value"] = pd.to_numeric(
                self.eval_df["value"], errors="coerce"
            )

            # Remove rows with NaN values
            self.golden_df = self.golden_df.dropna()
            self.eval_df = self.eval_df.dropna()

            print(f"Loaded golden file: {len(self.golden_df)} rows")
            print(f"Loaded eval file: {len(self.eval_df)} rows")

        except Exception as e:
            raise Exception(f"Error processing data: {str(e)}")

    def merge_data(self) -> None:
        """Merge the datasets based on key columns."""
        self.merged_df = pd.merge(
            self.golden_df,
            self.eval_df,
            on="key",
            how="inner",
            suffixes=("_golden", "_eval"),
        )

        if len(self.merged_df) == 0:
            raise ValueError("No matching keys found between the two files")

        print(f"Matched records: {len(self.merged_df)}")

        # Calculate differences
        self.merged_df["difference"] = (
            self.merged_df["value_eval"] - self.merged_df["value_golden"]
        )
        self.merged_df["abs_difference"] = np.abs(self.merged_df["difference"])
        self.merged_df["percent_error"] = (
            self.merged_df["difference"] / self.merged_df["value_golden"]
        ) * 100

    def calculate_statistics(self) -> Dict:
        """Calculate statistical metrics for the comparison."""
        differences = self.merged_df["difference"]
        abs_differences = self.merged_df["abs_difference"]
        percent_errors = (
            self.merged_df["percent_error"].replace([np.inf, -np.inf], np.nan).dropna()
        )

        self.stats = {
            "mean_difference": float(differences.mean()),
            "std_difference": float(differences.std()),
            "mean_abs_difference": float(abs_differences.mean()),
            "std_abs_difference": float(abs_differences.std()),
            "mean_percent_error": (
                float(percent_errors.mean()) if len(percent_errors) > 0 else np.nan
            ),
            "std_percent_error": (
                float(percent_errors.std()) if len(percent_errors) > 0 else np.nan
            ),
            "max_difference": float(differences.max()),
            "min_difference": float(differences.min()),
            "rmse": float(np.sqrt(np.mean(differences**2))),
            "mae": float(abs_differences.mean()),
            "correlation": float(
                self.merged_df["value_golden"].corr(self.merged_df["value_eval"])
            ),
            "total_records": len(self.merged_df),
            "records_within_3sigma": len(
                differences[np.abs(differences) <= 3 * differences.std()]
            ),
        }

        # Calculate percentage within 3 sigma
        self.stats["percent_within_3sigma"] = (
            self.stats["records_within_3sigma"] / self.stats["total_records"]
        ) * 100

        return self.stats

    def print_statistics(self) -> None:
        """Print statistical summary in a table format."""
        print("\n" + "=" * 60)
        print("STATISTICAL COMPARISON SUMMARY")
        print("=" * 60)

        # Create table rows
        table_data = [
            ["Total matched records", f"{self.stats['total_records']}"],
            ["Correlation coefficient", f"{self.stats['correlation']:.4f}"],
            ["", ""],
            ["Difference Statistics (Eval - Golden)", ""],
            ["Mean difference", f"{self.stats['mean_difference']:.6f}"],
            ["Standard deviation", f"{self.stats['std_difference']:.6f}"],
            ["Min difference", f"{self.stats['min_difference']:.6f}"],
            ["Max difference", f"{self.stats['max_difference']:.6f}"],
            ["", ""],
            ["Absolute Difference Statistics", ""],
            ["Mean absolute error (MAE)", f"{self.stats['mae']:.6f}"],
            ["Root mean square error (RMSE)", f"{self.stats['rmse']:.6f}"],
            ["", ""],
            ["Percent Error Statistics", ""],
        ]

        if not np.isnan(self.stats["mean_percent_error"]):
            table_data.extend(
                [
                    ["Mean percent error", f"{self.stats['mean_percent_error']:.4f}%"],
                    ["Std percent error", f"{self.stats['std_percent_error']:.4f}%"],
                ]
            )
        else:
            table_data.append(["Percent error", "Cannot calculate (division by zero)"])

        table_data.extend(
            [
                ["", ""],
                ["3-Sigma Analysis", ""],
                ["Records within 3σ", f"{self.stats['records_within_3sigma']}"],
                ["Percentage within 3σ", f"{self.stats['percent_within_3sigma']:.2f}%"],
            ]
        )

        # Print table
        print(tabulate(table_data, tablefmt="grid"))

    def create_plots(self, output_dir: str = ".", show_plots: bool = True) -> None:
        """Create comparison plots."""
        plt.style.use("default")
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("CSV Comparison Analysis", fontsize=16, fontweight="bold")

        # 1. Scatter plot: Golden vs Eval
        axes[0, 0].scatter(
            self.merged_df["value_golden"],
            self.merged_df["value_eval"],
            alpha=0.6,
            s=30,
            color="blue",
        )

        # Add perfect correlation line
        min_val = min(
            self.merged_df["value_golden"].min(), self.merged_df["value_eval"].min()
        )
        max_val = max(
            self.merged_df["value_golden"].max(), self.merged_df["value_eval"].max()
        )
        axes[0, 0].plot(
            [min_val, max_val],
            [min_val, max_val],
            "r--",
            linewidth=2,
            label="Perfect match",
        )

        axes[0, 0].set_xlabel("Golden Values")
        axes[0, 0].set_ylabel("Eval Values")
        axes[0, 0].set_title(
            f'Golden vs Eval\n(Correlation: {self.stats["correlation"]:.4f})'
        )
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Difference histogram
        axes[0, 1].hist(
            self.merged_df["difference"],
            bins=30,
            alpha=0.7,
            color="green",
            edgecolor="black",
        )
        axes[0, 1].axvline(
            self.stats["mean_difference"],
            color="red",
            linestyle="--",
            label=f'Mean: {self.stats["mean_difference"]:.4f}',
        )
        axes[0, 1].axvline(
            self.stats["mean_difference"] + self.stats["std_difference"],
            color="orange",
            linestyle=":",
            label=f'+1σ: {self.stats["std_difference"]:.4f}',
        )
        axes[0, 1].axvline(
            self.stats["mean_difference"] - self.stats["std_difference"],
            color="orange",
            linestyle=":",
            label=f"-1σ",
        )
        axes[0, 1].set_xlabel("Difference (Eval - Golden)")
        axes[0, 1].set_ylabel("Frequency")
        axes[0, 1].set_title("Difference Distribution")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Absolute difference vs Golden values
        axes[1, 0].scatter(
            self.merged_df["value_golden"],
            self.merged_df["abs_difference"],
            alpha=0.6,
            s=30,
            color="purple",
        )
        axes[1, 0].set_xlabel("Golden Values")
        axes[1, 0].set_ylabel("Absolute Difference")
        axes[1, 0].set_title("Absolute Difference vs Golden Values")
        axes[1, 0].grid(True, alpha=0.3)

        # 4. Percent error (if calculable)
        if not np.isnan(self.stats["mean_percent_error"]):
            valid_percent_errors = (
                self.merged_df["percent_error"]
                .replace([np.inf, -np.inf], np.nan)
                .dropna()
            )
            if len(valid_percent_errors) > 0:
                axes[1, 1].hist(
                    valid_percent_errors,
                    bins=30,
                    alpha=0.7,
                    color="orange",
                    edgecolor="black",
                )
                axes[1, 1].axvline(
                    self.stats["mean_percent_error"],
                    color="red",
                    linestyle="--",
                    label=f'Mean: {self.stats["mean_percent_error"]:.2f}%',
                )
                axes[1, 1].set_xlabel("Percent Error (%)")
                axes[1, 1].set_ylabel("Frequency")
                axes[1, 1].set_title("Percent Error Distribution")
                axes[1, 1].legend()
                axes[1, 1].grid(True, alpha=0.3)
            else:
                axes[1, 1].text(
                    0.5,
                    0.5,
                    "No valid percent\nerrors to display",
                    ha="center",
                    va="center",
                    transform=axes[1, 1].transAxes,
                )
                axes[1, 1].set_title("Percent Error Distribution")
        else:
            axes[1, 1].text(
                0.5,
                0.5,
                "Percent error cannot\nbe calculated\n(division by zero)",
                ha="center",
                va="center",
                transform=axes[1, 1].transAxes,
            )
            axes[1, 1].set_title("Percent Error Distribution")

        plt.tight_layout()

        # Save plot
        output_path = Path(output_dir) / "comparison_plots.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"\nPlots saved to: {output_path}")

        if show_plots:
            plt.show()
        else:
            plt.close()

    def save_results(self, output_dir: str = ".") -> None:
        """Save detailed results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save merged data with differences
        merged_output = output_path / "comparison_details.csv"
        self.merged_df.to_csv(merged_output, index=False)
        print(f"Detailed comparison saved to: {merged_output}")

        # Save statistics
        stats_output = output_path / "comparison_statistics.txt"
        with open(stats_output, "w") as f:
            f.write("CSV COMPARISON STATISTICS\n")
            f.write("=" * 50 + "\n\n")
            for key, value in self.stats.items():
                f.write(f"{key}: {value}\n")
        print(f"Statistics saved to: {stats_output}")

    def run_comparison(
        self, output_dir: str = ".", show_plots: bool = True, save_files: bool = True
    ) -> Dict:
        """Run the complete comparison analysis."""
        print("Starting CSV comparison analysis...")

        # Load and process data
        self.load_data()
        self.merge_data()

        # Calculate statistics
        stats = self.calculate_statistics()
        self.print_statistics()

        # Create visualizations
        self.create_plots(output_dir, show_plots)

        # Save results
        if save_files:
            self.save_results(output_dir)

        print("\nComparison analysis completed successfully!")
        return stats


# Unit Tests
class TestCSVComparator(unittest.TestCase):
    """Test cases for CSV Comparator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.golden_file = os.path.join(self.test_dir, "golden.csv")
        self.eval_file = os.path.join(self.test_dir, "eval.csv")
        self.output_dir = os.path.join(self.test_dir, "output")

        # Create sample data
        self.create_sample_files()

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir)

    def create_sample_files(self):
        """Create sample CSV files for testing."""
        # Golden file data
        golden_data = {
            "key": ["A", "B", "C", "D", "E"],
            "value": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
        golden_df = pd.DataFrame(golden_data)
        golden_df.to_csv(self.golden_file, index=False)

        # Eval file data (with some differences)
        eval_data = {
            "key": ["A", "B", "C", "D", "F"],  # F instead of E
            "value": [1.1, 2.0, 2.9, 4.1, 6.0],  # Slight differences
        }
        eval_df = pd.DataFrame(eval_data)
        eval_df.to_csv(self.eval_file, index=False)

    def create_no_header_files(self):
        """Create sample CSV files without headers."""
        golden_file_no_header = os.path.join(self.test_dir, "golden_no_header.csv")
        eval_file_no_header = os.path.join(self.test_dir, "eval_no_header.csv")

        # Write data without headers
        with open(golden_file_no_header, "w") as f:
            f.write("A,1.0\nB,2.0\nC,3.0\nD,4.0\nE,5.0\n")

        with open(eval_file_no_header, "w") as f:
            f.write("A,1.1\nB,2.0\nC,2.9\nD,4.1\nF,6.0\n")

        return golden_file_no_header, eval_file_no_header

    def test_initialization(self):
        """Test CSVComparator initialization."""
        comparator = CSVComparator(self.golden_file, self.eval_file)
        self.assertEqual(comparator.golden_file, self.golden_file)
        self.assertEqual(comparator.eval_file, self.eval_file)
        self.assertTrue(comparator.has_header)
        self.assertIsNone(comparator.golden_df)
        self.assertIsNone(comparator.eval_df)

    def test_load_data_with_header(self):
        """Test loading CSV data with headers."""
        comparator = CSVComparator(self.golden_file, self.eval_file)
        comparator.load_data()

        self.assertIsNotNone(comparator.golden_df)
        self.assertIsNotNone(comparator.eval_df)
        self.assertEqual(len(comparator.golden_df), 5)
        self.assertEqual(len(comparator.eval_df), 5)
        self.assertEqual(list(comparator.golden_df.columns), ["key", "value"])
        self.assertEqual(list(comparator.eval_df.columns), ["key", "value"])

    def test_load_data_without_header(self):
        """Test loading CSV data without headers."""
        golden_no_header, eval_no_header = self.create_no_header_files()
        comparator = CSVComparator(golden_no_header, eval_no_header, has_header=False)
        comparator.load_data()

        self.assertIsNotNone(comparator.golden_df)
        self.assertIsNotNone(comparator.eval_df)
        self.assertEqual(list(comparator.golden_df.columns), ["key", "value"])
        self.assertEqual(list(comparator.eval_df.columns), ["key", "value"])

    def test_load_data_file_not_found(self):
        """Test loading data with non-existent files."""
        comparator = CSVComparator("nonexistent1.csv", "nonexistent2.csv")
        with self.assertRaises(FileNotFoundError):
            comparator.load_data()

    def test_load_data_wrong_columns(self):
        """Test loading data with wrong number of columns."""
        # Create file with wrong number of columns
        wrong_file = os.path.join(self.test_dir, "wrong.csv")
        with open(wrong_file, "w") as f:
            f.write("col1,col2,col3\n1,2,3\n4,5,6\n")

        comparator = CSVComparator(wrong_file, self.eval_file)
        with self.assertRaises(ValueError):
            comparator.load_data()

    def test_merge_data(self):
        """Test merging data based on key columns."""
        comparator = CSVComparator(self.golden_file, self.eval_file)
        comparator.load_data()
        comparator.merge_data()

        self.assertIsNotNone(comparator.merged_df)
        # Should have 4 matches (A, B, C, D)
        self.assertEqual(len(comparator.merged_df), 4)
        self.assertIn("difference", comparator.merged_df.columns)
        self.assertIn("abs_difference", comparator.merged_df.columns)
        self.assertIn("percent_error", comparator.merged_df.columns)

    def test_merge_data_no_matches(self):
        """Test merging data with no matching keys."""
        # Create files with no matching keys
        no_match_file = os.path.join(self.test_dir, "no_match.csv")
        with open(no_match_file, "w") as f:
            f.write("key,value\nX,1\nY,2\nZ,3\n")

        comparator = CSVComparator(self.golden_file, no_match_file)
        comparator.load_data()

        with self.assertRaises(ValueError):
            comparator.merge_data()

    def test_calculate_statistics(self):
        """Test statistical calculations."""
        comparator = CSVComparator(self.golden_file, self.eval_file)
        comparator.load_data()
        comparator.merge_data()
        stats = comparator.calculate_statistics()

        # Check that all expected statistics are present
        expected_keys = [
            "mean_difference",
            "std_difference",
            "mean_abs_difference",
            "std_abs_difference",
            "mean_percent_error",
            "std_percent_error",
            "max_difference",
            "min_difference",
            "rmse",
            "mae",
            "correlation",
            "total_records",
            "records_within_3sigma",
            "percent_within_3sigma",
        ]

        for key in expected_keys:
            self.assertIn(key, stats)

        # Check some specific values
        self.assertEqual(stats["total_records"], 4)
        self.assertIsInstance(stats["correlation"], float)
        self.assertGreater(stats["correlation"], -1)
        self.assertLess(stats["correlation"], 1)

    def test_create_plots(self):
        """Test plot creation."""
        os.makedirs(self.output_dir, exist_ok=True)
        comparator = CSVComparator(self.golden_file, self.eval_file)
        comparator.load_data()
        comparator.merge_data()
        comparator.calculate_statistics()

        # Create plots without showing them
        comparator.create_plots(self.output_dir, show_plots=False)

        # Check if plot file was created
        plot_file = os.path.join(self.output_dir, "comparison_plots.png")
        self.assertTrue(os.path.exists(plot_file))

    def test_save_results(self):
        """Test saving results to files."""
        os.makedirs(self.output_dir, exist_ok=True)
        comparator = CSVComparator(self.golden_file, self.eval_file)
        comparator.load_data()
        comparator.merge_data()
        comparator.calculate_statistics()
        comparator.save_results(self.output_dir)

        # Check if result files were created
        details_file = os.path.join(self.output_dir, "comparison_details.csv")
        stats_file = os.path.join(self.output_dir, "comparison_statistics.txt")

        self.assertTrue(os.path.exists(details_file))
        self.assertTrue(os.path.exists(stats_file))

        # Check content of details file
        details_df = pd.read_csv(details_file)
        self.assertEqual(len(details_df), 4)
        self.assertIn("difference", details_df.columns)

    def test_run_comparison(self):
        """Test the complete comparison workflow."""
        os.makedirs(self.output_dir, exist_ok=True)
        comparator = CSVComparator(self.golden_file, self.eval_file)

        stats = comparator.run_comparison(
            output_dir=self.output_dir, show_plots=False, save_files=True
        )

        # Check that statistics were returned
        self.assertIsInstance(stats, dict)
        self.assertIn("correlation", stats)
        self.assertIn("total_records", stats)

        # Check that files were created
        self.assertTrue(
            os.path.exists(os.path.join(self.output_dir, "comparison_plots.png"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.output_dir, "comparison_details.csv"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.output_dir, "comparison_statistics.txt"))
        )

    def test_perfect_match(self):
        """Test comparison with identical files."""
        # Create identical files
        identical_file = os.path.join(self.test_dir, "identical.csv")
        shutil.copy(self.golden_file, identical_file)

        comparator = CSVComparator(self.golden_file, identical_file)
        comparator.load_data()
        comparator.merge_data()
        stats = comparator.calculate_statistics()

        # Should have perfect correlation and zero differences
        self.assertAlmostEqual(stats["correlation"], 1.0, places=10)
        self.assertAlmostEqual(stats["mean_difference"], 0.0, places=10)
        self.assertAlmostEqual(stats["rmse"], 0.0, places=10)

    def test_numeric_conversion(self):
        """Test handling of non-numeric values."""
        # Create file with mixed data types
        mixed_file = os.path.join(self.test_dir, "mixed.csv")
        with open(mixed_file, "w") as f:
            f.write("key,value\nA,1.0\nB,invalid\nC,3.0\nD,4.0\n")

        comparator = CSVComparator(self.golden_file, mixed_file)
        comparator.load_data()

        # Should have removed the invalid row
        self.assertEqual(len(comparator.eval_df), 3)  # B row removed

    def test_empty_files(self):
        """Test handling of empty files."""
        empty_file = os.path.join(self.test_dir, "empty.csv")
        with open(empty_file, "w") as f:
            f.write("key,value\n")  # Only header

        comparator = CSVComparator(self.golden_file, empty_file)
        comparator.load_data()

        with self.assertRaises(ValueError):
            comparator.merge_data()

    def test_division_by_zero_percent_error(self):
        """Test handling of division by zero in percent error calculation."""
        # Create file with zero values in golden
        zero_golden_file = os.path.join(self.test_dir, "zero_golden.csv")
        with open(zero_golden_file, "w") as f:
            f.write("key,value\nA,0.0\nB,2.0\nC,0.0\n")

        zero_eval_file = os.path.join(self.test_dir, "zero_eval.csv")
        with open(zero_eval_file, "w") as f:
            f.write("key,value\nA,1.0\nB,2.1\nC,0.5\n")

        comparator = CSVComparator(zero_golden_file, zero_eval_file)
        comparator.load_data()
        comparator.merge_data()
        stats = comparator.calculate_statistics()

        # Should handle infinite percent errors gracefully
        self.assertIsInstance(stats["mean_percent_error"], float)


class TestIntegration(unittest.TestCase):
    """Integration tests for the CSV comparator."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)

    def test_realistic_data(self):
        """Test with realistic data scenario."""
        # Create realistic test data
        np.random.seed(42)  # For reproducible results

        keys = [f"item_{i:03d}" for i in range(100)]
        golden_values = np.random.normal(100, 20, 100)

        # Add some realistic errors
        noise = np.random.normal(0, 2, 100)
        eval_values = golden_values + noise

        # Create CSV files
        golden_file = os.path.join(self.test_dir, "realistic_golden.csv")
        eval_file = os.path.join(self.test_dir, "realistic_eval.csv")

        golden_df = pd.DataFrame({"key": keys, "value": golden_values})
        eval_df = pd.DataFrame({"key": keys, "value": eval_values})

        golden_df.to_csv(golden_file, index=False)
        eval_df.to_csv(eval_file, index=False)

        # Run comparison
        comparator = CSVComparator(golden_file, eval_file)
        stats = comparator.run_comparison(
            output_dir=self.test_dir, show_plots=False, save_files=True
        )

        # Verify reasonable results
        self.assertEqual(stats["total_records"], 100)
        self.assertGreater(stats["correlation"], 0.9)  # Should be highly correlated
        self.assertLess(abs(stats["mean_difference"]), 1.0)  # Small mean difference

    def test_large_differences(self):
        """Test with data that has large differences."""
        keys = ["A", "B", "C", "D"]
        golden_values = [1, 10, 100, 1000]
        eval_values = [2, 20, 50, 2000]  # Large relative differences

        golden_file = os.path.join(self.test_dir, "large_diff_golden.csv")
        eval_file = os.path.join(self.test_dir, "large_diff_eval.csv")

        golden_df = pd.DataFrame({"key": keys, "value": golden_values})
        eval_df = pd.DataFrame({"key": keys, "value": eval_values})

        golden_df.to_csv(golden_file, index=False)
        eval_df.to_csv(eval_file, index=False)

        # Run comparison
        comparator = CSVComparator(golden_file, eval_file)
        stats = comparator.run_comparison(
            output_dir=self.test_dir, show_plots=False, save_files=False
        )

        # Should handle large differences appropriately
        self.assertEqual(stats["total_records"], 4)
        self.assertGreater(stats["rmse"], 0)
        self.assertIsInstance(stats["mean_percent_error"], float)


def create_test_suite():
    """Create a test suite with all test cases."""
    test_suite = unittest.TestSuite()

    # Add unit tests
    test_suite.addTest(unittest.makeSuite(TestCSVComparator))
    test_suite.addTest(unittest.makeSuite(TestIntegration))

    return test_suite


def run_tests():
    """Run all unit tests."""
    # Use non-interactive backend for testing
    import matplotlib

    matplotlib.use("Agg")

    print("Running CSV Comparator Unit Tests")
    print("=" * 50)

    # Create test suite
    suite = create_test_suite()

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    # Return success status
    return result.wasSuccessful()


def main():
    """Main function to run the CSV comparator from command line."""
    parser = argparse.ArgumentParser(
        description="Compare two CSV files with key-value pairs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run comparison
  python csv_comparator.py --compare --golden-file golden.csv --eval-file eval.csv
  
  # Without headers
  python csv_comparator.py --compare --golden-file golden.csv --eval-file eval.csv --no-header
  
  # Custom output directory
  python csv_comparator.py --compare --golden-file golden.csv --eval-file eval.csv --output-dir ./results
  
  # With specific delimiters
  python csv_comparator.py --compare --golden-file golden.csv --eval-file eval.csv --golden-delimiter ',' --eval-delimiter ' '
  
  # Run unit tests
  python csv_comparator.py --test
        """,
    )

    # Add argument groups for better organization
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--test", action="store_true", help="Run unit tests instead of comparison"
    )
    mode_group.add_argument(
        "--compare",
        action="store_true",
        help="Run comparison between golden and eval files",
    )

    # Create a separate argument group for files
    files_group = parser.add_argument_group("comparison files")
    files_group.add_argument(
        "--golden-file", type=str, help="Path to the golden/reference CSV file"
    )
    files_group.add_argument(
        "--eval-file", type=str, help="Path to the CSV file to be evaluated/compared"
    )

    # Optional arguments
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Specify if CSV files do not have headers",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save output files (default: current directory)",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Do not display plots (still saves them)",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Do not save result files"
    )
    parser.add_argument(
        "--golden-delimiter",
        default=",",
        help="Delimiter for the golden CSV file (default: comma)",
    )
    parser.add_argument(
        "--eval-delimiter",
        default="auto",
        help="Delimiter for the eval CSV file (default: auto-detect)",
    )

    args = parser.parse_args()

    # Run tests if --test flag is provided
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    # If comparison mode is selected, check for required file arguments
    if args.compare:
        if not args.golden_file or not args.eval_file:
            print(
                "Error: Both --golden-file and --eval-file are required for comparison",
                file=sys.stderr,
            )
            parser.print_help()
            sys.exit(1)

    try:
        # Check if files exist
        if not Path(args.golden_file).exists():
            raise FileNotFoundError(f"Golden file not found: {args.golden_file}")
        if not Path(args.eval_file).exists():
            raise FileNotFoundError(f"Eval file not found: {args.eval_file}")

        print(f"CSV Comparator Tool - {args.golden_file} vs {args.eval_file}")
        print(f"Created by: hi@xlindo.com")
        print(f"Date: 2025-01-23")
        print("-" * 60)

        # Set delimiters
        golden_delimiter = args.golden_delimiter
        eval_delimiter = " " if args.eval_delimiter == "auto" else args.eval_delimiter

        print(f"Using delimiter '{golden_delimiter}' for golden file")
        print(f"Using delimiter '{eval_delimiter}' for eval file")

        # Run comparison
        comparator = CSVComparator(
            golden_file=args.golden_file,
            eval_file=args.eval_file,
            has_header=not args.no_header,
            golden_delimiter=golden_delimiter,
            eval_delimiter=eval_delimiter,
        )

        comparator.run_comparison(
            output_dir=args.output_dir,
            show_plots=not args.no_plots,
            save_files=not args.no_save,
        )

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import os  # Add missing import for tests

    main()
