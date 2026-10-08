"""Retain real CLI certificates for exact scenes, input boxes and refusals."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from test_multipath_error_certificate_v1 import default_radii,scene,plane_x
from exp005_chain_fixture import chain_fixture,set_fields
from trace_exact_scene_v1 import encode


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,required=True); args=parser.parse_args()
    if args.out.exists(): raise ValueError('fresh CLI certificate evidence required')
    args.out.mkdir(parents=True)
    cases=[]
    for cells in (3,4):
        for all_modes in (False,True):
            snapshot=chain_fixture(cells)
            if all_modes: set_fields(snapshot,[1+0j]*(cells+1))
            bounds=default_radii(snapshot); radius=F(1,10**8)
            bounds['source_position']=radius
            bounds['object_translation']={n:(radius,)*3 for n in snapshot['objects']}
            bounds['source_direction']={s['id']:tuple(radius if v else F(0) for v in s['direction']) for s in snapshot['sources']}
            cases.append((f'k{cells}_'+('all' if all_modes else 'row'),snapshot,bounds,'CERTIFIED_SUPPLIED_MODEL_BOX'))
    snapshot=scene({'out':plane_x(2)})
    cases.append(('exact',snapshot,None,'CERTIFIED_REPRESENTED_MODEL'))
    bounds=default_radii(snapshot); bounds['source_direction']['input']=(0,F(1,10**6),0)
    cases.append(('angular',snapshot,bounds,'UNKNOWN'))
    bounds=default_radii(snapshot); bounds['vertex_radius']=None
    cases.append(('missing',snapshot,bounds,'UNKNOWN'))
    gap=F(1,2**44); snapshot=scene({'bs':plane_x(1,'bs',power_transmittance=1),'out':plane_x(1+gap)})
    bounds=default_radii(snapshot); bounds['object_translation']['bs']=(gap,0,0)
    cases.append(('gap_order',snapshot,bounds,'UNKNOWN'))
    receipt={'scope':'real public CPU error-certificate CLI','cases':[],'status':'PASS'}
    for name,snapshot,bounds,expected in cases:
        source,output=args.out/(name+'.scene.json'),args.out/(name+'.certificate.json')
        source.write_bytes((json.dumps(encode(snapshot),indent=2,allow_nan=False)+'\n').encode())
        command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'Blender/benchmarks/capacity_audit/certify_exact_scene_v1.py'),
                 '--scene',str(source),'--out',str(output)]
        if bounds is not None:
            bound_path=args.out/(name+'.radii.json')
            bound_path.write_bytes((json.dumps(encode(bounds),indent=2,allow_nan=False)+'\n').encode()); command+=['--radii',str(bound_path)]
        process=subprocess.run(command,capture_output=True,timeout=60)
        value=json.loads(output.read_bytes()) if output.exists() else {}
        passed=process.returncode==(2 if expected=='UNKNOWN' else 0) and value.get('status')==expected
        if not passed: receipt['status']='FAIL'
        record={'case':name,'expected':expected,'status':value.get('status'),'reason':value.get('reason'),
                'exit_code':process.returncode,'pass':passed,'path_count':value.get('path_count'),
                'stdout':process.stdout.decode('utf-8',errors='replace'),'stderr':process.stderr.decode('utf-8',errors='replace')}
        if value.get('ports'):
            record.update(max_field_error_upper=max(p['field_error_L1_upward_float'] for p in value['ports'].values()),
                          max_intensity_error_upper=max(p['intensity_error_upward_float'] for p in value['ports'].values()))
        receipt['cases'].append(record)
    deps=[Path(__file__),ROOT/'Blender/benchmarks/capacity_audit/certify_exact_scene_v1.py',
          ROOT/'Blender/benchmarks/capacity_audit/multipath_error_certificate_v1.py',ROOT/'Blender/benchmarks/capacity_audit/rational_interval_v1.py',
          ROOT/'Blender/benchmarks/capacity_audit/robust_multipath_v1.py',ROOT/'Docs/ERROR_CERTIFICATE_COVERAGE_AMENDMENT_2026-10-08.md']
    receipt['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in deps}
    receipt['evidence_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.out.iterdir() if p.is_file()}
    (args.out/'receipt.json').write_bytes((json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':receipt['status'],'cases':len(receipt['cases'])}))
    return 0 if receipt['status']=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())
