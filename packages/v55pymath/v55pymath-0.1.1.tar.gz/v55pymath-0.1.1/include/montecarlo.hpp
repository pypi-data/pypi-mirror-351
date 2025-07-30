#pragma once
#include <functional>

namespace montecarlo {

    /**
     * @brief Estimates the definite integral of a function using the Monte Carlo method.
     * 
     * This method approximates the integral of the function \f$f(x)\f$ over the interval \f$[a, b]\f$
     * by randomly sampling \f$n\f$ points in the interval and averaging the function values.
     * 
     * @param f The function to integrate.
     * @param a The lower bound of the integration interval.
     * @param b The upper bound of the integration interval.
     * @param n The number of random samples to use (default is 1000).
     * @return The estimated value of the integral.
     * @throws std::invalid_argument if n <= 0 or if a >= b.
     */
    double monte_carlo_integral(std::function<double(double)> f, double a, double b, int n = 1000);

} // namespace montecarlo
