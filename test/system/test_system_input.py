import os
import pytest
from modules import file_io
import main


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    profile_content = {
        "settings": {},
        "variants": [
            {"density": 200.0, "intensity": 0.75, "length_scale": 0.1},
            {"density": 10.0, "intensity": 1.0, "length_scale": 0.2},
            {"density": 0.5, "intensity": 1.1, "length_scale": 0.5},
            {"density": 0.005, "intensity": 1.2, "length_scale": 1.5},
        ],
    }
    file_io.write("profiles", "test_system_input_profile", profile_content, "json")

    main.main(
        [
            "new",
            "-p",
            "test_system_input_profile",
            "-n",
            "test_system_input_field",
            "-d",
            "10",
            "10",
            "10",
        ]
    )

    yield

    os.remove("src/profiles/test_system_input_profile.json")
    os.remove("src/fields/test_system_input_field.pkl")


@pytest.mark.system
def test_query_coordinate(capsys):
    query_content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-100, -100, 0],
            "high_bounds": [100, 100, 0],
            "step_size": 0.1,
            "chunk_size": 5,
            "time": 0,
        }
    }
    file_io.write("queries", "test_system_input_query", query_content, "json")
    main.main(["query", "-n", "test_system_input_field", "-q", "test_system_input_query"])
    captured = capsys.readouterr()
    assert "Bounds must be within the flow field" in captured.err

    # Clean up
    os.remove("src/queries/test_system_input_query.json")
