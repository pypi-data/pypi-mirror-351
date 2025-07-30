from collections.abc import Iterable

from .constants import DEFAULT_BACAP_TAB_NAMES_MAP


class TabNameMapper:
    """
    A utility class to manage the mapping between system tab names and their display names. Can be modified after initialization.
    """

    def __init__(self, additional_tabs: dict[str, str] = None):
        """
        Initializes the TabNameMapper with a default mapping and allows optional additions.

        :param additional_tabs: A dictionary of additional tab mappings to extend the default map.
        """
        self._mapping: dict[str, str] = DEFAULT_BACAP_TAB_NAMES_MAP.copy()
        if additional_tabs:
            self._mapping.update(additional_tabs)

    @property
    def tab_names(self) -> Iterable[str]:
        """
        Retrieves the system names of all tabs.

        :return: An iterable of system tab names (keys in the mapping).
        """
        return self._mapping.keys()

    @property
    def display_names(self) -> Iterable[str]:
        """
        Retrieves the display names of all tabs.

        :return: An iterable of display tab names (values in the mapping).
        """
        return self._mapping.values()

    def __getitem__(self, key: str) -> str:
        """
        :param key: key to look up in the mapping.
        :return: value in the mapping.
        :raises KeyError: if key is not in the mapping.
        """
        return self._mapping[key]

    def get[AnyType](self, key: str, default: AnyType = None) -> str | AnyType | None:
        """
        :param key: key to look up in the mapping.
        :param default: default value to return if key is not in the mapping.
        :return: value in the mapping or default if key is not in the mapping.
        """
        return self._mapping.get(key, default)

    def __setitem__(self, key: str, value: str):
        """
        :param key: key of the value to set.
        :param value: value to set.
        """
        self._mapping[key] = value

    @property
    def tab_mapping(self) -> dict[str, str]:
        """
        Provides the entire mapping of system names to display names.

        :return: A dictionary containing the tab mapping.
        """
        return self._mapping

    def __call__(self) -> dict[str, str]:
        """
        Allows the instance to be called directly to retrieve the current mapping.

        :return: The tab mapping as a dictionary.
        """
        return self._mapping

    def extend_mapping(self, additional_tabs: dict[str, str]):
        """
        Adds or updates entries in the tab mapping.

        :param additional_tabs: A dictionary containing new or updated tab mappings.
        """
        self._mapping.update(additional_tabs)
