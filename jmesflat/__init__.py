"""Initialize jmesflat package"""

__version__ = "0.0.2"

from . import constants, utils
from ._clean import clean
from ._flatten import flatten
from ._merge import merge, LevelMatchFunc
from ._unflatten import unflatten

__all__ = ["clean", "constants", "flatten", "merge", "unflatten", "utils", "LevelMatchFunc"]
