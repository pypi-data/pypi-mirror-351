from collections.abc import Iterable, Iterator
from functools import reduce
from pathlib import Path
from typing import Literal, Type, Any

from .AdvType import AdvType
from .ExtendedDict import ExtendedDict
from .constants import DEFAULT_MINECRAFT_DESCRIPTION_COLOR, DEFAULT_MINECRAFT_FRAME, DEFAULT_MINECRAFT_FRAME_COLOR_MAP
from .Color import Color
from .CriteriaList import CriteriaList
from .Datapack import Datapack
from .Item import Item
from .Rewards import Exp, Trophy, Reward
from .utils import path_to_mc_path, safe_load_json_file, trim_path_to_namespace


class AdvancementException(Exception):
    """
    A default exception class for handling errors during advancement initialization.
    Serves as a base class for creating other specific advancement-related exceptions.
    """

    def __init__(self, message="Something went wrong"):
        super().__init__(message)


class JSONParsingError(AdvancementException):
    """
    Exception raised when parsing JSON data fails.
    Indicates that the provided JSON data could not be successfully parsed.
    """

    def __init__(self):
        super().__init__("Failed to parse JSON data")


class InvalidRewardFunction(AdvancementException):
    """
    Exception raised when an invalid reward function is passed, or reward function does not exist.
    """
    def __init__(self):
        super().__init__("Advancement does not contain a valid reward function")


class MissingTitleField(AdvancementException):
    """
    Exception raised when a title does not exist.
    """
    def __init__(self):
        super().__init__("Advancement does not contain a title")


class MissingDescriptionField(AdvancementException):
    """
    Exception raised when description does not exist.
    """
    def __init__(self):
        super().__init__("Advancement does not contain a description")


class BaseAdvancement:
    def __init__(self, path: Path, adv_json: ExtendedDict | None, datapack: Datapack):
        """
        Initializes a new instance of the BaseAdvancement class.
        :param path: The file path to the advancement JSON file.
        :param adv_json: Parsed JSON file as dict.
        """
        self._json = adv_json
        self._path = path
        self._datapack = datapack

        self._filename = path.stem
        self._mc_path = path_to_mc_path(trim_path_to_namespace(self._path, self._datapack.namespaces))
        self._namespace = path.parts[0]
        self._criteria_list = CriteriaList(self._json["criteria"])

        if self._json:
            self._parent = self._json.get("parent")
        else:
            self._parent = None

    @property
    def path(self) -> Path:
        """
        :return: The file path.
        """
        return self._path

    @property
    def json_string(self) -> str:
        """
        :return: The raw JSON string of the advancement.
        """
        return self._path.read_text(encoding="utf-8")

    @property
    def json(self) -> dict | None:
        """
        :return: The JSON content of the advancement.
        """
        return self._json

    @property
    def parent(self) -> str | None:
        """
        :return: The Minecraft Path of the parent advancement, if any.
        """
        return self._parent

    @property
    def mc_path(self) -> str:
        """
        Returns the path of the advancement in Minecraft format.
        """
        return self._mc_path

    @property
    def namespace(self) -> str:
        """
        Returns the namespace of the advancement.
        """
        return self._namespace

    @property
    def filename(self) -> str:
        """
        Returns the file name of the advancement without extension.
        """
        return self._filename

    @property
    def criteria_list(self) -> CriteriaList:
        """
        Returns a 'CriteriaList' of criteria for the advancement
        """
        return self._criteria_list

    # To sort in alphabetic order by mcpath
    def __gt__(self, other):
        return self.mc_path > other.mc_path

    def __lt__(self, other):
        return self.mc_path < other.mc_path

    def __ge__(self, other):
        return self.mc_path >= other.mc_path

    def __le__(self, other):
        return self.mc_path <= other.mc_path

    def __str__(self):
        return f"{self.__class__.__name__}({self._path})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self._path})"


class InvalidAdvancement(BaseAdvancement):
    """
    Class representing invalid advancement.
    Inherits from BaseAdvancement.
    """

    def __init__(self, reason: AdvancementException, path: Path, adv_json: dict | None, datapack: Datapack):
        """
        Initializes a new instance of the InvalidAdvancement class.
        :param path: The file path to the advancement JSON file.
        :param datapack: The name of datapack.
        :param reason (str, optional): The reason why the advancement is considered invalid.
        """
        super().__init__(path, adv_json, datapack)
        self._reason = reason

    @property
    def reason(self) -> AdvancementException:
        """
        :return: The reason why the advancement is considered invalid.
        """
        return self._reason


class TechnicalAdvancement(BaseAdvancement):
    """
    Class representing technical advancement.
    Inherits from BaseAdvancement.
    """

    def __init__(self, path: Path, datapack: Datapack, adv_json):
        """
        Initializes a new instance of the TechnicalAdvancement class.
        :param path: The file path to the advancement JSON file.
        :param datapack: The name of datapack.
        """
        super().__init__(path, adv_json, datapack)


class Advancement(BaseAdvancement):
    """
    Class representing normal advancement.
    Inherits from BaseAdvancement.
    """

    def __init__(self, path: Path, adv_json: ExtendedDict, datapack: Datapack, reward_mcpath: str, tab: str, color: Color, frame: str, adv_type: AdvType,
                 hidden: bool):
        """
        Creates a new instance of the Advancement class

        :param path: The file path to the advancement JSON file.
        :param adv_json: The JSON data for the advancement.
        :param tab: The tab for advancement.
        :param color: The color for the advancement.
        :param frame: The frame type for advancement.
        :param adv_type: The AdvType class of advancement.
        :param hidden: Whether the advancement is hidden.
        :return: An instance of Advancement.
        """

        super().__init__(path, adv_json, datapack)
        self._tab = tab
        self._color = color
        self._frame = frame
        self._hidden = hidden
        self._type = adv_type
        self._reward_mcpath = reward_mcpath
        self._title = self._json["display"]["title"]["translate"]
        self._description = self._json["display"]["description"]["translate"]
        if "extra" in self._json["display"]["description"]:
            self._get_description_from_extra()
        self._background = self._json["display"].get("background")
        self._icon = Item(self._json["display"]["icon"])

        if self._datapack.reward_namespace_path is not None:
            self._exp = self._initialize_reward("exp", self._datapack.exp_class)
            self._reward = self._initialize_reward("reward", self._datapack.reward_class)
            self._trophy = self._initialize_reward("trophy", self._datapack.trophy_class)
        else:
            self._exp = None
            self._reward = None
            self._trophy = None

    def _get_description_from_extra(self):
        for item in self._json["display"]["description"].get("extra", []):
            if not item:
                continue
            text_value = item.get_with_multiple_values("text", "translate", default="")
            if isinstance(item, dict) and (item.get("color") == self._color.value or text_value == "\n" or text_value.rstrip("\n") == ""):
                self._description += text_value
        self._description = self._description.rstrip("\n")

    def _initialize_reward(self, name: Literal["exp", "reward", "trophy"], cls: Type[Exp | Reward | Trophy]):
        """
        :param name: Name of the reward: "exp", "reward", "trophy".
        :param cls: Class of the reward to be initialized (Exp, Reward, Trophy).
        :return: Instance of the reward class or None if initialization fails.
        """
        reward_path = self._build_reward_path(name)
        if reward_path.exists():
            try:
                return cls(reward_path, self._build_reward_mcpath(name))
            except ValueError:
                return None
        return None

    def _build_reward_mcpath(self, reward_type: Literal["exp", "reward", "trophy"]) -> str:
        namespace, folders = self._reward_mcpath.split(":", 1)
        return f"{namespace}:{reward_type}/{folders}"

    def _build_reward_path(self, reward_type: Literal["exp", "reward", "trophy"]) -> Path:
        return self._datapack.reward_namespace_path / f"function/{reward_type}/{self._reward_mcpath.split(":", 1)[1]}.mcfunction"

    @property
    def title(self) -> str:
        """
        :return: the title of the advancement.
        """
        return self._title

    @property
    def description(self) -> str:
        """
        :return: the description of the advancement.
        """
        return self._description

    @property
    def type(self) -> AdvType:
        """
        :return: The type of the advancement
        """
        return self._type

    @property
    def tab_display(self) -> str | None:
        """
        :return: The tab of the advancement that is displayed in minecraft advancement interface.
        """
        return self._datapack.tab_name_mapper.get(self._tab)

    @property
    def tab(self) -> str:
        """
        :return: The tab (folder) of the advancement.
        """
        return self._tab

    @property
    def color(self) -> Color | None:
        """
        :return: The color class of the advancement description.
        """
        return self._color

    @property
    def frame(self) -> str | None:
        """
        :return: The frame of the advancement.
        """
        return self._frame

    @property
    def hidden(self) -> bool:
        """
        :return: Is advancement hidden or not.
        """
        return self._hidden

    @property
    def background(self) -> str | None:
        """
        :return: Background path if it is root advancement.
        """
        return self._background

    @property
    def is_root(self) -> bool:
        """
        :return: Is this advancement a root of the tab, by checking the background Minecraft Path.
        """
        return self._background is not None

    @property
    def icon(self) -> Item:
        """
        :return: The Item class of the advancement icon.
        """
        return self._icon

    @property
    def reward_mcpath(self) -> str:
        """
        :return: The Minecraft path of the reward function.
        """
        return self._reward_mcpath

    @property
    def exp(self) -> Exp | None:
        """
        :return: Exp class if exp reward exists, else None.
        """
        return self._exp

    @property
    def reward(self) -> Reward | None:
        """
        :return: Reward class if item reward exists, else None.
        """
        return self._reward

    @property
    def trophy(self) -> Trophy| None:
        """
        :return: Trophy class if Trophy reward exists, else None.
        """
        return self._trophy

    def __repr__(self):
        return f"{self.__class__.__name__}([{self._datapack}] {self._mc_path})"

    def __str__(self):
        return f"{self.__class__.__name__}([{self._datapack}] {self._mc_path})"

class AdvancementManager:
    def __init__(self, datapack: Datapack, technical_tabs: Iterable[str] | None):
        """
        Initializes a new instance of the AdvancementManager class.
        :param datapack: Datapack instance
        """
        self._datapack = datapack

        self._advancement_folders = self._get_advancement_folders(datapack.data_path)
        self._technical_tabs_paths = [
            advancement_folder / technical_tab
            for advancement_folder in self._advancement_folders
            for technical_tab in technical_tabs
            if (advancement_folder / technical_tab).is_dir()
        ]

        self._advancements_dict: dict[Path, InvalidAdvancement | TechnicalAdvancement | Advancement] = {}
        self.__load_advancements()
        self._advancements_list: list = list(self._advancements_dict.values())

    def __load_advancements(self):
        for adv_folder in self._advancement_folders:
            for adv_path in adv_folder.rglob('*.json'):
                self._advancements_dict[adv_path] = _AdvancementFactory.load_advancement(adv_path, self)

    @staticmethod
    def _get_advancement_folders(data_path) -> list[Path]:
        advancement_folders = []

        for namespace in data_path.iterdir():
            if not namespace.is_dir():
                continue

            advancement_path = namespace / "advancement"

            if advancement_path.exists() and advancement_path.is_dir():
                advancement_folders.append(advancement_path)

        return advancement_folders

    @property
    def technical_tabs_paths(self) -> list[Path]:
        """
        :return: A list of paths to the technical tabs.
        """
        return self._technical_tabs_paths

    @property
    def adv_list(self) -> list[Advancement | InvalidAdvancement | TechnicalAdvancement]:
        """
        :return: A list of Advancement instances.
        """
        return self._advancements_list

    @property
    def adv_dict(self) -> dict[Path, Advancement | InvalidAdvancement | TechnicalAdvancement]:
        """
        :return: A dictionary of Advancement instances.
        """
        return self._advancements_dict

    def filtered_list(
            self,
            skip_invalid: bool = True, skip_technical: bool = True, skip_normal: bool = False) -> list[Advancement | InvalidAdvancement | TechnicalAdvancement]:
        """
        Returns list of advancements by parameters.
        """
        return list(self.filtered_iterator(skip_invalid, skip_technical, skip_normal))

    @staticmethod
    def __advancement_type_skip_check(adv: Advancement | InvalidAdvancement | TechnicalAdvancement, skip_invalid: bool, skip_technical: bool, skip_normal: bool):
        valid_advancement = not skip_invalid or not isinstance(adv, InvalidAdvancement)
        technical_advancement = not skip_technical or not isinstance(adv, TechnicalAdvancement)
        normal_advancement = not skip_normal or not isinstance(adv, Advancement)
        return valid_advancement and technical_advancement and normal_advancement

    def filtered_iterator(
            self,
            skip_invalid: bool = True,
            skip_technical: bool = True,
            skip_normal: bool = False
    ) -> Iterator[Advancement | InvalidAdvancement | TechnicalAdvancement]:
        """
        Return Iterator of advancements by parameters.
        """
        for adv in self._advancements_list:
            if self.__advancement_type_skip_check(adv, skip_invalid, skip_technical, skip_normal):
                yield adv

    def find(self, criteria: dict[str, Any], limit: int = None, skip_invalid: bool = True, skip_technical: bool = True, skip_normal: bool = False,
             invert: bool = False) -> list[Advancement | InvalidAdvancement | TechnicalAdvancement]:
        """
        Returns list of advancements by search parameters.
        :param skip_normal: Skip normal Advancement if True.
        :param skip_technical: Skip technical Advancement if True.
        :param skip_invalid: Skip invalid Advancement if True.
        :param criteria: A dict, where key is attribute, value is expected value.
        :param limit: How many find advancements.
        None if no limit
        :param invert: Invert find.
        If True, advancement, which fits the criteria, doesn't be added.
        :return: Instance of Advancement
        """
        iterator = self.filtered_iterator(skip_invalid, skip_technical, skip_normal)
        advancement_list = []
        count = 0
        for adv in iterator:
            if limit and count >= limit:
                break
            for attr, value in criteria.items():
                if (getattr(adv, attr) == value) == invert:
                    continue
                count += 1
                advancement_list.append(adv)
        return advancement_list

    def deep_find(self, criteria: dict[str, Any], limit: int = None, skip_invalid: bool = True, skip_technical: bool = True, skip_normal: bool = False,
                  invert: bool = False) -> list[Advancement | InvalidAdvancement | TechnicalAdvancement]:
        """
        Returns list of advancements by search parameters.
        :param skip_normal: Skip normal Advancement if True.
        :param skip_technical: Skip technical Advancement if True.
        :param skip_invalid: Skip invalid Advancement if True.
        :param criteria: A dict, where key is attribute, value is expected value.
        Key also can contain `.` and the value will be transformed to str.
        If value also can be callable, value will be transformed
        :param limit: How many find advancements.
        None if no limit
        :param invert: Invert find.
        If True, advancement, which fits the criteria, doesn't be added.
        :return: Instance of Advancement
        """

        def iterative_getattr(obj, attr):
            return reduce(getattr, attr.split('.'), obj)

        iterator = self.filtered_iterator(skip_invalid, skip_technical, skip_normal)
        advancement_list = []
        count = 0
        for adv in iterator:
            if limit and count >= limit:
                break
            for criteria_attr, value in criteria.items():
                attr_value = iterative_getattr(adv, criteria_attr)

                if callable(value) and value(attr_value) == invert:
                    continue
                elif not callable(value):
                    value_in_attr = value in str(attr_value)
                    if value_in_attr == invert:
                        continue
                count += 1
                advancement_list.append(adv)
        return advancement_list

    @property
    def datapack(self) -> Datapack:
        """
        Returns the datapack instance
        """
        return self._datapack

    def is_technical_advancement(self, path_to_adv: Path) -> bool:
        """
        Checks is the advancement path is relative to technical paths of the datapack.
        :param path_to_adv: Path to the advancement file.
        :return: True if the advancement path is relative to technical paths, else False.
        """
        return any(path_to_adv.is_relative_to(t_p) for t_p in self._technical_tabs_paths)


class _AdvancementFactory:
    @classmethod
    def load_advancement(cls, path: Path, advancement_manager: AdvancementManager) -> Advancement | TechnicalAdvancement | InvalidAdvancement:
        adv_json: ExtendedDict = safe_load_json_file(path)

        if cls._is_not_parsable_json(adv_json):
            return InvalidAdvancement(path=path, adv_json=adv_json, reason=JSONParsingError(), datapack=advancement_manager.datapack)

        if advancement_manager.is_technical_advancement(path):
            return TechnicalAdvancement(path, advancement_manager.datapack, adv_json)

        if cls._is_invalid_reward(adv_json):
            return InvalidAdvancement(path=path, adv_json=adv_json, reason=InvalidRewardFunction(), datapack=advancement_manager.datapack)

        reward_mcpath = adv_json["rewards"]["function"]

        if cls._has_no_title(adv_json):
            return InvalidAdvancement(path=path, adv_json=adv_json, reason=MissingTitleField(), datapack=advancement_manager.datapack)

        if cls._has_no_description(adv_json):
            return InvalidAdvancement(path=path, adv_json=adv_json, reason=MissingDescriptionField(), datapack=advancement_manager.datapack)

        tab: str = cls._get_tab(reward_mcpath)
        color_data = adv_json["display"]["description"].get("color")
        frame_data = adv_json["display"].get("frame")

        if frame_data:
            frame: str = frame_data
        else:
            frame: str = DEFAULT_MINECRAFT_FRAME

        if color_data:
            color: Color = Color(color_data)
        elif frame_data:
            color: Color = DEFAULT_MINECRAFT_FRAME_COLOR_MAP[frame_data]
        else:
            color: Color = DEFAULT_MINECRAFT_DESCRIPTION_COLOR


        hidden: bool = adv_json["display"].get("hidden", False)

        adv_type: AdvType = advancement_manager.datapack.adv_type_manager.recognize_type(frame=frame, color=color, tab=tab)

        return Advancement(path, adv_json, advancement_manager.datapack, reward_mcpath, tab, color, frame, adv_type, hidden)

    @staticmethod
    def _get_tab(reward_mcpath: str) -> str:
        return reward_mcpath.split(":", 1)[1].split("/", 1)[0]

    @staticmethod
    def _is_not_parsable_json(advancement_json: ExtendedDict) -> bool:
        return advancement_json is None

    @staticmethod
    def _has_no_title(advancement_json: ExtendedDict) -> bool:
        required_keys = (
            ("display", "title", "translate"),
            ("display", "title", "text")
        )
        return not any(advancement_json.can_access_keypath(keys) for keys in required_keys)

    @staticmethod
    def _has_no_description(advancement_json: ExtendedDict) -> bool:
        required_keys = (
            ("display", "description", "translate"),
            ("display", "description", "text")
        )
        return not any(advancement_json.can_access_keypath(keys) for keys in required_keys)

    @staticmethod
    def _is_invalid_reward(advancement_json: ExtendedDict) -> bool:
        return not advancement_json.can_access_keypath(("rewards", "function"))
