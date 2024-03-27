"""POC of broadcasting in numpy"""

import time
import numpy as np
from itertools import combinations, product
import matplotlib.pyplot as plt


def expanded_inbounds(centers, length_scales, low_bounds, high_bounds=None):
    if high_bounds is None:
        high_bounds = -low_bounds

    length_scales = length_scales.reshape(-1, 1)
    low_bounds = low_bounds.reshape(-1, 3)
    high_bounds = high_bounds.reshape(-1, 3)
    print("Centers: ", centers.shape)
    print("Length scales: ", length_scales.shape)
    print("High bounds: ", high_bounds.shape)
    print("Low bounds: ", low_bounds.shape)
    # print("High bounds expanded: ", (high_bounds + length_scales))
    # print("High bounds comparison: ", (centers < high_bounds + length_scales))
    return np.all(
        (centers > low_bounds - length_scales)
        & (centers < high_bounds + length_scales),
        axis=-1,
    )


def my_function(x):
    """Placeholder function"""
    return x


# Define the number of centers
start_time = time.time()
NUM_CENTERS = 20

# Create random centers, length_scale, and orientations of the spheres
centers = (
    np.random.rand(NUM_CENTERS, 3) * 200 - 100
)  # Random centers in the range [-10, 10]
length_scales = (
    np.random.rand(NUM_CENTERS) * 200
)  # Random length scales in the range [0, 10]
length_scales = np.repeat(5, NUM_CENTERS)
orientations = np.random.rand(NUM_CENTERS, 3)  # Random orientations in the range [0, 1]
print("Time taken for creating eddies: ", time.time() - start_time)

print("Centers: ", centers.shape)

# Define the range and step size
Lx, Ly, Lz = 200, 200, 200
STEP = 1

# Calculate the number of points
Nx, Ny, Nz = int(Lx / STEP) + 1, int(Ly / STEP) + 1, int(Lz / STEP) + 1

# Generate arrays of x, y, and z coordinates
x_coords = np.linspace(-Lx / 2, Lx / 2, Nx)
y_coords = np.linspace(-Ly / 2, Ly / 2, Ny)
z_coords = np.linspace(-Lz / 2, Lz / 2, Nz)

# Divide the coordinates into 4 parts
x_parts = np.array_split(x_coords, 2)
y_parts = np.array_split(y_coords, 2)
z_parts = np.array_split(z_coords, 2)

cx, cy, cz = 0, 0, 0

# Create a meshgrid of x, y, and z coordinates
positions = np.transpose(
    np.meshgrid(x_parts[cx], y_parts[cy], z_parts[cz]), (1, 2, 3, 0)
)
print("Positions: ", positions.shape)

print("Time taken for creating positions: ", time.time() - start_time)


# Get the minimum and maximum coordinates of the current part box
low_bounds = positions[0, 0, 0]
high_bounds = positions[-1, -1, -1]

# Find the centers that are inside or touching the box
mask = expanded_inbounds(centers, length_scales, low_bounds, high_bounds)
print("Mask: ", mask)

# Apply the mask to get the centers that are inside or touching the box
centers = centers[mask]
length_scales = length_scales[mask]
orientations = orientations[mask]
print("Centers: ", centers.shape)

# Reshape the centers, length_scale, and orientations arrays to allow broadcasting
centers = centers.reshape(-1, 1, 1, 1, 3)
length_scales = length_scales.reshape(-1, 1, 1, 1, 1)
orientations = orientations.reshape(-1, 1, 1, 1, 3)

# Calculate the relative position vectors
start_time = time.time()
rk = positions - centers / length_scales
print(
    "Time taken for calculating relative position vectors: ", time.time() - start_time
)

# Calculate the Euclidean distance
start_time = time.time()
dk = np.sqrt(np.sum(rk**2, axis=-1))
print("Time taken for calculating distances: ", time.time() - start_time)

# Create a mask for those nodes where dk <= 1
# mask = dk <= 1

# Calculate the cross product between the normalized relative position vectors and the orientations
# only for those nodes where dk <= 1
start_time = time.time()
cross_product = np.empty_like(rk)
# for i in range(len(centers)):
#     cross_product[i][mask[i]] = np.cross(rk[i][mask[i]], orientations[i])
cross_product = np.cross(rk, orientations)
print("Time taken for calculating cross product: ", time.time() - start_time)

# Apply the function to the cross product of the nodes that are inside the spheres
start_time = time.time()
result = my_function(cross_product)
print("Time taken for applying function: ", time.time() - start_time)

# Sum up the results for all points at each grid node
start_time = time.time()
sum_result = np.sum(result, axis=0)
print("Time taken for summing up results: ", time.time() - start_time)


# Reshape centers to 2D
centers_2d = centers.reshape(-1, 3)

# Create a new figure
fig = plt.figure()

# Add a 3D subplot
ax = fig.add_subplot(111, projection="3d")

# Plot the centers
ax.scatter(centers_2d[:, 0], centers_2d[:, 1], centers_2d[:, 2], color="blue")

# Create a list of all corners of the box
corners = (
    np.array([p for p in product([0, 1], repeat=3)]) * (high_bounds - low_bounds)
    + low_bounds
)

# Plot the lines connecting the corners to form the box
for s, e in combinations(corners, 2):
    if (
        np.linalg.norm(s - e) == high_bounds[0] - low_bounds[0]
        or np.linalg.norm(s - e) == high_bounds[1] - low_bounds[1]
        or np.linalg.norm(s - e) == high_bounds[2] - low_bounds[2]
    ):
        ax.plot(*zip(s, e), color="r")


# Set the labels
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

# Show the plot
plt.show()
