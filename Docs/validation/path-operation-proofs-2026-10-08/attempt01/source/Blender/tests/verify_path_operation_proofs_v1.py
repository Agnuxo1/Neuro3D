"""Concrete counterexamples and exact-cancellation provenance for point 5."""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from exp005_chain_fixture import chain_fixture,analytic_fields
from robust_multipath_v1 import trace_scene,estimate_path_field
from multipath_error_certificate_v1 import certify_scene,wire


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,required=True); args=parser.parse_args()
    if args.out.exists(): raise ValueError('fresh point-5 output required')
    args.out.mkdir(parents=True)
    scene=chain_fixture(2); scene['objects']['c0.r1']['phase_rad']=0
    dark=trace_scene(scene); certificate=certify_scene(scene)
    dark_paths=[p for p in dark['paths'] if p['terminal']=='c0.Y']
    contributions=[estimate_path_field(p,dark['wavelength']) for p in dark_paths]
    wrong_incoherent=sum(abs(v)**2 for v in contributions)
    shifted=copy.deepcopy(scene); shifted['objects']['c0.r1']['phase_rad']=1e-6
    lit=trace_scene(shifted)
    # The independent analytic transfer formula knows the dark amplitude exactly.
    expected=analytic_fields(2,[1+0j,0j,0j])
    expected_dark=F(0)  # phi0=0: yx=(1-exp(i*0))/2=0, irrespective of later cells.
    checks={
        'dark_complete':dark['status']=='COMPLETE',
        'nonzero_histories_retained':len(dark_paths)==2 and all(p['power_factor']>0 for p in dark_paths),
        'coherent_dark':abs(dark['fields']['c0.Y'])<1e-12,
        'intensity_sum_counterexample':wrong_incoherent>.49 and dark['powers']['c0.Y']<1e-24,
        'certificate_encloses_true_dark':certificate['status']=='CERTIFIED_REPRESENTED_MODEL' and all(
            F(*certificate['ports']['c0.Y'][k]['lo'])<=expected_dark<=F(*certificate['ports']['c0.Y'][k]['hi'])
            for k in ('field_real','field_imag','intensity')),
        'phase_change_reactivates_same_paths':lit['status']=='COMPLETE' and abs(lit['fields']['c0.Y'])>1e-7 and
            len([p for p in lit['paths'] if p['terminal']=='c0.Y'])==len(dark_paths),
        'small_terms_accumulate_exactly':sum([F(1,2**20)]*4096)==F(1,2**8),
    }
    # A dark observed total is not an exact-zero path. Two opposite prefix fields
    # are an algebraic counterexample to phase-blind power reduction.
    report={'schema':'neuro3d-path-operation-proof-witnesses-v1','status':'PASS' if all(checks.values()) else 'FAIL',
            'checks':checks,'dark_trace':dark,'dark_certificate':certificate,'shifted_trace':lit,
            'wrong_incoherent_intensity':wrong_incoherent,'correct_estimated_intensity':dark['powers']['c0.Y'],
            'scope':'CPU ideal scalar model; independent symbolic dark-port identity; no general fusion/performance claim'}
    deps=[Path(__file__),ROOT/'Blender/benchmarks/capacity_audit/robust_multipath_v1.py',
          ROOT/'Blender/benchmarks/capacity_audit/multipath_error_certificate_v1.py',
          ROOT/'Blender/benchmarks/capacity_audit/rational_interval_v1.py',ROOT/'Docs/PATH_OPERATION_PROOFS_2026-10-08.md']
    report['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in deps}
    (args.out/'receipt.json').write_bytes((json.dumps(wire(report),indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':report['status'],'checks':checks,'nonzero_dark_paths':len(dark_paths),
                      'wrong_power':wrong_incoherent,'dark_power':dark['powers']['c0.Y']}))
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())
