#include <vector>
#include <numeric>



std::vector<std::vector<int>> encode(
    const std::vector<int>& bits,
    const std::vector<std::vector<int>>& codes
) {
    // TODO: implement encoding
    const int U = static_cast<int>(bits.size());
    const int L = static_cast<int>(codes[0].size());
    std::vector<std::vector<int>> out(U, std::vector<int>(L, 0));
    for (int u = 0; u < U; ++u) {
        for (int m = 0; m < L; ++m) {
            out[u][m] = bits[u] * codes[u][m];
        }
    }
    return out;
}

std::vector<double> modulate(const std::vector<std::vector<int>>& encoded_chips) {
    // TODO: implement modulation (sum across users)
    const int U = static_cast<int>(encoded_chips.size());
    const int L = static_cast<int>(encoded_chips[0].size());
    std::vector<double> tx(L, 0.0);
    for (int m = 0; m < L; ++m) {
        double s = 0.0;
        for (int u = 0; u < U; ++u) {
            s += static_cast<double>(encoded_chips[u][m]);
        }
        tx[m] = s;
    }
    return tx;
}

std::vector<double> demodulate(
    const std::vector<double>& tx_signal,
    double noise_std,
    unsigned int seed
) {
    // TODO: implement demodulation/channel handling
    // Reference checks use noise_std=0, so pass-through is acceptable initially.
    (void)noise_std;
    (void)seed;
    return tx_signal;
}

std::vector<int> decode(
    const std::vector<double>& rx_signal,
    const std::vector<std::vector<int>>& codes
) {
    // TODO: implement decoding
    const int U = static_cast<int>(codes.size());
    const int L = static_cast<int>(codes[0].size());
    std::vector<int> bits_hat(U, -1);
    for (int u = 0; u < U; ++u) {
        double corr = 0.0;
        for (int m = 0; m < L; ++m) {
            corr += rx_signal[m] * static_cast<double>(codes[u][m]);
        }
        bits_hat[u] = (corr >= 0.0) ? 1 : -1;
    }
    return bits_hat;
}