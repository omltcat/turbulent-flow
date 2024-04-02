import numpy as np


def is_positive(number):
    return isinstance(number, (int, float)) and number > 0


def is_not_negative(number):
    return isinstance(number, (int, float)) and number >= 0


def stoch_round(numbers):
    """Stochastic rounding"""
    fractional, whole = np.modf(numbers)
    return whole.astype(int) + (np.random.rand(*numbers.shape) < fractional)


def random_unit_vectors(n):
    # Generate random directions.
    phi = 2 * np.pi * np.random.rand(n)  # Azimuthal angles
    theta = np.arccos(2 * np.random.rand(n) - 1)  # Polar angles

    # Convert to Cartesian coordinates.
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return np.stack((x, y, z), axis=-1)
