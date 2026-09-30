"""CPU reproduction of peer F3; additional gates, NOT a frozen runner edit."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
import precision_v3
from exp005_precision_fixture import direct
from exp005_triangle_oracle import trace_scene


def audit():
    old = ((0., True), (2e-5, True), (2e-4, False), (math.pi, False))
    new = ((3e-5, True), (6.3e-5, False))
    def accepts(theta, tolerance):
        return precision_v3.terminal_accept((1., 0., 0.),
            (math.cos(theta), math.sin(theta), 0.), dot_tolerance=tolerance)
    rows = []
    for tolerance in (1e-10, 2e-10, 4e-10, 1e-9, 5e-9, 1e-8, 5e-8):
        rows.append({'dot_tolerance': tolerance,
            'old_four_pass': all(accepts(a, tolerance) == want for a, want in old),
            'new_two_pass': all(accepts(a, tolerance) == want for a, want in new)})
    oracle = []
    for angle, expected in new:
        try:
            result = trace_scene(direct(2., angle), max_rays=4)
        except ValueError as exc:
            if 'arrival direction' not in str(exc): raise
            accepted = False
        else:
            accepted = result['rays'] == 1 and result['powers']['D'] == 1.
        if accepted != expected: raise ValueError('independent complete-scene control failed')
        oracle.append({'angle_rad': angle, 'expected_accept': expected,
                       'oracle_accept': accepted, 'v3_accept': accepts(angle, 1e-9)})
    if not all(r['v3_accept'] == r['expected_accept'] for r in oracle):
        raise ValueError('V3 specification mismatch')
    return {'scope': 'CPU scalar specification and full-scene oracle, NO GPU runtime',
        'rows': rows, 'oracle_controls': oracle,
        'consequence': 'Supplemental gates kill selected tolerance mutants; no proof of exact boundary or self-hit repair.'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    r = audit()
    paths = (Path(__file__), Path(precision_v3.__file__),
             Path(__file__).with_name('exp005_precision_fixture.py'),
             Path(__file__).with_name('exp005_triangle_oracle.py'))
    r['code_sha256'] = {str(x): hashlib.sha256(x.read_bytes()).hexdigest() for x in paths}
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'rows': len(r['rows']), 'oracle_controls': len(r['oracle_controls']),
        'killed_selected_mutants': [x['dot_tolerance'] for x in r['rows'] if x['old_four_pass'] and not x['new_two_pass']],
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
