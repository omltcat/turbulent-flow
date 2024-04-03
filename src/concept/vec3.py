import cupy as cp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create an array of 3D vectors
X, Y, Z = cp.meshgrid(cp.linspace(-1, 1, 10), cp.linspace(-1, 1, 10), cp.linspace(-1, 1, 10))
U, V, W = cp.sin(cp.pi * X) * cp.cos(cp.pi * Y) * cp.cos(cp.pi * Z), -cp.cos(cp.pi * X) * cp.sin(cp.pi * Y) * cp.cos(cp.pi * Z), (cp.sqrt(2.0 / 3.0) * cp.cos(cp.pi * X) * cp.cos(cp.pi * Y) * cp.sin(cp.pi * Z))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D vectors
ax.quiver(X, Y, Z, U, V, W, length=0.1, normalize=True)

plt.show()