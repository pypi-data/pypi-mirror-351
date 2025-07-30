#pragma once
#include <vector>
#include <stdexcept>
#include <complex>

namespace matrix {

    /// Alias for complex numbers with double precision.
    using Complex = std::complex<double>;

    /// Alias for a matrix of complex numbers.
    using Matrix = std::vector<std::vector<Complex>>;

    /**
     * @brief Checks if a matrix is square (i.e., rows == columns).
     * 
     * @param matrix The matrix to check.
     * @throws std::invalid_argument if the matrix is not square.
     */
    void check_square(const Matrix& matrix);

    /**
     * @brief Multiplies every element of a matrix by a scalar.
     * 
     * @param matrix The input matrix.
     * @param scalar The scalar to multiply by.
     * @return The result of scalar multiplication.
     */
    Matrix multiply_scalar(const Matrix& matrix, const Complex& scalar);

    /**
     * @brief Computes the determinant of a square matrix.
     * 
     * @param matrix The square matrix.
     * @return The determinant as a complex number.
     * @throws std::invalid_argument if the matrix is not square.
     */
    Complex determinant(const Matrix& matrix);

    /**
     * @brief Computes the Hermitian conjugate (conjugate transpose) of a matrix.
     * 
     * @param matrix The input matrix.
     * @return The Hermitian conjugate.
     */
    Matrix hermitian_conjugate(const Matrix& matrix);

    /**
     * @brief Multiplies two matrices.
     * 
     * @param A The first matrix.
     * @param B The second matrix.
     * @return The product of matrices A and B.
     * @throws std::invalid_argument if the matrices have incompatible dimensions.
     */
    Matrix multiply(const Matrix& A, const Matrix& B);

    /**
     * @brief Approximates the matrix exponential using a truncated power series.
     * 
     * @param matrix The input square matrix.
     * @param iterations The number of terms to include in the power series. Default is 10.
     * @return The exponential of the matrix.
     * @throws std::invalid_argument if the matrix is not square.
     */
    Matrix exponential(const Matrix& matrix, int iterations = 10);

    /**
     * @brief Raises a square matrix to an integer power.
     * 
     * @param matrix The input square matrix.
     * @param power The non-negative integer exponent.
     * @return The matrix raised to the given power.
     * @throws std::invalid_argument if the matrix is not square or power is negative.
     */
    Matrix power(const Matrix& matrix, int power);

    /**
     * @brief Computes the inverse of a square matrix.
     * 
     * @param matrix The input square matrix.
     * @return The inverse of the matrix.
     * @throws std::invalid_argument if the matrix is not square or is singular.
     */
    Matrix inverse(const Matrix& matrix);

    /**
     * @brief Generates an identity matrix of given size.
     * 
     * @param n The size of the identity matrix.
     * @return An n x n identity matrix.
     */
    Matrix identity_matrix(size_t n);

    /**
     * @brief Computes the minor matrix by removing a specific row and column.
     * 
     * @param matrix The input matrix.
     * @param row The row to remove.
     * @param col The column to remove.
     * @return The resulting minor matrix.
     */
    Matrix matrix_minor(const Matrix& matrix, size_t row, size_t col);

} // namespace matrix
