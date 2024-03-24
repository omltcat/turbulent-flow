import pytest
import modules.eddy_profile as eddy_profile
import modules.file_io as file_io
import os


def test_eddy_profile():
    # Test valid profile
    name = "center_upright"
    try:
        profile = eddy_profile.EddyProfile(name)
    except eddy_profile.InvalidProfile:
        pytest.fail(f"Failed to create EddyProfile with {name}")

    assert profile.get_params()[0]['orientation']['z'] == 1


def test_eddy_profile_invalid():
    # Test invalid profile
    name = "__invalid__"

    # Eddy typy not a list
    content = {"variants": {}}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # Eddy types list is empty
    content = {"variants": []}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # density is not a positive number
    content = {"variants": [{"density": -1}]}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # Length scale is not a positive number
    content = {"variants": [{
        "density": 1,
        "length_scale": -1,
        }]}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # Intensity is not a positive number
    content = {"variants": [{
        "density": 1,
        "length_scale": 1,
        "intensity": -1,
        }]}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # Clenup
    os.remove(f"./src/profiles/{name}.json")
