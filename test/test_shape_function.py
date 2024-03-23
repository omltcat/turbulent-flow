import pytest
import numpy as np
import modules.shape_function as shape_function


def test_shape_function():
    length_scale = 1.0

    shape_function.set_active(shape_function.exp_2pi)

    rel_pos = np.array([1.1, 1.1, 1.1])
    q = shape_function.active(rel_pos, length_scale)
    assert q > 0

    rel_pos = np.array([2.1, 2.1, 2.1])
    q = shape_function.active(rel_pos, length_scale)
    assert q == 0

    shape_function.set_active('quadratic')
    q = shape_function.active(rel_pos, length_scale)
    assert q == 0

    rel_pos = np.array([0.5, 0.5, 0.5])
    q = shape_function.active(rel_pos, length_scale)
    assert q > 0


def test_shape_function_exceptions():
    with pytest.raises(ValueError):
        shape_function.set_active('non_existent_function')

    with pytest.raises(ValueError):
        shape_function.set_active(123)
