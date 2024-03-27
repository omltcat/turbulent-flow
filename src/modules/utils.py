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


def expanded_inbounds(
    centers: np.ndarray,
    length_scales: np.ndarray,
    low_bounds=None | np.ndarray,
    high_bounds=None | np.ndarray,
):
    """
    Check for eddies either within the bounds of box, or outside but partially touching the box.

    Parameters:
    centers (np.ndarray): Centers of the eddies.
    length_scales (np.ndarray): Length scales of the eddies.
    low_bounds (np.ndarray): [x, y, z] lower bounds of the box.
    high_bounds (np.ndarray): [x, y, z] upper bounds of the box.

    Returns:
    np.ndarray: Boolean array indicating if the eddies are within the bounds of the box.
    """

    if low_bounds is None:
        low_bounds = -high_bounds
    elif high_bounds is None:
        high_bounds = -low_bounds

    length_scales = length_scales.reshape(-1, 1)
    low_bounds = low_bounds.reshape(-1, 3)
    high_bounds = high_bounds.reshape(-1, 3)
    return np.all(
        (centers > low_bounds - length_scales)
        & (centers < high_bounds + length_scales),
        axis=-1,
    )
