import pytest

from dyadic_tiling.dyadic_cube import DyadicCube
from dyadic_tiling.point_set import Point, PointSet


def test_initialization():
    cube = DyadicCube(level=3, points=Point(5 << 100, 2))
    assert cube.get_dim() == 2
    assert cube.get_level() == 3
    assert cube.get_morton_code() == 5
    assert cube.get_lengths() == [2**-3, 2**-3]
    assert cube.get_morton_string() == "000101"


def test_equality():
    cube1 = DyadicCube(level=3, points=Point(5 << 100, 2))
    cube2 = DyadicCube(level=3, points=Point(5 << 100, 2))
    cube3 = DyadicCube(level=3, points=Point(6 << 100, 2))
    assert cube1 == cube2
    assert cube1 != cube3


def test_copy():
    cube = DyadicCube(level=3, points=Point(5 << 100, 2))
    cube_copy = cube.copy()
    assert cube == cube_copy
    assert cube is not cube_copy


def test_find_common_ancestor():
    point1 = Point(0b000101 << 100, 2)
    point2 = Point(0b000110 << 100, 2)
    point3 = Point(0b00010100 << 98, 2)
    point4 = Point(0b0001 << 102, 2)
    point5 = Point(0b1000010010 << 96, 2)

    cube1 = DyadicCube(level=3, points=point1)
    cube2 = DyadicCube(level=3, points=point2)
    cube3 = DyadicCube(level=4, points=point3)
    cube4 = DyadicCube(level=2, points=point4)
    cube5 = DyadicCube(level=5, points=point5)

    # Find the common ancestor and check its level and points
    common_ancestor = cube1.find_common_ancestor(cube2)
    assert common_ancestor == cube4
    assert common_ancestor.get_level() == cube4.get_level()
    assert common_ancestor.get_points() == cube1.get_points().merge(cube2.get_points())

    common_ancestor = cube1.find_common_ancestor(cube3)
    assert common_ancestor == cube1
    assert common_ancestor.get_level() == cube1.get_level()
    assert common_ancestor.get_points() == cube1.get_points().merge(cube3.get_points())

    common_ancestor = cube1.find_common_ancestor(cube4)
    assert common_ancestor == cube4
    assert common_ancestor.get_level() == cube4.get_level()
    assert common_ancestor.get_points() == cube1.get_points().merge(cube4.get_points())

    common_ancestor = cube1.find_common_ancestor(cube5)
    root_cube = DyadicCube(level=0, points=Point(0b0, 2))
    assert common_ancestor == root_cube
    assert common_ancestor.get_level() == root_cube.get_level()
    assert common_ancestor.get_points() == cube1.get_points().merge(cube5.get_points())


def test_find_intersection():
    cube1 = DyadicCube(level=3, points=Point(0b000101 << 100, 2))
    cube2 = DyadicCube(level=3, points=Point(0b000101 << 100, 2))
    cube3 = DyadicCube(level=3, points=Point(0b000110 << 100, 2))
    cube4 = DyadicCube(level=2, points=Point(0b0001 << 102, 2))
    assert cube1.find_intersection(cube2) == cube1
    assert cube1.find_intersection(cube2) is not cube1
    assert cube1.find_intersection(cube3) is None
    assert cube1.find_intersection(cube4) == cube4
    assert cube1.find_intersection(cube4) is not cube4
    assert cube4.find_intersection(cube1) == cube4
    assert cube3.find_intersection(cube4) == cube4


def test_children():
    cube = DyadicCube(level=1, points=Point(0b01 << 104, 2))
    children = cube.children(iterable=False)
    children_gen = cube.children(iterable=True)
    assert list(children_gen) == children
    expected_children = [
        DyadicCube(level=2, points=Point(0b0100 << 102, 2)),
        DyadicCube(level=2, points=Point(0b0101 << 102, 2)),
        DyadicCube(level=2, points=Point(0b0110 << 102, 2)),
        DyadicCube(level=2, points=Point(0b0111 << 102, 2)),
    ]
    assert children == expected_children
    cube = DyadicCube(level=1, points=Point(0b111 << 156, 3))
    children = cube.children()
    expected_children = [
        DyadicCube(level=2, points=Point(0b111000 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111001 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111010 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111011 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111100 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111101 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111110 << 153, 3)),
        DyadicCube(level=2, points=Point(0b111111 << 153, 3)),
    ]
    assert children == expected_children


def test_top_left_point():
    cube = DyadicCube(level=0, points=Point(0b100101 << 100, 2))
    top_left = cube.top_left_point()
    expected_top_left = Point(0, 2)
    assert top_left == expected_top_left
    cube = DyadicCube(level=1, points=Point(0b100101 << 100, 2))
    top_left = cube.top_left_point()
    expected_top_left = Point(0b10 << 104, 2)
    assert top_left == expected_top_left
    cube = DyadicCube(level=2, points=Point(0b100101 << 100, 2))
    top_left = cube.top_left_point()
    expected_top_left = Point(0b1001 << 102, 2)
    assert top_left == expected_top_left
    cube = DyadicCube(level=3, points=Point(0b100101 << 100, 2))
    top_left = cube.top_left_point()
    expected_top_left = Point(0b100101 << 100, 2)
    assert top_left == expected_top_left


def test_bottom_right_point():
    cube = DyadicCube(level=0, points=Point(0b100101 << 100, 2))
    bottom_right = cube.bottom_right_point()
    expected_bottom_right = Point(2**106 - 1, 2)
    assert bottom_right == expected_bottom_right
    cube = DyadicCube(level=1, points=Point(0b100101 << 100, 2))
    bottom_right = cube.bottom_right_point()
    expected_bottom_right = Point(0b10 << 104 | 2**104 - 1, 2)
    assert bottom_right == expected_bottom_right
    cube = DyadicCube(level=2, points=Point(0b100101 << 100, 2))
    bottom_right = cube.bottom_right_point()
    expected_bottom_right = Point(0b1001 << 102 | 2**102 - 1, 2)
    assert bottom_right == expected_bottom_right
    cube = DyadicCube(level=3, points=Point(0b100101 << 100, 2))
    bottom_right = cube.bottom_right_point()
    expected_bottom_right = Point(0b100101 << 100 | 2**100 - 1, 2)
    assert bottom_right == expected_bottom_right


def test_level_zero_cube():
    point = Point(0, 2)
    cube = DyadicCube(level=0, points=point)
    assert cube.get_lengths() == [1, 1]
    assert cube.get_diameter() == 2**0.5
    assert cube.top_left_point() == Point(0, 2)
    assert cube.bottom_right_point() == Point((1 << 106) - 1, 2)


def test_high_level_cube():
    point = Point(0b1, 2)
    cube = DyadicCube(level=53, points=point)
    assert cube.get_lengths() == [2**-53, 2**-53]
    assert cube.top_left_point() == Point(0b1 << 0, 2)
    assert cube.bottom_right_point() == Point((0b1 << 0) | (1 << 0) - 1, 2)


def test_no_intersection():
    cube1 = DyadicCube(level=3, points=Point(0b000101 << 100, 2))
    cube2 = DyadicCube(level=3, points=Point(0b100000 << 100, 2))
    assert cube1.find_intersection(cube2) is None


def test_children_high_dimension():
    point = Point(0b111 << 52 * 3, 3)
    cube = DyadicCube(level=1, points=point)
    children = cube.children()
    assert len(children) == 8  # 2^3 children for a 3D cube
    expected_children_codes = [
        0b111000,
        0b111001,
        0b111010,
        0b111011,
        0b111100,
        0b111101,
        0b111110,
        0b111111,
    ]
    for child, expected_code in zip(children, expected_children_codes):
        assert child.get_morton_code() == expected_code


def test_middle_point():
    cube = DyadicCube(level=2, points=Point(0b1010 << 102, 2))
    middle = cube.middle_point()
    expected_middle = Point((0b1010 << 102) | 0b11 << 100, 2)
    assert middle == expected_middle


def test_contains_method():
    cube = DyadicCube(level=2, points=Point(0b1010 << 102, 2))
    contained_point = Point(0b1010 << 102, 2)
    non_contained_point = Point(0b1110 << 102, 2)
    assert contained_point in cube
    assert non_contained_point not in cube


def test_add_point():
    p1 = Point(0b101010 << 100, 2)
    p2 = Point(0b10101001 << 98, 2)
    p3 = Point(0b1010110110 << 96, 2)

    cube = DyadicCube(level=3, points=p1)

    cube.add_point(p2)
    assert cube.get_points() == PointSet([p1, p2])

    with pytest.raises(ValueError):
        cube.add_point(p3)


def test_add_points():
    p1 = Point(0b101010 << 100, 2)
    p2 = Point(0b10101001 << 98, 2)
    p3 = Point(0b10101011 << 98, 2)
    p4 = Point(0b1010110110 << 96, 2)
    ps2 = PointSet([p2, p3])
    ps3 = PointSet([p3, p4])

    cube = DyadicCube(level=3, points=p1)

    cube.add_points(ps2)
    assert cube.get_points() == PointSet([p1, p2, p3])

    with pytest.raises(ValueError):
        cube.add_points(ps3)


def test_creation_pointset():
    p1 = Point(0b101010 << 100, 2)
    p2 = Point(0b1010110110 << 96, 2)
    p3 = Point(0b10100100 << 98, 2)
    cube = DyadicCube(level=2, points=PointSet([p1, p2, p3]))
    assert cube.get_dim() == 2
    assert cube.get_level() == 2
    assert cube.get_morton_string() == "1010"
    assert cube.get_morton_code() == 10
    assert cube.get_lengths() == [2**-2, 2**-2]
    assert cube.num_points() == 3
    assert p1 in cube
    assert p2 in cube
    assert p3 in cube
    assert Point(0b101000 << 100, 2) in cube
    assert Point(0b101100 << 100, 2) not in cube


def test_equality_pointset():
    ps1 = PointSet([Point(0b101001 << 100, 2), Point(0b101000 << 100, 2)])
    ps2 = PointSet([Point(0b10100101 << 98, 2), Point(0b101001001101 << 94, 2)])
    ps3 = PointSet([Point(0b101101 << 100, 2), Point(0b101100 << 100, 2)])

    cube1 = DyadicCube(level=2, points=ps1)
    cube2 = DyadicCube(level=2, points=ps2)
    cube3 = DyadicCube(level=2, points=ps3)

    assert cube1 == cube2
    assert cube1 != cube3


def test_copy_pointset():
    ps = PointSet([Point(0b101001 << 100, 2), Point(0b101000 << 100, 2)])
    cube = DyadicCube(level=2, points=ps)
    cube_copy = cube.copy()

    assert cube == cube_copy
    assert cube is not cube_copy
    assert cube.get_points() == cube_copy.get_points()


def test_find_common_ancestor_pointset():
    # Two sets that differ slightly in their bits beyond level=3
    ps1 = PointSet(
        [
            Point(0b000101 << 100, 2),
            Point((0b000101 << 100) | (1 << 50), 2),
        ]
    )
    ps2 = PointSet(
        [
            Point(0b000110 << 100, 2),
            Point((0b000110 << 100) | (1 << 49), 2),
        ]
    )

    cube1 = DyadicCube(level=3, points=ps1)
    cube2 = DyadicCube(level=3, points=ps2)

    common_ancestor = cube1.find_common_ancestor(cube2)
    expected_ancestor = DyadicCube(level=2, points=ps1.merge(ps2))
    assert common_ancestor == expected_ancestor
    assert common_ancestor.get_level() == 2
    assert common_ancestor.num_points() == 4
    assert common_ancestor.get_points() == ps1.merge(ps2)


def test_find_intersection_pointset():
    ps1 = PointSet([Point(0b10100100 << 98, 2), Point(0b10100111 << 98, 2)])
    ps2 = PointSet([Point(0b10100101 << 98, 2), Point(0b101001011101 << 94, 2)])
    ps3 = PointSet([Point(0b101010 << 100, 2), Point(0b101010 << 100, 2)])

    cube1 = DyadicCube(level=3, points=ps1)
    cube2 = DyadicCube(level=3, points=ps2)
    cube3 = DyadicCube(level=3, points=ps3)

    intersection = cube1.find_intersection(cube2)
    assert intersection == cube2
    assert intersection is not cube2

    assert cube1.find_intersection(cube3) is None


def test_children_pointset():
    ps = PointSet([Point(0b10100100 << 98, 2), Point(0b10100111 << 98, 2)])
    cube = DyadicCube(level=1, points=ps)
    children = cube.children()
    assert len(children) == 4

    # Check a couple of them
    expected_codes = [0b1000, 0b1001, 0b1010, 0b1011]
    child_codes = [c.get_morton_code() for c in children]
    assert child_codes == expected_codes

    expected_points = [
        PointSet([Point(0b1000 << 102, 2)]),
        PointSet([Point(0b1001 << 102, 2)]),
        ps,
        PointSet([Point(0b1011 << 102, 2)]),
    ]

    child_points = [c.get_points() for c in children]

    assert child_points == expected_points


def test_top_left_point_pointset():
    ps = PointSet(
        [
            Point(0b100101 << 100, 2),
            Point((0b100101 << 100) | (1 << 50), 2),
        ]
    )
    cube = DyadicCube(level=2, points=ps)
    top_left = cube.top_left_point()
    expected_top_left = Point(0b1001 << 102, 2)
    assert top_left == expected_top_left


def test_bottom_right_point_pointset():
    ps = PointSet(
        [
            Point(0b100101 << 100, 2),
            Point((0b100101 << 100) | (1 << 49), 2),
        ]
    )
    cube = DyadicCube(level=2, points=ps)
    bottom_right = cube.bottom_right_point()
    expected_bottom_right = Point((0b1001 << 102) | ((1 << 102) - 1), 2)
    assert bottom_right == expected_bottom_right


def test_children_high_dimension_pointset():
    ps = PointSet(
        [
            Point(0b111 << (52 * 3), 3),
            Point((0b111 << (52 * 3)) | (1 << 60), 3),
        ]
    )
    cube = DyadicCube(level=1, points=ps)
    children = cube.children()
    assert len(children) == 8

    expected_children_codes = [
        0b111000,
        0b111001,
        0b111010,
        0b111011,
        0b111100,
        0b111101,
        0b111110,
        0b111111,
    ]
    child_codes = [c.get_morton_code() for c in children]
    assert child_codes == expected_children_codes


def test_middle_point_pointset():
    ps = PointSet(
        [
            Point(0b1010 << 102, 2),
            Point(((0b1010 << 102) | (1 << 50)), 2),
        ]
    )
    cube = DyadicCube(level=2, points=ps)
    middle = cube.middle_point()
    expected_middle = Point((0b1010 << 102) | (0b11 << 100), 2)
    assert middle == expected_middle


def test_contains_method_pointset():
    ps = PointSet(
        [
            Point(0b1010 << 102, 2),
            Point(((0b1010 << 102) | (1 << 50)), 2),
        ]
    )
    cube = DyadicCube(level=2, points=ps)

    contained_point = Point((0b1010 << 102) | (1 << 30), 2)
    non_contained_point = Point(0b1110 << 102, 2)

    assert contained_point in cube
    assert non_contained_point not in cube


def test_points_not_in_cube():
    ps = PointSet([Point(0b101010 << 100, 2), Point(0b101001 << 100, 2)])
    DyadicCube(level=2, points=ps)

    with pytest.raises(ValueError):
        DyadicCube(level=3, points=ps)
