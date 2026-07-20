"""Implement the `unflatten` function"""

import logging
import re
from collections.abc import Callable
from typing import Any, overload

import jmespath as jp

from . import constants
from . import utils


logger = logging.getLogger(__name__)


@overload
def unflatten(
    flattened: utils.FlattenedList,
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
    preserve_array_indices: bool = True,
) -> list[Any]: ...


@overload
def unflatten(
    flattened: utils.FlattenedDict,
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
    preserve_array_indices: bool = True,
) -> dict[str, Any]: ...


@overload
def unflatten(
    flattened: dict[str, Any],
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
    preserve_array_indices: bool = True,
) -> dict[str, Any] | list[Any]: ...


def unflatten(
    flattened: dict[str, Any],
    level: int = 0,
    discard_check: Callable[[str, Any], bool] | None = None,
    preserve_array_indices: bool = True,
) -> dict[str, Any] | list[Any]:
    """
    Given a dict of {jmespath_search_ query: value}, return its nested form.

    Args:
        flattened: a flattened json object or array (note: a flattened array \
        is itself a dict).
        level: the nesting level at which the unflatten operation is applied
        discard_check: the callable to which flat keys and values are supplied \
        to determine if they should be dropped. a return value of `True` \
        triggers a drop. Pass `None` (default) to fall back to the global \
        `constants.DISCARD_CHECK` if such has been defined.
        preserve_array_indices: if True (default), arrays are padded using \
        constants.MISSING_ARRAY_ENTRY_VALUE(flat key, value) to preserve the \
        indices as they were supplied in `flattened`. e.g. unflattening \
        `{"test[1]": 1}` with the default missing array entry function would \
        result in `{"test": [None, 1]}`. if False, missing indices are skipped, \
        and the example outputs `{"test": [1]}`.

    Returns:
        dict[str, Any] | list[Any]: Returns dict[str, Any] when level > 0 \
        or when no keys start with '['. Returns list[Any] when level == 0 and \
        all keys start with '['.

    Raises:
        ValueError: When keys are ambiguous (some start with '[' and some don't) \
        at level 0, indicating mixed object and array structure.
    """

    if level:
        return {
            k: unflatten(v, level - 1, discard_check, preserve_array_indices)
            for k, v in flattened.items()
        }

    if any(k.startswith("[") for k in flattened) and not all(k.startswith("[") for k in flattened):
        raise ValueError(
            "Ambiguous Entry Detected: Top level keys indicate both object and array."
        )

    discard_check = discard_check or constants.DISCARD_CHECK

    final_element_pattern = re.compile(rf"(.*?){constants.PATH_ELEMENT_REGEX.pattern}$")

    def _update_nest(path: str, value: Any, nest: dict[str, Any]):
        if callable(discard_check) and discard_check(path, value):
            # being paranoid. most are caught via equivalent check in _update_nest
            # calling loop below. adding `pragma: no cover` tag.
            return  # pragma: no cover
        if "." not in path and "]" not in path:
            nest[path.strip('"')] = value
            return
        if path.endswith("]"):
            parent_path = path
            child_key = ""
        elif final_element_match := final_element_pattern.match(path):
            parent_path, _, child_key = final_element_match.groups()
        else:
            logger.warning("Skipping invalid unflatten path: '%s'", path)
            return
        if parent_path.endswith("]"):
            pkey, _, pidx = parent_path[:-1].rpartition("[")
            if not isinstance(_list := jp.search(utils.jpquery_from_flat_key(pkey), nest), list):
                _update_nest(pkey, _list := [], nest)
            if child_key and len(_list) > int(pidx):
                _list[int(pidx)][child_key.strip('"')] = value
                return
            while preserve_array_indices and len(_list) < int(pidx):
                _missing = constants.MISSING_ARRAY_ENTRY_VALUE(path, value)
                if callable(discard_check) and discard_check(path, _missing):
                    break
                _list.append(_missing)
            _list.append({child_key.strip('"'): value} if child_key else value)
            return
        elif child_key and not isinstance(
            jp.search(utils.jpquery_from_flat_key(parent_path), nest), dict
        ):
            _update_nest(parent_path, {}, nest)
        jp.search(utils.jpquery_from_flat_key(parent_path), nest)[child_key.strip('"')] = value

    out_dict: dict[str, Any] = {}
    pop_top: bool = False
    for path, value in sorted(
        flattened.items(), key=lambda x: utils.raw_jpquery_path_elements(x[0])
    ):
        if pop_top or path.startswith("["):
            pop_top = True
            path = f"__top__{path}"
        if callable(discard_check) and discard_check(path, value):
            continue
        if isinstance(value, (dict, list)) and not value:
            # copy empty containers before planting them: deeper sibling keys
            # descend INTO the planted object, and inserting into a caller
            # supplied `{}`/`[]` would mutate the input (and anything that
            # shares a reference to it)
            value = type(value)()
        _update_nest(path, value, out_dict)
    return out_dict.pop("__top__") if pop_top else out_dict
