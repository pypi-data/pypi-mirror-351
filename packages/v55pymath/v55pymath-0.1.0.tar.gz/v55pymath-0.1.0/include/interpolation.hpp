#pragma once
#include <vector>

namespace interpolation {

    /**
     * @brief Performs Lagrange interpolation to estimate the value at a given point.
     * 
     * @param x_vals Vector of known x-values (nodes).
     * @param y_vals Vector of known y-values (function values at nodes).
     * @param x The x-value at which to interpolate.
     * @return Interpolated value at x.
     * @throws std::invalid_argument if x_vals and y_vals have different sizes or are empty.
     */
    double lagrange_interpolation(
        const std::vector<double>& x_vals,
        const std::vector<double>& y_vals,
        double x
    );
    
    /**
     * @brief Performs Newton interpolation to estimate the value at a given point.
     * 
     * @param x_vals Vector of known x-values (nodes).
     * @param y_vals Vector of known y-values (function values at nodes).
     * @param x The x-value at which to interpolate.
     * @return Interpolated value at x.
     * @throws std::invalid_argument if x_vals and y_vals have different sizes or are empty.
     */
    double newton_interpolation(
        const std::vector<double>& x_vals,
        const std::vector<double>& y_vals,
        double x
    );
    
    /**
     * @brief Performs cubic spline interpolation to estimate the value at a given point.
     * 
     * @param x Vector of known x-values (must be sorted in ascending order).
     * @param y Vector of known y-values (function values at nodes).
     * @param xi The x-value at which to interpolate.
     * @return Interpolated value at xi.
     * @throws std::invalid_argument if x and y have different sizes or less than 3 points.
     */
    double spline_interpolation(
        const std::vector<double>& x,
        const std::vector<double>& y, 
        double xi
    );
}
