import numpy as np
from typing import Callable, Union

HALF_PI = 0.5 * np.pi
C = 3.6276


def set_active(func: Union[Callable, str]):
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
    global cutoff
    cutoff = value


def get_cutoff():
    return cutoff


def quadratic(dk, length_scale):
    return np.where(
        dk < 1.0,
        length_scale * (1 - dk) ** 2,
        0
    )


# @numba.jit(nopython=True)
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
    # These are defined as constants at the top of this file, you can change it to a different value.
    # You should use pre-calcuated constants because this function is called many times.
    # It is faster not to recalculate these values every time.

    # cutoff is set in the query file.


active = gaussian
cutoff = 2.0
