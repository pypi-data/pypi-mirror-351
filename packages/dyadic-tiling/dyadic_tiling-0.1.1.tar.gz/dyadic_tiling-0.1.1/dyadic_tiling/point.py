import copy
import operator
from typing import List, Optional, Tuple, Union


class Point:
    def __init__(
        self,
        point: Union[List[float], Tuple[float, ...], int],
        dim: Optional[int] = None,
        coordinate_ranges: Optional[List[Tuple[float, float]]] = None,
        data: Optional = None,
    ):
        """
        Initialize a Point object.

        :param point: A list or tuple representing coordinates in any coordinate space,
                      or an integer representing a Morton code.
        :param coordinate_ranges: Optional coordinate ranges (bounds) for each dimension.
                                  Each element is a tuple (min_val, max_val) for that dimension.
                                  If None, defaults to (0.0, 1.0) for all dimensions.
        :param dim: The dimension of the point. Required if point is a Morton code.
        """
        # Set the number of bits per dimension
        self.bits_per_dim = 53

        if isinstance(point, int):
            # point is a Morton code
            if dim is None:
                raise ValueError(
                    "Must provide dimension when initializing from a Morton code."
                )
            if dim < 1:
                raise ValueError("Dimension must be positive.")
            self.morton_code = point
            self.dim = dim
            self.coordinates = None  # Will compute lazily
        elif isinstance(point, (list, tuple)):
            # point is coordinates
            self.coordinates = point
            self.dim = len(point)
            self.morton_code = None  # Will compute lazily
        else:
            raise TypeError(
                "Point must be an int (Morton code) or a list/tuple of coordinates."
            )

        # Set coordinate ranges
        self.coordinate_ranges = (
            coordinate_ranges
            if coordinate_ranges is not None
            else [(0.0, 1.0)] * self.dim
        )
        if len(self.coordinate_ranges) != self.dim:
            raise ValueError("Coordinate ranges must match the dimension of the point.")

        self.data = data

    def update_morton_code(self):
        """
        Compute the Morton code for the point based on current coordinate ranges.
        Raises a ValueError if any coordinate is outside its specified range.
        """
        if self.coordinates is None:
            raise ValueError("Coordinates are not set; cannot compute Morton code.")

        # Apply linear scaling to map the point to [0,1]^d
        scaled_coords = []
        for idx, (coord, (min_val, max_val)) in enumerate(
            zip(self.coordinates, self.coordinate_ranges)
        ):
            if max_val == min_val:
                raise ValueError(
                    f"Coordinate range max_val must not be equal to min_val for dimension {idx}."
                )
            if not (min_val <= coord <= max_val):
                raise ValueError(
                    f"Coordinate {coord} at index {idx} is outside of its range [{min_val}, {max_val}]."
                )
            scaled_coord = (coord - min_val) / (max_val - min_val)
            scaled_coords.append(scaled_coord)

        # Now compute the Morton code from the scaled coordinates
        from dyadic_tiling.morton_encoding import morton_key_from_continuous

        self.morton_code = morton_key_from_continuous(scaled_coords)

    def update_coordinates(self):
        """
        Compute the coordinates from the Morton code and coordinate ranges.
        """
        if self.morton_code is None:
            raise ValueError("Morton code is not set; cannot compute coordinates.")

        from dyadic_tiling.morton_encoding import continuous_from_morton_key

        # Get scaled coordinates in [0,1]^d
        scaled_coords = continuous_from_morton_key(self.morton_code, self.dim)

        # Map scaled coordinates back to original coordinate ranges
        coordinates = []
        for idx, (scaled_coord, (min_val, max_val)) in enumerate(
            zip(scaled_coords, self.coordinate_ranges)
        ):
            coord = scaled_coord * (max_val - min_val) + min_val
            coordinates.append(coord)

        self.coordinates = coordinates

    def set_coordinate_ranges(self, coordinate_ranges: List[Tuple[float, float]]):
        """
        Set new coordinate ranges and invalidate the Morton code.

        :param coordinate_ranges: A list of tuples representing the new coordinate ranges.
        """
        if self.coordinates is None:
            self.update_coordinates()
        if len(coordinate_ranges) != self.dim:
            raise ValueError("Coordinate ranges must match the dimension of the point.")
        self.coordinate_ranges = coordinate_ranges
        # Invalidate the Morton code since the scaling has changed
        self.morton_code = None

    def get_coordinate_ranges(self) -> List[Tuple[float, float]]:
        """
        Get the coordinate ranges of the point.

        :return: A list of tuples representing the coordinate ranges.
        """
        return self.coordinate_ranges

    def set_coordinates(self, new_coordinates: Union[List[float], Tuple[float, ...]]):
        """
        Update the point's coordinates and invalidate the Morton code.

        :param new_coordinates: A list or tuple representing the new coordinates.
        """
        if len(new_coordinates) != self.dim:
            raise ValueError("New coordinates must match the dimension of the point.")
        self.coordinates = new_coordinates
        # Invalidate the Morton code since the coordinates have changed
        self.morton_code = None

    def get_morton_code(self) -> int:
        """
        Get the Morton code of the point.

        :return: The Morton code as an integer.
        """
        if self.morton_code is None:
            self.update_morton_code()
        return self.morton_code

    def get_truncated_morton_code(self, level: Optional[int] = None) -> int:
        """
        Get the Morton code truncated to a certain level.

        :param level: The level to truncate the Morton code to.
        :return: The truncated Morton code.
        """
        code = self.get_morton_code()
        if level is None:
            return code
        if not (0 <= level <= self.bits_per_dim):
            raise ValueError(f"Level must be between 0 and {self.bits_per_dim}")
        shift = (self.bits_per_dim - level) * self.dim
        return code >> shift

    def get_coords(self) -> Union[List[float], Tuple[float, ...]]:
        """
        Get the original coordinates of the point.

        :return: The coordinates as a list or tuple.
        """
        if self.coordinates is None:
            self.update_coordinates()
        return self.coordinates

    def get_dim(self) -> int:
        """
        Get the dimension of the point.

        :return: The dimension of the point.
        """
        return self.dim

    def get_bits_per_dim(self) -> int:
        """
        Get the number of bits per dimension.

        :return: The number of bits per dimension.
        """
        return self.bits_per_dim

    def get_morton_string(self, level: Optional[int] = None) -> str:
        """
        Get the Morton code as a binary string.

        :param level: The level to which the Morton code is truncated.
        :return: The Morton code as a binary string.
        """
        code = self.get_truncated_morton_code(level)
        total_bits = (level if level is not None else self.bits_per_dim) * self.dim
        return bin(code)[2:].zfill(total_bits)

    def check_two_morton_codes_have_same_dim(self, other: "Point") -> bool:
        """
        Alias for check_same_dim_and_ranges for backward compatibility.
        """
        return self.check_same_dim_and_ranges(other)

    def raise_error_if_morton_codes_not_in_same_dim(self, other: "Point") -> None:
        """
        Alias for raise_error_if_not_same_dim_and_ranges for backward compatibility.
        """
        self.raise_error_if_not_same_dim_and_ranges(other)

    def check_same_dim_and_ranges(self, other: "Point") -> bool:
        """
        Check if two Point objects have the same dimension and coordinate ranges.

        :param other: Another Point object.
        :return: True if dimensions and coordinate ranges are the same, False otherwise.
        """
        if self.get_dim() != other.get_dim():
            return False
        return self.coordinate_ranges == other.coordinate_ranges

    def raise_error_if_not_same_dim_and_ranges(self, other: "Point") -> None:
        """
        Raise an error if two Point objects do not have the same dimension and coordinate ranges.

        :param other: Another Point object.
        """
        if not self.check_same_dim_and_ranges(other):
            raise ValueError(
                "Points must have the same dimension and coordinate ranges to be compared."
            )

    def compare_level_k(self, other: "Point", op: str, k: int) -> bool:
        """
        Compare the Points at level k using the given operator.

        :param other: Another Point object.
        :param k: The level at which to compare the Points.
        :param op: A comparison operator as a string ('>', '<', '>=', '<=', '==', '!=').
        :return: The result of the comparison.
        """
        operators = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
        }

        if op not in operators:
            raise ValueError(f"{op} must be one of '>', '<', '>=', '<=', '==', '!='")

        self.raise_error_if_not_same_dim_and_ranges(other)

        self_code = self.get_truncated_morton_code(k)
        other_code = other.get_truncated_morton_code(k)

        return operators[op](self_code, other_code)

    def copy(self) -> "Point":
        """
        Create a copy of the Point object.

        :return: A copy of the Point object.
        """
        return Point(
            point=copy.deepcopy(self.coordinates)
            if self.coordinates is not None
            else self.morton_code,
            coordinate_ranges=copy.deepcopy(self.coordinate_ranges),
            dim=self.dim,
        )

    def get_containing_cube(self, level: int):
        """
        Get the dyadic cube containing the point at the given level.

        :param level: The level of the dyadic cube.
        :return: A DyadicCube object containing the point.
        """
        if level < 0:
            raise ValueError("The level must be non-negative.")

        if level > self.bits_per_dim:
            raise ValueError(
                f"This point only has {self.bits_per_dim} bits per dimension, "
                f"so the maximum level of dyadic cube is {self.bits_per_dim}."
            )

        from dyadic_tiling.dyadic_cube import DyadicCube

        return DyadicCube(self.copy(), level)

    def __eq__(self, other: "Point") -> bool:
        """
        Check if two Point objects are equal based on their Morton codes.

        :param other: Another Point object.
        :return: True if the Morton codes are equal, False otherwise.
        """
        if not isinstance(other, Point):
            raise ValueError
        self.raise_error_if_not_same_dim_and_ranges(other)
        return self.get_morton_code() == other.get_morton_code()

    def __lt__(self, other: "Point") -> bool:
        """
        Check if this Point's Morton code is less than another's.

        :param other: Another Point object.
        :return: True if this Morton code is less than the other's, False otherwise.
        """
        if not isinstance(other, Point):
            raise ValueError
        self.raise_error_if_not_same_dim_and_ranges(other)
        return self.get_morton_code() < other.get_morton_code()

    def __le__(self, other: "Point") -> bool:
        """
        Check if this Point's Morton code is less than or equal to another's.

        :param other: Another Point object.
        :return: True if this Morton code is less than or equal to the other's, False otherwise.
        """
        if not isinstance(other, Point):
            raise ValueError
        self.raise_error_if_not_same_dim_and_ranges(other)
        return self.get_morton_code() <= other.get_morton_code()

    def __gt__(self, other: "Point") -> bool:
        """
        Check if this Point's Morton code is greater than another's.

        :param other: Another Point object.
        :return: True if this Morton code is greater than the other's, False otherwise.
        """
        if not isinstance(other, Point):
            raise ValueError
        self.raise_error_if_not_same_dim_and_ranges(other)
        return self.get_morton_code() > other.get_morton_code()

    def __ge__(self, other: "Point") -> bool:
        """
        Check if this Point's Morton code is greater than or equal to another's.

        :param other: Another Point object.
        :return: True if this Morton code is greater than or equal to the other's, False otherwise.
        """
        if not isinstance(other, Point):
            raise ValueError
        self.raise_error_if_not_same_dim_and_ranges(other)
        return self.get_morton_code() >= other.get_morton_code()

    def __ne__(self, other: "Point") -> bool:
        """
        Check if two Point objects are not equal based on their Morton codes.

        :param other: Another Point object.
        :return: True if the Morton codes are not equal, False otherwise.
        """
        if not isinstance(other, Point):
            raise ValueError
        self.raise_error_if_not_same_dim_and_ranges(other)
        return self.get_morton_code() != other.get_morton_code()

    def __repr__(self) -> str:
        """
        Representation of the Point object.
        """
        return (
            f"Point(point={self.get_coords() if self.coordinates is not None else 'None'}, morton_code="
            f"{self.morton_code}, dim={self.dim})"
        )

    def __hash__(self) -> int:
        """
        Hash function for the Point to make it hashable.

        :return: The hash of the Point object.
        """
        coordinate_ranges_hashable = tuple(self.coordinate_ranges)
        return hash((self.get_morton_code(), self.dim, coordinate_ranges_hashable))
