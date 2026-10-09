"""Hybrid coherent tangents: geometric/optical local derivatives on native GPU."""
import hashlib,json
import math
import time
from Blender.blender_lab.scene_capture_v1 import need


def coherent_sum(values):
    return complex(math.fsum(v.real for v in values), math.fsum(v.imag for v in values))


def transport_parameter_tangent(graph, backend, inputs, origin_jets, *, distance_tolerance_BU):
    need(graph['status'] == 'COMPLETE' and not graph['unresolved'], 'Complete admitted graph required')
    ids = {r['source_id'] for r in graph['roots']}
    need(0 < len(inputs) <= 150 and all(set(row) == ids for row in inputs), 'Complete coherent input batch required')
    need(len(origin_jets) == len(graph['nodes']), 'Every state requires a geometric origin tangent')
    count, samples = len(graph['nodes']), len(inputs)
    incoming = [[[] for _ in inputs] for _ in range(count)]
    incoming_j = [[[] for _ in inputs] for _ in range(count)]
    outputs = [{p: [] for p in graph['ports']} for _ in inputs]
    outputs_j = [{p: [] for p in graph['ports']} for _ in inputs]
    degree = [0] * count
    for node in graph['nodes']:
        for edge in node['edges']:
            degree[edge['target']] += 1
    for root in graph['roots']:
        for j, row in enumerate(inputs):
            incoming[root['node']][j].append(complex(*row[root['source_id']]))
    ready = [i for i, d in enumerate(degree) if d == 0]
    done, batches = [], []
    start = time.perf_counter()
    while ready:
        frontier, ready = ready, []
        queries, fields, jacobians, origins_j, mapping = [], [], [], [], []
        for i in frontier:
            node = graph['nodes'][i]
            previous = node['previous_plane']
            for j in range(samples):
                queries.append({'origin': node['origin'], 'direction': node['direction'], 'previous_name': previous[0] if previous else None})
                fields.append(coherent_sum(incoming[i][j]))
                jacobians.append(coherent_sum(incoming_j[i][j]))
                origins_j.append(origin_jets[i])
                mapping.append((i, j))
        need(len(queries) <= 4096, 'Bounded native tangent frontier required')
        result = backend.query(queries, fields, jacobians, origins_j)
        need(len(result['rows']) == len(mapping), 'Complete field and derivative readback required')
        batches.append({'node_ids':frontier,'query_count':len(queries),'readback_sha256':hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),'all_candidate_and_input_echo_gates_enforced':True})
        for (i, j), row in zip(mapping, result['rows']):
            node = graph['nodes'][i]
            need(row['object'] == node['hit_object'] and row['primitive_id'] in node['coincident_primitives'], 'Every tangent draw must select the admitted surface')
            distance = float(node['segment_parameter']) * math.sqrt(sum(float(v)**2 for v in node['direction']))
            need(abs(row['distance_BU'] - distance) <= distance_tolerance_BU, 'Native tangent geometry tolerance required')
            need(row['native_input_bit_echo_verified'] and row['native_jacobian_bit_echo_verified'], 'Both exact binary64 input echoes required')
            if 'terminal' in node:
                outputs[j][node['terminal']].append(complex(*row['first_reim']))
                outputs_j[j][node['terminal']].append(complex(*row['first_jacobian_reim']))
            for edge in node['edges']:
                branch = 'second' if edge['event'] == 'r' else 'first'
                incoming[edge['target']][j].append(complex(*row[branch + '_reim']))
                incoming_j[edge['target']][j].append(complex(*row[branch + '_jacobian_reim']))
        for i in frontier:
            done.append(i)
            for edge in graph['nodes'][i]['edges']:
                degree[edge['target']] -= 1
                if degree[edge['target']] == 0:
                    ready.append(edge['target'])
    need(len(done) == count, 'Every admitted state must execute native field and tangent transport')
    fields = [{p: coherent_sum(a) for p, a in row.items()} for row in outputs]
    jac = [{p: coherent_sum(a) for p, a in row.items()} for row in outputs_j]
    return {'fields_reim': [{p: [z.real, z.imag] for p, z in row.items()} for row in fields],
            'field_parameter_derivative_reim': [{p: [z.real, z.imag] for p, z in row.items()} for row in jac],
            'powers': [{p: abs(z)**2 for p, z in row.items()} for row in fields],
            'power_parameter_derivative': [{p: 2*(fields[j][p].conjugate()*z).real for p, z in row.items()} for j, row in enumerate(jac)],
            'samples': samples, 'states': count, 'actual_geometric_queries_including_echo_draw': 2*count*samples,
            'batches': batches, 'seconds': time.perf_counter()-start,
            'scope': 'GPU derives ray-plane and optical phase tangents from captured planes plus CPU-derived exact affine origin/displacement tangents. CPU compensated field/tangent merges and power readout remain explicit. No precomputed transfer/Jacobian matrix enters the shader.'}
