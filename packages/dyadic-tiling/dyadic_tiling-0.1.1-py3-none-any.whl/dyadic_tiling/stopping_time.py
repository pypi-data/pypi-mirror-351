from abc import ABC, abstractmethod

from dyadic_tiling.dyadic_cube_set import DyadicCube, DyadicCubeSet
from dyadic_tiling.point import Point
from dyadic_tiling.sets import AbstractSet, FullSpace


class AbstractStoppingTime(ABC):
    def __init__(self, omega: AbstractSet, *args, **kwargs):
        """
        This is an abstract base class for a stopping time.

        :param omega: An AbstractSet object.
        """
        self.omega = omega
        self._init_args = args
        self._init_kwargs = kwargs

    def get_omega(self) -> AbstractSet:
        """
        Get Omega.

        :return: A AbstractSet object.
        """
        return self.omega

    def __contains__(self, point: Point) -> bool:
        """
        Check if a Point is in Omega.

        :param point: A Point object.
        :return: True if the Point is in Omega, False otherwise.
        """
        return point in self.get_omega()

    def where(self, point: Point) -> Point | DyadicCube | FullSpace:
        """
        Get the constituent of Omega which contains the given point.

        :param point: A Point object.
        :return: A DyadicCube object.
        """
        return self.get_omega().where(point)

    def __call__(self, point: Point) -> int:
        """
        This method calls the derived class's implementation of _compute_stopping_time
        to get the stopping time for the given point.

        :param point: A Point object.
        :return: An integer value representing the stopping time for that point.
        """
        if point not in self:
            raise ValueError("The point is not in Omega.")
        return self._compute_stopping_time(point)

    def minimal_extension(self) -> "AbstractStoppingTime":
        """
        This method creates a stopping time which agrees with the current one on Omega,
        is defined on the whole space, and is minimal in the sense that it has the
        smallest number of additional tiles.

        :return: The minimally extended stopping time.
        """
        if isinstance(self.get_omega(), FullSpace):
            return self

        def minimal_extension_compute_stopping_time(point: Point) -> int:
            if point in self.get_omega():
                return self._compute_stopping_time(point)

            for k in range(point.get_bits_per_dim()):
                candidate_cube = point.get_containing_cube(k)
                subset = self.get_omega().in_cube(candidate_cube)

                if not subset:
                    break
                else:
                    object = subset.get_set()[0]
                    if isinstance(object, DyadicCube):
                        object = object.top_left_point()
                    if self(object) == k:
                        break

            return k

        new_instance = self.__class__(
            FullSpace(), *self._init_args, **self._init_kwargs
        )

        new_instance._compute_stopping_time = minimal_extension_compute_stopping_time

        return new_instance

    @abstractmethod
    def _compute_stopping_time(self, point: Point) -> int:
        """
        This abstract method should be implemented by the derived class to compute
        the stopping time for a given Point.

        :param point: A Point object.
        :return: An integer value representing the stopping time for that point.
        """
        pass

    def _test_stopping_time_is_consistent(self) -> bool:
        """
        Test whether the stopping time is consistent.

        :return: True if the stopping time is consistent, False otherwise.
        """

        if isinstance(self.get_omega(), FullSpace) or isinstance(
            self.get_omega(), DyadicCubeSet
        ):
            raise ValueError(
                "Test for consistent stopping time is not implemented for a stopping time defined on the "
                "FullSpace or a DyadicCubeSet."
            )

        for point in self.get_omega().get_set():
            stopping_time = self(point)
            dyadic_box = point.get_containing_cube(stopping_time)
            points_in_box = self.get_omega().in_cube(dyadic_box)

            for other_point in points_in_box.get_set():
                if self(other_point) != stopping_time:
                    return False

        return True


class DyadicCubeSetStoppingTime(AbstractStoppingTime):
    """
    A stopping time implementation based on a dyadic cube set.

    The stopping time for a point is defined as the level of the dyadic cube
    containing that point. When adding a new cube, any cubes contained within
    the new one are removed.
    """

    def __init__(self, omega: DyadicCubeSet = None):
        if omega is None:
            omega = DyadicCubeSet()
        super().__init__(omega)

    def _compute_stopping_time(self, point: Point) -> int:
        """
        Compute the stopping time for a given point.

        Parameters:
            point (Point): The point for which to compute the stopping time.

        Returns:
            int: The level of the cube containing the point.
        """
        return self.omega.where(point).get_level()

    def add(self, cube: DyadicCube) -> None:
        """
        Add a cube to the dyadic cube set. If the new cube contains other cubes,
        remove those in favor of the new cube.

        Parameters:
            cube (DyadicCube): The cube to add.
        """
        contained_cubes = self.omega.in_cube(cube)
        for contained_cube in contained_cubes.get_set():
            if contained_cube != cube:
                self.omega.remove(contained_cube)
        self.omega.add(cube)

    def check_if_cube_is_in_omega(self, cube: DyadicCube) -> bool:
        """
        Check if a tile is in omega.

        Parameters:
            tile (DyadicCube): The tile to check.

        Returns:
            bool: True if the tile is in omega, False otherwise.
        """
        return cube in self.omega
