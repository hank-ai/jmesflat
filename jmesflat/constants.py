"""Constants used as default arg values"""

import re

from typing import Any, Callable, Optional


PATH_ELEMENT_REGEX: re.Pattern = re.compile(r"(^|[\.\[\]])([^\.\[\]]*)")
MISSING_ARRAY_ENTRY_VALUE: Callable[[str, Any], Any] = lambda *_: None
ATOMIC_TYPES: tuple[type, ...] = (int, float, bool, str, type(None))
DISCARD_CHECK: Optional[Callable[[str, Any], bool]] = None
ESCAPED_CHARS: str = "@- "
