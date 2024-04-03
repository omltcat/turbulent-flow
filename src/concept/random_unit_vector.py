import cupy as cp
import timeit


def random_unit_vectors(n):
    phi = 2 * cp.pi * cp.random.rand(n)
    costheta = 2 * cp.random.rand(n) - 1
    theta = cp.arccos(costheta)
    x = cp.sin(theta) * cp.cos(phi)
    y = cp.sin(theta) * cp.sin(phi)
    z = cp.cos(theta)
    return cp.stack((x, y, z), axis=-1)


def random_unit_vectors_normal(n):
    points = cp.random.normal(size=(n, 3))
    return points / cp.linalg.norm(points, axis=1, keepdims=True)


n = 1000000  # Number of vectors to generate

# Measure the time for each method
start_time = timeit.default_timer()
random_unit_vectors(n)
print("Spherical coordinates method:", timeit.default_timer() - start_time)

start_time = timeit.default_timer()
random_unit_vectors_normal(n)
print("Normal distribution method:", timeit.default_timer() - start_time)
