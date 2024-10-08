import pytest
import os
import glob
import json
# import numpy as np
from modules import file_io
from modules.query import Query
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Setup and teardown for the module tests"""
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

    # Create a field
    field_name = "test_field"
    file_io.write("profiles", profile_name, content)
    profile = EddyProfile(profile_name)
    FlowField.verbose = False
    field = FlowField(profile, field_name, [10, 10, 5])
    query = Query(field)

    os.remove(f"src/profiles/{profile_name}.json")

    yield

    # Clean up
    FlowField.verbose = True
    for file in glob.glob(f"src/results/{field_name}_*.npy"):
        os.remove(file)
    for file in glob.glob(f"src/plots/{field_name}_*.png"):
        os.remove(file)


@pytest.mark.unit
def test_query_meshgrid():
    """Test querying the field with meshgrid mode"""
    # Query file content
    content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-5, -5, 0],
            "high_bounds": [5, 5, 0],
            "step_size": 0.2,
            "chunk_size": 5,
            "time": 0,
        },
        "plot": {"axis": "z", "index": 0, "size": [640, 480]},
    }
    request = "__test_mesh__"
    file_io.write("queries", "__test_mesh__", content, format="json")
    response = query.handle_request(request=request, format="file")
    # Check the response showing the plot is saved
    assert "Plot saved to plots" in response, f"{response}"

    # Change the plot axis to y
    content["params"]["low_bounds"] = [-1, 2, -1]
    content["params"]["high_bounds"] = [1, 2, 1]
    content["plot"]["axis"] = "y"
    response = query.handle_request(request=json.dumps(content))
    # Check the response showing the plot is saved
    assert "Plot saved to plots" in response, f"{response}"

    # Change the plot axis to x
    content["params"]["low_bounds"] = [-1, -1, -1]
    content["params"]["high_bounds"] = [1, 1, 1]
    content["plot"]["axis"] = "x"
    response = query.handle_request(request=json.dumps(content))
    # Check the response showing the plot is saved
    assert "Plot saved to plots" in response, f"{response}"

    # Clean up
    os.remove(f"src/queries/{request}.json")


@pytest.mark.unit
def test_query_points():
    """Test querying the field with points mode"""
    # Query file content
    content = {
        "mode": "points",
        "params": {
            "coords": [[0, 1, 0], [2, 1.5, 2.1]],
        },
    }
    response = query.handle_request(request=json.dumps(content))
    # Check the response showing the velocity calculation is complete
    assert "Velocity calculation complete (mode: points)." in response, f"{response}"

    # Remove the coordinates, shoud now use default value (0, 0, 0)
    del content["params"]["coords"]
    response = query.handle_request(request=json.dumps(content))
    # Check the response showing the velocity calculation is complete
    assert "Velocity calculation complete (mode: points)." in response, f"{response}"


@pytest.mark.unit
def test_query_meshgrid_exceptions():
    """Test query exceptions in meshgrid mode"""
    # Not json string
    content = "invalid"
    with pytest.raises(Exception, match=r"^Invalid query request string"):
        query.handle_request(request=content)

    # Params not dict
    content = json.dumps({"mode": "meshgrid", "params": "invalid"})
    with pytest.raises(TypeError, match=r"^Invalid request parameters"):
        query.handle_request(request=content)

    # Invalid meshgrid params
    content = json.dumps({"mode": "meshgrid", "params": {"low_bounds": [-100, 0, 0]}})
    with pytest.raises(Exception, match=r"^Error calculating velocity in meshgrid"):
        query.handle_request(request=content)


@pytest.mark.unit
def test_query_points_exceptions():
    """Test query exceptions in points mode"""
    # Invalid points params
    content = {
        "mode": "points",
        "params": {
            "coords": "invalid",
        },
    }
    with pytest.raises(Exception, match=r"^Invalid request parameters"):
        query.handle_request(request=json.dumps(content))

    # Invalid bounds
    content["params"]["coords"] = [[-100, 0, 0]]
    with pytest.raises(Exception, match=r"^Error calculating velocity at points"):
        query.handle_request(request=json.dumps(content))


@pytest.mark.unit
def test_query_mode_exceptions():
    """Test query exceptions with invalid mode"""
    # Invalid mode
    content = {"mode": "invalid", "params": {}}
    with pytest.raises(Exception, match=r"^Invalid request mode"):
        query.handle_request(request=json.dumps(content))


@pytest.mark.unit
def test_query_plot_exceptions():
    """Test query exceptions with invalid plot params"""
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
    with pytest.raises(Exception, match="Invalid plot index"):
        query.handle_request(request=json.dumps(content))

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
    with pytest.raises(Exception, match="Invalid plot axis"):
        query.handle_request(request=json.dumps(content))
