import pytest
import math
from pymath import vector_l1_norm, vector_l2_norm, vector_linf_norm, matrix_frobenius_norm, matrix_l1_norm, matrix_linf_norm
from pymath import euclidean_distance, manhattan_distance, chebyshev_distance

def assert_almost_equal(actual, expected, tol=1e-6):
    """Custom assertion for comparing floats within a tolerance."""
    assert abs(actual - expected) < tol, f"{actual} != {expected} within tolerance {tol}"

def test_vector_l1_norm():
    """Test L1 norm of a vector."""
    v = [1.0, -2.0, 3.0]
    result = vector_l1_norm(v)
    expected = 6.0  # |1| + |-2| + |3| = 6
    assert_almost_equal(result, expected)

def test_vector_l1_norm_zero():
    """Test L1 norm of a zero vector."""
    v = [0.0, 0.0, 0.0]
    result = vector_l1_norm(v)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_vector_l1_norm_empty():
    """Test L1 norm of an empty vector."""
    v = []
    result = vector_l1_norm(v)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_vector_l2_norm():
    """Test L2 norm of a vector."""
    v = [3.0, 4.0]
    result = vector_l2_norm(v)
    expected = 5.0  # sqrt(3^2 + 4^2) = sqrt(25) = 5
    assert_almost_equal(result, expected)

def test_vector_l2_norm_zero():
    """Test L2 norm of a zero vector."""
    v = [0.0, 0.0]
    result = vector_l2_norm(v)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_vector_l2_norm_empty():
    """Test L2 norm of an empty vector."""
    v = []
    result = vector_l2_norm(v)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_vector_linf_norm():
    """Test L-infinity norm of a vector."""
    v = [1.0, -3.0, 2.0]
    result = vector_linf_norm(v)
    expected = 3.0  # max(|1|, |-3|, |2|) = 3
    assert_almost_equal(result, expected)

def test_vector_linf_norm_zero():
    """Test L-infinity norm of a zero vector."""
    v = [0.0, 0.0]
    result = vector_linf_norm(v)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_matrix_frobenius_norm():
    """Test Frobenius norm of a matrix."""
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    result = matrix_frobenius_norm(matrix)
    expected = math.sqrt(30.0)  # sqrt(1^2 + 2^2 + 3^2 + 4^2) = sqrt(30)
    assert_almost_equal(result, expected)

def test_matrix_frobenius_norm_zero():
    """Test Frobenius norm of a zero matrix."""
    matrix = [[0.0, 0.0], [0.0, 0.0]]
    result = matrix_frobenius_norm(matrix)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_matrix_frobenius_norm_empty():
    """Test Frobenius norm of an empty matrix."""
    matrix = []
    result = matrix_frobenius_norm(matrix)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_matrix_l1_norm():
    """Test L1 norm of a matrix (maximum column sum)."""
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    result = matrix_l1_norm(matrix)
    expected = 6.0
    assert_almost_equal(result, expected)

def test_matrix_linf_norm():
    """Test L-infinity norm of a matrix (maximum row sum)."""
    matrix = [[1.0, 2.0], [3.0, 4.0]]
    result = matrix_linf_norm(matrix)
    expected = 7.0  # max(|1| + |2|, |3| + |4|) = max(3, 7) = 7
    assert_almost_equal(result, expected)

def test_matrix_linf_norm_empty():
    """Test L-infinity norm of an empty matrix."""
    matrix = []
    result = matrix_linf_norm(matrix)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_euclidean_distance():
    """Test Euclidean distance between two vectors."""
    v1 = [3.0, 4.0]
    v2 = [0.0, 0.0]
    result = euclidean_distance(v1, v2)
    expected = 5.0  # sqrt((3-0)^2 + (4-0)^2) = sqrt(25) = 5
    assert_almost_equal(result, expected)

def test_euclidean_distance_equal():
    """Test Euclidean distance between identical vectors."""
    v1 = [1.0, 2.0]
    v2 = [1.0, 2.0]
    result = euclidean_distance(v1, v2)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_manhattan_distance():
    """Test Manhattan distance between two vectors."""
    v1 = [1.0, 2.0]
    v2 = [3.0, 4.0]
    result = manhattan_distance(v1, v2)
    expected = 4.0  # |1-3| + |2-4| = 2 + 2 = 4
    assert_almost_equal(result, expected)

def test_manhattan_distance_equal():
    """Test Manhattan distance between identical vectors."""
    v1 = [1.0, 2.0]
    v2 = [1.0, 2.0]
    result = manhattan_distance(v1, v2)
    expected = 0.0
    assert_almost_equal(result, expected)

def test_chebyshev_distance():
    """Test Chebyshev distance between two vectors."""
    v1 = [1.0, 2.0, 3.0]
    v2 = [4.0, 1.0, 2.0]
    result = chebyshev_distance(v1, v2)
    expected = 3.0  # max(|1-4|, |2-1|, |3-2|) = max(3, 1, 1) = 3
    assert_almost_equal(result, expected)

def test_chebyshev_distance_equal():
    """Test Chebyshev distance between identical vectors."""
    v1 = [1.0, 2.0]
    v2 = [1.0, 2.0]
    result = chebyshev_distance(v1, v2)
    expected = 0.0
    assert_almost_equal(result, expected)