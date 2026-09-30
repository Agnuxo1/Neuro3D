"""Own eight-case CPU wavelength/phase replay; no peer sweep or GPU use."""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import sys
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from wavelength_transport_v1 import checked_wavelength
from phase_transport_budget_v1 import wavelength_phase_budget

RESPONSE = ROOT/'coordinacion/respuestas/PRECISION-006-CLAUDE.json'
RESPONSE_SHA = '5503b62c0031ab289e8f4278267f9958f2b2075c2aea4634119c405c7a836727'


def verified_peer():
    raw = RESPONSE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != RESPONSE_SHA: raise ValueError('peer response changed')
    peer = json.loads(raw)
    if peer['task_id'] != 'PRECISION-006' or peer['status'] != 'complete': raise ValueError('complete response required')
    hashes = {}
    for name, sha in peer['input_sha256'].items():
        path = ROOT/name
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha: raise ValueError('input changed: '+name)
        hashes[str(path)] = sha
    for name, sha in peer['artifacts']['artifact_sha256'].items():
        path = Path(peer['artifacts'][name])
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha: raise ValueError('artifact changed: '+name)
        hashes[str(path)] = sha
    return json.loads(Path(peer['artifacts']['a_lambda.json']).read_bytes()), hashes


def case_result(row):
    wavelength, length = row['lambda_BU'], row['L_eff_BU']
    transport = checked_wavelength(wavelength, relative_budget=1e-12)
    original, decoded = Fraction(wavelength), Fraction(transport['decoded_BU'])
    delta_cycles = Fraction(length)*(1/original-1/decoded)
    # Display only: pi is binary64 here, NOT exact-real pi or native sin/cos proof.
    signed_phase = float(2*delta_cycles)*math.pi
    budget = wavelength_phase_budget(wavelength, max_effective_length_BU=abs(length),
        phase_budget_rad=1e-4, relative_budget=1e-12)
    return {'peer_case': row, 'transport': transport,
        'delta_cycles_exact': [delta_cycles.numerator, delta_cycles.denominator],
        'signed_phase_rad_display': signed_phase,
        'peer_phase_display_delta': abs(signed_phase-row['phase_error_rad']),
        'unit_complex_delta_display': 2*abs(math.sin(math.pi*float(delta_cycles))),
        'wavelength_only_budget': budget,
        'length_bound_status': 'example supplied, NOT proved from a scene'}


def audit():
    peer, hashes = verified_peer()
    rows = [dict(case_result(row), group=group) for group in ('counterexamples', 'controls') for row in peer[group]]
    reported = peer['geometry_vs_lambda_term']['ulp_over_2_C=1e6_BU']
    actual_half_ulp = math.ulp(1e6)/2
    return {'scope': 'CPU actual hi-lo ABI + exact cycle differences, no native field network',
        'response_sha256': RESPONSE_SHA, 'verified_peer_sha256': hashes,
        'rows': rows, 'wavelength_budget_rejections': sum(not r['wavelength_only_budget']['accepted'] for r in rows),
        'half_ulp_audit': {'coordinate_BU': 1e6, 'peer_labeled_half_ulp_BU': reported,
            'actual_half_ulp_BU': actual_half_ulp, 'peer_to_actual_ratio': reported/actual_half_ulp},
        'limitations': ['Eight retained examples, NOT validation of random sweeps or universal max relative errors',
            'Unit-amplitude scalar complex delta is NOT multiple-path total-field error',
            'Length examples not a scene-derived bound; geometry/ref/source errors excluded',
            'Exact rational delta cycles; float pi/sin displays are not a native argument-reduction certificate',
            'No adoption of peer AABB reference restrictions or unmeasured N<=2^40 threshold',
            'No GPU/Bpy/RT/physical optics, no edits/execution of peer writers']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('new evidence path required')
    result = audit()
    files = [Path(__file__), Path(__file__).with_name('test_exp005_precision006_review.py')]
    files += [ROOT/'Blender/benchmarks/capacity_audit'/n for n in ('phase_transport_budget_v1.py',
        'wavelength_transport_v1.py', 'frontier_inputs.py')]
    files += [Path(__file__).with_name('exp005_blender_gpu.py')]
    files += [ROOT/'Blender/shaders'/n for n in ('exp005_shared_frontier.glsl', 'exp005_nearest_v2.glsl')]
    result['own_code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'cases': len(result['rows']), 'budget_rejections': result['wavelength_budget_rejections'],
        'half_ulp_ratio': result['half_ulp_audit']['peer_to_actual_ratio'],
        'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
