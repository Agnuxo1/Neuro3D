"""Bound-only CPU review of two retained reopened scenes, no ray replay."""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from scene_length_bound_v1 import scene_wavelength_budget
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


def audit():
    directory = NEURO3D_COGNITION / 'neuro3d/exp005_chain_native_20260930_0315'
    rows, inputs = [], {}
    for name in ('K3_base', 'K4_base'):
        p = directory/(name+'.json'); raw = p.read_bytes()
        inputs[str(p)] = hashlib.sha256(raw).hexdigest()
        case = json.loads(raw)[0]  # Only retained basis0, not a rerun of 246 probes.
        if case['probe'] != 'basis0' or not case['gpu']['valid']:
            raise ValueError('retained valid basis0 required')
        result = scene_wavelength_budget(case['snapshot'], max_depth=32, mode_cap=5,
            phase_budget_rad=1e-4, relative_budget=1e-12)
        limit = Fraction(*result['scene_bound']['effective_length_abs_BU_rational'])
        lengths = [r['effective_length_BU'] for port in case['gpu']['ports'].values() for r in port['ledger']]
        if not lengths or any(abs(Fraction(v)) > limit for v in lengths):
            raise ValueError('retained ledger outside ideal bound')
        rows.append({'scene':name, 'candidate':result, 'retained_ledger_entries':len(lengths),
            'retained_max_abs_effective_length_BU':max(abs(v) for v in lengths),
            'retained_depth_observed':max(p['max_depth'] for p in case['gpu']['ports'].values()),
            'limitation':'RGBA32F retained ledger only, not exact path or native bound certification'})
    return {'scope':'CPU ideal scene bound and retained ledger comparison only',
        'rows':rows, 'input_sha256':inputs, 'native_certified':False}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); result = audit()
    files = [Path(__file__), Path(__file__).with_name('test_exp005_scene_length_bound.py')]
    files += [ROOT/'Blender/benchmarks/capacity_audit'/n for n in
        ('scene_length_bound_v1.py','phase_transport_budget_v1.py','wavelength_transport_v1.py',
         'frontier_inputs.py','gpu_geometry_probe.py')]
    files += [ROOT/'Blender/shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    result['code_sha256'] = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'scenes':len(result['rows']),
        'retained_entries':sum(r['retained_ledger_entries'] for r in result['rows']),
        'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
