"""
Turbulent Flow Field Module
"""

# import time
from tqdm import tqdm
import numpy as np
from modules import utils
from modules import file_io
from modules import shape_function
from modules.eddy_profile import EddyProfile

WRAP_ITER = [-1, 0, 1]  # Iterations to wrap around the flow field, do not change
CUTOFF = 1.2 * shape_function.get_cutoff()  # has to be greater than 1


class FlowField:
    """
    Flow field class with eddies within.
    Contains methods to calculate the velocity at any point in the field.
    """

    def __init__(
        self,
        profile: EddyProfile,
        name: str,
        dimensions: np.ndarray | list,
        avg_vel: float,
    ):
        """Initialize the flow field with the given parameters."""
        if isinstance(dimensions, list):
            dimensions = np.array(dimensions)

        # Check for invalid inputs
        if not isinstance(dimensions, np.ndarray) or dimensions.shape != (3,):
            raise ValueError("Dimensions must be a 3D numpy array")
        elif not np.all(np.isreal(dimensions)):
            raise ValueError("Dimensions must be real numbers")
        if np.any(dimensions <= 0):
            raise ValueError("Dimensions must be positive")
        if not utils.is_not_negative(avg_vel):
            raise ValueError("Average velocity must be a non-negative number")
        self.profile = profile
        self.name = name
        self.dimensions = dimensions
        self.avg_vel = avg_vel

        self.new()

    def new(self):
        """Generate a new flow field based on the given parameters."""
        # Get differnet eddy variants
        self.variant_density = self.profile.get_density_array()
        self.variant_length_scale = self.profile.get_length_scale_array()
        self.variant_intensity = self.profile.get_intensity_array()

        if np.any(self.variant_length_scale * 2 > np.min(self.dimensions)):
            raise ValueError(
                "Eddy length scales are too large compared to field dimensions"
            )

        # Total volume of the flow field
        volume = np.prod(self.dimensions)

        # Number of eddies of each variant due to density
        self.variant_quantity = utils.stoch_round(self.variant_density * volume)

        # Total number of eddies
        self.N = np.sum(self.variant_quantity)

        # Length scales of each eddy
        self.sigma = np.repeat(self.variant_length_scale, self.variant_quantity)

        # Boundaries of the flow field
        self.low_bounds = -self.dimensions / 2
        self.high_bounds = self.dimensions / 2

        # Random center positions of the eddies
        self.init_x = np.random.uniform(self.low_bounds[0], self.high_bounds[0], self.N)
        self.y = {}
        self.z = {}
        self.set_rand_eddy_yz(0)
        self.set_rand_eddy_yz(1)
        self.set_rand_eddy_yz(2)

        self.alpha = utils.random_unit_vectors(self.N) * np.repeat(
            self.variant_intensity, self.variant_quantity
        ).reshape(-1, 1)

        print("Total eddies: ", self.N)

    def get_eddy_centers(self, fi: int):
        """Get the x, y, and z coordinates of the eddies in a flow iteration."""
        if fi not in self.y:
            self.set_rand_eddy_yz(fi)
        return np.stack((self.init_x, self.y[fi], self.z[fi]), axis=-1)

    def set_rand_eddy_yz(self, fi: int):
        """Set random y and z coordinates for eddies in a new flow iteration."""
        self.y[fi] = np.random.uniform(self.low_bounds[1], self.high_bounds[1], self.N)
        self.z[fi] = np.random.uniform(self.low_bounds[2], self.high_bounds[2], self.N)

    def sum_vel_mesh(
        self,
        low_bounds: np.ndarray | list = None,
        high_bounds: np.ndarray | list = None,
        step_size: float = 0.2,
        chunk_size: int = 5,
        t: float = 0,
        do_return: bool = True,
        do_cache: bool = False,
    ):
        """
        Calculate the velocity field for a meshgrid.

        Parameters
        ----------
        `low_bounds` : np.ndarray or list, optional
            Lower bounds of the meshgrid, by default low bounds of the whole field
        `high_bounds` : np.ndarray or list, optional
            Upper bounds of the meshgrid, by default high bounds of the whole field
        `step_size` : float, optional
            Step size of the meshgrid, by default 0.2
        `chunk_size` : int, optional
            Size of chunks to split the meshgrid into, by default 5
        `t` : float, optional
            Time passed, by default 0
        `do_return` : bool, optional
            Return the velocity field, by default True
        `do_cache` : bool, optional
            Save chunks cache, by default False

        Returns
        -------
        `vel`: np.ndarray
            Velocity field for the meshgrid
        """
        if low_bounds is None:
            low_bounds = self.low_bounds
        if high_bounds is None:
            high_bounds = self.high_bounds
        if isinstance(low_bounds, list) and isinstance(high_bounds, list):
            high_bounds = np.array(high_bounds)
            low_bounds = np.array(low_bounds)

        if not (
            isinstance(low_bounds, np.ndarray) and isinstance(high_bounds, np.ndarray)
        ):
            raise ValueError("Bounds must be lists or numpy arrays")

        if not (low_bounds.shape == (3,) and high_bounds.shape == (3,)):
            raise ValueError("Bounds must contain 3 elements (x, y, z) each")

        if not np.all(low_bounds <= high_bounds):
            raise ValueError("Low bounds cannot be greater than high bounds")

        if not utils.is_positive(step_size):
            raise ValueError("Step size must be a positive number")

        if not utils.is_not_negative(chunk_size):
            raise ValueError(
                "Chunk size not be negative. Use zero for no chunking (Potentially SLOW and HIGH memory usage!!!)"
            )

        if not utils.is_not_negative(t):
            raise ValueError("Time non-negative number, by default 0.0")

        # Generate arrays of x, y, and z coordinates
        x_coords = self.step_coords(low_bounds[0], high_bounds[0], step_size)
        y_coords = self.step_coords(low_bounds[1], high_bounds[1], step_size)
        z_coords = self.step_coords(low_bounds[2], high_bounds[2], step_size)

        # Initialize the velocity field if a return is needed
        if do_return:
            try:
                vel = np.zeros((len(x_coords), len(y_coords), len(z_coords), 3))
            except MemoryError as e:
                raise MemoryError(
                    f"{e}\nNot enough memory to allocate velocity field. "
                    "Consider using a larger step size or focus on a smaller region."
                ) from e
            vel[..., 0] = self.avg_vel

        # Divide the coordinates into chunks
        if chunk_size == 0:
            chunk_size = np.max([len(x_coords), len(y_coords), len(z_coords)])
            # chunk_size = 1
        x_chunks = self.chunk_split(np.arange(len(x_coords)), chunk_size)
        y_chunks = self.chunk_split(np.arange(len(y_coords)), chunk_size)
        z_chunks = self.chunk_split(np.arange(len(z_coords)), chunk_size)

        # Clear previous chunk cache
        file_io.clear_cache("chunks")

        # Get all eddies and their wrapped-around copies
        centers, alpha, sigma = self.get_wrap_arounds(t, high_bounds, low_bounds)
        print("Included eddies: ", centers.shape[0])
        # Save chunk information for future loading
        chunk_info = {
            "low_bounds": low_bounds.tolist(),
            "high_bounds": high_bounds.tolist(),
            "step_size": step_size,
            "indices": {
                "x": [[int(part[0]), int(part[-1])] for part in x_chunks],
                "y": [[int(part[0]), int(part[-1])] for part in y_chunks],
                "z": [[int(part[0]), int(part[-1])] for part in z_chunks],
            },
        }

        file_io.write(".cache/chunks", "__info__", chunk_info)

        # Calculate the velocity field for each chunk
        margins = sigma * CUTOFF
        print("Chunks [x, y, z]: ", [len(x_chunks), len(y_chunks), len(z_chunks)])
        pbar = tqdm(total=len(x_chunks) * len(y_chunks) * len(z_chunks))
        for i, xc in enumerate(x_chunks):
            vel_i = np.zeros((len(xc), len(y_coords), len(z_coords), 3))
            vel_i[..., 0] = self.avg_vel
            mask = self.within_margin(
                centers[:, 0], margins, x_coords[xc[0]], x_coords[xc[-1]]
            )
            centers_i = centers[mask]
            sigma_i = sigma[mask]
            alpha_i = alpha[mask]
            margins_i = margins[mask]
            for j, yc in enumerate(y_chunks):
                mask = self.within_margin(
                    centers_i[:, 1], margins_i, y_coords[yc[0]], y_coords[yc[-1]]
                )
                centers_j = centers_i[mask]
                sigma_j = sigma_i[mask]
                alpha_j = alpha_i[mask]
                margins_j = margins_i[mask]
                for k, zc in enumerate(z_chunks):
                    mask = self.within_margin(
                        centers_j[:, 2], margins_j, z_coords[zc[0]], z_coords[zc[-1]]
                    )
                    centers_k = centers_j[mask]
                    sigma_k = sigma_j[mask]
                    alpha_k = alpha_j[mask]
                    vel_i[
                        :,
                        yc[0] : yc[-1] + 1,
                        zc[0] : zc[-1] + 1,
                        :,
                    ] += self.sum_vel_chunk(
                        centers_k,
                        sigma_k,
                        alpha_k,
                        x_coords[xc],
                        y_coords[yc],
                        z_coords[zc],
                    )
                    # file_io.write_cache("chunks", f"{i}_{j}_{k}", vel)
                    pbar.update(1)
            if do_return:
                vel[xc[0] : xc[-1] + 1, :, :, :] = vel_i
            if do_cache:
                file_io.write_cache("chunks", f"x_{i}", vel)
        pbar.close()

        if do_return:
            return vel

    def sum_vel_chunk(
        self,
        centers: np.ndarray,
        sigma: np.ndarray,
        alpha: np.ndarray,
        x_coords: np.ndarray,
        y_coords: np.ndarray,
        z_coords: np.ndarray,
    ):
        """Calculate the velocity field within a chunk."""
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
        except MemoryError as e:
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

    def get_iter(self, t: float):
        """Get the current flow iteration based on the time passed."""
        return round(self.avg_vel * t / self.dimensions[0]) + 1

    def get_offset(self, t: float):
        """Get the x-offset of the flow field based on the time passed."""
        Lx = self.dimensions[0]
        offset = self.avg_vel * t % Lx
        offset = offset - Lx if offset > Lx / 2 else offset
        return offset

    def get_wrap_arounds(
        self, t: float, high_bounds: np.ndarray, low_bounds: np.ndarray
    ):
        """
        Get all eddies and their wrapped-around copies if any.
        Returns the centers, alpha, and sigma of the eddies that are within the bounds (including margins).
        """
        # Current flow iteration and x-offset
        flow_iter = self.get_iter(t)
        offset = self.get_offset(t)

        # Get all eddies and their wrapped-around copies if any
        wrapped_centers = [np.empty(0)] * 27
        wrapped_alpha = [np.empty(0)] * 27
        wrapped_sigma = [np.empty(0)] * 27
        w = 0
        # Wrap around for the x coordinates
        margin = self.sigma * CUTOFF
        for i in WRAP_ITER:
            centers = self.get_eddy_centers(flow_iter + i)
            centers[:, 0] += offset - i * self.dimensions[0]
            # Wrap around for the y and z coordinates
            for j in WRAP_ITER:
                for k in WRAP_ITER:
                    centers_wrap = centers + np.array(
                        [0, j * self.dimensions[1], k * self.dimensions[2]]
                    )
                    mask = self.within_margin(
                        centers_wrap[:, 1], margin, low_bounds[1], high_bounds[1]
                    )
                    mask[mask] = self.within_margin(
                        centers_wrap[:, 2][mask],
                        margin[mask],
                        low_bounds[2],
                        high_bounds[2],
                    )
                    mask[mask] = self.within_margin(
                        centers_wrap[:, 0][mask],
                        margin[mask],
                        low_bounds[0],
                        high_bounds[0],
                    )
                    wrapped_centers[w] = centers_wrap[mask]
                    wrapped_alpha[w] = self.alpha[mask]
                    wrapped_sigma[w] = self.sigma[mask]
                    w += 1

        wrapped_centers = np.concatenate(wrapped_centers)
        wrapped_alpha = np.concatenate(wrapped_alpha)
        wrapped_sigma = np.concatenate(wrapped_sigma)

        return wrapped_centers, wrapped_alpha, wrapped_sigma

    def within_margin(
        self,
        values: np.ndarray,
        margins: np.ndarray,
        low_bound: float,
        high_bound: float,
    ):
        """
        Check if values are within the bounds, or outside but within the margins.
        The number of values and margins must be match.
        """
        return (values < high_bound + margins) & (values > low_bound - margins)

    def step_coords(self, low_bounds, high_bounds, step_size):
        """Generate an array of coordinates with a given step size."""
        coords = np.arange(low_bounds, high_bounds + step_size, step_size)
        return coords[:-1] if coords[-1] > high_bounds else coords

    def chunk_split(self, array: np.ndarray, chunk_size):
        """Split an array into chunks of a given size."""
        if len(array) == 1:
            return [array]
        chunks = [array[i : i + chunk_size] for i in range(0, len(array), chunk_size)]
        if len(chunks[-1]) == 1:
            chunks[-2] = np.append(chunks[-2], chunks[-1])
            chunks.pop(-1)
        return chunks
