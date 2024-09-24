import numpy as np
cube = np.zeros((3, 3, 3, 3))
plane = np.zeros((3, 3))
plane += 1

print(cube)

# add plane to each slice of cube
cube[..., 0] += plane

print(cube[..., 0])