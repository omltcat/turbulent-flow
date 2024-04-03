import cupy as cp
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from modules import file_io

PLT_DIR = "plots"


def plot_mesh(
    vel: cp.ndarray,
    low_bounds: cp.ndarray | list,
    high_bounds: cp.ndarray | list,
    axis: str = "x",
    index: int = 0,
    save: str = None,
    size: dict = [1024, 768],
):
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

    magnitude = cp.linalg.norm(vel, axis=-1)

    fig: Figure = plt.figure(figsize=(size[0] / 100, size[1] / 100))
    ax: Axes = fig.add_subplot(111)
    im = ax.imshow(
        magnitude.T.get(),
        cmap="coolwarm",
        interpolation="nearest",
        extent=extent,
        origin="lower",
    )
    plt.colorbar(im, label="Velocity magnitude (m/s)")
    if save:
        file_io.write(PLT_DIR, save, fig, format="png")
    return fig
