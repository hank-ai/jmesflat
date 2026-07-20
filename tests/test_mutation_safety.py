"""Regression tests: flatten/unflatten/merge must not alias or mutate
empty-container leaves from their inputs.

Background: `flatten` emits empty dict/list leaves *by reference* and
`unflatten` plants leaf values by reference, then descends into them when
deeper sibling keys exist. As a result, `merge(base, overlay)` could insert
overlay values INTO a shared `{}`/`[]` object inside `base`, permanently
mutating it and contaminating every other structure that aliased that object.
"""

import copy

import jmesflat as jf


def test_flatten_copies_empty_dict_leaf():
    """Empty-container leaves in flatten output must not be the input objects"""
    nested = {"outer": {"inner": {}}}
    flat = jf.flatten(nested)
    assert flat["outer.inner"] == {}
    assert flat["outer.inner"] is not nested["outer"]["inner"]


def test_flatten_copies_empty_list_leaf():
    """Empty list leaves must be copied too, including at the top level"""
    nested = {"top": [], "outer": {"inner": []}}
    flat = jf.flatten(nested)
    assert flat["top"] is not nested["top"]
    assert flat["outer.inner"] is not nested["outer"]["inner"]


def test_unflatten_does_not_mutate_input_empty_dict_leaf():
    """Deeper sibling keys must not be inserted into the caller's `{}` object"""
    shared_empty: dict = {}
    flat = {"settings.required": shared_empty, "settings.required.note": "value"}
    result = jf.unflatten(flat)
    assert result == {"settings": {"required": {"note": "value"}}}
    assert shared_empty == {}


def test_unflatten_does_not_mutate_input_empty_list_leaf():
    """Deeper sibling array keys must not be appended into the caller's `[]`"""
    shared_empty: list = []
    flat = {"settings.items": shared_empty, "settings.items[0]": "value"}
    result = jf.unflatten(flat)
    assert result == {"settings": {"items": ["value"]}}
    assert shared_empty == []


def test_merge_does_not_mutate_nest1_via_empty_dict_leaf():
    """The pdf-extractor contamination shape: overlay keys beneath an
    empty-dict leaf in nest1 must not be written back into nest1"""
    base = {"hreExtractionSettings": {"requiredNoteTypes": {}}}
    base_snapshot = copy.deepcopy(base)
    overlay = {
        "hreExtractionSettings": {
            "requiredNoteTypes": {"SurgeonProcedureNote": ["SurgeonProcedureNote"]}
        }
    }
    merged = jf.merge(base, overlay, array_merge="deduped")
    assert merged == overlay
    assert base == base_snapshot


def test_merge_result_does_not_alias_nest1_empty_containers():
    """Mutating an empty container in the merge result must not affect nest1"""
    base = {"settings": {"required": {}, "items": []}}
    merged = jf.merge(base, {"other": 1})
    merged["settings"]["required"]["note"] = "value"
    merged["settings"]["items"].append("entry")
    assert base == {"settings": {"required": {}, "items": []}}
