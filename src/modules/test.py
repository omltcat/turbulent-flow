import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Suppose Vx, Vy, and Vz are your velocity field
Vx = np.random.rand(100, 100, 100)
Vy = np.random.rand(100, 100, 100)
Vz = np.random.rand(100, 100, 100)

# Define the value of a
a = 5

# Generate 100 points from -a to a
points = np.linspace(-a, a, 100)

# Create a 3D meshgrid
X, Y, Z = np.meshgrid(points, points, points)

# Downsample the field
ds = 10
X = X[::ds, ::ds, ::ds]
Y = Y[::ds, ::ds, ::ds]
Z = Z[::ds, ::ds, ::ds]
Vx = Vx[::ds, ::ds, ::ds]
Vy = Vy[::ds, ::ds, ::ds]
Vz = Vz[::ds, ::ds, ::ds]

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the vector field
ax.quiver(X, Y, Z, Vx, Vy, Vz, length=0.1, normalize=True)

# Show the plot
plt.show()