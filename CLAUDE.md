# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

jmesflat is a Python library that extends JMESPath functionality to provide flattening, unflattening, and merging capabilities for deeply nested JSON objects. The library enables working with complex nested structures using flattened key representations (e.g., "a.b[0].c").

## Development Commands

### Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install package in development mode with dependencies
pip install -e .

# Install test dependencies
pip install pytest
```

### Testing
```bash
# Run all tests
pytest tests/

# Run tests with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_merge.py
pytest tests/test_roundtrip.py

# Run tests using unittest (alternative)
python -m unittest discover tests
```

### Test Coverage
```bash
# Install coverage dependencies
pip install pytest-cov

# Run tests with coverage report in terminal
pytest tests/ --cov=jmesflat

# Run tests with detailed terminal coverage (shows missing lines)
pytest tests/ --cov=jmesflat --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=jmesflat --cov-report=html

# Generate both terminal and HTML reports
pytest tests/ --cov=jmesflat --cov-report=term --cov-report=html

# View HTML coverage report
# Open htmlcov/index.html in a browser
```

#### VSCode Integration
The project is configured to automatically generate coverage reports when running tests through VSCode's testing interface. The `.vscode/settings.json` includes:
- Automatic HTML coverage report generation in `htmlcov/`
- Terminal coverage output in the test results
- Test discovery on file save

To run tests with coverage in VSCode:
1. Open the Testing sidebar (flask icon)
2. Run tests using the play buttons
3. Coverage reports are automatically generated in `htmlcov/index.html`

### Building and Distribution
```bash
# Build distribution packages (uses flit)
pip install flit
flit build

# Install from source
pip install .
```

## Code Architecture

The jmesflat package (`/workspace/jmesflat/`) consists of four core operations, each implemented in a separate module:

### Core Modules

1. **`_flatten.py`** - Contains the `flatten()` function that converts nested objects into flat key-value pairs using JMESPath notation
   - Handles arrays with bracket notation: `key[index]`
   - Supports multi-level flattening with the `level` parameter
   - Preserves atomic types including empty lists/dicts

2. **`_unflatten.py`** - Contains the `unflatten()` function that reconstructs nested objects from flattened representations
   - Handles array index gaps with configurable padding values
   - Supports partial unflattening at specified depth levels
   - Uses `MISSING_ARRAY_ENTRY_VALUE` from constants for array padding

3. **`_merge.py`** - Contains the `merge()` function for combining deeply nested objects
   - Supports three merge strategies: overwrite (default), topdown, bottomup
   - Allows custom merge logic via `level_match_funcs` parameter
   - Array merge modes: overwrite, extend at top/bottom, deduped with custom matching

4. **`_clean.py`** - Contains the `clean()` function for filtering nested objects
   - Accepts a `discard_check` function to determine which keys/values to remove
   - Works recursively through nested structures

### Supporting Modules

- **`constants.py`** - Global configuration defaults
  - `DISCARD_CHECK`: Global filter function for clean operations
  - `MISSING_ARRAY_ENTRY_VALUE`: Callable for array padding values during unflatten
  
- **`utils.py`** - Internal utility functions for the library

### Key Design Patterns

1. **Level Parameter**: Most functions accept a `level` parameter to control operation depth, allowing partial processing of nested structures

2. **Array Handling**: Special attention to array merging with multiple strategies (overwrite, topdown, bottomup, deduped)

3. **JMESPath Integration**: Built on top of jmespath library, using its path notation for flattened keys

4. **Type Preservation**: Empty collections ({} and []) are treated as atomic values in flattened form

## Testing Structure

- `tests/test_merge.py` - Parametrized tests for merge functionality with various scenarios
- `tests/test_roundtrip.py` - Tests that verify flatten/unflatten operations are reversible
- `testbench.py` - Interactive examples and experimentation file (not part of test suite)

## Important Notes

- Python 3.10+ required (despite README saying 3.9+, pyproject.toml specifies >=3.10)
- Main dependency: jmespath
- Uses flit for build/packaging
- The library handles special characters in keys (spaces, @, -) by design