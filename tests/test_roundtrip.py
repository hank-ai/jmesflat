"""Test a flatten/unflatten round trip"""

from copy import deepcopy

import pytest

import jmesflat as jf

TEST_NEST = {
    "Outer Object Key 1": {
        "deepNest": {"a": [{"b": 1}, {"c": {"d": [{"e": "f", "g": "h"}, {"e": "f1"}]}}]},
        "mixedArray": [
            "mixed array string",
            {"mixed Array Object 1 Key": "spaces demo"},
            12345,
            [
                {"@subArray": "@ symbol demo"},
                {"@subArray": "@ symbol demo"},
                {"@subArray": "@ symbol demo"},
            ],
            {"mixed-array-object-2-key": "dashed key demo"},
        ],
    },
    "Outer Object Key 2": {
        "deepNest": {"a": [{"b": 1}, {"c": {"d": [{"e": "f", "g": "h"}, {"e": "f1"}]}}]},
        "mixedArray": [
            "mixed array string",
            {"mixed Array Object 1 Key": "spaces are accepted"},
            12345,
            [
                {"@subArray": "handle an @ symbol"},
                {"@subArray": "handle an @ symbol"},
                {"@subArray": "handle an @ symbol"},
            ],
            {"mixed-array-object-2-key": "handle a dashed key"},
        ],
    },
}

EXPECTED_FLAT = {
    "Outer Object Key 1": {
        "deepNest.a[0].b": 1,
        "deepNest.a[1].c.d[0].e": "f",
        "deepNest.a[1].c.d[0].g": "h",
        "deepNest.a[1].c.d[1].e": "f1",
        "mixedArray[0]": "mixed array string",
        'mixedArray[1]."mixed Array Object 1 Key"': "spaces demo",
        "mixedArray[2]": 12345,
        'mixedArray[3][0]."@subArray"': "@ symbol demo",
        'mixedArray[3][1]."@subArray"': "@ symbol demo",
        'mixedArray[3][2]."@subArray"': "@ symbol demo",
        'mixedArray[4]."mixed-array-object-2-key"': "dashed key demo",
    },
    "Outer Object Key 2": {
        "deepNest.a[0].b": 1,
        "deepNest.a[1].c.d[0].e": "f",
        "deepNest.a[1].c.d[0].g": "h",
        "deepNest.a[1].c.d[1].e": "f1",
        "mixedArray[0]": "mixed array string",
        'mixedArray[1]."mixed Array Object 1 Key"': "spaces are accepted",
        "mixedArray[2]": 12345,
        'mixedArray[3][0]."@subArray"': "handle an @ symbol",
        'mixedArray[3][1]."@subArray"': "handle an @ symbol",
        'mixedArray[3][2]."@subArray"': "handle an @ symbol",
        'mixedArray[4]."mixed-array-object-2-key"': "handle a dashed key",
    },
}


def test_roundtrip():
    flat = jf.flatten(TEST_NEST, level=1)
    assert flat == EXPECTED_FLAT
    assert jf.unflatten(flat, level=1) == TEST_NEST
    with pytest.raises(ValueError, match="`level` parameter"):
        jf.flatten([{"whoops": "outer list w/ level > 0!!"}], 1)


# A top level key needing quotes has no parent path to descend from. `flatten`
# escaped such a key only when its value was a container, so an atomic value
# emitted a traversable path that collided with a genuine nested path, and
# `unflatten` raised IndexError resolving the empty parent of a quoted key.
QUOTED_TOP_LEVEL_CASES = [
    ({"a.b": 1}, {'"a.b"': 1}),
    ({"a.b": [1]}, {'"a.b"[0]': 1}),
    ({"a.b": {"c": 1}}, {'"a.b".c': 1}),
    ({"a.b": {}}, {'"a.b"': {}}),
    ({"a.b": []}, {'"a.b"': []}),
    ({"a-b": 1}, {'"a-b"': 1}),
    ({"a b": 1}, {'"a b"': 1}),
    ({"@type": 1}, {'"@type"': 1}),
    ({"0": 1}, {'"0"': 1}),
    ({"plain": 1, "a.b": [1, 2]}, {'"a.b"[0]': 1, '"a.b"[1]': 2, "plain": 1}),
    # the collision: without the escape both of these flattened to "a.b"
    ({"a.b": 1, "a": {"b": 2}}, {'"a.b"': 1, "a.b": 2}),
    ([{"a.b": 1}], {'[0]."a.b"': 1}),
]


@pytest.mark.parametrize(argnames=("nested", "expected_flat"), argvalues=QUOTED_TOP_LEVEL_CASES)
def test_quoted_top_level_key_roundtrip(nested, expected_flat):
    """A top level key holding reserved chars survives a flatten/unflatten round trip."""
    original = deepcopy(nested)
    flat = jf.flatten(nested)
    assert flat == expected_flat
    assert jf.unflatten(flat) == original
    assert nested == original
