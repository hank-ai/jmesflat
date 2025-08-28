"""Implement the `flatten` function"""

from collections.abc import Callable
from typing import Any, overload

import jmespath as jp

from . import constants
from . import utils


@overload
def flatten(
    nested: dict[str, Any],
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> utils.FlattenedDict: ...


@overload
def flatten(
    nested: list[Any],
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> utils.FlattenedList: ...


def flatten(
    nested: dict[str, Any] | list[Any],
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> dict[str, Any]:
    """
    Given a nested json object, return {jmespath_pattern: value} for all
    atomic values (see constants.ATOMIC_TYPES) and empty containers.

    Args:
        nested: a flattened jsonable dict object.
        level: the nesting level at which the unflatten operation is applied
        discard_check: the callable to which flat keys and values are supplied \
        to determine if they should be dropped. a return value of `True` \
        triggers a drop. Pass `None` (default) to fall back to the global \
        `constants.DISCARD_CHECK` if such has been defined.

    Returns:
        dict[str, Any]: flattened json object.
    """

    if level:
        if not isinstance(nested, dict):
            raise ValueError(
                f"`level` parameter does not support array traversal. {type(nested)=!r}"
            )
        return {k: flatten(v, level - 1, discard_check) for k, v in nested.items()}

    return_type = utils.FlattenedDict if isinstance(nested, dict) else utils.FlattenedList

    discard_check = discard_check or constants.DISCARD_CHECK

    def _recurs_flatten(
        _nest: dict[str, Any] | list[dict[str, Any]],
        _parent_keys: list[str | int],
        _out_dict: dict[str, Any],
    ):
        query = utils.escaped_query_from_path_elements(_parent_keys)
        this_entry = jp.search(query, _nest)
        if isinstance(this_entry, dict) and this_entry:
            for _k in this_entry:
                _recurs_flatten(_nest, _parent_keys + [_k], _out_dict)
            return
        if isinstance(this_entry, list) and this_entry:
            for idx, _ in enumerate(this_entry):
                _recurs_flatten(_nest, _parent_keys + [idx], _out_dict)
            return
        flat_key = utils.flat_key_from_path_elements(_parent_keys)
        if not (callable(discard_check) and discard_check(flat_key, this_entry)):
            _out_dict[flat_key] = this_entry

    out_dict: dict[str, Any] = {}
    for key, val in (
        nested if isinstance(nested, dict) else dict(enumerate(nested))  # type:ignore[arg-type]
    ).items():
        flat_key = f"[{key}]" if isinstance(key, int) else key
        empty_container = isinstance(val, (dict, list)) and not val
        if not isinstance(val, constants.ATOMIC_TYPES) and not empty_container:
            _recurs_flatten(nested, [key], out_dict)
        elif not (callable(discard_check) and discard_check(flat_key, val)):
            out_dict[flat_key] = val

    return return_type(
        sorted(out_dict.items(), key=lambda x: utils.raw_jpquery_path_elements(x[0]))
    )
