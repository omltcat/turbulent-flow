import pytest
# import numpy as np
import modules.eddy_profile as eddy_profile
import modules.file_io as file_io
import os


def test_eddy_profile():
    # Test valid profile
    name = "__valid__"
    content = {
        "settings": {},
        "variants": [
            {
                "density": 0.1,
                "intensity": 1.15,
                "length_scale": 1
            }
        ]
    }
    file_io.write("profiles", name, content)
    try:
        profile = eddy_profile.EddyProfile(name)
    except eddy_profile.InvalidProfile:
        pytest.fail(f"Failed to create EddyProfile with {name}")

    assert profile.get_settings() == {}
    assert profile.get_params()[0]['intensity'] == 1.15
    assert profile.get_variant_count() == 1
    assert profile.get_density(0) == 0.1
    assert profile.get_length_scale(0) == 1
    assert profile.get_intensity(0) == 1.15
    # assert np.array_equal(profile.get_orientation(0), [0, 0, 1])
    # assert np.array_equal(profile.get_center(0), [5, 5, 5])

    # Cleanup
    os.remove(f"./src/profiles/{name}.json")


def test_eddy_profile_invalid():
    # Test invalid profile
    name = "__invalid__"

    # Eddy type not a list
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
        "length_scale": 'string',
    }]}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # Intensity is not a positive number
    content = {"variants": [{
        "density": 1,
        "length_scale": 1,
    }]}
    file_io.write("profiles", name, content)
    with pytest.raises(eddy_profile.InvalidProfile):
        _ = eddy_profile.EddyProfile(name)

    # # Orientation is not a list
    # content = {"variants": [{
    #     "density": 1,
    #     "length_scale": 1,
    #     "intensity": 1,
    #     "orientation": 'string',
    #     }]}
    # file_io.write("profiles", name, content)
    # with pytest.raises(eddy_profile.InvalidProfile):
    #     _ = eddy_profile.EddyProfile(name)

    # # Orientation is not a list of 3 numbers
    # content = {"variants": [{
    #     "density": 1,
    #     "length_scale": 1,
    #     "intensity": 1,
    #     "orientation": [1, 2],
    #     }]}
    # file_io.write("profiles", name, content)
    # with pytest.raises(eddy_profile.InvalidProfile):
    #     _ = eddy_profile.EddyProfile(name)

    # # Orientation is a zero vector
    # content = {"variants": [{
    #     "density": 1,
    #     "length_scale": 1,
    #     "intensity": 1,
    #     "orientation": [0, 0, 0],
    #     }]}
    # file_io.write("profiles", name, content)
    # with pytest.raises(eddy_profile.InvalidProfile):
    #     _ = eddy_profile.EddyProfile(name)

    # # Center is not a list
    # content = {"variants": [{
    #     "density": 1,
    #     "length_scale": 1,
    #     "intensity": 1,
    #     "center": 'string',
    #     }]}
    # file_io.write("profiles", name, content)
    # with pytest.raises(eddy_profile.InvalidProfile):
    #     _ = eddy_profile.EddyProfile(name)

    # Clenup
    os.remove(f"./src/profiles/{name}.json")
