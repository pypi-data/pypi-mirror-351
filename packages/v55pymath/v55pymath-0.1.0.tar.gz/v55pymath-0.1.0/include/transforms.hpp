#pragma once
#include <vector>
#include <complex>

namespace transforms {

    /**
     * @brief Computes the Discrete Fourier Transform (DFT) of a complex signal.
     * @param signal Input signal represented as a vector of complex numbers.
     * @return DFT of the signal as a vector of complex numbers.
     */
    std::vector<std::complex<double>> dft(
        const std::vector<std::complex<double>>& signal
    );
    
    /**
     * @brief Computes the Inverse Discrete Fourier Transform (IDFT).
     * @param transform Input frequency-domain signal as complex numbers.
     * @return Reconstructed time-domain signal as a vector of real values.
     */
    std::vector<double> idft(
        const std::vector<std::complex<double>>& transform
    );
    
    /**
     * @brief Computes the Fast Fourier Transform (FFT) of a complex signal.
     *        The input size must be a power of two.
     * @param signal Input signal represented as a vector of complex numbers.
     * @return FFT of the signal as a vector of complex numbers.
     */
    std::vector<std::complex<double>> fft(
        const std::vector<std::complex<double>>& signal
    );
    
    /**
     * @brief Approximates the Laplace Transform of a real function f(t) evaluated at s = s_real + i * s_imag.
     * @param f Function pointer to f(t).
     * @param s_real Real part of Laplace variable s.
     * @param s_imag Imaginary part of Laplace variable s.
     * @param t_max Upper bound of the integration interval [0, t_max].
     * @param dt Time step for numerical integration.
     * @return Pair of doubles representing the real and imaginary parts of the Laplace Transform at s.
     */
    std::pair<double, double> laplace_transform(
        double (*f)(double),
        double s_real,
        double s_imag,
        double t_max,
        double dt
    );

} // namespace transforms
