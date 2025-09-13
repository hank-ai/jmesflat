"""
Flatten, unflatten, and merge deeply nested JSON objects using JMESPath notation.

jmesflat extends JMESPath with powerful utilities for working with complex nested
structures through flattened key-value representations (e.g., "a.b[0].c").

Key features:
- Flatten nested objects to dotted-key notation
- Reconstruct nested structures from flattened representations
- Deep merge with configurable array handling strategies
- Clean/filter nested objects with custom logic
- Support for spaces and special characters in keys
"""

__version__ = "0.1.1"

from . import constants, utils
from ._clean import clean
from ._flatten import flatten
from ._merge import merge, LevelMatchFunc
from ._unflatten import unflatten

__all__ = ["clean", "constants", "flatten", "merge", "unflatten", "utils", "LevelMatchFunc"]
