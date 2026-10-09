"""Own retained CPU replay of Claude's two history fixtures; no peer writers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
import history_lineage_cpu_v1 as old
import history_lineage_cpu_v2 as new
from exp005_history_lineage_audit import fixture,negatives
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT=Path(__file__).parents[2]
PEER=NEURO3D_COGNITION / 'neuro3d/history_claude'
PINS={ROOT/'coordinacion/respuestas/HISTORY-LINEAGE-CLAUDE.json':'80e5e57de7696485e3d5738efe224a4ceab5e3650d71c8fdc7ede4a8f3242ca0',
      PEER/'a_false_reject.py':'c26f56f8d63c51f35b8738c7a07e5ef47406f03bba15615ae12c13c7346f92b0',
      PEER/'a_false_reject.json':'9acd37b274dbe8aafaf0f5bf3df5c6deee2e0ee05b2cae5767248f55a0fac4a2'}


def replay():
    hashes={}
    for path,sha in PINS.items():
        raw=path.read_bytes();current=hashlib.sha256(raw).hexdigest()
        if current!=sha:raise ValueError('peer input changed: '+str(path))
        hashes[str(path)]=current
    peer=json.loads((PEER/'a_false_reject.json').read_text())
    if len(peer['cases'])!=2:raise ValueError('two retained peer fixtures required')
    cases=[]
    for c in peer['cases']:
        s,records=c['snapshot'],c['records']
        try:old.validate_history(s,records);was='accepted';reason=None
        except ValueError as e:was='rejected';reason=str(e)
        result=new.validate_history(s,records)
        if result['records'][1]['t_parameter_exact']!=[2,1]:raise ValueError('wrong terminal parameter')
        cases.append({'snapshot':s,'input_records':records,'v1':was,'v1_reason':reason,'v2':result})
    if [c['v1'] for c in cases]!=['accepted','rejected']:raise ValueError('old false-reject reproduction changed')
    for splitter in (False,True):
        s,r=fixture(splitter)
        if old.validate_history(s,r)['records']!=new.validate_history(s,r)['records']:raise ValueError('old positive changed')
    rejected=[]
    for label,s,records in negatives():
        try:new.validate_history(s,records)
        except ValueError as e:rejected.append({'case':label,'reason':str(e)})
        else:raise ValueError('old negative accepted: '+label)
    return {'scope':'retained synthetic CPU fixtures; no Bpy/GPU history or rounding bound',
            'peer_sha256':hashes,'cases':cases,'old_positives_preserved':2,'old_negatives_rejected':rejected,
            'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    report=replay();b=ROOT/'Blender'
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_coplanar.py'),b/'tests/exp005_history_lineage_audit.py']
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_lineage_cpu_v1.py','history_lineage_cpu_v2.py','frontier_inputs.py','gpu_geometry_probe.py')]
    files += [b/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    report['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'v1_retained_false_reject':1,'v2_peer_cases_accepted':2,'old_negatives_rejected':8,
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
