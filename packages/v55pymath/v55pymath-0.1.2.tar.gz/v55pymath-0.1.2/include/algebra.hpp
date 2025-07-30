#pragma once
#include <vector>
#include <stdexcept>

namespace algebra {

    /**
     * @brief Solves a system of linear algebraic equations (SLAE) using Gaussian elimination.
     * 
     * This function solves the system Ax = b for x, where:
     * - A is a square coefficient matrix.
     * - b is the right-hand side vector.
     * 
     * @param A Coefficient matrix (NxN)
     * @param b Right-hand side vector (length N)
     * @return Solution vector x (length N)
     * 
     * @throws std::invalid_argument if the matrix A is not square or if the dimensions of A and b are incompatible.
     * @throws std::runtime_error if the system has no unique solution.
     */
    std::vector<double> solve_slae(
        const std::vector<std::vector<double>>& A, 
        const std::vector<double>& b
    );

}
