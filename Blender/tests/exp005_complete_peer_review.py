"""Own small replay of retained COMPLETE001 evidence, no peer imports/writers."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from history_completeness_cpu_v1 import validate_complete_tree
from history_lineage_cpu_v2 import scene_binding
from exp005_history_mzi_audit import fixture
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT=Path(__file__).parents[2]
RESPONSE=ROOT/'coordinacion/respuestas/PRECISION-COMPLETE-001-CLAUDE.json'


def verify_peer():
    data=json.loads(RESPONSE.read_text(encoding='utf-8'));checked={}
    for name,expected in data['input_sha256_verified_equal_to_task_pins'].items():
        path=(NEURO3D_COGNITION / 'neuro3d'/name) if name=='exp005_history_mzi_cpu_20260930_1308.json' else ROOT/name
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected:raise ValueError('peer input changed: '+name)
        checked[str(path)]=actual
    for name,path in data['artifacts'].items():
        actual=hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if actual!=data['artifact_sha256'][name]:raise ValueError('peer artifact changed: '+name)
        checked[path]=actual
    retained=json.loads(Path(data['artifacts']['probes.json']).read_text(encoding='utf-8'))
    if retained['results']!=data['results']:raise ValueError('retained peer results differ from response')
    checked[str(RESPONSE)]=hashlib.sha256(RESPONSE.read_bytes()).hexdigest()
    if checked[str(RESPONSE)]!='e146c62499472c26b2e657eb76f31d46a0260e43934a17624da5b5365e84abf6':
        raise ValueError('reviewed peer response changed')
    return data,checked


def rebind(s,rows):
    sha,_=scene_binding(s)
    for row in rows:row['snapshot_sha256']=sha


def candidates():
    s,r=fixture();yield 'control',s,r,True,None
    s,r=fixture();s['objects']['B1']['faces'].append(copy.deepcopy(s['objects']['B1']['faces'][0]));rebind(s,r)
    yield 'duplicate_face_without_downstream_reindex',s,r,False,'independently selected nearest'
    s,r=copy.deepcopy((s,r))
    for row in r:
        if row['primitive_id'] is not None and row['primitive_id']>=2:row['primitive_id']+=1
    yield 'duplicate_face_with_correct_global_ids',s,r,True,None
    for name,drop in (('subtree4_omitted',{7,8,11,12}),('whole_first_r_arm_omitted',{2,4,7,8,11,12})):
        s,r=fixture();yield name,s,[row for row in r if row['id'] not in drop],False,'incomplete tree'
    for tau in (0.,1.):
        s,r=fixture()
        for name in ('B1','B2'):s['objects'][name]['power_transmittance']=tau
        rebind(s,r);yield 'T_'+str(tau),s,r,True,None
    for degenerate in (True,False):
        s,r=fixture()
        s['objects']['Far']={'kind':'escape','vertices_world_BU':
                            [[5.,5.,5.],[6.,6.,6.],[7.,7.,7.]] if degenerate else [[5.,5.,5.],[6.,5.,5.],[5.,6.,5.]],
                            'faces':[[0,1,2]],'mode_origin_BU':[5.,5.,5.],'mode_direction':[1.,0.,0.]}
        yield ('remote_degenerate' if degenerate else 'remote_valid_unreached_terminal',
               s,r,not degenerate,'degenerate triangle' if degenerate else None)


def audit():
    peer,checked=verify_peer();observed=[]
    for name,s,r,wanted,reason_part in candidates():
        try:
            rebind(s,r);result=validate_complete_tree(s,r);accepted=True;reason=None
        except ValueError as e:
            accepted=False;reason=str(e);result=None
        if accepted!=wanted or (reason_part and reason_part not in (reason or '')):
            raise ValueError('own replay mismatch '+name)
        observed.append({'case':name,'expected_accepted':wanted,'accepted':accepted,'reason':reason,
                         'snapshot':s,'records':r,'result':result})
    return {'scope':'small exact represented CPU completeness review, NOT exhaustive/GPU/optical',
            'peer_status':peer['status'],'peer_probe_count':len(peer['results']),
            'input_sha256':checked,'own_probes':observed,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=audit()
    b=Path(__file__).parents[1];files=[Path(__file__),Path(__file__).with_name('test_exp005_complete_peer_review.py'),
                                     b/'tests/exp005_history_mzi_audit.py']
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_fields_cpu_v1.py','history_lengths_cpu_v1.py',
                                                      'history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
                                                      'frontier_inputs.py','gpu_geometry_probe.py')]
    files += [b/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'peer_probes':out['peer_probe_count'],'own_probes':len(out['own_probes']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
