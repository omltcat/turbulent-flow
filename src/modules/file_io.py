"""
This module provides functions to read and write files in different formats.
"""
import os
import json
import numpy as np
import pickle

DIR = os.path.join(os.path.dirname(__file__), "..")


class FailToRead(Exception):
    pass


class FailToWrite(Exception):
    pass


def read(sub_dir: str, name: str, format="json"):
    """
    Read a file from the specified sub-directory.

    Parameters
    ----------
    sub_dir : str
        Sub-directory to read from.
    name : str
        Name of the file to read.
    format : str, optional
        Format of the file, by default "json".

    Returns
    -------
    dict or np.ndarray
        File content in the specified format.

    Raises
    ------
    FailToRead
        If the file cannot be read.
    """
    try:
        # Json file, return as dict
        if format == "json":
            with open(f"{DIR}/{sub_dir}/{name}.{format}", "r") as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise ValueError("Not a JSON object, please check provided examples")
                return data
        # Numpy file, return as np.ndarray
        if format == "npy":
            return np.load(f"{DIR}/{sub_dir}/{name}.{format}")
        # Pickle file, return as object
        if format == "obj":
            with open(f"{DIR}/{sub_dir}/{name}.pkl", "rb") as file:
                return pickle.load(file)
        raise ValueError(f"Invalid format: {format}")
    except Exception as e:
        raise FailToRead(f"Cannot read {sub_dir} file '{name}': {e}")


def write(sub_dir: str, name: str, content, format='json', indent=None):
    """
    Write a file to the specified sub-directory.

    Parameters
    ----------
    sub_dir : str
        Sub-directory to write to.
    name : str
        Name of the file to write.
    content : dict or np.ndarray
        Content to write to the file.
    format : str, optional
        Format of the file, by default "json".
    indent : int, optional
        Indentation level for JSON files, by default None.

    Raises
    ------
    FailToWrite
        If the file cannot be written.
    """
    try:
        os.makedirs(f"{DIR}/{sub_dir}", exist_ok=True)
        # numpy array, save as .npy
        if format == "npy":
            return np.save(f"{DIR}/{sub_dir}/{name}.npy", content)
        # dict, save as .json
        if format == "json":
            with open(f"{DIR}/{sub_dir}/{name}.json", "w") as file:
                return json.dump(content, file, indent=indent)
        # object, save as .pkl (pickle)
        if format == "obj":
            with open(f"{DIR}/{sub_dir}/{name}.pkl", "wb") as file:
                return pickle.dump(content, file)
        # matplotlib figure, save as .png
        if format == 'png':
            return content.savefig(f"{DIR}/{sub_dir}/{name}.png")
        raise FailToWrite(f"Invalid format: {format}")
    except IOError as e:
        raise FailToWrite(f"Cannot write file: {e}")


def clear(sub_dir):
    """
    Clear the specified sub-directory.

    Parameters
    ----------
    sub_dir : str
        Sub-directory to clear.

    Raises
    ------
    FailToWrite
        If the directory cannot be cleared.
    """
    try:
        os.makedirs(f"{DIR}/{sub_dir}", exist_ok=True)
        for file in os.listdir(f"{DIR}/{sub_dir}"):
            if os.path.isfile(f"{DIR}/{sub_dir}/{file}"):
                os.remove(f"{DIR}/{sub_dir}/{file}")
    except IOError as e:
        raise FailToWrite(f"Cannot clear directory: {e}")
