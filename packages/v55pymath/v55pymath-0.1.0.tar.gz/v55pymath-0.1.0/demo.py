from pymath import (
    matrix_inverse,
    monte_carlo_integral,
    lagrange_interpolation,
    find_extrema
)

def main():
    # Demonstration of matrix_inverse
    A = [[1.0, 2.0], [3.0, 4.0]]
    inv = matrix_inverse(A)
    print("Inverse matrix of [[1, 2], [3, 4]]:")
    for row in inv:
        print(row)

    # Demonstration of Monte Carlo integration
    integral = monte_carlo_integral(lambda x: x**2, 0, 1, 10000)
    print(f"\nIntegral of x^2 on [0, 1] ≈ {integral:.4f} (expected ~0.3333)")

    # Lagrange interpolation
    x_vals = [0, 1, 2]
    y_vals = [1, 3, 2]
    value = lagrange_interpolation(x_vals, y_vals, 1.5)
    print(f"\nValue of the Lagrange interpolation polynomial at 1.5: {value:.4f}")

    # Extremum finding
    f = lambda x: -(x - 2)**2 + 4
    x_ext = find_extrema(f, 0, 4)
    print(f"\nExtremum of the function -(x - 2)^2 + 4 found at x = {x_ext:.4f}")

if __name__ == "__main__":
    main()

