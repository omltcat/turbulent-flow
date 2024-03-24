import numpy as np


def is_positive(number):
    return isinstance(number, (int, float)) and number > 0


def prob_round(number):
    fractional, whole = np.modf(number)
    if np.random.rand() < fractional:
        return int(np.ceil(number))
    else:
        return int(np.floor(number))
