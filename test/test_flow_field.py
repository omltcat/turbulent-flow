import os
import numpy as np
import modules.file_io as file_io
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField
import pytest

import matplotlib.pyplot as plt

# from itertools import combinations, product
# import matplotlib.pyplot as plt

RTOL = 1e-5


@pytest.mark.skip(reason="Single eddy, only for development purposes.")
def test_eddy_generation():
    # Test profile
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 0.005, "intensity": 1.2, "length_scale": 4.0},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    # Create flow field
    field_name = "one_eddy"
    dimensions = np.array([20, 20, 20])
    avg_vel = 0
    field = FlowField(profile, field_name, dimensions, avg_vel)

    # Remove additional eddies
    field.N = 1
    field.sigma = field.sigma[:1]
    field.alpha = field.alpha[:1]

    # Move the eddy to the center at t=0
    field.init_x = np.array([0])
    field.y[0] = np.array([0])
    field.z[0] = np.array([0])
    field.y[1] = np.array([0])
    field.z[1] = np.array([0])
    field.y[2] = np.array([0])
    field.z[2] = np.array([0])

    # Orient eddy to along z-axis
    field.alpha[0] = np.array([0, 0, 1])

    # Get velocities at t=0, xyz=0
    vel_000 = field.sum_vel_mesh(
        t=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[0, 0, 0],
        high_bounds=[0, 0, 0],
    ).squeeze()
    print(vel_000)
    assert np.isclose(np.linalg.norm(vel_000), 0, rtol=RTOL)

    # Get velocities at t=0, x=1.2 and x=-1.2
    vel_pos12 = field.sum_vel_mesh(
        t=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[1.2, 0, 0],
        high_bounds=[1.2, 0, 0],
    ).squeeze()
    vel_neg12 = field.sum_vel_mesh(
        t=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[-1.2, 0, 0],
        high_bounds=[-1.2, 0, 0],
    ).squeeze()
    print(vel_pos12, vel_neg12)
    assert np.isclose(np.linalg.norm(vel_pos12 + vel_neg12), 0, rtol=RTOL)

    # Get velocities at t=0, z=0
    vel_t0 = field.sum_vel_mesh(
        t=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[-10, -10, 0],
        high_bounds=[10, 10, 0],
    )

    # Calculate number of samples
    num_samples = np.prod(vel_t0.shape[:-1])

    # vel_t0[:, 80, 0] = 10

    # Check zero velocity in z direction
    # assert np.isclose(np.sum(vel_t0[:, :, 0]), 0, rtol=RTOL)

    # Check average velocity fluctation is zero
    avg_fluct = np.sum(vel_t0 - np.array([avg_vel, 0, 0]), axis=(0, 1, 2)) / num_samples
    print(avg_fluct)

    magnitude = np.linalg.norm(vel_t0, axis=-1)
    # Create a 2D heatmap for the chosen z value
    im = plt.imshow(
        magnitude[:, :, 0].T,
        cmap="coolwarm",
        interpolation="nearest",
        extent=[-10, 10, -10, 10],
        origin="lower",
    )
    plt.colorbar(im, label="Velocity magnitude (m/s)")
    plt.show()


# @pytest.mark.skip(reason="Slow test, skipped to save time during devlopment.")
def test_flow_field():
    # Test profile
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 20, "intensity": 0.8, "length_scale": 0.1},
            {"density": 1.0, "intensity": 1, "length_scale": 0.2},
            {"density": 0.05, "intensity": 1.1, "length_scale": 0.5},
            {"density": 0.0005, "intensity": 1.2, "length_scale": 1.5},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    # Test flow field creation
    field_name = "test_field"
    dimensions = np.array([20, 20, 20])
    field = FlowField(profile, field_name, dimensions)

    field.set_avg_vel(2.0)

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

    # Get velocities at t=0, x=-10 and t=10, x=10
    vel_t0_xneg10 = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[-10, -10, -10],
        high_bounds=[-10, 10, 10],
        t=0,
    )

    vel_t10_x10 = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[10, -10, -10],
        high_bounds=[10, 10, 10],
        t=10,
        do_cache=True,
    )

    # Due to average flow velocity, these two should be the same
    diff_sum = np.sum(np.linalg.norm(vel_t0_xneg10 - vel_t10_x10, axis=-1))
    assert diff_sum < RTOL

    # # Test for zero average velocity fluctuation
    # vel_t20 = field.sum_vel_mesh(
    #     step_size=0.2,
    #     chunk_size=5,
    #     t=20,
    # )
    # # Calculate number of samples
    # num_samples = np.prod(vel_t20.shape[:-1])

    # # Velocity fluctuation
    # vel_fluct = vel_t20 - np.array([avg_vel, 0, 0])

    # # Check for zero average velocity fluctuation
    # avg_fluct = np.sum(vel_fluct, axis=(0, 1, 2)) / num_samples
    # assert np.linalg.norm(avg_fluct) < 0.01

    # # Create a 2D heatmap for at t=0, x=0
    # magnitude = np.linalg.norm(vel_fluct - np.array([avg_vel, 0, 0]), axis=-1)
    # im = plt.imshow(
    #     magnitude[0, :, :],
    #     cmap="coolwarm",
    #     interpolation="nearest",
    #     extent=[-10, 10, -10, 10],
    #     origin="lower",
    # )
    # plt.colorbar(im, label="Velocity magnitude (m/s)")
    # plt.show()

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")


def test_flow_field_load():
    field: FlowField = FlowField.load("test_field")
    assert field.name == "test_field"
    assert field.dimensions[0] == 20
    assert field.variant_length_scale[0] == 0.1


def test_flow_field_init_exceptions():
    profile_name = "__invalid__"
    content = {
        "settings": {},
        "variants": [
            {"density": 20, "intensity": 0.8, "length_scale": 15},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    field_name = "test_field"
    dimensions = np.array([20, 20, 20])
    avg_vel = 2

    # Test for invalid dimensions shape
    with pytest.raises(ValueError):
        FlowField(profile, field_name, [20, 20], avg_vel)

    # Test for invalid dimensions type
    with pytest.raises(ValueError):
        FlowField(profile, field_name, ["a", 2, 3], avg_vel)

    # Test for negative dimensions
    with pytest.raises(ValueError):
        FlowField(profile, field_name, [-20, 20, 20], avg_vel)

    # Test for invalid average velocity
    with pytest.raises(ValueError):
        FlowField(profile, field_name, dimensions, -2)

    # Test for length scale too large
    with pytest.raises(ValueError):
        FlowField(profile, field_name, dimensions, avg_vel)

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")


def test_flow_field_mesh_exceptions():
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 20, "intensity": 0.8, "length_scale": 0.1},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    field_name = "test_field"
    dimensions = np.array([20, 20, 20])
    avg_vel = 2
    field = FlowField(profile, field_name, dimensions, avg_vel)

    # Test for invalid bound types
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=1,
            chunk_size=5,
            low_bounds=3,
            high_bounds=[10, 10, 10],
        )

    # Test for invalid bound shapes
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=1,
            chunk_size=5,
            low_bounds=[-10, -10],
            high_bounds=[10, 10, 10],
        )

    # Test for low_bounds > high_bounds
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=1,
            chunk_size=5,
            low_bounds=[10, -10, -10],
            high_bounds=[-10, 10, 10],
        )

    # Test for out of bounds
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=1,
            chunk_size=5,
            low_bounds=[-10, -10, -10],
            high_bounds=[-10, 50, 10],
        )

    # Test for invalid chunk_size
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=1,
            chunk_size=-1,
        )

    # Test for invalid step_size
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=-1,
            chunk_size=5,
        )

    # Test for invalid time
    with pytest.raises(ValueError):
        field.sum_vel_mesh(
            step_size=1,
            chunk_size=5,
            t=-1,
        )

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")


def test_flow_field_set_exceptions():
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 20, "intensity": 0.8, "length_scale": 0.1},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    field_name = "test_field"
    dimensions = np.array([20, 20, 20])
    avg_vel = 2
    field = FlowField(profile, field_name, dimensions, avg_vel)

    # Test for invalid average velocity
    with pytest.raises(ValueError):
        field.set_avg_vel(-2)

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")


@pytest.mark.skip(reason="Use too much memory, known to work.")
def test_flow_field_out_of_memory():
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 2000, "intensity": 0.8, "length_scale": 0.1},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    field_name = "test_field"
    dimensions = np.array([20, 20, 20])
    avg_vel = 2
    field = FlowField(profile, field_name, dimensions, avg_vel)

    # Test grid too fine
    with pytest.raises(MemoryError):
        field.sum_vel_mesh(
            step_size=0.001,
            chunk_size=5,
            t=0,
        )

    # Test chunk_size too large
    with pytest.raises(MemoryError):
        field.sum_vel_mesh(
            step_size=0.02,
            chunk_size=0,
            t=0,
        )

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")