"""Own small scene-to-history CPU pilot with frozen analytic MZI controls."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from exp005_history_mzi_audit import fixture,analytic,ideal_fields
from history_trace_cpu_v1 import trace_scene


def audit():
    cases=[]
    for label,phase,shift in (('base',0.,0.),('switch',math.pi,0.),('reference',0.,.03125)):
        snapshot,expected=fixture(phase,shift);before=copy.deepcopy(snapshot)
        out=trace_scene(snapshot)
        if out['records']!=expected:raise ValueError('generated geometry history differs from fixed MZI oracle')
        if snapshot!=before:raise ValueError('snapshot mutated')
        fields=ideal_fields(snapshot,out['records'],coherence_groups={'s':'g'})
        error=max(abs(complex(*fields['ports'][p]['groups']['g']['field_reim'])-z) for p,z in analytic(phase,shift).items())
        if error>1e-13:raise ValueError('generated CPU fields differ from analytic MZI')
        cases.append({'case':label,'snapshot':snapshot,'trace':out,'field_error':error,'fields':fields})
    negatives=[]
    for kwargs in ({'record_cap':12},{'depth_cap':3},{'record_cap':65},{'depth_cap':33},{'record_cap':True}):
        s,_=fixture()
        try:trace_scene(s,**kwargs)
        except ValueError as e:negatives.append({'caps':kwargs,'reason':str(e)})
        else:raise ValueError('invalid cap or truncated trace accepted')
    return {'scope':'CPU exact synthetic scene traversal and fields only; no bpy/readback/native backend',
            'cases':cases,'cap_negatives':negatives,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=audit()
    b=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_trace.py'),b/'tests/exp005_history_mzi_audit.py']
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_trace_cpu_v1.py','history_fields_cpu_v1.py',
                  'history_lengths_cpu_v1.py','history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
                  'frontier_inputs.py','gpu_geometry_probe.py')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'controls':len(out['cases']),'cap_negatives':len(out['cap_negatives']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
