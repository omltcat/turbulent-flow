import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create an array of 3D vectors
X, Y, Z = np.meshgrid(np.linspace(-1, 1, 10), np.linspace(-1, 1, 10), np.linspace(-1, 1, 10))
U, V, W = np.sin(np.pi * X) * np.cos(np.pi * Y) * np.cos(np.pi * Z), -np.cos(np.pi * X) * np.sin(np.pi * Y) * np.cos(np.pi * Z), (np.sqrt(2.0 / 3.0) * np.cos(np.pi * X) * np.cos(np.pi * Y) * np.sin(np.pi * Z))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D vectors
ax.quiver(X, Y, Z, U, V, W, length=0.1, normalize=True)

plt.show()