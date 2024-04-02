import numpy as np
import timeit


def random_unit_vectors(n):
    phi = 2 * np.pi * np.random.rand(n)
    costheta = 2 * np.random.rand(n) - 1
    theta = np.arccos(costheta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.stack((x, y, z), axis=-1)


def random_unit_vectors_normal(n):
    points = np.random.normal(size=(n, 3))
    return points / np.linalg.norm(points, axis=1, keepdims=True)


n = 1000000  # Number of vectors to generate

# Measure the time for each method
start_time = timeit.default_timer()
random_unit_vectors(n)
print("Spherical coordinates method:", timeit.default_timer() - start_time)

start_time = timeit.default_timer()
random_unit_vectors_normal(n)
print("Normal distribution method:", timeit.default_timer() - start_time)
