"""AI Invoice Extractor Benchmarks.

This package provides comprehensive benchmarking tools for evaluating AI models
on invoice extraction tasks.

Main functions:
    - benchmark_batch: Simple batch processing with timing
    - benchmark_with_rating: Interactive evaluation with user ratings
    - benchmark_threaded: Concurrent processing (recommended for efficiency)

CLI usage:
    python -m benchmarks.cli batch
    python -m benchmarks.cli rate
    python -m benchmarks.cli threaded --start-file invoice-test-5.pdf

For more information, see benchmarks/README.md
"""

from .benchmark import benchmark_batch, benchmark_threaded, benchmark_with_rating

__all__ = [
    'benchmark_batch',
    'benchmark_with_rating',
    'benchmark_threaded',
]
