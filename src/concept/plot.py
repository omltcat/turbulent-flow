import cupy as cp
import matplotlib.pyplot as plt

# Create a grid of points
x, y, z = cp.meshgrid(
    cp.arange(-0.8, 1, 0.2), cp.arange(-0.8, 1, 0.2), cp.arange(-0.8, 1, 0.8)
)

# Define the vector field
u = cp.sin(cp.pi * x) * cp.cos(cp.pi * y) * cp.cos(cp.pi * z)
v = -cp.cos(cp.pi * x) * cp.sin(cp.pi * y) * cp.cos(cp.pi * z)
w = cp.sqrt(2.0 / 3.0) * cp.cos(cp.pi * x) * cp.cos(cp.pi * y) * cp.sin(cp.pi * z)

# Create a 3D figure
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

# Plot the vector field
ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True)

print(x.shape, y.shape, z.shape)

plt.show()
