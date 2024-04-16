import pytest
import modules.eddy_profile as eddy_profile
import modules.file_io as file_io
import os


@pytest.mark.unit
def test_eddy_profile():
    """Test with a valid profile"""
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

    # Create EddyProfile object
    try:
        profile = eddy_profile.EddyProfile(name)
    except eddy_profile.InvalidProfile:
        pytest.fail(f"Failed to create EddyProfile with {name}")

    # no settings are passed
    assert profile.get_settings() == {}
    # intensity of first variant is 1.15
    assert profile.get_params()[0]['intensity'] == 1.15
    # there is only one variant
    assert profile.get_variant_count() == 1
    # density of first variant is 0.1
    assert profile.get_density(0) == 0.1
    # length scale of first variant is 1
    assert profile.get_length_scale(0) == 1
    # intensity of first variant is 1.15
    assert profile.get_intensity(0) == 1.15
    # Cleanup
    os.remove(f"./src/profiles/{name}.json")


@pytest.mark.unit
def test_eddy_profile_invalid():
    """Test with invalid profiles for exceptions"""
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

    # Clenup
    os.remove(f"./src/profiles/{name}.json")
