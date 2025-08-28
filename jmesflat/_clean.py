"Implement the `clean` function"

from collections.abc import Callable
from typing import Any, TypeVar

from . import constants
from ._flatten import flatten
from ._unflatten import unflatten


# pylint: disable=invalid-name
T_TOP = TypeVar("T_TOP", dict[str, Any], list[Any])


def clean(
    nested: T_TOP,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> T_TOP:
    """
    Apply `discard_check` to all atomic values in nested and remove entries
    for which `discard_check` returns True.

    Args:
        nested: the nested object / array to clean
        discard_check: the callable to which flat keys and values are supplied \
        to determine if they should be dropped. a return value of `True` \
        triggers a drop. Pass `None` (default) to fall back to the global \
        `constants.DISCARD_CHECK` if such has been defined.

    Returns
        Union[dict[str, Any], list[Any]]: the cleaned nested object or array
    """

    discard_check = discard_check or constants.DISCARD_CHECK
    cleaned = unflatten(flatten(nested, discard_check=discard_check))
    assert isinstance(cleaned, type(nested))
    return cleaned
