from typing import List, Tuple, Union

from sortedcontainers import SortedList

from dyadic_tiling.point import Point
from dyadic_tiling.sets import AbstractSet


class PointSet(AbstractSet):
    """
    A class representing a set of Points, stored in a sorted list.
    """

    def __init__(self, morton_points: Union[List[Point], Tuple[Point, ...]]):
        """
        Initialize the PointSet with a list or tuple of Points.

        :param morton_points: A list or tuple of Points.
        :raises ValueError: If any element in the input is not a Point.
        """
        if not all(isinstance(point, Point) for point in morton_points):
            raise ValueError("All elements in the list must be Point objects.")
        self.set = SortedList(morton_points)

    def __eq__(self, other: "AbstractSet") -> bool:
        """
        Check if another AbstractSet is equal to this PointSet.

        :param other: Another AbstractSet to compare with.
        :return: True if the sets are equal, False otherwise.
        """
        if not isinstance(other, PointSet):
            return False
        return self.get_set() == other.get_set()

    def get_set(self) -> SortedList:
        """
        Get the sorted list of Points.

        :return: A SortedList containing Points.
        """
        return self.set

    def add(self, point: Point) -> None:
        """
        Add a Point to the PointSet.

        :param point: A Point to add to the set.
        """
        if not isinstance(point, Point):
            raise ValueError("Only Point objects can be added to the PointSet.")
        self.get_set().add(point)

    def remove(self, point: Point) -> None:
        """
        Remove a Point from the PointSet.

        :param point: A Point to remove from the set.
        """
        self.get_set().remove(point)

    def __contains__(self, point: Point) -> bool:
        """
        Check if the PointSet contains a specific Point.

        :param point: A Point to check for membership.
        :return: True if the set contains the point, False otherwise.
        """
        return point in self.get_set()

    def __repr__(self) -> str:
        """
        Get a string representation of the PointSet.

        :return: A string representation of the PointSet.
        """
        return f"PointSet(morton_points={self.get_set()})"

    def get_cardinality(self) -> int:
        """
        Get the cardinality (number of elements) of the PointSet.

        :return: An integer representing the cardinality of the set.
        """
        return self.__len__()

    def __len__(self) -> int:
        """
        Get the number of elements in the PointSet.

        :return: The number of Points in the set.
        """
        return len(self.get_set())

    def in_cube(self, cube: "DyadicCube") -> "PointSet":
        """
        Return a new PointSet containing only the Points that are inside the given DyadicCube.

        :param cube: A DyadicCube to check for inclusion.
        :return: A PointSet containing Points inside the DyadicCube.
        """
        left = cube.top_left_point()
        right = cube.bottom_right_point()
        points = self.get_set()
        left_idx = points.bisect_left(left)
        right_idx = points.bisect_right(right)
        return PointSet(points[left_idx:right_idx])

    def __bool__(self) -> bool:
        """
        Check if the PointSet is non-empty.

        :return: True if the set is non-empty, False otherwise.
        """
        return bool(self.set)

    def where(self, point: Point) -> Point:
        """
        Returns the actual instance of the given Point in the PointSet,
        if it exists. Otherwise, raises a KeyError.

        :param point: The Point to search for.
        :return: The actual instance of the Point stored in the PointSet.
        :raises KeyError: If the point is not found in the PointSet.
        """
        idx = self.get_set().bisect_left(point)
        if idx < len(self.get_set()) and self.get_set()[idx] == point:
            return self.get_set()[idx]
        raise KeyError(f"Point {point} not found in the PointSet.")

    def merge(self, other: "PointSet") -> "PointSet":
        """
        Efficiently merge two PointSets and return a new PointSet containing
        the union of points from both, without duplicates.

        The merging is done in O(n + m) time by leveraging the fact that both
        point sets are stored in sorted order.

        :param other: Another PointSet to merge with.
        :return: A new PointSet representing the union of the two point sets.
        :raises TypeError: If other is not a PointSet.
        """
        if not isinstance(other, PointSet):
            raise TypeError("Merge operation requires another PointSet.")

        a = self.get_set()
        b = other.get_set()
        i, j = 0, 0
        merged_points = []

        # Merge the two sorted lists while avoiding duplicates.
        while i < len(a) and j < len(b):
            if a[i] < b[j]:
                merged_points.append(a[i])
                i += 1
            elif a[i] > b[j]:
                merged_points.append(b[j])
                j += 1
            else:
                # If the points are equal, include only one copy.
                merged_points.append(a[i])
                i += 1
                j += 1

        # Append any remaining points from either list.
        if i < len(a):
            merged_points.extend(a[i:])
        if j < len(b):
            merged_points.extend(b[j:])

        return PointSet(merged_points)

    def __hash__(self):
        """
        Compute the hash of the PointSet.

        :return: The hash value of the PointSet.
        """
        return hash(tuple(self.get_set()))
