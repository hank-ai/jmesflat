"""Test `unflatten()` operations for uncovered lines"""

import pytest
import jmesflat as jf


def test_unflatten_flattened_list():
    """Test unflattening a FlattenedList (all keys start with '[')
    This covers lines 119-120 where pop_top is set to True"""
    flattened_list = {
        "[0]": "first",
        "[1]": "second",
        "[2].nested": "third",
        "[3][0]": "fourth",
    }
    result = jf.unflatten(flattened_list)
    assert result == ["first", "second", {"nested": "third"}, ["fourth"]]


def test_unflatten_ambiguous_keys_error():
    """Test ValueError for ambiguous keys (some start with '[', some don't)"""
    ambiguous = {
        "[0]": "array_element",
        "object_key": "object_value",
        "[1]": "another_array_element",
    }
    with pytest.raises(ValueError, match="Ambiguous Entry Detected"):
        jf.unflatten(ambiguous)


@pytest.mark.parametrize(
    argnames=("flattened", "expected_path"),
    argvalues=[
        ({"a[0]": 1, "a.k": 2}, "'a'"),
        ({"a.k": 2, "a[0]": 1}, "'a'"),
        ({"a.b[0]": 1, "a.b.k": 2}, "'a.b'"),
        ({"a.b.c.d[0]": 1, "a.b.c.d.k": 2}, "'a.b.c.d'"),
        ({'"x.y"[0]': 1, '"x.y".k': 2}, "'\"x.y\"'"),
        ({"z": 0, "a.b.k": 2, "m.n": 3, "a.b[0]": 1}, "'a.b'"),
    ],
)
def test_unflatten_ambiguous_keys_below_root(flattened, expected_path):
    """A path indicating both object and array raises at any depth, not just the root.

    Below the root this used to escape as an opaque TypeError from the internal
    sort, comparing an array index against a sibling object key."""
    with pytest.raises(ValueError, match="Ambiguous Entry Detected") as excinfo:
        jf.unflatten(flattened)
    assert expected_path in str(excinfo.value)


@pytest.mark.parametrize(
    argnames="flattened",
    argvalues=[
        {"a[0]": 1, "a[1]": 2},
        {"a.k": 1, "a.j": 2},
        {"a[0]": 1, "b.k": 2},
        {"a[0].k": 1, "a[1].j": 2},
        {},
    ],
)
def test_unflatten_unambiguous_keys_pass(flattened):
    """Keys agreeing on each container type are untouched by the ambiguity check."""
    assert jf.flatten(jf.unflatten(dict(flattened))) == flattened


def test_bad_path_element_query():
    """Verify exceptions are thrown for bad path 1st path element entries"""
    with pytest.raises(ValueError, match="Invalid array index"):
        jf.utils.escaped_query_from_path_elements(["*"])
        jf.utils.escaped_query_from_path_elements(["?bad"], "poobag")
    bad_not_strict = jf.utils.escaped_query_from_path_elements(["*"], "FartBag", False)
    assert bad_not_strict == "FartBag[*]"


def test_unflatten_with_discard_check_simple_key():
    """Test discard_check on simple key-value pairs
    This covers line 88 where discard_check returns early"""
    flattened = {
        "keep": "value1",
        "discard": "value2",
        "nested.keep": "value3",
    }

    def discard_check(key, value):
        return "discard" in key

    result = jf.unflatten(flattened, discard_check=discard_check)
    assert result == {"keep": "value1", "nested": {"keep": "value3"}}


def test_unflatten_array_padding_with_discard_check():
    """Test array padding when missing entries are discarded
    This covers lines 101-104 where array padding is discarded"""
    flattened = {
        "arr[5]": "value_at_5",
        "arr[10]": "value_at_10",
    }

    # Custom missing entry function that returns a value to be discarded
    original_missing = jf.constants.MISSING_ARRAY_ENTRY_VALUE
    jf.constants.MISSING_ARRAY_ENTRY_VALUE = lambda path, value: "DISCARD_ME"

    def discard_check(key, value):
        return value == "DISCARD_ME"

    try:
        result = jf.unflatten(flattened, discard_check=discard_check, preserve_array_indices=True)
        # Array should not have padding because discard_check filtered them out
        assert result == {"arr": ["value_at_5", "value_at_10"]}
    finally:
        # Restore original
        jf.constants.MISSING_ARRAY_ENTRY_VALUE = original_missing


def test_unflatten_preserve_array_indices_false():
    """Test with preserve_array_indices=False to skip array padding
    This ensures the while loop at lines 100-104 is not entered"""
    flattened = {
        "arr[2]": "second",
        "arr[5]": "fifth",
    }

    result = jf.unflatten(flattened, preserve_array_indices=False)
    assert result == {"arr": ["second", "fifth"]}


def test_unflatten_array_padding_normal():
    """Test normal array padding behavior with gaps
    This covers lines 100-104 in the normal case"""
    flattened = {
        "data[3]": "third",
        "data[7]": "seventh",
    }

    result = jf.unflatten(flattened, preserve_array_indices=True)
    assert result == {"data": [None, None, None, "third", None, None, None, "seventh"]}
