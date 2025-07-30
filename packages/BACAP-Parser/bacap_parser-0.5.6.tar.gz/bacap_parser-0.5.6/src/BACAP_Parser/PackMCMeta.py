from pathlib import Path

from .utils import safe_load_json_file


class PackMCMeta:
    """
    Object for managing and validating a Minecraft datapack's metadata.
    """
    def __init__(self, datapack_path: Path):
        """
        :param datapack_path: A `Path` object representing the root directory of the Minecraft datapack.
                              This directory must contain a valid `pack.mcmeta` file.
        :raises FileNotFoundError: If `pack.mcmeta` is not found in the provided datapack directory,
        or if the `data` directory (or an overlay directory, if specified) is missing or not a directory.
        :raises ValueError: If `pack.mcmeta` is not a valid JSON file or is empty.
        """
        if not (datapack_path / "pack.mcmeta").exists():
            raise FileNotFoundError("pack.mcmeta not found in the datapack root, may be this is a wrong path")

        self._path = datapack_path / "pack.mcmeta"
        self._json = safe_load_json_file(path=self._path, object_hook_class=dict)

        if self._json is None:
            raise ValueError("pack.mcmeta is not a valid json, or empty")

        self._pack_format = self._validate_pack_format()
        if "overlays" in self._json:
            self._data_path = datapack_path / f"{self._get_max_min_overlay_directory()}/data"
        else:
            self._data_path = datapack_path / "data"

        if not (self._data_path.exists() or self._data_path.is_dir()):
            raise FileNotFoundError(f"latest data directory: \"{self._data_path}\" not found in the datapack, or it is not a directory")

        self._description = self._parse_description()

    def _parse_description(self) -> str:
        """
        Parses and extracts the description from the `pack.mcmeta` file.

        :return: A string containing the description of the datapack.
        :raises KeyError: If the `pack.mcmeta` file does not contain a `pack` or `description` key.
        """
        raw_description = self._json["pack"]["description"]
        if isinstance(raw_description, str):
            return raw_description
        else:
            text = ""
            for line in raw_description:
                text += line["text"]
            return text

    def _validate_pack_format(self) -> int:
        """
        Validates the `pack_format` value from the `pack.mcmeta` file.

        :return: An integer representing the validated `pack_format`.
        :raises ValueError: If the `pack_format` key is missing or if the format is unsupported.
        """
        pack_format = self._json.get("pack", {}).get("pack_format", -1)

        if pack_format == -1:
            raise ValueError("pack.mcmeta does not have pack_format")

        if pack_format < 48:
            raise ValueError("Datapacks with pack_format less than 48 (minecraft < 1.21) are not supported")

        return pack_format

    @staticmethod
    def __get_min_inclusive(format_field: [int, list[int, int], dict[str, int]]) -> int | None:
        """
        Extracts the minimum inclusive `pack_format` from a given format field.

        :param format_field: The format field.
        :return: An integer representing the minimum inclusive `pack_format`, or `None` if the format is invalid.
        """
        if isinstance(format_field, int):
            return format_field  # If it's just an int, return it

        elif isinstance(format_field, list):
            return min(format_field)  # If it's a list, take the minimum value

        elif isinstance(format_field, dict):
            return format_field.get("min_inclusive", None)  # If it's a dict, return min_inclusive

        return None  # If the format is invalid, return None

    def _get_max_min_overlay_directory(self) -> Path:
        """
        Determines the overlay directory with the highest minimum `pack_format` value.

        :return: A `Path` object representing the directory of the overlay with the highest minimum inclusive format.
        :raises ValueError: If the `overlays` dictionary does not contain `entries`, or if any entry has invalid formats.
        :raises KeyError: If an entry is missing the `formats` dictionary or `directory` field.
        """
        overlays = self._json.get("overlays", {})
        entries = overlays.get("entries", [])

        if not entries:
            raise ValueError("pack.mcmeta does not have entries, while having \"overlays\" dictionary")

        max_min_inclusive = float("-inf")
        max_min_inclusive_directory = None

        for entry in entries:
            formats = entry.get("formats")
            if formats is None:
                raise KeyError(f"entry \"{entry}\" does not have \"formats\" dictionary")

            min_inclusive = self.__get_min_inclusive(formats)
            if min_inclusive is None:
                raise ValueError(f"{formats} is not in a valid format")

            if min_inclusive > max_min_inclusive:
                max_min_inclusive_directory = entry.get("directory")
                if max_min_inclusive_directory is None:
                    raise KeyError(f"entry \"{entry}\" does not have \"directory\" field")
                max_min_inclusive = min_inclusive

        return max_min_inclusive_directory

    @property
    def path(self) -> Path:
        """
        :return: The path to the `pack.mcmeta` file.
        """
        return self._path

    @property
    def json(self) -> dict:
        """
        :return: The parsed JSON content of the `pack.mcmeta` file.
        """
        return self._json

    @property
    def data_path(self) -> Path:
        """
        :return: The path to the `data` directory or the data directory in the latest overlay in the datapack.
        """
        return self._data_path

    @property
    def description(self) -> str | None:
        """
        :return: The description of the datapack, or ``None`` if datapack does not contain it.
        """
        return self._description

    @property
    def pack_format(self) -> int:
        """
        :return: Pack format of the datapack.
        """
        return self._pack_format
