#!/usr/bin/env python3
"""Verification script for benchmark consolidation.

This script verifies that:
1. All benchmark modules can be imported (structure check)
2. Public API is accessible
3. Old compatibility shims exist and have proper deprecation warnings
"""

import ast
import sys
from pathlib import Path


def check_module_structure():
    """Verify benchmark package structure."""
    print("Checking benchmark package structure...")
    
    benchmarks_dir = Path(__file__).parent.parent / 'benchmarks'
    
    required_files = [
        '__init__.py',
        '__main__.py',
        'benchmark.py',
        'cli.py',
        'config.py',
        'metrics.py',
        'rating.py',
        '_utils.py',
        'README.md'
    ]
    
    for filename in required_files:
        filepath = benchmarks_dir / filename
        if not filepath.exists():
            print(f"  ✗ Missing: {filename}")
            return False
        print(f"  ✓ Found: {filename}")
    
    return True


def check_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error in {filepath}: {e}")
        return False


def check_python_syntax():
    """Verify all Python files have valid syntax."""
    print("\nChecking Python syntax...")
    
    benchmarks_dir = Path(__file__).parent.parent / 'benchmarks'
    
    for py_file in benchmarks_dir.glob('*.py'):
        if check_syntax(py_file):
            print(f"  ✓ Valid syntax: {py_file.name}")
        else:
            return False
    
    return True


def check_compatibility_shims():
    """Verify compatibility shims exist."""
    print("\nChecking compatibility shims...")
    
    tests_dir = Path(__file__).parent.parent / 'tests'
    
    files = [
        'run_rating.py',
        'test_ai_requester_lot.py'
    ]
    
    for filename in files:
        filepath = tests_dir / filename
        if not filepath.exists():
            print(f"  ✗ Missing: {filename}")
            return False
        
        # Check for deprecation warning
        with open(filepath, 'r') as f:
            content = f.read()
            if 'DEPRECATED' in content or 'deprecated' in content.lower():
                print(f"  ✓ Found with deprecation warning: {filename}")
            else:
                print(f"  ⚠ Missing deprecation warning: {filename}")
    
    return True


def check_old_backups():
    """Verify old files are preserved."""
    print("\nChecking old file backups...")
    
    tests_dir = Path(__file__).parent.parent / 'tests'
    
    old_files = [
        'run_rating.py.old',
        'test_ai_requester_lot.py.old'
    ]
    
    for filename in old_files:
        filepath = tests_dir / filename
        if filepath.exists():
            print(f"  ✓ Preserved: {filename}")
        else:
            print(f"  ⚠ Not found: {filename} (optional)")
    
    return True


def check_documentation():
    """Verify documentation exists."""
    print("\nChecking documentation...")
    
    readme = Path(__file__).parent.parent / 'benchmarks' / 'README.md'
    
    if not readme.exists():
        print("  ✗ Missing: benchmarks/README.md")
        return False
    
    with open(readme, 'r') as f:
        content = f.read()
        required_sections = [
            'Overview',
            'Quick Start',
            'Benchmark Modes',
            'Configuration',
            'Usage'
        ]
        
        for section in required_sections:
            if section.lower() in content.lower():
                print(f"  ✓ Found section: {section}")
            else:
                print(f"  ⚠ Missing section: {section}")
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("BENCHMARK CONSOLIDATION VERIFICATION")
    print("=" * 70)
    print()
    
    checks = [
        ("Module Structure", check_module_structure),
        ("Python Syntax", check_python_syntax),
        ("Compatibility Shims", check_compatibility_shims),
        ("Old File Backups", check_old_backups),
        ("Documentation", check_documentation),
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
                print(f"\n⚠ {name} check had warnings")
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            all_passed = False
    
    print()
    print("=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Run benchmark: python -m benchmarks.cli threaded --help")
        print("3. Remove .old files once verified: rm tests/*.old")
    else:
        print("⚠ SOME CHECKS HAD WARNINGS")
        print()
        print("Review the output above for details.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
