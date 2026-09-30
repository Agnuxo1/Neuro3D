"""CPU wavelength ABI audit: no geometry tracing, GPU, Blender or peer writers."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_inputs import pack_frontier
from exp005_blender_gpu import split_double
from exp005_precision_fixture import direct
import wavelength_transport_v1 as candidate

# Prospective representation budget only, NOT an optical-field gate.
RELATIVE_BUDGET = 1e-12
VALUES = (.125, 1e-6, 1e-30, 1e-40, 1e-46, 1e-300, 1e30, 1e39)


def audit():
    rows = []
    for value in VALUES:
        scene = direct(2.)
        scene['lambda_BU'] = value
        pack_frontier(scene)  # The frozen raw preflight admits all eight inputs.
        row = {'lambda_BU': value, 'raw_preflight_accepted': True}
        try:
            hi, lo = split_double(value)
        except (OverflowError, ValueError) as exc:
            row.update(legacy_split_error=type(exc).__name__)
        else:
            decoded = float(hi)+float(lo)
            row.update(decoded_BU=decoded, relative_error=abs(decoded-value)/value,
                       collapsed=decoded <= 0.)
        try:
            row['candidate'] = candidate.checked_wavelength(value, relative_budget=RELATIVE_BUDGET)
        except ValueError as exc:
            row.update(candidate_rejected=True, rejection=str(exc))
        else:
            row['candidate_rejected'] = False
        rows.append(row)
    return {'scope': 'CPU actual wavelength hi-lo ABI and opt-in preflight; NO GPU runtime',
            'relative_budget': RELATIVE_BUDGET, 'rows': rows,
            'limitations': 'Representation budget only; no path-length/phase/complex-field accuracy certificate.'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    r = audit()
    paths = (Path(__file__), Path(candidate.__file__),
             Path(__file__).with_name('exp005_blender_gpu.py'),
             Path(__file__).with_name('exp005_precision_fixture.py'),
             Path(__file__).with_name('exp005_peer_ambiguity_audit.py'),
             Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'frontier_inputs.py',
             Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'gpu_geometry_probe.py')
    r['code_sha256'] = {str(x): hashlib.sha256(x.read_bytes()).hexdigest() for x in paths}
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'cases': len(r['rows']),
        'collapses': sum(x.get('collapsed', False) for x in r['rows']),
        'legacy_split_errors': sum('legacy_split_error' in x for x in r['rows']),
        'candidate_rejections': sum(x['candidate_rejected'] for x in r['rows']),
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
