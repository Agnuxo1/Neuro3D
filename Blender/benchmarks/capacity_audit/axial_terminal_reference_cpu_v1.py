"""Opt-in fixed-original terminal plane-wave reference, CPU exact model only.

Consumes retained word geometry; no branch tracing, scene writer or native run.
HOST mode-reference encoding is new, explicitly charged, not a free exact ABI.
"""
import base64
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-fixed-original-terminal-plane-reference-CPU-v1'
FRAME = 'fixed original world point; ideal unit-X plane-wave mode'
S = 1 << 149
CLOSURE = 'coordinacion/respuestas/AXIAL-SCENE-CLOSURE-001-CODEX.json'
CLOSURE_SHA = '0f545f51b6dd76fd259ab7e230dfd2e13cbf815690edd961dfb1dac8b9211d25'
GEOMETRY = 'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
GEOMETRY_SHA = 'dfdb03a27f7aaa58dd05d750ea1980de789281ed798b75fd2c5209d12712a5fa'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def ratio(q):
    q = F(q)
    return [q.numerator, q.denominator]


def rational(v):
    require(type(v) is list and len(v) == 2 and all(type(x) is int for x in v)
            and v[1] > 0, 'exact rational pair required')
    return F(*v)


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def finite(v):
    require(type(v) in (int, float) and math.isfinite(v), 'finite original number required')
    return F(v)


def vector(v):
    require(type(v) is list and len(v) == 3, 'explicit three-coordinate vector required')
    return list(map(finite, v))


def decode_word(w):
    require(type(w) is int and 0 <= w < 1 << 32, 'uint32 word required')
    exponent = (w >> 23) & 255
    mantissa = w & 0x7fffff
    require(exponent != 255 and not (exponent == 0 and mantissa),
            'normal-or-zero mode/geometry limb required')
    return F(struct.unpack('<f', struct.pack('<I', w))[0])


def decode_pair(words):
    require(type(words) is list and len(words) == 2, 'two explicit hi-lo limbs required')
    return sum(map(decode_word, words), F(0))


def encoded_reference(x):
    """Same HOST split formula as frozen split_double, no producer invocation."""
    finite(x)
    require(type(x) is float, 'original binary64 mode-X required')
    hi = struct.unpack('<f', struct.pack('<f', x))[0]
    difference = x - hi
    lo = struct.unpack('<f', struct.pack('<f', difference))[0]
    words = [struct.unpack('<I', struct.pack('<f', v))[0] for v in (hi, lo)]
    center = decode_pair(words)
    error = abs(F(x) - center)
    r = error * S
    radius = F((r.numerator + r.denominator - 1) // r.denominator, S)
    return {'uint32_hilo': words, 'center_BU': ratio(center),
            'original_BU': ratio(F(x)), 'encoding_error_BU': ratio(error),
            'outward_radius_BU': ratio(radius),
            'HOST_RN32_encodings': 2, 'HOST_RN64_subtractions': 1,
            'HOST_subtraction_defect_BU': ratio(abs(F(difference) - (F(x) - F(hi))))}


def load_retained():
    data = (ROOT / CLOSURE).read_bytes()
    require(hashlib.sha256(data).hexdigest() == CLOSURE_SHA, 'closure SHA mismatch')
    report = json.loads(data)
    require(report['test_run']['rc'] == report['independent_validation']['rc'] == 0,
            'retained closure status mismatch')
    pins = dict(report['code_doc_sha256'], **{CLOSURE: CLOSURE_SHA})
    for p, expected in pins.items():
        require(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == expected,
                'changed frozen input: ' + p)
    graw = (ROOT / GEOMETRY).read_bytes()
    require(hashlib.sha256(graw).hexdigest() == GEOMETRY_SHA, 'geometry SHA mismatch')
    g = json.loads(graw)
    run = g['test_run']
    raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
    require(hashlib.sha256(raw).hexdigest() == run['stdout_sha256'] and len(raw) == run['stdout_bytes'],
            'retained geometry raw mismatch')
    previous = zlib.decompress(base64.b64decode(report['test_run']['stdout_zlib_base64'], validate=True))
    require(hashlib.sha256(previous).hexdigest() == report['test_run']['stdout_sha256'],
            'closure raw mismatch')
    return pins, json.loads(raw)['cases'], json.loads(previous)['cases']


def check_case(g, *, reference_model, reference_frame):
    require(reference_model == MODEL and reference_frame == FRAME, 'explicit fixed-original CPU mode model required')
    snapshot = g['scene_snapshot']
    abi = g['word_ABI']
    ids = [src['id'] for src in snapshot['sources']]
    require(ids == abi['source_order'] == [p['source_id'] for p in g['sources']] and
            ids == [p['source_id'] for p in abi['sources']] and
            len(set(ids)) == len(ids) and ids, 'ordered complete source coverage required')
    require(snapshot['schema'] == 'exp005-readback-v2' and
            snapshot['undeclared_meshes'] == [] and set(snapshot['objects']) == {'M', 'D'},
            'bounded declared original axial scene required')
    require(abi['object_ids'] == ['M', 'D'] and abi['kinds'] == ['mirror', 'det'],
            'retained axial mirror-detector profile required')
    binding = digest({'snapshot': snapshot, 'object_order': abi['object_ids'], 'source_order': ids})
    require(binding == abi['original_scene_binding_sha256'] and digest(abi) == g['word_ABI_sha256'],
            'scene/word ABI binding mismatch')
    mode = snapshot['objects']['D']
    axis = vector(mode['mode_direction'])
    origin = vector(mode['mode_origin_BU'])
    require(axis in ([F(1), F(0), F(0)], [F(-1), F(0), F(0)]),
            'explicit unit-X terminal mode required; no oblique/zero/nonunit normalization')
    require(snapshot['objects']['M']['kind'] == 'mirror' and
            finite(snapshot['objects']['M']['phase_rad']) == 0 and mode['kind'] == 'det',
            'unchanged mirror-zero/detector role required')
    out = {'scene_binding_sha256': binding, 'geometry_case_sha256': digest(g),
           'reference_model': MODEL, 'reference_frame': FRAME, 'source_ids': ids,
           'terminal_mode_direction': [ratio(v) for v in axis],
           'terminal_mode_origin_BU': [ratio(v) for v in origin], 'paths': [],
           'HOST_reference_RN32_encodings': 0, 'HOST_reference_RN64_subtractions': 0,
           'accepted_terminal_reference_CPU_only': False, 'accepted_full_field_pipeline': False,
           'geometric_tree_complete_certified': False, 'coherence_authenticated': False,
           'native_reference_implemented': False}
    reference = None
    for row, src, encoded_src in zip(g['sources'], snapshot['sources'], abi['sources']):
        accepted = row['accepted_geometry_words_CPU_only']
        require(type(accepted) is bool and type(row['accepted_phase_budget_CPU_only']) is bool,
                'exact retained geometry/phase bool required')
        p = {'source_id': src['id'], 'previous_geometry_accepted': accepted,
             'previous_phase_accepted': row['accepted_phase_budget_CPU_only'],
             'reference_evaluated': False, 'accepted_terminal_reference_CPU_only': False}
        if not accepted:
            out['paths'].append(dict(p, reason='retained geometry rejection; no mode reference arithmetic'))
            continue
        sign = row['direction_sign']
        require(type(sign) is int and sign in (-1, 1) and row['mirror_owner'] == 0 and row['terminal_owner'] == 1,
                'derived mirror/terminal identity and signed unit ray required')
        direction = vector(src['direction'])
        decoded_direction = [decode_pair(w) for w in encoded_src['direction_uint32_hilo']]
        require(direction == decoded_direction == [F(sign), F(0), F(0)] and
                axis == [F(-sign), F(0), F(0)], 'exact forward-collinear reflected terminal mode required')
        require(row['phase_reference_id'] == 'original-source-zero:' + binding + ':' + src['id'],
                'original source-zero gauge required')
        if reference is None:
            reference = encoded_reference(mode['mode_origin_BU'][0])
            out.update(reference_ABI=reference, HOST_reference_RN32_encodings=2,
                       HOST_reference_RN64_subtractions=1)
        ref = rational(reference['center_BU'])
        rr = rational(reference['outward_radius_BU'])
        intervals = {}
        for owner in (0, 1):
            triangles = [t for t in abi['triangles'] if t['owner'] == owner]
            require(all(type(t['X_radius_scaled']) is int and t['X_radius_scaled'] >= 0
                        for t in triangles), 'nonnegative integer owner radii required')
            values = {(decode_pair(v[0]), F(t['X_radius_scaled'], S))
                      for t in triangles for v in t['vertices_uint32_hilo']}
            require(len(values) == 1, 'shared per-owner X variable required')
            center, radius = values.pop()
            require(radius >= 0, 'nonnegative owner radius required')
            intervals[owner] = (center-radius, center+radius)
        sc = decode_pair(encoded_src['origin_uint32_hilo'][0])
        require(type(encoded_src['X_radius_scaled']) is int and encoded_src['X_radius_scaled'] >= 0,
                'nonnegative integer source radius required')
        sr = F(encoded_src['X_radius_scaled'], S)
        require(sr >= 0, 'nonnegative source radius required')
        sl, sh = sc-sr, sc+sr
        ml, mh = intervals[0]; dl, dh = intervals[1]
        original_planes = []
        for key in ('M', 'D'):
            xs = {finite(v[0]) for v in snapshot['objects'][key]['vertices_world_BU']}
            require(len(xs) == 1, 'original axial plane required')
            original_planes.append(xs.pop())
        original_path = sign * (2*original_planes[0] - finite(src['position_BU'][0]) - original_planes[1])
        require(original_path == rational(row['original_length_BU_rational']), 'retained original geometric path mismatch')
        length = sorted((sign*(2*ml-sh-dh), sign*(2*mh-sl-dl)))
        require(length == list(map(rational, row['length_interval_BU_rational'])),
                'retained geometric length enclosure mismatch')
        correction = sorted((-sign*(ref-rr-dh), -sign*(ref+rr-dl)))
        # SAME D variable in L and correction: +sign*D cancels -sign*D.
        effective = sorted((sign*(2*ml-sh-(ref+rr)), sign*(2*mh-sl-(ref-rr))))
        independent_sum = [length[0]+correction[0], length[1]+correction[1]]
        original_correction = -sign*(origin[0]-original_planes[1])
        original_effective = original_path + original_correction
        require(effective[0] <= original_effective <= effective[1], 'original reference length outside enclosure')
        wc = decode_pair(abi['wavelength_uint32_hilo'])
        require(type(abi['wavelength_radius_scaled']) is int and abi['wavelength_radius_scaled'] >= 0,
                'nonnegative integer wavelength radius required')
        wr = F(abi['wavelength_radius_scaled'], S)
        require(wr >= 0 and wc-wr > 0, 'positive wavelength enclosure required')
        original_cycles = original_effective / finite(snapshot['lambda_BU'])
        corners = [x/w for x in effective for w in (wc-wr, wc+wr)]
        phase = 8 * max(abs(q-original_cycles) for q in corners)
        cap = rational(row['phase_budget_rad'])
        require(cap >= 0, 'unchanged nonnegative original phase cap required')
        p.update(reference_evaluated=True, port='D', source_phase_reference_id=row['phase_reference_id'],
                 terminal_reference_id='fixed-original-plane-mode:' + binding + ':D',
                 correlated_variable_cancelled='same terminal X variable D, not independent interval sum',
                 geometric_length_interval_BU=[ratio(v) for v in length],
                 reference_correction_interval_BU=[ratio(v) for v in correction],
                 independent_sum_NOT_used_BU=[ratio(v) for v in independent_sum],
                 effective_reference_length_interval_BU=[ratio(v) for v in effective],
                 original_reference_correction_BU=ratio(original_correction),
                 original_effective_reference_length_BU=ratio(original_effective),
                 original_effective_cycles=ratio(original_cycles),
                 mode_encoding_phase_charge_upper_rad=ratio(8*rr/(wc-wr)),
                 phase_error_upper_rad=ratio(phase), phase_budget_rad=ratio(cap),
                 enclosure_inputs={'M': [ratio(ml), ratio(mh)], 'D': [ratio(dl), ratio(dh)],
                                   'S': [ratio(sl), ratio(sh)], 'reference': [ratio(ref-rr), ratio(ref+rr)],
                                   'lambda': [ratio(wc-wr), ratio(wc+wr)]},
                 accepted_terminal_reference_CPU_only=row['accepted_phase_budget_CPU_only'] and phase <= cap)
        out['paths'].append(p)
    out['accepted_terminal_reference_CPU_only'] = all(p['accepted_terminal_reference_CPU_only'] for p in out['paths'])
    return out


def audit(*, reference_model, reference_frame):
    pins, cases, closure = load_retained()
    result = {name: check_case(c, reference_model=reference_model, reference_frame=reference_frame)
              for name, c in cases.items()}
    for name, c in result.items():
        c['retained_closure_gates_UNCHANGED'] = closure[name]['stage_gates_retained']
    return {'model': MODEL, 'reference_frame': FRAME, 'pins': pins, 'cases': result,
            'counts': {'cases': len(result), 'sources': sum(len(c['paths']) for c in result.values()),
                       'reference_evaluated_paths': sum(p['reference_evaluated'] for c in result.values() for p in c['paths']),
                       'accepted_reference_cases_CPU_only': sum(c['accepted_terminal_reference_CPU_only'] for c in result.values()),
                       'HOST_reference_RN32_encodings': sum(c['HOST_reference_RN32_encodings'] for c in result.values()),
                       'HOST_reference_RN64_subtractions': sum(c['HOST_reference_RN64_subtractions'] for c in result.values())},
            'geometry_word_operations_replayed': 0, 'retained_writers_executed': False,
            'GPU_executed': False, 'ALU_executed': False, 'Bpy_executed': False,
            'execution_authenticated': False, 'coherence_authenticated': False,
            'native_promotion_allowed': False, 'accepted_full_field_pipeline': False,
            'scope': 'new HOST mode encoding + exact CPU correlated reference enclosure; no native operation graph, field reinference, tree completeness or physical coherence',
            'pending': ['general complete history/terminal branch proof',
                        'native mode-reference ABI/operation graph with error and costs',
                        'feed effective reference length into downstream opt-in arithmetic before promotion',
                        'scene-bound execution authentication and equivalent-work full-cost protocol']}
