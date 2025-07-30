import pytest
from pymath import solve_slae

def assert_almost_equal(actual, expected, tol=1e-6):
    """Custom assertion for comparing lists of floats within a tolerance."""
    assert len(actual) == len(expected), f"Length mismatch: {len(actual)} != {len(expected)}"
    for a, e in zip(actual, expected):
        assert abs(a - e) < tol, f"{a} != {e} within tolerance {tol}"

def test_regular_system():
    """Test a simple 3x3 system with a known solution."""
    A = [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]
    b = [8, -11, -3]
    expected = [2, 3, -1]
    result = solve_slae(A, b)
    assert_almost_equal(result, expected)

def test_singular_matrix():
    """Test a singular matrix, which should raise an exception."""
    A = [[1, 2], [2, 4]]  # Rows are linearly dependent
    b = [3, 6]
    with pytest.raises(Exception, match="Singular matrix detected"):
        solve_slae(A, b)

def test_single_element():
    """Test a 1x1 system."""
    A = [[5]]
    b = [10]
    expected = [2]
    result = solve_slae(A, b)
    assert_almost_equal(result, expected)

def test_zero_diagonal():
    """Test a system where pivoting is required (zero on diagonal)."""
    A = [[0, 1], [1, 0]]
    b = [2, 3]
    expected = [3, 2]
    result = solve_slae(A, b)
    assert_almost_equal(result, expected)

@pytest.mark.parametrize("A,b,expected", [
    ([[1e10, 2], [3, 4]], [1e10 + 2, 7], [1, 1]),  # Large numbers
    ([[1e-10, 2e-10], [3e-10, 4e-10]], [3e-10, 7e-10], [1, 1]),  # Small numbers
])
def test_numeric_stability(A, b, expected):
    """Test systems with large and small coefficients."""
    result = solve_slae(A, b)
    assert_almost_equal(result, expected)

def test_identity_matrix():
    """Test with an identity matrix (simplest case)."""
    A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    b = [1, 2, 3]
    expected = [1, 2, 3]
    result = solve_slae(A, b)
    assert_almost_equal(result, expected)

def test_diagonal_dominant():
    """Test a diagonally dominant system."""
    A = [[10, 1, 2], [1, 10, 3], [2, 3, 10]]
    b = [13, 14, 15]
    expected = [1, 1, 1]
    result = solve_slae(A, b)
    assert_almost_equal(result, expected)

def test_invalid_dimensions():
    """Test a system with mismatched dimensions."""
    A = [[1, 2], [3, 4]]
    b = [1, 2, 3]  # b has wrong size
    with pytest.raises(Exception):
        solve_slae(A, b)

def test_empty_system():
    """Test an empty system."""
    A = []
    b = []
    with pytest.raises(Exception):
        solve_slae(A, b)