from typing import List, Tuple, Union

from sortedcontainers import SortedList

from dyadic_tiling.dyadic_cube import DyadicCube
from dyadic_tiling.point_set import Point, PointSet
from dyadic_tiling.sets import AbstractSet


class DyadicCubeSet(AbstractSet):
    """
    A class representing a set of DyadicCubes, stored in a sorted list.
    The cubes are assumed to be ordered by the Morton code of their
    top left point, followed by their level.
    """

    def __init__(
        self, dyadic_cubes: Union[List[DyadicCube], Tuple[DyadicCube, ...]] = ()
    ):
        """
        Initialize the DyadicCubeSet with a list or tuple of DyadicCubes.

        :param dyadic_cubes: A list or tuple of DyadicCubes.
        :raises ValueError: If any element in the input is not a DyadicCube.
        """
        if not all(isinstance(cube, DyadicCube) for cube in dyadic_cubes):
            raise ValueError("All elements in the list must be DyadicCube objects.")
        self.set = SortedList(dyadic_cubes)

    def __eq__(self, other: "AbstractSet") -> bool:
        """
        Check if another AbstractSet is equal to this DyadicCubeSet.
        """
        if not isinstance(other, DyadicCubeSet):
            return False
        return self.get_set() == other.get_set()

    def get_set(self) -> SortedList:
        """
        Get the underlying SortedList of DyadicCubes.
        """
        return self.set

    def add(self, cube: DyadicCube) -> None:
        """
        Add a DyadicCube to the set.
        """
        self.get_set().add(cube)

    def remove(self, cube: DyadicCube) -> None:
        """
        Remove a DyadicCube from the set.
        """
        self.get_set().remove(cube)

    def __len__(self):
        return len(self.get_set())

    def __contains__(self, item: Union[Point, DyadicCube]) -> bool:
        """
        Check whether the DyadicCubeSet contains a given Point or DyadicCube.
        For a Point, this method calls the `where` method and returns True if
        the point is contained in one of the cubes.
        For a DyadicCube, it uses binary search on the sorted list to check for
        an exact match.
        """
        if isinstance(item, Point):
            try:
                self.where(item)
                return True
            except KeyError:
                return False
        elif isinstance(item, DyadicCube):
            idx = self.get_set().bisect_left(item)
            if idx < len(self.get_set()) and self.get_set()[idx] == item:
                return True
            return False
        else:
            raise TypeError(
                f"Item must be of type Point or DyadicCube, not {type(item)}."
            )

    def get_cube(self, cube: DyadicCube) -> DyadicCube:
        """
        Get the DyadicCube in the set that is equal to the given cube.
        Uses binary search for efficient lookup.
        """
        idx = self.get_set().bisect_left(cube)  # Find insertion index
        if idx < len(self.get_set()) and self.get_set()[idx] == cube:
            return self.get_set()[idx]  # Found exact match
        raise KeyError(f"DyadicCube {cube} not found in the set.")

    def __repr__(self) -> str:
        """
        String representation of the DyadicCubeSet.
        """
        return f"DyadicCubeSet(dyadic_cubes={self.get_set()})"

    def get_cardinality(self) -> float:
        """
        Get the cardinality of the DyadicCubeSet.
        Returns 0 if empty and infinity otherwise.
        """
        if not self.get_set():
            return 0
        return float("inf")

    def in_cube(self, cube: DyadicCube) -> "DyadicCubeSet":
        """
        Return a new DyadicCubeSet containing only the DyadicCubes that
        are inside the given DyadicCube. This is done using binary search
        on the sorted list.

        :param cube: A DyadicCube to check for inclusion.
        :return: A DyadicCubeSet containing cubes inside the given cube.
        """
        cubes = self.get_set()
        if cubes:
            coordinate_ranges = cubes[0].get_coordinate_ranges()
        else:
            coordinate_ranges = None
        left_idx = cubes.bisect_left(cube)
        br = cube.bottom_right_point()
        max_morton = 2 ** (cube.get_dim() * cube.get_a_point().get_bits_per_dim()) - 1
        if br.get_morton_code() == max_morton:
            right_idx = len(cubes)
        else:
            # Create a dummy cube starting just after the bottom-right point.
            dummy = DyadicCube(
                Point(br.get_morton_code() + 1, cube.get_dim(), coordinate_ranges),
                cube.get_level(),
            )
            right_idx = cubes.bisect_left(dummy)
        return DyadicCubeSet(cubes[left_idx:right_idx])

    def where(self, point: Point) -> DyadicCube:
        """
        Return the smallest DyadicCube that contains the given Point.

        This method uses binary search on the sorted list of cubes to find
        the candidate cube. It creates a dummy cube using the point (with an
        assumed level of 0) to locate the insertion position. If the candidate
        cube (immediately preceding the insertion point) indeed contains the
        point, it is returned. Otherwise, a KeyError is raised.

        :param point: The Point to search for.
        :return: The DyadicCube containing the point.
        :raises KeyError: If no cube in the set contains the point.
        """
        cubes = self.get_set()
        dummy_cube = DyadicCube(point, point.get_bits_per_dim())
        idx = cubes.bisect_right(dummy_cube) - 1
        if idx >= 0:
            candidate = cubes[idx]
            if point in candidate:
                return candidate
        raise KeyError(
            f"No DyadicCube in the DyadicCubeSet contains the point {point}."
        )

    def __bool__(self) -> bool:
        """
        Check if the DyadicCubeSet is non-empty.
        """
        return bool(self.get_set())

    def get_points(self) -> PointSet:
        """
        Get the set of points contained in the DyadicCubeSet.
        """
        points = PointSet([])
        for cube in self.get_set():
            points = points.merge(other=cube.get_points())
        return points

    def num_points(self) -> int:
        """
        Get the number of points in the DyadicCubeSet.
        """
        return sum(cube.num_points() for cube in self.get_set())
