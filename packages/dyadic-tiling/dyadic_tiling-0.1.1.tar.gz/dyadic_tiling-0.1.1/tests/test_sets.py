import pytest

from dyadic_tiling.dyadic_cube import DyadicCube
from dyadic_tiling.dyadic_cube_set import DyadicCubeSet
from dyadic_tiling.point import Point
from dyadic_tiling.point_set import PointSet
from dyadic_tiling.sets import FullSpace


def test_mortonpointset_initialization():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    omega_1 = PointSet([point_1, point_2])
    assert omega_1.get_set() == [point_2, point_1]
    omega_2 = PointSet((point_1, point_2))
    assert omega_2.get_set() == [point_2, point_1]
    omega_3 = PointSet([])
    omega_3.add(point_1)
    omega_3.add(point_2)
    assert omega_3.get_set() == [point_2, point_1]


def test_mortonpointset_add_remove_point():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    omega = PointSet([point_1])
    omega.add(point_2)
    assert omega.get_set() == [point_2, point_1]
    omega.remove(point_2)
    assert omega.get_set() == [point_1]


def test_mortonpointset_add_invalid_point():
    point_1 = Point([0.5, 0.75])
    omega = PointSet([point_1])
    with pytest.raises(ValueError):
        omega.add([0.25, 0.25])


def test_mortonpointset_initialization_with_invalid_points():
    with pytest.raises(ValueError):
        PointSet([Point([0.5, 0.75]), [0.25, 0.25]])


def test_mortonpointset_adding_invalid_morton_point():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    point_3 = Point([0.25])
    omega = PointSet([point_1, point_2])
    with pytest.raises(ValueError):
        omega.add(point_3)


def test_mortonpointset_repr():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    omega = PointSet([point_1, point_2])
    assert (
        repr(omega) == f"PointSet("
        f"morton_points=SortedList([{repr(point_2)}, {repr(point_1)}]))"
    )


def test_mortonpointset_in_cube():
    point_1 = Point([0.6, 0.7])
    point_2 = Point([0.2, 0.3])
    point_3 = Point([0.2, 0.7])
    point_4 = Point([0.6, 0.3])
    point_5 = Point([0.7, 0.7])
    point_6 = Point([0.2, 0.2])
    omega = PointSet([point_1, point_2, point_3, point_4, point_5, point_6])
    cube = DyadicCube(level=0, points=Point(0, 2))
    omega_in_cube = omega.in_cube(cube)
    assert (
        omega_in_cube.get_set()
        == PointSet([point_1, point_2, point_3, point_4, point_5, point_6]).get_set()
    )
    cube = DyadicCube(level=1, points=Point(0b00 << 104, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([point_2, point_6]).get_set()
    cube = DyadicCube(level=1, points=Point(0b01 << 104, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([point_3]).get_set()
    cube = DyadicCube(level=1, points=Point(0b10 << 104, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([point_4]).get_set()
    cube = DyadicCube(level=1, points=Point(0b11 << 104, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([point_1, point_5]).get_set()
    cube = DyadicCube(level=2, points=Point(0b0000 << 102, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([point_6]).get_set()
    cube = DyadicCube(level=2, points=Point(0b0100 << 102, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([point_3]).get_set()
    cube = DyadicCube(level=2, points=Point(0b0101 << 102, 2))
    omega_in_cube = omega.in_cube(cube)
    assert omega_in_cube.get_set() == PointSet([]).get_set()


def test_mortonpointset_cardinality():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    empty_set = PointSet([])
    assert empty_set.get_cardinality() == 0
    single_point_set = PointSet([point_1])
    assert single_point_set.get_cardinality() == 1
    multi_point_set = PointSet([point_1, point_2])
    assert multi_point_set.get_cardinality() == 2


def test_mortonpointset_equality():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    omega_1 = PointSet([point_1, point_2])
    omega_2 = PointSet([point_1, point_2])
    omega_3 = PointSet([point_1])

    assert omega_1 == omega_2
    assert omega_1 != omega_3


def test_mortonpointset_not_equal_to_fullspace():
    point_1 = Point([0.5, 0.75])
    omega_1 = PointSet([point_1])
    omega_2 = FullSpace()

    assert omega_1 != omega_2


def test_fullspace_initialization():
    omega = FullSpace()
    assert repr(omega) == "FullSpace()"


def test_fullspace_get_set():
    omega = FullSpace()
    assert omega.get_set() == omega


def test_fullspace_in_cube():
    omega = FullSpace()
    cube = DyadicCube(level=0, points=Point(0, 2))
    assert omega.in_cube(cube) == cube

    cube_1 = DyadicCube(level=1, points=Point(0b00 << 104, 2))
    assert omega.in_cube(cube_1) == cube_1

    cube_2 = DyadicCube(level=1, points=Point(0b01 << 104, 2))
    assert omega.in_cube(cube_2) == cube_2


def test_fullspace_where():
    omega = FullSpace()
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    assert omega.where(point_1) == omega
    assert omega.where(point_2) == omega


def test_fullspace_contains_any_point():
    omega = FullSpace()
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.25, 0.25])
    assert point_1 in omega
    assert point_2 in omega


def test_fullspace_len():
    omega = FullSpace()
    assert omega.get_cardinality() == float("inf")


def test_fullspace_add_point():
    omega = FullSpace()
    point_1 = Point([0.5, 0.75])
    omega.add(point_1)
    assert point_1 in omega


def test_fullspace_equality():
    omega_1 = FullSpace()
    omega_2 = FullSpace()

    assert omega_1 == omega_2


def test_dyadiccubeset_initialization():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube2 = DyadicCube(level=2, points=Point([0.25, 0.25]))
    omega = DyadicCubeSet([cube1, cube2])
    assert omega.get_set() == [cube2, cube1]

    with pytest.raises(ValueError):
        DyadicCubeSet([cube1, [0.25, 0.25]])


def test_len_dyadiccubeset():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube2 = DyadicCube(level=2, points=Point([0.25, 0.25]))
    omega = DyadicCubeSet([cube1, cube2])
    assert len(omega) == 2


def test_get_cube_returns_correct_cube():
    cube = DyadicCube(level=2, points=Point([0.5, 0.75]))
    omega = DyadicCubeSet([cube])
    assert omega.get_cube(cube) == cube
    cube2 = DyadicCube(level=3, points=Point([0.5, 0.75]))
    with pytest.raises(KeyError):
        omega.get_cube(cube2)


def test_dyadiccubeset_repr():
    cube = DyadicCube(level=2, points=Point([0.5, 0.75]))
    omega = DyadicCubeSet([cube])
    repr_str = repr(omega)
    assert isinstance(repr_str, str)
    assert repr_str == f"DyadicCubeSet(dyadic_cubes=SortedList([{repr(cube)}]))"


def test_dyadiccubeset_get_points_and_num_points():
    p1 = Point([0.5, 0.75])
    p2 = Point([0.5, 0.76])
    cube = DyadicCube(level=3, points=PointSet([p1, p2]))
    omega = DyadicCubeSet([cube])
    points = omega.get_points()
    assert p1 in points and p2 in points
    assert omega.num_points() == 2


def test_dyadiccubeset_add_remove_cube():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube2 = DyadicCube(level=2, points=Point([0.25, 0.25]))
    omega = DyadicCubeSet([cube1])
    omega.add(cube2)
    assert omega.get_set() == [cube2, cube1]
    omega.remove(cube2)
    assert omega.get_set() == [cube1]


def test_dyadiccubeset_contains_point():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    point1 = Point([0.5, 0.75])
    point2 = Point([0.3, 0.3])
    omega = DyadicCubeSet([cube1])
    assert point1 in omega
    assert point2 not in omega

    with pytest.raises(TypeError):
        0.25 in omega


def test_dyadiccubeset_in_cube():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube2 = DyadicCube(level=1, points=Point([0.25, 0.25]))
    omega = DyadicCubeSet([cube1, cube2])
    outer_cube = DyadicCube(level=0, points=Point([0.0, 0.0]))
    omega_in_cube = omega.in_cube(outer_cube)
    assert omega_in_cube.get_set() == [cube2, cube1]


def test_dyadiccubeset_where():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    point = Point([0.5, 0.75])
    omega = DyadicCubeSet([cube1])
    assert omega.where(point) == cube1


def test_dyadiccubeset_where_nested():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube2 = DyadicCube(level=3, points=Point([0.5, 0.75]))
    point = Point([0.5, 0.75])
    omega = DyadicCubeSet([cube1, cube2])
    assert omega.where(point) == cube2
    assert omega.where(point) != cube1


def test_dyadiccubeset_cardinality():
    omega = DyadicCubeSet([])
    assert omega.get_cardinality() == 0
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    omega.add(cube1)
    assert omega.get_cardinality() == float("inf")


def test_dyadiccubeset_equality():
    cube_1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube_2 = DyadicCube(level=2, points=Point([0.25, 0.25]))

    omega_1 = DyadicCubeSet([cube_1, cube_2])
    omega_2 = DyadicCubeSet([cube_1, cube_2])
    omega_3 = DyadicCubeSet([cube_1])

    assert omega_1 == omega_2
    assert omega_1 != omega_3

    assert omega_1 != FullSpace()


def test_dyadiccubeset_not_equal_to_mortonpointset():
    point_1 = Point([0.5, 0.75])
    cube_1 = DyadicCube(level=2, points=point_1)

    omega_1 = PointSet([point_1])
    omega_2 = DyadicCubeSet([cube_1])

    assert omega_1 != omega_2


def test_empty_sets():
    empty_morton_set = PointSet([])
    assert len(empty_morton_set) == 0
    assert not bool(empty_morton_set)

    empty_cube_set = DyadicCubeSet([])
    assert not bool(empty_cube_set)
    assert len(empty_cube_set.get_set()) == 0

    cube = DyadicCube(level=0, points=Point([0.0, 0.0]))
    assert empty_morton_set.in_cube(cube).get_cardinality() == 0
    assert len(empty_cube_set.in_cube(cube).get_set()) == 0


def test_pointset_merge_non_overlapping():
    # Create four points such that their natural ordering is point1 < point2 < point3 < point4.
    point1 = Point([0.1, 0.1])
    point2 = Point([0.2, 0.2])
    point3 = Point([0.3, 0.3])
    point4 = Point([0.4, 0.4])

    # Create two sets with non overlapping points.
    set1 = PointSet([point1, point3])
    set2 = PointSet([point2, point4])

    merged = set1.merge(set2)
    expected = PointSet([point1, point2, point3, point4])
    assert merged == expected


def test_pointset_merge_overlapping():
    # Create three points.
    point1 = Point([0.1, 0.1])
    point2 = Point([0.2, 0.2])
    point3 = Point([0.3, 0.3])

    # Create two sets with a common point.
    set1 = PointSet([point1, point2])
    set2 = PointSet([point2, point3])

    merged = set1.merge(set2)
    # The merged set should contain each point only once.
    expected = PointSet([point1, point2, point3])
    assert merged == expected


def test_pointset_merge_with_empty():
    point1 = Point([0.1, 0.1])
    set1 = PointSet([point1])
    empty_set = PointSet([])

    # Merging a non-empty set with an empty set (in either order) should return the non-empty set.
    merged1 = set1.merge(empty_set)
    merged2 = empty_set.merge(set1)
    assert merged1 == set1
    assert merged2 == set1


def test_pointset_merge_both_empty():
    empty_set1 = PointSet([])
    empty_set2 = PointSet([])

    merged = empty_set1.merge(empty_set2)
    expected = PointSet([])
    assert merged == expected


def test_pointset_merge_self():
    # Merging a set with itself should yield a set with no duplicate entries.
    point1 = Point([0.1, 0.1])
    point2 = Point([0.2, 0.2])
    set1 = PointSet([point1, point2])

    merged = set1.merge(set1)
    assert merged == set1


def test_pointset_merge_invalid_type():
    point1 = Point([0.1, 0.1])
    set1 = PointSet([point1])

    # Trying to merge with a non-PointSet should raise a TypeError.
    with pytest.raises(TypeError):
        set1.merge("not a PointSet")


def test_pointset_where_returns_correct_instance():
    # Create two distinct Point instances.
    point1 = Point([0.5, 0.75])
    point2 = Point([0.25, 0.25])
    ps = PointSet([point1, point2])
    stored_point1 = ps.get_set()[1]
    stored_point2 = ps.get_set()[0]

    result1 = ps.where(Point([0.5, 0.75]))
    result2 = ps.where(Point([0.25, 0.25]))

    assert result1 is stored_point1
    assert result2 is stored_point2


def test_pointset_where_not_found():
    point1 = Point([0.5, 0.75])
    ps = PointSet([point1])
    with pytest.raises(KeyError):
        ps.where(Point([0.1, 0.1]))


def test_dyadiccubeset_where_returns_correct_cube():
    # Create two DyadicCube instances.
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    cube2 = DyadicCube(level=2, points=Point([0.25, 0.25]))
    dcs = DyadicCubeSet([cube1, cube2])

    result1 = dcs.where(Point([0.5, 0.75]))
    result2 = dcs.where(Point([0.25, 0.25]))

    assert result1 == cube1
    assert result2 == cube2


def test_dyadiccubeset_where_not_found():
    cube1 = DyadicCube(level=2, points=Point([0.5, 0.75]))
    dcs = DyadicCubeSet([cube1])
    with pytest.raises(KeyError):
        dcs.where(Point([0.1, 0.1]))


def test_dyadiccubeset_where_varying_cube_sizes():
    cube_fine = DyadicCube(level=3, points=Point([0.5, 0.5]))
    cube_coarse = DyadicCube(level=2, points=Point([0.25, 0.25]))
    dcs = DyadicCubeSet([cube_fine, cube_coarse])

    point_inside_fine = Point([0.5, 0.5])
    assert dcs.where(point_inside_fine) == cube_fine

    point_inside_coarse = Point([0.3, 0.3])
    assert dcs.where(point_inside_coarse) == cube_coarse


def test_dyadiccubeset_where_on_edge():
    cube = DyadicCube(level=3, points=Point([0.5, 0.5]))
    point_on_edge = Point([0.625 - 10e-16, 0.625 - 10e-16])
    dcs = DyadicCubeSet([cube])
    # Expect the cube to be returned if the point is considered inside.
    assert dcs.where(point_on_edge) == cube
    point_outside = Point([0.625, 0.625])
    with pytest.raises(KeyError):
        dcs.where(point_outside)


def test_fullspace_always_contains_point():
    fs = FullSpace()
    for coords in ([0.1, 0.1], [0.5, 0.5], [0.9, 0.9]):
        p = Point(coords)
        assert p in fs
        fs.add(p)
