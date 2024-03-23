import modules.file_io as file_io
import modules.utils as utils
from typing import List, Dict


class InvalidProfile(Exception):
    pass


class EddyProfile:
    def __init__(self, name):
        data: dict = file_io.read('profiles', name)

        self.name: str = name
        self.settings: dict = data.get('settings', {})
        self.params: List[Dict] = data.get('eddy_types', [])

        if not isinstance(self.params, list):
            raise InvalidProfile('Eddy types must be a list (array)')
        if len(self.params) == 0:
            raise InvalidProfile('Eddy types list must not be empty')

        self.weights = [eddy_type.get('weight', 1) for eddy_type in self.params]

        for i in range(len(self.weights)):
            if not utils.is_positive(self.weights[i]):
                raise InvalidProfile('Weight must be a positive number')
            if not utils.is_positive(self.params[i].get('length_scale')):
                raise InvalidProfile('Length scale must be a positive number')
            if not utils.is_positive(self.params[i].get('intensity')):
                raise InvalidProfile('Intensity must be a positive number')

    def get_params(self):
        return self.params

    def get_weights(self):
        return self.weights
