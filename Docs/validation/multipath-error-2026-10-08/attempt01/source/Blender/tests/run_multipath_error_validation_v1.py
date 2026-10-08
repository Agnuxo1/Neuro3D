"""Retain new certificate acceptance evidence, including negative attempts."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import test_multipath_error_certificate_v1 as tests
from multipath_error_certificate_v1 import certify_scene,default_radii
from exp005_chain_fixture import chain_fixture,inputs,set_fields


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,required=True); args=parser.parse_args()
    if args.out.exists(): raise ValueError('fresh certificate evidence directory required')
    args.out.mkdir(parents=True)
    output=io.StringIO()
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    report={'schema':'neuro3d-error-certification-validation-v1','time_utc':datetime.now(timezone.utc).isoformat(),
            'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'test_output':output.getvalue(),
            'scope':'CPU complete scalar model; external input radii supplied, physical bounds unknown'}
    rows=[]
    if result.wasSuccessful():
        max_field=max_power=F(0)
        for cells in (3,4):
            snapshot=chain_fixture(cells)
            for label,amps in inputs(cells+1):
                set_fields(snapshot,amps); certificate=certify_scene(snapshot)
                max_field=max(max_field,max(F(*p['field_error_L1_upper']) for p in certificate['ports'].values()))
                max_power=max(max_power,max(F(*p['intensity_error_upper']) for p in certificate['ports'].values()))
                rows.append({'cells':cells,'probe':label,'certificate':certificate})
        report.update(analytic_certificates=len(rows),max_field_error_upper=float(max_field),max_intensity_error_upper=float(max_power))
        (args.out/'certificates.json').write_bytes((json.dumps(rows,indent=2,allow_nan=False)+'\n').encode())
        adverse=[]
        snapshot=tests.scene({'out':tests.plane_x(2)})
        for label,change in [('stable',lambda b:b['object_translation'].update(out=(F(1,10**6),0,0))),
                             ('angular',lambda b:b['source_direction'].update(input=(0,F(1,10**6),0))),
                             ('missing_physical',lambda b:b.update(vertex_radius=None))]:
            bounds=default_radii(snapshot); change(bounds)
            adverse.append({'case':label,'certificate':certify_scene(snapshot,radii=bounds)})
        (args.out/'input_boxes.json').write_bytes((json.dumps(adverse,indent=2,allow_nan=False)+'\n').encode())
    deps=[Path(__file__),Path(tests.__file__),ROOT/'Blender/benchmarks/capacity_audit/rational_interval_v1.py',
          ROOT/'Blender/benchmarks/capacity_audit/multipath_error_certificate_v1.py',ROOT/'Blender/benchmarks/capacity_audit/robust_multipath_v1.py',
          ROOT/'Blender/tests/exp005_chain_fixture.py',ROOT/'Docs/ERROR_CERTIFICATE_PREREGISTRATION_2026-10-08.md']
    report['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in deps}
    report['evidence_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.out.iterdir() if p.is_file()}
    (args.out/'receipt.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:report[k] for k in ('status','tests','failures','errors')}))
    if not result.wasSuccessful(): print(output.getvalue()[-16000:])
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__': raise SystemExit(main())
