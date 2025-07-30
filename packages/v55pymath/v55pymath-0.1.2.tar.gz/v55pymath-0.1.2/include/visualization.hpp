#pragma once
#include <vector>
#include <utility>

namespace visualization {

    /**
     * @brief Plots a solution as an ASCII graph with time and value axes.
     *
     * Displays the (time, value) pairs as a simple ASCII plot in the console,
     * scaling values to fit within a fixed-width line.
     *
     * @param solution A vector of (t, y) pairs representing time and corresponding values.
     *                 The time (t) is shown on the left, and a '*' marks the scaled value position.
     */
    void plot_solution(
        const std::vector<std::pair<double, double>>& solution
    );

} // namespace visualization
