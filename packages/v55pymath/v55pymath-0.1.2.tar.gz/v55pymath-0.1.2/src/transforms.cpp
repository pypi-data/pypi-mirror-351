#include "transforms.hpp"
#include "math_utils.hpp"
#include <cmath>
#include <stdexcept>

namespace transforms {

    /**
     * @brief Computes the Discrete Fourier Transform (DFT) of a complex signal.
     * 
     * Uses the direct summation formula for DFT:
     *   X(k) = sum_{n=0}^{N-1} x(n) * exp(-2πikn/N)
     * 
     * @param signal Input vector of complex numbers representing the signal in time domain.
     * @return Vector of complex numbers representing the frequency spectrum.
     */
    std::vector<std::complex<double>> dft(const std::vector<std::complex<double>>& signal) {
        size_t N = signal.size();
        std::vector<std::complex<double>> transform(N);
        
        for (size_t k = 0; k < N; ++k) {
            double real = 0.0;
            double imag = 0.0;
            for (size_t n = 0; n < N; ++n) {
                double angle = -2 * math_utils::PI * k * n / N;
                double c = math_utils::taylor_cos(angle);
                double s = math_utils::taylor_sin(angle);
                real += signal[n].real() * c - signal[n].imag() * s;
                imag += signal[n].real() * s + signal[n].imag() * c;
            }
            transform[k] = std::complex<double>(real, imag);
        }

        return transform;
    }

    /**
     * @brief Computes the Inverse Discrete Fourier Transform (IDFT) of a complex spectrum.
     * 
     * Uses the inverse summation formula for IDFT:
     *   x(n) = (1/N) * sum_{k=0}^{N-1} X(k) * exp(2πikn/N)
     * 
     * Note: Returns only the real part of the reconstructed signal.
     * 
     * @param transform Input vector of complex numbers representing the frequency spectrum.
     * @return Vector of doubles representing the reconstructed time-domain signal.
     */
    std::vector<double> idft(const std::vector<std::complex<double>>& transform) {
        size_t N = transform.size();
        std::vector<double> signal(N);
        
        for (size_t n = 0; n < N; ++n) {
            double real = 0.0;
            double imag = 0.0;
            for (size_t k = 0; k < N; ++k) {
                double angle = 2 * math_utils::PI * k * n / N;
                double c = math_utils::taylor_cos(angle);
                double s = math_utils::taylor_sin(angle);
                real += transform[k].real() * c - transform[k].imag() * s;
                imag += transform[k].real() * s + transform[k].imag() * c;
            }
            signal[n] = real / N; 
        }

        return signal;
    }

    /**
     * @brief Computes the Fast Fourier Transform (FFT) of a complex signal.
     * 
     * Implements the Cooley-Tukey radix-2 decimation-in-time FFT algorithm.
     * Signal length must be a power of two.
     * 
     * @param signal Input vector of complex numbers representing the signal in time domain.
     * @return Vector of complex numbers representing the frequency spectrum.
     * @throws std::invalid_argument if signal size is not a power of two.
     */
    std::vector<std::complex<double>> fft(const std::vector<std::complex<double>>& signal) {
        size_t N = signal.size();

        if (N <= 1) return signal;

        if ((N & (N - 1)) != 0) {
            throw std::invalid_argument("Signal length must be a power of 2");
        }

        std::vector<std::complex<double>> even(N / 2);
        std::vector<std::complex<double>> odd(N / 2);

        for (size_t i = 0; i < N / 2; ++i) {
            even[i] = signal[2 * i];
            odd[i] = signal[2 * i + 1];
        }

        even = fft(even);
        odd = fft(odd);

        std::vector<std::complex<double>> result(N);
        for (size_t k = 0; k < N / 2; ++k) {
            double twiddle_factor = -2 * math_utils::PI * k / N;
            double c = math_utils::taylor_cos(twiddle_factor);
            double s = math_utils::taylor_sin(twiddle_factor);

            std::complex<double> odd_term(odd[k].real() * c - odd[k].imag() * s,
                                          odd[k].real() * s + odd[k].imag() * c);

            result[k] = even[k] + odd_term;
            result[k + N / 2] = even[k] - odd_term;
        }

        return result;
    }

    /**
     * @brief Numerically computes the Laplace transform of a function f(t).
     * 
     * The Laplace transform is defined as:
     *   L{f}(s) = ∫_0^∞ f(t) * exp(-s * t) dt,
     * where s = s_real + i * s_imag.
     * 
     * This implementation performs numerical integration using the rectangle method
     * over the interval [0, t_max] with step size dt.
     * 
     * @param f Pointer to a function of a single double argument representing f(t).
     * @param s_real Real part of complex parameter s.
     * @param s_imag Imaginary part of complex parameter s.
     * @param t_max Upper limit of integration (integration from 0 to t_max).
     * @param dt Integration step size.
     * @return Pair of doubles representing the real and imaginary parts of L{f}(s).
     */
    std::pair<double, double> laplace_transform(double (*f)(double), double s_real, double s_imag, double t_max, double dt) {
        double integral_real = 0.0;
        double integral_imag = 0.0;
        double t = 0.0;

        while (t <= t_max) {
            double st_real = s_real * t;
            double st_imag = s_imag * t;
            double exp_real = math_utils::taylor_exp(-st_real) * math_utils::taylor_cos(st_imag);
            double exp_imag = -math_utils::taylor_exp(-st_real) * math_utils::taylor_sin(st_imag);

            double ft = f(t);
            integral_real += ft * exp_real * dt;
            integral_imag += ft * exp_imag * dt;

            t += dt;
        }

        return {integral_real, integral_imag};
    }
}
