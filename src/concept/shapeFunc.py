import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def q_sigma(rk: np.array, sigma=1):
    rk = np.linalg.norm(rk_array, axis=1)

    def distribution(x):
        mean = 0
        std = 1/3
        return norm.pdf(x, mean, std)
    return np.where(rk < 1, sigma * distribution(rk), 0)


# Create an array of 100 x values from -2 to 2
x_values = np.linspace(-2, 2, 201)

# Create an array of 100 3D vectors
rk_array = np.array([x_values, np.zeros(201), np.zeros(201)]).T

# Generate y values
y = q_sigma(rk_array)

# Create the plot
plt.plot(x_values, y)

# Show the plot
plt.show()
