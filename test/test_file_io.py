import pytest
import os
import modules.file_io

def test_file_io():
    type = "profiles"
    name = "file_io_test"
    content = {"test": "string", "data": [1, 2, 3]}

    # Test writing to the file
    try:
        modules.file_io.write(type, name, content)
    except modules.file_io.FailToWrite:
        pytest.fail(f"Failed to write to file ./{type}/{name}.json")

    # Read the file and compare the content
    try:
        written_content = modules.file_io.read(type, name)
    except modules.file_io.FileNotExist:
        pytest.fail(f"File not found at ./{type}/{name}.json")

    assert written_content == content

    # Delete the file
    try:
        file_path = f"./{type}/{name}.json"
        os.remove(file_path)
    except OSError:
        pytest.fail(f"Failed to delete file {file_path}")
