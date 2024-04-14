"""
A placeholder module for visualizing the velocity field.
Currently, only a simple mesh plot of velocity magnitude is implemented.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes


def plot_mesh(
    vel: np.ndarray,
    low_bounds: np.ndarray,
    high_bounds: np.ndarray,
    axis: str = "x",
    index: int = 0,
    size: dict = [1024, 768],
):
    """
    Plot a meshgrid of velocity magnitude in the specified axis and index.

    Parameters
    ----------
    vel : np.ndarray
        3D velocity field array.
    low_bounds : np.ndarray
        Lower bounds of the field in [x, y, z].
    high_bounds : np.ndarray
        Upper bounds of the field in [x, y, z].
    axis : str, optional
        Axis to plot along, by default "x".
    index : int, optional
        Index along the axis to plot, by default 0.
    size : dict, optional
        Size of the figure in pixels, by default [1024, 768].

    Returns
    -------
    fig : Figure
        Matplotlib figure object.
    """
    # Check the input parameters
    try:
        if axis == "x":
            layers = vel.shape[0]
            vel = vel[index, :, :]
            extent = [low_bounds[1], high_bounds[1], low_bounds[2], high_bounds[2]]
        elif axis == "y":
            layers = vel.shape[1]
            vel = vel[:, index, :]
            extent = [low_bounds[0], high_bounds[0], low_bounds[2], high_bounds[2]]
        elif axis == "z":
            layers = vel.shape[2]
            vel = vel[:, :, index]
            extent = [low_bounds[0], high_bounds[0], low_bounds[1], high_bounds[1]]
        else:
            raise ValueError("Invalid plot axis. Must be one of ['x', 'y', 'z']")
    except IndexError:
        raise IndexError(
            f"Invalid plot index '{index}': meshgrid has only {layers} layers in {axis}-axis"
        )

    # Calculate the velocity magnitude
    magnitude = np.linalg.norm(vel, axis=-1)

    # Plot the meshgrid
    fig: Figure = plt.figure(figsize=(size[0] / 100, size[1] / 100))
    ax: Axes = fig.add_subplot(111)
    im = ax.imshow(
        magnitude.T,
        cmap="coolwarm",
        interpolation="nearest",
        extent=extent,
        origin="lower",
    )
    plt.colorbar(im, label="Velocity magnitude (m/s)")
    return fig
