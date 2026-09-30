"""Prepared opt-in Blender scene/save/reopen export; NOT executed/qualified yet.

No render, GPU kernel or wave tracing. CPU reference fields explicitly labelled.
Create a NEW isolated scene; never delete objects or overwrite existing assets.
Run only in a guarded exclusive private Blender child, not a desktop console.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from exp005_history_mzi_audit import fixture,analytic
from exp005_scene_readback import export_snapshot
from history_fields_cpu_v1 import ideal_fields
from history_lineage_cpu_v2 import scene_binding

CASES=(('base',0.,0.),('switch',3.141592653589793,0.),('reference',0.,.03125))
CORE=('schema','lambda_BU','objects','sources','undeclared_meshes')


def build_isolated_scene(bpy,expected,name):
    if name in bpy.data.scenes:raise ValueError('fresh isolated scene name required')
    scene=bpy.data.scenes.new(name)
    scene['optical_contract']=expected['schema'];scene['lambda_BU']=expected['lambda_BU']
    scene['optical_object_ids']=json.dumps(list(expected['objects']))
    scene['optical_sources']=json.dumps(expected['sources'])
    scene['coherence_groups']=json.dumps({'s':'g'})
    for name,record in expected['objects'].items():
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(record['vertices_world_BU'],[],record['faces']);mesh.update()
        obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
        obj.location=(0.,0.,0.);obj.scale=(1.,1.,1.);obj.rotation_euler=(0.,0.,0.)
        for prop in ('kind','phase_rad','power_transmittance','mode_origin_BU','mode_direction'):
            if prop in record:obj[prop]=record[prop]
    if bpy.context.window is None:raise ValueError('private Blender window context required')
    bpy.context.window.scene=scene
    return scene


def evaluated_readback(bpy,scene):
    for obj in scene.objects:obj.update_tag()
    bpy.context.view_layer.update()
    out=export_snapshot(scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
    out['coherence_groups']=json.loads(scene['coherence_groups'])
    if set(out['coherence_groups'])!={s['id'] for s in out['sources']}:
        raise ValueError('scene-owned coherence groups required for all sources')
    if any(not isinstance(g,str) or not g for g in out['coherence_groups'].values()):
        raise ValueError('nonempty scene-owned coherence groups required')
    return out


def validate_export(expected,before,after,records,phase,shift):
    if not before.get('evaluated_optics_checked') or not after.get('evaluated_optics_checked'):
        raise ValueError('evaluated readback required before and after reopen')
    if before!=after:raise ValueError('save/reopen readback mismatch')
    if after.get('coherence_groups')!={'s':'g'}:raise ValueError('fixture coherence groups mismatch')
    if list(after['objects'])!=list(expected['objects']):raise ValueError('global object order mismatch')
    for key in CORE:
        if json.loads(json.dumps(expected[key]))!=json.loads(json.dumps(after[key])):
            raise ValueError('fixture-to-evaluated-scene mismatch: '+key)
    # Compute from actual snapshot; expected fixture is a strict equality gate,
    # never a fallback if a Blender property is missing or rounded differently.
    sha,_=scene_binding(after);rows=json.loads(json.dumps(records))
    for row in rows:row['snapshot_sha256']=sha
    reference=ideal_fields(after,rows,coherence_groups=after['coherence_groups'])
    formula=analytic(phase,shift)
    error=max(abs(complex(*reference['ports'][p]['groups']['g']['field_reim'])-z) for p,z in formula.items())
    if error>1e-13:raise ValueError('CPU reference analytic field gate failed')
    return {'scene_binding_sha256':sha,'cpu_reference':reference,'analytic_field_error':error,
            'scope':'save/reopen evaluated scene export plus CPU ideal fields, NOT GPU or Blender wave simulation'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--authorized-private-child',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_private_child:raise ValueError('guarded exclusive private child authorization required')
    folder=args.evidence.resolve()
    if folder.exists():raise ValueError('fresh evidence directory required; never overwrite')
    import bpy  # CPU tests never reach here. Outer gpuq/guard still mandatory.
    if bpy.data.filepath:raise ValueError('must not run on an existing .blend')
    folder.mkdir();report={'scope':'Blender evaluated export and CPU reference only, no GPU inference','cases':[]}
    for label,phase,shift in CASES:
        expected,rows=fixture(phase,shift);name='history_mzi_'+label
        scene=build_isolated_scene(bpy,expected,name);before=evaluated_readback(bpy,scene)
        blend=folder/(label+'.blend')
        if blend.exists():raise ValueError('fresh blend path required')
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.data.scenes[name]
        if bpy.context.window is None:raise ValueError('reopened window context required')
        bpy.context.window.scene=scene;after=evaluated_readback(bpy,scene)
        checked=validate_export(expected,before,after,rows,phase,shift)
        report['cases'].append({'case':label,'before':before,'after':after,'checks':checked,
                                'blend_path':str(blend),'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest()})
    report['blender_version']=bpy.app.version_string
    with (folder/'export.json').open('x',encoding='utf-8') as f:f.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('HISTORY_MZI_EVALUATED_EXPORT_PASS',len(report['cases']))


if __name__=='__main__':main()
