import pytest
import modules.shape_function as shape_function


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Setup and teardown for the module tests"""
    shape_function.set_active('gaussian')
    shape_function.set_cutoff(2.0)
    yield
    shape_function.set_active('gaussian')
    shape_function.set_cutoff(2.0)


@pytest.mark.unit
def test_shape_function():
    """Test shape function with different functions and cutoffs"""

    # Test gaussian function with default cutoff 2.0
    length_scale = 1.0
    shape_function.set_active('gaussian')
    # Within cutoff, q should be positive
    q = shape_function.active(1.5, length_scale)
    assert q > 0

    # Outside cutoff, q should be zero
    q = shape_function.active(4, length_scale)
    assert q == 0

    # Change cutoff to 5.0
    shape_function.set_cutoff(5)
    # Within cutoff, q should be positive
    q = shape_function.active(4, length_scale)
    assert q > 0
    # Check the cutoff
    assert shape_function.get_cutoff() == 5

    # Set active shape function to quadratic, its cutoff is fixed at 1.0
    shape_function.set_active(shape_function.quadratic)
    # Within cutoff, q should be positive
    q = shape_function.active(0.5, length_scale)
    assert q > 0

    # Outside cutoff, q should be zero
    q = shape_function.active(1.5, length_scale)
    assert q == 0


@pytest.mark.unit
def test_shape_function_exceptions():
    """Test exceptions in shape function"""
    # Set non-existent function
    with pytest.raises(ValueError):
        shape_function.set_active('non_existent_function')

    # Set non-function
    with pytest.raises(ValueError):
        shape_function.set_active(123)

    # Set negative cutoff
    with pytest.raises(ValueError):
        shape_function.set_cutoff(-1)
