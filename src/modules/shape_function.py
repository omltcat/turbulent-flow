import numpy as np
from typing import Callable, Union


def active(rel_pos: np.ndarray, length_scale: float):
    d = np.linalg.norm(rel_pos)/length_scale
    return active_function(d, length_scale)


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


def quadratic(d, sigma):
    cutoff = 1.0
    if d > cutoff:
        return 0
    else:
        return sigma * (1 - d**2)


def exp_2pi(d, sigma):
    cutoff = 2.0
    if d > cutoff:
        return 0
    else:
        return 2 * np.pi * np.exp(-4.5 * d**2)


active_function = quadratic
