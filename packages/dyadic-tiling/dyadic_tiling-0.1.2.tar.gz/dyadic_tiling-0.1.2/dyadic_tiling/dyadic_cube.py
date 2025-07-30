from typing import Generator, List, Optional, Tuple, Union

from dyadic_tiling.point_set import Point, PointSet


class DyadicCube:
    """
    A class to represent a dyadic cube in [0,1]^d. A dyadic cube consists of a
    Morton Point and a level. The Morton Point is a point in [0,1]^d represented by a
    Morton code. The level is an integer that determines the size of the cube.

    The main methods implemented are:
    - Comparison operators: <, <=, ==, !=, >=, >.
    - Finding the common ancestor of two dyadic cubes.
    - Finding the intersection of two dyadic cubes.
    - Generating the children of a dyadic cube.
    """

    def __init__(
        self,
        points: Point | PointSet,
        level: int,
        data: Optional = None,
    ):
        """
        Initialise the DyadicCube object with a dimension, a level, and a Morton
        code.

        :param points: A Point or PointSet containing points in the cube.
        :param level: The level of the cube.
        """
        if isinstance(points, Point):
            points = PointSet([points])
        self.points = points
        self.level = level
        self.morton_string = None
        self.data = data
        self.coordinate_ranges = self.get_a_point().get_coordinate_ranges()

        self._check_consistency()

    def _check_consistency(self) -> None:
        """
        Ensure that all the points in PointSet lie within the DyadicCube.

        :raises ValueError: If any point in the PointSet is not in the DyadicCube.
        """

        tl = self.top_left_point()
        br = self.bottom_right_point()
        sorted_points = self.get_points().get_set()
        first_point = sorted_points[0]
        last_point = sorted_points[-1]

        if tl > first_point or last_point > br:
            raise ValueError("PointSet contains points outside the DyadicCube.")

    def get_level(self) -> int:
        """
        Get the level of the dyadic cube.

        :return: The level of the dyadic cube.
        """
        return self.level

    def get_lengths(self) -> list[float]:
        """
        Get the side lengths of the dyadic cube.

        :return: The side length of the dyadic cube.
        """
        return [
            2 ** (-self.get_level()) * (high - low)
            for low, high in self.coordinate_ranges
        ]

    def get_diameter(self) -> float:
        """
        Get the diameter of the dyadic cube.
        """
        return sum(l**2 for l in self.get_lengths()) ** 0.5

    def get_points(self) -> PointSet:
        """
        Get the Morton Points in the Cube.

        :return: The Points in the Cube
        """
        return self.points

    def add_point(self, point: Point):
        """
        Add Morton Point to the Cube.

        :param point: Point to be added
        """
        tl = self.top_left_point()
        br = self.bottom_right_point()
        if tl > point or br < point:
            raise ValueError("Point outside cube")
        self.points.add(point)

    def add_points(self, points: PointSet):
        """
        Add a PointSet to the Cube.

        :param points: Points to be added
        """
        tl = self.top_left_point()
        br = self.bottom_right_point()
        first_point = points.get_set()[0]
        last_point = points.get_set()[-1]

        if tl > first_point or last_point > br:
            raise ValueError("PointSet contains points outside the DyadicCube.")

        self.points = self.points.merge(points)

    def num_points(self) -> int:
        """
        Get the number of points in the DyadicCube.

        :return: The number of points in the DyadicCube.
        """
        return len(self.get_points())

    def get_a_point(self) -> Point:
        """
        Get a Morton Point in the Cube.

        :return: A Point in the Cube
        """
        return self.get_points().get_set()[0]

    def get_dim(self) -> int:
        """
        Get the dimension of the Morton Point.

        :return: The dimension of the Morton Point.
        """
        return self.get_a_point().get_dim()

    def get_morton_code(self) -> int:
        """
        Get the Morton code as an integer.

        :return: The Morton code as an integer.
        """
        return self.get_a_point().get_truncated_morton_code(self.get_level())

    def get_morton_string(self) -> str:
        """
        Get the Morton code as a string of binary.

        :return: The Morton code as a string of binary.
        """
        if not self.morton_string:
            self.morton_string = self.get_a_point().get_morton_string(self.get_level())
        return self.morton_string

    def get_data(self):
        """
        Get the data associated with the DyadicCube object.

        :return: The data associated with the DyadicCube object.
        """
        return self.data

    def get_coordinate_ranges(self) -> List[Tuple[float, float]]:
        """
        Get the coordinate ranges of the DyadicCube object.

        :return: The coordinate ranges of the DyadicCube object.
        """
        return self.coordinate_ranges

    def copy(self) -> "DyadicCube":
        """
        Create a copy of the DyadicCube object.

        :return: A copy of the DyadicCube object.
        """
        return DyadicCube(self.get_points(), self.get_level())

    def find_common_ancestor(self, other: "DyadicCube") -> "DyadicCube":
        """
        Find the common ancestor of two DyadicCube objects.

        :param other: Another DyadicCube object.
        :return: The common ancestor of the two DyadicCube objects.
        """
        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )

        min_level = min(self.get_level(), other.get_level())

        result_level = 0
        for i in range(min_level):
            if self.get_a_point().get_truncated_morton_code(
                i + 1
            ) != other.get_a_point().get_truncated_morton_code(i + 1):
                break
            result_level += 1

        new_points = self.get_points().merge(other.get_points())

        return DyadicCube(new_points, result_level)

    def find_intersection(self, other: "DyadicCube") -> Optional["DyadicCube"]:
        """
        Find the intersection of two DyadicCube objects.

        :param other: Another DyadicCube object.
        :return: The intersection of the two DyadicCube objects, or None if they don't
         intersect.
        """

        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )
        self_level = self.get_level()
        other_level = other.get_level()

        if self_level == other_level:
            if self == other:
                return self.copy()
            else:
                return None

        if self_level > other_level:
            shift = (self_level - other_level) * self.get_dim()
            if self.get_morton_code() >> shift == other.get_morton_code():
                return self.copy()
        else:
            shift = (other_level - self_level) * self.get_dim()
            if other.get_morton_code() >> shift == self.get_morton_code():
                return other.copy()
        return None

    def children(
        self, iterable: bool = False
    ) -> Union[List["DyadicCube"], Generator["DyadicCube", None, None]]:
        """
        Find the children of a DyadicCube object.

        :param iterable: If True, return an iterator; otherwise, return a list.
        :return: A list or an iterator of the children of the DyadicCube object.
        """
        if iterable:
            return self._children_generator()
        else:
            return list(self._children_generator())

    def _children_generator(self) -> Generator["DyadicCube", None, None]:
        """
        Generator to find the children of a DyadicCube object.
        """
        bits_per_dim = self.get_a_point().get_bits_per_dim()
        for i in range(1 << self.get_dim()):
            new_morton_code = i + (self.get_morton_code() << self.get_dim())
            shift = (bits_per_dim - self.get_level() - 1) * self.get_dim()
            child = DyadicCube(
                Point(new_morton_code << shift, self.get_dim()),
                self.get_level() + 1,
            )

            child_points = self.points.in_cube(child)

            if len(child_points) != 0:
                child.points = child_points

            yield child

    def top_left_point(self) -> Point:
        """
        Get the point corresponding to the top left corner of the DyadicCube object.

        :return: The top left of the DyadicCube object.
        """
        code = self.get_morton_code()
        coordinate_ranges = self.get_a_point().get_coordinate_ranges()
        shift = self.get_dim() * (
            self.get_a_point().get_bits_per_dim() - self.get_level()
        )
        return Point(code << shift, self.get_dim(), coordinate_ranges)

    def middle_point(self) -> Point:
        """
        Get the point corresponding to the middle of the DyadicCube object.

        :return: The middle of the DyadicCube object.
        """
        code = self.get_morton_code()
        coordinate_ranges = self.get_a_point().get_coordinate_ranges()
        shift = self.get_dim() * (
            self.get_a_point().get_bits_per_dim() - self.get_level()
        )
        mask = ((1 << self.get_dim()) - 1) << (shift - self.get_dim())
        return Point(code << shift | mask, self.get_dim(), coordinate_ranges)

    def bottom_right_point(self) -> Point:
        """
        Get the point corresponding to the bottom right corner of the DyadicCube object.

        :return: The bottom right of the DyadicCube object.
        """
        code = self.get_morton_code()
        coordinate_ranges = self.get_a_point().get_coordinate_ranges()
        shift = self.get_dim() * (
            self.get_a_point().get_bits_per_dim() - self.get_level()
        )
        mask = (1 << shift) - 1
        return Point((code << shift) | mask, self.get_dim(), coordinate_ranges)

    def __eq__(self, other: "DyadicCube") -> bool:
        """
        Check if two DyadicCube objects are equal.

        :param other: Another DyadicCube object.
        :return: True if the two DyadicCube objects are equal; otherwise, False.
        """
        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )
        return (
            self.top_left_point() == other.top_left_point()
            and self.level == other.level
        )

    def __lt__(self, other: "DyadicCube") -> bool:
        """
        Check if one DyadicCube object is less than another.

        :param other: Another DyadicCube object.
        :return: True if the DyadicCube object is less than the other, False otherwise.
        """
        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )
        return self.top_left_point() < other.top_left_point() or (
            self.top_left_point() == other.top_left_point() and self.level < other.level
        )

    def __le__(self, other: "DyadicCube") -> bool:
        """
        Check if one DyadicCube object is less than or equal to another.

        :param other: Another DyadicCube object.
        :return: True if the DyadicCube object is less than or equal to the other,
                 False otherwise.
        """
        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other: "DyadicCube") -> bool:
        """
        Check if one DyadicCube object is greater than another.

        :param other: Another DyadicCube object.
        :return: True if the DyadicCube object is greater than the other, False otherwise.
        """
        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )
        return self.top_left_point() > other.top_left_point() or (
            self.top_left_point() == other.top_left_point() and self.level > other.level
        )

    def __ge__(self, other: "DyadicCube") -> bool:
        """
        Check if one DyadicCube object is greater than or equal to another.

        :param other: Another DyadicCube object.
        :return: True if the DyadicCube object is greater than or equal to the other,
                 False otherwise.
        """
        self.get_a_point().raise_error_if_morton_codes_not_in_same_dim(
            other.get_a_point()
        )
        return self.__eq__(other) or self.__gt__(other)

    def __ne__(self, other):
        """
        Check if two DyadicCube objects are not equal.

        :param other: Another DyadicCube object.
        :return: True if the two DyadicCube objects are not equal; otherwise, False.
        """
        return (
            self.top_left_point() != other.top_left_point() or self.level != other.level
        )

    def __contains__(self, point: Point) -> bool:
        """
        Check if a point is contained in a DyadicCube object.

        :param point: A Point object.
        :return: True if the point is contained in the DyadicCube object;
                 otherwise, False.
        """
        return point.compare_level_k(self.get_a_point(), "==", self.get_level())

    def __repr__(self) -> str:
        """
        Representation of the DyadicCube object.

        :return: A string representation of the DyadicCube object.
        """
        return (
            f"DyadicCube(dim={self.get_dim()}, level={self.get_level()}, "
            f"morton_code={self.get_morton_string()})"
        )

    def __hash__(self):
        """
        Hash the DyadicCube object.

        :return: The hash value of the DyadicCube object.
        """
        return hash((self.level, hash(self.get_points())))
