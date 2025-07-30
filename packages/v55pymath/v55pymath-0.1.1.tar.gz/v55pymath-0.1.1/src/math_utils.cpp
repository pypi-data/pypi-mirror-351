#include "math_utils.hpp"
#include <stdexcept>
#include <cmath>

namespace math_utils {

/**
 * @brief Calculate the square root of a number using Newton's method.
 * 
 * Uses an iterative approach to approximate the square root of `x`
 * with precision defined by `epsilon`.
 * 
 * @param x The number to find the square root of (must be non-negative).
 * @param epsilon The precision tolerance for the approximation.
 * @return Approximated square root of `x`.
 * @throws std::domain_error if `x` is negative.
 */
double newton_sqrt(double x, double epsilon) {
    if (x < 0.0) {
        throw std::domain_error("Negative number under the square root");
    }
    double guess = x;

    // Iterate until the difference between guess^2 and x is less than epsilon
    while (std::abs(guess * guess - x) > epsilon) {
        guess = (guess + x / guess) / 2.0;
    }
    return guess;
}

/**
 * @brief Calculate sine of x using Taylor series expansion.
 * 
 * Reduces `x` modulo 2*PI and computes sine using a finite number of terms.
 * 
 * @param x The angle in radians.
 * @param terms Number of terms in the Taylor series.
 * @return Approximate sine of `x`.
 */
double taylor_sin(double x, int terms) {
    x = std::fmod(x, 2 * PI);  // Reduce angle within [0, 2π)
    double result = 0.0;
    double power = x;  // Current power of x in the series
    int sign = 1;      // Alternating sign in series

    // Sum up terms of the Taylor series for sine
    for (int n = 1; n <= terms; ++n) {
        result += sign * power;
        // Update power for the next term: x^(2n+1)
        power *= x * x / ((2 * n) * (2 * n + 1));
        sign *= -1;  // Alternate sign
    }
    return result;
}

/**
 * @brief Calculate cosine of x using Taylor series expansion.
 * 
 * Reduces `x` modulo 2*PI and computes cosine using a finite number of terms.
 * 
 * @param x The angle in radians.
 * @param terms Number of terms in the Taylor series.
 * @return Approximate cosine of `x`.
 */
double taylor_cos(double x, int terms) {
    x = std::fmod(x, 2 * PI);  // Reduce angle within [0, 2π)
    double result = 0.0;
    double power = 1.0;  // Current power of x in the series (x^0 = 1)
    int sign = 1;        // Alternating sign in series

    // Sum up terms of the Taylor series for cosine
    for (int n = 0; n < terms; ++n) {
        result += sign * power;
        // Update power for the next term: x^(2n+2)
        power *= x * x / ((2 * n + 1) * (2 * n + 2));
        sign *= -1;  // Alternate sign
    }
    return result;
}

/**
 * @brief Calculate exponential of x using Taylor series expansion.
 * 
 * Computes e^x using a finite number of terms in the series.
 * 
 * @param x The exponent value.
 * @param terms Number of terms in the Taylor series.
 * @return Approximate value of e^x.
 */
double taylor_exp(double x, int terms) {
    double result = 1.0;  // First term of the series is 1
    double term = 1.0;    // Current term (x^n / n!)

    // Sum terms of the exponential series
    for (int n = 1; n <= terms; ++n) {
        term *= x / n;  // Compute next term incrementally
        result += term;
    }
    return result;
}

/**
 * @brief Calculate the exponential of a complex number.
 * 
 * Given a complex number z = a + bi (represented as a pair), this function
 * computes e^(a + bi) = e^a * (cos b + i sin b) using Taylor expansions.
 * 
 * @param z A pair<double, double> representing the real (a) and imaginary (b) parts.
 * @return A pair<double, double> representing the real and imaginary parts of e^z.
 */
std::pair<double, double> complex_exp(std::pair<double, double> z) {
    double a = z.first;   // Real part
    double b = z.second;  // Imaginary part

    double exp_a = taylor_exp(a);        // Compute e^a
    double real = taylor_cos(b) * exp_a; // Real part: e^a * cos(b)
    double imag = taylor_sin(b) * exp_a; // Imag part: e^a * sin(b)

    return {real, imag};
}

} // namespace math_utils
