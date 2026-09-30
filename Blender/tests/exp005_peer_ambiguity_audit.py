"""Bounded independent reproduction using retained peer CPU emulator only.

Does not execute peer scripts (which write peer artifacts) or GPU. Preserves
old shaders; finding is emulated semantics, not a runtime GPU certification.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_inputs import pack_frontier
from exp005_triangle_oracle import trace_scene


def plane(x,kind):
    record={'kind':kind,'vertices_world_BU':[(x,-.125,-.125),(x,.125,-.125),(x,.125,.125),(x,-.125,.125)],
            'faces':[(0,1,2),(0,2,3)]}
    if kind=='mirror':record['phase_rad']=0.
    else:record.update(mode_origin_BU=(-1.,0.,0.),mode_direction=(-1.,0.,0.))
    return record


def audit(peer_path):
    spec=importlib.util.spec_from_file_location('retained_peer_emulator',peer_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=[]
    for order in itertools.permutations('ABC'):
        offset={'A':0.,'B':-.9e-9,'C':-1.8e-9}
        objects={name:plane(5.+offset[name],'mirror') for name in order}
        objects['D']=plane(-1.,'det')
        scene={'schema':'exp005-readback-v2','lambda_BU':.125,'objects':objects,'undeclared_meshes':[],
               'sources':[{'id':'s','position_BU':[0.,0.,0.],'direction':[1.,0.,0.],'field_reim':[1.,0.]}]}
        batch=pack_frontier(scene)
        distance,index,normal,ambiguous=module.nearest(module.Kernel(batch),(0.,0.,0.),(1.,0.,0.))
        try:trace_scene(scene,max_rays=4)
        except ValueError as exc:
            if 'ambiguous' not in str(exc):raise
            oracle_rejected=True
        else:oracle_rejected=False
        rows.append({'order':''.join(order),'peer_emulated_ambiguous':bool(ambiguous),
                     'selected':batch.geometry.object_ids[index],'oracle_rejected':oracle_rejected})
    if sum(r['peer_emulated_ambiguous'] for r in rows)!=5 or not all(r['oracle_rejected'] for r in rows):
        raise ValueError('reported six-permutation counterexample did not reproduce')
    return {'reproduced':True,'scope':'CPU peer emulator and independent triangular oracle; GPU runtime not tested',
        'peer_sha256':hashlib.sha256(peer_path.read_bytes()).hexdigest(),'rows':rows,
        'consequence':'no generalization/scaling until new order-independent nearest-hit contract and adversarial GPU gate'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--peer',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('new own audit evidence required')
    result=audit(a.peer);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
