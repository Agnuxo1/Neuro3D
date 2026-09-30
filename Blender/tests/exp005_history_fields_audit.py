"""Own analytic fixture fields, no peer code or GPU calls."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from history_fields_cpu_v1 import ideal_fields
from exp005_history_completeness_audit import fixture,duplicate_sources
from exp005_history_lengths_audit import rebinding


def audit():
    rows=[]
    for tau in (0.,.25,.5,1.):
        s,r=fixture(True);s['objects']['B']['power_transmittance']=tau;rebinding(s,r)
        out=ideal_fields(s,r,coherence_groups={'s':'g'})
        expected={'T':tau,'E':1-tau}
        expected_fields={'T':[math.sqrt(tau),0.],'E':[0.,math.sqrt(1-tau)]}
        if any(abs(out['ports'][p]['intensity']-x)>1e-14 for p,x in expected.items()):
            raise ValueError('analytic splitter intensity mismatch')
        if any(abs(complex(*out['ports'][p]['groups']['g']['field_reim'])-complex(*z))>1e-14
               for p,z in expected_fields.items()):
            raise ValueError('analytic splitter complex phase mismatch')
        rows.append({'case':'splitter_T_'+str(tau),'snapshot':s,'records':r,'expected_intensities':expected,
                     'expected_fields':expected_fields,'result':out})
    for tag,groups,opposite,expected in (
        ('coherent',{'s':'g','s2':'g'},False,{'T':2.,'E':2.}),
        ('incoherent',{'s':'g1','s2':'g2'},False,{'T':1.,'E':1.}),
        ('destructive',{'s':'g','s2':'g'},True,{'T':0.,'E':0.})):
        s,r=duplicate_sources()
        if opposite:s['sources'][1]['field_reim']=[-1.,0.];rebinding(s,r)
        out=ideal_fields(s,r,coherence_groups=groups)
        if any(abs(out['ports'][p]['intensity']-x)>1e-14 for p,x in expected.items()):
            raise ValueError('analytic coherence mismatch')
        rows.append({'case':tag,'snapshot':s,'records':r,'expected_intensities':expected,'result':out})
    return {'scope':'synthetic scene-bound ideal CPU fields, not GPU/RT or precision repair',
            'analytic_cases':rows,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=audit()
    b=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_fields.py')]
    files += [b/'tests'/n for n in ('exp005_history_lineage_audit.py','exp005_history_completeness_audit.py','exp005_history_lengths_audit.py')]
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_fields_cpu_v1.py','history_lengths_cpu_v1.py',
                                                      'history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
                                                      'frontier_inputs.py','gpu_geometry_probe.py')]
    files += [b/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with a.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'analytic_cases':len(out['analytic_cases']),
                      'report_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
