"""Small own synthetic history fixtures, no GPU or peer imports/writers."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from history_lineage_cpu_v1 import scene_binding,validate_history


def plane(x,kind):
    o={'kind':kind,'vertices_world_BU':[[x,-1.,-1.],[x,1.,-1.],[x,1.,1.],[x,-1.,1.]],'faces':[[0,1,2],[0,2,3]]}
    if kind=='mirror': o['phase_rad']=0.
    if kind=='bs': o['power_transmittance']=.5
    if kind in ('det','escape'): o.update(mode_origin_BU=[x,0.,0.],mode_direction=[1. if kind=='det' else -1.,0.,0.])
    return o


def fixture(splitter=False):
    objects={'B':plane(1.,'bs'),'T':plane(2.,'det'),'E':plane(-1.,'escape')} if splitter else {'M':plane(1.,'mirror'),'D':plane(-1.,'det')}
    if not splitter: objects['D']['mode_direction']=[-1.,0.,0.]
    s={'schema':'exp005-readback-v2','lambda_BU':.125,'objects':objects,'undeclared_meshes':[],
       'sources':[{'id':'s','position_BU':[0.,0.,0.],'direction':[1.,0.,0.],'field_reim':[1.,0.]}]}
    sha,_=scene_binding(s)
    def node(i,parent,event,pid,x,dx,depth):
        return {'id':i,'parent_id':parent,'source_id':'s','snapshot_sha256':sha,'depth':depth,
                'event':event,'primitive_id':pid,'origin_BU':[x,0.,0.],'direction':[dx,0.,0.]}
    rows=[node(0,None,'source',None,0.,1.,0)]
    if splitter: rows += [node(1,0,'t',0,1.,1.,1),node(2,0,'r',0,1.,-1.,1),node(3,1,'detect',2,2.,1.,2),node(4,2,'escape',4,-1.,-1.,2)]
    else: rows += [node(1,0,'mirror',0,1.,-1.,1),node(2,1,'detect',2,-1.,-1.,2)]
    return s,rows


def negatives():
    s,base=fixture()
    for label,mutate in (
        ('fake_prior_primitive',lambda r:r[1].update(primitive_id=2)),
        ('wrong_reflection',lambda r:r[1].update(direction=[1.,0.,0.])),
        ('shifted_saved_origin',lambda r:r[1].update(origin_BU=[1.+1e-8,0.,0.])),
        ('undeclared_source',lambda r:r[1].update(source_id='other')),
        ('depth_tamper',lambda r:r[1].update(depth=2)),
        ('future_parent',lambda r:r[1].update(parent_id=2)),
        ('wrong_role',lambda r:r[1].update(event='t')),
        ('duplicate_record_id',lambda r:r[2].update(id=1))):
        rows=copy.deepcopy(base); mutate(rows); yield label,s,rows


def audit():
    valid=[]
    for splitter in (False,True):
        s,rows=fixture(splitter); valid.append({'fixture':'splitter' if splitter else 'mirror','snapshot':s,'input_records':rows,'result':validate_history(s,rows)})
    rejected=[]
    for label,s,rows in negatives():
        try: validate_history(s,rows)
        except ValueError as e: rejected.append({'case':label,'reason':str(e)})
        else: raise ValueError('invalid history accepted: '+label)
    return {'scope':'synthetic exact CPU history prefix, NOT Blender/GPU readback or transport',
            'valid':valid,'rejected':rejected,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();report=audit()
    root=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_lineage.py')]
    files += [root/'benchmarks/capacity_audit'/n for n in ('history_lineage_cpu_v1.py','frontier_inputs.py','gpu_geometry_probe.py')]
    files += [root/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    report['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'valid_prefixes':len(report['valid']),'rejected_histories':len(report['rejected']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
