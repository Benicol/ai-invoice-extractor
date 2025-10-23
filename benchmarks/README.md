# AI Invoice Extractor Benchmarks

This directory contains benchmarking tools for evaluating AI models on invoice extraction tasks.

## Overview

The benchmark suite provides three modes of operation:

1. **Batch Mode**: Simple batch processing with timing measurements
2. **Rating Mode**: Interactive evaluation with manual rating of results
3. **Threaded Mode**: Concurrent processing with interactive rating (recommended)

## Quick Start

### Running Benchmarks

```bash
# Simple batch processing (fastest, no rating)
python -m benchmarks.cli batch

# Interactive rating for all models (comprehensive)
python -m benchmarks.cli rate

# Threaded mode with concurrent processing (recommended)
python -m benchmarks.cli threaded

# Resume from a specific file
python -m benchmarks.cli threaded --start-file invoice-test-5.pdf

# Resume from a specific index
python -m benchmarks.cli threaded --start-index 5
```

### Using as a Module

```python
from benchmarks import benchmark_batch, benchmark_with_rating, benchmark_threaded

# Run simple batch benchmark
benchmark_batch(model_name="qwen2.5vl")

# Run with interactive rating
benchmark_with_rating()

# Run threaded benchmark (recommended)
benchmark_threaded(start_index=5)
```

## Benchmark Modes

### Batch Mode

The simplest mode that processes all PDF files with a single model and records timing information.

**Features:**
- Fast execution (no user interaction)
- Timing measurements for each file
- Progress tracking with ETA
- Output saved to JSON files

**Output:**
- JSON files in `tests/test_data/json_batches/<n>/`
- Filename format: `<invoice>__<model>__<mm-ss>.json`

### Rating Mode

Interactive mode that evaluates all configured models and collects user ratings.

**Features:**
- Tests multiple models sequentially
- User confirmation before processing each file
- Interactive rating for each field (0-100 points)
- Metrics saved to CSV

**Scoring System:**
- total_excluding_vat: 0-15 points
- total_vat: 0-15 points
- total_including_vat: 0-15 points
- date: 0-25 points
- supplier: 0-30 points
- **Total: 100 points**

**Output:**
- JSON responses in `tests/test_data/json_batches/<n>/`
- Metrics CSV with all ratings and timing

### Threaded Mode (Recommended)

Advanced mode that runs AI inference in a background thread while the main thread handles interactive rating.

**Features:**
- Concurrent processing (no waiting between ratings)
- Resume capability from specific file or index
- Crash-safe with progress tracking
- Skips already-processed combinations
- Most efficient for large-scale evaluation

**Output:**
- JSON responses in `tests/test_data/json_batches/<n>/`
- Progressive metrics in `tests/test_data/json_batches/metrics_progress.csv`
- Final metrics in batch folder

## Configuration

### Models

Configured in `benchmarks/config.py`:

```python
MODELS = [
    {"name": "qwen2.5vl", "parameters": 3, "size": 3.2},
    {"name": "qwen2.5vl", "parameters": 7, "size": 6.0},
    {"name": "granite3.2-vision", "parameters": 2, "size": 2.4},
    {"name": "qwen2.5vl", "parameters": 32, "size": 21.0},
    {"name": "mistral-small3.2", "parameters": 24, "size": 15.0}
]
```

### Expected Results

Ground truth values for validation are defined in `benchmarks/config.py` in the `EXPECTED_RESULTS` dictionary.

## Output Structure

```
tests/test_data/json_batches/
├── metrics_progress.csv          # Progressive metrics (crash-safe)
├── 1/                             # First batch
│   ├── invoice-test-1__qwen2.5vl__00-05.json
│   ├── invoice-test-2__qwen2.5vl__00-06.json
│   └── metrics.csv
├── 2/                             # Second batch
│   └── ...
└── ...
```

## Metrics

The benchmark collects the following metrics:

- **model_name**: Name of the AI model
- **model_parameters**: Model size in billions of parameters
- **model_size**: Model size in GB
- **pdf_file**: Name of the PDF file processed
- **elapsed_time_seconds**: Processing time in seconds
- **user_rating_percentage**: Rating from 0-100

## Architecture

The benchmark suite is organized into clean, modular components:

```
benchmarks/
├── __init__.py          # Package exports
├── cli.py               # Command-line interface
├── benchmark.py         # Main benchmark functions
├── config.py            # Model and test data configuration
├── metrics.py           # Metrics collection and CSV handling
├── rating.py            # Interactive rating functionality
├── _utils.py            # Shared utility functions
└── README.md            # This file
```

### Module Responsibilities

- **benchmark.py**: Core benchmark logic and orchestration
- **config.py**: Centralized configuration (models, expected results)
- **metrics.py**: Metrics collection and persistence
- **rating.py**: Interactive rating with validation
- **_utils.py**: Shared helper functions (formatting, I/O, validation)
- **cli.py**: Command-line interface and argument parsing

## Migration from Old Files

This consolidated benchmark replaces the previous split implementation:

- ~~`tests/test_ai_requester_lot.py`~~ → `benchmarks/benchmark.py`
- ~~`tests/run_rating.py`~~ → `benchmarks/cli.py`

The new implementation provides:
- ✅ Cleaner separation of concerns
- ✅ Better code organization
- ✅ Comprehensive documentation
- ✅ Type hints and docstrings
- ✅ Consistent naming conventions
- ✅ No code duplication
- ✅ Easier to maintain and extend

## Tips

1. **Use threaded mode** for the best experience when rating multiple models
2. **Resume interrupted runs** using `--start-file` or `--start-index`
3. **Check progress** in `metrics_progress.csv` during long runs
4. **Batch mode** is best for quick timing tests without rating
5. **Expected values auto-score**: If the AI response matches expected values exactly, full points are awarded automatically

## Troubleshooting

**Problem**: Benchmark interrupted/crashed  
**Solution**: Use `--start-index` to resume from where you left off

**Problem**: Want to re-run specific file  
**Solution**: Delete its entries from `metrics_progress.csv` or use a new batch

**Problem**: Rating taking too long  
**Solution**: Use threaded mode - you can rate while the next inference is running

## Future Enhancements

Potential improvements for future versions:
- Automated rating using fuzzy matching
- Parallel model evaluation
- Performance profiling and optimization
- Statistical analysis and visualization
- Export to different formats (HTML, Markdown)
- Integration with CI/CD pipelines
