"""Own opt-in ideal represented-scene CPU producer and conditional composition.

Derives fields AND path L1 bounds in one call, not from supplied fields/bounds.
Exact bounded CPU traversal, rational length/sqrt enclosures and Taylor
remainders. No libm sin/cos, GPU paths, fitted matrix or native admission.
"""
from fractions import Fraction as F
import hashlib
import json
import math
import struct

from history_trace_cpu_v1 import trace_scene
from history_lengths_cpu_v1 import reconstruct_lengths, sqrt_interval
from history_lineage_cpu_v2 import scene_binding, triangles
from coherent_reduction_cpu_v1 import f32, rational
from coherent_error_composition_cpu_v1 import compose_field_errors

PI_LOWER = F('3.14159265358979323846264338327950288419716939937510')
PI_UPPER = F('3.14159265358979323846264338327950288419716939937511')
DEGREE = 48
ERROR_SCALE = 2**128


def l1(z):
    return abs(z[0])+abs(z[1])


def multiply(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def rotation(angle):
    """Rational polynomials: each real Taylor remainder <= |x|^49/49!.

    Both sin/cos degree48 polynomials share this conservative L1 bound.
    Domain is deliberately bounded, not enlarged from frozen scene bounds.
    """
    angle = F(angle)
    if abs(angle) > 8:
        raise ValueError('CPU coefficient/propagation angle outside [-8,8] rad')
    term = F(1); real = F(0); imag = F(0)
    for n in range(DEGREE+1):
        if n % 4 == 0: real += term
        elif n % 4 == 1: imag += term
        elif n % 4 == 2: real -= term
        else: imag -= term
        term *= angle/F(n+1)
    return (real, imag), 2*abs(angle)**(DEGREE+1)/math.factorial(DEGREE+1)


def product_with_error(a, ea, b, eb):
    # Complex L1 is submultiplicative; includes the cross term ea*eb.
    return multiply(a, b), l1(a)*eb+l1(b)*ea+ea*eb


def rounded_error(error):
    """Outward dyadic ABI <=256 bits; never round an error bound down."""
    scaled = error*ERROR_SCALE
    result = F(-(-scaled.numerator//scaled.denominator), ERROR_SCALE)
    if result.numerator.bit_length() > 256:
        raise ValueError('CPU error bound outside bounded rational ABI')
    return rational(result)


def produce_scene_fields(snapshot, *, coherence_groups, algorithm='neumaier32',
                         field_budget=1e-4, intensity_budget=2e-4):
    """Complete scene-derived fields versus the SAME ideal represented scene.

    Source fields and optics are exact represented inputs. The ideal model
    has unit plane-wave terminal modes and exp(i*2*pi*L/lambda). Coefficient
    sqrt, mirror phases, path-length enclosure, pi/Taylor approximation and
    final binary32 component conversion are all charged, then composed with
    modeled RN32 reduction. This is NOT a bound for any native backend.
    """
    binding, packed = scene_binding(snapshot)
    sources = {s['id']: s for s in snapshot['sources']}
    if type(coherence_groups) is not dict or set(coherence_groups) != set(sources) or \
            any(type(g) is not str or not g for g in coherence_groups.values()):
        raise ValueError('explicit coherence group for EVERY scene source required')
    generated = trace_scene(snapshot)  # No caller-supplied terminal/field ledger.
    lengths = reconstruct_lengths(snapshot, generated['records'])
    terminals = {p['id']: p for p in lengths['terminals']}
    geometry = triangles(packed)
    wavelength = F(snapshot['lambda_BU'])
    reference = 'ideal-scene-source-gauge:'+binding
    metadata = {sid: {'coherence_group': coherence_groups[sid],
        'lambda_BU': snapshot['lambda_BU'], 'phase_reference_id': reference} for sid in sources}
    amplitudes = {}; rows = []; bounds = []; evidence = []
    for record in generated['records']:
        rid = record['id']; sid = record['source_id']; event = record['event']
        if record['parent_id'] is None:
            z = tuple(map(F, sources[sid]['field_reim'])); error = F(0)
        else:
            z, error = amplitudes[record['parent_id']]
            owner = geometry[record['primitive_id']][0]
            obj = snapshot['objects'][packed.geometry.object_ids[owner]]
            if event in ('t', 'r'):
                tau = F(packed.optics[owner*12+1])
                lo, hi = sqrt_interval(tau if event == 't' else 1-tau)
                mid = (lo+hi)/2
                coefficient = (mid, F(0)) if event == 't' else (F(0), mid)
                z, error = product_with_error(z, error, coefficient, (hi-lo)/2)
            elif event == 'mirror':
                coefficient, delta = rotation(F(obj['phase_rad']))
                z, error = product_with_error(z, error, tuple(-x for x in coefficient), delta)
        amplitudes[rid] = (z, error)
        if rid not in terminals: continue
        info = terminals[rid]; enclosure = info['effective_length']
        lo, hi = F(*enclosure['rational_lower']), F(*enclosure['rational_upper'])
        turns = (lo+hi)/(2*wavelength)
        reduced = turns-((turns+F(1,2))//1)  # Signed reference corrections allowed.
        pi_mid = (PI_LOWER+PI_UPPER)/2
        angle = 2*pi_mid*reduced
        unit, taylor_error = rotation(angle)
        angle_error = 2*PI_UPPER*(hi-lo)/(2*wavelength)+abs(reduced)*(PI_UPPER-PI_LOWER)
        # norm2 chord <= min(2, angular deviation), L1 <= 2*norm2.
        unit_error = taylor_error+min(F(4), 2*angle_error)
        ideal_approx, total = product_with_error(z, error, unit, unit_error)
        represented = [f32(float(x)) for x in ideal_approx]
        conversion = sum((abs(F(v)-x) for v, x in zip(represented, ideal_approx)), F(0))
        words = [struct.unpack('<I', struct.pack('<f', x))[0] for x in represented]
        row = {'id': rid, 'source_id': sid, 'port': info['port'], 'field_uint32': words}
        rows.append(row)
        bounds.append({**row, **metadata[sid],
            'field_error_L1_upper_rational': rounded_error(total+conversion)})
        evidence.append({'id': rid, 'effective_length': enclosure,
            'reduced_turns_rational': rational(reduced),
            'coefficient_error_L1_upper_rational': rounded_error(error),
            'propagation_unit_error_L1_upper_rational': rounded_error(unit_error),
            'conversion_error_L1_upper_rational': rounded_error(conversion)})
    composition = compose_field_errors(rows, expected_ids=list(terminals), sources=metadata,
        path_error_bounds=bounds, algorithm=algorithm, field_budget=field_budget,
        intensity_budget=intensity_budget)
    payload = {'scene_binding_sha256': binding, 'sources': metadata,
        'rows': rows, 'path_error_bounds': bounds, 'path_evidence': evidence}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False,
        separators=(',', ':')).encode()).hexdigest()
    return {'schema': 'exp005-scene-field-producer-CPU-v1', **payload,
        'producer_payload_sha256': digest, 'generated_record_count': len(generated['records']),
        'nearest_queries': generated['nearest_queries'], 'composition': composition,
        'accepted_ideal_scene_CPU_only': composition['accepted_conditional_upstream_and_reduction_only'],
        'upstream_bounds_origin': 'same own CPU producer, regenerated ideal represented scene',
        'upstream_metric': 'complex L1; explicit L1 <= 2*norm2 for propagation phase',
        'scene_complete_within_frozen_CPU_profile': True,
        'execution_authenticated': False, 'native_promotion_allowed': False,
        'CPU_paths_supplied_to_GPU': False, 'GPU_executed': False, 'no_jev_aval': True,
        'excluded': ['uncertainty before represented snapshot/hi-lo native export',
            'encoded wavelength and compensated/native phase transport candidates',
            'GPU ALU/driver/libm/FTZ/reassociation and detection arithmetic',
            'physical source calibration/coherence/mode overlap/RT']}
