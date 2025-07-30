from .inference import guess_return_type
from .inject import fill_type_hints
from .replace import replace_type_hint_deep, replace_type_hint_map_deep

__all__ = ["fill_type_hints", "guess_return_type", "replace_type_hint_deep", "replace_type_hint_map_deep"]