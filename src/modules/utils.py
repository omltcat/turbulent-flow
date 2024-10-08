import numpy as np


def is_positive(number):
    """
    Check if a variable is a positive number.
    """
    return isinstance(number, (int, float)) and number > 0


def is_not_negative(number):
    """
    Check if a variable is a positive number or zero.
    """
    return isinstance(number, (int, float)) and number >= 0


def stoch_round(numbers):
    """
    Stochastic rounding
    Round numbers to the nearest integer with a probability equal to the fractional part.
    """
    fractional, whole = np.modf(numbers)
    return whole.astype(int) + (np.random.rand(*numbers.shape) < fractional)


def random_unit_vectors(n):
    """
    Generate evently distributed random unit vectors on the sphere.

    Parameters
    ----------
    n : int
        Number of vectors to generate.

    Returns
    -------
    np.ndarray
        Array of shape (n, 3) containing the unit vectors.
    """
    # Generate random directions.
    phi = 2 * np.pi * np.random.rand(n)  # Azimuthal angles
    theta = np.arccos(2 * np.random.rand(n) - 1)  # Polar angles

    # Convert to Cartesian coordinates.
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return np.stack((x, y, z), axis=-1)


def filter_keys(dictionary, keys):
    """
    Filter dictionary keys by a list of keys.
    Mainly used to filter out unwanted keys from a user provided json object.

    Parameters
    ----------
    dictionary : dict
        Dictionary to filter.
    keys : list
        List of keys to keep.

    Returns
    -------
    dict
        Filtered dictionary.
    """
    return {key: dictionary[key] for key in keys if key in dictionary}
