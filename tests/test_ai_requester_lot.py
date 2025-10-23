"""Compatibility shim for old test_ai_requester_lot.py benchmark functions.

DEPRECATED: These functions have been moved to the benchmarks package.

Old usage (as tests):
    pytest tests/test_ai_requester_lot.py::test_batch_invoice_to_json
    pytest tests/test_ai_requester_lot.py::test_evaluate_models_capabilities

New usage (as benchmarks):
    python -m benchmarks.cli batch
    python -m benchmarks.cli rate
    python -m benchmarks.cli threaded

For more information, see benchmarks/README.md

Note: These are not real unit tests, they are benchmark functions.
They are preserved here for backward compatibility but will be removed
in a future version.
"""

import warnings

import pytest

# Show deprecation warning
warnings.warn(
    "test_ai_requester_lot.py is deprecated. Use the benchmarks package instead. "
    "See benchmarks/README.md for details.",
    DeprecationWarning,
    stacklevel=2
)


@pytest.mark.skip(reason="Deprecated: Use 'python -m benchmarks.cli batch' instead")
def test_batch_invoice_to_json():
    """DEPRECATED: Use 'python -m benchmarks.cli batch' instead."""
    from benchmarks import benchmark_batch
    benchmark_batch()


@pytest.mark.skip(reason="Deprecated: Use 'python -m benchmarks.cli rate' instead")
def test_evaluate_models_capabilities():
    """DEPRECATED: Use 'python -m benchmarks.cli rate' instead."""
    from benchmarks import benchmark_with_rating
    benchmark_with_rating()


@pytest.mark.skip(reason="Deprecated: Use 'python -m benchmarks.cli threaded' instead")
def test_evaluate_models_capabilities_threaded():
    """DEPRECATED: Use 'python -m benchmarks.cli threaded' instead."""
    from benchmarks import benchmark_threaded
    benchmark_threaded()
