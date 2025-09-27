import importlib

def test_deep_merge_spec_example():
    merge = importlib.import_module("merge")
    deep_merge = merge.deep_merge

    before = {
        "foo": "bar",
        "k2": {"sk3": 15, "sk4": None},
        "k3": [1, 2, 3, "foo"],
    }
    patch = {
        "k2": {"sk4": "val4", "sk5": 42},
        "k3": None,
        "k10": "val10",
    }
    out = deep_merge(before, patch)

    assert out == {
        "foo": "bar",
        "k2": {"sk3": 15, "sk4": "val4", "sk5": 42},
        "k3": None,
        "k10": "val10",
    }

def test_arrays_replace_not_merge():
    merge = importlib.import_module("merge")
    deep_merge = merge.deep_merge

    before = {"a": [1, 2, 3], "b": {"x": 1}}
    patch = {"a": ["replaced"], "b": {"y": 2}}
    out = deep_merge(before, patch)

    assert out["a"] == ["replaced"]
    assert out["b"] == {"x": 1, "y": 2}

def test_null_overrides_existing_values():
    merge = importlib.import_module("merge")
    deep_merge = merge.deep_merge

    before = {"k": {"x": 1}, "n": 5}
    patch = {"k": None, "n": None}
    out = deep_merge(before, patch)

    assert out["k"] is None
    assert out["n"] is None

def test_scalar_replaces_object():
    merge = importlib.import_module("merge")
    deep_merge = merge.deep_merge

    before = {"k": {"x": 1}}
    patch = {"k": 999}
    out = deep_merge(before, patch)

    assert out["k"] == 999
