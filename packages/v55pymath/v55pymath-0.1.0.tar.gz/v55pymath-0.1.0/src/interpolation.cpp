#include "interpolation.hpp"

namespace interpolation {

/**
 * @brief Perform Lagrange polynomial interpolation for a given point.
 * 
 * This function computes the value of the Lagrange interpolating polynomial
 * at a given point `x` based on the provided data points (`x_vals`, `y_vals`).
 * 
 * @param x_vals Vector of x-coordinates of data points.
 * @param y_vals Vector of y-coordinates of data points.
 * @param x The x-value at which to interpolate.
 * @return Interpolated y-value at x.
 */
double lagrange_interpolation(const std::vector<double>& x_vals, const std::vector<double>& y_vals, double x) {

    double result = 0.0;
    size_t n = x_vals.size();

    // Calculate the Lagrange basis polynomials and sum them up
    for (size_t i = 0; i < n; ++i) {
        double term = y_vals[i];
        for (size_t j = 0; j < n; ++j) {
            if (i != j) {
                // Compute the Lagrange basis polynomial L_i(x)
                term *= (x - x_vals[j]) / (x_vals[i] - x_vals[j]);
            }
        }
        result += term;
    }

    return result;
}

/**
 * @brief Perform Newton polynomial interpolation for a given point.
 * 
 * This function calculates the Newton interpolating polynomial value at `x`.
 * It first computes divided differences coefficients and then evaluates
 * the polynomial using these coefficients.
 * 
 * @param x_vals Vector of x-coordinates of data points.
 * @param y_vals Vector of y-coordinates of data points.
 * @param x The x-value at which to interpolate.
 * @return Interpolated y-value at x.
 */
double newton_interpolation(const std::vector<double>& x_vals, const std::vector<double>& y_vals, double x) {
    size_t n = x_vals.size();
    std::vector<double> coef = y_vals;

    // Compute divided differences coefficients in-place
    for (size_t j = 1; j < n; ++j) {
        for (size_t i = n - 1; i >= j; --i) {
            coef[i] = (coef[i] - coef[i - 1]) / (x_vals[i] - x_vals[i - j]);
        }
    }

    // Evaluate the Newton polynomial using Horner's method
    double result = coef[n - 1];
    for (int i = n - 2; i >= 0; --i) {
        result = result * (x - x_vals[i]) + coef[i];
    }

    return result;
}

/**
 * @brief Perform cubic spline interpolation for a given point.
 * 
 * This function computes the cubic spline interpolation for the point `xi`
 * using natural spline boundary conditions. It calculates spline coefficients
 * and evaluates the spline polynomial on the interval containing `xi`.
 * 
 * @param x Vector of x-coordinates of data points (must be sorted).
 * @param y Vector of y-coordinates of data points.
 * @param xi The x-value at which to interpolate.
 * @return Interpolated y-value at xi.
 */
double spline_interpolation(const std::vector<double>& x, const std::vector<double>& y, double xi) {
    size_t n = x.size();
    std::vector<double> h(n - 1);

    // Compute the distances between adjacent x-values
    for (size_t i = 0; i < n - 1; ++i) {
        h[i] = x[i + 1] - x[i];
    }

    // Calculate alpha values used for the system of equations
    std::vector<double> alpha(n, 0.0);
    for (size_t i = 1; i < n - 1; ++i) {
        alpha[i] = (3.0 / h[i]) * (y[i + 1] - y[i]) - (3.0 / h[i - 1]) * (y[i] - y[i - 1]);
    }

    // Vectors for the tridiagonal system solution and spline coefficients
    std::vector<double> l(n), mu(n), z(n), c(n), b(n - 1), d(n - 1);
    l[0] = 1.0;

    // Forward sweep for solving tridiagonal system (LU decomposition)
    for (size_t i = 1; i < n - 1; ++i) {
        l[i] = 2.0 * (x[i + 1] - x[i - 1]) - h[i - 1] * mu[i - 1];
        mu[i] = h[i] / l[i];
        z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i];
    }
    l[n - 1] = 1.0;

    // Back substitution to find c coefficients (second derivatives)
    for (int j = n - 2; j >= 0; --j) {
        c[j] = z[j] - mu[j] * c[j + 1];
        // Calculate b and d coefficients for spline polynomial
        b[j] = (y[j + 1] - y[j]) / h[j] - h[j] * (c[j + 1] + 2.0 * c[j]) / 3.0;
        d[j] = (c[j + 1] - c[j]) / (3.0 * h[j]);
    }

    // Find the interval [x[i], x[i+1]] that contains xi
    size_t i = n - 2;
    for (size_t j = 0; j < n - 1; ++j) {
        if (x[j] <= xi && xi <= x[j + 1]) {
            i = j;
            break;
        }
    }

    // Calculate the difference from the base point of the interval
    double dx = xi - x[i];
    // Evaluate the cubic spline polynomial at xi
    return y[i] + b[i] * dx + c[i] * dx * dx + d[i] * dx * dx * dx;
}

} // namespace interpolation
