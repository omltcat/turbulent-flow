"""POC of broadcasting in numpy"""

import time
import numpy as np


def my_function(x):
    """Placeholder function"""
    return x


# Define the number of centers
start_time = time.time()
NUM_CENTERS = 1000

# Create random centers, length_scale, and orientations of the spheres
centers = (
    np.random.rand(NUM_CENTERS, 3) * 200 - 100
)  # Random centers in the range [-10, 10]
length_scale = (
    np.random.rand(NUM_CENTERS) * 10
)  # Random length scales in the range [0, 10]
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
x_parts = np.array_split(x_coords, 4)
y_parts = np.array_split(y_coords, 4)
z_parts = np.array_split(z_coords, 4)

cx, cy, cz = 2, 2, 2

# Create a meshgrid of x, y, and z coordinates
positions = np.transpose(
    np.meshgrid(x_parts[cx], y_parts[cy], z_parts[cz]), (1, 2, 3, 0)
)

print("Time taken for creating positions: ", time.time() - start_time)


# Get the minimum and maximum coordinates of the current part box
min_x, max_x = x_parts[cx][0], x_parts[cx][-1]
min_y, max_y = y_parts[cy][0], y_parts[cy][-1]
min_z, max_z = z_parts[cz][0], z_parts[cz][-1]

print("Min x: ", min_x)
print("Max x: ", max_x)

# Calculate the distance of each center from the boundaries of the current part box
dist_x = np.minimum(centers[:, 0] - min_x, max_x - centers[:, 0])
dist_y = np.minimum(centers[:, 1] - min_y, max_y - centers[:, 1])
dist_z = np.minimum(centers[:, 2] - min_z, max_z - centers[:, 2])

# Find the centers that are inside or touching the box
mask = np.logical_and(
    dist_x >= -length_scale, dist_y >= -length_scale, dist_z >= -length_scale
)

# Apply the mask to get the centers that are inside or touching the box
centers = centers[mask]
length_scale = length_scale[mask]
orientations = orientations[mask]
print("Centers: ", centers.shape)

# Reshape the centers, length_scale, and orientations arrays to allow broadcasting
centers = centers.reshape(-1, 1, 1, 1, 3)
length_scale = length_scale.reshape(-1, 1, 1, 1, 1)
orientations = orientations.reshape(-1, 1, 1, 1, 3)

# Calculate the relative position vectors
start_time = time.time()
rk = positions - centers / length_scale
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
