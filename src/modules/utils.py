import cupy as cp


def is_positive(number):
    return isinstance(number, (int, float)) and number > 0


def is_not_negative(number):
    return isinstance(number, (int, float)) and number >= 0


def stoch_round(numbers):
    """Stochastic rounding"""
    fractional, whole = cp.modf(numbers)
    return whole.astype(int) + (cp.random.rand(*numbers.shape) < fractional)


def random_unit_vectors(n):
    # Generate random directions.
    phi = 2 * cp.pi * cp.random.rand(n)  # Azimuthal angles
    theta = cp.arccos(2 * cp.random.rand(n) - 1)  # Polar angles

    # Convert to Cartesian coordinates.
    x = cp.sin(theta) * cp.cos(phi)
    y = cp.sin(theta) * cp.sin(phi)
    z = cp.cos(theta)

    return cp.stack((x, y, z), axis=-1)
