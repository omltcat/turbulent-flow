import cupy as cp
import matplotlib.pyplot as plt
from scipy.stats import norm


def q_sigma(rk: cp.array, sigma=1):
    rk = cp.linalg.norm(rk, axis=1)

    def distribution(x):
        mean = 0
        std = 1/4
        value = norm.pdf(x, mean, std)
        return value / norm.pdf(mean, mean, std)
    return cp.where(rk < 1, sigma * distribution(rk), 0)


def q_d(dk):
    dk = cp.linalg.norm(dk, axis=1)
    return 1 - dk**2


def q_e(dk):
    dk = cp.linalg.norm(dk, axis=1)
    C = 3.6276 * cp.sqrt(1)
    return C * cp.exp(-0.5*cp.pi * dk**2)


# Create an array of 100 x values from -2 to 2
x_values = cp.linspace(-2, 2, 201)

# Create an array of 100 3D vectors
rk_array = cp.array([x_values, cp.zeros(201), cp.zeros(201)]).T

# Generate y values
y = q_e(rk_array)

area = cp.trapz(y, x=x_values)
print(area)

# print(y)

# Create the plot
plt.plot(x_values, y)
plt.grid(True)
# Show the plot
plt.show()
