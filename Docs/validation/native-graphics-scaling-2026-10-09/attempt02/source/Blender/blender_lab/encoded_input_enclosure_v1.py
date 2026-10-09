"""Independent ideal encoder and interval-input scalar graph composition.

Raw CSV numbers mean their parsed binary64 values; measurement and parsing
preimages are not claimed. This adds an observed encoder arithmetic budget.
"""
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I, interval
from Blender.blender_lab.state_graph_enclosure_v1 import cmultiply, propagation, component


def encode_feature_row(values, low, high, source_ids):
    if len(values) != 4 or len(low) != 4 or len(high) != 4 or set(source_ids) != {'r0', 'r1', 'c0', 'c1', 'c2'} or len(source_ids) != 5:
        raise ValueError('Four parsed features and five unique coherent source IDs required')
    if any(F(b) <= F(a) for a, b in zip(low, high)):
        raise ValueError('Strictly positive training feature ranges required')
    scaled = [(I(F(v)) - I(F(a))) / (I(F(b)) - I(F(a))) for v, a, b in zip(values, low, high)]
    values_by_id = dict(zip(('r0', 'r1', 'c0', 'c1'), scaled), c2=I(1))
    norm = sum((value.square() for value in values_by_id.values()), I(0)).sqrt()
    return {sid: (values_by_id[sid] / norm, I(0)) for sid in source_ids}


def enclose_interval_inputs(graph, fields):
    if graph['status'] != 'COMPLETE' or graph['unresolved']:
        raise ValueError('Audited complete graph required')
    if set(fields) != {r['source_id'] for r in graph['roots']}:
        raise ValueError('Complete interval source fields required')
    incoming = [[] for _ in graph['nodes']]; outputs = {p: [] for p in graph['ports']}
    for root in graph['roots']:
        pair = fields[root['source_id']]
        incoming[root['node']].append((interval(pair[0]), interval(pair[1])))
    for node_id in graph['topological_order']:
        node = graph['nodes'][node_id]
        merged = tuple(sum((v[k] for v in incoming[node_id]), I(0)) for k in (0, 1))
        norm2 = sum((F(v) ** 2 for v in node['direction']), F(0))
        forwarded = cmultiply(merged, propagation(F(node['segment_parameter']), norm2, F(graph['wavelength'])))
        if 'terminal' in node:
            value = cmultiply(forwarded, propagation(F(node['reference_parameter']), norm2, F(graph['wavelength'])))
            outputs[node['terminal']].append(value)
        for edge in node['edges']:
            coefficient = component(F(edge['power']), edge['quarter_turns'], F(edge['phase_rad']))
            incoming[edge['target']].append(cmultiply(forwarded, coefficient))
    return {p: tuple(sum((v[k] for v in values), I(0)) for k in (0, 1)) for p, values in outputs.items()}
