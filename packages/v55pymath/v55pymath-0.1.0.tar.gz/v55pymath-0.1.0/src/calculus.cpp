#include "calculus.hpp"
#include <functional>
#include <vector>

namespace calculus {

/**
 * @brief Finds an extremum (local minimum or maximum) of a function within a given interval using discrete steps.
 * 
 * This function scans the interval [a, b] with a fixed step size and detects sign changes in the discrete derivative,
 * indicating a local extremum.
 * 
 * @param f Function to analyze. Takes a double argument and returns a double.
 * @param a Lower bound of the interval.
 * @param b Upper bound of the interval.
 * @param step Step size used for discretization.
 * @return double x-coordinate of the detected extremum, or -1.0 if no extremum is found.
 */
double find_extrema(const std::function<double(double)>& f, double a, double b, double step) {
    double prev = a;
    double curr = a + step;

    while (curr <= b) {
        if ((f(curr) - f(prev)) * (f(curr + step) - f(curr)) < 0) {
            return curr;
        }
        prev = curr;
        curr += step;
    }

    return -1.0;
}

/**
 * @brief Numerically integrates a function over [a, b] using the trapezoidal rule.
 * 
 * The interval is divided into n subintervals, and the trapezoidal rule is applied to approximate the integral.
 * 
 * @param f Function to integrate. Takes a double argument and returns a double.
 * @param a Lower limit of integration.
 * @param b Upper limit of integration.
 * @param n Number of subintervals to divide [a, b].
 * @return double Approximate value of the definite integral.
 */
double integrate(const std::function<double(double)>& f, double a, double b, int n) {
    double h = (b - a) / n;
    double result = 0.5 * (f(a) + f(b));

    for (int i = 1; i < n; ++i) {
        result += f(a + i * h);
    }

    return result * h;
}

/**
 * @brief Numerically integrates a function of two variables over a rectangular region using the rectangular (midpoint) rule.
 * 
 * The region [ax, bx] x [ay, by] is divided into nx by ny subintervals. The function is evaluated at the bottom-left corner of each subrectangle.
 * 
 * @param f Function to integrate. Takes two doubles (x, y) and returns a double.
 * @param ax Lower bound for x.
 * @param bx Upper bound for x.
 * @param ay Lower bound for y.
 * @param by Upper bound for y.
 * @param nx Number of subintervals in the x-direction.
 * @param ny Number of subintervals in the y-direction.
 * @return double Approximate value of the double integral.
 */
double integrate_double(const std::function<double(double, double)>& f,
                        double ax, double bx, double ay, double by,
                        int nx, int ny) {
    double hx = (bx - ax) / nx;
    double hy = (by - ay) / ny;
    double result = 0;

    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            double x = ax + i * hx;
            double y = ay + j * hy;
            result += f(x, y) * hx * hy;
        }
    }

    return result;
}

/**
 * @brief Numerically integrates a function of three variables over a rectangular parallelepiped region using the rectangular rule.
 * 
 * The region [ax, bx] x [ay, by] x [az, bz] is divided into nx by ny by nz subintervals. The function is evaluated at the corner of each sub-box.
 * 
 * @param f Function to integrate. Takes three doubles (x, y, z) and returns a double.
 * @param ax Lower bound for x.
 * @param bx Upper bound for x.
 * @param ay Lower bound for y.
 * @param by Upper bound for y.
 * @param az Lower bound for z.
 * @param bz Upper bound for z.
 * @param nx Number of subintervals in the x-direction.
 * @param ny Number of subintervals in the y-direction.
 * @param nz Number of subintervals in the z-direction.
 * @return double Approximate value of the triple integral.
 */
double integrate_triple(const std::function<double(double, double, double)>& f,
                        double ax, double bx, double ay, double by, double az, double bz,
                        int nx, int ny, int nz) {
    double hx = (bx - ax) / nx;
    double hy = (by - ay) / ny;
    double hz = (bz - az) / nz;
    double result = 0;

    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                double x = ax + i * hx;
                double y = ay + j * hy;
                double z = az + k * hz;
                result += f(x, y, z) * hx * hy * hz;
            }
        }
    }

    return result;
}

/**
 * @brief Solves an ordinary differential equation (ODE) dy/dt = f(t, y) using Euler's method.
 * 
 * Starting from initial condition y(t0) = y0, the solution is advanced in steps of size h until t1 is reached.
 * The method approximates the solution by linear increments.
 * 
 * @param f Function defining the ODE, taking time t and state y, returning dy/dt.
 * @param y0 Initial value of y at t0.
 * @param t0 Initial time.
 * @param t1 Final time.
 * @param h Step size.
 * @return std::vector<std::pair<double, double>> Vector of (t, y) pairs representing the approximate solution.
 */
std::vector<std::pair<double, double>> solve_ode(const std::function<double(double, double)>& f,
                                                double y0, double t0, double t1, double h) {
    double t = t0;
    double y = y0;

    std::vector<std::pair<double, double>> solution;
    solution.emplace_back(t, y);

    while (t < t1) {
        y += h * f(t, y);
        t += h;
        solution.emplace_back(t, y);
    }

    return solution;
}

} // namespace calculus
