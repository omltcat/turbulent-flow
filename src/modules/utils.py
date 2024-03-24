import numpy as np


def is_positive(number):
    return isinstance(number, (int, float)) and number > 0


def prob_round(number):
    fractional, whole = np.modf(number)
    if np.random.rand() < fractional:
        return int(np.ceil(number))
    else:
        return int(np.floor(number))


def random_unit_vector():
    # Generate a random direction.
    phi = 2 * np.pi * np.random.rand()  # Azimuthal angle
    costheta = 2 * np.random.rand() - 1  # Cosine of the polar angle

    # Convert to Cartesian coordinates.
    theta = np.arccos(costheta)  # Polar angle
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return np.array([x, y, z])
