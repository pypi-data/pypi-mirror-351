import pytest

from dyadic_tiling.morton_encoding import (
    continuous_from_morton_key,
    deinterleave_bits,
    float_to_int,
    interleave_bits,
    morton_key_from_continuous,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.0, 0),
        (2 ** (-53), 1),
        (0.25 - 2 ** (-53), 2251799813685247),
        (0.25, 2251799813685248),
        (0.25 + 2 ** (-53), 2251799813685249),
        (0.5 - 2 ** (-53), 4503599627370495),
        (0.5, 4503599627370496),
        (0.5 + 2 ** (-53), 4503599627370497),
        (0.75 - 2 ** (-53), 6755399441055743),
        (0.75, 6755399441055744),
        (0.75 + 2 ** (-53), 6755399441055745),
        (1.0 - 2 ** (-53), 9007199254740991),
        (1.0, 9007199254740991),
    ],
)
def test_float_to_int(value, expected):
    assert float_to_int(value) == expected


@pytest.mark.parametrize(
    "args, bits_per_dim, expected",
    [
        ([int("0", 2)], 1, int("0", 2)),
        ([int("0", 2)], 10, int("0", 2)),
        ([int("1", 2)], 1, int("1", 2)),
        ([int("1", 2)], 10, int("1", 2)),
        ([int("01", 2), int("10", 2)], 2, int("0110", 2)),
        ([int("01", 2), int("10", 2)], 3, int("0110", 2)),
        (
            [
                int("0110101", 2),
                int("1010101", 2),
                int("1111111", 2),
                int("0001100", 2),
            ],
            7,
            int("0110101011100011111100101110", 2),
        ),
    ],
)
def test_interleave_bits(args, bits_per_dim, expected):
    assert interleave_bits(*args) == expected & ((1 << (53 - bits_per_dim)) - 1)


@pytest.mark.parametrize(
    "coords, bits_per_dim, expected",
    [
        ([0.0], 1, int("0", 2)),
        ([0.25], 1, int("0", 2)),
        ([0.5 - 2 ** (-16)], 1, int("0", 2)),
        ([0.5], 1, int("1", 2)),
        ([0.75], 1, int("1", 2)),
        ([1.0], 1, int("1", 2)),
        ([0.0], 10, int("0000000000", 2)),
        ([0.0 + 2 ** (-10)], 10, int("0000000001", 2)),
        ([0.0 + 2 ** (-10) - 2 ** (-16)], 10, int("0000000000", 2)),
        ([0.25 - 2 ** (-16)], 10, int("0011111111", 2)),
        ([0.25], 10, int("0100000000", 2)),
        ([0.25 + 2 ** (-16)], 10, int("0100000000", 2)),
        ([0.25 + 2 ** (-10)], 10, int("0100000001", 2)),
        ([0.5 - 2 ** (-16)], 10, int("0111111111", 2)),
        ([0.5], 10, int("1000000000", 2)),
        ([0.5 + 2 ** (-16)], 10, int("1000000000", 2)),
        ([0.5 + 2 ** (-10)], 10, int("1000000001", 2)),
        ([0.75 - 2 ** (-16)], 10, int("1011111111", 2)),
        ([0.75], 10, int("1100000000", 2)),
        ([0.75 + 2 ** (-16)], 10, int("1100000000", 2)),
        ([0.75 + 2 ** (-10)], 10, int("1100000001", 2)),
        ([1.0 - 2 ** (-10) - 2 ** (-16)], 10, int("1111111110", 2)),
        ([1.0 - 2 ** (-10)], 10, int("1111111111", 2)),
        ([1.0], 10, int("1111111111", 2)),
        ([0.0, 0.0], 10, int("00000000000000000000", 2)),
        ([1.0, 1.0], 10, int("11111111111111111111", 2)),
        ([0.0, 1.0], 10, int("01010101010101010101", 2)),
        ([0.25, 0.25], 10, int("00110000000000000000", 2)),
        ([0.75, 0.75], 10, int("11110000000000000000", 2)),
        ([0.0], 53, int("0", 2)),
        ([0.25], 53, 2251799813685248),
        ([0.5], 53, 4503599627370496),
        ([0.75], 53, 6755399441055744),
        ([1.0], 53, 9007199254740991),
        ([0.0, 0.0], 53, int("0", 2)),
        ([1.0, 1.0], 53, int("1" * 106, 2)),
        ([0.0, 1.0], 53, int("01" * 53, 2)),
        ([0.25, 0.25], 53, int("0011" + "0" * 102, 2)),
        ([0.75, 0.75], 53, int("1111" + "0" * 102, 2)),
    ],
)
def test_morton_key_from_continuous(coords, bits_per_dim, expected):
    assert (
        morton_key_from_continuous(coords) >> len(coords) * (53 - bits_per_dim)
        == expected
    )


@pytest.mark.parametrize(
    "morton_key, dim, expected",
    [
        (int("0", 2), 1, [int("0", 2)]),
        (int("1", 2), 1, [int("1", 2)]),
        (int("0110", 2), 2, [int("01", 2), int("10", 2)]),
        (
            int("0110" + "1010" + "1110" + "0011" + "1111" + "0010" + "1110", 2),
            4,
            [
                int("0110101", 2),
                int("1010101", 2),
                int("1111111", 2),
                int("0001100", 2),
            ],
        ),
    ],
)
def test_deinterleave_bits(morton_key, dim, expected):
    assert deinterleave_bits(morton_key, dim) == expected


@pytest.mark.parametrize(
    "morton_key, dim, expected",
    [
        (morton_key_from_continuous([0.0]), 1, [0.0]),
        (morton_key_from_continuous([0.25]), 1, [0.25]),
        (morton_key_from_continuous([0.5]), 1, [0.5]),
        (morton_key_from_continuous([0.75]), 1, [0.75]),
        (morton_key_from_continuous([1]), 1, [1 - 2**-53]),
        (
            morton_key_from_continuous(
                [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            ),
            10,
            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        ),
    ],
)
def test_continuous_from_morton_key(morton_key, dim, expected):
    assert all(
        (
            [
                abs(x - y) < 2**-52
                for x, y in zip(continuous_from_morton_key(morton_key, dim), expected)
            ]
        )
    )


def test_float_to_int_value_error():
    with pytest.raises(ValueError):
        float_to_int(
            1.0 + 2**-52
        )  # This should raise an error since it's out of bounds
