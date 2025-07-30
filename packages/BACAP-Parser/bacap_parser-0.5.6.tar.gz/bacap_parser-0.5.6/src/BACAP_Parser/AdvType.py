from collections.abc import Iterable
from typing import Type

from .Color import Color
from .constants import ADV_FRAMES
from .utils import to_collection


class AdvType:
    """
    Represents an advanced type with specific attributes.

    :param name: The name of the type.
    :param frames: A string or an iterable of strings representing the frames. Valid options are ``"task"``, ``"goal"``, ``"challenge"``.
    :param colors: A single color or an iterable containing colors of type Color.
    :param tabs: A list of possible tabs. If not provided, any tab is allowed.
    :param hidden_color: Color of the advancement if it is hidden.
    :raises ValueError: If frames are not a subset of ``constants.ADV_FRAMES``, or if colors are not of type Color.
    """

    def __init__(self, name: str, frames: Iterable[str] | str,
                 colors: Iterable[Color] | Color, tabs: Iterable[str] | str = None, hidden_color: Color | None = None):

        self._name = name

        self._frames = to_collection(frames, set)
        if not self._frames.issubset(ADV_FRAMES):
            raise ValueError(f"Invalid frames: {self._frames}")

        self._colors = to_collection(colors, set)

        if not self.__all_elements_of_type(self._colors, Color):
            raise ValueError("Not all colors have Color class")

        if hidden_color:
            self._colors.add(hidden_color)

        self._tabs = to_collection(tabs, set) if tabs else None

    @property
    def name(self) -> str:
        """
        :return: The name of the type.
        """
        return self._name

    @property
    def frames(self) -> set[str]:
        """
        :return: The set of possible frames.
        """
        return self._frames

    @property
    def colors(self) -> set[Color]:
        """
        :return: The set of colors frames.
        """
        return self._colors

    @property
    def tabs(self) -> set[str] | None:
        """
        :return: The set of possible tabs.
        """
        return self._tabs

    @staticmethod
    def __all_elements_of_type(items: Iterable, expected_type: Type) -> bool:
        return all(isinstance(item, expected_type) for item in items)

    def __repr__(self):
        return f"AdvType('{self.name}')"


class MultipleTypesMatch(Exception):
    def __init__(self, frame: str, color: Color, tab: str):
        super().__init__(f"Multiple types match the given frame: \"{frame}\", color: \"{color}\", and tab: \"{tab}\".")


class NoTypesMatch(Exception):
    def __init__(self, frame: str, color: Color, tab: str):
        super().__init__(f"No types match the given frame: \"{frame}\", color: \"{color}\", and tab: \"{tab}\".")


class AdvTypeManager:
    def __init__(self, *adv_types: AdvType):
        """
        A class to manage possible AdvTypes of the datapack
        :param adv_types: One or more AdvType instances to initialize the AdvTypeManager with.
        """
        self._types: dict[str, AdvType] = {}
        self.register_types(to_collection(adv_types, list))

    def register_type(self, adv_type: AdvType):
        """
        Adds a new AdvType to the AdvTypeManager to parse advancements.
        :param adv_type: The AdvType instance to add.
        :raises ValueError: If an AdvType is already registered.
        """
        if adv_type not in self._types:
            self._types[adv_type.name] = adv_type
        else:
            raise ValueError("This type is already registered")

    def register_types(self, adv_types: Iterable[AdvType]):
        """
        Adds an iterable of AdvType to the AdvTypeManager to parse advancements.
        :param adv_types: The iterable of AdvType instances to add.
        :raises ValueError: If any of AdvType is already registered.
        """
        for adv_type in adv_types:
            self.register_type(adv_type)

    @property
    def types(self) -> dict[str, AdvType]:
        """
        :return: dict of AdvType instances.
        """
        return self._types

    def recognize_type(self, *, frame: str | None = None, color: Color | None = None, tab: str | None = None) -> AdvType:
        """
        Recognizes and returns a single AdvType based on the provided parameters.

        :param frame: The frame identifier to match against ``adv_type.frames``. If None, this parameter is ignored.
        :param color: The color to match against ``adv_type.colors``. If None, this parameter is ignored.
        :param tab: The tab identifier to match against ``adv_type.tabs``. If None, this parameter is ignored.
        :return: The matched `AdvType` instance.
        :raises MultipleTypesMatch: If more than one ``AdvType`` matches the given parameters without clear priority.
        :raises NoTypesMatch: If no ``AdvType`` matches the given parameters.
        """
        matching_types = [
            adv_type for adv_type in self._types.values()
            if (frame is None or frame in adv_type.frames) and
               (color is None or color in adv_type.colors) and
               (adv_type.tabs is None or tab in adv_type.tabs)
        ]

        if len(matching_types) > 1:
            # Prioritize types with a non-None "tabs" that matches the provided "tab".
            prioritized_types = [
                adv_type for adv_type in matching_types
                if adv_type.tabs is not None and tab in adv_type.tabs
            ]

            if len(prioritized_types) == 1:
                return prioritized_types[0]
            elif len(prioritized_types) > 1:
                raise MultipleTypesMatch(frame, color, tab)

        if len(matching_types) == 1:
            return matching_types[0]

        raise NoTypesMatch(frame, color, tab)
