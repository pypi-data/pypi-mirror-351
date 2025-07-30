from collections.abc import Callable, Iterable
from typing import Union

from .Criteria import Criteria


class CriteriaList(list):
    def __init__(self, adv_criteria: Union[dict, Criteria, list, "CriteriaList", None] = None, *args, **kwargs):
        """
        :param adv_criteria: dict with parsed criteria JSON, list of Criteria, CriteriaList, single Criteria or None
        """
        super().__init__(*args, **kwargs)
        if adv_criteria is None:
            return

        elif isinstance(adv_criteria, CriteriaList):
            self.extend(adv_criteria)

        elif isinstance(adv_criteria, dict):
            for name, crit in adv_criteria.items():
                criteria = Criteria(name, crit["trigger"], conditions=crit.get("conditions"))
                self.append(criteria)

        elif isinstance(adv_criteria, Criteria):
            self.append(adv_criteria)

        elif isinstance(adv_criteria, list):
            if not all(isinstance(item, Criteria) for item in adv_criteria):
                raise TypeError("All elements must be instances of the Criteria class")
            self.extend(adv_criteria)
        else:
            raise TypeError("Argument must be a dict, Criteria object, or a list of Criteria objects")

    def is_all_impossible(self) -> bool:
        """
        :return: True if all criteria are impossible, False otherwise
        """
        return all(criteria.is_impossible for criteria in self)

    def __repr__(self):
        return super().__repr__()

    def append(self, criteria: Criteria):
        if not isinstance(criteria, Criteria):
            return TypeError("Element must be an instance of the Criteria class")
        super().append(criteria)

    def __str__(self):
        return super().__str__()

    def extend(self, criteria_list: Union["CriteriaList", Iterable[Criteria]]):
        if not all(isinstance(criteria, Criteria) for criteria in criteria_list):
            raise TypeError("All elements must be instances of the Criteria class")
        super().extend(criteria_list)

    def insert(self, __index, __object):
        if not isinstance(__object, Criteria):
            return TypeError("Element must be an instance of the Criteria class")
        super().insert(__index, __object)

    def sort(self, *, key: Callable = None, reverse: bool = False):
        if key is None:
            key = lambda criteria: criteria.name
        super().sort(key=key, reverse=reverse)

    def count(self, criteria: str | Criteria) -> int:
        """
        :param criteria: Criteria to count (will check both trigger and name string equation), or criteria name
        :return:
        """
        if isinstance(criteria, Criteria):
            return super().count(criteria)
        return sum(crt.name == criteria for crt in self)

    def remove(self, criteria: Criteria | str, **kwargs):
        """
        :param criteria: Criteria to remove (will check both trigger and name string equation), or criteria name
        """
        if isinstance(criteria, Criteria):
            for crit in self:
                if criteria.name == crit.name and criteria.trigger == crit.trigger:
                    self.remove(criteria)
        else:
            for criteria in self:
                if criteria.name == criteria:
                    self.remove(criteria)

    def __eq__(self, other: "CriteriaList") -> bool:
        if not isinstance(other, CriteriaList):
            return NotImplemented
        return super().__eq__(other)

    def __contains__(self, criteria: Criteria) -> bool:
        """
        :param criteria: Criteria to check
        :return: True if criteria is in CriteriaList, False otherwise
        """
        if not isinstance(criteria, Criteria):
            raise TypeError("Element must be an instance of the Criteria class")
        return any(crt.name == criteria.name and crt.trigger == criteria.trigger for crt in self)

    def __ne__(self, other: "CriteriaList") -> bool:
        return super().__ne__(other)

    def __add__(self, other: "CriteriaList") -> "CriteriaList":
        """
        :param other: Other CriteriaList
        :return: New CriteriaList that contains both lists
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Element must be an instance of the CriteriaList class")
        new_list = CriteriaList(self)
        new_list.extend(other)
        return new_list

    def __or__(self, other: "CriteriaList") -> "CriteriaList":
        """
        :param other: Other CriteriaList
        :return: New CriteriaList that contains elements from both lists
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Element must be an instance of the CriteriaList class")
        return self + other

    def __and__(self, other):
        """
        :param other: Other CriteriaList
        :return: New CriteriaList that contains elements that are in both lists
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Other element must be an instance of the CriteriaList class")
        new_list = CriteriaList()
        for crit in self:
            if crit in self and crit in other:
                new_list.append(crit)
        return new_list

    def __xor__(self, other: "CriteriaList"):
        if not isinstance(other, self.__class__):
            raise TypeError("Other element must be an instance of the CriteriaList class")
        new_list = CriteriaList()

        for crit in self:
            if crit not in other:
                new_list.append(crit)

        for crit in other:
            if crit not in self:
                new_list.append(crit)

        return new_list