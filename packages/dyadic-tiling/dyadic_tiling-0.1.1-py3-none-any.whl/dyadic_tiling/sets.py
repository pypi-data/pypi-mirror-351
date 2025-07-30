from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

from sortedcontainers import SortedList

from dyadic_tiling.point import Point


class AbstractSet(ABC):
    """
    Abstract base class for a Set. Provides a common interface for different types of sets.
    """

    @abstractmethod
    def __contains__(self, item: Point | "DyadicCube") -> bool:
        """
        Check if the set contains a given Point or Cube.

        :param point: A Point or Cube to check for membership.
        :return: True if the set contains the point, False otherwise.
        """
        pass

    @abstractmethod
    def get_set(self) -> Union[SortedList, "AbstractSet"]:
        """
        Get the internal representation of the set.

        :return: A SortedList or another AbstractSet representing the elements of the set.
        """
        pass

    @abstractmethod
    def __eq__(self, other: "AbstractSet") -> bool:
        """
        Check if two sets are equal.

        :param other: Another AbstractSet to compare with.
        :return: True if the sets are equal, False otherwise.
        """
        pass

    @abstractmethod
    def add(self, object: Union[Point, "DyadicCube"]) -> None:
        """
        Add a Point or DyadicCube to the set.

        :param object: A Point or DyadicCube to add to the set.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """
        Get a string representation of the set.

        :return: A string representing the set.
        """
        pass

    @abstractmethod
    def get_cardinality(self) -> Union[int, float]:
        """
        Get the cardinality of the set, i.e., the number of elements in the set.

        :return: An integer representing the cardinality or float('inf') for infinite sets.
        """
        pass

    @abstractmethod
    def in_cube(self, cube: "DyadicCube") -> "AbstractSet":
        """
        Get the subset of the set that is contained in the given DyadicCube.

        :param cube: A DyadicCube to check.
        :return: A subset of the set that is contained in the cube.
        """
        pass

    @abstractmethod
    def where(self, point: Point) -> Union[AbstractSet, Point, "DyadicCube"]:
        """
        Gets the constituent of the set that contains the given point.

        :param point: A Point to check.
        :return: The constituent of the set that contains the point.
        """
        pass


class FullSpace(AbstractSet):
    """
    A class representing the full space, i.e., the entire domain of all possible Points.
    The cardinality is infinite.
    """

    def __init__(self, data=None):
        self.data = data

    def __eq__(self, other: "AbstractSet") -> bool:
        """
        Check if another set is also a FullSpace.

        :param other: Another AbstractSet to compare.
        :return: True if the other set is also a FullSpace, False otherwise.
        """
        return isinstance(other, FullSpace)

    def add(self, point: Point | "DyadicCube") -> None:
        """
        Does nothing because FullSpace contains all possible Points by definition.
        """
        pass

    def get_set(self) -> "AbstractSet":
        """
        Return self, as FullSpace represents all points.

        :return: self
        """
        return self

    def __contains__(self, item: Point | "DyadicCube") -> bool:
        """
        Check if a Point is in the FullSpace. Always returns True.

        :param point: A Point to check.
        :return: True
        """
        return True

    def get_cardinality(self) -> float:
        """
        Get the cardinality of the FullSpace, which is infinite.

        :return: float('inf')
        """
        return float("inf")

    def __repr__(self) -> str:
        """
        Get a string representation of the FullSpace.

        :return: "FullSpace()"
        """
        return "FullSpace()"

    def in_cube(self, cube: "DyadicCube") -> "DyadicCube":
        """
        Get the subset of the set that is contained in the given DyadicCube.

        :param cube: The DyadicCube to check.
        :return: The DyadicCube itself.
        """
        return cube

    def where(self, point: Point) -> "FullSpace":
        """
        Gets the constituent of the set that contains the given point.

        :param point:
        :return: FullSpace()
        """
        return self
