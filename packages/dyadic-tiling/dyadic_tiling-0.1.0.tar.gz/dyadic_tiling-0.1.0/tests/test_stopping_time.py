import random

import pytest

from dyadic_tiling.dyadic_cube_set import DyadicCube, DyadicCubeSet
from dyadic_tiling.point_set import Point, PointSet
from dyadic_tiling.sets import FullSpace
from dyadic_tiling.stopping_time import AbstractStoppingTime, DyadicCubeSetStoppingTime


class StoppingTimeTest(AbstractStoppingTime):
    def __init__(self, omega, error_bound):
        super().__init__(omega, error_bound)
        self.error_bound = error_bound

    def _compute_stopping_time(self, point):
        for k in range(point.get_bits_per_dim()):
            if point.get_containing_cube(k).get_lengths()[0] < self.error_bound:
                return k


@pytest.fixture
def point_1():
    return Point([0.6, 0.7])


@pytest.fixture
def point_2():
    return Point([0.2, 0.3])


@pytest.fixture
def omega(point_1):
    return PointSet([point_1])


@pytest.fixture
def stopping_time(omega):
    return StoppingTimeTest(omega, 0.1)


@pytest.fixture
def cube_level_2():
    """
    Create a DyadicCube at level 2.
    Here we assume that the cube constructed with a Point (say, (0,0))
    represents the dyadic cube with top-left corner (0,0) at level 2.
    """
    return DyadicCube(Point([0.0, 0.0]), level=2)


@pytest.fixture
def cube_level_1():
    """
    Create a DyadicCube at level 1.
    """
    return DyadicCube(Point([0.0, 0.0]), level=1)


@pytest.fixture
def dyadic_cube_stopping_time():
    """
    Create an instance of DyadicCubeSetStoppingTime with an initially empty
    DyadicCubeSet.
    """
    cube_set = DyadicCubeSet()
    return DyadicCubeSetStoppingTime(cube_set)


def test_init(point_1, omega, stopping_time):
    assert stopping_time.get_omega() == omega
    assert stopping_time.error_bound == 0.1


def test_check_morton_point_in_omega(point_1, point_2, omega, stopping_time):
    assert point_1 in stopping_time
    assert point_2 not in stopping_time


def test_add_morton_point_to_omega(point_1, point_2, stopping_time):
    stopping_time.get_omega().add(point_2)
    assert point_2 in stopping_time


def test_compute_stopping_time(point_1, stopping_time):
    assert stopping_time._compute_stopping_time(point_1) == 4


def test_call_with_valid_point(point_1, stopping_time):
    result = stopping_time(point_1)
    assert result == 4


def test_call_with_invalid_point(stopping_time, point_2):
    with pytest.raises(ValueError, match="The point is not in Omega."):
        stopping_time(point_2)


def test_minimal_extension_with_point_inside_omega(point_1, point_2, stopping_time):
    extended_stopping_time = stopping_time.minimal_extension()
    assert extended_stopping_time.get_omega() == FullSpace()
    assert extended_stopping_time(point_1) == stopping_time(point_1)
    with pytest.raises(ValueError, match="The point is not in Omega."):
        stopping_time(point_2)
    extended_stopping_time(point_2)


def test_minimal_extension_with_point_outside_omega(point_1, point_2, stopping_time):
    extended_stopping_time = stopping_time.minimal_extension()
    stopping_time.get_omega().add(point_2)
    assert extended_stopping_time.get_omega() == FullSpace()
    assert extended_stopping_time(point_2) == stopping_time(point_2)
    assert extended_stopping_time(point_2) == extended_stopping_time(point_1)


def test_stopping_time_consistency(stopping_time):
    for _ in range(100):
        point = Point([random.random(), random.random()])
        stopping_time.get_omega().add(point)
    assert len(stopping_time.get_omega()) == 101
    assert stopping_time._test_stopping_time_is_consistent() is True


def test_stopping_time_with_empty_omega():
    empty_omega = PointSet([])
    stopping_time = StoppingTimeTest(empty_omega, 0.1)
    with pytest.raises(ValueError, match="The point is not in Omega."):
        stopping_time(Point([0.5, 0.5]))


def test_varying_error_bounds(point_1, omega):
    stopping_time_small_bound = StoppingTimeTest(omega, 0.01)
    stopping_time_large_bound = StoppingTimeTest(omega, 0.5)

    assert stopping_time_small_bound(point_1) > stopping_time_large_bound(point_1)


def test_stopping_time_with_multiple_points(point_1, point_2, stopping_time):
    stopping_time.get_omega().add(point_2)

    assert stopping_time(point_1) == 4
    assert stopping_time(point_2) == stopping_time._compute_stopping_time(point_2)


def test_stopping_time_on_boundaries(stopping_time):
    point_boundary = Point([1.0, 1.0])
    stopping_time.get_omega().add(point_boundary)

    assert stopping_time(point_boundary) == stopping_time._compute_stopping_time(
        point_boundary
    )


def test_dyadic_cube_contains_point(cube_level_2):
    inside_point = Point([0.1, 0.1])
    assert inside_point in cube_level_2

    outside_point = Point([0.8, 0.8])
    assert outside_point not in cube_level_2


def test_dyadic_cube_stopping_time_membership(cube_level_2, dyadic_cube_stopping_time):
    dyadic_cube_stopping_time.add(cube_level_2)
    point_inside = Point([0.1, 0.1])
    assert point_inside in dyadic_cube_stopping_time.get_omega()
    assert dyadic_cube_stopping_time(point_inside) == cube_level_2.get_level()


def test_dyadic_cube_stopping_time_point_outside(
    cube_level_2, dyadic_cube_stopping_time
):
    dyadic_cube_stopping_time.add(cube_level_2)
    point_outside = Point([0.8, 0.8])
    with pytest.raises(ValueError, match="The point is not in Omega."):
        dyadic_cube_stopping_time(point_outside)


def test_dyadic_cube_stopping_time_add_removes_contained_cubes(
    cube_level_1, cube_level_2, dyadic_cube_stopping_time
):
    dyadic_cube_stopping_time.add(cube_level_2)
    assert cube_level_2 in dyadic_cube_stopping_time.get_omega()

    dyadic_cube_stopping_time.add(cube_level_1)
    assert cube_level_1 in dyadic_cube_stopping_time.get_omega()
    assert cube_level_2 not in dyadic_cube_stopping_time.get_omega()


def test_dyadic_cube_stopping_time_minimal_extension(
    cube_level_2, dyadic_cube_stopping_time
):
    dyadic_cube_stopping_time.add(cube_level_2)
    extended_stopping_time = dyadic_cube_stopping_time.minimal_extension()

    assert isinstance(extended_stopping_time.get_omega(), FullSpace)

    point_inside = Point([0.1, 0.1])
    assert extended_stopping_time(point_inside) == dyadic_cube_stopping_time(
        point_inside
    )

    point_outside = Point([0.8, 0.8])
    _ = extended_stopping_time(point_outside)


def test_dyadic_cube_stopping_time_consistency_method_raises(dyadic_cube_stopping_time):
    with pytest.raises(
        ValueError, match="Test for consistent stopping time is not implemented"
    ):
        dyadic_cube_stopping_time._test_stopping_time_is_consistent()
