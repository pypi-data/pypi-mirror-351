#include "montecarlo.hpp"
#include <random>

namespace montecarlo {

    /**
     * @brief Estimates the definite integral of a function over an interval using the Monte Carlo method.
     * 
     * This function approximates the integral of the function `f` on the interval [a, b]
     * by randomly sampling `n` points uniformly distributed in the interval and averaging the
     * function values at these points.
     * 
     * @param f The integrand function, a callable that takes a double and returns a double.
     * @param a The lower bound of the integration interval.
     * @param b The upper bound of the integration interval.
     * @param n The number of random samples to use for the approximation.
     * 
     * @return The approximate value of the integral of f over [a, b].
     * 
     * @throws std::invalid_argument if n is not positive or if a >= b.
     */
    double monte_carlo_integral(std::function<double(double)> f, double a, double b, int n) {
        if (n <= 0) {
            throw std::invalid_argument("Number of points n must be positive");
        }
        if (a >= b) {
            throw std::invalid_argument("Invalid interval: a must be less than b");
        }

        double total = 0;
        unsigned seed = 1; 
        for (int i = 0; i < n; ++i) {
            // Linear congruential generator for pseudo-random numbers
            seed = (seed * 1103515245 + 12345) % (2U << 30);

            // Generate a pseudo-random number uniformly in [a, b]
            double x = a + (b - a) * (static_cast<double>(seed) / (2U << 30));

            // Accumulate function values
            total += f(x);
        }
        // Multiply average value by interval length to estimate integral
        return (b - a) * total / n;
    }

}
