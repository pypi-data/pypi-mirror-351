import pytest

from dyadic_tiling.point import Point


@pytest.fixture
def sample_point():
    return Point([0.3, 0.6, 0.8])


@pytest.fixture
def morton_points():
    point_2d_1 = Point([0.5, 0.75])
    point_2d_2 = Point([0.25, 0.25])
    point_1d = Point([0.5])
    point_2d_3 = Point([0.5, 0.5])
    return point_2d_1, point_2d_2, point_1d, point_2d_3


@pytest.fixture
def high_dimensional_point():
    return Point([0.5] * 10)


@pytest.fixture
def boundary_points():
    return Point([0.0, 0.0]), Point([1.0, 1.0])


@pytest.fixture
def custom_coordinate_ranges_points():
    point_default = Point(
        [0.5, 0.1]
    )  # Uses default coordinate_ranges [(0.0, 1.0), (0.0, 1.0)]
    point_custom = Point([0.5, 0.1], coordinate_ranges=[(0, 10), (-5, 15)])
    point_out_of_range = Point([15, 20], coordinate_ranges=[(0, 10), (-5, 15)])
    return point_default, point_custom, point_out_of_range


def test_sample_point(sample_point):
    assert sample_point.get_coords() == [0.3, 0.6, 0.8]
    assert sample_point.get_dim() == 3
    assert sample_point.get_bits_per_dim() == 53
    assert sample_point.get_truncated_morton_code(3) == int("011101000", 2)
    assert sample_point.get_morton_string(3) == "011101000"
    assert (
        str(sample_point)
        == "Point(point=[0.3, 0.6, 0.8], morton_code="
        + f"{int('011101' + '000010111101' * 12 + '000011110', 2)}, dim=3)"
    )


def test_str_fill():
    x = Point([0.0625, 0.125])
    assert x.get_morton_string(1) == "00"
    assert x.get_morton_string(2) == "0000"
    assert x.get_morton_string(3) == "000001"
    assert x.get_morton_string(4) == "00000110"
    assert x.get_morton_string(5) == "0000011000"
    assert x.get_morton_string(6) == "000001100000"
    for dim in range(1, 53):
        x = Point([2 ** (-dim), 2 ** (-dim)])
        assert x.get_morton_string(dim) == "0" * (2 * (dim - 1)) + "11"


def test_check_two_points_have_same_dim(morton_points):
    point_2d_1, point_2d_2, point_1d, point_2d_3 = morton_points
    assert point_2d_1.check_two_morton_codes_have_same_dim(point_2d_2)
    assert not point_2d_1.check_two_morton_codes_have_same_dim(point_1d)
    assert point_2d_1.check_two_morton_codes_have_same_dim(point_2d_3)


def test_check_two_points_are_comparable(morton_points):
    point_2d_1, point_2d_2, point_1d, _ = morton_points
    point_2d_1.raise_error_if_morton_codes_not_in_same_dim(point_2d_2)
    with pytest.raises(ValueError):
        point_2d_1.raise_error_if_morton_codes_not_in_same_dim(point_1d)


def test_equality_comparison(morton_points):
    point_2d_1, point_2d_2, point_1d, point_2d_3 = morton_points
    new_point_2d_1 = point_2d_1.copy()
    assert point_2d_1 != point_2d_2
    assert point_2d_1 == new_point_2d_1
    assert point_2d_1 is not new_point_2d_1
    assert point_2d_1 > point_2d_2
    assert point_2d_2 < point_2d_1
    assert point_2d_1 >= point_2d_2
    assert point_2d_2 <= point_2d_1
    assert point_2d_1 >= point_2d_3
    assert point_2d_1 >= point_2d_3
    with pytest.raises(ValueError):
        _ = point_2d_1 == point_1d


def test_equality_comparison_level_k():
    point_1 = Point([0.5, 0.75])
    i = 1
    while i < 53:
        point_2 = Point([0.5 + 2 ** -(i + 1), 0.75 + 2 ** -(i + 1)])
        assert point_1.compare_level_k(point_2, "==", i)
        i += 1
        assert point_1.compare_level_k(point_2, "<", i)


def test_containing_dyadiccube(morton_points):
    point_2d_1, _, _, _ = morton_points
    cube = point_2d_1.get_containing_cube(0)
    assert cube.get_dim() == 2
    assert cube.get_level() == 0
    assert cube.get_morton_code() == int("0", 2)
    cube = point_2d_1.get_containing_cube(1)
    assert cube.get_dim() == 2
    assert cube.get_level() == 1
    assert cube.get_morton_code() == int("11", 2)
    cube = point_2d_1.get_containing_cube(2)
    assert cube.get_dim() == 2
    assert cube.get_level() == 2
    assert cube.get_morton_code() == int("1101", 2)
    cube = point_2d_1.get_containing_cube(3)
    assert cube.get_dim() == 2
    assert cube.get_level() == 3
    assert cube.get_morton_code() == int("110100", 2)
    cube = point_2d_1.get_containing_cube(5)
    assert cube.get_dim() == 2
    assert cube.get_level() == 5
    assert cube.get_morton_code() == point_2d_1.get_truncated_morton_code(5)


def test_invalid_morton_code_initialization():
    with pytest.raises(ValueError):
        Point(12345)  # Should provide 'dim' when initializing with Morton code


def test_invalid_point_initialization():
    with pytest.raises(TypeError):
        Point("invalid_point")


def test_invalid_dimension_morton_code():
    with pytest.raises(ValueError):
        Point(12345, dim=-1)

    with pytest.raises(ValueError):
        Point(12345, dim=0)


def test_boundary_points(boundary_points):
    point_min, point_max = boundary_points
    assert point_min.get_coords() == [0.0, 0.0]
    assert point_max.get_coords() == [1.0, 1.0]
    assert point_min.get_truncated_morton_code(1) == 0
    assert point_max.get_truncated_morton_code(1) == int("11", 2)


def test_high_dimensional_point(high_dimensional_point):
    assert high_dimensional_point.get_dim() == 10
    assert len(high_dimensional_point.get_morton_string(1)) == 10
    assert high_dimensional_point.get_morton_string(1) == "1" * 10
    assert high_dimensional_point.get_morton_string(2) == "1" * 10 + "0" * 10
    assert high_dimensional_point.get_morton_string(3) == "1" * 10 + "00" * 10


def test_comparison_at_levels():
    point_1 = Point([0.5, 0.75])
    point_2 = Point([0.5, 0.75 + 2**-5])  # Adjusted for testing
    assert point_1.compare_level_k(point_2, "==", 4)
    assert point_1.compare_level_k(point_2, "!=", 5)


def test_comparison_at_level_zero(morton_points):
    point_2d_1, point_2d_2, _, _ = morton_points
    assert point_2d_1.compare_level_k(
        point_2d_2, "==", 0
    )  # All points should be equal at level 0


def test_copy_functionality(morton_points):
    point_2d_1, _, _, _ = morton_points
    point_copy = point_2d_1.copy()
    assert point_copy.get_coords() == point_2d_1.get_coords()
    assert point_copy.get_morton_code() == point_2d_1.get_morton_code()
    assert point_copy.get_dim() == point_2d_1.get_dim()
    assert point_copy is not point_2d_1  # Ensure they are different objects


def test_invalid_cube_levels(morton_points):
    point_2d_1, _, _, _ = morton_points
    with pytest.raises(ValueError):
        point_2d_1.get_containing_cube(
            point_2d_1.bits_per_dim + 1
        )  # Beyond bits per dimension

    with pytest.raises(ValueError):
        point_2d_1.get_containing_cube(-1)  # Invalid level


def test_hash_functionality(morton_points):
    point_2d_1, point_2d_2, _, point_2d_3 = morton_points
    new_point_2d_1 = point_2d_1.copy()
    assert hash(point_2d_1) == hash(new_point_2d_1)
    assert point_2d_1 is not new_point_2d_1
    assert hash(point_2d_1) != hash(point_2d_2)
    assert hash(point_2d_1) != hash(point_2d_3)


def test_point_with_custom_coordinate_ranges(custom_coordinate_ranges_points):
    point_default, point_custom, _ = custom_coordinate_ranges_points

    # Default coordinate_ranges should be [(0.0, 1.0), (0.0, 1.0)]
    assert point_default.coordinate_ranges == [(0.0, 1.0), (0.0, 1.0)]

    # Custom coordinate_ranges should be [(0, 10), (-5, 15)]
    assert point_custom.coordinate_ranges == [(0, 10), (-5, 15)]

    # Both points should have the same coordinates
    assert point_default.get_coords() == point_custom.get_coords()

    # Morton codes should differ due to different scaling
    assert point_default.get_morton_code() != point_custom.get_morton_code()


def test_point_out_of_range_coordinates(custom_coordinate_ranges_points):
    _, _, point_out_of_range = custom_coordinate_ranges_points

    # Attempting to get Morton code should raise ValueError due to coordinates out of range
    with pytest.raises(ValueError):
        point_out_of_range.get_morton_code()


def test_setting_new_coordinate_ranges(sample_point):
    sample_point.set_coordinate_ranges([(0.0, 1.0), (0.5, 1.0), (0.0, 1.0)])
    # Morton code should be recalculated based on new coordinate_ranges
    old_morton_code = sample_point.get_morton_code()
    sample_point.set_coordinate_ranges([(0.0, 1.0)] * 3)
    new_morton_code = sample_point.get_morton_code()
    assert old_morton_code != new_morton_code


def test_comparing_points_with_different_coordinate_ranges():
    point_1 = Point([0.5, 0.75], coordinate_ranges=[(0, 1), (0, 1)])
    point_2 = Point([0.5, 0.75], coordinate_ranges=[(0, 2), (0, 2)])
    with pytest.raises(ValueError):
        _ = (
            point_1 == point_2
        )  # Should raise ValueError due to different coordinate_ranges


def test_comparing_points_with_same_coordinate_ranges():
    coordinate_ranges = [(-3, 10), (0, 10)]
    point_1 = Point([5, 5], coordinate_ranges=coordinate_ranges)
    point_2 = Point([5, 5], coordinate_ranges=coordinate_ranges)
    assert point_1 == point_2  # Should be equal


def test_point_coordinate_out_of_range_after_update():
    point = Point([5, 5], coordinate_ranges=[(0, 10), (0, 10)])
    point.set_coordinates([15, 5])  # Update coordinates
    with pytest.raises(ValueError):
        point.get_morton_code()  # Should raise ValueError due to coordinate out of range


def test_setting_invalid_coordinate_ranges():
    with pytest.raises(ValueError):
        Point([5, 5], coordinate_ranges=[(0, 10)])  # Mismatch in dimensions


def test_comparing_points_after_coordinate_ranges_change():
    point_1 = Point([5, 5], coordinate_ranges=[(0, 10), (0, 10)])
    point_2 = Point([5, 5], coordinate_ranges=[(0, 10), (0, 10)])
    assert point_1 == point_2
    point_2.set_coordinate_ranges([(0, 20), (0, 20)])
    with pytest.raises(ValueError):
        _ = point_1 == point_2  # Now coordinate_ranges differ


def test_invalid_coordinate_range_values():
    with pytest.raises(ValueError):
        Point(
            [5, 5], coordinate_ranges=[(10, 0), (0, 10)]
        ).update_morton_code()  # min_val > max_val

    with pytest.raises(ValueError):
        Point(
            [5, 5], coordinate_ranges=[(5, 5), (0, 10)]
        ).update_morton_code()  # min_val == max_val


def test_coordinate_ranges_after_copy(morton_points):
    point_2d_1, _, _, _ = morton_points
    point_copy = point_2d_1.copy()
    assert point_copy.coordinate_ranges == point_2d_1.coordinate_ranges
    point_copy.set_coordinate_ranges([(0, 2), (0, 2)])
    assert point_copy.coordinate_ranges != point_2d_1.coordinate_ranges


def test_large_coordinate_ranges():
    point = Point([-5000, 10000], coordinate_ranges=[(-10000, 4), (0, 20000)])
    morton_code = point.get_morton_code()
    assert morton_code is not None  # Ensure morton code is computed without errors


def test_zero_length_coordinate_range():
    with pytest.raises(ValueError):
        Point([5], coordinate_ranges=[(5, 5)]).update_morton_code()  # Zero-length range


def test_coordinate_scaling():
    point = Point([5], coordinate_ranges=[(-3, 10)])
    scaled_coord = (5 - -3) / (10 - -3)  # Expected to be 8/13
    point.update_morton_code()
    from dyadic_tiling.morton_encoding import morton_key_from_continuous

    expected_morton_code = morton_key_from_continuous([scaled_coord])
    assert point.get_morton_code() == expected_morton_code
