"""Tiny NEW saved/reopened fixtures for readback/depsgraph parity, not fields.

CPU only; no render or propagation. Must run under gpuq + owned-child watchdog.
Expected outcomes frozen in EXPECTED before execution; no multicell promotion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

EXPECTED={
    'base':None,
    'hidden_viewport':('hidden optics','missing from evaluated'),
    'hidden_render':('hidden optics',),
    'hidden_layer':('hidden in view layer','missing from evaluated'),
    'excluded_collection':('missing from evaluated',),
    'negative_transform':('negative/singular',),
    'singular_transform':('negative/singular',),
    'render_only_modifier':('modifiers unsupported',),
    'mesh_only_phase':('phase_rad',),
    'shared_mesh_object_phases':None,
}


def main():
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from exp005_runtime_smoke import build
    from exp005_scene_readback import export_snapshot
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    folder=Path(args.evidence).resolve(); folder.mkdir(parents=True,exist_ok=True)
    if any(folder.glob('*.blend')) or (folder/'parity_runtime.json').exists():
        raise ValueError('fresh evidence folder required; no overwrite')
    reports=[]
    for case,reasons in EXPECTED.items():
        build('base'); sc=bpy.context.scene; ob=sc.objects['r1']
        if case=='hidden_viewport': ob.hide_viewport=True
        elif case=='hidden_render': ob.hide_render=True
        elif case=='hidden_layer': ob.hide_set(True)
        elif case=='excluded_collection':
            collection=bpy.data.collections.new('excluded_optics'); sc.collection.children.link(collection)
            sc.collection.objects.unlink(ob); collection.objects.link(ob)
            bpy.context.view_layer.update()
            bpy.context.view_layer.layer_collection.children[collection.name].exclude=True
        elif case=='negative_transform': ob.scale.x=-1
        elif case=='singular_transform': ob.scale.x=0
        elif case=='render_only_modifier':
            mod=ob.modifiers.new('render_only','BEVEL'); mod.show_viewport=False; mod.show_render=True
        elif case=='mesh_only_phase':
            del ob['phase_rad']; ob.data['phase_rad']=.3
        elif case=='shared_mesh_object_phases':
            other=bpy.data.objects.new('shared_mirror',ob.data); sc.collection.objects.link(other)
            other.location.x=100; other['kind']='mirror'; other['phase_rad']=.4
            ob['phase_rad']=.2
            sc['optical_object_ids']=json.dumps(json.loads(sc['optical_object_ids'])+[other.name])
        path=folder/f'{case}.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path)); bpy.ops.wm.open_mainfile(filepath=str(path))
        bpy.context.view_layer.update()
        report={'case':case,'expected':'accept' if reasons is None else 'reject',
                'blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        try:
            snap=export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),
                                 view_layer=bpy.context.view_layer)
            report.update(outcome='accept',passed=reasons is None and snap['evaluated_optics_checked'])
            if case=='shared_mesh_object_phases':
                a=bpy.context.scene.objects['r1']; b=bpy.context.scene.objects['shared_mirror']
                report['shared_datablock']=a.data.as_pointer()==b.data.as_pointer()
                report['object_phases']=[snap['objects']['r1']['phase_rad'],snap['objects']['shared_mirror']['phase_rad']]
                report['passed'] &= report['shared_datablock'] and report['object_phases']==[.2,.4]
            (folder/f'{case}_snapshot.json').write_text(json.dumps(snap,indent=2)+'\n',encoding='utf-8')
        except (ValueError,KeyError) as exc:
            report.update(outcome='reject',error_type=type(exc).__name__,reason=str(exc),
                          passed=reasons is not None and any(token in str(exc) for token in reasons))
        reports.append(report)
        result={'scope':'saved/reopened readback parity only, no optical fields, raycast or RT',
                'passed':all(r['passed'] for r in reports),'completed_cases':len(reports),
                'expected_cases':len(EXPECTED),'cases':reports,'blender_version':bpy.app.version_string,
                'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (folder/'parity_runtime.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if not result['passed']: raise ValueError('parity smoke failed; preserve results, do not relax expected outcomes')
    print('EXP005_PARITY_RUNTIME_PASS',flush=True)


if __name__=='__main__': main()
