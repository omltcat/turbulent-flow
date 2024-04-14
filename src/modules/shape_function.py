"""
Shape function library for eddy calculation

This module is intended to be modifiable by the user to define custom shape functions.
"""
import numpy as np
from typing import Callable, Union
from modules import utils

HALF_PI = 0.5 * np.pi
C = 3.6276


def set_active(func: Union[Callable, str]):
    """
    Set the active shape function to be used in the eddy calculation.

    Parameters
    ----------
    func : Union[Callable, str]
        Shape function to use. Can be a function object or a string name of a function.
    """
    if isinstance(func, str):
        try:
            func = globals()[func]
        except KeyError:
            raise ValueError(f"Shape function \"{func}\" is not defined.")

    if not callable(func):
        raise ValueError("Argument must be a valid function or function name in string.")

    global active
    active = func


def set_cutoff(value: float):
    """
    Set the global cutoff value for the shape function.
    Outside this value, the shape function that uses such global value should return 0.
    Note: Some shape functions may have inherently defined cutoff values.

    Parameters
    ----------
    value : float
        Cutoff value for the shape function.
    """
    if not utils.is_positive(value):
        raise ValueError("Cutoff value must be a positive.")
    global cutoff
    cutoff = value


def get_cutoff():
    return cutoff


def quadratic(dk, length_scale):
    """Quadratic shape function"""
    return np.where(
        dk < 1.0,
        length_scale * (1 - dk) ** 2,
        0
    )
    # Note that this function uses a custom cutoff value of 1.0 and is not affected by the global cutoff value.


def gaussian(dk, length_scale):
    """Gaussian shape function"""
    return np.where(
        dk < cutoff,
        C * np.exp(-HALF_PI * dk**2),
        0
    )
    # Mathematically, this function is equivalent to:

    #         ┌ C * e^(-π/2 * dk^2), if dk < cutoff
    # q(dk) = ┤
    #         └ 0, elsewhere

    # where C = 3.6276, HALF_PI = π/2
    # These are defined as constants at the top of this file. You can use different values or define new ones.
    # Use pre-calcuated constants when possible because this function is called many times.
    # It is faster not to recalculate these values every time.

    # Your inputs must include dk and length_scale (sigma), even if some shape functions may not use length_scale.

    # You can choose what shape function and cutoff value to use in query arguments.


active = gaussian
cutoff = 2.0
