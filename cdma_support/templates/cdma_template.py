import numpy as np

def encode(bits, codes):
    """Encode each user bit with that user's chipping code.
    bits:  shape (U,), values in {-1, +1}
    codes: shape (U, L), values in {-1, +1}
    returns encoded chips with shape (U, L)
    """
    # TODO: implement encoding
    return bits[:, None] * codes


def modulate(encoded_chips):
    """Combine all users on the shared channel.
    encoded_chips: shape (U, L)
    returns tx_signal: shape (L,)
    """
    # TODO: implement modulation (sum across users)
    return encoded_chips.sum(axis=0)


def demodulate(tx_signal, noise_std=0.0, rng=None):
    """Channel / receiver front-end.
    Add optional Gaussian noise and return received chips.
    """
    # TODO: implement demodulation/channel handling
    if rng is None:
        rng = np.random.default_rng(0)
    return tx_signal + noise_std * rng.normal(size=tx_signal.shape[0])


def decode(rx_signal, codes):
    """Recover each user bit by correlation with each user's code.
    rx_signal: shape (L,)
    codes:     shape (U, L)
    returns bits_hat: shape (U,), values in {-1, +1}
    """
    # TODO: implement decoding
    corr = codes @ rx_signal
    return np.where(corr >= 0, 1, -1)


def run_cdma_pipeline(bits, codes, noise_std=0.0, seed=7):
    """Keep this wrapper for testing; students usually edit stage functions above."""
    bits = np.asarray(bits, dtype=np.int32)
    codes = np.asarray(codes, dtype=np.int32)
    encoded = encode(bits, codes)
    tx_signal = modulate(encoded)
    rng = np.random.default_rng(seed)
    rx_signal = demodulate(tx_signal, noise_std=noise_std, rng=rng)
    bits_hat = decode(rx_signal, codes)
    return np.asarray(bits_hat, dtype=np.int32)