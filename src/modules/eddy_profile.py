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
        self.variants: List[Dict] = data.get('variants', [])

        if not isinstance(self.variants, list):
            raise InvalidProfile('Eddy variants must be a list (array)')
        if len(self.variants) == 0:
            raise InvalidProfile('Eddy variants list must not be empty')

        for i in range(len(self.variants)):
            if not utils.is_positive(self.variants[i].get('density')):
                raise InvalidProfile('Eddy density must be a positive number')
            if not utils.is_positive(self.variants[i].get('length_scale')):
                raise InvalidProfile('Eddy length-scale must be a positive number')
            if not utils.is_positive(self.variants[i].get('intensity')):
                raise InvalidProfile('Eddy intensity must be a positive number')

    def get_settings(self):
        return self.settings

    def get_params(self):
        return self.variants

    def get_variant_count(self):
        return len(self.variants)

    def get_density(self, index: int):
        return self.variants[index]['density']

    def get_length_scale(self, index: int):
        return self.variants[index]['length_scale']

    def get_intensity(self, index: int):
        return self.variants[index]['intensity']

    def get_orientation(self, index: int):
        return self.variants[index].get('orientation', None)

    def get_center(self, index: int):
        return self.variants[index].get('center', None)
