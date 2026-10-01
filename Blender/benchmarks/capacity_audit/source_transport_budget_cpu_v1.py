"""Opt-in, scene-bound source hi-lo budget; no native/phase/trace execution.

Uses the frozen packer and split helper, preserves source order and measures
exact rational limb error separately from modeled CPU binary64 decoding.
These are source-input errors, NOT terminal-field or complete-scene bounds.
"""
from fractions import Fraction as F
import math
import struct

from history_lineage_cpu_v2 import scene_binding
from exp005_blender_gpu import split_double


def ratio(value):
    value = F(value)
    return [value.numerator, value.denominator]


def budget(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, F)):
        raise ValueError('explicit finite nonnegative rational source budget required')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('finite source budget required')
    value = F(value)
    if value < 0:
        raise ValueError('nonnegative source budget required')
    return value


def component(value):
    try:
        hi, lo = split_double(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError('source outside frozen finite hi-lo ABI') from exc
    words = [struct.unpack('<I', struct.pack('<f', x))[0] for x in (hi, lo)]
    ideal = F(value)
    limbs = F(hi)+F(lo)
    decoded = hi+lo  # CPU binary64 model only; no claim about driver dtype.
    if not math.isfinite(decoded):
        raise ValueError('finite CPU source decoding required')
    return {
        'input_binary64_rational': ratio(ideal), 'limb_uint32': words,
        'exact_limb_sum_rational': ratio(limbs),
        'limb_error_signed_rational': ratio(limbs-ideal),
        'modeled_CPU64_decode_rational': ratio(decoded),
        'CPU64_decode_rounding_signed_rational': ratio(F(decoded)-limbs),
        'total_error_signed_rational': ratio(F(decoded)-ideal),
        'has_binary32_subnormal_limb': any((w & 0x7f800000) == 0 and
                                         (w & 0x007fffff) != 0 for w in words),
        'nonzero_input_collapsed_to_zero': ideal != 0 and decoded == 0,
        'input_negative_zero': value == 0 and math.copysign(1., value) < 0,
        'decoded_negative_zero': decoded == 0 and math.copysign(1., decoded) < 0,
    }


def audit_source_transport(snapshot, *, coherence_groups, absolute_L1_budget,
                           relative_L1_budget):
    """Budgets per source; no cancellation credited across distinct sources.

    Units are those of snapshot field_reim; relative L1 is dimensionless.
    A zero field has relative error0 only when its transport error is zero.
    Native admission ALWAYS false, even with all numeric budgets satisfied.
    """
    absolute = budget(absolute_L1_budget)
    relative = budget(relative_L1_budget)
    binding, packed = scene_binding(snapshot)  # Same frozen bounded scene ABI.
    if type(coherence_groups) is not dict or set(coherence_groups) != set(packed.source_ids) or \
            any(type(x) is not str or not x for x in coherence_groups.values()):
        raise ValueError('explicit coherence group for every and only scene source required')
    rows = []
    for i, sid in enumerate(packed.source_ids):
        # Actual packed origin/re/dir/im layout: field offsets3 and7 in row8.
        values = [packed.sources[8*i+3], packed.sources[8*i+7]]
        components = list(map(component, values))
        norm = sum((abs(F(x)) for x in values), F(0))
        error = sum((abs(F(*c['total_error_signed_rational'])) for c in components), F(0))
        relative_error = error/norm if norm else F(0)
        absolute_ok = error <= absolute
        relative_ok = relative_error <= relative
        rows.append({'source_id': sid, 'source_index': i,
            'coherence_group': coherence_groups[sid], 'scene_binding_sha256': binding,
            'source_phase_reference_id': 'ideal-scene-source-gauge:'+binding,
            'packed_field_offsets': [8*i+3, 8*i+7], 'components': components,
            'input_field_L1_rational': ratio(norm),
            'source_transport_error_L1_rational': ratio(error),
            'relative_source_transport_error_L1_rational': ratio(relative_error),
            'absolute_budget_satisfied': absolute_ok, 'relative_budget_satisfied': relative_ok,
            'accepted_CPU_source_transport_budget_only': absolute_ok and relative_ok})
    return {'schema': 'exp005-source-transport-budget-CPU-v1',
        'scene_binding_sha256': binding, 'source_order': list(packed.source_ids),
        'absolute_L1_budget_rational': ratio(absolute),
        'relative_L1_budget_rational': ratio(relative), 'sources': rows,
        'accepted_CPU_source_transport_budget_only': all(
            row['accepted_CPU_source_transport_budget_only'] for row in rows),
        'requires_native_subnormal_semantics': any(
            c['has_binary32_subnormal_limb'] for row in rows for c in row['components']),
        'native_admitted': False, 'native_promotion_allowed': False,
        'GPU_executed': False, 'scene_traced': False, 'terminal_bounds_certified': False,
        'scope': 'source field hi-lo numerical transport, same bounded represented-scene ABI',
        'excluded': ['geometry/length/reference/wavelength transport and phase arithmetic',
                     'coefficient amplification and terminal reduction/detection',
                     'GPU RN/FTZ/FMA/dtype, runtime binding, RT and physical calibration']}
