"""CPU audit of the REAL hi-lo transport ABI, not shader or Blender execution.

Reconstructs triangle/source/optics inputs from actual pack_frontier+texture_data
and compares two complete-scene CPU traces. No hits are ever sent to GPU.
"""
import argparse
import cmath
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_inputs import pack_frontier
from exp005_blender_gpu import texture_data, split_double
from exp005_precision_fixture import direct, reflected
from exp005_triangle_oracle import trace_scene

FIELD_TOL = 1e-4
OFFSETS = (0., 1024.123456789, 65536.987654321, 999900.321987654)
SCALES = (1., 16.)
WAVELENGTHS = (.125, 1e-6)


def transform(snapshot, offset, scale, wavelength):
    result = copy.deepcopy(snapshot)
    shift = (offset, -.371234567*offset, .19314159*offset)
    def point(v): return [s+scale*x for s, x in zip(shift, v)]
    result['lambda_BU'] = scale*wavelength
    for obj in result['objects'].values():
        obj['vertices_world_BU'] = [point(v) for v in obj['vertices_world_BU']]
        if obj['kind'] in ('det', 'escape'): obj['mode_origin_BU'] = point(obj['mode_origin_BU'])
    for source in result['sources']: source['position_BU'] = point(source['position_BU'])
    return result


def transported(snapshot):
    batch = pack_frontier(snapshot)
    def recover(values):
        _, hi, lo = texture_data(values)
        return tuple(float(a)+float(b) for a, b in zip(hi[:len(values)], lo[:len(values)]))
    triangles, sources, optics = map(recover, (batch.geometry.triangles, batch.sources, batch.optics))
    result = copy.deepcopy(snapshot)
    for name in batch.geometry.object_ids:
        result['objects'][name].update(vertices_world_BU=[], faces=[])
    for start in range(0, len(triangles), 12):
        row = triangles[start:start+12]; index = int(row[3])
        if row[3] != index: raise ValueError('object identity changed during transport')
        obj = result['objects'][batch.geometry.object_ids[index]]
        k = len(obj['vertices_world_BU'])
        obj['vertices_world_BU'].extend([list(row[j:j+3]) for j in (0, 4, 8)])
        obj['faces'].append([k, k+1, k+2])
    for i, name in enumerate(batch.geometry.object_ids):
        row = optics[12*i:12*i+12]; obj = result['objects'][name]
        if obj['kind'] == 'bs': obj['power_transmittance'] = row[1]
        if obj['kind'] == 'mirror': obj['phase_rad'] = row[2]
        if obj['kind'] in ('det', 'escape'):
            obj['mode_origin_BU'] = list(row[4:7]); obj['mode_direction'] = list(row[8:11])
    for i, source in enumerate(result['sources']):
        row = sources[8*i:8*i+8]
        source.update(position_BU=list(row[:3]), direction=list(row[4:7]), field_reim=[row[3], row[7]])
    hi, lo = split_double(batch.wavelength_BU); result['lambda_BU'] = float(hi)+float(lo)
    error = max(abs(a-b) for before, after in ((batch.geometry.triangles, triangles),
        (batch.sources, sources), (batch.optics, optics)) for a, b in zip(before, after))
    return result, error


def audit():
    report = {'scope': 'CPU actual ABI roundtrip + two triangle oracles; NO GPU/Bpy runtime',
              'field_tolerance': FIELD_TOL, 'rows': [], 'transport_failures': [], 'trace_rejections': []}
    for kind, factory in (('direct', direct), ('reflected', reflected)):
        for gap in (1e-8, 2.):
            for offset in OFFSETS:
                for scale in SCALES:
                    for wavelength in WAVELENGTHS:
                        snapshot = transform(factory(gap), offset, scale, wavelength)
                        row = {'kind': kind, 'gap_BU': gap*scale, 'offset_BU': offset,
                               'scale': scale, 'lambda_BU': snapshot['lambda_BU']}
                        try:
                            recovered, input_error = transported(snapshot)
                            original = trace_scene(snapshot, max_rays=4)
                            decoded = trace_scene(recovered, max_rays=4)
                            field_error = abs(original['fields']['D']-decoded['fields']['D'])
                            geometric_length = (gap if kind == 'direct' else 1+gap)*scale
                            sign = 1 if kind == 'direct' else -1
                            analytic = sign*cmath.exp(2j*math.pi*geometric_length/snapshot['lambda_BU'])
                            row.update(input_error=input_error, transport_field_error=field_error,
                                original_field_reim=[original['fields']['D'].real, original['fields']['D'].imag],
                                transported_field_reim=[decoded['fields']['D'].real, decoded['fields']['D'].imag],
                                # Ideal unrounded placement is NOT the actual raw scene.
                                construction_vs_ideal_error=abs(original['fields']['D']-analytic),
                                transport_pass=field_error<=FIELD_TOL, original_casts=original['rays'],
                                transported_casts=decoded['rays'])
                            if field_error > FIELD_TOL: report['transport_failures'].append(copy.deepcopy(row))
                        except ValueError as exc:
                            row['trace_rejection'] = str(exc)
                            report['trace_rejections'].append(copy.deepcopy(row))
                        report['rows'].append(row)
    if len(report['rows']) != 64: raise ValueError('all bounded transport cases required')
    report['max_transport_field_error'] = max(r.get('transport_field_error', 0.) for r in report['rows'])
    report['max_input_error'] = max(r.get('input_error', 0.) for r in report['rows'])
    report['consequence'] = 'Do not promote full ABI domain; retain failures and preflight precision or local-frame contract.'
    return report


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    report = audit()
    dependencies = [Path(__file__), Path(__file__).with_name('exp005_precision_fixture.py'),
        Path(__file__).with_name('exp005_triangle_oracle.py'), Path(__file__).with_name('exp005_blender_gpu.py'),
        Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'frontier_inputs.py',
        Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'gpu_geometry_probe.py']
    report['code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
    a.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'cases': len(report['rows']), 'transport_failures': len(report['transport_failures']),
        'trace_rejections': len(report['trace_rejections']), 'max_field_error': report['max_transport_field_error'],
        'max_input_error': report['max_input_error'], 'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
