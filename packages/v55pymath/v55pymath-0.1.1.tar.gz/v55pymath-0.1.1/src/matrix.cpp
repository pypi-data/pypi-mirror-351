#include "matrix.hpp"
#include <cmath>
#include <algorithm>

namespace matrix {

    /**
     * @brief Check if a matrix is square.
     * @param matrix Input matrix to check.
     * @throw std::invalid_argument if the matrix is not square or is empty.
     */
    void check_square(const Matrix& matrix) {
        if (matrix.empty() || matrix.size() != matrix[0].size()) {
            throw std::invalid_argument("Matrix must be square");
        }
    }

    /**
     * @brief Multiply a matrix by a scalar.
     * @param matrix Input matrix.
     * @param scalar Complex scalar multiplier.
     * @return New matrix resulting from scalar multiplication.
     */
    Matrix multiply_scalar(const Matrix& matrix, const Complex& scalar) {
        Matrix result = matrix;
        for (auto& row : result) {
            for (auto& element : row) {
                element *= scalar;
            }
        }
        return result;
    }

    /**
     * @brief Create an identity matrix of size n x n.
     * @param n Dimension of the identity matrix.
     * @return Identity matrix of size n x n.
     */
    Matrix identity_matrix(size_t n) {
        Matrix I(n, std::vector<Complex>(n, 0.0));
        for (size_t i = 0; i < n; ++i) {
            I[i][i] = 1.0;
        }
        return I;
    }

    /**
     * @brief Compute the minor matrix by removing specified row and column.
     * @param matrix Input matrix.
     * @param row Row index to remove.
     * @param col Column index to remove.
     * @return Minor matrix after removing the specified row and column.
     * @throw std::out_of_range if row or col is out of bounds.
     */
    Matrix matrix_minor(const Matrix& matrix, size_t row, size_t col) {
        if (matrix.empty() || row >= matrix.size() || col >= matrix[0].size()) {
            throw std::out_of_range("Invalid row or column index");
        }

        Matrix minor;
        for (size_t i = 0; i < matrix.size(); ++i) {
            if (i == row) continue;
            std::vector<Complex> new_row;
            for (size_t j = 0; j < matrix[i].size(); ++j) {
                if (j != col) new_row.push_back(matrix[i][j]);
            }
            minor.push_back(new_row);
        }
        return minor;
    }

    /**
     * @brief Calculate the determinant of a square matrix.
     * Uses recursive Laplace expansion.
     * @param matrix Input square matrix.
     * @return Determinant as a Complex number.
     * @throw std::invalid_argument if matrix is not square.
     */
    Complex determinant(const Matrix& matrix) {
        check_square(matrix);
        if (matrix.size() == 1) return matrix[0][0];
        
        Complex det = 0.0;
        for (size_t col = 0; col < matrix[0].size(); ++col) {
            Complex sign = (col % 2 == 0) ? 1.0 : -1.0;
            det += matrix[0][col] * sign * determinant(matrix_minor(matrix, 0, col));
        }
        return det;
    }

    /**
     * @brief Compute the Hermitian conjugate (conjugate transpose) of a matrix.
     * @param matrix Input matrix.
     * @return Hermitian conjugate matrix.
     */
    Matrix hermitian_conjugate(const Matrix& matrix) {
        Matrix result(matrix[0].size(), std::vector<Complex>(matrix.size()));
        for (size_t i = 0; i < matrix.size(); ++i) {
            for (size_t j = 0; j < matrix[i].size(); ++j) {
                result[j][i] = std::conj(matrix[i][j]);
            }
        }
        return result;
    }

    /**
     * @brief Multiply two square matrices.
     * @param A First input matrix.
     * @param B Second input matrix.
     * @return Result of multiplication A * B.
     * @throw std::invalid_argument if matrices are not square or sizes mismatch.
     */
    Matrix multiply(const Matrix& A, const Matrix& B) {
        check_square(A);
        check_square(B);
        size_t n = A.size();
        Matrix result(n, std::vector<Complex>(n, 0.0));
        
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                for (size_t k = 0; k < n; ++k) {
                    result[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        return result;
    }

    /**
     * @brief Compute the matrix exponential using Taylor series expansion.
     * exp(A) = I + A + A^2/2! + A^3/3! + ...
     * @param matrix Input square matrix A.
     * @param iterations Number of terms in the Taylor series.
     * @return Matrix exponential exp(A).
     */
    Matrix exponential(const Matrix& matrix, int iterations) {
        size_t n = matrix.size();
        
        // Initialize result as the identity matrix
        Matrix result = identity_matrix(n);
        
        // Start with the identity matrix as the first term
        Matrix current_term = result;
        
        // Initialize factorial for k=0
        double factorial = 1.0;
        
        // Compute Taylor series: exp(A) = I + A + A^2/2! + A^3/3! + ...
        for (int k = 1; k <= iterations; ++k) {
            // Update current term: current_term = current_term * A
            current_term = multiply(current_term, matrix);
            
            // Update factorial: k! = k * (k-1)!
            factorial *= static_cast<double>(k);
            
            // Add current_term / k! to the result
            for (size_t i = 0; i < n; ++i) {
                for (size_t j = 0; j < n; ++j) {
                    result[i][j] += current_term[i][j] / factorial;
                }
            }
        }
        
        return result;
    }

    /**
     * @brief Raise a square matrix to an integer power.
     * Uses exponentiation by squaring for efficiency.
     * @param matrix Input square matrix.
     * @param power Integer power (can be negative).
     * @return Matrix raised to the specified power.
     * @throw std::invalid_argument if matrix is not square or singular for negative powers.
     */
    Matrix power(const Matrix& matrix, int power) {
        check_square(matrix);
        if (power == 0) return identity_matrix(matrix.size());
        
        Matrix result = identity_matrix(matrix.size());
        Matrix base = matrix;
        int exponent = abs(power);
        
        while (exponent > 0) {
            if (exponent % 2 == 1) {
                result = multiply(result, base);
            }
            base = multiply(base, base);
            exponent /= 2;
        }
        return (power < 0) ? inverse(result) : result;
    }

    /**
     * @brief Compute the inverse of a square matrix using the adjugate method.
     * @param matrix Input square matrix.
     * @return Inverse of the matrix.
     * @throw std::invalid_argument if the matrix is singular or not square.
     */
    Matrix inverse(const Matrix& matrix) {
        check_square(matrix);
        size_t n = matrix.size();
        Complex det = determinant(matrix);
        if (std::abs(det) < 1e-10) {
            throw std::invalid_argument("Matrix is singular");
        }
        
        Matrix adjugate(n, std::vector<Complex>(n));
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                Complex sign = ((i + j) % 2 == 0) ? 1.0 : -1.0;
                adjugate[j][i] = sign * determinant(matrix_minor(matrix, i, j));
            }
        }
        return multiply_scalar(adjugate, Complex(1.0)/det);
    }
}
