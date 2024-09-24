from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Define the size of the array
array_size = 10000
# Initialize the array
data = np.zeros(array_size)


# Define the worker function for each thread
def compute_subsection(arr, start, end):
    for i in range(start, end):
        arr[i] = i
        # Simulate some work
        if i % 100 == 0:
            pass


# Function to dynamically create and start threads using ThreadPoolExecutor
def start_tasks_with_thread_pool(num_tasks, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(num_tasks):
            start = i * (array_size // num_tasks)
            end = (
                (i + 1) * (array_size // num_tasks)
                if i != num_tasks - 1
                else array_size
            )
            # Submit each task to the executor
            future = executor.submit(compute_subsection, data, start, end)
            futures.append(future)
        # Wait for all futures to complete
        for future in futures:
            future.result()  # This will block until the future is complete


# Example usage
num_tasks = 100  # Assuming you have 100 tasks to run
start_tasks_with_thread_pool(num_tasks)

print(data.shape)
