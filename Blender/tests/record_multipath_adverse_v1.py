"""Preserve adverse outcomes through the real JSON CLI, not only unit assertions."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from test_robust_multipath_v1 import scene, plane_x
from trace_exact_scene_v1 import encode


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): raise ValueError('fresh evidence directory required')
    args.out.mkdir(parents=True)
    quad = plane_x(1, 'bs', power_transmittance=1)
    quad.update(vertices_world_BU=[(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)], faces=[(0,1,2),(0,2,3)])
    cases = {
        'tiny_gap': (scene({'bs': plane_x(1, 'bs', power_transmittance=1), 'out': plane_x(1+F(1,2**44))}), 'COMPLETE'),
        'interior_seam': (scene({'quad': quad, 'out': plane_x(2)}), 'COMPLETE'),
        'contact': (scene({'touch': plane_x(0, 'mirror'), 'out': plane_x(2)}), 'CONTACT'),
        'tie': (scene({'a': plane_x(1, 'mirror'), 'b': plane_x(1, 'mirror'), 'out': plane_x(2)}), 'TRUE_TIE'),
        'boundary': (scene({'out': plane_x(1)}, origin=(0,0,-4)), 'BOUNDARY'),
        'return_loop': (scene({'left': plane_x(0, 'mirror'), 'right': plane_x(1, 'mirror'), 'out': plane_x(2)}, origin=(.5,0,0)), 'RESOURCE_LIMIT'),
        'lost': (scene({'out': plane_x(1)}, direction=(-1,0,0)), 'MISS'),
        'mode': (scene({'out': plane_x(1, axis=(1,1,0))}), 'MODE_MISMATCH'),
    }
    receipt = {'scope': 'CPU exact full-path public CLI, adverse outcomes retained', 'cases': [], 'status': 'PASS'}
    for name, (snapshot, expected) in cases.items():
        source, output = args.out/(name+'.scene.json'), args.out/(name+'.trace.json')
        source.write_text(json.dumps(encode(snapshot), indent=2, allow_nan=False)+'\n', encoding='utf-8')
        process = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(ROOT/'Blender/benchmarks/capacity_audit/trace_exact_scene_v1.py'),
                                  '--scene', str(source), '--out', str(output), '--max-depth', '8'], capture_output=True, timeout=20)
        value = json.loads(output.read_bytes()) if output.exists() else {}
        passed = (process.returncode == 0 and value.get('status') == expected) if expected == 'COMPLETE' else (
            process.returncode == 2 and value.get('status') == 'INCOMPLETE' and value.get('fields') is None and
            any(row['status'] == expected for row in value.get('unresolved', [])))
        if not passed: receipt['status'] = 'FAIL'
        receipt['cases'].append({'name': name, 'expected': expected, 'exit_code': process.returncode, 'pass': passed,
                                 'stdout': process.stdout.decode('utf-8', errors='replace'), 'stderr': process.stderr.decode('utf-8', errors='replace')})
    dependencies = [Path(__file__), ROOT/'Blender/benchmarks/capacity_audit/trace_exact_scene_v1.py',
                    ROOT/'Blender/benchmarks/capacity_audit/robust_multipath_v1.py', ROOT/'Blender/tests/test_robust_multipath_v1.py']
    receipt['source_sha256'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
    receipt['files_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.out.iterdir() if p.is_file()}
    (args.out/'receipt.json').write_text(json.dumps(receipt, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'status': receipt['status'], 'cases': len(receipt['cases'])}))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__': raise SystemExit(main())
