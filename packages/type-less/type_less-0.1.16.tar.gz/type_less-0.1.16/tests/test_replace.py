from .matching import validate_is_equivalent_type
from type_less.replace import replace_type_hint_deep, replace_type_hint_map_deep
from typing import TypedDict

def test_replace_flat():
    test_type = list[str]
    replaced_type, occurrences = replace_type_hint_deep(test_type, str, int)
    assert replaced_type == list[int]
    assert occurrences == 1

def test_replace_nested():
    test_type = list[dict[str, int]]
    replaced_type, occurrences = replace_type_hint_deep(test_type, str, int)
    assert replaced_type == list[dict[int, int]]
    assert occurrences == 1

def test_replace_map():
    test_type = list[dict[str, int]]
    replaced_type, occurrences = replace_type_hint_map_deep(test_type, {str: int, int: str})
    assert replaced_type == list[dict[int, str]]
    assert occurrences == 2

def test_replace_typeddict():
    test_type = TypedDict("Test", {"name": str, "age": int})
    replaced_type, occurrences = replace_type_hint_deep(test_type, str, int)
    assert validate_is_equivalent_type(replaced_type, TypedDict("Test", {"name": int, "age": int}))
    assert occurrences == 1
