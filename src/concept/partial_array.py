import numpy as np

# Create the first array with shape (5, 5, 1, 3)
first_array = np.zeros((5, 5, 1, 3))

# Create the second array with shape (2, 2, 1, 3)
second_array = np.ones((2, 2, 1, 3))

# Choose the start indices for each dimension
start_i, start_j, start_k, start_l = 1, 1, 0, 0

# Replace the slice of the first array with the second array
first_array[
    start_i : start_i + second_array.shape[0],
    start_j : start_j + second_array.shape[1],
    start_k : start_k + second_array.shape[2],
    start_l : start_l + second_array.shape[3],
] = second_array

print(first_array)
