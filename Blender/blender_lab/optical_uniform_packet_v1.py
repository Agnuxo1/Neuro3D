"""Bounded, byte-preserving host packet candidate; not integrated in a GPU trial."""
import numpy as np


def optical_uniform_bytes(rows, count=14):
    if count != 14 or not 0 < len(rows) <= 256 or any(len(row) != count for row in rows):
        raise ValueError('Bounded fixed UBO extent required')
    values = np.asarray(rows, dtype='<f8')
    if values.shape != (len(rows), 14) or not np.isfinite(values).all():
        raise ValueError('Finite UBO binary64 required')
    packet = np.zeros((256, 16), dtype='<f8')
    packet[:len(rows), :14] = values
    return packet.tobytes(order='C')
