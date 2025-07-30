class Criteria:
    def __init__(self, name: str, trigger: str, conditions: dict | None = None):
        """
        Class of the advancement criteria.
        :param name: Name of the criteria.
        :param trigger: Trigger of the criteria.
        :param conditions: Conditions of the criteria as raw dict object.
        """
        self._name = name
        self._trigger = trigger
        self._conditions = conditions
        self._is_impossible = None

    @property
    def name(self) -> str:
        """
        :return: name of the criteria
        """
        return self._name

    @property
    def trigger(self) -> str:
        """
        :return: trigger of the criteria
        """
        return self._trigger

    @property
    def conditions(self) -> dict | None:
        return self._conditions

    def __repr__(self):
        return f"<Criteria name={self._name}, trigger={self._trigger}"

    def __str__(self):
        return f"<Criteria name={self._name}, trigger={self._trigger}"

    def __eq__(self, other: "Criteria") -> bool:
        if not isinstance(other, Criteria):
            raise TypeError("Element must be an instance of the Criteria class")
        return (self._name == other._name) and (self._trigger == other._trigger) and (self._conditions == other._conditions)

    def __ne__(self, other: "Criteria") -> bool:
        return not self.__eq__(other)

    @property
    def is_impossible(self):
        """
        :return: True if criteria is impossible, False otherwise
        """
        if self._is_impossible is None:
            self._is_impossible = self._trigger == "impossible"
        return self._is_impossible
