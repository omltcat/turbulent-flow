import pytest
import modules.shape_function as shape_function


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    shape_function.set_active('gaussian')
    shape_function.set_cutoff(2.0)
    yield
    shape_function.set_active('gaussian')
    shape_function.set_cutoff(2.0)


@pytest.mark.unit
def test_shape_function():
    length_scale = 1.0
    shape_function.set_active('gaussian')
    q = shape_function.active(1.5, length_scale)
    assert q > 0

    q = shape_function.active(4, length_scale)
    assert q == 0

    shape_function.set_cutoff(5)
    q = shape_function.active(4, length_scale)
    assert q > 0
    assert shape_function.get_cutoff() == 5

    shape_function.set_active(shape_function.quadratic)
    q = shape_function.active(0.5, length_scale)
    assert q > 0

    q = shape_function.active(1.5, length_scale)
    assert q == 0


@pytest.mark.unit
def test_shape_function_exceptions():
    with pytest.raises(ValueError):
        shape_function.set_active('non_existent_function')

    with pytest.raises(ValueError):
        shape_function.set_active(123)

    with pytest.raises(ValueError):
        shape_function.set_cutoff(-1)
