import numpy as np
import matplotlib.pyplot as plt

HALF_PI = 0.5 * np.pi
C = 3.6276
cutoff = 2.0


def step_coords(low_bounds, high_bounds, step_size):
    """Generate an array of coordinates with a given step size."""
    coords = np.arange(low_bounds, high_bounds + step_size, step_size)
    return coords[:-1] if coords[-1] > high_bounds else coords


def gaussian(dk, length_scale):
    """Gaussian shape function"""
    return np.where(
        dk < cutoff,
        C * np.exp(-HALF_PI * dk**2),
        0
    )


# Eddy parameters
gamma = np.array([1.5])
sigma = np.array([1.5])
intensity = np.array([1.15])
center = np.array([0.0, 0.0, 0.0])

# orient = utils.random_unit_vectors(1)
# orient = np.array([0.7071, 0.7071, 0.0])
orient = np.array([0.57735027, 0.57735027, 0.57735027])
# orient = np.array([1.0, 0.0, 0.0])
alpha = intensity * orient

sigma_a = gamma ** (2 / 3) * sigma
sigma_r = gamma ** (-1 / 3) * sigma
sigma = np.maximum(sigma_a, sigma_r)

# Generate arrays of x, y, and z coordinates
low_bounds = np.array([-5.0, -5.0, -5.0])
high_bounds = np.array([5.0, 5.0, 5.0])
step_size = 1

x_coords = step_coords(low_bounds[0], high_bounds[0], step_size)
y_coords = step_coords(low_bounds[1], high_bounds[1], step_size)
z_coords = step_coords(low_bounds[2], high_bounds[2], step_size)


# Calculate velocity field
positions = np.stack(
    np.meshgrid(x_coords, y_coords, z_coords, indexing="ij"), axis=-1
)[np.newaxis, ...]

centers = center.reshape(-1, 1, 1, 1, 3)
orient = orient.reshape(-1, 1, 1, 1, 3)
alpha = alpha.reshape(-1, 1, 1, 1, 3)
sigma = sigma.reshape(-1, 1, 1, 1, 1)
sigma_a = sigma_a.reshape(-1, 1, 1, 1, 1)
sigma_r = sigma_r.reshape(-1, 1, 1, 1, 1)

# Relative position vectors
rel_vec = positions - centers

# Axial position component
rel_vec_a: np.ndarray = np.sum(np.multiply(rel_vec, orient), axis=-1)[..., np.newaxis] * orient

# Radial position component
rel_vec_r = rel_vec - rel_vec_a

# Axial and radial r components
rk_a = rel_vec_a / sigma_a
rk_r = rel_vec_r / sigma_r
rk = rk_a + rk_r

dk = np.linalg.norm(rk, axis=-1)[..., np.newaxis]

# Velocity fluctuation field
vel_fluct = gaussian(dk, sigma) * np.cross(-rk, alpha)
vel_fluct = np.sum(vel_fluct, axis=0)


# Plot velocity field 3D
x = positions[..., 0]
y = positions[..., 1]
z = positions[..., 2]

u = vel_fluct[..., 0]
v = vel_fluct[..., 1]
w = vel_fluct[..., 2]

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.quiver(x, y, z, u, v, w, length=0.2, normalize=True)
ax.set_xlim(low_bounds[0], high_bounds[0])
ax.set_ylim(low_bounds[1], high_bounds[1])
ax.set_zlim(low_bounds[2], high_bounds[2])
ax.set_box_aspect([1, 1, 1])
plt.show()
