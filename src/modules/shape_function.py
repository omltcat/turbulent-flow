import numpy as np
from typing import Callable, Union


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
    # This value determines cutoff distance
    if dk > 2.0:
        return 0
    else:
        return 3.6276 * np.exp(-0.5*np.pi * dk**2)


active_function = gaussian
