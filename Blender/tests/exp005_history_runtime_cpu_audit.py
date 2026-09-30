"""Own in-memory workflow double, not actual bpy or blend persistence."""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import exp005_history_generated_runtime as runtime
from exp005_history_mzi_export_cpu_audit import doubles,evaluated_readback


def workflow(*,change_on_reopen=False,fail_save=False):
    scenes={};events=[]
    bpy=NS(data=NS(filepath='',scenes=scenes),context=NS(window=NS(scene=None)),app=NS(version_string='CPU DOUBLE'))
    def build(_bpy,expected,name):
        fake,scene=doubles(expected);scenes[name]=(fake,scene);return scenes[name]
    def read(_bpy,pair):return evaluated_readback(*pair)
    def save(**kwargs):
        events.append({'event':'save','path':kwargs['filepath']})
        if fail_save:raise OSError('synthetic save failure')
    def reopen(**kwargs):
        events.append({'event':'reopen','path':kwargs['filepath']})
        if change_on_reopen:
            for fake,scene in scenes.values():scene.objects['MA']['phase_rad']=.25
    bpy.ops=NS(wm=NS(save_as_mainfile=save,open_mainfile=reopen))
    def clock():events.append({'event':'deadline_check'})
    with patch.object(runtime,'build_isolated_scene',build),patch.object(runtime,'evaluated_readback',read),\
         patch.object(Path,'exists',return_value=False),patch.object(Path,'mkdir'),\
         patch.object(Path,'read_bytes',return_value=b'CPU DOUBLE, NOT BLEND'):
        try:result=runtime.run_private_child(bpy,Path('synthetic_evidence'),clock)
        except (ValueError,OSError) as e:return {'scope':'CPU workflow double only','events':events,'error':str(e)}
    return {'scope':'CPU workflow double only, NOT bpy/files/process lifecycle','events':events,'result':result}


def audit():
    control=workflow();changed=workflow(change_on_reopen=True);failed=workflow(fail_save=True)
    if 'result' not in control or len(control['result']['cases'])!=3:raise ValueError('workflow control failed')
    if 'error' not in changed or 'error' not in failed:raise ValueError('invalid workflow accepted')
    return {'scope':'in-memory CPU double; no real Blender/save/reopen/guard/process/GPU',
            'control':control,'reopen_changed':changed,'save_failed':failed,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=audit()
    b=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_generated_runtime.py')]
    files += [b/'tests'/n for n in ('exp005_history_generated_runtime.py','exp005_history_generated_export.py',
       'exp005_history_mzi_export_cpu_audit.py','exp005_history_mzi_export.py','exp005_history_mzi_audit.py',
       'exp005_scene_readback.py','exp005_scene_properties.py','test_exp005_scene_readback.py')]
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_trace_cpu_v1.py','history_fields_cpu_v1.py',
       'history_lengths_cpu_v1.py','history_completeness_cpu_v1.py','history_lineage_cpu_v2.py','frontier_inputs.py','gpu_geometry_probe.py')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'fake_bpy_cases':3,'workflow_negatives':2,'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
