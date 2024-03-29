import os
import numpy as np
import modules.file_io as file_io
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField

import matplotlib.pyplot as plt

# from itertools import combinations, product
# import matplotlib.pyplot as plt

RTOL = 1e-5


def test_flow_field():
    # Test profile
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 200, "intensity": 0.8, "length_scale": 0.1},
            {"density": 10.0, "intensity": 1, "length_scale": 0.2},
            {"density": 0.5, "intensity": 1.1, "length_scale": 0.5},
            {"density": 0.005, "intensity": 1.2, "length_scale": 1.5},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    # Test flow field creation
    field_name = "test_field"
    dimensions = np.array([20, 20, 20])
    avg_vel = 2
    field = FlowField(profile, field_name, dimensions, avg_vel)

    volume = np.prod(dimensions)
    variant_quantity = np.array(
        [v["density"] * volume for v in content["variants"]], dtype=int
    )

    # Correct number of eddies
    assert np.isclose(field.N, np.sum(variant_quantity), 1)

    # Correct variant quantities and length scales
    assert np.isclose(
        np.sum(field.sigma),
        np.sum(profile.get_length_scale_array() * variant_quantity),
        rtol=RTOL,
    )

    # Correct variant intensities
    assert np.isclose(
        np.linalg.norm(field.alpha[variant_quantity[0] - 1]),
        profile.get_intensity(0),
        rtol=RTOL,
    )

    # Many random orientations should cancel out alpha
    if np.sum(variant_quantity) > 1000:
        total_intensity = np.sum(profile.get_intensity_array() * variant_quantity)
        assert np.isclose(
            np.linalg.norm(np.sum(field.alpha, axis=0)) / total_intensity,
            0,
            atol=RTOL * total_intensity,
        )

    # Field iteration and offset
    assert field.get_iter(0) == 1
    assert field.get_iter(4.9) == 1
    assert field.get_iter(5.1) == 2

    assert field.get_offset(0) == 0
    assert np.isclose(field.get_offset(5), field.dimensions[0] / 2, rtol=RTOL)
    assert np.isclose(
        field.get_offset(4.9),
        -field.get_offset(5.1),
        rtol=RTOL,
    )

    # Test mesh
    vel = field.sum_vel_mesh(step_size=0.1, chunk_size=5, low_bounds=[-10, -10, 0], high_bounds=[10, 10, 0])

    magnitude = np.linalg.norm(vel, axis=-1)

    # Choose a specific z value
    z_value = 0

    # Create a 2D heatmap for the chosen z value
    plt.imshow(
        np.transpose(magnitude[:, :, z_value]),
        cmap="cool",
        interpolation="nearest",
        extent=[-10, 10, -10, 10],
    )
    plt.show()

    # # Test wrapping
    # centers, alphas, sigmas = field.get_wrap_arounds(0)
    # print("Original centers: ", field.get_eddy_centers(0).shape)
    # print("After wrapping: ", centers.shape)

    # # Reshape centers to 2D
    # centers_2d = centers.reshape(-1, 3)

    # high_bounds = field.high_bounds
    # low_bounds = field.low_bounds

    # # Create a new figure
    # fig = plt.figure()

    # # Add a 3D subplot
    # ax = fig.add_subplot(111, projection="3d")

    # # Plot the centers
    # ax.scatter(centers_2d[:, 0], centers_2d[:, 1], centers_2d[:, 2], color="blue")

    # # Create a list of all corners of the box
    # corners = (
    #     np.array([p for p in product([0, 1], repeat=3)]) * (high_bounds - low_bounds)
    #     + low_bounds
    # )

    # # Plot the lines connecting the corners to form the box
    # for s, e in combinations(corners, 2):
    #     if (
    #         np.linalg.norm(s - e) == high_bounds[0] - low_bounds[0]
    #         or np.linalg.norm(s - e) == high_bounds[1] - low_bounds[1]
    #         or np.linalg.norm(s - e) == high_bounds[2] - low_bounds[2]
    #     ):
    #         ax.plot(*zip(s, e), color="r")

    # # Set the labels
    # ax.set_xlabel("X")
    # ax.set_ylabel("Y")
    # ax.set_zlabel("Z")

    # # Show the plot
    # plt.show()

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")
