#pragma once
#include <utility>

namespace math_utils {

/**
 * @brief Constant value of π (pi) to high precision.
 */
constexpr double PI = 3.141592653589793;

/**
 * @brief Calculates the square root of a number using Newton's method.
 * 
 * @param x The number for which to compute the square root. Must be non-negative.
 * @param epsilon The precision of the result. Default is 1e-10.
 * @return The approximated square root of x.
 * @throws std::invalid_argument if x is negative.
 */
double newton_sqrt(double x, double epsilon = 1e-10);

/**
 * @brief Approximates the sine of a number using the Taylor series expansion.
 * 
 * @param x The angle in radians.
 * @param terms Number of terms to include in the Taylor series. Default is 15.
 * @return Approximated value of sin(x).
 */
double taylor_sin(double x, int terms = 15);

/**
 * @brief Approximates the cosine of a number using the Taylor series expansion.
 * 
 * @param x The angle in radians.
 * @param terms Number of terms to include in the Taylor series. Default is 15.
 * @return Approximated value of cos(x).
 */
double taylor_cos(double x, int terms = 15);

/**
 * @brief Approximates the exponential function e^x using the Taylor series expansion.
 * 
 * @param x The exponent.
 * @param terms Number of terms to include in the Taylor series. Default is 20.
 * @return Approximated value of e^x.
 */
double taylor_exp(double x, int terms = 20);

/**
 * @brief Computes the complex exponential function e^(a + bi).
 * 
 * @param z A pair (a, b) representing the complex number a + bi.
 * @return A pair (real, imag) representing the result of e^(a + bi).
 */
std::pair<double, double> complex_exp(std::pair<double, double> z);

} // namespace math_utils
