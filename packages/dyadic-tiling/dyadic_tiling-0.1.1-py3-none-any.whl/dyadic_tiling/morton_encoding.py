"""
This file contains functions for encoding a point in [0,1]^d into a Morton key.
In each dimension, the first bit of the Morton encoding determines which interval
of [0, 0.5) and [0.5, 1] the value in that dimension is in. Subsequent bits
determine further subintervals, for example the first two bits determine which
interval of [0, 0.25), [0.25, 0.5), [0.5, 0.75), [0.75, 1) the value is in. The bits
corresponding to each dimension are interleaved to form the Morton key.
"""

import struct


def float_to_int(x):
    """Convert a double precision float in [0, 1] to a 53-bit integer"""
    if not (0 <= x <= 1):
        raise ValueError("Float must be in the range [0, 1]")

    if x == 0.0:
        return 0
    if x == 1.0:
        return 2**53 - 1

    # Pack the float into 8 bytes (double precision)
    packed = struct.pack(">d", x)
    # Unpack as 64-bit unsigned integer
    unpacked = struct.unpack(">Q", packed)[0]

    # Mask to get the mantissa (the last 52 bits)
    mantissa = unpacked & ((1 << 52) - 1)
    # Extract the exponent (bits 52 to 62)
    exponent = ((unpacked >> 52) & 0x7FF) - 1023

    # Include the implicit leading 1 in the mantissa if exponent is not the smallest
    if exponent != -1023:
        mantissa |= 1 << 52

    # Adjust the mantissa according to the exponent to get a 53-bit integer
    # representation
    result = (
        mantissa << (52 - exponent) if exponent >= 0 else mantissa >> (-1 - exponent)
    )

    return result


def interleave_bits(*args: int) -> list[int]:
    """
    Interleave bits from multiple integers (coordinates).
    """
    result = 0
    for i in range(53 - 1, -1, -1):
        for arg in args:
            result = (result << 1) | ((arg >> i) & 1)

    return result


def morton_key_from_continuous(coords: list[float]) -> int:
    """Generate a Morton key for coordinates in [0, 1]^d."""
    discretised_coords = [float_to_int(coord) for coord in coords]
    return interleave_bits(*discretised_coords)


def deinterleave_bits(morton_key: int, dim: int) -> list[int]:
    """
    Deinterleave bits from a Morton key into individual coordinates using
    the final bits_per_dim bits of each integer.
    """
    coords = [0] * dim
    for i in range(53):
        for j in range(dim):
            coords[j] |= ((morton_key >> ((53 - i) * dim - j - 1)) & 1) << (53 - i - 1)
    return coords


def continuous_from_morton_key(morton_key: int, dim: int) -> list[float]:
    """Generate coordinates in [0, 1]^d from a Morton key."""
    discretised_coords = deinterleave_bits(morton_key, dim)
    max_val = 1 << 53
    return [coord / max_val for coord in discretised_coords]
