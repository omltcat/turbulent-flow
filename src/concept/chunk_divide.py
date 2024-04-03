import cupy as cp


def chunk_array(array, chunk_size):
    return [
        cp.array(array[i:i + chunk_size]) for i in range(0, len(array), chunk_size)
    ]


array = cp.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
chunk_size = 4
print(chunk_array(array, chunk_size))

print(array[cp.array([0, 1, 2, 3])])
