# Migration Guide: Old Benchmark → New Benchmark

This guide helps you transition from the old split benchmark files to the new consolidated benchmarks package.

## Quick Reference

### Old Way → New Way

| Old Command | New Command |
|------------|-------------|
| `python tests/run_rating.py` | `python -m benchmarks.cli threaded` |
| `python tests/run_rating.py --start-file invoice-test-5.pdf` | `python -m benchmarks.cli threaded --start-file invoice-test-5.pdf` |
| `python tests/run_rating.py --start-index 5` | `python -m benchmarks.cli threaded --start-index 5` |
| `pytest tests/test_ai_requester_lot.py::test_batch_invoice_to_json` | `python -m benchmarks.cli batch` |
| `pytest tests/test_ai_requester_lot.py::test_evaluate_models_capabilities` | `python -m benchmarks.cli rate` |

### Old Imports → New Imports

| Old Import | New Import |
|-----------|-----------|
| `from tests.test_ai_requester_lot import test_batch_invoice_to_json` | `from benchmarks import benchmark_batch` |
| `from tests.test_ai_requester_lot import test_evaluate_models_capabilities` | `from benchmarks import benchmark_with_rating` |
| `from tests.test_ai_requester_lot import test_evaluate_models_capabilities_threaded` | `from benchmarks import benchmark_threaded` |

## What Changed?

### File Reorganization

**Before:**
```
tests/
├── run_rating.py                    (50 lines)
└── test_ai_requester_lot.py         (563 lines)
```

**After:**
```
benchmarks/
├── __init__.py          # Package exports
├── __main__.py          # Makes package runnable
├── benchmark.py         # Core benchmark functions (418 lines)
├── cli.py               # Command-line interface (94 lines)
├── config.py            # Configuration (118 lines)
├── metrics.py           # Metrics collection (113 lines)
├── rating.py            # Interactive rating (114 lines)
├── _utils.py            # Utilities (115 lines)
└── README.md            # Documentation (265 lines)

tests/
├── run_rating.py        # Compatibility wrapper with deprecation warning
├── test_ai_requester_lot.py  # Compatibility shim for pytest
├── run_rating.py.old    # Original preserved
└── test_ai_requester_lot.py.old  # Original preserved
```

### Function Name Changes

| Old Name | New Name | Reason |
|----------|----------|--------|
| `test_batch_invoice_to_json()` | `benchmark_batch()` | Not a test, it's a benchmark |
| `test_evaluate_models_capabilities()` | `benchmark_with_rating()` | More descriptive name |
| `test_evaluate_models_capabilities_threaded()` | `benchmark_threaded()` | Clearer, shorter name |
| `_format_elapsed()` | `format_elapsed()` | Now public in _utils module |
| `_next_batch_folder()` | `next_batch_folder()` | Now public in _utils module |

### Configuration Changes

**Before:** Models and expected results embedded in test_ai_requester_lot.py

**After:** Centralized in `benchmarks/config.py`

```python
# Import models
from benchmarks.config import MODELS, EXPECTED_RESULTS

# Use in your code
for model in MODELS:
    print(f"{model['name']}:{model['parameters']}b")
```

## Step-by-Step Migration

### For CLI Users

1. **Update your scripts:**
   ```bash
   # Old
   python tests/run_rating.py --start-file invoice-test-5.pdf
   
   # New
   python -m benchmarks.cli threaded --start-file invoice-test-5.pdf
   ```

2. **Update your documentation:**
   - Point to `benchmarks/README.md` for usage instructions
   - Update any tutorial or onboarding docs

3. **Update CI/CD pipelines:**
   - Replace old command paths with new ones
   - No functional changes needed

### For Python Developers

1. **Update imports:**
   ```python
   # Old
   from tests.test_ai_requester_lot import (
       test_batch_invoice_to_json,
       test_evaluate_models_capabilities_threaded
   )
   
   # New
   from benchmarks import benchmark_batch, benchmark_threaded
   ```

2. **Update function calls:**
   ```python
   # Old
   test_evaluate_models_capabilities_threaded()
   
   # New
   benchmark_threaded()
   ```

3. **Access configuration:**
   ```python
   # Old - embedded in test file
   models = [{"name": "qwen2.5vl", ...}, ...]
   
   # New - import from config
   from benchmarks.config import MODELS, EXPECTED_RESULTS
   ```

## Backward Compatibility

The old files still work with deprecation warnings:

```bash
$ python tests/run_rating.py --start-file invoice-test-5.pdf
Note: This script is deprecated. Use 'python -m benchmarks.cli threaded' instead.
Forwarding to: python -m benchmarks.cli threaded --start-file invoice-test-5.pdf

# Then proceeds with benchmark...
```

This gives you time to update your scripts gradually.

## Benefits of Migration

1. **Cleaner code structure** - Each module has a single responsibility
2. **Better documentation** - Comprehensive README with examples
3. **Type safety** - Type hints throughout the codebase
4. **Easier maintenance** - Modular design makes changes simpler
5. **No duplication** - Shared utilities consolidated
6. **Better CLI** - More modes, better help text
7. **Future-proof** - Easy to add new features

## Timeline

- **Now**: Both old and new systems work (with deprecation warnings)
- **Soon**: Remove .old backup files (after verification)
- **Future**: Remove compatibility shims (in next major version)

## Need Help?

- Read `benchmarks/README.md` for detailed usage instructions
- Check `BENCHMARK_CONSOLIDATION_SUMMARY.md` for technical details
- Run `python -m benchmarks.cli --help` to see available commands
- Run verification: `python utils/verify_benchmark_consolidation.py`

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'benchmarks'`  
**Solution**: Make sure you're running from the repository root or the package is installed

**Problem**: Old scripts not working  
**Solution**: The compatibility layer requires the new benchmarks package. Migrate to the new CLI

**Problem**: Need to re-run specific benchmarks  
**Solution**: Delete entries from `tests/test_data/json_batches/metrics_progress.csv` or use a new batch number

**Problem**: Metrics CSV missing or corrupted  
**Solution**: The new metrics module auto-creates CSV with proper headers if missing

## Questions?

If you have questions about the migration, please:
1. Check the documentation in `benchmarks/README.md`
2. Review the consolidation summary in `BENCHMARK_CONSOLIDATION_SUMMARY.md`
3. Open an issue on GitHub with the `benchmarks` label
