"""Metrics collection and CSV management for benchmarks."""

import csv
import os
from typing import Any


class Metrics:
    """Collects and stores benchmark metrics to CSV."""

    def __init__(self, csv_path: str | None = None):
        """Initialize Metrics with optional CSV path.

        Args:
            csv_path: Path to metrics CSV file. If None, uses default location
                     in tests/test_data/json_batches/metrics_progress.csv
        """
        self.data = []
        if csv_path is None:
            # Default progress CSV inside tests/test_data/json_batches
            csv_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'tests', 'test_data', 'json_batches'
            )
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, 'metrics_progress.csv')
        self.csv_path = csv_path

        # Initialize CSV with header only if file does not exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'model_name', 'model_parameters', 'model_size',
                    'pdf_file', 'elapsed_time_seconds', 'user_rating_percentage'
                ])
                writer.writeheader()

    def add(
        self,
        model_name: str,
        model_params: int,
        model_size: float,
        pdf_file: str,
        elapsed: float,
        user_rating_percentage: float
    ) -> None:
        """Add a benchmark result to metrics.

        Args:
            model_name: Name of the AI model
            model_params: Model parameters in billions
            model_size: Model size in GB
            pdf_file: PDF filename that was processed
            elapsed: Time taken in seconds
            user_rating_percentage: Rating from 0-100
        """
        row = {
            "model_name": model_name,
            "model_parameters": model_params,
            "model_size": model_size,
            "pdf_file": pdf_file,
            "elapsed_time_seconds": elapsed,
            "user_rating_percentage": user_rating_percentage
        }
        self.data.append(row)

        # Append immediately to CSV for crash-safe persistence
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)

    def to_csv(self, csv_path: str) -> None:
        """Export all metrics to a CSV file.

        Args:
            csv_path: Path where CSV will be written
        """
        if not self.data:
            return
        keys = self.data[0].keys()
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.data)


def load_processed_set(csv_path: str) -> set[tuple[str, str, str]]:
    """Load already-processed benchmark combinations from CSV.

    Args:
        csv_path: Path to the metrics CSV file

    Returns:
        Set of tuples (pdf_file, model_name, model_parameters) that have
        already been processed
    """
    processed = set()
    if not os.path.exists(csv_path):
        return processed
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                # Use (pdf_file, model_name, model_parameters) as identity
                processed.add((
                    r.get('pdf_file'),
                    r.get('model_name'),
                    r.get('model_parameters')
                ))
    except Exception:
        # If CSV is corrupted or unreadable, treat as empty
        return set()
    return processed
