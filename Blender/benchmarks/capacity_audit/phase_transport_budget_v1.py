"""Prospective CPU wavelength-only phase budget; no frozen runner integration.

The caller must prove the declared effective-length bound independently. This
does not enumerate rays, reduce phase, compute outputs or certify total error.
"""
from decimal import Decimal, localcontext, ROUND_CEILING
from fractions import Fraction
from frontier_inputs import scalar
from wavelength_transport_v1 import checked_wavelength

# Decimal prefix of pi rounded UP; using a rational avoids intermediate rounding.
PI_UPPER = Fraction('3.14159265358979323846264338327950288519716939937511')


def wavelength_phase_budget(value, *, max_effective_length_BU,
                            phase_budget_rad, relative_budget):
    length = scalar(max_effective_length_BU)
    budget = scalar(phase_budget_rad)
    if length < 0 or budget < 0:
        raise ValueError('nonnegative explicit length and phase budgets required')
    transport = checked_wavelength(value, relative_budget=relative_budget)
    original = Fraction(scalar(value))
    decoded = Fraction(transport['decoded_BU'])
    bound = 2*PI_UPPER*Fraction(length)*abs(decoded-original)/(original*decoded)
    with localcontext() as ctx:
        ctx.prec = 80
        ctx.rounding = ROUND_CEILING
        upper = Decimal(bound.numerator)/Decimal(bound.denominator)
    return {'accepted': bound <= Fraction(budget),
            'wavelength_transport': transport,
            'declared_max_effective_length_BU': length,
            'phase_budget_rad': budget,
            'wavelength_phase_upper_rad_decimal': str(upper),
            'scope': 'wavelength encoding only; supplied length bound unverified',
            'excluded': ['geometry/export precision', 'length accumulation',
                         'reference/source fields', 'GPU phase reduction',
                         'multiple-path field amplification']}
