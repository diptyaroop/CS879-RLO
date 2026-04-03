#include <iostream>
#include <vector>

std::vector<std::vector<int>> encode(
    const std::vector<int>& bits,
    const std::vector<std::vector<int>>& codes
);
std::vector<double> modulate(const std::vector<std::vector<int>>& encoded_chips);
std::vector<double> demodulate(
    const std::vector<double>& tx_signal,
    double noise_std,
    unsigned int seed
);
std::vector<int> decode(
    const std::vector<double>& rx_signal,
    const std::vector<std::vector<int>>& codes
);

int main() {
    std::vector<int> bits = {1, -1, 1};
    std::vector<std::vector<int>> codes = {
        {1, 1, 1, 1, 1, 1, 1, 1},
        {1, -1, 1, -1, 1, -1, 1, -1},
        {1, 1, -1, -1, 1, 1, -1, -1}
    };

    auto encoded = encode(bits, codes);
    auto tx = modulate(encoded);
    auto rx = demodulate(tx, 0.0, 7);
    auto out = decode(rx, codes);

    for (size_t i = 0; i < out.size(); ++i) {
        if (i) std::cout << ' ';
        std::cout << (out[i] >= 0 ? 1 : -1);
    }
    std::cout << std::endl;
    return 0;
}