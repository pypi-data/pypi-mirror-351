import re
import io
import sys
from pymath import plot_solution

def test_plot_solution_linear():
    """Test plot_solution with a linear function (y = t)."""
    solution = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        plot_solution(solution)
        assert True
    except:
        assert False

def test_plot_solution_constant():
    """Test plot_solution with a constant function (y = 1)."""
    solution = [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0)]
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        plot_solution(solution)
        assert True
    except:
        assert False

def test_plot_solution_empty():
    """Test plot_solution with an empty solution."""
    solution = []
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        plot_solution(solution)
        assert True
    except:
        assert False

def test_plot_solution_single_point():
    """Test plot_solution with a single point."""
    solution = [(0.0, 5.0)]
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        plot_solution(solution)
        assert True
    except:
        assert False

def test_plot_solution_negative_values():
    """Test plot_solution with negative and positive y values."""
    solution = [(0.0, -1.0), (1.0, 0.0), (2.0, 1.0)]
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        plot_solution(solution)
        assert True
    except:
        assert False

def test_plot_solution_large_range():
    """Test plot_solution with a large range of y values."""
    solution = [(0.0, 0.0), (1.0, 100.0)]
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        plot_solution(solution)
        assert True
    except:
        assert False