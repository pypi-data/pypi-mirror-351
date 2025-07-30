import pytest
import math
from pymath import dft, idft, fft, laplace_transform

def assert_almost_equal(actual, expected, tol=1e-6):
    """Custom assertion for comparing floats, complex numbers, or lists within a tolerance."""
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected), f"Length mismatch: {len(actual)} != {len(expected)}"
        for a, e in zip(actual, expected):
            assert_almost_equal(a, e, tol)
    elif isinstance(actual, complex) and isinstance(expected, complex):
        assert abs(actual.real - expected.real) < tol, f"Real part {actual.real} != {expected.real} within tolerance {tol}"
        assert abs(actual.imag - expected.imag) < tol, f"Imag part {actual.imag} != {expected.imag} within tolerance {tol}"
    elif isinstance(actual, tuple) and isinstance(expected, tuple):
        assert len(actual) == len(expected), f"Tuple length mismatch: {len(actual)} != {len(expected)}"
        for a, e in zip(actual, expected):
            assert abs(a - e) < tol, f"{a} != {e} within tolerance {tol}"
    else:
        assert abs(actual - expected) < tol, f"{actual} != {expected} within tolerance {tol}"

def test_dft_constant():
    """Test DFT of a constant signal."""
    signal = [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0)]
    result = dft(signal)
    expected = [complex(4.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0)]
    assert_almost_equal(result, expected)

def test_dft_single_point():
    """Test DFT of a single-point signal."""
    signal = [complex(1.0, 0.0)]
    result = dft(signal)
    expected = [complex(1.0, 0.0)]
    assert_almost_equal(result, expected)

def test_dft_empty():
    """Test DFT of an empty signal."""
    signal = []
    result = dft(signal)
    expected = []
    assert_almost_equal(result, expected)

def test_idft_constant():
    """Test IDFT of a constant transform (DC component)."""
    transform = [complex(4.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0)]
    result = idft(transform)
    expected = [1.0, 1.0, 1.0, 1.0]  # IDFT of [4, 0, 0, 0] gives constant 1
    assert_almost_equal(result, expected)

def test_idft_single_point():
    """Test IDFT of a single-point transform."""
    transform = [complex(1.0, 0.0)]
    result = idft(transform)
    expected = [1.0]
    assert_almost_equal(result, expected)

def test_idft_empty():
    """Test IDFT of an empty transform."""
    transform = []
    result = idft(transform)
    expected = []
    assert_almost_equal(result, expected)

def test_dft_idft_roundtrip():
    """Test DFT followed by IDFT returns the original signal."""
    signal = [complex(1.0, 0.0), complex(2.0, 1.0), complex(3.0, -1.0)]
    transform = dft(signal)
    result = idft(transform)
    expected = [1.0, 2.0, 3.0]  # IDFT returns real parts (imaginary parts are near zero)
    assert_almost_equal(result, expected, tol=1e-5)

def test_fft_constant():
    """Test FFT of a constant signal (length = power of 2)."""
    signal = [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0)]
    result = fft(signal)
    expected = [complex(4.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0)]
    assert_almost_equal(result, expected)

def test_fft_single_point():
    """Test FFT of a single-point signal."""
    signal = [complex(1.0, 0.0)]
    result = fft(signal)
    expected = [complex(1.0, 0.0)]
    assert_almost_equal(result, expected)

def test_fft_non_power_of_two():
    """Test FFT with a non-power-of-two signal length."""
    signal = [complex(1.0, 0.0), complex(2.0, 0.0), complex(3.0, 0.0)]
    with pytest.raises(Exception, match="Signal length must be a power of 2"):
        fft(signal)

def test_fft_dft_equivalence():
    """Test that FFT matches DFT for a power-of-two signal."""
    signal = [complex(1.0, 0.0), complex(2.0, 0.0), complex(3.0, 0.0), complex(4.0, 0.0)]
    dft_result = dft(signal)
    fft_result = fft(signal)
    assert_almost_equal(fft_result, dft_result)

def test_laplace_transform_invalid_dt():
    """Test Laplace transform with invalid dt <= 0."""
    def f(t): return 1.0
    with pytest.raises(Exception):
        laplace_transform(f, 1.0, 0.0, 10.0, 0.0)

def test_laplace_transform_invalid_t_max():
    """Test Laplace transform with invalid t_max <= 0."""
    def f(t): return 1.0
    with pytest.raises(Exception):
        laplace_transform(f, 1.0, 0.0, 0.0, 0.01)