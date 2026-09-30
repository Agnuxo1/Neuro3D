"""Retained small CPU synthetic tie lists, not Bpy or native nearest evidence."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from primitive_tie_guard_v1 import resolve_candidates
from primitive_return_guard_v1 import classify_return

SNAPSHOT = 'a'*64  # Synthetic label, NOT hash of an evaluated Blender scene.
MANIFEST = [{'primitive_id': i, 'object_id': 'same_object'} for i in (7, 2, 9)]
PREVIOUS = {'snapshot_sha256': SNAPSHOT, 'primitive_id': 7, 'departure_event': 'mirror'}


def hit(pid, distance=2., normal=(1., 0., 0.)):
    return {'primitive_id': pid, 'distance_BU': distance, 'normal': list(normal)}


def audit():
    rows = []
    for order in itertools.permutations((hit(7), hit(2), hit(9, 3.))):
        # Tempting FIRST-min + single-candidate guard composition is unsafe.
        first = min(order, key=lambda x: x['distance_BU'])
        naive = classify_return(previous_primitive=7,
            candidate_primitive=first['primitive_id'], departure_event='mirror',
            distance_BU=first['distance_BU'])
        proposed = resolve_candidates(snapshot_sha256=SNAPSHOT, manifest=MANIFEST,
                                      candidates=order, previous=PREVIOUS)
        if proposed['action'] != 'abort': raise ValueError('tie policy accepted self candidate')
        rows.append({'candidate_order': list(order), 'naive_single_candidate': naive,
                     'proposed_tie_set': proposed})
    if sum(r['naive_single_candidate']['action'] == 'continue' for r in rows) != 3:
        raise ValueError('expected naive-composition ordering counterexample')
    return {'scope': 'CPU synthetic candidate arbitration ONLY; no geometry/Blender/GPU',
            'manifest': MANIFEST, 'synthetic_snapshot_label': SNAPSHOT,
            'previous': PREVIOUS, 'permutations': rows,
            'naive_continues': 3, 'proposed_aborts': 6,
            'limitations': ['Not a reproduction of native shader + previous-ID state',
                'Does not address missing/filtered hits, adjacent-face error or Bpy precision',
                'Manifest authenticity/exporter ABI and native integration pending']}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    result = audit()
    root = Path(__file__).parents[1]
    files = [Path(__file__), Path(__file__).with_name('test_exp005_primitive_tie.py'),
        root/'benchmarks/capacity_audit/primitive_tie_guard_v1.py',
        root/'benchmarks/capacity_audit/primitive_return_guard_v1.py',
        root/'benchmarks/capacity_audit/frontier_inputs.py',
        root/'benchmarks/capacity_audit/gpu_geometry_probe.py',
        root/'shaders/exp005_shared_frontier.glsl', root/'shaders/exp005_nearest_v2.glsl']
    result['code_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'naive_continues': 3, 'proposed_aborts': 6,
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
