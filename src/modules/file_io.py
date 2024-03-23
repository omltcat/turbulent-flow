import os
import json

class FileNotExist(Exception):
    pass

class FailToWrite(Exception):
    pass

def read(type, name):
    try:
        with open(f'./{type}/{name}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotExist(f'File not found at ./{type}/{name}.json')

def write(type, name, content):
    try:
        os.makedirs(type, exist_ok=True)
        with open(f'./{type}/{name}.json', 'w') as file:
            json.dump(content, file)
    except Exception as e:
        raise FailToWrite(f'Failed to write to file: {e}')