"""Implement the `merge` function"""

from collections.abc import Callable
from typing import Any, Literal, TypeVar, overload

import jmespath as jp

from . import utils
from ._clean import clean
from ._flatten import flatten
from ._unflatten import unflatten


T = TypeVar("T", dict[str, Any], list[Any])
LevelMatchFunc = Callable[[str, dict[str, Any], dict[str, Any]], dict[str, Any] | list[Any]]


def default_match(
    nest1_key: str, nest1: dict[str, Any], nest2: dict[str, Any]
) -> dict[str, Any] | list[Any]:
    """The default level match func. Requires direct key matches between nest1 and nest2."""
    match = nest2.pop(nest1_key, None) or type(nest1)()
    if not isinstance(match, (list, dict)):
        return {}
    return match


@overload
def merge(
    nest1: T,
    nest2: Any,
    level: int = 0,
    array_merge: Literal["overwrite", "topdown", "bottomup", "deduped"] = "overwrite",
    level_match_funcs: dict[int, LevelMatchFunc] | None = None,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> T: ...


@overload
def merge(
    nest1: Any,
    nest2: T,
    level: int = 0,
    array_merge: Literal["overwrite", "topdown", "bottomup", "deduped"] = "overwrite",
    level_match_funcs: dict[int, LevelMatchFunc] | None = None,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> T: ...


@overload
def merge(
    nest1: dict[str, Any] | list[Any],
    nest2: dict[str, Any] | list[Any],
    level: int = 0,
    array_merge: Literal["overwrite", "topdown", "bottomup", "deduped"] = "overwrite",
    level_match_funcs: dict[int, LevelMatchFunc] | None = None,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> dict[str, Any] | list[Any]: ...


def merge(
    nest1: dict[str, Any] | list[Any],
    nest2: dict[str, Any] | list[Any],
    level: int = 0,
    array_merge: Literal["overwrite", "topdown", "bottomup", "deduped"] = "overwrite",
    level_match_funcs: dict[int, LevelMatchFunc] | None = None,
    discard_check: Callable[[str, Any], bool] | None = None,
) -> dict[str, Any] | list[Any]:
    """
    Return the object resulting from a nested merge of nest1 and nest2
    with nest2 values having priority in the event of a key collision.

    NOTE: discard_check is *ONLY* applied to nest2 during a merge operation.
    This allows selective retention of nest1 values. Use `clean` on nest1
    to apply the discard_check yourself if needed.

    Args:
        nest1: a nested json object
        nest2: the nested json object to merge into nest1
        level: the level at which the merge operation should occur
        array_merge: if "overwrite" (default), array entries from nest2 will \
            overwrite entries from nest1. if "topdown", array entries from \
            nest2 will extend the topmost array having a matching index. \
            if "bottomup", the lowest matched-index array is extended. \
            if "deduped", the lowest matched-index array is extended with \
            only those values not already present in the equivalent nest1 \
            array.
        level_match_funcs: a dict of levels and corresponding LevelMatchFuncs. \
            Each LevelMatchFunc accepts a key from the current level in nest1, \
            the dict value for that key (must be a dict since the 'level' cannot \
            exceed the first array instance) and the current nest2 value. \
            The output of the LevelMatchFunc will be passed as the new nest2 value \
            as each level is descended. If no LevelMatchFunc is assigned, an exact \
            key match between the current nest1 and nest2 objects is assumed. \
            NOTE: level match funcs should *consume* nest2 as objects are returned. \
            I.e. the returned value should be 'popped' from nest2 for the typical \
            use case. An entry for level `0` that returns a static dict can be \
            used to merge the same value set into *all* level `0` nest1 objects. To \
            enable this functionality, nest2 should be supplied as an empty dict.
        discard_check: optional function that will disregard atomic values \
            *from nest2* if discard_check(flat_key, value) returns True. allows \
            selective retention of values in nest1

    Example:
        >>> merge(
        ...     nest1={
        ...         "nest1-0": {"id": 0, "data": ["nest1-01", "nest1-02", 0]},
        ...         "nest1-1": {"id": 1, "data": ["nest-11", "nest1-12", 1]},
        ...     },
        ...     nest2={
        ...         "nest2-1": {"id": 1, "data": ["nest-11", "nest2-12", 1]},
        ...         "nest2-2": {"id": 2, "data": ["nest2-21", "nest2-22", 2]},
        ...     },
        ...     level=1,
        ...     array_merge="deduped",
        ...     level_match_funcs={
        ...         1: lambda _, next_nest1, nest2: (
        ...             nest2.pop(_k) if any(
        ...                 v["id"] == next_nest1["id"] for k, v in nest2.items() if str(_k := k)
        ...             ) else {}
        ...         )
        ...     },
        ... )
        {
            'nest1-0': {'data': ['nest1-01', 'nest1-02', 0], 'id': 0},
            'nest1-1': {'data': ['nest-11', 'nest1-12', 1, 'nest2-12'], 'id': 1},
            'nest2-2': {'data': ['nest2-21', 'nest2-22', 2], 'id': 2}
        }

    Note on Type Safety:
        This function preserves types: dict inputs produce dict output, \
        list inputs produce list output. The implementation guarantees this \
        type preservation, though Python's type system cannot fully express \
        this guarantee due to the runtime dependency on flattened key patterns. \
        The @overload decorators provide type hints for common cases.

    Returns:
        The merged object with the same type as the inputs (dict or list)
    """
    if not nest2:
        return nest1

    if level:
        if not isinstance(nest1, dict):
            raise ValueError(
                f"`level` parameter does not support array traversal. {type(nest1)=!r}"
            )
        if not isinstance(nest2, dict):
            raise ValueError(
                f"`level` parameter does not support array traversal. {type(nest2)=!r}"
            )
        match_func: LevelMatchFunc = (level_match_funcs or {}).get(level, default_match)
        nest2_copy = nest2.copy()
        return {
            k: merge(
                v,
                match_func(k, v, nest2_copy),
                level - 1,
                array_merge,
                level_match_funcs,
                discard_check,
            )
            for k, v in nest1.items()
        } | clean(nest2_copy, discard_check=discard_check)
    flat1 = flatten(nest1)
    flat2 = flatten(
        # 'or' condition enables static values merge
        nest2 or (level_match_funcs or {}).get(0, lambda *_: {})("", {}, {}),
        discard_check=discard_check,
    )

    if array_merge == "overwrite":
        return unflatten(flat1 | flat2)

    partition_func = str.partition if array_merge == "topdown" else str.rpartition

    if array_merge == "deduped":
        flat2 = {k: v for k, v in flat2.items() if v != flat1.get(k, not v)}

    prefix_replacements = {
        prefix: len(jp.search(utils.jpquery_from_flat_key(prefix), nest1) or "")
        for prefix in set(partition_func(k, "[")[0] for k in flat2 if "[" in k)
    }
    flat2 = {
        (
            k.replace(
                f"{_parts[0]}[{_idx}]",
                f"{_parts[0]}[{prefix_replacements[_parts[0]] + int(_idx)}]",
                1,
            )
            if _parts[0] in prefix_replacements
            else k
        ): v
        for k, v in flat2.items()
        if (_parts := partition_func(k, "[")) and (_idx := _parts[-1].partition("]")[0])
    }
    return unflatten(flat1 | flat2, preserve_array_indices=array_merge == "topdown")
