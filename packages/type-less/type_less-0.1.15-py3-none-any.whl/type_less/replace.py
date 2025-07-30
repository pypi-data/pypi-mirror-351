from copy import copy
from types import UnionType
from typing import (
    Union,
    get_origin,
    get_args,
)

def replace_type_hint_deep(type_hint: type, find: type, replace: type) -> type:
    """
    Deep search and replace type occurrences within a type hint structure.
    """
    return replace_type_hint_map_deep(type_hint, {find: replace})

def replace_type_hint_map_deep(type_hint: type, type_map: dict[type, type]) -> type:
    """
    Deep search and replace type occurrences within a type hint structure.

    Args:
        type_hint: The type hint to search through (e.g., List[Dict[str, int]])
        search_type: The type to find and replace (e.g., str)
        replace_type: The replacement type (e.g., bytes)

    Returns:
        A new type hint with all occurrences of search_type replaced with replace_type

    Examples:
        # Replace str with bytes in List[Dict[str, int]]
        result = deep_search_replace_type(List[Dict[str, int]], str, bytes)
        # Returns: List[Dict[bytes, int]]

        # Replace int with float in complex nested type
        result = deep_search_replace_type(
            Dict[str, Tuple[List[int], Optional[int]]],
            int,
            float
        )
        # Returns: Dict[str, Tuple[List[float], Optional[float]]]
    """

    # If the type hint itself is the search type, replace it
    if type_hint in type_map:
        return type_map[type_hint]

    # Special handling for TypedDict
    if hasattr(type_hint, "__annotations__") and hasattr(type_hint, "__total__"):
        new_typed_dict = copy(type_hint)
        type_hint.__annotations__ = {
            key: replace_type_hint_map_deep(value, type_map)
            for key, value in type_hint.__annotations__.items()
        }

        return new_typed_dict

    # Get the origin (container) and args (type parameters) of the type hint
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # If no origin (simple type like int, str), return as-is
    if origin is None:
        return type_hint

    # If no args, return the original type hint
    if not args:
        return type_hint

    # Recursively process all type arguments
    new_args = tuple(replace_type_hint_map_deep(arg, type_map) for arg in args)

    # Reconstruct the type hint with new arguments
    try:
        # Handle special cases for different Python versions and typing constructs
        if origin in (Union, UnionType):
            # Union types need special handling
            if len(new_args) == 1:
                return new_args[0]
            return Union[new_args]
        elif hasattr(origin, "__class_getitem__"):
            # Generic types that support subscription
            return origin[new_args]
        else:
            # Fallback for other types
            return origin[new_args]
    except (TypeError, AttributeError) as e:
        # If reconstruction fails, return original
        return type_hint
