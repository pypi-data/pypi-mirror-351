import pytest
import math
from pymath import find_extrema, integrate, integrate_double, integrate_triple

def assert_almost_equal(actual, expected, tol=1e-6):
    """Custom assertion for comparing floats or lists of floats within a tolerance."""
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected), f"Length mismatch: {len(actual)} != {len(expected)}"
        for a, e in zip(actual, expected):
            if isinstance(a, (list, tuple)) and isinstance(e, (list, tuple)):
                assert_almost_equal(a, e, tol)
            else:
                assert abs(a - e) < tol, f"{a} != {e} within tolerance {tol}"
    else:
        assert abs(actual - expected) < tol, f"{actual} != {expected} within tolerance {tol}"

def test_find_extrema_quadratic():
    """Test find_extrema with a quadratic function f(x) = x^2 (minimum at x=0)."""
    def f(x): return x * x
    result = find_extrema(f, -1.0, 1.0, 0.1)
    assert_almost_equal(result, 0.0, tol=0.1)

def test_find_extrema_no_extrema():
    """Test find_extrema with a linear function (no extrema)."""
    def f(x): return x
    result = find_extrema(f, -1.0, 1.0, 0.1)
    assert_almost_equal(result, -1.0)  # No extrema found

def test_find_extrema_small_step():
    """Test find_extrema with a small step size for better precision."""
    def f(x): return x * x
    result = find_extrema(f, -1.0, 1.0, 0.001)
    assert_almost_equal(result, 0.0, tol=0.001)

def test_find_extrema_boundary():
    """Test find_extrema with extrema at the boundary."""
    def f(x): return (x - 1) * (x - 1)  # Minimum at x=1
    result = find_extrema(f, 0.0, 1.0, 0.1)
    assert_almost_equal(result, 1.0, tol=0.1)

def test_integrate_linear():
    """Test integrate with a linear function f(x) = x over [0, 1]."""
    def f(x): return x
    result = integrate(f, 0.0, 1.0, 100)
    expected = 0.5  # Integral of x from 0 to 1 is x^2/2 = 0.5
    assert_almost_equal(result, expected)

def test_integrate_constant():
    """Test integrate with a constant function f(x) = 1 over [0, 1]."""
    def f(x): return 1.0
    result = integrate(f, 0.0, 1.0, 100)
    expected = 1.0  # Integral of 1 from 0 to 1 is 1
    assert_almost_equal(result, expected)

def test_integrate_double_constant():
    """Test integrate_double with a constant function f(x, y) = 1 over [0,1]x[0,1]."""
    def f(x, y): return 1.0
    result = integrate_double(f, 0.0, 1.0, 0.0, 1.0, 10, 10)
    expected = 1.0  # Integral over unit square is 1
    assert_almost_equal(result, expected)

def test_integrate_double_linear():
    """Test integrate_double with f(x, y) = x + y over [0,1]x[0,1]."""
    def f(x, y): return x + y
    result = integrate_double(f, 0.0, 1.0, 0.0, 1.0, 100, 100)
    expected = 1.0  # Integral of (x + y) over [0,1]x[0,1] is 1
    assert_almost_equal(result, expected, tol=1e-2)

def test_integrate_triple_constant():
    """Test integrate_triple with a constant function f(x, y, z) = 1 over [0,1]x[0,1]x[0,1]."""
    def f(x, y, z): return 1.0
    result = integrate_triple(f, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 10, 10, 10)
    expected = 1.0  # Integral over unit cube is 1
    assert_almost_equal(result, expected)

def test_integrate_triple_linear():
    """Test integrate_triple with f(x, y, z) = x + y + z over [0,1]x[0,1]x[0,1]."""
    def f(x, y, z): return x + y + z
    result = integrate_triple(f, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 50, 50, 50)
    expected = 1.5  # Integral of (x + y + z) over [0,1]^3 is 1.5
    assert_almost_equal(result, expected, tol=1e-1)

def test_solve_ode_linear():
    """Test solve_ode with dy/dt = -y, y(0) = 1 over [0, 1]."""
    def f(t, y): return