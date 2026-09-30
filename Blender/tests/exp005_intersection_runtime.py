"""Read-only frozen scene, native GPU intersection component; not RT/network.

Intermediate queries are previous CPU ray inputs, never expected hits sent GPU.
Independent reference and bpy compare results only after native readback.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from gpu_geometry_probe import BIAS,pack_geometry,native_geometry_shader,dispatch_geometry,require_unambiguous
from exp005_triangle_oracle import geometry,triangle_hit,unit,add,scale,dot


def queries_from_records(snapshot,records):
    sources={s['id']:s for s in snapshot['sources']}; queries=[]; seen=set()
    def append(origin,direction):
        key=tuple(origin)+tuple(direction)
        if key not in seen:
            seen.add(key); queries.append({'origin_BU':list(origin),'direction':list(direction)})
    for source in sources.values(): append(source['position_BU'],source['direction'])
    for record in records:
        for path in record['bpy']:
            origin=sources[path['source_id']]['position_BU']
            for hit in path['hits']:
                append(origin,hit['incoming_direction']); origin=hit['point_BU']
    for origin,direction in (([50,50,50],[1,0,0]),([-50,-50,-50],[0,-1,0])):
        append(origin,direction)
    return queries


def independent_hits(snapshot,queries):
    _,objects=geometry(snapshot); results=[]
    for ray in queries:
        direction=unit(ray['direction']); origin=add(ray['origin_BU'],scale(direction,BIAS)); hits=[]
        for name,obj in objects.items():
            for triangle in obj['triangles']:
                hit=triangle_hit(origin,direction,triangle,1e-9)
                if hit is not None: hits.append((hit[0],name,hit[1]))
        if not hits: results.append({'status':'miss'}); continue
        distance,name,normal=min(hits,key=lambda x:x[0])
        ambiguous=any(n!=name for t,n,_ in hits if abs(t-distance)<=1e-9)
        results.append({'status':'ambiguous' if ambiguous else 'hit','object_id':name,
                        'distance_BU':distance+BIAS,'normal':normal})
    return results


def compare(actual,expected):
    if len(actual)!=len(expected): raise ValueError('incomplete comparisons')
    max_distance=0.; max_normal=0.
    for a,e in zip(actual,expected):
        if a['status']!=e['status']: raise ValueError('nearest hit/miss/ambiguity mismatch')
        if e['status']=='miss': continue
        if e['status']=='hit' and a['object_id']!=e['object_id']: raise ValueError('nearest object mismatch')
        max_distance=max(max_distance,abs(a['distance_BU']-e['distance_BU']))
        max_normal=max(max_normal,abs(1-abs(dot(a['normal'],e['normal']))))
    if max_distance>1e-5 or max_normal>1e-6: raise ValueError('frozen intersection precision gate failed')
    return {'distance_max_BU':max_distance,'normal_absdot_error_max':max_normal}


def main():
    import bpy
    import gpu
    from mathutils import Vector
    from exp005_scene_readback import export_snapshot
    from exp005_blender_gpu import schedule_exit
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    artifacts=args.report.with_suffix('')
    if not args.authorized_by_user or args.report.exists() or artifacts.exists(): raise ValueError('authorization/fresh artifacts required')
    artifacts.mkdir(); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    blend=args.evidence/'base.blend'; inputs=[blend]+[args.evidence/f'base_basis{i}_paths.json' for i in range(3)]
    hashes={p.name:sha(p) for p in inputs}
    report={'passed':False,'scope':'native GPU raw-triangle nearest-hit component, not RT, optical fields or complete network',
            'query_origin':'fixed source and previous CPU path rays; no GPU propagation proved',
            'thresholds':{'distance_BU':1e-5,'normal_absdot_error':1e-6},'input_sha256':hashes,'cases':[],
            'blender_version':bpy.app.version_string,'backend':gpu.platform.backend_type_get(),'renderer':gpu.platform.renderer_get()}
    if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA context required')
    shader=None
    try:
        bpy.ops.wm.open_mainfile(filepath=str(blend)); bpy.context.view_layer.update()
        base=export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
        queries=queries_from_records(base,[json.loads(p.read_text()) for p in inputs[1:]])
        report['query_count']=len(queries); shader=native_geometry_shader(gpu); results={}
        for label in ('base','sham','shift','removed','overlap'):
            bpy.ops.wm.open_mainfile(filepath=str(blend)); scene=bpy.context.scene
            if label=='sham': scene.objects['a.r1'].color=(.1,.3,.7,1.)
            if label=='shift':
                for name in ('a.r1','a.r2'):
                    obj=scene.objects[name]
                    for vertex in obj.data.vertices: vertex.co.x+=.03125
                    obj.data.update(); obj.update_tag()
            if label=='removed':
                bpy.data.objects.remove(scene.objects['a.r1'],do_unlink=True)
                scene['optical_object_ids']=json.dumps([n for n in json.loads(scene['optical_object_ids']) if n!='a.r1'])
            if label=='overlap':
                duplicate=scene.objects['a.r1'].copy(); duplicate.data=duplicate.data.copy(); duplicate.name='alias.r1'
                scene.collection.objects.link(duplicate)
                scene['optical_object_ids']=json.dumps(json.loads(scene['optical_object_ids'])+[duplicate.name])
            bpy.context.view_layer.update(); graph=bpy.context.evaluated_depsgraph_get()
            snapshot=export_snapshot(scene,depsgraph=graph,view_layer=bpy.context.view_layer)
            batch=pack_geometry(snapshot,queries); actual,elapsed=dispatch_geometry(gpu,shader,batch)
            reference=independent_hits(snapshot,queries); metrics=compare(actual,reference)
            bpy_hits=[]; comparable=[]
            for i,(ray,result) in enumerate(zip(queries,reference)):
                if result['status']=='ambiguous': continue
                origin=Vector(ray['origin_BU']); direction=Vector(ray['direction']).normalized()
                found,point,normal,_,obj,_=scene.ray_cast(graph,origin+direction*BIAS,direction)
                bpy_hits.append({'status':'hit','object_id':obj.name,'distance_BU':(point-origin).length,
                                 'normal':list(normal.normalized())} if found else {'status':'miss'})
                comparable.append(actual[i])
            bpy_metrics=compare(comparable,bpy_hits)
            ambiguous=sum(r['status']=='ambiguous' for r in actual); misses=sum(r['status']=='miss' for r in actual)
            rejection=None
            try: require_unambiguous(actual)
            except ValueError as exc: rejection=str(exc)
            if label=='overlap' and (not ambiguous or rejection is None): raise ValueError('overlap control did not reject')
            if label!='overlap' and (ambiguous or rejection): raise ValueError('unexpected ambiguity')
            if misses<2: raise ValueError('explicit external miss controls failed')
            results[label]=actual
            report['cases'].append({'case':label,'triangles':batch.triangle_count,'queries':batch.query_count,
                'oracle_metrics':metrics,'bpy_metrics':bpy_metrics,'ambiguous':ambiguous,'misses':misses,
                'inference_rejection':rejection,'dispatch_sync_readback_ms':elapsed})
            (artifacts/f'{label}.json').write_text(json.dumps({'snapshot':snapshot,'queries':queries,
                'gpu':actual,'oracle':reference,'bpy_nonambiguous':bpy_hits},indent=2,allow_nan=False)+'\n',encoding='utf-8')
        def changed(a,b):
            return sum(x['status']!=y['status'] or x.get('object_id')!=y.get('object_id') or
                       abs(x.get('distance_BU',0)-y.get('distance_BU',0))>1e-5 for x,y in zip(a,b))
        report['changed_queries']={n:changed(results['base'],results[n]) for n in ('sham','shift','removed')}
        if results['sham']!=results['base'] or min(report['changed_queries'][n] for n in ('shift','removed'))<1:
            raise ValueError('geometry causal/sham controls failed')
        if any(sha(p)!=hashes[p.name] for p in inputs): raise ValueError('frozen input modified')
        code=[Path(__file__),Path(__file__).with_name('exp005_triangle_oracle.py'),
              Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'gpu_geometry_probe.py',
              Path(__file__).parents[1]/'shaders'/'exp005_intersections.glsl']
        report['code_sha256']={p.name:sha(p) for p in code}; report['passed']=True
        print('EXP005_GPU_INTERSECTION_COMPONENT_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
