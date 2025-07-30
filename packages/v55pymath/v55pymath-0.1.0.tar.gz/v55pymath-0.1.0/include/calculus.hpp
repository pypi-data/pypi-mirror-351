#pragma once
#include <functional>
#include <vector>
#include <utility>

namespace calculus {

    /**
     * @brief Finds a local extremum (minimum or maximum) of a function in a given interval.
     * 
     * @param f The function to analyze.
     * @param a Start of the interval.
     * @param b End of the interval.
     * @param step Step size for scanning the interval.
     * @return The x-value at which the extremum occurs.
     */
    double find_extrema(const std::function<double(double)>& f, double a, double b, double step = 1e-5);

    /**
     * @brief Numerically integrates a function over an interval using the trapezoidal rule.
     * 
     * @param f The function to integrate.
     * @param a Lower bound of the integral.
     * @param b Upper bound of the integral.
     * @param n Number of subintervals.
     * @return Approximate value of the definite integral.
     */
    double integrate(const std::function<double(double)>& f, double a, double b, int n = 1000);

    /**
     * @brief Numerically computes a double integral over a rectangular region using the composite trapezoidal rule.
     * 
     * @param f The function f(x, y) to integrate.
     * @param ax Lower bound for x.
     * @param bx Upper bound for x.
     * @param ay Lower bound for y.
     * @param by Upper bound for y.
     * @param nx Number of subintervals in x.
     * @param ny Number of subintervals in y.
     * @return Approximate value of the double integral.
     */
    double integrate_double(const std::function<double(double, double)>& f,
                            double ax, double bx, double ay, double by,
                            int nx = 100, int ny = 100);

    /**
     * @brief Numerically computes a triple integral over a rectangular prism region using the composite trapezoidal rule.
     * 
     * @param f The function f(x, y, z) to integrate.
     * @param ax Lower bound for x.
     * @param bx Upper bound for x.
     * @param ay Lower bound for y.
     * @param by Upper bound for y.
     * @param az Lower bound for z.
     * @param bz Upper bound for z.
     * @param nx Number of subintervals in x.
     * @param ny Number of subintervals in y.
     * @param nz Number of subintervals in z.
     * @return Approximate value of the triple integral.
     */
    double integrate_triple(const std::function<double(double, double, double)>& f,
                            double ax, double bx, double ay, double by, double az, double bz,
                            int nx = 20, int ny = 20, int nz = 20);

    /**
     * @brief Solves an ordinary differential equation (ODE) dy/dt = f(t, y) using Euler's method.
     * 
     * @param f Function representing the derivative dy/dt.
     * @param y0 Initial value of y at t = t0.
     * @param t0 Start time.
     * @param t1 End time.
     * @param h Step size for integration.
     * @return Vector of (t, y) pairs representing the approximate solution.
     */
    std::vector<std::pair<double, double>> solve_ode(const std::function<double(double, double)>& f,
                                                     double y0, double t0, double t1, double h = 0.01);

}
