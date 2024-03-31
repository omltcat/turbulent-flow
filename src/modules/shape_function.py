import numpy as np
from typing import Callable, Union

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


def gaussian(dk, length_scale):
    global cutoff
    return np.where(
        dk < cutoff,
        C * np.exp(-HALF_PI * dk**2),
        0
    )


active_function = gaussian
cutoff = 2.0
