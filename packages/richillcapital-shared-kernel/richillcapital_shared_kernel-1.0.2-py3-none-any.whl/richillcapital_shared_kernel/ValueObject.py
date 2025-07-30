from abc import ABCMeta, abstractmethod
from typing import Iterable


class ValueObject(metaclass=ABCMeta):
    """
    Base class for value objects.
    """

    @abstractmethod
    def _get_atomic_values(self) -> Iterable[object]: ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return False

        return self._get_atomic_values() == other._get_atomic_values()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(tuple(self._get_atomic_values()))


class SingleValueObject[TValue](ValueObject):
    """
    Represents a single value object.
    """

    def __init__(self, value: TValue):
        self.__value = value

    @property
    def value(self) -> TValue:
        """
        Returns the value of the ValueObject.

        Returns:
            TValue: The value of the ValueObject.
        """
        return self.__value

    def __str__(self) -> str:
        return str(self.__value)

    def _get_atomic_values(self) -> Iterable[object]:
        return [self.value]
