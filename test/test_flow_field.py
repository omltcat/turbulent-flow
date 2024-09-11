import os
import numpy as np
import modules.file_io as file_io
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField
import pytest

import matplotlib.pyplot as plt

# Relative tolerance for floating point comparisons
RTOL = 1e-5


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    FlowField.verbose = False
    yield
    FlowField.verbose = True

    # Clean up
    os.remove("src/profiles/__test__.json")
    os.remove("src/fields/test_field.pkl")


@pytest.mark.slow
@pytest.mark.unit
@pytest.mark.poc
def test_eddy_generation():
    """
    Test single eddy generation
    SLOW MESHGRID!! NOT USED BY AUTO TESTS
    """
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
        time=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[0, 0, 0],
        high_bounds=[0, 0, 0],
    ).squeeze()
    assert np.isclose(np.linalg.norm(vel_000), avg_vel, rtol=RTOL)

    # Get velocities at t=0, x=1.2 and x=-1.2
    vel_pos12 = field.sum_vel_mesh(
        time=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[1.2, 0, 0],
        high_bounds=[1.2, 0, 0],
    ).squeeze()
    vel_neg12 = field.sum_vel_mesh(
        time=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[-1.2, 0, 0],
        high_bounds=[-1.2, 0, 0],
    ).squeeze()
    assert np.isclose(np.linalg.norm(vel_pos12 + vel_neg12) / 2, avg_vel, rtol=RTOL)

    # Get velocities at t=0, z=0
    vel_t0 = field.sum_vel_mesh(
        time=0,
        step_size=0.02,
        chunk_size=5,
        low_bounds=[0, -10, -10],
        high_bounds=[0, 10, 10],
    )

    # Calculate number of samples
    num_samples = np.prod(vel_t0.shape[:-1])

    # Check average velocity fluctation is zero
    avg_fluct = np.sum(vel_t0 - np.array([avg_vel, 0, 0]), axis=(0, 1, 2)) / num_samples
    assert np.linalg.norm(avg_fluct) < RTOL

    magnitude = np.linalg.norm(vel_t0, axis=-1)
    # Create a 2D heatmap for the chosen z value
    im = plt.imshow(
        magnitude[0, :, :].T,
        cmap="coolwarm",
        interpolation="nearest",
        extent=[-10, 10, -10, 10],
        origin="lower",
    )
    plt.colorbar(im, label="Velocity magnitude (m/s)")
    plt.show()

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")


@pytest.mark.poc
def test_flow_field_wrap():
    """Test wrap-around with a single eddy"""
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 0.005, "intensity": 5, "length_scale": 4.0},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    # Create flow field
    field_name = "one_eddy_wrap"
    dimensions = np.array([20, 20, 20])
    avg_vel = 1
    field = FlowField(profile, field_name, dimensions, avg_vel)

    # Remove additional eddies
    field.N = 1
    field.sigma = field.sigma[:1]
    field.alpha = field.alpha[:1]
    field.init_x = field.init_x[:1]
    field.y = {k: v[:1] for k, v in field.y.items()}
    field.z = {k: np.array([0]) for k, v in field.z.items()}

    # Get velocities at t=0
    vel_t0 = field.sum_vel_mesh(
        low_bounds=[-10, -10, 0],
        high_bounds=[10, 10, 0],
        time=0,
        step_size=0.1,
    )

    # Create a 2D heatmap for the chosen z value
    magnitude = np.linalg.norm(vel_t0, axis=-1)
    im = plt.imshow(
        magnitude[:, :, 0].T,
        cmap="coolwarm",
        interpolation="nearest",
        extent=[-10, 10, -10, 10],
        origin="lower",
    )
    plt.colorbar(im, label="Velocity magnitude (m/s)")
    plt.show()

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")


@pytest.mark.unit
def test_flow_field():
    """Test flow field generation and properties"""
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
    field.save()

    # Test flow field load
    field: FlowField = FlowField.load("test_field")
    assert field.name == "test_field"
    assert field.dimensions[0] == 20
    assert field.variant_length_scale[0] == 0.1

    # Test set average velocity
    field.set_avg_vel(2.0)
    assert field.avg_vel == 2.0

    # Correct number of eddies
    volume = np.prod(dimensions)
    variant_quantity = np.array(
        [v["density"] * volume for v in content["variants"]], dtype=int
    )

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
        time=0,
    )

    vel_t10_x10 = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[10, -10, -10],
        high_bounds=[10, 10, 10],
        time=10,
    )

    # Due to average flow velocity, these two should be the same
    diff_sum = np.sum(np.linalg.norm(vel_t0_xneg10 - vel_t10_x10, axis=-1))
    assert diff_sum < RTOL


@pytest.mark.unit
def test_flow_field_parallel():
    field: FlowField = FlowField.load("test_field")
    field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[-10, -10, -10],
        high_bounds=[10, 10, 10],
        time=0,
        threads=4,
    )

    # Check for number of chunk cache files created
    expected_files = 20 / 0.2 // 5
    assert len([f for f in os.listdir("src/.cache") if "x_" in f]) == expected_files


@pytest.mark.unit
def test_non_uniform_x_vel():
    """Test using a linear velocity profile from 0 to 8 m/s from y=-10 to y=10 (like a slip boundary)"""
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 0.005, "intensity": 1.2, "length_scale": 2.0},
        ],
    }

    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)

    # Field creation
    field_name = "two_eddies"
    dimensions = np.array([20, 20, 20])
    field = FlowField(profile, field_name, dimensions, avg_vel=8, x_vel_prof="linear_2d")

    # Keep only two eddies, so we can track their movements without interference
    field.N = 2
    field.sigma = field.sigma[:2]
    field.alpha = field.alpha[:2]

    # Move one eddy to 0,-5,0 and the other to 0,5,0
    field.init_x = np.array([0, 0])
    field.y[0] = np.array([-5, 5])
    field.z[0] = np.array([0, 0])

    # Recalculate x_vel at these new positions
    ny: np.ndarray = field.y[0] / field.high_bounds[1]
    nz: np.ndarray = field.z[0] / field.high_bounds[2]
    field.x_vel = field.x_vel_func(ny, nz) * field.avg_vel

    field.save()

    # Avg velocity for eddy A is 2 m/s, for eddy B is 6 m/s

    # Get velocities at t=0, around 0,-5,0 and 0,5,0
    vel_t0_a = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[-2, -7, -2],
        high_bounds=[2, -3, 2],
        time=0,
    )
    vel_t0_b = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[-2, 3, -2],
        high_bounds=[2, 7, 2],
        time=0,
    )

    # Get velocities at t=1, around 2,-5,0 and 6,5,0
    vel_t1_a = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[0, -7, -2],
        high_bounds=[4, -3, 2],
        time=1,
    )
    vel_t1_b = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[4, 3, -2],
        high_bounds=[8.0001, 7, 2],
        time=1,
    )
    # Check if the velocity box at t=0 and t=1 is the same
    diff_sum = np.sum(np.linalg.norm(vel_t0_a - vel_t1_a, axis=-1))
    assert diff_sum < RTOL

    diff_sum = np.sum(np.linalg.norm(vel_t0_b - vel_t1_b, axis=-1))
    assert diff_sum < RTOL

    # Get velocities at t=2, around 4,-5,0 and -8,5,0 (wrapping around)
    vel_t2_a = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[2, -7, -2],
        high_bounds=[6.0001, -3, 2],
        time=2,
    )
    vel_t2_b = field.sum_vel_mesh(
        step_size=0.2,
        chunk_size=5,
        low_bounds=[-10, 3, -2],
        high_bounds=[-6, 7, 2],
        time=2,
    )

    # Check if the velocity box at t=0 and t=2 is the same
    diff_sum = np.sum(np.linalg.norm(vel_t0_a - vel_t2_a, axis=-1))
    assert diff_sum < RTOL

    diff_sum = np.sum(np.linalg.norm(vel_t0_b - vel_t2_b, axis=-1))
    assert diff_sum < RTOL

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")
    os.remove(f"src/fields/{field_name}.pkl")


@pytest.mark.unit
def test_flow_field_init_exceptions():
    """Test exceptions for flow field initialization"""
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


@pytest.mark.unit
def test_flow_field_mesh_exceptions():
    """Test exceptions for flow field mesh qeury"""
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
            time=-1,
        )


@pytest.mark.unit
def test_flow_field_set_exceptions():
    """Test exceptions for flow field setters"""
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


@pytest.mark.slow
@pytest.mark.memory
@pytest.mark.unit
def test_flow_field_out_of_memory():
    """
    Test flow field generation with out of memory conditions
    SLOW!! NOT USED BY AUTO TESTS
    """
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
            time=0,
        )

    # Test chunk_size too large
    with pytest.raises(MemoryError):
        field.sum_vel_mesh(
            step_size=0.02,
            chunk_size=0,
            time=0,
        )

    # Clean up
    os.remove(f"src/profiles/{profile_name}.json")
