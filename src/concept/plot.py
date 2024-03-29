import numpy as np
import matplotlib.pyplot as plt

# Create a grid of points
x, y, z = np.meshgrid(
    np.arange(-0.8, 1, 0.2), np.arange(-0.8, 1, 0.2), np.arange(-0.8, 1, 0.8)
)

# Define the vector field
u = np.sin(np.pi * x) * np.cos(np.pi * y) * np.cos(np.pi * z)
v = -np.cos(np.pi * x) * np.sin(np.pi * y) * np.cos(np.pi * z)
w = np.sqrt(2.0 / 3.0) * np.cos(np.pi * x) * np.cos(np.pi * y) * np.sin(np.pi * z)

# Create a 3D figure
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

# Plot the vector field
ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True)

print(x.shape, y.shape, z.shape)

plt.show()
