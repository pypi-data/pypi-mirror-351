#pragma once
#include <vector>

namespace norms_metrics {

    /**
     * @brief Computes the L1 norm (Manhattan norm) of a vector.
     * @param v Input vector.
     * @return L1 norm of the vector.
     */
    double vector_l1_norm(const std::vector<double>& v);

    /**
     * @brief Computes the L2 norm (Euclidean norm) of a vector.
     * @param v Input vector.
     * @return L2 norm of the vector.
     */
    double vector_l2_norm(const std::vector<double>& v);

    /**
     * @brief Computes the L∞ norm (maximum norm) of a vector.
     * @param v Input vector.
     * @return L∞ norm of the vector.
     */
    double vector_linf_norm(const std::vector<double>& v);

    /**
     * @brief Computes the Frobenius norm of a matrix.
     * @param matrix Input matrix.
     * @return Frobenius norm of the matrix.
     */
    double matrix_frobenius_norm(const std::vector<std::vector<double>>& matrix);

    /**
     * @brief Computes the L1 norm of a matrix (maximum absolute column sum).
     * @param matrix Input matrix.
     * @return L1 norm of the matrix.
     */
    double matrix_l1_norm(const std::vector<std::vector<double>>& matrix);

    /**
     * @brief Computes the L∞ norm of a matrix (maximum absolute row sum).
     * @param matrix Input matrix.
     * @return L∞ norm of the matrix.
     */
    double matrix_linf_norm(const std::vector<std::vector<double>>& matrix);

    /**
     * @brief Computes the Euclidean distance between two vectors.
     * @param v1 First vector.
     * @param v2 Second vector.
     * @return Euclidean distance between v1 and v2.
     */
    double euclidean_distance(const std::vector<double>& v1, const std::vector<double>& v2);

    /**
     * @brief Computes the Manhattan distance between two vectors.
     * @param v1 First vector.
     * @param v2 Second vector.
     * @return Manhattan distance between v1 and v2.
     */
    double manhattan_distance(const std::vector<double>& v1, const std::vector<double>& v2);

    /**
     * @brief Computes the Chebyshev distance between two vectors.
     * @param v1 First vector.
     * @param v2 Second vector.
     * @return Chebyshev distance between v1 and v2.
     */
    double chebyshev_distance(const std::vector<double>& v1, const std::vector<double>& v2);

} // namespace norms_metrics
