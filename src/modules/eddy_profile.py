from typing import List, Dict
import numpy as np
import modules.file_io as file_io
import modules.utils as utils


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

        for i, variant in enumerate(self.variants):
            if not utils.is_positive(variant.get('density')):
                raise InvalidProfile('Eddy density must be a positive number')
            if not utils.is_positive(variant.get('length_scale')):
                raise InvalidProfile('Eddy length-scale must be a positive number')
            if not utils.is_positive(variant.get('intensity')):
                raise InvalidProfile('Eddy intensity must be a positive number')

            # if variant.get('orientation') is not None:
            #     if not isinstance(variant['orientation'], list) or len(variant['orientation']) != 3:
            #         raise InvalidProfile('Eddy orientation must be a list of 3 numbers for x, y, z')
            #     norm = np.linalg.norm(variant['orientation'])
            #     if norm == 0:
            #         raise InvalidProfile('Eddy orientation must not be a zero vector')
            #     variant['orientation'] = np.array(variant['orientation']) / norm

            # if variant.get('center') is not None:
            #     if not isinstance(variant['center'], list) or len(variant['center']) != 3:
            #         raise InvalidProfile('Eddy center must be a list of 3 numbers for x, y, z')
            #     variant['center'] = np.array(variant['center'])

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
        return self.variants[index]["intensity"]

    def get_density_array(self):
        return np.array(
            [variant["density"] for variant in self.variants]
        )

    def get_length_scale_array(self):
        return np.array(
            [variant["length_scale"] for variant in self.variants]
        )

    def get_intensity_array(self):
        return np.array(
            [variant["intensity"] for variant in self.variants]
        )

    # def get_orientation(self, index: int):
    #     return self.variants[index].get('orientation', None)

    # def get_center(self, index: int):
    #     return self.variants[index].get('center', None)
