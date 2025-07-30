import pytest
import math
from pymath import monte_carlo_integral

def assert_almost_equal(actual, expected, tol=1e-2):
    """Custom assertion for comparing floats within a tolerance."""
    assert abs(actual - expected) < tol, f"{actual} != {expected} within tolerance {tol}"

def test_monte_carlo_integral_constant():
    """Test Monte Carlo integration of a constant function f(x) = 1 over [0, 1]."""
    def f(x): return 1.0
    result = monte_carlo_integral(f, 0.0, 1.0, 10000)
    expected = 1.0  # Integral of 1 over [0, 1] is 1
    assert_almost_equal(result, expected)

def test_monte_carlo_integral_linear():
    """Test Monte Carlo integration of a linear function f(x) = x over [0, 1]."""
    def f(x): return x
    result = monte_carlo_integral(f, 0.0, 1.0, 10000)
    expected = 0.5  # Integral of x over [0, 1] is x^2/2 = 0.5
    assert_almost_equal(result, expected)

def test_monte_carlo_integral_quadratic():
    """Test Monte Carlo integration of a quadratic function f(x) = x^2 over [0, 1]."""
    def f(x): return x * x
    result = monte_carlo_integral(f, 0.0, 1.0, 10000)
    expected = 1.0 / 3.0  # Integral of x^2 over [0, 1] is x^3/3 = 1/3
    assert_almost_equal(result, expected)

def test_monte_carlo_integral_negative_interval():
    """Test Monte Carlo integration over a negative interval [-1, 0] with f(x) = x."""
    def f(x): return x
    result = monte_carlo_integral(f, -1.0, 0.0, 10000)
    expected = -0.5  # Integral of x over [-1, 0] is x^2/2 = -0.5
    assert_almost_equal(result, expected)

def test_monte_carlo_integral_large_n():
    """Test Monte Carlo integration with a large number of points."""
    def f(x): return 1.0
    result = monte_carlo_integral(f, 0.0, 1.0, 100000)
    expected = 1.0
    assert_almost_equal(result, expected, tol=1e-3)  # Tighter tolerance for larger n

def test_monte_carlo_integral_small_n():
    """Test Monte Carlo integration with a small number of points."""
    def f(x): return 1.0
    result = monte_carlo_integral(f, 0.0, 1.0, 100)
    expected = 1.0
    assert_almost_equal(result, expected, tol=1e-1)  # Larger tolerance for small n

def test_monte_carlo_integral_invalid_n():
    """Test Monte Carlo integration with invalid n <= 0."""
    def f(x): return x
    with pytest.raises(Exception):
        monte_carlo_integral(f, 0.0, 1.0, 0)

def test_monte_carlo_integral_invalid_interval():
    """Test Monte Carlo integration with invalid interval (a >= b)."""
    def f(x): return x
    with pytest.raises(Exception):
        monte_carlo_integral(f, 1.0, 0.0, 1000)