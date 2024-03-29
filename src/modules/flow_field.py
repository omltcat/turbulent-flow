"""
Turbulent Flow Field Module
"""

from tqdm import tqdm
import numpy as np
from modules import utils
from modules import file_io
from modules import shape_function
from modules.eddy_profile import EddyProfile

WRAP_ITER = [-1, 0, 1]
CUTOFF_MARGIN = 0.2


class FlowField:
    """
    Flow field class with eddies within.
    Contains methods to calculate the velocity at any point in the field.
    """

    def __init__(
        self,
        profile: EddyProfile,
        name: str,
        dimensions: np.ndarray,
        avg_vel: float,
    ):
        """Initialize the flow field with the given parameters."""
        # Check for invalid inputs
        if not isinstance(dimensions, np.ndarray) or dimensions.shape != (3,):
            raise ValueError("Dimensions must be a 3D numpy array")
        if np.any(dimensions <= 0):
            raise ValueError("Dimensions must be positive")
        if not utils.is_positive(avg_vel):
            raise ValueError("Average velocity must be a positive number")

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
        low_bounds: np.ndarray = None,
        high_bounds: np.ndarray = None,
        step_size: float = 0.02,
        chunk_size: int = 5,
        time: float = 0,
    ):
        """Calculate the velocity field for a meshgrid."""
        if low_bounds is None:
            low_bounds = self.low_bounds
        if high_bounds is None:
            high_bounds = self.high_bounds
        high_bounds = np.array(high_bounds)
        low_bounds = np.array(low_bounds)

        # Generate arrays of x, y, and z coordinates
        x_coords = self.step_coords(low_bounds[0], high_bounds[0], step_size)
        y_coords = self.step_coords(low_bounds[1], high_bounds[1], step_size)
        z_coords = self.step_coords(low_bounds[2], high_bounds[2], step_size)

        vel = np.zeros((len(x_coords), len(y_coords), len(z_coords), 3))
        vel[..., 0] = self.avg_vel

        # Divide the coordinates into chunks
        x_chunks = self.chunk_split(np.arange(len(x_coords)), chunk_size)
        y_chunks = self.chunk_split(np.arange(len(y_coords)), chunk_size)
        z_chunks = self.chunk_split(np.arange(len(z_coords)), chunk_size)

        # Clear previous chunk cache
        file_io.clear_cache("chunks")

        # Get all eddies and their wrapped-around copies
        centers, alpha, sigma = self.get_wrap_arounds(time, high_bounds, low_bounds)
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
        cutoff = sigma * (1 + CUTOFF_MARGIN) * shape_function.get_cutoff()
        print("Chunks [x, y, z]: ", [len(x_chunks), len(y_chunks), len(z_chunks)])
        pbar = tqdm(total=len(x_chunks) * len(y_chunks) * len(z_chunks))
        for i, xc in enumerate(x_chunks):
            # Progresively filter out eddies that are not in the chunk
            mask = centers[:, 0] < x_coords[xc[-1]] + cutoff
            mask[mask] = centers[:, 0][mask] > x_coords[xc[0]] - cutoff[mask]
            centers_i = centers[mask]
            sigma_i = sigma[mask]
            alpha_i = alpha[mask]
            cutoff_i = cutoff[mask]
            for j, yc in enumerate(y_chunks):
                mask = centers_i[:, 1] < y_coords[yc[-1]] + cutoff_i
                mask[mask] = centers_i[:, 1][mask] > y_coords[yc[0]] - cutoff_i[mask]
                centers_j = centers_i[mask]
                sigma_j = sigma_i[mask]
                alpha_j = alpha_i[mask]
                cutoff_j = cutoff_i[mask]
                for k, zc in enumerate(z_chunks):
                    mask = centers_j[:, 2] < z_coords[zc[-1]] + cutoff_j
                    mask[mask] = (
                        centers_j[:, 2][mask] > z_coords[zc[0]] - cutoff_j[mask]
                    )
                    centers_k = centers_j[mask]
                    sigma_k = sigma_j[mask]
                    alpha_k = alpha_j[mask]
                    vel[
                        xc[0] : xc[-1] + 1,
                        yc[0] : yc[-1] + 1,
                        zc[0] : zc[-1] + 1,
                        :,
                    ] = self.sum_vel_chunk(
                        centers_k,
                        sigma_k,
                        alpha_k,
                        x_coords[xc],
                        y_coords[yc],
                        z_coords[zc],
                    )
                    # file_io.write_cache("chunks", f"{i}_{j}_{k}", vel)
                    pbar.update(1)
        pbar.close()

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
        X, Y, Z = np.meshgrid(x_coords, y_coords, z_coords, indexing="ij")
        positions = np.stack((X, Y, Z), axis=-1)[np.newaxis, ...]
        del X, Y, Z

        # Get the minimum and maximum coordinates of the current chunk box
        # low_bounds = positions[0, 0, 0]
        # high_bounds = positions[-1, -1, -1]
        # print("Time for creating positions: ", time.time() - start_time)

        # Check if the eddies are touching the box
        # start_time = time.time()
        # mask = self.expanded_inbounds(centers, sigma, low_bounds, high_bounds)
        chunk_centers = centers.reshape(-1, 1, 1, 1, 3)
        chunk_alpha = alpha.reshape(-1, 1, 1, 1, 3)
        chunk_sigma = sigma.reshape(-1, 1, 1, 1, 1)
        # return np.mean(chunk_centers[..., 1])
        # print("Time for checking inbounds: ", time.time() - start_time)

        # Calculate the relative position vectors
        # time_start = time.time()
        rk = (positions - chunk_centers) / chunk_sigma
        # return np.mean(rk[..., 1], axis=0)[..., np.newaxis]
        del positions
        del chunk_centers
        # print("Time for calculating relative position vectors: ", time.time() - time_start)

        # Calculate the Euclidean distance
        # time_start = time.time()
        dk = np.linalg.norm(rk, axis=-1)[..., np.newaxis]
        # return np.mean(rk[..., 0], axis=0)[..., np.newaxis]
        # print("Time for calculating distances: ", time.time() - time_start)

        # Calculate cross product
        # time_start = time.time()
        cross_product = np.cross(rk, chunk_alpha)
        del rk
        del chunk_alpha
        # print("Time for calculating cross product: ", time.time() - time_start)

        # Apply the shape function
        # time_start = time.time()
        shape = shape_function.active(dk, chunk_sigma)
        # plt.imshow(np.squeeze(np.sum(shape, axis=0)), cmap='hot', interpolation='nearest')
        # plt.show()
        del dk
        del chunk_sigma
        # print("Time for applying shape function: ", time.time() - time_start)

        # Calculate the velocity fluctuations
        # time_start = time.time()
        vel_fluct = shape * cross_product
        # print(cross_product)
        vel_fluct = np.sum(vel_fluct, axis=0)
        del shape
        del cross_product
        # print("Time for calculating velocity fluctuations: ", time.time() - time_start)

        # print(vel_fluct.shape)

        # X, Y, Z = np.meshgrid(x_coords, y_coords, z_coords, indexing="ij")
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.quiver(
        #     X,
        #     Y,
        #     vel_fluct[:, :, 0, 0],
        #     vel_fluct[:, :, 0, 1],
        # )
        # plt.show()

        return vel_fluct

    def get_iter(self, time: float):
        """Get the current flow iteration based on the time passed."""
        return round(self.avg_vel * time / self.dimensions[0]) + 1

    def get_offset(self, time: float):
        """Get the x-offset of the flow field based on the time passed."""
        Lx = self.dimensions[0]
        offset = self.avg_vel * time % Lx
        offset = offset - Lx if offset > Lx / 2 else offset
        return offset

    def get_wrap_arounds(
        self, time: float, high_bounds: np.ndarray, low_bounds: np.ndarray
    ):
        """Get all eddies and their wrapped-around copies if any."""
        # Current flow iteration and x-offset
        flow_iter = self.get_iter(time)
        offset = self.get_offset(time)

        # Get all eddies and their wrapped-around copies if any
        wrapped_centers = [np.empty(0)] * 27
        wrapped_alpha = [np.empty(0)] * 27
        wrapped_sigma = [np.empty(0)] * 27
        w = 0
        # Wrap around for the x coordinates
        cutoff = self.sigma * (1 + CUTOFF_MARGIN) * shape_function.get_cutoff()
        for i in WRAP_ITER:
            centers = self.get_eddy_centers(flow_iter + i)
            centers[:, 0] += offset - i * self.dimensions[0]
            # Wrap around for the y and z coordinates
            for j in WRAP_ITER:
                for k in WRAP_ITER:
                    centers_wrap = centers + np.array(
                        [0, j * self.dimensions[1], k * self.dimensions[2]]
                    )
                    mask = self.expanded_inbounds(
                        centers_wrap, cutoff, low_bounds, high_bounds
                    )
                    wrapped_centers[w] = centers_wrap[mask]
                    wrapped_alpha[w] = self.alpha[mask]
                    wrapped_sigma[w] = self.sigma[mask]
                    w += 1

        wrapped_centers = np.concatenate(wrapped_centers)
        wrapped_alpha = np.concatenate(wrapped_alpha)
        wrapped_sigma = np.concatenate(wrapped_sigma)

        return wrapped_centers, wrapped_alpha, wrapped_sigma

    def expanded_inbounds(
        self,
        centers: np.ndarray,
        cutoff: np.ndarray,
        low_bounds: np.ndarray,
        high_bounds: np.ndarray,
    ):
        """
        Check for eddies either within the bounds of box, or outside but partially touching the box.

        Parameters:
        centers (np.ndarray): Centers of the eddies.
        length_scales (np.ndarray): Length scales of the eddies.
        low_bounds (np.ndarray): [x, y, z] lower bounds of the box.
        high_bounds (np.ndarray): [x, y, z] upper bounds of the box.

        Returns:
        np.ndarray: Boolean array indicating if the eddies are within the bounds of the box.
        """

        if not (
            isinstance(low_bounds, (np.ndarray, list))
            and isinstance(high_bounds, (np.ndarray, list))
        ):
            raise ValueError("Bounds must be a list or a numpy array.")

        # length_scales = length_scales.reshape(-1, 1)
        # low_bounds = low_bounds.reshape(-1, 3)
        # high_bounds = high_bounds.reshape(-1, 3)
        # print(centers[:, 0].shape, high_bounds.shape, length_scales.shape)
        cutoff = cutoff * 3
        mask = centers[:, 0] < high_bounds[0] + cutoff
        mask[mask] = centers[:, 0][mask] > low_bounds[0] - cutoff[mask]
        mask[mask] = centers[:, 1][mask] < high_bounds[1] + cutoff[mask]
        mask[mask] = centers[:, 1][mask] > low_bounds[1] - cutoff[mask]
        mask[mask] = centers[:, 2][mask] < high_bounds[2] + cutoff[mask]
        mask[mask] = centers[:, 2][mask] > low_bounds[2] - cutoff[mask]

        return mask

    def step_coords(self, low_bounds, high_bounds, step_size):
        """Generate an array of coordinates with a given step size."""
        coords = np.arange(low_bounds, high_bounds + step_size, step_size)
        return coords[:-1] if coords[-1] > high_bounds else coords

    def chunk_split(self, array: np.ndarray | list, chunk_size):
        """Split an array into chunks of a given size."""
        if len(array) == 1:
            return [array]
        chunks = [array[i : i + chunk_size] for i in range(0, len(array), chunk_size)]
        if len(chunks[-1]) == 1:
            if isinstance(chunks[-2], np.ndarray):
                chunks[-2] = np.append(chunks[-2], chunks[-1])
            else:
                chunks[-2].extend(chunks[-1])
            chunks.pop(-1)
        return chunks
