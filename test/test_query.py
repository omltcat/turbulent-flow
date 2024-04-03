import pytest
import os
import glob
import json
# import numpy as np
from matplotlib.figure import Figure
from modules import file_io
from modules.query import Query
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    global query
    # Eddy profile
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 100, "intensity": 0.8, "length_scale": 0.1},
            {"density": 10, "intensity": 1, "length_scale": 0.2},
            {"density": 0.5, "intensity": 1.1, "length_scale": 0.5},
            {"density": 0.005, "intensity": 1.2, "length_scale": 1.5},
        ],
    }
    field_name = "test_field"
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)
    FlowField.verbose = False
    field = FlowField(profile, field_name, [10, 10, 5])
    query = Query(field)

    os.remove(f"src/profiles/{profile_name}.json")

    yield

    FlowField.verbose = True
    for file in glob.glob(f"src/results/{field_name}_*.npy"):
        os.remove(file)


@pytest.mark.unit
def test_query_meshgrid():
    content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-5, -5, 0],
            "high_bounds": [5, 5, 0],
            "step_size": 0.2,
            "chunk_size": 5,
            "t": 0,
        },
        "plot": {"axis": "z", "index": 0, "save": "__test_fig__", "size": [640, 480]},
    }
    request = "__test_mesh__"
    file_io.write("queries", "__test_mesh__", content, format="json")
    response = query.handle_request(request=request, format="file")
    assert isinstance(response, Figure), f"{response}"

    content["params"]["low_bounds"] = [-1, 2, -1]
    content["params"]["high_bounds"] = [1, 2, 1]
    content["plot"]["axis"] = "y"
    response = query.handle_request(request=json.dumps(content))
    assert isinstance(response, Figure), f"{response}"

    content["params"]["low_bounds"] = [-1, -1, -1]
    content["params"]["high_bounds"] = [1, 1, 1]
    content["plot"]["axis"] = "x"
    response = query.handle_request(request=json.dumps(content))
    assert isinstance(response, Figure), f"{response}"

    content["params"]["do_return"] = False
    del content["plot"]
    response = query.handle_request(request=json.dumps(content))
    assert "Meshgrid velocity calculation complete" in response, f"{response}"

    # Clean up
    os.remove(f"src/queries/{request}.json")


@pytest.mark.unit
def test_query_points():
    content = {
        "mode": "points",
        "params": {
            "coords": [[0, 1, 0], [2, 1.5, 2.1]],
        },
    }
    response = query.handle_request(request=json.dumps(content))
    assert "Points velocity calculation complete" in response, f"{response}"

    del content["params"]["coords"]
    response = query.handle_request(request=json.dumps(content))
    assert "Points velocity calculation complete" in response, f"{response}"


@pytest.mark.unit
def test_query_meshgrid_exceptions():
    # Not json string
    content = "invalid"
    response = query.handle_request(request=content)
    assert "Invalid query request string" in response, f"{response}"

    # Params not dict
    content = json.dumps({"mode": "meshgrid", "params": "invalid"})
    response = query.handle_request(request=content)
    assert "Invalid request" in response, f"{response}"

    # Invalid meshgrid params
    content = json.dumps({"mode": "meshgrid", "params": {"low_bounds": [-100, 0, 0]}})
    response = query.handle_request(request=content)
    assert "Error calculating velocity" in response, f"{response}"


@pytest.mark.unit
def test_query_points_exceptions():
    # Invalid points params
    content = {
        "mode": "points",
        "params": {
            "coords": "invalid",
        },
    }
    response = query.handle_request(request=json.dumps(content))
    assert "Invalid request parameters" in response, f"{response}"

    # Invalid bounds
    content["params"]["coords"] = [[-100, 0, 0]]
    response = query.handle_request(request=json.dumps(content))
    assert "Error calculating velocity at points" in response, f"{response}"


@pytest.mark.unit
def test_query_mode_exceptions():
    # Invalid mode
    content = {"mode": "invalid", "params": {}}
    response = query.handle_request(request=json.dumps(content))
    assert "Invalid request mode" in response, f"{response}"


@pytest.mark.unit
def test_query_plot_exceptions():
    # Invalid plot params (index out of bounds)
    content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-5, -5, 0],
            "high_bounds": [5, 5, 0],
            "step_size": 0.2,
        },
        "plot": {
            "axis": "z",
            "index": 10,
        },
    }
    response = query.handle_request(request=json.dumps(content))
    assert "Invalid plot index '10'" in response, f"{response}"

    # Invalid plot params (invalid axis)
    content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-5, -5, 0],
            "high_bounds": [5, 5, 0],
            "step_size": 0.2,
        },
        "plot": {
            "axis": "invalid",
        },
    }
    response = query.handle_request(request=json.dumps(content))
    assert "Invalid plot axis" in response, f"{response}"


@pytest.mark.slow
@pytest.mark.benchmark
@pytest.mark.unit
def test_query_performance():
    # Eddy profile
    FlowField.verbose = True
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 1000, "intensity": 0.8, "length_scale": 0.05},
            {"density": 10, "intensity": 1, "length_scale": 0.2},
            {"density": 0.5, "intensity": 1.1, "length_scale": 0.5},
            {"density": 0.005, "intensity": 1.2, "length_scale": 1.5},
        ],
    }
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)
    field = FlowField(profile, "test_field", [20, 20, 20])
    query = Query(field)
    os.remove(f"src/profiles/{profile_name}.json")

    # Meshgrid query
    content = {
        "mode": "meshgrid",
        "params": {
            "step_size": 0.02,
            # "low_bounds": [0, -10, -10],
            # "high_bounds": [0, 10, 10],
            "chunk_size": 5,
            "t": 0,
            "do_return": True,
            # "do_cache": True,
        },
        "plot": {"axis": "x", "index": 0, "save": "__test_fig__", "size": [1280, 960]},
    }
    response = query.handle_request(request=json.dumps(content))
    if isinstance(response, str):
        print(response)
