"""
Author: hi@xlindo.com
Create Time: 2025-04-29
Description: Utilities for generating and printing ASCII tables from column labels and row data.
Usage:
    from ascii_utils import ascii_table_lines, print_ascii_table
    lines = ascii_table_lines(["A", "B"], [[1, 2], [3, 4]])
    print("\n".join(lines))
    # or
    print_ascii_table(["A", "B"], [[1, 2], [3, 4]])
"""

import logging

logger = logging.getLogger(__name__)


def ascii_table_lines(col_labels, row_data):
    col_widths = [
        max(len(str(x)) for x in [label] + [row[i] for row in row_data])
        for i, label in enumerate(col_labels)
    ]
    header = " | ".join(
        label.ljust(col_widths[i]) for i, label in enumerate(col_labels)
    )
    sep = "-+-".join("-" * w for w in col_widths)
    lines = [header, sep]
    for row in row_data:
        lines.append(
            " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(col_labels)))
        )
    return lines


def print_ascii_table(col_labels, row_data, to_log=True, file_handle=None):
    """
    Print an ASCII table with the given column labels and row data.

    Args:
        col_labels: List of column headers
        row_data: List of rows, where each row is a list of values
        to_log: If True, output to the logger; if False and file_handle is None, print to stdout
        file_handle: If provided, write to this file handle instead of logging/stdout
    """
    lines = ascii_table_lines(col_labels, row_data)

    if file_handle:
        # Write to the provided file handle
        for line in lines:
            file_handle.write(line + "\n")
    elif to_log:
        # Write to the logger
        logger.info("\n" + "\n".join(lines))
    else:
        # Write to stdout
        print("\n".join(lines))


def log_to_file(file_handle, *messages):
    """
    Write messages to a file handle, similar to how logging would work.

    Args:
        file_handle: An open file object
        *messages: Messages to write to the file
    """
    for msg in messages:
        file_handle.write(str(msg) + "\n")
