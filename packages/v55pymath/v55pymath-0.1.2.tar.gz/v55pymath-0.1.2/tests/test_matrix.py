import pytest
import math
from pymath import identity_matrix, matrix_minor, determinant, hermitian_conjugate, matrix_multiply, multiply_scalar, matrix_exponential, matrix_power, matrix_inverse

def assert_almost_equal(actual, expected, tol=1e-6):
    """Custom assertion for comparing floats, complex numbers, or nested lists within a tolerance."""
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected), f"Length mismatch: {len(actual)} != {len(expected)}"
        for a, e in zip(actual, expected):
            assert_almost_equal(a, e, tol)
    elif isinstance(actual, complex) and isinstance(expected, complex):
        assert abs(actual.real - expected.real) < tol, f"Real part {actual.real} != {expected.real} within tolerance {tol}"
        assert abs(actual.imag - expected.imag) < tol, f"Imag part {actual.imag} != {expected.imag} within tolerance {tol}"
    else:
        assert abs(actual - expected) < tol, f"{actual} != {expected} within tolerance {tol}"

def test_multiply_scalar_real():
    """Test multiply_scalar with a real scalar."""
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    scalar = 2.0
    result = multiply_scalar(matrix, scalar)
    expected = [[2.0, 4.0], [6.0, 8.0]]
    assert_almost_equal(result, expected)

def test_multiply_scalar_complex():
    """Test multiply_scalar with a complex scalar."""
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    scalar = complex(1.0, 1.0)
    result = multiply_scalar(matrix, scalar)
    expected = [[complex(1.0, 1.0), complex(2.0, 2.0)], [complex(3.0, 3.0), complex(4.0, 4.0)]]
    assert_almost_equal(result, expected)

def test_identity_matrix():
    """Test identity_matrix for a 3x3 matrix."""
    result = identity_matrix(3)
    expected = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    assert_almost_equal(result, expected)

def test_identity_matrix_size_one():
    """Test identity_matrix for a 1x1 matrix."""
    result = identity_matrix(1)
    expected = [[1.0]]
    assert_almost_equal(result, expected)

def test_matrix_minor():
    """Test matrix_minor for a 3x3 matrix, removing row 1 and column 1."""
    input_matrix = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    result = matrix_minor(input_matrix, 1, 1)
    expected = [[1.0, 3.0], [7.0, 9.0]]
    assert_almost_equal(result, expected)

def test_matrix_minor_invalid():
    """Test matrix_minor with invalid indices."""
    matrix_data = [[1.0, 2.0], [3.0, 4.0]]
    with pytest.raises(Exception):
        matrix_minor(matrix_data, 2, 0)  # Row index out of bounds

def test_determinant_1x1():
    """Test determinant for a 1x1 matrix."""
    matrix_data = [[5.0]]
    result = determinant(matrix_data)
    expected = 5.0
    assert_almost_equal(result, expected)

def test_determinant_2x2():
    """Test determinant for a 2x2 matrix."""
    matrix_data = [[1.0, 2.0], [3.0, 4.0]]
    result = determinant(matrix_data)
    expected = -2.0  # 1*4 - 2*3 = -2
    assert_almost_equal(result, expected)

def test_determinant_3x3_complex():
    """Test determinant for a 3x3 matrix with complex numbers."""
    matrix_data = [[complex(1, 1), 0, 0], [0, complex(1, 1), 0], [0, 0, complex(1, 1)]]
    result = determinant(matrix_data)
    expected = complex(1, 1) * complex(1, 1) * complex(1, 1)
    assert_almost_equal(result, expected)

def test_determinant_non_square():
    """Test determinant with a non-square matrix."""
    matrix_data = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    with pytest.raises(Exception, match="Matrix must be square"):
        determinant(matrix_data)

def test_hermitian_conjugate():
    """Test hermitian_conjugate for a 2x2 matrix with complex numbers."""
    matrix_data = [[complex(1, 2), complex(3, 4)], [complex(5, 6), complex(7, 8)]]
    result = hermitian_conjugate(matrix_data)
    expected = [[complex(1, -2), complex(5, -6)], [complex(3, -4), complex(7, -8)]]
    assert_almost_equal(result, expected)

def test_multiply():
    """Test matrix multiplication for 2x2 matrices."""
    A = [[1.0, 2.0], [3.0, 4.0]]
    B = [[5.0, 6.0], [7.0, 8.0]]
    result = matrix_multiply(A, B)
    expected = [[19.0, 22.0], [43.0, 50.0]]  # [1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]
    assert_almost_equal(result, expected)

def test_multiply_non_square():
    """Test matrix multiplication with non-square matrices."""
    A = [[1.0, 2.0]]
    with pytest.raises(Exception, match="Matrix must be square"):
        matrix_multiply(A, A)

def test_exponential_identity():
    """Test exponential of a zero matrix (should be identity)."""
    matrix_data = [[0.0, 0.0], [0.0, 0.0]]
    result = matrix_exponential(matrix_data, 10)
    expected = [[1.0, 0.0], [0.0, 1.0]]
    assert_almost_equal(result, expected, tol=1e-5)

def test_exponential_diagonal():
    """Test exponential of a diagonal matrix."""
    matrix_data = [[1.0, 0.0], [0.0, 2.0]]
    result = matrix_exponential(matrix_data, 10)
    expected = [[math.exp(1.0), 0.0], [0.0, math.exp(2.0)]]
    assert_almost_equal(result, expected, tol=1e-3)

def test_exponential_invalid():
    """Test exponential with a non-square matrix."""
    matrix_data = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    with pytest.raises(Exception, match="Matrix must be square"):
        matrix_exponential(matrix_data, 10)

def test_power_zero():
    """Test power with exponent 0 (should return identity)."""
    matrix_data = [[1.0, 2.0], [3.0, 4.0]]
    result = matrix_power(matrix_data, 0)
    expected = [[1.0, 0.0], [0.0, 1.0]]
    assert_almost_equal(result, expected)

def test_power_positive():
    """Test power with positive exponent."""
    matrix_data = [[1.0, 2.0], [3.0, 4.0]]
    result = matrix_power(matrix_data, 2)
    expected = [[7.0, 10.0], [15.0, 22.0]]  # Matrix squared
    assert_almost_equal(result, expected)

def test_power_negative():
    """Test power with negative exponent (requires inverse)."""
    matrix_data = [[1.0, 1.0], [0.0, 1.0]]
    result = matrix_power(matrix_data, -1)
    expected = [[1.0, -1.0], [0.0, 1.0]]  # Inverse of [[1, 1], [0, 1]]
    assert_almost_equal(result, expected, tol=1e-5)

def test_inverse_2x2():
    """Test inverse of a 2x2 matrix."""
    matrix_data = [[4.0, 7.0], [2.0, 6.0]]
    result = matrix_inverse(matrix_data)
    expected = [[0.6, -0.7], [-0.2, 0.4]]  # Adjugate / det, det = 24 - 14 = 10
    assert_almost_equal(result, expected, tol=1e-5)

def test_inverse_singular():
    """Test inverse of a singular matrix."""
    matrix_data = [[1.0, 2.0], [2.0, 4.0]]
    with pytest.raises(Exception, match="Matrix is singular"):
        matrix_inverse(matrix_data)

def test_inverse_non_square():
    """Test inverse with a non-square matrix."""
    matrix_data = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    with pytest.raises(Exception, match="Matrix must be square"):
        matrix_inverse(matrix_data)
