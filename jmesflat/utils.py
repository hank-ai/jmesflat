"""Utility functions for flatten/unflatten operations"""

from collections.abc import Sequence
from typing import Any

from . import constants


class FlattenedList(dict[str, Any]):
    """A branded version of `dict[str, Any]` to improve `unflatten()` type hinting.
    Functions identically to a normal dict. Assigned by `flatten` when the `nested`
    parameter has type `list[Any]`."""


class FlattenedDict(dict[str, Any]):
    """A branded version of `dict[str, Any]` to improve `unflatten()` type hinting.
    Functions identically to a normal dict. Assigned by `flatten` when the `nested`
    parameter has type `dict[str, Any]`."""


def jpquery_from_flat_key(flat_key: str, strict: bool = True) -> str:
    """
    Add escape quotes around path elements containing reserved chars or spaces.

    Args:
        flat_key (str): flattened json key
        strict (bool, optional): if True, raise ValueError "[*]" array refs. \
            Default is True.

    Returns:
        str: properly escaped jmespath query string

    Example:
        >>> jpquery_from_flat_key('foo-bar.baz[2].test.@type')
        '"foo-bar".baz[2].test."@type"'
    """
    return escaped_query_from_path_elements(
        raw_jpquery_path_elements(flat_key),
        strict=strict,
    )


def raw_jpquery_path_elements(flat_key: str) -> list[str | int]:
    """
    Split a flat key into a list of path elements.

    Args:
        flat_key (str): The flat key string to be split.

    Returns:
        list[str | int]: A list of path elements extracted from the flat key. \
            Output contains strs for key references and ints for array indices.

    Example:
        >>> raw_jpquery_path_elements("foo[0].bar[1].baz")
        ['foo', 0, 'bar', 1, 'baz']
    """
    return [
        int(sub_e[1]) if sub_e[0] == "[" and sub_e[1].isnumeric() else sub_e[1]
        for sub_e in constants.PATH_ELEMENT_REGEX.findall(flat_key)
        if sub_e[1]
    ]


def _escaped_key(key: str) -> str:
    """
    Escape path elements containing reserved chars or spaces.

    Args:
        key (str): key to escape

    Returns:
        str: escaped key
    """
    if not key:
        # should be impossible. adding `pragma:no cover`
        return ""  # pragma: no cover
    if not (key[0] == key[-1] == '"') and (
        any(c in key for c in constants.ESCAPED_CHARS) or all(c.isnumeric() for c in key)
    ):
        return f'"{key.strip(chr(34))}"'
    return key


def escaped_query_from_path_elements(
    elements: Sequence[str | int], prefix: str = "", strict: bool = True
) -> str:
    """
    Escape each key containing reserved chars or spaces with double quotes to
    prevent jmespath from interpreting them as operators.

    Args:
        elements (Sequence[str | int]): list of keys and/or indices
        prefix (str, optional): prefix to prepend to first key. Defaults to "".
        strict (bool, optional): if True, raise ValueError if an array index is a "*".

    Returns:
        str: properly escaped jmespath query string built from elements
    """
    if isinstance(elements[0], int):
        next_key = f"{prefix}[{elements[0]}]"
    elif elements[0] == "*" or elements[0].startswith("?"):
        if strict:
            raise ValueError(f"Invalid array index: {elements[0]!r}; original {elements=!r}")
        next_key = f"{prefix}[{elements[0]}]"
    elif not prefix:
        next_key = _escaped_key(elements[0])
    else:
        next_key = f"{prefix}.{_escaped_key(elements[0])}"
    if len(elements) == 1:
        return next_key
    return escaped_query_from_path_elements(elements[1:], next_key, strict)


def flat_key_from_path_elements(elements: Sequence[str | int]) -> str:
    """return an unescaped flattened key from a list of path elements"""
    return escaped_query_from_path_elements(elements, strict=False).replace('"', "")
