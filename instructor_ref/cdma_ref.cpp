#include <cmath>
#include <cstdint>
#include <random>
#include <vector>

#if defined(_WIN32)
#define CDMA_EXPORT __declspec(dllexport)
#else
#define CDMA_EXPORT __attribute__((visibility("default")))
#endif

extern "C" CDMA_EXPORT int cdma_reference_decode(
    int users,
    int chip_len,
    const int* bits,
    const int* codes_flat,
    double noise_std,
    unsigned int seed,
    int* out_decoded_bits
) {
    if (users <= 0 || chip_len <= 0 || bits == nullptr || codes_flat == nullptr || out_decoded_bits == nullptr) {
        return -1;
    }

    std::vector<double> rx(static_cast<size_t>(chip_len), 0.0);

    // Encoding + modulation: sum over all users for each chip.
    for (int u = 0; u < users; ++u) {
        const int b = bits[u] >= 0 ? 1 : -1;
        for (int m = 0; m < chip_len; ++m) {
            const int c = codes_flat[u * chip_len + m] >= 0 ? 1 : -1;
            rx[m] += static_cast<double>(b * c);
        }
    }

    // Add deterministic Gaussian noise for reproducible hidden checks.
    std::mt19937 rng(seed);
    std::normal_distribution<double> dist(0.0, noise_std);
    for (int m = 0; m < chip_len; ++m) {
        rx[m] += dist(rng);
    }

    // Demodulation + decoding via correlation with each user's code.
    for (int u = 0; u < users; ++u) {
        double corr = 0.0;
        for (int m = 0; m < chip_len; ++m) {
            const int c = codes_flat[u * chip_len + m] >= 0 ? 1 : -1;
            corr += rx[m] * static_cast<double>(c);
        }
        out_decoded_bits[u] = (corr >= 0.0) ? 1 : -1;
    }

    return 0;
}
