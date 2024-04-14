import os
import glob
import pytest
import numpy as np
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField
from modules import file_io
from modules import shape_function
import main

RTOL = 1e-5


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    profile_content = {
        "settings": {},
        "variants": [
            {"density": 0.01, "intensity": 1.0, "length_scale": 1.0}
        ]
    }
    file_io.write("profiles", "test_system_eddy_profile", profile_content, "json")
    profile = EddyProfile("test_system_eddy_profile")
    field = FlowField(profile, "test_system_eddy_field", [10, 10, 10])

    # keep only one eddy
    field.N = 1
    field.sigma = field.sigma[:1]
    field.alpha = field.alpha[:1]

    # Move the eddy to the center
    field.init_x = np.array([0.0])
    field.y[0] = np.array([0.0])
    field.z[0] = np.array([0.0])
    field.y[1] = np.array([0.0])
    field.z[1] = np.array([0.0])
    field.y[2] = np.array([0.0])
    field.z[2] = np.array([0.0])

    # Orient eddy to along z-axis
    field.alpha[0] = np.array([0, 0, 1])

    # Save field
    field.save()

    yield

    # Clean up
    shape_function.set_cutoff(2.0)
    os.remove("src/profiles/test_system_eddy_profile.json")
    os.remove("src/fields/test_system_eddy_field.pkl")
    os.remove("src/queries/test_system_eddy_query.json")
    for file in glob.glob("src/results/test_system_eddy_*"):
        os.remove(file)


@pytest.mark.system
def test_eddy_shape():
    query_content = {
        "mode": "points",
        "params": {
            "coords": [
                [0.5, 0.5, 0.5],
                [-0.5, -0.5, -0.5],
                [2.0, 2.0, 2.0],
                [-2.0, -2.0, -2.0]
            ]
        },
    }
    file_io.write("queries", "test_system_eddy_query", query_content, "json")
    main.main(["query", "-n", "test_system_eddy_field", "-q", "test_system_eddy_query", "-c", "1.0"])
    files = glob.glob("src/results/test_system_eddy_*")
    if len(files) == 0:
        raise FileNotFoundError("No result files found")

    filename = os.path.splitext(os.path.basename(max(files, key=os.path.getmtime)))[0]
    velocities = file_io.read("results", filename, "npy")
    assert np.linalg.norm(velocities[0] + velocities[1]) < RTOL * np.linalg.norm(velocities[0])
    assert np.linalg.norm(velocities[2]) == 0.0
    assert np.linalg.norm(velocities[3]) == 0.0


@pytest.mark.system
def test_eddy_std():
    query_content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-1, -1, -1],
            "high_bounds": [1, 1, 1],
            "step_size": 0.02,
            "chunk_size": 5,
        }
    }
    file_io.write("queries", "test_system_eddy_query", query_content, "json")
    main.main(["query", "-n", "test_system_eddy_field", "-q", "test_system_eddy_query"])
    files = glob.glob("src/results/test_system_eddy_*")
    if len(files) == 0:
        raise FileNotFoundError("No result files found")

    filename = os.path.splitext(os.path.basename(max(files, key=os.path.getmtime)))[0]
    global vel_field
    vel_field = file_io.read("results", filename, "npy")
    assert np.std(vel_field[..., 2]) < RTOL
    assert np.mean(vel_field[..., 0]) < RTOL
    assert np.mean(vel_field[..., 1]) < RTOL
