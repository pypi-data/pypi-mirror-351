from collections.abc import Iterable
from pathlib import Path
from typing import Type

from .utils import to_collection
from .AdvType import AdvTypeManager
from .TabNameMapper import TabNameMapper
from .Rewards import Exp, Reward, Trophy
from .PackMCMeta import PackMCMeta

class Datapack:
    """
    Class that represents a Datapack folder
    """
    def __init__(self, name: str, path: Path, adv_type_manager: AdvTypeManager, reward_namespace: str | None = None,
                 technical_tabs: Iterable[str] | None = None, tab_name_mapper: TabNameMapper = TabNameMapper(),
                 exp_class: Type[Exp] = Exp, reward_class: Type[Reward] = Reward, trophy_class: Type[Trophy] = Trophy):
        """
        :param name: Name of the datapack that will be used to identify it in Parser instance
        :param path: Path to the datapack folder, zip-files are not supported
        :param adv_type_manager: AdvTypeManager instance
        :param reward_namespace: namespace where rewards (exp, trophy, reward) are stored.
        If None Exp, Trophy and item rewards will not be parsed.
        :param technical_tabs: A list of tabs with technical advancements
        :param tab_name_mapper: TabNameMapper instance with custom tabs, if not specified.
        It will be created automatically with default BACAP tabs
        :param exp_class: Specifies the class to be used for parsing the experience (exp) part of the achievement.
            The provided class must inherit from the base `Exp` class.
        :param reward_class: Specifies the class to be used for parsing the reward part of the achievement.
            The provided class must inherit from the base `Reward` class.
        :param trophy_class: Specifies the class to be used for parsing the trophy part of the achievement.
            The provided class must inherit from the base `Trophy` class.
        :raises NotImplementedError: If a zipped datapack path is given.
        :raises FileNotFoundError: If reward_namespace does not exist in the datapack namespaces.
        :raises ValueError: If exp_class, reward_class, reward_class are not inherited from Exp, Reward, Trophy classes.
        """
        from .Advancement import AdvancementManager
        self._name = name

        if path.suffix == '.zip':
            raise NotImplementedError("Zipped datapacks not supported, unpack it to the folder first")

        self._path = path

        technical_tabs = to_collection(technical_tabs, tuple)

        self._pack_mcmeta = PackMCMeta(self._path)

        self._namespaces = [entry for entry in self._pack_mcmeta.data_path.iterdir() if entry.is_dir()]

        if reward_namespace is not None:
            if reward_namespace not in [entry.name for entry in self._namespaces]:
                raise FileNotFoundError(f"Reward namespace \"{reward_namespace}\" does not exist, possible namespaces: {[entry.name for entry in self._namespaces]}")
            self._reward_namespace_path = next(entry for entry in self._namespaces if entry.name == reward_namespace)
        else:
            self._reward_namespace_path = None

        self._reward_namespace = reward_namespace

        self._adv_type_manager = adv_type_manager

        self.__check_inheritance(exp_class, Exp)
        self._exp_class = exp_class
        self.__check_inheritance(reward_class, Reward)
        self._reward_class = reward_class
        self.__check_inheritance(trophy_class, Trophy)
        self._trophy_class = trophy_class

        self._tab_name_mapper = tab_name_mapper

        self._advancement_manager = AdvancementManager(datapack=self, technical_tabs=technical_tabs)

    @staticmethod
    def __check_inheritance(base_class: type, derived_class: type):
        """
        Checks whether a given class inherits from a specified base class.

        :param base_class: The class that is expected to be inherited from.
        :param derived_class: The class to check for inheritance.
        :raises ValueError: If `derived_class` does not inherit from `base_class`.
        """

        if not issubclass(derived_class, base_class):
            raise ValueError(f"`{derived_class.__name__}` must inherit from `{base_class.__name__}`.")

    def __repr__(self):
        return f"Datapack('{self._name}')"

    @property
    def name(self) -> str:
        """
        :return: Name of the datapack
        """
        return self._name

    @property
    def path(self):
        """
        :return: Path to the datapack
        """
        return self._path

    @property
    def adv_type_manager(self):
        """
        :return: AdvTypeManager instance of the datapack
        """
        return self._adv_type_manager

    @property
    def advancement_manager(self):
        """
        :return: AdvancementManager instance of the datapack
        """
        return self._advancement_manager

    @property
    def reward_namespace(self):
        """
        :return: namespace that contains advancement rewards of the datapack
        """
        return self._reward_namespace

    @property
    def reward_namespace_path(self):
        """
        :return: path to the reward_namespace
        """
        return self._reward_namespace_path

    @property
    def namespaces(self):
        """
        :return: list of namespaces of the datapack
        """
        return self._namespaces

    @property
    def tab_name_mapper(self):
        """
        :return: TabMap instance of the datapack
        """
        return self._tab_name_mapper

    @property
    def exp_class(self):
        """
        :return: Class that will be used to parse and store experience rewards of the advancements
        """
        return self._exp_class

    @property
    def reward_class(self):
        """
        :return: Class that will be used to parse and store item rewards of the advancements
        """
        return self._reward_class

    @property
    def trophy_class(self):
        """
        :return: Class that will be used to parse and store trophy rewards of the advancements
        """
        return self._trophy_class

    @property
    def pack_mcmeta(self):
        return self._pack_mcmeta

    @property
    def data_path(self) -> path:
        return self._pack_mcmeta.data_path