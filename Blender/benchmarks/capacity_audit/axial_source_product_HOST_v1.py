"""Opt-in HOST source times propagation unit, NOT total field or amplitude gate."""
import base64
from fractions import Fraction as F
import hashlib
import json
import struct
import axial_quarter_unit_HOST_v1 as unit
import axial_native_source_encoder_v1 as encoder
MODEL = 'axial-source-hilo32-decode-RN64-product-HOST-v1'

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def pair(v):
    v = F(v)
    return [v.numerator, v.denominator]

def digest(v):
    return hashlib.sha256(unit.quarter.prev.quotient.phase.canon(v)).hexdigest()

def bound(value):
    require(type(value) is list and len(value) == 2 and
            all(type(v) is int for v in value) and value[0] >= 0 and value[1] > 0,
            'nonnegative exact rational L1 bound required')
    return F(*value)

def product_HOST(original_source_uint64, unit_uint64, unit_error_L1, *, model):
    """Mathematical primitive; caller-supplied unit bound is NOT authenticated evidence."""
    require(model == MODEL, 'explicit HOST source product model required')
    require(type(unit_uint64) is list and len(unit_uint64) == 2, 'two unit words')
    u = [unit.polynomial.component64(v) for v in unit_uint64]
    bu = bound(unit_error_L1)
    encoded = encoder.encode_complex(original_source_uint64)
    source = [F(*v) for v in encoded['source_exact_limb_sum_rational']]
    original = [encoder.decode(v, 64) for v in original_source_uint64]
    trace = []
    def rn(a, b, op, label):
        exact = a * b if op == 'mul' else a + b
        word, value = unit.polynomial.round64(exact)
        trace.append({'label': label, 'op': op, 'inputs': [pair(a), pair(b)],
                      'output_uint64': word, 'delta': pair(value - exact)})
        return word, value
    decoded = []
    for i in range(2):
        high, low = encoded['source_limb_uint32'][2*i:2*i+2]
        _, value = rn(encoder.decode(high, 32), encoder.decode(low, 32), 'add', 'decode' + str(i))
        decoded.append(value)
    a, b = decoded
    c, d = u
    _, ac = rn(a, c, 'mul', 'ac')
    _, bd = rn(b, d, 'mul', 'bd')
    _, ad = rn(a, d, 'mul', 'ad')
    _, bc = rn(b, c, 'mul', 'bc')
    wr, real = rn(ac, -bd, 'add', 'real')
    wi, imag = rn(ad, bc, 'add', 'imag')
    eenc = F(*encoded['source_encoding_error_L1'])
    edec = sum((abs(x-y) for x, y in zip(decoded, source)), F(0))
    nu = sum(map(abs, u), F(0))
    ns = sum(map(abs, original), F(0))
    eround = sum((abs(F(*n['delta'])) for n in trace[2:]), F(0))
    charges = {'source_encoding': eenc * nu, 'source_decode_RN64': edec * nu,
               'unit_to_ORIGINAL': ns * bu, 'product_RN64': eround}
    exact_decoded_product = [a*c-b*d, a*d+b*c]
    exact_original_times_represented_unit = [original[0]*c-original[1]*d,
                                           original[0]*d+original[1]*c]
    total = sum(charges.values(), F(0))
    observed = sum((abs(x-y) for x, y in zip([real, imag], exact_original_times_represented_unit)), F(0))
    require(observed <= charges['source_encoding']+charges['source_decode_RN64']+eround,
            'source product rational bound violated')
    return {'model': MODEL, 'source_encoder': encoded, 'unit_uint64': list(unit_uint64),
            'unit_error_L1_to_ORIGINAL_bound': pair(bu),
            'source_decoded_RN64': list(map(pair, decoded)), 'operations': trace,
            'product_uint64': [wr, wi], 'product_rational': [pair(real), pair(imag)],
            'exact_decoded_product': list(map(pair, exact_decoded_product)),
            'exact_original_times_represented_unit': list(map(pair, exact_original_times_represented_unit)),
            'observed_error_to_original_times_represented_unit_L1': pair(observed),
            'charges_L1': {k: pair(v) for k, v in charges.items()},
            'error_L1_to_original_source_times_ideal_unit_bound': pair(total),
            'costs_partial': {'HOST_encoder_RN32_casts': 4, 'HOST_exact_residual_subtractions': 2,
                              'HOST_decode_RN64_adds': 2, 'modeled_product_RN64_muls': 4,
                              'modeled_product_RN64_adds': 2},
            'source_product_evaluated': True, 'amplitude_budget_accepted': False,
            'accepted_full_field_pipeline': False, 'field_sum_computed': False,
            'reflection_coefficient_applied': False, 'GPU_executed': False}

def source_inputs(parent, expected_sha256, previous):
    """Raw input bytes only; matches ORIGINAL field words and ordered unique IDs."""
    require(digest(parent) == expected_sha256, 'parent receipt')
    buffers = {k: base64.b64decode(v, validate=True) for k, v in parent['buffers_base64'].items()}
    for key, raw in buffers.items():
        require(parent['manifest']['buffers'][key] ==
                {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}, 'buffer receipt')
    metadata = encoder.parse(buffers['input_metadata_json'])
    snapshot = encoder.parse(buffers['original_scene_json'])
    ids = metadata['source_order']
    require(ids == previous['source_order'] == [s['id'] for s in snapshot['sources']] and
            len(ids) == len(set(ids)) and 1 <= len(ids) <= 64, 'ordered unique source coverage')
    require(metadata['scene_binding_sha256'] == previous['scene_binding_sha256'] and
            metadata['word_ABI_sha256'] == previous['word_ABI_sha256'], 'source scene binding')
    require(metadata['original_snapshot_sha256'] ==
            hashlib.sha256(buffers['original_scene_json']).hexdigest(), 'snapshot receipt')
    require(parent['manifest']['layout']['sources']['stride_words'] == 32 and
            len(buffers['sources']) == 128*len(ids), 'source stride')
    fields = []
    for i, sid in enumerate(ids):
        raw = buffers['sources'][128*i+112:128*i+128]
        field = snapshot['sources'][i]['field_reim']
        require(type(field) is list and len(field) == 2 and
                all(type(v) in (float, int) for v in field), 'original complex source input')
        require(raw == struct.pack('<dd', *field), 'ORIGINAL source field bits')
        fields.append({'source_id': sid, 'original_source_uint64': list(struct.unpack('<QQ', raw))})
    return fields

def audit_scene_product_HOST(name, parent, parent_sha256, overlay, overlay_sha256, *, model):
    require(model == MODEL, 'explicit HOST source product model required')
    previous = unit.audit_scene_unit_HOST(name, parent, parent_sha256, overlay, overlay_sha256, model=unit.MODEL)
    fields = source_inputs(parent, parent_sha256, previous)
    rows = []
    for old, field in zip(previous['sources'], fields):
        sid = field['source_id']
        require(old['source_id'] == sid and old['phase_reference_id'] ==
                'original-source-zero:' + previous['scene_binding_sha256'] + ':' + sid, 'source gauge')
        row = dict(field, phase_reference_id=old['phase_reference_id'],
                   terminal_reference_id=old['terminal_reference_id'], upstream_unit_row_sha256=digest(old),
                   source_product_evaluated=False, amplitude_budget_accepted=False,
                   accepted_full_field_pipeline=False)
        if not old['accepted_unit_phase_bound_CPU_only']:
            row['reason'] = old['reason']
        else:
            row['unchanged_original_phase_cap_rad'] = old['unchanged_original_phase_cap_rad']
            row['upstream_unit_phase_bound_rad'] = old['composed_unit_phase_bound_rad']
            try:
                products = [product_HOST(field['original_source_uint64'], v['unit_uint64'],
                            old['composed_unit_error_L1_to_ORIGINAL_bound'], model=model)
                            for v in old['encoded_corner_units_HOST']]
                row.update(source_product_evaluated=True, encoded_corner_products=products,
                           product_error_L1_to_ORIGINAL_bound=pair(max(F(*v['error_L1_to_original_source_times_ideal_unit_bound']) for v in products)))
            except ValueError as e:
                row['reason'] = str(e)
        rows.append(row)
    return {'model': MODEL, 'case_name': name, 'input_packet_sha256': parent_sha256,
            'overlay_sha256': overlay_sha256, 'scene_binding_sha256': previous['scene_binding_sha256'],
            'word_ABI_sha256': previous['word_ABI_sha256'], 'source_order': previous['source_order'],
            'sources': rows, 'HOST_only': True, 'amplitude_budget_accepted': False,
            'field_values_computed': False, 'field_sum_computed': False, 'detector_evaluated': False,
            'native_kernel_implemented': False, 'GPU_executed': False, 'GPU_job_admission': False,
            'execution_authenticated': False, 'reflection_coefficient_applied': False,
            'accepted_full_field_pipeline': False,
            'cost_scope': 'partial only; fresh unit/scene/reference/quarter costs and HOST work are EXTRA',
            'scope': 'per-source amplitude times propagation unit ONLY; no new amplitude cap or phase-of-product gate'}
