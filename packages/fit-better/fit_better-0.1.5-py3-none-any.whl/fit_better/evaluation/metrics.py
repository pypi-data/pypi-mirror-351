"""
Author: hi@xlindo.com
Create Time: 2025-04-29
Description: Evaluation utilities for regression results, including statistics and ASCII table output.
Usage:
    from eval_utils import key_statistics
    key_statistics(X, y, results)
"""

import numpy as np
from fit_better.utils.statistics import calc_regression_statistics
from fit_better.utils.ascii import print_ascii_table


def key_statistics(X, y, results):
    row_data = []
    orig_stats = calc_regression_statistics(y, X.flatten())
    row_data.append(
        [
            "Local X vs Golden y",
            f"{orig_stats['mae']:.6f}",
            f"{orig_stats['rmse']:.6f}",
            f"{orig_stats['r2']:.6f}",
            f"{orig_stats['std_residual']:.6f}",
            f"{orig_stats['max_residual']:.6f}",
            f"{orig_stats['min_residual']:.6f}",
            f"{orig_stats['pct_within_3pct']:.2f}%",
            f"{orig_stats['pct_within_5pct']:.2f}%",
            f"{orig_stats['pct_within_10pct']:.2f}%",
        ]
    )
    for res in results:
        name = res["name"]
        stats = res["stats"]
        row_data.append(
            [
                name,
                f"{stats['mae']:.6f}",
                f"{stats['rmse']:.6f}",
                f"{stats['r2']:.6f}",
                f"{stats['std_residual']:.6f}",
                f"{stats['max_residual']:.6f}",
                f"{stats['min_residual']:.6f}",
                f"{stats['pct_within_3pct']:.2f}%",
                f"{stats['pct_within_5pct']:.2f}%",
                f"{stats['pct_within_10pct']:.2f}%",
            ]
        )
    return row_data


EVAL_STAT_KEYS = [
    ("mae", "MAE"),
    ("rmse", "RMSE"),
    ("r2", "R2"),
    ("std_residual", "Std(Res)"),
    ("max_residual", "Max(Res)"),
    ("min_residual", "Min(Res)"),
    ("pct_within_3pct", "<=3%"),
    ("pct_within_5pct", "<=5%"),
    ("pct_within_10pct", "<=10%"),
]


def make_eval_row(label, stats):
    row = [label]
    for k, _ in EVAL_STAT_KEYS:
        val = stats.get(k, None)
        if val is None:
            row.append("")
        elif "pct_within" in k:
            row.append(f"{val:.2f}%")
        else:
            row.append(f"{val:.6f}")
    return row


def evaluate_model_on_data(model, X, y_true, top_n=10, print_stats=True):
    from fit_better.io import predict_with_model
    from fit_better.utils.logging_utils import get_logger
    from fit_better.utils.ascii import print_ascii_table

    stats = calc_regression_statistics(y_true, predict_with_model(model, X))
    if print_stats:
        logger = get_logger(__name__)
        logger.info("\nRegression statistics:")
        col_labels = ["Metric", "Value"]
        stat_keys = [
            "mean_true",
            "std_true",
            "mean_pred",
            "std_pred",
            "mean_residual",
            "std_residual",
            "mae",
            "rmse",
            "max_abs_residual",
            "min_residual",
            "max_residual",
            "r2",
            "pct_within_3pct",
            "pct_within_5pct",
            "pct_within_10pct",
            "pct_within_20pct",
        ]
        row_data = []
        for k in stat_keys:
            if k in stats:
                if not k.startswith("pct_within"):
                    row_data.append([k, f"{stats[k]:.6f}"])
                else:
                    row_data.append([k, f"{stats[k]:.2f}%"])
        print_ascii_table(col_labels, row_data)
    return stats
