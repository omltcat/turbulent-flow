import os
import glob
import pytest
import numpy as np
from modules import file_io
import main

AVG_VEL = 2.5
RTOL = 1e-5
STD_TOL = 0.05


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    global profile_content
    profile_content = {
        "settings": {},
        "variants": [
            {"density": 200.0, "intensity": 0.75, "length_scale": 0.1},
            {"density": 10.0, "intensity": 1.0, "length_scale": 0.2},
            {"density": 0.5, "intensity": 1.1, "length_scale": 0.5},
        ],
    }
    file_io.write("profiles", "test_system_field_profile", profile_content, "json")

    main.main(
        [
            "new",
            "-p",
            "test_system_field_profile",
            "-n",
            "test_system_field_field",
            "-d",
            "2",
            "2",
            "2",
            "-v",
            str(AVG_VEL),
        ]
    )

    global query_content
    query_content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-1, -1, -1],
            "high_bounds": [1, 1, 1],
            "step_size": 0.02,
            "chunk_size": 5,
            "time": 0,
        }
    }
    file_io.write("queries", "test_system_field_query", query_content, "json")

    yield

    os.remove("src/profiles/test_system_field_profile.json")
    os.remove("src/fields/test_system_field_field.pkl")
    os.remove("src/queries/test_system_field_query.json")
    for file in glob.glob("src/results/test_system_field_*"):
        os.remove(file)


@pytest.mark.system
def test_field_mean():
    main.main(["query", "-n", "test_system_field_field", "-q", "test_system_field_query"])
    files = glob.glob("src/results/test_system_field_*")
    if len(files) == 0:
        raise FileNotFoundError("No result files found")

    filename = os.path.splitext(os.path.basename(max(files, key=os.path.getmtime)))[0]
    global vel_field_0
    vel_field_0 = file_io.read("results", filename, "npy")
    vel_field_0[..., 0] -= AVG_VEL

    # Get sum of velocities
    assert np.linalg.norm(np.mean(vel_field_0, axis=(0, 1, 2))) < RTOL


@pytest.mark.system
def test_field_std_time():
    global query_content
    query_content["params"]["time"] = 10
    file_io.write("queries", "test_system_field_query", query_content, "json")
    main.main(["query", "-n", "test_system_field_field", "-q", "test_system_field_query"])
    files = glob.glob("src/results/test_system_field_*")
    if len(files) == 0:
        raise FileNotFoundError("No result files found")

    filename = os.path.splitext(os.path.basename(max(files, key=os.path.getmtime)))[0]
    vel_field_10 = file_io.read("results", filename, "npy")
    vel_field_10[..., 0] -= AVG_VEL

    # Get standard deviation of velocities
    std_0 = np.std(vel_field_0, axis=(0, 1, 2))
    std_10 = np.std(vel_field_10, axis=(0, 1, 2))
    # print(std_0, std_10)
    assert np.linalg.norm(std_0 - std_10) < STD_TOL


@pytest.mark.system
def test_field_std_intensity():
    # Set time back to 0
    global query_content
    query_content["params"]["time"] = 0
    file_io.write("queries", "test_system_field_query", query_content, "json")

    # Increase intensity for each variant
    global profile_content
    for variant in profile_content["variants"]:
        variant["intensity"] *= 2
    file_io.write("profiles", "test_system_field_profile", profile_content, "json")
    main.main(
        [
            "new",
            "-p",
            "test_system_field_profile",
            "-n",
            "test_system_field_field",
            "-d",
            "2",
            "2",
            "2",
            "-v",
            str(AVG_VEL),
        ]
    )

    main.main(["query", "-n", "test_system_field_field", "-q", "test_system_field_query"])
    files = glob.glob("src/results/test_system_field_*")
    if len(files) == 0:
        raise FileNotFoundError("No result files found")

    filename = os.path.splitext(os.path.basename(max(files, key=os.path.getmtime)))[0]
    vel_field_intense = file_io.read("results", filename, "npy")
    vel_field_intense[..., 0] -= AVG_VEL

    # Get standard deviation of velocities
    std_intense = np.std(vel_field_intense, axis=(0, 1, 2))
    std_0 = np.std(vel_field_0, axis=(0, 1, 2))
    assert np.linalg.norm(std_intense) > np.linalg.norm(std_0)


@pytest.mark.system
def test_field_divergence():
    # Calculate partial derivatives
    dvdx = np.gradient(vel_field_0[..., 0], axis=0)
    dvdy = np.gradient(vel_field_0[..., 1], axis=1)
    dvdz = np.gradient(vel_field_0[..., 2], axis=2)

    # Calculate divergence
    div = dvdx + dvdy + dvdz
    abs_div = np.abs(div)
    assert np.mean(abs_div) < STD_TOL
