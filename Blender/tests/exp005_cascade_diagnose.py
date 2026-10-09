"""Read-only diagnostic of the failed frozen file; no save/render/field gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


def main():
    import bpy
    from mathutils import Vector
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from exp005_scene_readback import export_snapshot
    from exp005_triangle_oracle import trace_scene
    from exp005_runtime_smoke import write_json
    from exp005_reflection import reflect_direction
    p=argparse.ArgumentParser(); p.add_argument('--evidence',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); folder=Path(a.evidence)
    folder.mkdir(parents=True,exist_ok=True)
    source=NEURO3D_COGNITION / 'neuro3d/exp005_cascade_cpu_20260930_0014/base.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source)); bpy.context.view_layer.update()
    scene=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
    snapshot=export_snapshot(scene,depsgraph=dg,view_layer=bpy.context.view_layer)
    # v1 completed bases0/1; basis2 is the first probe without a saved report.
    for index,record in enumerate(snapshot['sources']): record['field_reim']=[int(index==2),0]
    expected=trace_scene(snapshot)
    initial=snapshot['sources'][2]
    stack=[(Vector(initial['position_BU']),Vector(initial['direction']).normalized(),[])]
    events=[]; completed=[]; lost=[]
    while stack:
        origin,direction,history=stack.pop()
        if len(events)>4096 or len(history)>=64: raise ValueError('diagnostic bounds')
        found,point,normal,face,obj,_=scene.ray_cast(dg,origin+direction*1e-6,direction)
        if not found:
            lost.append({'origin':list(origin),'direction':list(direction),'history':history}); continue
        record={'object_id':obj.name,'point':list(point),'normal':list(normal),
                'face':face,'distance_BU':(point-origin).length}
        events.append(record)
        if obj['kind'] in ('det','escape'):
            completed.append(history+[dict(record,event='detect')]); continue
        reflected=(direction-2*direction.dot(normal)*normal).normalized()
        for event,ray in ([('mirror',reflected)] if obj['kind']=='mirror' else [('t',direction),('r',reflected)]):
            stack.append((point,ray,history+[dict(record,event=event)]))
    report={'scope':'readonly bpy traversal diagnostic of v1, not numerical PASS',
            'lost':lost,'completed':completed,'events':events,'oracle_paths':expected['paths'],
            'source_file':str(source),'source_id':initial['id'],
            'blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'blender_version':bpy.app.version_string}
    # Causal microprobe: same saved mesh/origin, only reflection arithmetic changes.
    n=Vector((.7071068286895752,-.7071068286895752,0))
    old=(Vector((0,1,0))-2*Vector((0,1,0)).dot(n)*n).normalized()
    stable=Vector(reflect_direction((0,1,0),n))
    micro=[]
    for origin in ((4,2,0),(4,4,0)):
        for method,direction in [('legacy',old),('normal_norm_corrected',stable)]:
            found,point,normal,face,obj,_=scene.ray_cast(dg,Vector(origin)+direction*1e-6,direction)
            micro.append({'origin':origin,'method':method,'direction':list(direction),
                          'found':found,'object_id':obj.name if found else None})
    report['microprobes']=micro
    write_json(folder/'diagnosis.json',report)
    print('DIAGNOSIS_WRITTEN',len(lost),len(completed),flush=True)


if __name__=='__main__': main()
