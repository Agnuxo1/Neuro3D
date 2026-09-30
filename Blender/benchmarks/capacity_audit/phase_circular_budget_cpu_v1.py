"""A-posteriori rational phase bound for a represented CPU scalar trace.

Not an authenticated native trace, uniform-domain theorem, sin/cos driver
certificate, scene error budget or GPU admission. No scene/routes/weights.
"""
from fractions import Fraction as F
import math
import struct
import sys

PI_UPPER = F('3.14159265358979323846264338327950288519716939937511')
PI_LOWER = PI_UPPER - F(1, 10**50)


def _require(trace, key, expected):
    actual = trace.get(key)
    if type(actual) is not float or not math.isfinite(actual) or actual != expected:
        raise ValueError('invalid represented arithmetic step: ' + key)
    # Zero sign is immaterial to this ideal-phasor bound, not certified here.


def scalar_circular_budget(length, wavelength, trace, *, field_budget):
    if type(trace) is not dict:
        raise ValueError('explicit scalar trace required')
    if any(type(v) is not float or not math.isfinite(v)
           for v in (length, wavelength, field_budget)):
        raise ValueError('finite represented scalars required')
    if length < 0 or wavelength <= 0 or field_budget < 0:
        raise ValueError('invalid signs')
    if any(0 < abs(v) < sys.float_info.min for v in (length, wavelength)):
        raise ValueError('subnormal input unsupported')
    exact_q = F(length) / F(wavelength)
    try:
        q = float(exact_q)
    except OverflowError as error:
        raise ValueError('quotient overflow outside prototype domain') from error
    if not math.isfinite(q) or q >= 2**52 or (length and q < sys.float_info.min):
        raise ValueError('outside compensated prototype domain')
    _require(trace, 'quotient_binary64', q)
    residual = float(F(length) - F(q)*F(wavelength))
    _require(trace, 'residual_binary64', residual)
    correction = float(F(residual)/F(wavelength))
    _require(trace, 'correction_binary64', correction)
    if abs(correction) > .5 or any(0 < abs(v) < sys.float_info.min
                                   for v in (residual, correction)):
        raise ValueError('unsupported normal-arithmetic domain')
    cycles = float((F(q) - math.floor(q)) + F(correction))
    integer = math.floor(float(F(cycles) + F(1, 2)))
    reduced = float(F(cycles) - integer)
    _require(trace, 'reduced_cycles_binary64', reduced)
    product64 = float(F(math.tau)*F(reduced))
    angle32 = struct.unpack('<f', struct.pack('<f', product64))[0]
    _require(trace, 'angle_float32', angle32)

    # Choose the shortest cycle displacement; no discontinuous angle compare.
    difference = F(reduced) - exact_q
    circular = difference - ((difference + F(1, 2)) // 1)
    cycle_term = 2*PI_UPPER*abs(circular)
    tau_error = max(abs(F(math.tau)-2*PI_LOWER), abs(F(math.tau)-2*PI_UPPER))
    tau_term = tau_error*abs(F(reduced))
    # Exact represented subtraction includes BOTH multiply64 and cast32 errors.
    final_term = abs(F(angle32)-F(math.tau)*F(reduced))
    rad_upper = cycle_term + tau_term + final_term
    chord_upper = min(F(2), rad_upper)  # |exp(i a)-exp(i b)| <= min(2, |a-b|)
    upper_float = float(chord_upper)
    if F(upper_float) < chord_upper:
        upper_float = math.nextafter(upper_float, math.inf)
    encode = lambda value: [value.numerator, value.denominator]
    return {'cycle_error_circular_rational': encode(circular),
            'cycle_term_upper_rad': encode(cycle_term),
            'tau_term_upper_rad': encode(tau_term),
            'multiply_and_cast_term_rad': encode(final_term),
            'ideal_unit_phasor_error_upper_rational': encode(chord_upper),
            'ideal_unit_phasor_error_upper_float': upper_float,
            'field_budget_satisfied_arithmetic_only': chord_upper <= F(field_budget),
            'represented_RN_trace_validated': True,
            'trace_execution_authenticated': False,
            'uniform_domain_bound_proved': False,
            'sin_cos_driver_certified': False,
            'native_promotion_allowed': False,
            'scope': 'conditional point-scalars and ideal exponential; excludes scene/driver/inputs uncertainty'}
