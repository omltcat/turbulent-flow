import os
import json
import numpy as np

DIR = os.path.join(os.path.dirname(__file__), "..")


class FileNotExist(Exception):
    pass


class FailToWrite(Exception):
    pass


def read(type, name):
    try:
        with open(f"{DIR}/{type}/{name}.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotExist(f"File not found at ./{type}/{name}.json")


def write(type, name, content, indent=None):
    try:
        os.makedirs(f"{DIR}/{type}", exist_ok=True)
        with open(f"{DIR}/{type}/{name}.json", "w") as file:
            json.dump(content, file, indent=indent)
    except Exception as e:
        raise FailToWrite(f"Failed to write to file: {e}")


def read_cache(type, name):
    try:
        return np.load(f"{DIR}/.cache/{type}/{name}.npy")
    except FileNotFoundError:
        raise FileNotExist(f"File not found at ./.cache/{type}/{name}.npy")


def write_cache(type, name, content):
    try:
        os.makedirs(f"{DIR}/.cache/{type}", exist_ok=True)
        np.save(f"{DIR}/.cache/{type}/{name}.npy", content)
        # print(f"Cache saved: {name}.npy")
    except Exception as e:
        raise FailToWrite(f"Failed to write to file: {e}")


def clear_cache(type):
    try:
        os.makedirs(f"{DIR}/.cache/{type}", exist_ok=True)
        for file in os.listdir(f"{DIR}/.cache/{type}"):
            os.remove(f"{DIR}/.cache/{type}/{file}")
    except Exception as e:
        raise FailToWrite(f"Failed to clear cache: {e}")
