"""Retained CPU doubles for generated-history/evaluated-export linkage."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from exp005_history_mzi_export_cpu_audit import doubles,fixture,CASES,evaluated_readback
from exp005_history_generated_export import validate_generated_export


def audit():
    cases=[]
    def control(label,expected,phase,shift):
        bpy,scene=doubles(expected);before=evaluated_readback(bpy,scene);after=copy.deepcopy(before)
        inputs=copy.deepcopy((expected,before,after));out=validate_generated_export(expected,before,after,phase,shift)
        if inputs!=(expected,before,after):raise ValueError('input snapshots mutated')
        cases.append({'case':label,'expected':expected,'fake_evaluated_readback':after,'result':out})
    for label,phase,shift in CASES:
        expected,_=fixture(phase,shift);control(label,expected,phase,shift)
    # Added same-plane facet shifts downstream primitive IDs without moving
    # any optical plane. Fresh traversal must derive them, not reuse rows.
    expected,_=fixture();expected['objects']['MA']['faces'].insert(0,[0,2,3])
    control('CPU_only_face_reindex',expected,0.,0.)
    negatives=[];expected,_=fixture();bpy,scene=doubles(expected);base=evaluated_readback(bpy,scene)
    for label in ('unchecked','reopen_change','same_side_phase_change','coherence_change'):
        before=copy.deepcopy(base);after=copy.deepcopy(base)
        if label=='unchecked':before['evaluated_optics_checked']=False
        elif label=='reopen_change':after['objects']['MA']['phase_rad']=.2
        elif label=='same_side_phase_change':before['objects']['MA']['phase_rad']=.2;after=copy.deepcopy(before)
        else:before['coherence_groups']={'s':'other'};after=copy.deepcopy(before)
        try:validate_generated_export(expected,before,after,0.,0.)
        except ValueError as e:negatives.append({'case':label,'reason':str(e)})
        else:raise ValueError('invalid generated export accepted: '+label)
    return {'scope':'CPU doubles only: no bpy/save/reopen/GPU execution',
            'cases':cases,'negatives':negatives,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=audit()
    b=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_generated_export.py')]
    files += [b/'tests'/n for n in ('exp005_history_generated_export.py','exp005_history_mzi_export_cpu_audit.py',
          'exp005_history_mzi_export.py','exp005_history_mzi_audit.py','exp005_scene_readback.py',
          'exp005_scene_properties.py','test_exp005_scene_readback.py')]
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_trace_cpu_v1.py','history_fields_cpu_v1.py',
          'history_lengths_cpu_v1.py','history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
          'frontier_inputs.py','gpu_geometry_probe.py')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'CPU_double_controls':len(out['cases']),'negative_checks':len(out['negatives']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
