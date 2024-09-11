"""
Functions in this module is to calculate the multiplier of the mean x-velocity in the flow field.
Arguments are the normalized distance from x-axis (centerline) in y and z directions.
i.e. ny = 1 or -1 means the point is on the edge, ny = 0 means the point is on the centerline.
ny and nz will always be in the range of -1 to 1.

Also note that ny and nz are passed in as numpy arrays, so your function should be able to handle that.
Generally, regular math operations will work just fine, but more complex logic may require additional considerations.

If the function returns 0.5, and avg_vel set by user is 10 m/s, then the x-velocity at that point is 5 m/s.

You can define your own velocity function here with any inner workings,
as long as it takes ny and nz as arguments and returns a multiplier.
"""

from typing import Callable


def get_func(func_name) -> Callable[[float, float], float]:
    """
    Get the function object by its name.
    Don't change this function unless you know what you're doing.
    """
    try:
        return globals()[func_name]
    except KeyError:
        raise ValueError(f"Velocity function \"{func_name}\" is not defined.")


# Put your custom velocity functions below

def parabola_2d(ny, nz):
    """
    Parabolic velocity profile in y, with no variation in z direction.
    """
    return 1 - ny**2


def linear_2d(ny, nz):
    """
    Linear velocity profile in y, with no variation in z direction.
    """
    return (ny + 1) / 2
