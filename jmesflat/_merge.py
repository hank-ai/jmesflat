"""Implement the `merge` function"""

from typing import Any, Callable, Literal, Optional, Union

import jmespath as jp

from ._flatten import flatten
from ._unflatten import unflatten


def merge(
    nest1: Union[dict[str, Any], list[Any]],
    nest2: Union[dict[str, Any], list[Any]],
    level: int = 0,
    array_merge: Literal["overwrite", "topdown", "bottomup"] = "overwrite",
    discard_check: Optional[Callable[[str, Any], bool]] = None,
) -> Union[dict[str, Any], list[Any]]:
    """
    Return the object resulting from a nested merge of nest1 and nest2
    with nest2 values having priority in the event of a key collision.

    Args:
        nest1: a nested json object
        nest2: the nested json object to merge into nest1
        level: the level at which the merge operation should occur
        array_merge: if "overwrite" (default), array entries from nest2 will \
        overwrite entries from nest1. if "topdown", array entries from nest2 \
        will extend the topmost array having a matching index. if "bottomup", \
        array entries from nest2 will extend the lowest matched-index array.
        discard_check: optional function that will disregard atomic values \
        *from nest2* if discard_check(flat_key, value) returns True. allows \
        selective retention of values in nest1

    Returns:
        dict[str, Any]: the merged object
    """

    if level:
        if not isinstance(nest1, dict):
            raise ValueError(
                f"`level` parameter does not support array traversal. {type(nest1)=!r}"
            )
        if not isinstance(nest2, dict):
            raise ValueError(
                f"`level` parameter does not support array traversal. {type(nest2)=!r}"
            )
        return {
            k: merge(v, nest2.get(k) or type(v)(), level - 1, array_merge, discard_check)
            for k, v in nest1.items()
        }

    flat1 = flatten(nest1)
    flat2 = flatten(nest2, discard_check=discard_check)

    if array_merge == "overwrite":
        return unflatten(flat1 | flat2)

    partition_func = str.partition if array_merge == "topdown" else str.rpartition

    prefix_replacements = {
        prefix: len(jp.search(prefix, nest1) or "")
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
