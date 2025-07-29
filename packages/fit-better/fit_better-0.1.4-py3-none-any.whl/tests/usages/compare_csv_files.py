#!/usr/bin/env python3
"""
Simple CSV Comparator for golden.csv and eval.csv

This script reads two CSV files with different delimiters, matches records by keys,
and prints a comprehensive summary in a single table.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import argparse
from typing import Dict, Tuple


def detect_delimiter(file_path: str) -> str:
    """Auto-detect the delimiter in a CSV file."""
    with open(file_path, "r") as f:
        first_line = f.readline().strip()

    # Check common delimiters
    if "," in first_line:
        return ","
    elif "\t" in first_line:
        return "\t"
    elif " " in first_line:
        return " "
    else:
        return ","  # Default to comma


def load_csv_file(file_path: str, has_header: bool = True) -> pd.DataFrame:
    """Load a CSV file with auto-detected delimiter."""
    delimiter = detect_delimiter(file_path)

    try:
        header_param = 0 if has_header else None
        df = pd.read_csv(file_path, delimiter=delimiter, header=header_param)

        # If no header, set column names
        if not has_header:
            df.columns = ["key", "value"]
        else:
            # If has header, standardize to 'key', 'value'
            df.columns = ["key", "value"]

        # Convert value column to numeric, drop non-numeric values
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        sys.exit(1)


def compare_csv_files(
    golden_file: str, eval_file: str, has_header: bool = True
) -> Dict:
    """Compare two CSV files and return statistics."""
    # Load files
    print(f"Loading golden file: {golden_file}")
    golden_df = load_csv_file(golden_file, has_header)

    print(f"Loading eval file: {eval_file}")
    eval_df = load_csv_file(eval_file, has_header)

    print(f"Golden file: {len(golden_df)} records")
    print(f"Eval file: {len(eval_df)} records")

    # Merge based on keys
    merged_df = pd.merge(
        golden_df, eval_df, on="key", how="inner", suffixes=("_golden", "_eval")
    )

    print(f"Matched records: {len(merged_df)}")

    if len(merged_df) == 0:
        print("No matching keys found between the files")
        sys.exit(1)

    # Calculate differences
    merged_df["difference"] = merged_df["value_eval"] - merged_df["value_golden"]
    merged_df["abs_difference"] = np.abs(merged_df["difference"])
    merged_df["percent_error"] = (
        merged_df["difference"] / merged_df["value_golden"]
    ) * 100

    # Calculate statistics
    differences = merged_df["difference"]
    abs_differences = merged_df["abs_difference"]
    percent_errors = (
        merged_df["percent_error"].replace([np.inf, -np.inf], np.nan).dropna()
    )

    stats = {
        "matched_records": len(merged_df),
        "mean_difference": float(differences.mean()),
        "std_difference": float(differences.std()),
        "mean_abs_difference": float(abs_differences.mean()),
        "max_difference": float(differences.max()),
        "min_difference": float(differences.min()),
        "rmse": float(np.sqrt(np.mean(differences**2))),
        "mae": float(abs_differences.mean()),
        "correlation": float(merged_df["value_golden"].corr(merged_df["value_eval"])),
        "mean_percent_error": (
            float(percent_errors.mean()) if len(percent_errors) > 0 else np.nan
        ),
    }

    # Print summary table
    print("\n" + "=" * 80)
    print(f"{'COMPARISON SUMMARY':^80}")
    print("=" * 80)

    table_format = f"| {'Metric':<20} | {'Value':^20} | {'Description':<35} |"
    separator = f"|{'-'*22}|{'-'*22}|{'-'*37}|"

    print(separator)
    print(table_format)
    print(separator)

    print(
        f"| {'Matched Records':<20} | {stats['matched_records']:^20} | {'Number of keys present in both files':<35} |"
    )
    print(
        f"| {'Correlation':<20} | {stats['correlation']:^20.4f} | {'Correlation between golden and eval':<35} |"
    )
    print(
        f"| {'Mean Difference':<20} | {stats['mean_difference']:^20.6f} | {'Average of (eval - golden)':<35} |"
    )
    print(
        f"| {'Std Difference':<20} | {stats['std_difference']:^20.6f} | {'Std deviation of differences':<35} |"
    )
    print(
        f"| {'Min Difference':<20} | {stats['min_difference']:^20.6f} | {'Minimum difference':<35} |"
    )
    print(
        f"| {'Max Difference':<20} | {stats['max_difference']:^20.6f} | {'Maximum difference':<35} |"
    )
    print(f"| {'RMSE':<20} | {stats['rmse']:^20.6f} | {'Root Mean Square Error':<35} |")
    print(f"| {'MAE':<20} | {stats['mae']:^20.6f} | {'Mean Absolute Error':<35} |")

    if not np.isnan(stats["mean_percent_error"]):
        print(
            f"| {'Mean Percent Error':<20} | {stats['mean_percent_error']:^20.4f} | {'Average percentage error':<35} |"
        )
    else:
        print(
            f"| {'Mean Percent Error':<20} | {'N/A':^20} | {'Cannot calculate (division by zero)':<35} |"
        )

    print(separator)

    # Show top 5 differences (if available)
    if len(merged_df) > 0:
        print("\n" + "=" * 80)
        print(f"{'TOP 5 LARGEST ABSOLUTE DIFFERENCES':^80}")
        print("=" * 80)

        top_diff = merged_df.sort_values(by="abs_difference", ascending=False).head(5)

        print(
            f"| {'Key':<30} | {'Golden':<15} | {'Eval':<15} | {'Difference':<15} | {'% Error':<15} |"
        )
        print(f"|{'-'*32}|{'-'*17}|{'-'*17}|{'-'*17}|{'-'*17}|")

        for _, row in top_diff.iterrows():
            percent_err = row["percent_error"]
            percent_str = (
                f"{percent_err:.2f}%"
                if not pd.isna(percent_err) and not np.isinf(percent_err)
                else "N/A"
            )

            print(
                f"| {row['key']:<30} | {row['value_golden']:<15.6f} | {row['value_eval']:<15.6f} | "
                f"{row['difference']:<15.6f} | {percent_str:<15} |"
            )

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Compare two CSV files and display a summary table",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--golden-file",
        type=str,
        required=True,
        help="Path to the golden/reference CSV file",
    )
    parser.add_argument(
        "--eval-file",
        type=str,
        required=True,
        help="Path to the CSV file to be evaluated/compared",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Specify if CSV files do not have headers",
    )

    args = parser.parse_args()

    # Check if files exist
    if not Path(args.golden_file).exists():
        print(f"Error: Golden file not found: {args.golden_file}")
        sys.exit(1)
    if not Path(args.eval_file).exists():
        print(f"Error: Eval file not found: {args.eval_file}")
        sys.exit(1)

    # Run comparison
    compare_csv_files(
        golden_file=args.golden_file,
        eval_file=args.eval_file,
        has_header=not args.no_header,
    )


if __name__ == "__main__":
    main()
