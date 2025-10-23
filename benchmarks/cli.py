#!/usr/bin/env python3
"""Command-line interface for AI invoice extractor benchmarks.

This module provides a CLI for running various benchmark modes:
- batch: Simple batch processing with timing
- rate: Interactive rating of all models
- threaded: Concurrent processing with interactive rating (recommended)

Usage examples:
    python -m benchmarks.cli batch
    python -m benchmarks.cli rate
    python -m benchmarks.cli threaded --start-file invoice-test-5.pdf
    python -m benchmarks.cli threaded --start-index 5
"""

import argparse
import sys

from .benchmark import benchmark_batch, benchmark_threaded, benchmark_with_rating


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments. If None, uses sys.argv[1:]

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Run AI invoice extractor benchmarks"
    )
    subparsers = parser.add_subparsers(dest='mode', help='Benchmark mode')

    # Batch mode
    batch_parser = subparsers.add_parser(
        'batch',
        help='Run simple batch processing with timing'
    )
    batch_parser.add_argument(
        '--model',
        default='qwen2.5vl',
        help='Model name to use (default: qwen2.5vl)'
    )

    # Rating mode
    subparsers.add_parser(
        'rate',
        help='Run interactive rating for all models'
    )

    # Threaded mode (recommended)
    threaded_parser = subparsers.add_parser(
        'threaded',
        help='Run concurrent processing with interactive rating (recommended)'
    )
    threaded_parser.add_argument(
        '--start-file',
        help='Start from specific PDF file (e.g., invoice-test-5.pdf)'
    )
    threaded_parser.add_argument(
        '--start-index',
        type=int,
        help='Start from specific 1-based index'
    )

    args = parser.parse_args(argv)

    if not args.mode:
        parser.print_help()
        return 1

    try:
        if args.mode == 'batch':
            benchmark_batch(model_name=args.model)
        elif args.mode == 'rate':
            benchmark_with_rating()
        elif args.mode == 'threaded':
            benchmark_threaded(
                start_file=args.start_file,
                start_index=args.start_index
            )
        return 0
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running benchmark: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
