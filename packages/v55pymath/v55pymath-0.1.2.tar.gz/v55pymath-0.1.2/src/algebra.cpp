#include "algebra.hpp"
#include <cmath>
#include <vector>
#include <stdexcept>

namespace algebra {

/**
 * @brief Solve a system of linear algebraic equations (SLAE) Ax = b using Gaussian elimination with partial pivoting.
 * 
 * This function takes a square matrix A and a right-hand side vector b,
 * and returns the solution vector x such that Ax = b.
 * It uses partial pivoting to improve numerical stability.
 * 
 * @param A Square matrix of coefficients (n x n).
 * @param b Right-hand side vector (size n).
 * @return std::vector<double> Solution vector x.
 * 
 * @throws std::invalid_argument If the input dimensions mismatch or if the matrix is singular (non-invertible).
 */
std::vector<double> solve_slae(const std::vector<std::vector<double>>& A, const std::vector<double>& b) {
    // Validate input dimensions
    if (A.empty() || b.size() != A.size()) {
        throw std::invalid_argument("Dimension mismatch: b must have the same size as A rows");
    }

    size_t n = A.size();

    // Create working copies to avoid modifying original inputs
    std::vector<std::vector<double>> matrix = A;
    std::vector<double> result = b;

    // Forward elimination phase with partial pivoting
    for (size_t i = 0; i < n; ++i) {
        // Find pivot row with maximum absolute value in column i
        size_t max_row = i;
        for (size_t k = i + 1; k < n; ++k) {
            if (std::abs(matrix[k][i]) > std::abs(matrix[max_row][i])) {
                max_row = k;
            }
        }

        // Check for singular matrix (pivot element too close to zero)
        if (std::abs(matrix[max_row][i]) < 1e-20) {
            throw std::invalid_argument("Singular matrix detected");
        }

        // Swap current row with pivot row
        std::swap(matrix[i], matrix[max_row]);
        std::swap(result[i], result[max_row]);

        // Eliminate entries below the pivot
        for (size_t k = i + 1; k < n; ++k) {
            double factor = matrix[k][i] / matrix[i][i];
            result[k] -= factor * result[i];
            for (size_t j = i; j < n; ++j) {
                matrix[k][j] -= factor * matrix[i][j];
            }
        }
    }

    // Back substitution phase to find solution vector x
    std::vector<double> x(n);
    for (int i = static_cast<int>(n) - 1; i >= 0; --i) {
        double sum = 0.0;
        for (size_t j = i + 1; j < n; ++j) {
            sum += matrix[i][j] * x[j];
        }
        x[i] = (result[i] - sum) / matrix[i][i];
    }

    return x;
}

} // namespace algebra
