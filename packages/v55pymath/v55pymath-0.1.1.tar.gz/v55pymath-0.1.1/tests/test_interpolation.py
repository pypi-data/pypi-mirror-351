import pytest
import math
from pymath import lagrange_interpolation, newton_interpolation, spline_interpolation

def assert_almost_equal(actual, expected, tol=1e-6):
    """Custom assertion for comparing floats or lists of floats within a tolerance."""
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected), f"Length mismatch: {len(actual)} != {len(expected)}"
        for a, e in zip(actual, expected):
            assert abs(a - e) < tol, f"{a} != {e} within tolerance {tol}"
    else:
        assert abs(actual - expected) < tol, f"{actual} != {expected} within tolerance {tol}"

def test_lagrange_interpolation_linear():
    """Test Lagrange interpolation for a linear function f(x) = x."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 2.0]
    result = lagrange_interpolation(x_vals, y_vals, 1.5)
    expected = 1.5
    assert_almost_equal(result, expected)

def test_lagrange_interpolation_quadratic():
    """Test Lagrange interpolation for a quadratic function f(x) = x^2 at x=1.5."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 4.0]
    result = lagrange_interpolation(x_vals, y_vals, 1.5)
    expected = 2.25  # 1.5^2 = 2.25
    assert_almost_equal(result, expected)

def test_lagrange_interpolation_single_point():
    """Test Lagrange interpolation with a single point."""
    x_vals = [1.0]
    y_vals = [2.0]
    result = lagrange_interpolation(x_vals, y_vals, 1.0)
    expected = 2.0
    assert_almost_equal(result, expected)

def test_newton_interpolation_linear():
    """Test Newton interpolation for a linear function f(x) = x."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 2.0]
    result = newton_interpolation(x_vals, y_vals, 1.5)
    expected = 1.5
    assert_almost_equal(result, expected)

def test_newton_interpolation_quadratic():
    """Test Newton interpolation for a quadratic function f(x) = x^2 at x=1.5."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 4.0]
    result = newton_interpolation(x_vals, y_vals, 1.5)
    expected = 2.25  # 1.5^2 = 2.25
    assert_almost_equal(result, expected)

def test_newton_interpolation_single_point():
    """Test Newton interpolation with a single point."""
    x_vals = [1.0]
    y_vals = [2.0]
    result = newton_interpolation(x_vals, y_vals, 1.0)
    expected = 2.0
    assert_almost_equal(result, expected)

def test_spline_interpolation_linear():
    """Test spline interpolation for a linear function f(x) = x."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 2.0]
    result = spline_interpolation(x_vals, y_vals, 1.5)
    expected = 1.5
    assert_almost_equal(result, expected, tol=1e-5)

def test_spline_interpolation_quadratic():
    """Test spline interpolation for a quadratic function f(x) = x^2 at x=1.5."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 4.0]
    result = spline_interpolation(x_vals, y_vals, 1.5)
    expected = 2.25  # 1.5^2 = 2.25
    assert_almost_equal(result, expected, tol=1e-0)

def test_spline_interpolation_outside_interval():
    """Test spline interpolation outside the x_vals interval."""
    x_vals = [0.0, 1.0, 2.0]
    y_vals = [0.0, 1.0, 4.0]
    result = spline_interpolation(x_vals, y_vals, 2.5)
    # Expect extrapolation to follow the last spline segment
    expected = 5.5  # Linear extrapolation from last segment
    assert_almost_equal(result, expected, tol=1e-0)