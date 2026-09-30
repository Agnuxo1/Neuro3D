"""Own exact represented two-arm MZI fixture and analytic CPU comparison.

No Blender or GPU, no external oracle/writer, no trained matrix. Histories
are explicit candidate inputs that the existing exact tree gate verifies.
"""
import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from history_fields_cpu_v1 import ideal_fields
from history_lineage_cpu_v2 import scene_binding


def diagonal(x,y,kind,phase=0.):
    out={'kind':kind,'vertices_world_BU':[[x-.125,y-.125,-.125],[x+.125,y+.125,-.125],
                                         [x+.125,y+.125,.125],[x-.125,y-.125,.125]],
         'faces':[[0,1,2],[0,2,3]]}
    if kind=='bs':out['power_transmittance']=.5
    if kind=='mirror':out['phase_rad']=phase
    return out


def fixture(phase=0.,reference_shift=0.):
    dx={'kind':'det','vertices_world_BU':[[2.,.875,-.125],[2.,1.125,-.125],
                                         [2.,1.125,.125],[2.,.875,.125]],
        'faces':[[0,1,2],[0,2,3]],'mode_origin_BU':[2.+reference_shift,1.,0.],'mode_direction':[1.,0.,0.]}
    dy={'kind':'det','vertices_world_BU':[[.875,2.,-.125],[1.125,2.,-.125],
                                         [1.125,2.,.125],[.875,2.,.125]],
        'faces':[[0,1,2],[0,2,3]],'mode_origin_BU':[1.,2.,0.],'mode_direction':[0.,1.,0.]}
    objects={'B1':diagonal(0.,0.,'bs'),'MA':diagonal(1.,0.,'mirror',phase),
             'MB':diagonal(0.,1.,'mirror'),'B2':diagonal(1.,1.,'bs'),'Dx':dx,'Dy':dy}
    s={'schema':'exp005-readback-v2','lambda_BU':.125,'objects':objects,'undeclared_meshes':[],
       'sources':[{'id':'s','position_BU':[-1.,0.,0.],'direction':[1.,0.,0.],'field_reim':[1.,0.]}]}
    sha,_=scene_binding(s)
    def node(i,parent,event,pid,x,y,ux,uy,depth):
        return {'id':i,'parent_id':parent,'source_id':'s','snapshot_sha256':sha,'depth':depth,
                'event':event,'primitive_id':pid,'origin_BU':[x,y,0.],'direction':[ux,uy,0.]}
    rows=[node(0,None,'source',None,-1.,0.,1.,0.,0),
          node(1,0,'t',0,0.,0.,1.,0.,1),node(2,0,'r',0,0.,0.,0.,1.,1),
          node(3,1,'mirror',2,1.,0.,0.,1.,2),node(4,2,'mirror',4,0.,1.,1.,0.,2),
          node(5,3,'t',6,1.,1.,0.,1.,3),node(6,3,'r',6,1.,1.,1.,0.,3),
          node(7,4,'t',6,1.,1.,1.,0.,3),node(8,4,'r',6,1.,1.,0.,1.,3),
          node(9,5,'detect',10,1.,2.,0.,1.,4),node(10,6,'detect',8,2.,1.,1.,0.,4),
          node(11,7,'detect',8,2.,1.,1.,0.,4),node(12,8,'detect',10,1.,2.,0.,1.,4)]
    return s,rows


def analytic(phase,shift=0.):
    # Derived two-arm formula, independent of traversal/ledger implementation.
    a=cmath.exp(1j*phase)
    return {'Dx':-.5j*(1+a)*cmath.exp(1j*math.tau*shift/.125),'Dy':.5*(1-a)}


def audit():
    cases=[];max_error=0.;max_balance=0.
    for phase,shift in [(p,0.) for p in (0.,math.pi/2,math.pi,3*math.pi/2,2*math.pi)]+[(0.,.03125)]:
        s,rows=fixture(phase,shift);out=ideal_fields(s,rows,coherence_groups={'s':'g'})
        expected=analytic(phase,shift)
        errors={port:abs(complex(*out['ports'][port]['groups']['g']['field_reim'])-z)
                for port,z in expected.items()}
        balance=abs(sum(v['intensity'] for v in out['ports'].values())-1.)
        max_error=max(max_error,*errors.values());max_balance=max(max_balance,balance)
        if max(errors.values())>1e-13 or balance>1e-13:raise ValueError('analytic MZI gate failed')
        if len(out['ledger'])!=4 or any(v['groups']['g']['path_count']!=2 for v in out['ports'].values()):
            raise ValueError('two distinct arms per output required')
        cases.append({'phase_rad':phase,'reference_shift_BU':shift,'snapshot':s,'records':rows,
                      'expected_fields':{p:[z.real,z.imag] for p,z in expected.items()},
                      'field_errors':errors,'balance_error':balance,'result':out})
    return {'scope':'exact represented synthetic CPU MZI geometry and ideal digital fields, NOT Blender/GPU/RT',
            'cases':cases,'max_field_error':max_error,'max_balance_error':max_balance,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=audit()
    b=Path(__file__).parents[1];files=[Path(__file__),Path(__file__).with_name('test_exp005_history_mzi.py')]
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_fields_cpu_v1.py','history_lengths_cpu_v1.py',
                                                      'history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
                                                      'frontier_inputs.py','gpu_geometry_probe.py')]
    files += [b/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':len(out['cases']),'max_field_error':out['max_field_error'],
                      'max_balance_error':out['max_balance_error'],
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
