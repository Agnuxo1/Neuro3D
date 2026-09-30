"""Small own length/reference fixtures and retained report, CPU only."""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from history_lengths_cpu_v1 import reconstruct_lengths,sqrt_interval
from exp005_history_completeness_audit import fixture,duplicate_sources,scene_binding


def rebinding(s,r):
    sha,_=scene_binding(s)
    for row in r: row['snapshot_sha256']=sha


def audit():
    valid=[]
    for split in (False,True):
        s,r=fixture(split)
        valid.append({'case':'splitter' if split else 'mirror','snapshot':s,'records':r,'result':reconstruct_lengths(s,r)})
    s,r=fixture(True)
    for row in r: row['direction']=[3*x for x in row['direction']]
    s['sources'][0]['direction']=[3.,0.,0.];s['objects']['T']['mode_origin_BU'][0]=2.25
    rebinding(s,r)
    valid.append({'case':'raw_direction_3_reference_shift','snapshot':s,'records':r,'result':reconstruct_lengths(s,r)})
    s,r=duplicate_sources()
    valid.append({'case':'two_separate_sources','snapshot':s,'records':r,'result':reconstruct_lengths(s,r)})
    roots=[]
    for q in (F(0),F(1),F(2),F(5),F(1,2**60),F(2**60+1)):
        lo,hi=sqrt_interval(q)
        if not lo*lo<=q<=hi*hi: raise ValueError('sqrt enclosure failed')
        roots.append({'squared':[q.numerator,q.denominator],
                      'lower':[lo.numerator,lo.denominator],'upper':[hi.numerator,hi.denominator]})
    s,r=fixture(True);s['objects']['T']['mode_direction']=[1.,1e-12,0.];rebinding(s,r)
    try: reconstruct_lengths(s,r)
    except ValueError as e: rejected={'reason':str(e),'snapshot':s,'records':r}
    else: raise ValueError('non-collinear terminal accepted')
    return {'scope':'synthetic CPU ideal length enclosures, NOT phase/native precision repair',
            'valid':valid,'sqrt_checks':roots,'rejected_terminal':rejected,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=audit()
    b=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_lengths.py'),
           b/'tests/exp005_history_lineage_audit.py',b/'tests/exp005_history_completeness_audit.py']
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_lengths_cpu_v1.py','history_completeness_cpu_v1.py',
                                                      'history_lineage_cpu_v2.py','frontier_inputs.py','gpu_geometry_probe.py')]
    files += [b/'shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with a.output.open('x',encoding='utf-8') as f: f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'valid_trees':len(out['valid']),'sqrt_checks':len(out['sqrt_checks']),
                      'report_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
