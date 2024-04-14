import os
import glob
import pytest
from modules import file_io
import main


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # Create a profile file
    profile_content = {
        "settings": {},
        "variants": [
            {"density": 200.0, "intensity": 0.75, "length_scale": 0.1},
            {"density": 10.0, "intensity": 1.0, "length_scale": 0.2},
            {"density": 0.5, "intensity": 1.1, "length_scale": 0.5},
            {"density": 0.005, "intensity": 1.2, "length_scale": 1.5},
        ],
    }
    file_io.write("profiles", "main_test_profile", profile_content, "json")

    # Create a query file
    query_content = {
        "mode": "meshgrid",
        "params": {
            "low_bounds": [-5, -5, 0],
            "high_bounds": [5, 5, 0],
            "step_size": 0.1,
            "chunk_size": 5,
            "time": 0,
        }
    }
    file_io.write("queries", "main_test_query", query_content, "json")
    yield
    os.remove("src/profiles/main_test_profile.json")
    os.remove("src/queries/main_test_query.json")
    for file in glob.glob("src/results/main_test_*.npy"):
        os.remove(file)
    for file in glob.glob("src/plots/main_test_*.png"):
        os.remove(file)


@pytest.mark.unit
def test_main_new():
    args = [
        "new",
        "-p",
        "main_test_profile",
        "-n",
        "main_test_field",
        "-d",
        "10",
        "10",
        "10",
        "-v",
        "0",
    ]
    main.main(args)
    assert os.path.exists("src/fields/main_test_field.pkl")


@pytest.mark.unit
def test_main_query():
    args = [
        "query",
        "-n",
        "main_test_field",
        "-q",
        "main_test_query",
        "-s",
        "gaussian",
        "-c",
        "1.0",
    ]
    main.main(args)
    assert glob.glob("src/results/main_test_*.npy")


@pytest.mark.unit
def test_main_new_exceptions(capsys):
    args = [
        "new",
        "-p",
        "non_existent_profile",
        "-n",
        "main_test_field",
        "-d",
        "10",
        "10",
        "10",
    ]
    main.main(args)
    captured = capsys.readouterr()
    assert "Error creating new field: Cannot read profiles file" in captured.err


@pytest.mark.unit
def test_main_query_field_not_exist(capsys):
    args = [
        "query",
        "-n",
        "non_existent_field",
        "-q",
        "main_test_query",
        "-s",
        "gaussian",
        "-c",
        "1.0",
    ]
    main.main(args)
    captured = capsys.readouterr()
    assert "Error loading field 'non_existent_field': Cannot read fields file" in captured.err


@pytest.mark.unit
def test_main_query_shape_function_exception(capsys):
    args = [
        "query",
        "-n",
        "main_test_field",
        "-q",
        "main_test_query",
        "-s",
        "non_existent_sf"
    ]
    main.main(args)
    captured = capsys.readouterr()
    assert "Error setting shape function: Shape function \"non_existent_sf\" is not defined." in captured.err


@pytest.mark.unit
def test_main_query_exception(capsys):
    args = [
        "query",
        "-n",
        "main_test_field",
        "-q",
        "non_existent_query",
    ]
    main.main(args)
    captured = capsys.readouterr()
    assert "Error handling query: Cannot read queries file 'non_existent_query'" in captured.err
