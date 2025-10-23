"""Utility functions for AI invoice extractor benchmarks."""

import os
from typing import Any


def next_batch_folder(base_dir: str) -> str:
    """Create and return path to a new numeric folder inside base_dir.

    If there are no numeric subfolders, creates '1'. Otherwise creates folder
    with max+1.

    Args:
        base_dir: Base directory path where numbered folders will be created

    Returns:
        Path to the newly created folder
    """
    os.makedirs(base_dir, exist_ok=True)
    nums = []
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path) and name.isdigit():
            try:
                nums.append(int(name))
            except ValueError:
                pass
    next_num = 1 if not nums else max(nums) + 1
    new_folder = os.path.join(base_dir, str(next_num))
    os.makedirs(new_folder, exist_ok=True)
    return new_folder


def format_elapsed(seconds_float: float, sep: str = '-') -> str:
    """Format elapsed seconds as MM<sep>SS.

    Args:
        seconds_float: Number of seconds (can be fractional)
        sep: Separator character. Use ':' for display, '-' for filenames

    Returns:
        Formatted string like "05:42" or "05-42"
    """
    total = int(seconds_float)
    mm = total // 60
    ss = total % 60
    return f"{mm:02d}{sep}{ss:02d}"


def values_equal(expected: Any, got: Any) -> bool:
    """Check if two values are equal, handling None, numeric and string comparisons.

    Args:
        expected: Expected value
        got: Actual value received

    Returns:
        True if values are considered equal, False otherwise
    """
    # Both None / empty
    if expected is None and (got is None or str(got).strip() == '' or got == 'None'):
        return True
    # Try numeric comparison
    try:
        if expected is not None and got is not None:
            exp_num = float(expected)
            got_num = float(got)
            if abs(exp_num - got_num) <= 1e-6:
                return True
    except Exception:
        pass
    # Fallback string compare
    if expected is not None and got is not None:
        try:
            if str(expected).strip().lower() == str(got).strip().lower():
                return True
        except Exception:
            pass
    return False


def ask_yes_no(prompt: str) -> str:
    """Ask for yes/no input with validation.

    Args:
        prompt: Question to display to user

    Returns:
        'y' or 'n'
    """
    while True:
        val = input(prompt).strip().lower()
        if val in ("y", "n"):
            return val
        print("Invalid response. Please enter 'y' or 'n'.")


def ask_int_in_range(prompt: str, min_val: int, max_val: int) -> int:
    """Ask for integer input within a specific range with validation.

    Args:
        prompt: Question to display to user
        min_val: Minimum acceptable value (inclusive)
        max_val: Maximum acceptable value (inclusive)

    Returns:
        Validated integer within the specified range
    """
    while True:
        val = input(prompt).strip()
        try:
            num = int(val)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Please enter a valid integer.")
