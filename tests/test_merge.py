"""test `merge()` operations"""

import json
from copy import deepcopy
from typing import Any, Callable, Literal, Optional, Union

import pytest

import jmesflat as jf


BASIC_NEST1 = jf.unflatten(
    {
        "a.b[0].c": "nest1->a->b->0->>c",
        "a.b[0].d[0]": "nest1->a->b->0->d->>0",
        "a.e": "nest1->a->e",
    }
)
BASIC_NEST2 = jf.unflatten(
    {
        "a.b[0].c": "nest2->a->b->0->>c",
        "a.b[0].d[0]": "nest2->a->b->0->d->>0",
        "a.e": "nest2->a->e",
    }
)


@pytest.mark.parametrize(
    argnames=(
        "title",
        "nest1",
        "nest2",
        "expected",
        "level",
        "array_merge",
        "level_match_funcs",
        "discard_check",
    ),
    argvalues=[
        (
            "Basic Overwrite Merge",
            BASIC_NEST1,
            BASIC_NEST2,
            BASIC_NEST2,
            0,
            "none",
            None,
            None,
        ),
        (
            "Basic Top Down Merge",
            BASIC_NEST1,
            BASIC_NEST2,
            {
                "a": {
                    "b": [
                        {"c": "nest1->a->b->0->>c", "d": ["nest1->a->b->0->d->>0"]},
                        {"c": "nest2->a->b->0->>c", "d": ["nest2->a->b->0->d->>0"]},
                    ],
                    "e": "nest1->a->e",
                }
            },
            0,
            "topdown",
            None,
            None,
        ),
        (
            "Basic Bottom Up Merge",
            BASIC_NEST1,
            BASIC_NEST2,
            {
                "a": {
                    "b": [
                        {
                            "c": "nest1->a->b->0->>c",
                            "d": ["nest1->a->b->0->d->>0", "nest2->a->b->0->d->>0"],
                        },
                        {"c": "nest2->a->b->0->>c"},
                    ],
                    "e": "nest2->a->e",
                }
            },
            0,
            "bottomup",
            None,
            None,
        ),
        (
            "Basic Bottom Up Merge, Nest 2 'c' Discarded",
            BASIC_NEST1,
            BASIC_NEST2,
            {
                "a": {
                    "b": [
                        {
                            "c": "nest1->a->b->0->>c",
                            "d": ["nest1->a->b->0->d->>0", "nest2->a->b->0->d->>0"],
                        }
                    ],
                    "e": "nest2->a->e",
                }
            },
            0,
            "bottomup",
            None,
            lambda key, _: key.endswith("c"),
        ),
        (
            "Deduped Level 1 Merge w/ Custom Match Func",  # title
            {  # nest1
                "nest1-0": {"id": 0, "data": ["nest1-01", "nest1-02", 0]},
                "nest1-1": {"id": 1, "data": ["nest-11", "nest1-12", 1]},
            },
            {  # nest2
                "nest2-1": {"id": 1, "data": ["nest-11", "nest2-12", 1]},
                "nest2-2": {"id": 2, "data": ["nest2-21", "nest2-22", 2]},
            },
            {  # expected
                "nest1-0": {"data": ["nest1-01", "nest1-02", 0], "id": 0},
                "nest1-1": {"data": ["nest-11", "nest1-12", 1, "nest2-12"], "id": 1},
                "nest2-2": {"data": ["nest2-21", "nest2-22", 2], "id": 2},
            },
            1,  # level
            "deduped",  # array_match
            {  # level_match_funcs
                1: lambda _, next_nest1, nest2: (
                    nest2.pop(_k)
                    if any(v["id"] == next_nest1["id"] for k, v in nest2.items() if str(_k := k))
                    else {}
                )
            },
            None,
        ),
    ],
)
def test_merge(
    title: str,
    nest1: Union[dict[str, Any], list[Any]],
    nest2: Union[dict[str, Any], list[Any]],
    expected: Union[dict[str, Any], list[Any]],
    level: int,
    array_merge: Literal["none", "topdown", "bottomup", "deduped"],
    level_match_funcs: Optional[dict[int, jf.LevelMatchFunc]],
    discard_check: Optional[Callable[[str, Any], bool]],
):
    """Test `merge()` function with all parameter variants."""
    print(f"Running {title!r}.")
    nest1_original = deepcopy(nest1)
    nest2_original = deepcopy(nest2)
    merged = jf.merge(nest1, nest2, level, array_merge, level_match_funcs, discard_check)
    print(json.dumps(merged, indent=2))
    assert merged == expected
    assert nest1 == nest1_original
    assert nest2 == nest2_original
