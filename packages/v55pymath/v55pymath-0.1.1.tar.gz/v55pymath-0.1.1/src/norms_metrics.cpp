#include "norms_metrics.hpp"
#include "math_utils.hpp"

namespace norms_metrics {

    /**
     * @brief Computes the L1 norm (Manhattan norm) of a vector.
     * 
     * The L1 norm is the sum of the absolute values of the vector elements.
     * 
     * @param v Input vector of doubles.
     * @return The L1 norm of the vector.
     */
    double vector_l1_norm(const std::vector<double>& v) {
        double sum = 0;
        for (double x : v) {
            sum += std::abs(x);
        }
        return sum;
    }

    /**
     * @brief Computes the L2 norm (Euclidean norm) of a vector.
     * 
     * The L2 norm is the square root of the sum of the squares of the vector elements.
     * 
     * @param v Input vector of doubles.
     * @return The L2 norm of the vector.
     */
    double vector_l2_norm(const std::vector<double>& v) {
        double sum = 0;
        for (double x : v) {
            sum += x * x;
        }
        return math_utils::newton_sqrt(sum);
    }

    /**
     * @brief Computes the L∞ norm (maximum norm) of a vector.
     * 
     * The L∞ norm is the maximum absolute value among the vector elements.
     * 
     * @param v Input vector of doubles.
     * @return The L∞ norm of the vector.
     */
    double vector_linf_norm(const std::vector<double>& v) {
        auto max_it = std::max_element(v.begin(), v.end(),
            [](double a, double b) { return std::abs(a) < std::abs(b); });
        return std::abs(*max_it);
    }

    /**
     * @brief Computes the Frobenius norm of a matrix.
     * 
     * The Frobenius norm is the square root of the sum of the squares of all matrix elements.
     * 
     * @param matrix Input 2D vector representing the matrix.
     * @return The Frobenius norm of the matrix.
     */
    double matrix_frobenius_norm(const std::vector<std::vector<double>>& matrix) {
        double sum = 0;
        for (const auto& row : matrix) {
            for (double x : row) {
                sum += x * x;
            }
        }
        return math_utils::newton_sqrt(sum);
    }

    /**
     * @brief Computes the L1 norm of a matrix.
     * 
     * The L1 norm of a matrix is the maximum absolute column sum.
     * 
     * @param matrix Input 2D vector representing the matrix.
     * @return The L1 norm of the matrix.
     */
    double matrix_l1_norm(const std::vector<std::vector<double>>& matrix) {
        size_t rows = matrix.size();
        size_t cols = matrix[0].size();

        double max_sum = 0.0;
        for (size_t j = 0; j < cols; ++j) {
            double col_sum = 0.0;
            for (size_t i = 0; i < rows; ++i) {
                col_sum += std::abs(matrix[i][j]);
            }
            max_sum = std::max(max_sum, col_sum);
        }
        return max_sum;
    }

    /**
     * @brief Computes the L∞ norm of a matrix.
     * 
     * The L∞ norm of a matrix is the maximum absolute row sum.
     * 
     * @param matrix Input 2D vector representing the matrix.
     * @return The L∞ norm of the matrix.
     */
    double matrix_linf_norm(const std::vector<std::vector<double>>& matrix) {
        double max_sum = 0;
        for (const auto& row : matrix) {
            double row_sum = 0;
            for (double x : row) {
                row_sum += std::abs(x);
            }
            max_sum = std::max(max_sum, row_sum);
        }
        return max_sum;
    }

    /**
     * @brief Computes the Euclidean distance between two vectors.
     * 
     * The Euclidean distance is the L2 norm of the difference vector (v1 - v2).
     * 
     * @param v1 First vector.
     * @param v2 Second vector.
     * @return The Euclidean distance between v1 and v2.
     */
    double euclidean_distance(const std::vector<double>& v1, const std::vector<double>& v2) {
        double sum = 0;
        for (size_t i = 0; i < v1.size(); ++i) {
            sum += (v1[i] - v2[i]) * (v1[i] - v2[i]);
        }
        return math_utils::newton_sqrt(sum, 1e-10);
    }

    /**
     * @brief Computes the Manhattan distance between two vectors.
     * 
     * The Manhattan distance is the sum of the absolute differences of their coordinates.
     * 
     * @param v1 First vector.
     * @param v2 Second vector.
     * @return The Manhattan distance between v1 and v2.
     */
    double manhattan_distance(const std::vector<double>& v1, const std::vector<double>& v2) {
        double sum = 0;
        for (size_t i = 0; i < v1.size(); ++i) {
            sum += std::abs(v1[i] - v2[i]);
        }
        return sum;
    }

    /**
     * @brief Computes the Chebyshev distance between two vectors.
     * 
     * The Chebyshev distance is the maximum absolute difference between the coordinates of the vectors.
     * 
     * @param v1 First vector.
     * @param v2 Second vector.
     * @return The Chebyshev distance between v1 and v2.
     */
    double chebyshev_distance(const std::vector<double>& v1, const std::vector<double>& v2) {
        double max_diff = 0;
        for (size_t i = 0; i < v1.size(); ++i) {
            max_diff = std::max(max_diff, std::abs(v1[i] - v2[i]));
        }
        return max_diff;
    }

}
