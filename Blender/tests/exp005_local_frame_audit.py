"""Bounded CPU local-frame experiment; separate transport from frame drift."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from local_frame_v1 import local_frame
from exp005_precision_transport_audit import transform, transported, OFFSETS, SCALES, WAVELENGTHS, FIELD_TOL
from exp005_precision_fixture import direct, reflected
from exp005_triangle_oracle import trace_scene


def audit():
    report = {'scope': 'CPU prototype and triangle-oracle comparison; NO GPU/Bpy runtime',
              'rows': [], 'local_transport_failures': [], 'world_vs_local_failures': [], 'rejections': []}
    for kind, factory in (('direct', direct), ('reflected', reflected)):
        for gap in (1e-8, 2.):
            for offset in OFFSETS:
                for scale in SCALES:
                    for wavelength in WAVELENGTHS:
                        world = transform(factory(gap), offset, scale, wavelength)
                        row = {'kind': kind, 'gap_BU': gap*scale, 'offset_BU': offset,
                               'scale': scale, 'lambda_BU': world['lambda_BU']}
                        try:
                            local, metadata = local_frame(world)
                            decoded, input_error = transported(local)
                            w, l, d = (trace_scene(scene, max_rays=4) for scene in (world, local, decoded))
                            row.update(frame=metadata, local_input_error=input_error,
                                local_transport_field_error=abs(l['fields']['D']-d['fields']['D']),
                                world_vs_local_field_error=abs(w['fields']['D']-l['fields']['D']),
                                final_vs_world_field_error=abs(w['fields']['D']-d['fields']['D']))
                            if row['local_transport_field_error'] > FIELD_TOL:
                                report['local_transport_failures'].append(row)
                            if row['world_vs_local_field_error'] > FIELD_TOL:
                                report['world_vs_local_failures'].append(row)
                        except ValueError as exc:
                            row['rejection'] = str(exc); report['rejections'].append(row)
                        report['rows'].append(row)
    if len(report['rows']) != 64: raise ValueError('all bounded cases required')
    report['max_local_transport_error'] = max(r.get('local_transport_field_error', 0.) for r in report['rows'])
    report['max_frame_drift'] = max(r.get('world_vs_local_field_error', 0.) for r in report['rows'])
    report['consequence'] = 'Prototype only; do not hide frame drift or promote general phase accuracy.'
    return report


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    r = audit()
    from local_frame_v1 import __file__ as prototype
    r['prototype_sha256'] = hashlib.sha256(Path(prototype).read_bytes()).hexdigest()
    r['auditor_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'cases': len(r['rows']), 'local_transport_failures': len(r['local_transport_failures']),
        'frame_drift_failures': len(r['world_vs_local_failures']), 'rejections': len(r['rejections']),
        'max_local_transport_error': r['max_local_transport_error'], 'max_frame_drift': r['max_frame_drift'],
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
