"""Small prospective CPU phase-budget experiment, not a native precision gate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
import phase_transport_budget_v1 as candidate

WAVELENGTHS = (.125, 1e-6, 1.23456789e-6, .123456789,
               1.11111111111111e-6, 3.141592653589793e-6)
LENGTHS = (2., 1e6)
RELATIVE_BUDGET = 1e-12
PHASE_BUDGET_RAD = 1e-4


def audit():
    rows = []
    for wavelength in WAVELENGTHS:
        for length in LENGTHS:
            result = candidate.wavelength_phase_budget(wavelength,
                max_effective_length_BU=length, phase_budget_rad=PHASE_BUDGET_RAD,
                relative_budget=RELATIVE_BUDGET)
            rows.append({'wavelength_BU': wavelength, **result})
    return {'scope': 'CPU rational wavelength-only budget; NO GPU/runtime/length-bound proof',
            'phase_budget_rad': PHASE_BUDGET_RAD, 'rows': rows}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    r = audit()
    paths = (Path(__file__), Path(candidate.__file__),
             Path(candidate.__file__).with_name('wavelength_transport_v1.py'),
             Path(candidate.__file__).with_name('frontier_inputs.py'),
             Path(candidate.__file__).with_name('gpu_geometry_probe.py'),
             Path(__file__).with_name('exp005_blender_gpu.py'))
    r['code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'cases': len(r['rows']),
        'phase_rejections': sum(not x['accepted'] for x in r['rows']),
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
