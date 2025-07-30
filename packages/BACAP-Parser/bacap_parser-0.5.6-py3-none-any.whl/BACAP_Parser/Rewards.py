import re
from collections.abc import MutableSequence
from pathlib import Path

from .ExtendedDict import ExtendedDict
from .patterns import exp_pattern
from .nbt_decoder import nbt_decoder
from .patterns import reward_give_pattern, reward_summon_pattern, trophy_give_pattern, trophy_summon_pattern
from .components_decoder import components_decoder
from .Item import RewardItem, TrophyItem
from .Color import Color


class DefaultReward:
    def __init__(self, path: Path, mcpath: str):
        """
        Default class for all rewards.
        :param path: Path to the reward file.
        :param mcpath: Minecraft path of the reward
        """
        self._path = path
        self._mcpath = mcpath
        self._raw_text = self._path.read_text(encoding='utf-8').strip()

    @property
    def path(self) -> Path:
        """
        :return: Path to the reward file.
        """
        return self._path

    @property
    def mcpath(self) -> str:
        """
        :return: Minecraft internal path to the file.
        """
        return self._mcpath

    @property
    def raw_text(self) -> str:
        """
        :return: Raw text of the reward file.
        """
        return self._raw_text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._mcpath})"


class Exp(DefaultReward):
    """
    Default class for all exp rewards.
    """
    def __init__(self, path: Path, mcpath: str):
        """
        Class for Exp reward.
        :param path: Path to the reward file.
        :param mcpath: Minecraft path of the reward
        :raises ValueError: If the reward file is invalid/empty.
        """
        super().__init__(path, mcpath)
        self._value = self.__parse_exp()

        if self._value is None:
            raise ValueError("Invalid experience value: None")

    def __parse_exp(self):
        if not self._raw_text:
            return None

        search = re.search(exp_pattern, self._raw_text)
        if search:
            return int(search.groups()[0])

        return None

    @property
    def value(self) -> int:
        """
        :return: Experience amount value.
        """
        return self._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._mcpath}, exp:{self._value})"


class Reward(DefaultReward):
    __item_class = RewardItem

    def __init__(self, path: Path, mcpath: str):
        """
        Class for Item reward.
        :param path: Path to the reward file.
        :param mcpath: Minecraft path of the reward
        :raises ValueError: If the reward file is invalid/empty.
        """
        super().__init__(path, mcpath)
        self._command_type = None
        self._item = self.__parse_reward()

        if self._item is None:
            raise ValueError("Invalid reward item: None")

    def __parse_reward(self) -> RewardItem | None:
        if not self._raw_text:
            return None

        item_type_match = re.search(r"tellraw .*?{\"translate\":\"(item|block)", self._raw_text)
        item_type = item_type_match.group(1) if item_type_match else None

        match = re.search(reward_give_pattern, self._raw_text)
        if match:
            command_data = match.groupdict()
            self._command_type = "give"

            components = components_decoder(command_data["components"]) if command_data.get("components") else None
            return self.__item_class(command_data["item_id"], components, item_type, command_data["amount"])

        match = re.search(reward_summon_pattern, self._raw_text)
        if match:
            nbt_data = nbt_decoder(match.groupdict()["nbt"])
            self._command_type = "summon"

            return self.__item_class(nbt_data["Item"]["id"], nbt_data["Item"]["count"], item_type, nbt_data["Item"].get("components"))

        return None

    @property
    def command_type(self) -> str:
        """
        :return: Command type of the reward. Can be "give" or "summon".
        """
        return self._command_type

    @property
    def item(self) -> RewardItem:
        """
        :return: Item of the reward.
        """
        return self._item

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._mcpath}, {self._item})"


class Trophy(DefaultReward):
    __item_class = TrophyItem

    def __init__(self, path: Path, mcpath: str):
        """
        Class for Trophy reward.
        :param path: Path to the reward file.
        :param mcpath: Minecraft path of the reward
        :raises ValueError: If the reward file is invalid/empty.
        """
        super().__init__(path, mcpath)
        self._command_type = None
        self._item = self.__parse_trophy()

        if self._item is None:
            raise ValueError("Invalid trophy item: None")

    @staticmethod
    def __parse_description(lore: MutableSequence) -> list:
        desc_list = []

        for line in lore[:-3]:
            if isinstance(line, ExtendedDict):
                desc_list.append(line.get_with_multiple_values("text", "translate"))
            elif isinstance(line, list):
                desc_list.append("".join([element.get_with_multiple_values("text", "translate") for element in line]))
        return desc_list

    def __parse_trophy(self) -> TrophyItem | None:
        if not self._raw_text:
            return None

        give_search = re.search(trophy_give_pattern, self._raw_text)
        if give_search:
            self._command_type = "give"
            item_id = give_search["item_id"]
            components = components_decoder(give_search.groupdict()["components"])

        else:
            summon_search = re.search(trophy_summon_pattern, self._raw_text)
            if not summon_search:
                return None

            self._command_type = "summon"
            nbt = nbt_decoder(summon_search.groupdict()["nbt"])
            item_id = nbt["Item"]["id"]
            components = nbt["Item"]["components"]

        custom_name = components.get_with_multiple_values("custom_name", "item_name")
        name = custom_name.get_with_multiple_values("text", "translate")
        color = custom_name.get("color", None)

        if color:
            color = Color(color)

        description = "\n".join(x for x in self.__parse_description(components.get("lore", [])) if ".minecraft." not in x)

        return self.__item_class(item_id=item_id, components=components, name=name, color=color, description=description)

    @property
    def command_type(self) -> str:
        """
        :return: Command type of the reward. Can be "give" or "summon".
        """
        return self._command_type

    @property
    def item(self) -> TrophyItem:
        """
        :return: Trophy item of the reward.
        """
        return self._item

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._mcpath}, {self._item})"