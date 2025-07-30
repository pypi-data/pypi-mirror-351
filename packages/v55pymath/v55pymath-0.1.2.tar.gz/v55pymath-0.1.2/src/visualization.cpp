#include "visualization.hpp"
#include <vector>
#include <cstdio>
#include <algorithm>
#include <string>

namespace visualization {

    /**
     * @brief Plots a solution as an ASCII graph on the console.
     * 
     * This function takes a vector of (time, value) pairs and prints
     * an ASCII representation where the horizontal position of the '*' 
     * corresponds to the scaled value y, and the time t is shown on the left.
     * 
     * @param solution Vector of pairs (t, y), representing points of the solution.
     *                 - t: time or independent variable.
     *                 - y: function value or dependent variable at time t.
     * 
     * If the input vector is empty, the function returns without output.
     * The y-values are scaled linearly to fit within a fixed width (20 characters).
     * 
     * Output format per line:
     *   "t_value |<spaces>*"
     * 
     * The newline uses carriage return and line feed ("\r\n") for Windows compatibility.
     */
    void plot_solution(const std::vector<std::pair<double, double>>& solution) {
        if (solution.empty()) {
            return; // Silently return for empty solution
        }

        // Find minimum and maximum y values for scaling the plot horizontally
        double min_y = solution[0].second;
        double max_y = solution[0].second;
        for (const auto& [t, y] : solution) {
            min_y = std::min(min_y, y);
            max_y = std::max(max_y, y);
        }

        // Define horizontal scale (maximum number of spaces)
        const int scale = 20;

        // Plot each (t, y) point as a line with '*' positioned proportionally to y
        for (const auto& [t, y] : solution) {
            int pos = 0;
            if (max_y > min_y + 1e-10) { // Prevent division by zero in case of constant y
                pos = static_cast<int>(scale * (y - min_y) / (max_y - min_y));
                // Clamp position within [0, scale]
                pos = std::max(0, std::min(pos, scale));
            }

            // Generate a string of spaces for horizontal positioning of '*'
            std::string spaces(pos, ' ');

            // Print formatted line: time, pipe character, spaces, and '*'
            std::printf("%.2f |%s *\r\n", t, spaces.c_str());
            std::fflush(stdout); // Flush output buffer to ensure immediate display
        }
    }

} // namespace visualization
