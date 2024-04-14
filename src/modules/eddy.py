"""
Library eddy related functions.

Currently only supports spherical isotropic eddies.
"""
import numpy as np
from modules import shape_function


def sum_vel_chunk(
    centers: np.ndarray,
    sigma: np.ndarray,
    alpha: np.ndarray,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    z_coords: np.ndarray,
):
    """
    Calculate the velocity field due to each eddy within a chunk.

    Parameters
    ----------
    centers : np.ndarray
        Array of eddy centers.
    sigma : np.ndarray
        Array of eddy length scales.
    alpha : np.ndarray
        Array of eddy intensities.
    x_coords : np.ndarray
        Array of x coordinates spanning the chunk.
    y_coords : np.ndarray
        Array of y coordinates spanning the chunk.
    z_coords : np.ndarray
        Array of z coordinates spanning the chunk.

    Returns
    -------
    np.ndarray
        Array of velocity fluctuations due to each eddy within the chunk.
    """
    # Create a meshgrid of x, y, and z coordinates
    # start_time = time.time()
    positions = np.stack(
        np.meshgrid(x_coords, y_coords, z_coords, indexing="ij"), axis=-1
    )[np.newaxis, ...]

    # Reshape the centers, alpha, and sigma arrays to allow broadcasting
    chunk_centers = centers.reshape(-1, 1, 1, 1, 3)
    chunk_alpha = alpha.reshape(-1, 1, 1, 1, 3)
    chunk_sigma = sigma.reshape(-1, 1, 1, 1, 1)

    # Calculate the relative position vectors and normalize
    try:
        rk = (positions - chunk_centers) / chunk_sigma
    except MemoryError as e:    # pragma: no cover
        raise MemoryError(
            f"{e}\nNot enough memory to calculate meshgrid-eddy relations. Consider decrease chunk size."
        ) from e

    del positions, chunk_centers

    # Calculate the normalized distance
    dk = np.linalg.norm(rk, axis=-1)[..., np.newaxis]

    # Calculate the velocity fluctuation due to each eddy
    vel_fluct = shape_function.active(dk, chunk_sigma) * np.cross(rk, chunk_alpha)
    del rk, dk, chunk_alpha, chunk_sigma

    # Sum the velocity fluctuations from all eddies
    vel_fluct = np.sum(vel_fluct, axis=0)

    return vel_fluct
