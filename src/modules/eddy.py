from typing import List, Dict
import numpy as np
import modules.utils as utils
import modules.shape_function as shape_function

LOOP_IJK = [-1, 0, 1]


class Eddy:
    field = np.array([10, 10, 10])
    half_field = field / 2
    variants:  List[Dict] = []

    def __init__(self, variant_index: int):
        self.variant_index = variant_index

        # Set initial center positions
        self.init_x = np.random.uniform(-self.half_field[0], self.half_field[0])
        self.y = {}
        self.z = {}
        self.center = np.array([self.init_x, 0, 0])
        self.get_center(0)
        self.get_center(1)
        self.get_center(2)

        # Set orientation
        self.orientation = utils.random_unit_vector()

    def get_variant(self):
        return self.variants[self.variant_index]

    def get_length_scale(self):
        return self.variants[self.variant_index]['length_scale']

    def get_intensity(self):
        return self.variants[self.variant_index]['intensity']

    def get_orientation(self):
        return self.orientation

    def get_center(self, iter: int):
        self.center[0] = self.init_x
        if iter in self.y:
            self.center[1] = self.y[iter]
            self.center[2] = self.z[iter]
        else:
            self.y[iter] = np.random.uniform(-self.half_field[1], self.half_field[1])
            self.z[iter] = np.random.uniform(-self.half_field[2], self.half_field[2])
            self.center[1] = self.y[iter]
            self.center[2] = self.z[iter]
        return self.center

    def get_vel(self, pos: np.ndarray, iter: int, offset: float):
        vel = np.zeros(3)
        for i in LOOP_IJK:
            center = self.get_center(iter+i)
            center[0] += offset
            center[0] += self.field[0] * i
            base_y = center[1]
            base_z = center[2]
            for j in LOOP_IJK:
                center[1] = base_y + j * self.field[1]
                for k in LOOP_IJK:
                    center[2] = base_z + k * self.field[2]
                    r = (pos - center) / self.get_length_scale()
                    d = np.linalg.norm(r)
                    q = shape_function.active(d, self.get_length_scale())
                    vel = vel + q * np.cross(r, self.orientation*self.get_intensity()) if d > 0 else vel
        return vel

    def set_orientation(self, orientation: np.ndarray):
        if len(orientation) != 3:
            raise ValueError('Eddy orientation must be a list of 3 numbers for x, y, z')
        norm = np.linalg.norm(orientation)
        if norm == 0:
            raise ValueError('Eddy orientation must not be a zero vector')
        self.orientation = np.array(orientation) / norm

    @classmethod
    def set_field_dimension(cls, field_dimensions: np.ndarray):
        cls.field = field_dimensions
        cls.half_field = field_dimensions / 2

    @classmethod
    def set_variants(cls, variants: list):
        cls.variants = variants
