from collections.abc import Iterable, Hashable
from typing import Any


class ExtendedDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def can_access_keypath(self, keys: Iterable[Hashable]) -> bool:
        """
        Checks if the key-path exists in the dictionary.

        :param keys: List of keys.
        :return: True if the key-path exists in the dictionary, else False.
        """
        current = self
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False
        return True

    def get_by_keypath[T: Any](self, keys: Iterable[Hashable], default: T = None) -> Any | T | None:
        """
        Retrieves the value at the given key-path. If any key in the path is missing,
        returns the default value.

        :param keys: List of keys to traverse.
        :param default: Value to return if the key-path does not exist.
        :return: Value at the key-path, or the default value if not found.
        """
        current = self
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_with_multiple_values(self, *keys: Hashable, default: Any = None) -> Any | None:
        """
        Returns the value of the first key found in the dictionary among the provided keys.
        If none of the keys are found, returns the default value.

        :param keys: Keys to search for in the dictionary.
        :param default: Value to return if no keys are found in the dictionary.
        :return: The value corresponding to the first found key, or the default value if not found.
        """
        for key in keys:
            if key in self:
                return self[key]
        return default