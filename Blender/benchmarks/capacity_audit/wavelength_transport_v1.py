"""Opt-in CPU validation of wavelength transport, not field accuracy.

No frozen runner uses this candidate automatically. A relative wavelength
budget cannot certify phase error without a separate path-length/error budget.
"""
import math
from frontier_inputs import scalar


def checked_wavelength(value, *, relative_budget):
    value = scalar(value)
    relative_budget = scalar(relative_budget)
    if value <= 0:
        raise ValueError('positive wavelength required')
    if not 0 <= relative_budget < 1:
        raise ValueError('explicit relative transport budget in [0,1) required')
    from exp005_blender_gpu import split_double
    try:
        hi, lo = split_double(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError('wavelength cannot be represented by the frozen hi-lo ABI') from exc
    decoded = float(hi)+float(lo)
    if not math.isfinite(decoded) or decoded <= 0:
        raise ValueError('wavelength transport collapsed to zero or nonfinite')
    relative_error = abs(decoded-value)/value
    if relative_error > relative_budget:
        raise ValueError('wavelength relative transport budget exceeded')
    return {'hi': hi, 'lo': lo, 'decoded_BU': decoded,
            'relative_error': relative_error, 'relative_budget': relative_budget}
