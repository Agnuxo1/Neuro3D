"""Retrospective exact topology and phase bound for the archived Iris blueprint.

This checks already archived rational geometry, not Blender storage or GPU RT.
No producer, triangle-selector, mpmath or numerical auditor is imported.
The output bound depends explicitly on the archived algebraic certificate.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / 'Blender/benchmarks/capacity_audit/rational_interval_v1.py'
sys.path.insert(0, str(MATH.parent))
import rational_interval_v1 as ri
from rational_interval_v1 import Interval as I, upward_float

BLUEPRINT = ROOT / 'Docs/validation/iris-native-circuit-2026-10-08/geometry_bridge01'
CERTIFICATE = ROOT / 'Docs/validation/iris-retrospective-interval-2026-10-08/attempt06-native02'
CERTIFICATE_SHA = '7348c9a2e914575dedcf0547ffd95fc99b29ab901f660e5642115a4c48fa0046'
PI_BINARY64 = F(884279719003555, 281474976710656)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    raw = Path(path).read_bytes()
    need(len(raw) <= 16 * 2**20, 'bounded input JSON')
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def decode(value):
    if isinstance(value, dict):
        if set(value) == {'numerator', 'denominator'}:
            need(type(value['numerator']) is int and type(value['denominator']) is int,
                 'rational integer words')
            return F(value['numerator'], value['denominator'])
        return {k: decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [decode(v) for v in value]
    return value


def vec(v):
    need(len(v) == 3, 'three coordinates')
    return tuple(map(F, v))


def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def scale(a, s): return tuple(x * s for x in a)
def dot(a, b): return sum((x * y for x, y in zip(a, b)), F(0))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def exp_upper(x):
    """Positive Taylor tail; no floating exp. Only the saved positive gain."""
    x = F(x)
    need(0 <= x <= 32, 'bounded nonnegative saved log gain')
    total = term = F(1)
    for n in range(1, 129):
        term *= x / n
        total += term
    return total + (term * x / 129) / (1 - x / 130)


def ray_triangle(origin, direction, vertices):
    """Exact plane intersection plus oriented half-plane triangle membership."""
    a, b, c = vertices
    normal = cross(sub(b, a), sub(c, a))
    need(normal != (0, 0, 0), 'nondegenerate archived triangle')
    denominator = dot(normal, direction)
    if denominator == 0:
        if dot(normal, sub(origin, a)) != 0:
            return None
        # Clip the half-line to all three oriented half-planes. An infinite
        # coincident plane alone does not mean the finite triangle is reached.
        lower, upper = F(0), None
        for i in range(3):
            edge = sub(vertices[(i+1) % 3], vertices[i])
            intercept = dot(cross(edge, sub(origin, vertices[i])), normal)
            slope = dot(cross(edge, direction), normal)
            if slope == 0:
                if intercept < 0: return None
            elif slope > 0:
                lower = max(lower, -intercept/slope)
            else:
                bound = -intercept/slope
                upper = bound if upper is None else min(upper, bound)
            if upper is not None and lower > upper:
                return None
        raise ValueError('coplanar finite triangle encounter outside certificate domain')
        return None
    t = dot(normal, sub(a, origin)) / denominator
    if t < 0:
        return None
    point = add(origin, scale(direction, t))
    if any(dot(cross(sub(vertices[(i+1) % 3], vertices[i]),
                     sub(point, vertices[i])), normal) < 0 for i in range(3)):
        return None
    return t, point, normal


def inspect_case(case, state):
    scene, graph = decode(case['geometry']), decode(case['graph_proof'])
    theta = list(state['theta'])
    if case['case_id'] == 'phase':
        theta[0] += .1  # Match the archived binary64 intervention before F.
    theta = list(map(F, theta))
    wavelength = F(.1)
    need(scene['lambda_BU'] == wavelength and not scene['undeclared_meshes'], 'complete rational scene')
    X, Y = [F(0)], [F(0)]
    for index in range(1, 4):
        X.append(X[-1] + 4 + F(.0137)*index + F(.0031)*index*index)
        Y.append(Y[-1] + 4 + F(.0211)*index + F(.0017)*index*index)
    expected = {}
    local = [('bs1', (0, 0), (1, -1, 0), 'bs'),
             ('r1', (2, 0), (1, -1, 0), 'mirror'),
             ('r2', (2, F(1, 2)), (1, 1, 0), 'mirror'),
             ('f1', (1, F(1, 2)), (1, 1, 0), 'mirror'),
             ('m2', (0, 2), (1, -1, 0), 'mirror'),
             ('bs2', (1, 2), (1, -1, 0), 'bs')]
    lengths = []
    for i in range(4):
        for j in range(4):
            d = theta[4*i+j] * wavelength / (4 * PI_BINARY64)
            ox, oy = X[i] + j, Y[j] + 2*i
            for name, (lx, ly), normal, kind in local:
                expected[f'c{i}{j}.{name}'] = ((ox+lx+(d if name in ('r1', 'r2') else 0), oy+ly, F(0)), normal, kind)
            need(2+d > 0 and 1+d > 0, 'positive cardinal long-arm segments')
            lengths.append({'cell': 4*i+j, 'displacement_BU': str(d),
                            'long_arm_BU': str(5+2*d), 'short_arm_BU': '3'})
    for j in range(4):
        expected[f'R{j}'] = ((X[3]+j+2, Y[j]+8, F(0)), (1, 0, 0), 'det')
    for i in range(4):
        expected[f'C{i}'] = ((X[i]+4, Y[3]+2*i+3, F(0)), (0, 1, 0), 'det')
    need(set(scene['objects']) == set(expected), 'all 104 optical objects exactly declared')
    triangles, centers, normals = [], {}, {}
    for name, obj in scene['objects'].items():
        center, normal, kind = expected[name]
        tangent = (normal[1], -normal[0], 0)
        corners = [tuple(center[k] + F(1, 8)*(s*tangent[k]+(t if k == 2 else 0)) for k in range(3))
                   for s, t in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        need(list(map(vec, obj['vertices_world_BU'])) == corners and
             obj['faces'] == [[0, 1, 2], [0, 2, 3]] and obj['kind'] == kind,
             'exact archived planar quads and triangles')
        if kind == 'bs': need(obj['power_transmittance'] == F(1, 2), 'balanced splitter')
        if kind == 'mirror': need(obj['phase_rad'] == 0, 'fixed mirror phase convention')
        if kind == 'det': need(vec(obj['mode_origin_BU']) == center and vec(obj['mode_direction']) == normal, 'terminal reference')
        centers[name], normals[name] = center, vec(normal)
        for face in obj['faces']:
            triangles.append((name, len(triangles), tuple(corners[p] for p in face)))
    nodes = graph['nodes']
    need(len(nodes) == 136 and [n['id'] for n in nodes] == list(range(136)), 'complete unique node index')
    roots = graph['root_node_ids']
    need(len(roots) == 8 and len(set(roots)) == 8 and len(scene['sources']) == 8, 'all source roots')
    source_specs = [(f'r{j}', (F(j)-1, Y[j], F(0)), (1, 0, 0)) for j in range(4)]
    source_specs += [(f'c{i}', (X[i], F(2*i)-1, F(0)), (0, 1, 0)) for i in range(4)]
    for root, source, (name, origin, direction) in zip(roots, scene['sources'], source_specs):
        need(source['id'] == name and vec(source['position_BU']) == origin and vec(source['direction']) == direction and source['field_reim'] == [1, 0], 'canonical source semantics')
        need(vec(nodes[root]['origin']) == origin and vec(nodes[root]['direction']) == direction, 'bound source root')
    previous = [set() for _ in nodes]
    for node in nodes:
        for edge in node['edges']:
            need(type(edge['target']) is int and 0 <= edge['target'] < len(nodes), 'bounded target')
            previous[edge['target']].add(node['hit'])
    order = graph['topological_order']
    need(sorted(order) == list(range(136)), 'topological permutation')
    position = {n: i for i, n in enumerate(order)}
    reached = set(roots)
    state_keys = set()
    for index in order:
        need(index in reached, 'all optical states reachable, no orphan state')
        node = nodes[index]
        origin, direction = vec(node['origin']), vec(node['direction'])
        need(dot(direction, direction) == 1 and sum(v != 0 for v in direction) == 1, 'unit cardinal rays')
        need(previous[index] == set() if index in roots else len(previous[index]) == 1, 'one preceding optical plane per state')
        prev = next(iter(previous[index]), None)
        key = (origin, direction, prev)
        need(key not in state_keys, 'no duplicate quotient state')
        state_keys.add(key)
        hits = []
        for name, primitive, vertices in triangles:
            hit = ray_triangle(origin, direction, vertices)
            if hit is None: continue
            t, point, normal = hit
            if t == 0:
                need(name == prev and point == centers[name], 'only justified self departure excluded')
                continue
            hits.append((t, name, primitive, point, normal))
        need(hits, 'no lost path')
        nearest = min(h[0] for h in hits)
        tied = [h for h in hits if h[0] == nearest]
        name = tied[0][1]
        need(len(tied) == 2 and all(h[1] == name and h[3] == centers[name] for h in tied), 'only interior quad seam aliases')
        need(node['hit'] == name and node['segment'] == nearest and vec(node['point']) == centers[name] and
             node['coincident_primitives'] == [h[2] for h in tied], 'independent exact first-hit agreement')
        kind = scene['objects'][name]['kind']
        normal = normals[name]
        reflection = sub(direction, scale(normal, 2*dot(direction, normal)/dot(normal, normal)))
        if kind == 'det':
            need(node.get('terminal') == name and not node['edges'] and direction == normal, 'complete terminal mode')
            continue
        branches = [(reflection, F(1), 2)] if kind == 'mirror' else [(direction, F(1, 2), 0), (reflection, F(1, 2), 1)]
        need(len(branches) == len(node['edges']), 'no discarded branch')
        for edge, (outgoing, power, turn) in zip(node['edges'], branches):
            target = edge['target']
            need(position[index] < position[target], 'acyclic complete propagation')
            need(vec(nodes[target]['origin']) == centers[name] and vec(nodes[target]['direction']) == outgoing and
                 edge['coefficient_power'] == power and edge['quarter_turns'] == turn, 'exact optical edge semantics')
            cell, part = name.split('.')
            i, j = int(cell[1]), int(cell[2])
            if part == 'bs1': next_hit = cell+('.r1' if outgoing == (1, 0, 0) else '.m2')
            elif part == 'r1': next_hit = cell+'.r2'
            elif part in ('r2',): next_hit = cell+'.f1'
            elif part in ('f1', 'm2'): next_hit = cell+'.bs2'
            elif outgoing == (1, 0, 0): next_hit = f'c{i+1}{j}.bs1' if i < 3 else f'R{j}'
            else: next_hit = f'c{i}{j+1}.bs1' if j < 3 else f'C{i}'
            need(nodes[target]['hit'] == next_hit, 'canonical arm/link network topology')
            reached.add(target)
    need({n['hit'] for n in nodes} == set(expected), 'every optical object used')
    return theta, lengths


def interval_from_wire(value):
    return I(F(*value['lo']), F(*value['hi']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    need(output.is_relative_to(ROOT), 'output inside own checkout')
    output.mkdir(parents=True, exist_ok=False)
    (output/'source').mkdir()
    shutil.copyfile(__file__, output/'source/checker.py')
    shutil.copyfile(MATH, output/'source/rational_interval_v1.py')
    ri.BITS, ri.GRID = 256, 1 << 256
    ri.pi_interval.cache_clear()
    need(F(math.pi) == PI_BINARY64, 'explicit binary64 pi identity')
    geometry_path, certificate_path = BLUEPRINT/'receipt.json', CERTIFICATE/'certificate.json'
    need(sha(certificate_path) == CERTIFICATE_SHA, 'pinned previously verified algebraic certificate')
    geometry, certificate = load(geometry_path), load(certificate_path)
    for relative, digest in geometry['source_sha256'].items():
        need(sha(BLUEPRINT/'source'/relative) == digest, 'archived geometry source preimage')
    for relative, digest in certificate['certificate_source_hashes'].items():
        basename = 'certificate.py' if Path(relative.replace('\\', '/')).name == 'certify_archived_iris_outputs_v1.py' else 'rational_interval_v1.py'
        need(sha(CERTIFICATE/'source'/basename) == digest, 'archived algebraic checker preimage')
    need(geometry['status'] == 'PASS' and [c['case_id'] for c in geometry['cases']] == ['baseline', 'phase'], 'complete historical blueprint cases')
    need(certificate['status'] == 'CERTIFIED_WITHIN_HISTORICAL_UTILITY' and certificate['certified_decisions'] == 450 and
         not certificate['new_native_execution'], 'previous complete retrospective audit')
    state = load(BLUEPRINT/'source/Blender/demo_lattice_iris/trained_lattice.json')
    # The same state was source-bound to all raw packets by the pinned prior certificate.
    native_state = ROOT/'Docs/validation/iris-native-circuit-2026-10-08/native02/source/Blender/demo_lattice_iris/trained_lattice.json'
    need(sha(native_state) == geometry['source_sha256']['Blender/demo_lattice_iris/trained_lattice.json'], 'same archived native/geometry parameters')
    ratio = ri.pi_interval()/PI_BINARY64 - 1
    phase_factor_error = ratio.max_abs()
    gain = exp_upper(F(state['logt']))
    results = []
    for case in geometry['cases']:
        theta, lengths = inspect_case(case, state)
        # Unit-norm input; telescope sixteen embedded unitary MZI gates.
        operator_error = phase_factor_error * sum(map(abs, theta), F(0))
        field_bridge = I(2).sqrt().hi * operator_error
        power_bridge = 2*operator_error + operator_error**2
        logit_bridge = gain * power_bridge
        associated = [c for c in certificate['cases'] if c['case_id'] == case['case_id'] or
                      (case['case_id'] == 'baseline' and c['case_id'] == 'sham')]
        bounded = []
        for original in associated:
            row_evidence = []
            for row in original['rows']:
                logits = [interval_from_wire(v) for v in row['logits_reference']]
                prediction = row['native_prediction']
                margin = logits[prediction].lo - max(logits[c].hi for c in range(3) if c != prediction)
                residual = margin - 2*logit_bridge
                row_evidence.append({'row': row['row'], 'prediction': prediction,
                                     'algebraic_logit_margin_lower': str(margin),
                                     'planned_geometry_logit_margin_lower': str(residual),
                                     'planned_geometry_decision_certified': residual > 0})
            bounds = original['maximum_upper_rational']
            bounded.append({'case_id': original['case_id'], 'certified_decisions': sum(r['planned_geometry_decision_certified'] for r in row_evidence),
                            'field_l1_error_upper': str(F(bounds['field_l1'])+field_bridge),
                            'power_error_upper': str(F(bounds['power'])+power_bridge),
                            'logit_error_upper': str(F(bounds['logit'])+logit_bridge),
                            'rows': row_evidence})
        results.append({'geometry_case_id': case['case_id'], 'independent_first_hit_queries': 136,
                        'all_triangles': 208, 'all_objects': 104, 'local_arm_lengths': lengths,
                        'operator_error_upper': str(operator_error), 'field_l1_bridge_upper': str(field_bridge),
                        'power_bridge_upper': str(power_bridge), 'logit_bridge_upper': str(logit_bridge),
                        'archived_native_cases': bounded})
    flattened = [c for result in results for c in result['archived_native_cases']]
    decisions = sum(c['certified_decisions'] for c in flattened)
    maxima = {name: max(F(c[name+'_error_upper']) for c in flattened) for name in ['field_l1', 'power', 'logit']}
    useful = decisions == 450 and maxima['field_l1'] <= F(1, 10**11) and maxima['power'] <= F(1, 10**11) and maxima['logit'] <= F(1, 10**9)
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in [geometry_path, certificate_path, native_state]}
    result = {'schema': 'neuro3d.planned_rational_geometry.retrospective_linkage.v1',
              'status': 'CERTIFIED_PLANNED_BLUEPRINT_WITHIN_HISTORICAL_UTILITY' if useful else 'LINKAGE_NOT_USEFUL',
              'scope': 'archived rational planned geometry, ideal scalar optics and existing native algebraic outputs',
              'new_GPU_execution': False, 'actual_Blender_capture_certified': False,
              'native_triangle_traversal_certified': False, 'physical_model_certified': False,
              'novelty_demonstrated': False, 'H1_confirmatory': False,
              'dependent_algebraic_certificate_sha256': CERTIFICATE_SHA,
              'pi_binary64': str(PI_BINARY64), 'pi_ratio_error_upper': str(phase_factor_error),
              'source_sha256': {Path(__file__).relative_to(ROOT).as_posix(): sha(__file__), MATH.relative_to(ROOT).as_posix(): sha(MATH)},
              'inputs_sha256': inputs, 'certified_decisions': decisions,
              'maximum_upper_rational': {k: str(v) for k, v in maxima.items()},
              'maximum_upper_display': {k: upward_float(v) for k, v in maxima.items()}, 'cases': results}
    need(all(sha(ROOT/p) == digest for p, digest in inputs.items()), 'input bytes unchanged')
    (output/'receipt.json').write_bytes((json.dumps(result, indent=2, allow_nan=False)+'\n').encode())
    print(json.dumps({k: result[k] for k in ['status', 'certified_decisions', 'maximum_upper_display']}))
    return 0 if useful else 2


if __name__ == '__main__':
    sys.exit(main())
