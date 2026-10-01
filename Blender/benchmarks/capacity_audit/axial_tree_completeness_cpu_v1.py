"""Opt-in exhaustive axial event-tree certificate, exact CPU geometry only.

Reads pinned evidence; never calls previous producers or native writers.
Proof covers original geometry and the declared shared-X enclosure family,
not general scenes, field phase/coherence, authentication, or native runtime.
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
MODEL = 'axial-shared-X-finite-event-tree-certificate-CPU-v1'
WORDS_MODEL = 'scene-hilo32-axial-geometry-signed512-CPU-v1'
PREVIOUS = 'coordinacion/respuestas/AXIAL-TERMINAL-REFERENCE-001-CODEX.json'
PREVIOUS_SHA = '806867ae71c97bf352ea2e7552d183e549cfb8f6eb6a14df2aa3e12cb868016b'
GEOMETRY = 'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
CLOSURE = 'coordinacion/respuestas/AXIAL-SCENE-CLOSURE-001-CODEX.json'
S = 1 << 149


def require(c, reason):
    if not c:
        raise ValueError(reason)


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def pair(v):
    v = F(v)
    return [v.numerator, v.denominator]


def rational(v):
    require(type(v) is list and len(v) == 2 and all(type(n) is int for n in v)
            and v[1] > 0, 'exact rational required')
    return F(*v)


def finite(v):
    require(type(v) in (float, int) and math.isfinite(v) and abs(v) <= 10**6,
            'bounded finite original number required')
    return F(v)


def decode(v):
    require(type(v) is list and len(v) == 2, 'two hi-lo words required')
    out = F(0)
    for w in v:
        require(type(w) is int and 0 <= w < 1 << 32, 'uint32 word required')
        e, m = (w >> 23) & 255, w & 0x7fffff
        require(e != 255 and not (e == 0 and m), 'normal-or-zero limb required')
        out += F(struct.unpack('<f', struct.pack('<I', w))[0])
    return out


def radius(v):
    require(type(v) is int and 0 <= v < 1 << 511, 'nonnegative signed512 radius required')
    return F(v, S)


def vector(v):
    require(type(v) is list and len(v) == 3, 'three coordinates required')
    return list(map(finite, v))


def words_vector(v):
    require(type(v) is list and len(v) == 3, 'three word-pairs required')
    return list(map(decode, v))


def _scene(g):
    a, s = g['word_ABI'], g['scene_snapshot']
    ids = [p['id'] for p in s['sources']]
    require(s['schema'] == 'exp005-readback-v2' and s['undeclared_meshes'] == []
            and set(s['objects']) == {'M', 'D'}, 'bounded declared M/D scene required')
    require(1 <= len(ids) <= 3 and all(type(i) is str and 0 < len(i) <= 128 for i in ids)
            and len(set(ids)) == len(ids), 'unique bounded source IDs required')
    require(ids == a['source_order'] == [p['source_id'] for p in a['sources']]
            == [p['source_id'] for p in g['sources']], 'ordered full source coverage required')
    require(a['model'] == g['geometry_model'] == WORDS_MODEL
            and a['object_ids'] == ['M', 'D'] and a['kinds'] == ['mirror', 'det'],
            'restricted axial profile, not BS/escape/general history')
    require(s['objects']['M']['kind'] == 'mirror'
            and finite(s['objects']['M']['phase_rad']) == 0
            and s['objects']['D']['kind'] == 'det', 'mirror/detector roles unchanged')
    binding = digest({'snapshot': s, 'object_order': a['object_ids'], 'source_order': ids})
    require(binding == a['original_scene_binding_sha256'] and digest(a) == g['word_ABI_sha256'],
            'snapshot/order/ABI binding mismatch')
    extra = rational(a['extra_radius_HOST_BU_rational'])
    require(extra >= 0, 'nonnegative explicitly declared extra radius')
    eq = extra*S
    extra_scaled = (eq.numerator + eq.denominator-1)//eq.denominator
    require(rational(a['extra_radius_HOST_outward_inflation_BU_rational'])
            == F(extra_scaled, S)-extra, 'outward extra radius mismatch')
    require(len(a['triangles']) == 4, 'exact four primitive coverage required')
    triangles, planes = [], {}
    for owner, key in enumerate(('M', 'D')):
        obj = s['objects'][key]
        require(obj['faces'] == [[0, 1, 2], [0, 2, 3]]
                and len(obj['vertices_world_BU']) == 4, 'frozen quad topology/order required')
        original = list(map(vector, obj['vertices_world_BU']))
        require(len({p[0] for p in original}) == 1, 'one original X plane per owner')
        for face_index, face in enumerate(obj['faces']):
            pid = owner*2+face_index
            t = a['triangles'][pid]
            require(type(t['owner']) is int and t['owner'] == owner, 'primitive owner/order required')
            require(len(t['vertices_uint32_hilo']) == 3, 'three triangle vertices required')
            verts = list(map(words_vector, t['vertices_uint32_hilo']))
            require(len({p[0] for p in verts}) == 1, 'one decoded X plane required')
            r = radius(t['X_radius_scaled'])
            c = verts[0][0]
            error = F(0)
            for v, index in zip(verts, face):
                orig = original[index]
                require(v[1:] == orig[1:], 'unchanged exact YZ geometry required')
                error = max(error, abs(v[0]-orig[0]))
            q = error*S
            require(t['X_radius_scaled'] == (q.numerator+q.denominator-1)//q.denominator+extra_scaled,
                    'original X encoding enclosure/radius mismatch')
            if owner in planes:
                require(planes[owner] == (c-r, c+r), 'SAME shared X variable per owner')
            planes[owner] = (c-r, c+r)
            triangles.append((owner, verts))
    sources = []
    for orig, enc in zip(s['sources'], a['sources']):
        v = words_vector(enc['origin_uint32_hilo'])
        ov, od = vector(orig['position_BU']), vector(orig['direction'])
        d = words_vector(enc['direction_uint32_hilo'])
        require(d == od and d in ([F(1), F(0), F(0)], [F(-1), F(0), F(0)]),
                'original/decoded signed unit-X source required')
        require(v[1:] == ov[1:], 'unchanged source YZ required')
        r = radius(enc['X_radius_scaled'])
        q = abs(ov[0]-v[0])*S
        require(enc['X_radius_scaled'] == (q.numerator+q.denominator-1)//q.denominator+extra_scaled,
                'original source X enclosure mismatch')
        sources.append((v, (v[0]-r, v[0]+r), int(d[0])))
    return binding, ids, triangles, planes, sources


def _bary(verts, yz):
    a, b, c = [p[1:] for p in verts]
    cross = lambda p, q: p[0]*q[1]-p[1]*q[0]
    sub = lambda p, q: (p[0]-q[0], p[1]-q[1])
    det = cross(sub(b, a), sub(c, a))
    require(det != 0, 'nondegenerate YZ triangle')
    u = cross(sub(yz, a), sub(c, a))/det
    v = cross(sub(b, a), sub(yz, a))/det
    w = 1-u-v
    require(min(u, v, w) != 0 or min(u, v, w) < 0, 'boundary excluded; no snap')
    return (w, u, v)


def _transition(triangles, planes, yz, origin, sign, departure, chosen):
    require(type(chosen) is int and 0 <= chosen < len(triangles), 'chosen primitive required')
    proof, positive = [], {}
    for pid, (owner, verts) in enumerate(triangles):
        bary = _bary(verts, yz)
        p = {'primitive_id': pid, 'owner': owner, 'barycentric': list(map(pair, bary))}
        if min(bary) < 0:
            p['relation'] = 'projected_miss'
        elif owner == departure:
            # SAME variable X_origin = X_owner, not independent intervals.
            p.update(relation='same_owner_departure', distance_BU=[[0, 1], [0, 1]])
        else:
            lo, hi = planes[owner]
            interval = sorted((sign*(lo-origin[1]), sign*(hi-origin[0])))
            p['distance_BU'] = list(map(pair, interval))
            if interval[1] < 0:
                p['relation'] = 'behind'
            else:
                require(interval[0] > 0, 'zero/contact uncertain root rejected')
                p['relation'] = 'chosen' if pid == chosen else 'strictly_later'
                positive[pid] = interval
        proof.append(p)
    require(chosen in positive, 'chosen must be strict interior positive, not departure/miss/behind')
    chosen_owner = triangles[chosen][0]
    for p in proof:
        if p['relation'] != 'strictly_later':
            continue
        owner = p['owner']
        # Common origin cancels. Do NOT subtract independent t intervals.
        gap = (planes[owner][0]-planes[chosen_owner][1] if sign > 0
               else planes[chosen_owner][0]-planes[owner][1])
        require(gap > 0, 'all competitor planes strictly beyond chosen required')
        p['shared_origin_clearance_BU'] = pair(gap)
    return proof


def _nodes(g, i, triangles, planes, sources):
    row = g['sources'][i]
    require(type(row['accepted_geometry_words_CPU_only']) is bool
            and row['accepted_geometry_words_CPU_only'], 'retained geometry rejection cannot be revived')
    require(type(row['accepted_phase_budget_CPU_only']) is bool, 'retained phase bool required')
    require(len(row['segments']) == 2, 'both retained transitions required')
    position, source_range, sign = sources[i]
    require(row['direction_sign'] == sign and type(row['direction_sign']) is int
            and type(row['mirror_owner']) is int and type(row['terminal_owner']) is int
            and row['mirror_owner'] == 0 and row['terminal_owner'] == 1, 'retained reflection/context required')
    def primitive_ids(v):
        require(type(v) is list and all(type(x) is int and 0 <= x < 4 for x in v)
                and v == sorted(set(v)), 'strict ordered unique primitive IDs required')
    primitive_ids(row['projected_misses'])
    sid = row['source_id']
    nodes = [
        {'id': sid+':root', 'source_id': sid, 'parent': None, 'event': 'source',
         'arrival_primitive_id': None, 'origin_context': 'original-source-X-enclosure',
         'direction_sign': sign, 'children': [sid+':mirror']},
        {'id': sid+':mirror', 'source_id': sid, 'parent': sid+':root', 'event': 'reflect',
         'arrival_primitive_id': row['segments'][0]['primitive_id'],
         'origin_context': 'SAME-owner-0-X-variable', 'direction_sign': -sign,
         'children': [sid+':det']},
        {'id': sid+':det', 'source_id': sid, 'parent': sid+':mirror', 'event': 'detect',
         'arrival_primitive_id': row['segments'][1]['primitive_id'],
         'origin_context': 'absorbing-owner-1-X-variable', 'direction_sign': None, 'children': []}
    ]
    for j in (0, 1):
        segment = row['segments'][j]
        primitive_ids(segment['behind'])
        primitive_ids(segment['same_owner_departures_skipped'])
        bounds = segment['segment_interval_scaled']
        require(type(bounds) is list and len(bounds) == 2 and all(type(x) is int for x in bounds),
                'strict integer retained root endpoints required')
        require(segment['competitor_clearance_scaled'] is None
                or type(segment['competitor_clearance_scaled']) is int, 'strict clearance integer required')
        require(type(segment['owner']) is int and segment['owner'] == j,
                'mirror then absorbing detector; no pruning/depth cap')
        selected = segment['primitive_id']
        proof = _transition(triangles, planes, position[1:], source_range if j == 0 else planes[0],
                            sign if j == 0 else -sign, None if j == 0 else 0, selected)
        require(triangles[selected][0] == j, 'event owner/primitive mismatch')
        misses = [p['primitive_id'] for p in proof if p['relation'] == 'projected_miss']
        behind = [p['primitive_id'] for p in proof if p['relation'] == 'behind']
        skipped = [p['primitive_id'] for p in proof if p['relation'] == 'same_owner_departure']
        gaps = [rational(p['shared_origin_clearance_BU']) for p in proof if p['relation'] == 'strictly_later']
        clearance = min(gaps)*S if gaps else None
        interval = proof[selected]['distance_BU']
        require(misses == row['projected_misses'] and behind == segment['behind']
                and skipped == segment['same_owner_departures_skipped'],
                'retained full primitive partition/context mismatch')
        require([rational(x)*S for x in interval] == segment['segment_interval_scaled']
                and clearance == segment['competitor_clearance_scaled'],
                'retained root/competitor certificate mismatch')
        nodes[j]['next_primitive_partition'] = proof
    return nodes


def make_witness(g, *, model):
    require(model == MODEL, 'explicit CPU completeness model required')
    binding, ids, ts, planes, sources = _scene(g)
    require(all(type(p['accepted_geometry_words_CPU_only']) is bool for p in g['sources']),
            'retained geometry booleans required')
    require(all(p['accepted_geometry_words_CPU_only'] for p in g['sources']),
            'no complete witness for retained rejected geometry')
    require(g['accepted_geometry_words_CPU_only'] is True, 'retained aggregate rejection cannot be revived')
    return {'model': MODEL, 'scene_binding_sha256': binding, 'word_ABI_sha256': g['word_ABI_sha256'],
            'geometry_case_sha256': digest(g), 'source_order': ids, 'object_order': ['M', 'D'],
            'primitive_count': 4,
            'trees': [_nodes(g, i, ts, planes, sources) for i in range(len(ids))]}


def verify_witness(g, witness, *, model):
    # Revalidate every primitive mathematically, not solely SHA/record counts.
    expected = make_witness(g, model=model)
    require(digest(witness) == digest(expected), 'missing/extra/foreign/reordered event or primitive evidence')
    return {'model': MODEL, 'scene_binding_sha256': expected['scene_binding_sha256'],
            'source_order': expected['source_order'], 'certificate_sha256': digest(witness),
            'certificate': witness, 'geometric_tree_complete_restricted_CPU_only': True,
            'retained_phase_gates_UNCHANGED': [p['accepted_phase_budget_CPU_only'] for p in g['sources']],
            'record_count': 3*len(expected['trees']), 'transition_count': 2*len(expected['trees']),
            'primitive_checks': 8*len(expected['trees']),
            'fields_computed': False, 'native_promotion_allowed': False,
            'execution_authenticated': False, 'physical_coherence_verified': False,
            'accepted_full_field_pipeline': False,
            'scope': 'finite absorbing source-mirror-det tree for original and shared-X enclosure family; exact YZ; no BS/general tree/native arithmetic proof'}


def read_payload(p):
    r = json.loads((ROOT/p).read_bytes())
    run = r['test_run']
    raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
    require(hashlib.sha256(raw).hexdigest() == run['stdout_sha256']
            and len(raw) == run['stdout_bytes'], 'retained payload digest/size mismatch')
    return json.loads(raw)


def load_retained():
    data = (ROOT/PREVIOUS).read_bytes()
    require(hashlib.sha256(data).hexdigest() == PREVIOUS_SHA, 'previous reference report SHA')
    r = json.loads(data)
    require(r['test_run']['rc'] == r['independent_validation']['rc'] == 0, 'previous verification status')
    pins = dict(r['code_doc_sha256'], **{PREVIOUS: PREVIOUS_SHA})
    for p, h in pins.items():
        require(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, 'changed frozen input '+p)
    return pins, read_payload(GEOMETRY)['cases'], read_payload(CLOSURE)['cases']


def audit(*, model):
    require(model == MODEL, 'explicit CPU completeness model required')
    pins, cases, closure = load_retained()
    out = {}
    for name, g in cases.items():
        _scene(g)
        accepted = all(p['accepted_geometry_words_CPU_only'] is True for p in g['sources'])
        require(type(g['accepted_geometry_words_CPU_only']) is bool
                and g['accepted_geometry_words_CPU_only'] == accepted, 'retained aggregate mismatch')
        if accepted:
            # Build new witness once; validation is an explicitly separate CPU cost.
            out[name] = verify_witness(g, make_witness(g, model=model), model=model)
        else:
            out[name] = {'geometric_tree_complete_restricted_CPU_only': False,
                         'reason': 'retained geometry rejection, no certificate construction',
                         'source_order': g['word_ABI']['source_order'],
                         'accepted_full_field_pipeline': False, 'record_count': 0,
                         'transition_count': 0, 'primitive_checks': 0}
        out[name]['retained_closure_gates_UNCHANGED'] = closure[name]['stage_gates_retained']
    return {'model': MODEL, 'pins': pins, 'cases': out,
            'counts': {'cases': len(out), 'source_ids': sum(len(c['source_order']) for c in out.values()),
                       'certified_cases': sum(c['geometric_tree_complete_restricted_CPU_only'] for c in out.values()),
                       'records': sum(c['record_count'] for c in out.values()),
                       'transitions': sum(c['transition_count'] for c in out.values()),
                       'primitive_checks_per_verification': sum(c['primitive_checks'] for c in out.values())},
            'geometry_signed512_graph_replayed': False, 'retained_writers_executed': False,
            'GPU_executed': False, 'Bpy_executed': False, 'RT_executed': False,
            'execution_authenticated': False, 'physical_coherence_verified': False,
            'accepted_full_field_pipeline': False, 'native_promotion_allowed': False,
            'cost_scope': 'new witness construction and re-verification rational CPU; not zero-work hash gate; no runtime performance comparison',
            'pending': ['feed correlated terminal reference into downstream graph',
                        'native effective geometry/reference operations with scene-bound guard authentication',
                        'general event trees/BS/mode overlap/coherence and equivalent-work full costs']}
