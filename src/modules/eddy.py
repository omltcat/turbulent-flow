"""Library eddy related functions."""
import cupy as cp
from modules import shape_function


def sum_vel_chunk(
    centers: cp.ndarray,
    sigma: cp.ndarray,
    alpha: cp.ndarray,
    x_coords: cp.ndarray,
    y_coords: cp.ndarray,
    z_coords: cp.ndarray,
):
    """Calculate the velocity field due to each eddy within a chunk."""
    # Create a meshgrid of x, y, and z coordinates
    # start_time = time.time()
    positions = cp.stack(
        cp.meshgrid(x_coords, y_coords, z_coords, indexing="ij"), axis=-1
    )[cp.newaxis, ...]

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
    dk = cp.linalg.norm(rk, axis=-1)[..., cp.newaxis]

    # Calculate the velocity fluctuation due to each eddy
    vel_fluct = shape_function.active(dk, chunk_sigma) * cp.cross(rk, chunk_alpha)
    del rk, dk, chunk_alpha, chunk_sigma

    # Sum the velocity fluctuations from all eddies
    vel_fluct = cp.sum(vel_fluct, axis=0)

    return vel_fluct
