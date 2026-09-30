"""Opt-in scalar CPU candidate, NOT native/GPU admission or a scene backend.

Requires binary64 nearest-even with correctly rounded math.fma, no FTZ.
No fallback to multiply-then-subtract. No coefficient/geometry error budget.
"""
import math
import struct
import sys

QUOTIENT_CAP_EXCLUSIVE = float(2**52)


def _normal_or_zero(value):
    return value == 0 or abs(value) >= sys.float_info.min


def compensated_angle(length, wavelength):
    """Return a float32 angle for two already represented binary64 scalars.

    This prototype has no certified driver/libm/global error bound. Its
    explicit arithmetic domain is not permission to expand scene bounds.
    """
    for name, value in (('length', length), ('wavelength', wavelength)):
        if type(value) is not float or not math.isfinite(value):
            raise ValueError(name + ': finite binary64 float required')
        if not _normal_or_zero(value):
            raise ValueError(name + ': subnormal input unsupported')
    if length < 0 or wavelength <= 0:
        raise ValueError('nonnegative length and positive wavelength required')
    fma = getattr(math, 'fma', None)
    if not callable(fma):
        raise ValueError('correctly rounded FMA required; no fallback')
    quotient = length / wavelength
    if (not math.isfinite(quotient) or quotient >= QUOTIENT_CAP_EXCLUSIVE
            or not _normal_or_zero(quotient) or (length > 0 and quotient == 0)):
        raise ValueError('quotient outside prototype domain')
    residual = fma(-quotient, wavelength, length)
    if not math.isfinite(residual) or not _normal_or_zero(residual):
        raise ValueError('non-normal FMA residual unsupported')
    correction = residual / wavelength
    if not math.isfinite(correction) or not _normal_or_zero(correction):
        raise ValueError('non-normal correction unsupported')
    if abs(correction) > .5:
        raise ValueError('division rounding model not satisfied')
    cycles = (quotient - math.floor(quotient)) + correction
    reduced = cycles - math.floor(cycles + .5)
    angle = struct.unpack('<f', struct.pack('<f', math.tau * reduced))[0]
    return {'angle_float32': angle, 'quotient_binary64': quotient,
            'residual_binary64': residual, 'correction_binary64': correction,
            'reduced_cycles_binary64': reduced,
            'native_promotion_allowed': False,
            'complete_precision_budget_certified': False}
