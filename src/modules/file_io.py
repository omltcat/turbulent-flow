import os
import json

DIR = os.path.join(os.path.dirname(__file__), '..')


class FileNotExist(Exception):
    pass


class FailToWrite(Exception):
    pass


def read(type, name):
    try:
        with open(f'{DIR}/{type}/{name}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotExist(f'File not found at ./{type}/{name}.json')


def write(type, name, content, indent=None):
    try:
        # os.makedirs(type, exist_ok=True)
        with open(f'{DIR}/{type}/{name}.json', 'w') as file:
            json.dump(content, file, indent=indent)
    except Exception as e:
        raise FailToWrite(f'Failed to write to file: {e}')
