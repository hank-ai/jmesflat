"""Constants used as default arg values"""

import re
from collections.abc import Callable
from typing import Any


PATH_ELEMENT_REGEX: re.Pattern = re.compile(r"(^|[\.\[\]])([^\.\[\]]*)")
MISSING_ARRAY_ENTRY_VALUE: Callable[[str, Any], Any] = lambda *_: None
ATOMIC_TYPES: tuple[type, ...] = (int, float, bool, str, type(None))
DISCARD_CHECK: Callable[[str, Any], bool] | None = None
ESCAPED_CHARS: str = "@- "
