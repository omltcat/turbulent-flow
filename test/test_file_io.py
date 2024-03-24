import pytest
import os
import modules.file_io as file_io


# def test_file_io_read():
#     file_type = "profiles"
#     name = "center_upright"

#     # Read the file and check the content
#     try:
#         content = file_io.read(file_type, name)
#     except file_io.FileNotExist:
#         pytest.fail(f"File not found at ./{file_type}/{name}.json")

#     assert content['variants'][0]['orientation'] == [0, 0, 1]


def test_file_io():
    # Test writing to the file
    file_type = "profiles"
    name = "__test__"
    content = {"key": "value", "list": [1, 2, 3]}
    try:
        file_io.write(file_type, name, content, indent=4)
    except file_io.FailToWrite:
        pytest.fail(f"Failed to write to file ./{file_type}/{name}.json")

    try:
        content_read = file_io.read(file_type, name)
    except file_io.FileNotExist:
        pytest.fail(f"File not found at ./{file_type}/{name}.json")

    assert content == content_read

    # Clean up
    os.remove(f"./src/{file_type}/{name}.json")


def test_file_io_read_fail():
    type = "profiles"
    name = "__not_exist__"

    # Read the file and check the content
    try:
        _ = file_io.read(type, name)
        pytest.fail('Should have raised FileNotExist')
    except file_io.FileNotExist:
        return


def test_file_io_write_fail():
    # Test writing to the file
    file_type = "__not_exist__"
    name = "__test__"
    content = {"key": "value", "list": [1, 2, 3]}
    try:
        file_io.write(file_type, name, content, indent=4)
        pytest.fail('Should have raised FailToWrite')
    except file_io.FailToWrite:
        return
