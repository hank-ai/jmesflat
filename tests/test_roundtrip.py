"""Test a flatten/unflatten round trip"""

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
        "mixedArray[1].mixed Array Object 1 Key": "spaces demo",
        "mixedArray[2]": 12345,
        "mixedArray[3][0].@subArray": "@ symbol demo",
        "mixedArray[3][1].@subArray": "@ symbol demo",
        "mixedArray[3][2].@subArray": "@ symbol demo",
        "mixedArray[4].mixed-array-object-2-key": "dashed key demo",
    },
    "Outer Object Key 2": {
        "deepNest.a[0].b": 1,
        "deepNest.a[1].c.d[0].e": "f",
        "deepNest.a[1].c.d[0].g": "h",
        "deepNest.a[1].c.d[1].e": "f1",
        "mixedArray[0]": "mixed array string",
        "mixedArray[1].mixed Array Object 1 Key": "spaces are accepted",
        "mixedArray[2]": 12345,
        "mixedArray[3][0].@subArray": "handle an @ symbol",
        "mixedArray[3][1].@subArray": "handle an @ symbol",
        "mixedArray[3][2].@subArray": "handle an @ symbol",
        "mixedArray[4].mixed-array-object-2-key": "handle a dashed key",
    },
}


def test_roundtrip():
    flat = jf.flatten(TEST_NEST, level=1)
    assert flat == EXPECTED_FLAT
    assert jf.unflatten(flat, level=1) == TEST_NEST
    with pytest.raises(ValueError, match="`level` parameter"):
        jf.flatten([{"whoops": "outer list w/ level > 0!!"}], 1)
