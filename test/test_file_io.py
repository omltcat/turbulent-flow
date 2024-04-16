import pytest
import os
from unittest.mock import patch, mock_open
import modules.file_io as file_io


@pytest.mark.unit
def test_file_io():
    """Test writing content to a file and reading it back"""
    sub_dir = "profiles"
    name = "__test__"
    content = {"key": "value", "list": [1, 2, 3]}
    try:
        file_io.write(sub_dir, name, content, indent=4)
    except file_io.FailToWrite:
        pytest.fail(f"Failed to write to file ./{sub_dir}/{name}.json")

    # Read the file and check the content
    try:
        content_read = file_io.read(sub_dir, name)
    except file_io.FailToRead:
        pytest.fail(f"File not found at ./{sub_dir}/{name}.json")

    assert content == content_read

    # Clean up
    os.remove(f"./src/{sub_dir}/{name}.json")


@pytest.mark.unit
def test_file_io_read_fail():
    """Test reading a file that does not exist"""
    sub_dir = "profiles"
    name = "__not_exist__"

    # Read the file and check the content, should raise an exception
    with pytest.raises(file_io.FailToRead):
        _ = file_io.read(sub_dir, name)


@pytest.mark.unit
def test_file_io_read_fail_format():
    """Test reading a file with invalid format"""
    sub_dir = "profiles"
    name = "__not_dict__"
    content = "not a dict"

    # Write the file
    file_io.write(sub_dir, name, content)
    with pytest.raises(file_io.FailToRead):
        _ = file_io.read(sub_dir, name)
    os.remove(f"./src/{sub_dir}/{name}.json")

    # Test with invalid format, should raise an exception
    with pytest.raises(file_io.FailToRead):
        _ = file_io.read(sub_dir, name, format="invalid")


@pytest.mark.unit
def test_file_io_write_fail():
    """Test writing content to a file that fails"""
    sub_dir = "profiles"
    name = "__test_write_fail__"
    content = {"key": "value", "list": [1, 2, 3]}

    # Mock the open function to raise an IOError when called
    with patch('builtins.open', mock_open()) as m:
        m.side_effect = IOError
        with pytest.raises(file_io.FailToWrite):
            file_io.write(sub_dir, name, content, indent=4)

    # Test with invalid format
    with pytest.raises(file_io.FailToWrite):
        file_io.write(sub_dir, name, content, format="invalid")


@pytest.mark.unit
def test_file_io_clear_fail():
    """Test clearing a directory that fails"""
    sub_dir = "profiles"

    # Mock the os.remove function to raise an OSError when called
    with patch('os.remove') as mock_remove:
        mock_remove.side_effect = OSError
        with pytest.raises(file_io.FailToWrite):
            file_io.clear(sub_dir)
