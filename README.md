# jmesflat ✨

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-green.svg)](htmlcov/index.html)

Built upon and considered an extension of [`jmespath`](https://jmespath.org), `jmesflat` is similarly pronounced (say "James flat") and provides a simple interface for flattening, 'unflattening', and merging deeply nested JSON objects.

Common use cases:

```python
>>> # 1. Building deeply nested objects without constructing individual layers:
>>> import jmesflat as jf
>>> nest1 = jf.unflatten({"a.b[0].c[0].d": "e", "a.b[1].f": "g"})
>>> nest1
{'a': {'b': [{'c': [{'d': 'e'}]}, {'f': 'g'}]}}
>>>
>>> # 2. Merging deeply nested objects:
>>> nest2 = {"a": {"b": [{"f": "g"}, {"c": [{"d": "e"}]}]}}
>>> merged_nest = jf.merge(nest1, nest2)
>>> merged_nest
{'a': {'b': [{'c': [{'d': 'e'}], 'f': 'g'}, {'c': [{'d': 'e'}], 'f': 'g'}]}}
>>>
>>> # 3. Making dumps of complex nest objects compact and human readable
>>> import json
>>> print(json.dumps(jf.flatten(merged_nest), indent=2))
{
  "a.b[0].c[0].d": "e",
  "a.b[0].f": "g",
  "a.b[1].c[0].d": "e",
  "a.b[1].f": "g"
}
```

## 🚀 Installation

```bash
pip install jmesflat
```

## 📋 Requirements

- Python 3.10+
- jmespath

## 🎯 Key Features

1. Keys *can* contain spaces and reserved characters (`@` and `-`)
2. Supports any arbitrary nesting pattern including mixed and multi-level array objects
3. Empty lists / dicts are considered atomic types and included in the flattened output alongside the 'true' atomic types `int`, `float`, `str`, `bool`, and `None`
4. Flatten / unflatten / merge at an arbitrary *object* depth using the `level` parameter (depth *cannot exceed* the depth of the first array instance)
5. Extend rather than overwrite arrays during merge operations using the `array_merge` parameter. 'topdown' merges extend at the first array instance. 'bottomup' extends at the final array instance.
6. Scrub the data during `flatten`/`unflatten`/`merge` operations or simply scrub a nested object via `clean` using the `discard_check` parameter. The check is ONLY applied to `nest2` during the `merge` operation.

```python
>>> import json
>>> import jmesflat as jf
>>>
>>> test_nest = {
...     "Outer Object Key 1": {
...         "mixedArray": [
...             "mixed array string",
...             {"mixed Array Object 1 Key": "spaces demo"},
...             12345,
...             [
...                 {"@subArray": "@ symbol demo"},
...                 {"@subArray": 1.2345},
...                 {"@subArray": None},
...             ],
...             {"mixed-array-object-2-key": "dashed key demo"},
...             [],
...             {},
...         ],
...     },
...     "Outer Object Key 2": {
...         "deepNest": {
...             "a": [
...                 {"b": 1},
...                 {
...                     "c": {
...                         "d": [
...                             {"e": "f", "g": "h"},
...                             {"e": "f1"}
...                         ]
...                     }
...                 }
...             ]
...         },
...     },
... }
>>>
>>> flat = jf.flatten(test_nest, level=1)
>>> print(json.dumps(flat, indent=2))
{
  "Outer Object Key 1": {
    "mixedArray[0]": "mixed array string",
    "mixedArray[1].mixed Array Object 1 Key": "spaces demo",
    "mixedArray[2]": 12345,
    "mixedArray[3][0].@subArray": "@ symbol demo",
    "mixedArray[3][1].@subArray": "@ symbol demo",
    "mixedArray[3][2].@subArray": "@ symbol demo",
    "mixedArray[4].mixed-array-object-2-key": "dashed key demo",
    "mixedArray[5]": [],
    "mixedArray[6]": {}
  },
  "Outer Object Key 2": {
    "deepNest.a[0].b": 1,
    "deepNest.a[1].c.d[0].e": "f",
    "deepNest.a[1].c.d[0].g": "h",
    "deepNest.a[1].c.d[1].e": "f1"
  }
}
>>>
>>> jf.unflatten(flat, level=1) == test_nest
True
>>>
>>> from copy import deepcopy
>>> test_nest2 = deepcopy(test_nest)
>>> # NOTE: `jf.flatten` wrapper is used for ease of visualization only in the merge/clean examples below
>>> print(json.dumps(jf.flatten(jf.merge(test_nest, test_nest2, level=1), level=2), indent=2))
{
  "Outer Object Key 1": {
    "mixedArray": {
      "[0]": "mixed array string",
      "[1].mixed Array Object 1 Key": "spaces demo",
      "[2]": 12345,
      "[3][0].@subArray": "@ symbol demo",
      "[3][1].@subArray": 1.2345,
      "[3][2].@subArray": null,
      "[4].mixed-array-object-2-key": "dashed key demo",
      "[5]": [],
      "[6]": {}
    }
  },
  "Outer Object Key 2": {
    "deepNest": {
      "a[0].b": 1,
      "a[1].c.d[0].e": "f",
      "a[1].c.d[0].g": "h",
      "a[1].c.d[1].e": "f1"
    }
  }
}
>>> print(json.dumps(jf.flatten(jf.merge(test_nest, test_nest2, level=1, array_merge="topdown"), level=2), indent=2))
{
  "Outer Object Key 1": {
    "mixedArray": {
      "[0]": "mixed array string",
      "[1].mixed Array Object 1 Key": "spaces demo",
      "[2]": 12345,
      "[3][0].@subArray": "@ symbol demo",
      "[3][1].@subArray": 1.2345,
      "[3][2].@subArray": null,
      "[4].mixed-array-object-2-key": "dashed key demo",
      "[5]": [],
      "[6]": {},
      "[7]": "mixed array string",
      "[8].mixed Array Object 1 Key": "spaces demo",
      "[9]": 12345,
      "[10][0].@subArray": "@ symbol demo",
      "[10][1].@subArray": 1.2345,
      "[10][2].@subArray": null,
      "[11].mixed-array-object-2-key": "dashed key demo",
      "[12]": [],
      "[13]": {}
    }
  },
  "Outer Object Key 2": {
    "deepNest": {
      "a[0].b": 1,
      "a[1].c.d[0].e": "f",
      "a[1].c.d[0].g": "h",
      "a[1].c.d[1].e": "f1",
      "a[2].b": 1,
      "a[3].c.d[0].e": "f",
      "a[3].c.d[0].g": "h",
      "a[3].c.d[1].e": "f1"
    }
  }
}
>>> print(json.dumps(jf.flatten(jf.merge(test_nest, test_nest2, level=1, array_merge="bottomup"), level=2), indent=2))
{
  "Outer Object Key 1": {
    "mixedArray": {
      "[0]": "mixed array string",
      "[1].mixed Array Object 1 Key": "spaces demo",
      "[2]": 12345,
      "[3][0].@subArray": "@ symbol demo",
      "[3][1].@subArray": 1.2345,
      "[3][2].@subArray": null,
      "[3][3].@subArray": "@ symbol demo",
      "[3][4].@subArray": 1.2345,
      "[3][5].@subArray": null,
      "[4].mixed-array-object-2-key": "dashed key demo",
      "[5]": [],
      "[6]": {},
      "[7]": "mixed array string",
      "[8].mixed Array Object 1 Key": "spaces demo",
      "[9]": 12345,
      "[10].mixed-array-object-2-key": "dashed key demo",
      "[11]": [],
      "[12]": {}
    }
  },
  "Outer Object Key 2": {
    "deepNest": {
      "a[0].b": 1,
      "a[1].c.d[0].e": "f",
      "a[1].c.d[0].g": "h",
      "a[1].c.d[1].e": "f1",
      "a[1].c.d[2].e": "f",
      "a[1].c.d[2].g": "h",
      "a[1].c.d[3].e": "f1",
      "a[2].b": 1
    }
  }
}
>>> print(json.dumps(jf.flatten(jf.clean(test_nest, discard_check=lambda key, val: "-" in key or not isinstance(val, (str, int))), level=2), indent=2))
{
  "Outer Object Key 1": {
    "mixedArray": {
      "[0]": "mixed array string",
      "[1].mixed Array Object 1 Key": "spaces demo",
      "[2]": 12345,
      "[3][0].@subArray": "@ symbol demo"
    }
  },
  "Outer Object Key 2": {
    "deepNest": {
      "a[0].b": 1,
      "a[1].c.d[0].e": "f",
      "a[1].c.d[0].g": "h",
      "a[1].c.d[1].e": "f1"
    }
  }
}
```

## ⚙️ Configuration via `constants` Module

The `constants` module allows global defaults to be set for several key features. For example, a global discard check function can be defined by setting the value of `jf.constants.DISCARD_CHECK`. If the user wishes to discard all `None` type values, simply set `jf.constants.DISCARD_CHECK = lambda _, val: val is None` after the initial `import jmesflat as jf` statement. In addition, users can customize the default values that will be used when extending arrays during an index preserving unflatten operation via `jf.MISSING_ARRAY_ENTRY_VALUE`, a callable that accepts the flattened key of the array element *being set* and the value said *is being set to* and returns the value that should be used to pad the array until its length is >= the desired index. Other settings in the `constants` module are considered 'use at your own risk' and included for possible future extensibility.

## 📊 Test Coverage

| Module | Statements | Missing | Excluded | Coverage |
|--------|------------|---------|----------|----------|
| jmesflat/__init__.py | 7 | 0 | 0 | 100.00% |
| jmesflat/_clean.py | 11 | 0 | 0 | 100.00% |
| jmesflat/_flatten.py | 39 | 0 | 0 | 100.00% |
| jmesflat/_merge.py | 41 | 0 | 1 | 100.00% |
| jmesflat/_unflatten.py | 50 | 0 | 2 | 100.00% |
| jmesflat/constants.py | 8 | 0 | 0 | 100.00% |
| jmesflat/utils.py | 29 | 0 | 1 | 100.00% |
| **Total** | **185** | **0** | **4** | **100.00%** |
