"""
Turbulent Flow Field Module
"""

# import time
from tqdm import tqdm
import numpy as np
from modules import utils
from modules import file_io
from modules import shape_function
from modules import eddy
from modules.eddy_profile import EddyProfile

WRAP_ITER = [-1, 0, 1]  # Iterations to wrap around the flow field, do not change
CUTOFF = 1.2 * shape_function.get_cutoff()  # has to be greater than 1
CACHE_DIR = ".cache"
CACHE_FORMAT = "npy"


class FlowField:
    """
    Flow field class with eddies within.
    Contains methods to calculate the velocity at any point in the field.
    """

    verbose = True  # Show prints and progress bar

    def __init__(
        self,
        profile: EddyProfile,
        name: str,
        dimensions: np.ndarray | list,
        avg_vel: float | int = 0,
    ):
        """
        Generate a new flow field.

        Note that this object only contains the eddy positions and properties,
        not a specific meshgrid.
        That is privided by the when querying with `sum_vel_mesh` method.

        Dimensions are in the form of `[x, y, z]`.
        - `x` is the direction of the flow
        - `y` is the direction of the width
        - `z` is the direction of the height

        Coordinates are centered at `[0, 0, 0]`

        Bounds are from `-dimensions/2` to `dimensions/2`

        Parameters
        ----------
        `profile` : EddyProfile
            Eddy profile object
        `name` : str
            Name of the flow field
        `dimensions` : np.ndarray or list
            Dimensions of the the form of `[x, y, z]`
        `avg_vel` : float, optional (default: `0.0`)
            Average flow velocity to move the eddies
        """
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
        self.name = str(name)
        self.dimensions = dimensions
        self.avg_vel = avg_vel

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

        # if avg_vel is zero, wrap around in x will be the same method as in y and z (exact coordinates)
        if self.avg_vel == 0:
            self.y[1] = self.y[0]
            self.z[1] = self.z[0]
            self.y[2] = self.y[0]
            self.z[2] = self.z[0]
        # if avg_vel is not zero, wrap around in x will have random y and z to avoid periodicity
        else:
            self.set_rand_eddy_yz(1)
            self.set_rand_eddy_yz(2)

        self.alpha = utils.random_unit_vectors(self.N) * np.repeat(
            self.variant_intensity, self.variant_quantity
        ).reshape(-1, 1)

        # self.save()

        self.print("Total eddies: ", self.N)

    def get_eddy_centers(self, fi: int):
        """Get the x, y, and z coordinates of the eddies in a flow iteration."""
        if fi not in self.y:
            self.set_rand_eddy_yz(fi)
        return np.stack((self.init_x, self.y[fi], self.z[fi]), axis=-1)

    def set_rand_eddy_yz(self, fi: int):
        """Set random y and z coordinates for eddies in a new flow iteration."""
        self.y[fi] = np.random.uniform(self.low_bounds[1], self.high_bounds[1], self.N)
        self.z[fi] = np.random.uniform(self.low_bounds[2], self.high_bounds[2], self.N)

    def set_avg_vel(self, avg_vel: float):
        """Set the average velocity of the flow field."""
        if not utils.is_not_negative(avg_vel):
            raise ValueError("Average velocity must be a non-negative number")
        self.avg_vel = avg_vel

    def save(self):
        """Save the flow field to a file."""
        file_io.write("fields", self.name, self, "obj")

    def sum_vel_mesh(
        self,
        low_bounds: np.ndarray | list = None,
        high_bounds: np.ndarray | list = None,
        step_size: float = 0.2,
        chunk_size: int = 5,
        time: float = 0,
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

        if np.any(low_bounds < self.low_bounds) or np.any(high_bounds > self.high_bounds):
            raise ValueError("Bounds must be within the flow field")

        if not utils.is_positive(step_size):
            raise ValueError("Step size must be a positive number")

        if not utils.is_not_negative(chunk_size):
            raise ValueError(
                "Chunk size not be negative. Use zero for no chunking (Potentially SLOW and HIGH memory usage!!!)"
            )

        if not utils.is_not_negative(time):
            raise ValueError("Time must be non-negative number, by default 0.0")

        # Generate arrays of x, y, and z coordinates
        x_coords = self.step_coords(low_bounds[0], high_bounds[0], step_size)
        y_coords = self.step_coords(low_bounds[1], high_bounds[1], step_size)
        z_coords = self.step_coords(low_bounds[2], high_bounds[2], step_size)

        # Initialize the velocity field if a return is needed
        if do_return:
            try:
                vel = np.zeros((len(x_coords), len(y_coords), len(z_coords), 3))
            except MemoryError as e:  # pragma: no cover
                raise MemoryError(
                    f"{e}\nNot enough memory to allocate velocity field. "
                    "Consider using a larger step size or focus on a smaller region."
                ) from e
            vel[..., 0] = self.avg_vel

        # Divide the coordinates into chunks
        if chunk_size == 0:     # pragma: no cover
            chunk_size = np.max([len(x_coords), len(y_coords), len(z_coords)])
            # chunk_size = 1
        x_chunks = self.chunk_split(np.arange(len(x_coords)), chunk_size)
        y_chunks = self.chunk_split(np.arange(len(y_coords)), chunk_size)
        z_chunks = self.chunk_split(np.arange(len(z_coords)), chunk_size)

        # Clear previous chunk cache
        file_io.clear(CACHE_DIR)

        # Get all eddies and their wrapped-around copies
        centers, alpha, sigma = self.get_wrap_arounds(time, high_bounds, low_bounds)
        self.print("Included eddies: ", centers.shape[0])
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

        file_io.write(CACHE_DIR, "__info__", chunk_info, "json")

        # Calculate the velocity field for each chunk, slicing by x, y, and z
        margins = sigma * CUTOFF
        self.print("Chunks [x, y, z]: ", [len(x_chunks), len(y_chunks), len(z_chunks)])
        if self.verbose:
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
            for _, yc in enumerate(y_chunks):
                mask = self.within_margin(
                    centers_i[:, 1], margins_i, y_coords[yc[0]], y_coords[yc[-1]]
                )
                centers_j = centers_i[mask]
                sigma_j = sigma_i[mask]
                alpha_j = alpha_i[mask]
                margins_j = margins_i[mask]
                for _, zc in enumerate(z_chunks):
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
                    ] += eddy.sum_vel_chunk(
                        centers_k,
                        sigma_k,
                        alpha_k,
                        x_coords[xc],
                        y_coords[yc],
                        z_coords[zc],
                    )
                    if self.verbose:
                        pbar.update(1)
            if do_return:
                vel[xc[0] : xc[-1] + 1, :, :, :] = vel_i
            if do_cache:
                file_io.write(CACHE_DIR, f"x_{i}", vel_i, CACHE_FORMAT)

        if self.verbose:
            pbar.close()

        if do_return:
            return vel

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

    @classmethod
    def load(cls, name: str):
        """Load a flow field from a file."""
        return file_io.read("fields", name, "obj")

    @classmethod
    def print(cls, *content):
        """Print content if verbose is enabled."""
        if cls.verbose:
            print(*content)
