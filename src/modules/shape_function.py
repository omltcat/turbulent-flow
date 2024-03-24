import numpy as np
from typing import Callable, Union

CUTOFF_1 = 1.0
CUTOFF_2 = 2.0
HALF_PI = 0.5 * np.pi
C = 3.6276


def active(dk: float, length_scale: float):
    return active_function(dk, length_scale)


def set_active(func: Union[Callable, str]):
    if isinstance(func, str):
        try:
            func = globals()[func]
        except KeyError:
            raise ValueError(f"Shape function \"{func}\" is not defined.")

    if not callable(func):
        raise ValueError("Argument must be a valid function or function name in string.")

    global active_function
    active_function = func


def quadratic(dk, length_scale):
    if dk > 1.0:
        return 0
    else:
        return length_scale * (1 - dk**2)


def gaussian(dk, length_scale):
    return np.where(
        dk < CUTOFF_2,
        C * np.exp(-HALF_PI * dk**2),
        0
    )


active_function = gaussian
