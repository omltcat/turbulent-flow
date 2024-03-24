import pytest
import modules.shape_function as shape_function


def test_shape_function():
    length_scale = 1.0

    shape_function.set_active('gaussian')
    q = shape_function.active(1.5, length_scale)
    assert q > 0

    q = shape_function.active(4, length_scale)
    assert q == 0

    shape_function.set_active('quadratic')
    q = shape_function.active(0.5, length_scale)
    assert q > 0

    q = shape_function.active(1.5, length_scale)
    assert q == 0


def test_shape_function_exceptions():
    with pytest.raises(ValueError):
        shape_function.set_active('non_existent_function')

    with pytest.raises(ValueError):
        shape_function.set_active(123)
