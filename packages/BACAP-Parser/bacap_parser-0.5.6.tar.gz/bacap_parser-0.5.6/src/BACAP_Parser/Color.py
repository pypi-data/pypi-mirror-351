MINECRAFT_TEXT_COLORS_MAP = {
    "black": "#000000",
    "dark_blue": "#0000AA",
    "dark_green": "#00AA00",
    "dark_aqua": "#00AAAA",
    "dark_red": "#AA0000",
    "dark_purple": "#AA00AA",
    "gold": "#FFAA00",
    "gray": "#AAAAAA",
    "dark_gray": "#555555",
    "blue": "#5555FF",
    "green": "#55FF55",
    "aqua": "#55FFFF",
    "red": "#FF5555",
    "light_purple": "#FF55FF",
    "yellow": "#FFFF55",
    "white": "#FFFFFF"
}
MINECRAFT_TEXT_COLORS_MAP_REVERSED = {value: key for key, value in MINECRAFT_TEXT_COLORS_MAP.items()}

class Color:
    def __init__(self, color: str):
        """
        :param color: Minecraft text color or hex representation of color (with or without '#')

        :raises ValueError: If color is invalid
        """
        self._color = None
        self.__set_color(color)

    def __set_color(self, color: str):
        if color in MINECRAFT_TEXT_COLORS_MAP:
            self._color = MINECRAFT_TEXT_COLORS_MAP[color]
        else:
            color = color.lstrip('#')
            if len(color) != 6:
                raise ValueError(f"Invalid hex color length. A hex color must have exactly 6 characters (without '#').")

            try:
                color_check = int(color, 16)
            except ValueError:
                raise ValueError(f"Invalid hex color: '{color}'. It must consist of valid hex digits (0-9, A-F).")

            if not (0 <= color_check <= 0xFFFFFF):
                raise ValueError(f"Hex color '{color}' is out of valid range (0 to #FFFFFF).")

            self._color = f"#{color}"

    def __repr__(self):
        return self._color

    def __eq__(self, other):
        if not isinstance(other, Color):
            return NotImplemented
        return self._color == other._color

    def __hash__(self):
        return hash(self._color)

    @property
    def value(self) -> str:
        """
        :return: HEX representation of color
        """
        return self._color

    @property
    def as_rgb(self) -> tuple[int, int, int]:
        """
        :return: color representation as RGB tuple
        """
        hex_color = self._color.lstrip("#")
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    @property
    def as_int(self) -> int:
        """
        :return: color representation as Integer value
        """
        return self.__int__()

    def __int__(self) -> int:
        return int(self._color.lstrip('#'), 16)

    @property
    def as_color(self) -> str | None:
        """
        :return: Minecraft Text color if exists, else None
        """
        return MINECRAFT_TEXT_COLORS_MAP_REVERSED.get(self._color)

    @classmethod
    def color_to_hex(cls, color: str) -> str:
        """
        Converts a color name to its hexadecimal representation.

        If the input color is already in hexadecimal format, it is returned as is.
        If the color name is valid, its corresponding hex value is returned.
        If the color name is not found, a ValueError is raised.

        :param color: A string representing the color name or hex value (e.g., 'light_purple' or '#FFA500').

        :return: The hexadecimal string representation of the color.

        :raises ValueError: If the color name is not found in the dictionary.
        """
        if color[0] == "#":
            return color
        else:
            try:
                return MINECRAFT_TEXT_COLORS_MAP[color]
            except KeyError:
                raise ValueError(f"'{color}' is not a valid color")

    @classmethod
    def hex_to_color(cls, color: str) -> str:
        """
        Converts a hexadecimal color string to its corresponding color name.

        If a color name exists in the list of minecraft text colors for the given hex color,
        it will be returned.
        Otherwise, an error will be raised.

        :param color: A string representing the color in hexadecimal format (e.g., '#FFA500').

        :return: The color name if it exists in the list of Minecraft text colors.

        :raises ValueError: If the hex color is not found in the list of Minecraft text colors.
        """
        color_name = MINECRAFT_TEXT_COLORS_MAP_REVERSED.get(color)
        if color_name is None:
            raise ValueError(f"Color '{color}' not found in the list of minecraft text colors.")
        return color_name

    @classmethod
    def color_to_rgb(cls, color: str) -> tuple:
        """
        Converts a color name or hex value to its RGB representation.

        If the input is a valid hex color or color name, it will be converted to a tuple (R, G, B).

        :param color: A string representing the color name or hex value (e.g., 'light_purple' or '#FFA500').

        :return: A tuple (R, G, B) representing the color in RGB format.
        """
        hex_color = cls.color_to_hex(color).lstrip("#")
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )

    @classmethod
    def rgb_to_hex(cls, color: tuple[int, int, int]) -> str:
        """
        Converts an RGB tuple to its hexadecimal representation.

        The input tuple should contain three integers representing the red, green, and blue components
        of the color.
        Each component should be in the range 0 to 255.

        :param color: A tuple containing the RGB components (R, G, B), where each component is an integer in the range [0, 255].

        :return: A string representing the color in hexadecimal format, e.g., '#FFA500'.

        :raises ValueError: If any of the RGB components are outside the valid range of 0 to 255.
        """
        if not all(0 <= component <= 255 for component in color):
            raise ValueError("Each RGB component must be in the range 0 to 255 (inclusive).")

        return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"

    @classmethod
    def rgb_to_color(cls, color: tuple[int, int, int]) -> str:
        """
        Converts an RGB tuple to its corresponding color name, if available.

        The input tuple should contain three integers representing the red, green, and blue components
        of the color.
        If the color exists in the list of Minecraft text colors, its name will be returned.
        Otherwise, the hexadecimal representation of the color is returned.

        :param color: A tuple containing the RGB components (R, G, B), where each component is an integer in the range [0, 255].

        :return: The color name if it exists in the list of Minecraft text colors, otherwise the hexadecimal string representation of the color.

        :raises ValueError: If the rgb color is not found in the list of Minecraft text colors.
        """

        hex_color = cls.rgb_to_hex(color)
        color_name = MINECRAFT_TEXT_COLORS_MAP_REVERSED.get(hex_color)
        if color_name is None:
            raise ValueError(f"Color '{color}' not found in the list of minecraft text colors.")
        return color_name

    @classmethod
    def color_to_int(cls, color: str) -> int:
        """
        Converts a color name or hex value to its integer representation.

        If the input color is in a valid hex format (either a name or a hex value),
        it will be converted to its corresponding integer representation.

        :param color: A string representing the color name or hex value (e.g., 'light_purple' or '#FFA500').

        :return: The integer representation of the color.
        """
        return int(cls.color_to_hex(color).lstrip("#"), 16)

    @classmethod
    def int_to_color(cls, color_int: int) -> str:
        """
        Converts an integer color value to its color name or hexadecimal representation.

        If a color name exists in the list of minecraft text colors, it will be returned.
        Otherwise, the hexadecimal string representation of the color is returned.

        :param color_int: An integer representing a color.

        :return: The color name if it exists in the list of minecraft text colors, otherwise the hexadecimal string representation of the color.
        """
        hex_color = cls.int_to_hex(color_int)
        return MINECRAFT_TEXT_COLORS_MAP_REVERSED.get(hex_color, hex_color)

    @classmethod
    def int_to_hex(cls, color_int: int) -> str:
        """
        Converts an integer color value to its hexadecimal string representation.

        :param color_int: An integer representing a color.

        :return: A string in the format '#RRGGBB'.
        """
        if not (0 <= color_int <= 0xFFFFFF):
            raise ValueError("Color integer must be in the range 0 to 0xFFFFFF (inclusive).")

        return f"#{color_int:06X}"

    @classmethod
    def int_to_rgb(cls, color_int: int) -> tuple[int, int, int]:
        """
        Converts an integer color value to its RGB string representation.
        :param color_int: An integer representing a color.

        :return: A string in the format [int, int, int]
        """
        if not (0 <= color_int <= 0xFFFFFF):
            raise ValueError("Color integer must be in the range 0 to 0xFFFFFF (inclusive).")

        return (color_int >> 16) & 0xFF, (color_int >> 8) & 0xFF, color_int & 0xF

    @classmethod
    def rgb_to_int(cls, rgb: tuple[int, int, int]) -> int:
        """
        Converts an RGB tuple to its integer color representation.

        :param rgb: A tuple containing the RGB components [R, G, B].

        :return: An integer representing the color.
        """
        if not all(0 <= component <= 255 for component in rgb):
            raise ValueError("Each RGB component must be in the range 0 to 255 (inclusive).")

        return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
