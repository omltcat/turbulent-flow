import pytest
import os
import modules.file_io as file_io


# def test_file_io_read():
#     sub_dir = "profiles"
#     name = "center_upright"

#     # Read the file and check the content
#     try:
#         content = file_io.read(sub_dir, name)
#     except file_io.FileNotExist:
#         pytest.fail(f"File not found at ./{sub_dir}/{name}.json")

#     assert content['variants'][0]['orientation'] == [0, 0, 1]


def test_file_io():
    # Test writing to the file
    sub_dir = "profiles"
    name = "__test__"
    content = {"key": "value", "list": [1, 2, 3]}
    try:
        file_io.write(sub_dir, name, content, indent=4)
    except file_io.FailToWrite:
        pytest.fail(f"Failed to write to file ./{sub_dir}/{name}.json")

    try:
        content_read = file_io.read(sub_dir, name)
    except file_io.FailToRead:
        pytest.fail(f"File not found at ./{sub_dir}/{name}.json")

    assert content == content_read

    # Clean up
    os.remove(f"./src/{sub_dir}/{name}.json")


def test_file_io_read_fail():
    sub_dir = "profiles"
    name = "__not_exist__"

    # Read the file and check the content
    with pytest.raises(file_io.FailToRead):
        _ = file_io.read(sub_dir, name)


def test_file_io_read_fail_format():
    sub_dir = "profiles"
    name = "__not_dict__"
    content = "not a dict"

    # Write the file
    file_io.write(sub_dir, name, content)
    with pytest.raises(file_io.FailToRead):
        _ = file_io.read(sub_dir, name)
    os.remove(f"./src/{sub_dir}/{name}.json")

    with pytest.raises(file_io.FailToRead):
        _ = file_io.read(sub_dir, name, format="invalid")


def test_file_io_write_fail():
    # Test writing to the file
    sub_dir = "__:::////__"
    name = "__test__"
    content = {"key": "value", "list": [1, 2, 3]}
    with pytest.raises(file_io.FailToWrite):
        file_io.write(sub_dir, name, content, indent=4)

    with pytest.raises(file_io.FailToWrite):
        file_io.write('profiles', name, content, format="invalid")


def test_file_io_clear_fail():
    sub_dir = "__:::////__"
    with pytest.raises(file_io.FailToWrite):
        file_io.clear(sub_dir)
