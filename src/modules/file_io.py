import os
import json
import cupy as cp
import pickle

DIR = os.path.join(os.path.dirname(__file__), "..")


class FailToRead(Exception):
    pass


class FailToWrite(Exception):
    pass


def read(sub_dir: str, name: str, format="json"):
    try:
        if format == "json":
            with open(f"{DIR}/{sub_dir}/{name}.{format}", "r") as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    raise ValueError("Not a JSON object, please check provided examples")
                return data
        if format == "npy":
            return cp.load(f"{DIR}/{sub_dir}/{name}.{format}")
        if format == "obj":
            with open(f"{DIR}/{sub_dir}/{name}.pkl", "rb") as file:
                return pickle.load(file)
        raise ValueError(f"Invalid format: {format}")
    except Exception as e:
        raise FailToRead(f"Cannot read {sub_dir} file '{name}': {e}")


def write(sub_dir: str, name: str, content, format='json', indent=None):
    try:
        os.makedirs(f"{DIR}/{sub_dir}", exist_ok=True)
        if format == "npy":
            return cp.save(f"{DIR}/{sub_dir}/{name}.npy", content)
        if format == "json":
            with open(f"{DIR}/{sub_dir}/{name}.json", "w") as file:
                return json.dump(content, file, indent=indent)
        if format == "obj":
            with open(f"{DIR}/{sub_dir}/{name}.pkl", "wb") as file:
                return pickle.dump(content, file)
        if format == 'png':
            return content.savefig(f"{DIR}/{sub_dir}/{name}.png")
        raise FailToWrite(f"Invalid format: {format}")
    except IOError as e:
        raise FailToWrite(f"Cannot write file: {e}")


def clear(sub_dir):
    try:
        os.makedirs(f"{DIR}/{sub_dir}", exist_ok=True)
        for file in os.listdir(f"{DIR}/{sub_dir}"):
            if os.path.isfile(f"{DIR}/{sub_dir}/{file}"):
                os.remove(f"{DIR}/{sub_dir}/{file}")
    except IOError as e:
        raise FailToWrite(f"Cannot clear directory: {e}")
