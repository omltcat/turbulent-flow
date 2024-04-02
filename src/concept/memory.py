import numpy as np


def random_unit_vectors(n):
    phi = 2 * np.pi * np.random.rand(n)
    costheta = 2 * np.random.rand(n) - 1
    theta = np.arccos(costheta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.stack((x, y, z), axis=-1)


# Total number of vectors to generate
total_n = 1000 * 1000 * 1000

# Number of vectors to generate per chunk
chunk_n = 1000 * 1000 * 100

# Number of chunks
num_chunks = total_n // chunk_n

for i in range(num_chunks):
    # Generate a chunk of vectors
    vectors = random_unit_vectors(chunk_n)

    # Save the chunk to a file
    np.save(f"vectors_chunk_{i}.npy", vectors)
