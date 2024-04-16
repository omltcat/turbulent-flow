import os
import json
import pytest
from modules.flow_field import FlowField
from modules.eddy_profile import EddyProfile
from modules.query import Query
from modules import file_io


@pytest.mark.slow
@pytest.mark.performance
@pytest.mark.system
def test_query_performance():
    # Eddy profile
    FlowField.verbose = True
    profile_name = "__test__"
    content = {
        "settings": {},
        "variants": [
            {"density": 1200, "intensity": 0.8, "length_scale": 0.05},
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
            "time": 0,
            "do_return": True,
            # "do_cache": True,
        },
        "plot": {"axis": "x", "index": 0, "size": [1280, 960]},
    }
    response = query.handle_request(request=json.dumps(content))
    if isinstance(response, str):
        print(response)
