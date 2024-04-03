import cupy as cp


def random_unit_vectors(n):
    phi = 2 * cp.pi * cp.random.rand(n)
    costheta = 2 * cp.random.rand(n) - 1
    theta = cp.arccos(costheta)
    x = cp.sin(theta) * cp.cos(phi)
    y = cp.sin(theta) * cp.sin(phi)
    z = cp.cos(theta)
    return cp.stack((x, y, z), axis=-1)


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
    cp.save(f"vectors_chunk_{i}.npy", vectors)
