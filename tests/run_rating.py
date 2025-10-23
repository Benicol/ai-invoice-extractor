#!/usr/bin/env python3
"""Compatibility wrapper for old run_rating.py script.

DEPRECATED: This script has been replaced by the consolidated benchmarks package.

Old usage:
    python tests/run_rating.py --start-file invoice-test-5.pdf
    python tests/run_rating.py --start-index 5

New usage:
    python -m benchmarks.cli threaded --start-file invoice-test-5.pdf
    python -m benchmarks.cli threaded --start-index 5

For more information, see benchmarks/README.md
"""

import sys
import warnings

# Show deprecation warning
warnings.warn(
    "tests/run_rating.py is deprecated. Use 'python -m benchmarks.cli threaded' instead. "
    "See benchmarks/README.md for details.",
    DeprecationWarning,
    stacklevel=2
)

# Forward to new CLI
try:
    from benchmarks.cli import main as benchmark_main
    
    # Convert old args to new format
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-file", help="Start from specific PDF file")
    parser.add_argument("--start-index", type=int, help="Start from specific 1-based index")
    args = parser.parse_args()
    
    # Build new args
    new_args = ['threaded']
    if args.start_file:
        new_args.extend(['--start-file', args.start_file])
    if args.start_index:
        new_args.extend(['--start-index', str(args.start_index)])
    
    print("Note: This script is deprecated. Use 'python -m benchmarks.cli threaded' instead.")
    print(f"Forwarding to: python -m benchmarks.cli {' '.join(new_args)}\n")
    
    sys.exit(benchmark_main(new_args))
    
except ImportError as e:
    print("ERROR: Could not import benchmarks package.", file=sys.stderr)
    print(f"Error: {e}", file=sys.stderr)
    print("\nPlease use the new benchmark CLI:", file=sys.stderr)
    print("  python -m benchmarks.cli threaded --help", file=sys.stderr)
    sys.exit(1)
