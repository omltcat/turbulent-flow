import numpy as np
from modules.eddy import Eddy
# import matplotlib.pyplot as plt


TOL = 1e-8
REL_POS = np.array([0.5, 0.5, 0.5])
SAMPLES = 100
VARIANTS = [
    {
        "density": 0.1,
        "intensity": 1.15,
        "length_scale": 1
    },
    {
        "density": 1.2,
        "intensity": 0.9,
        "length_scale": 0.2
    }
]


def test_eddy():
    # Define eddy variants
    Eddy.set_variants(VARIANTS)

    # Define field dimensions
    Eddy.set_field_dimension(np.array([10, 10, 10]))

    # Test Eddy class
    eddy = Eddy(0)
    assert eddy.get_variant() == VARIANTS[0]
    assert eddy.get_length_scale() == 1
    assert eddy.get_intensity() == 1.15
    assert np.isclose(np.linalg.norm(eddy.get_orientation()), 1, atol=TOL)

    center = eddy.get_center(1)
    assert center[0] == eddy.init_x

    # Test get_vel
    vel = []
    vel.append(eddy.get_vel(center+REL_POS, 1, 0))
    vel.append(eddy.get_vel(center-REL_POS, 1, 0))
    assert np.isclose(np.linalg.norm(vel[0]+vel[1]), 0, atol=TOL)

    # Test set_orientation
    # eddy.set_orientation(np.array([0, 0, 1]))

    # Sample positions with upright orientation
    length_scale = VARIANTS[0]['length_scale']
    x = np.linspace(-length_scale*3, length_scale*3, SAMPLES) + center[0]
    y = np.zeros(SAMPLES) + center[1]
    z = np.zeros(SAMPLES) + center[2]
    pos_samples = np.column_stack((x, y, z))
    vels = np.array([eddy.get_vel(pos, 1, 0) for pos in pos_samples])
    assert np.isclose(np.linalg.norm(np.sum(vels, axis=0)), 0, atol=TOL)

    # plt.plot(x, vels[:, 0])
    # plt.plot(x, vels[:, 1])
    # plt.plot(x, vels[:, 2])
    # plt.grid()
    # plt.show()

    # points = np.linspace(-length_scale*3, length_scale*3, 50)
    # X, Y = np.meshgrid(points+center[0], points+center[1])

    # # Initialize arrays for the velocity field
    # Vx = np.zeros_like(X)
    # Vy = np.zeros_like(Y)

    # # Compute the velocity field
    # for i in range(X.shape[0]):
    #     for j in range(X.shape[1]):
    #         v = eddy.get_vel(np.array([X[i, j], Y[i, j], center[2]]), 1, 0)
    #         Vx[i, j] = v[0]
    #         Vy[i, j] = v[1]

    # # Create a 2D plot
    # fig, ax = plt.subplots()

    # # Plot the vector field
    # ax.quiver(X, Y, Vx, Vy, scale=50)

    # # Set the limits of the plot to match the range of the meshgrid
    # ax.set_xlim([center[0]-length_scale*3, center[0]+length_scale*3])
    # ax.set_ylim([center[1]-length_scale*3, center[1]+length_scale*3])

    # # Show the plot
    # plt.show()
