"""Fresh saved/reopened K3/K4 scenes; native raw-scene GPU tracing, not RT.

Host builds/exports/preflights/transfers and independently validates. Only raw
scene data reach dispatch; the shader owns ray branching and complex fields.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from exp005_chain_fixture import chain_fixture,inputs,analytic_fields
from exp005_frontier_runtime import parity
from frontier_gpu import dispatch,native_shader,SHADER

CASES=('base','sham','phase','shift','T','lambda')
NEGATIVES={'missing_mirror':'lost ray','overlap':'ambiguous geometry',
           'direction':'terminal direction mismatch','step':'step limit','depth':'depth limit'}


def validate_roundtrip(fixture,before,after):
    if before!=after or not after.get('evaluated_optics_checked'):
        raise ValueError('evaluated save/reopen mismatch')
    for name in ('schema','lambda_BU','objects','sources','undeclared_meshes'):
        # JSON normalizes tuples only; no rounding or tolerance for optical state.
        if json.loads(json.dumps(fixture[name]))!=json.loads(json.dumps(after[name])):
            raise ValueError('fixture to scene mismatch: '+name)


def analytic_check(cells,case,amps,native):
    if case not in ('base','sham','phase'): return None
    reference=analytic_fields(cells,amps,phase_shift=.1 if case=='phase' else 0.)
    if set(reference)!=set(native['ports']): raise ValueError('analytic port set mismatch')
    error=max(abs(complex(*native['ports'][p]['field_reim'])-f) for p,f in reference.items())
    if error>1e-4: raise ValueError('independent analytic complex gate failed')
    return error


def causal_check(results,count):
    for label,_ in inputs(count):
        if results[('base',label)]!=results[('sham',label)]:
            raise ValueError('exact GPU sham mismatch')
    base=results[('base','basis0')]['ports']
    effects={case:max(abs(results[(case,'basis0')]['ports'][p]['power']-d['power'])
                           for p,d in base.items()) for case in ('phase','shift','T','lambda')}
    if min(effects.values())<=1e-3: raise ValueError('frozen causal power gate failed')
    return effects


def build_scene(bpy,fixture,case):
    # This private child starts factory-empty and never opens an existing asset.
    for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
    scene=bpy.context.scene
    scene['optical_contract']=fixture['schema']; scene['lambda_BU']=fixture['lambda_BU']
    scene['optical_object_ids']=json.dumps(list(fixture['objects']))
    scene['optical_sources']=json.dumps(fixture['sources'])
    for name,record in fixture['objects'].items():
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(record['vertices_world_BU'],[],record['faces']); mesh.update()
        obj=bpy.data.objects.new(name,mesh); scene.collection.objects.link(obj)
        for prop in ('kind','phase_rad','power_transmittance','mode_origin_BU','mode_direction'):
            if prop in record: obj[prop]=record[prop]
        if case=='sham': obj.color=(.1,.3,.7,1.)
    return scene


def readback(bpy,scene):
    from exp005_scene_readback import export_snapshot
    for obj in scene.objects: obj.update_tag()
    bpy.context.view_layer.update()
    return export_snapshot(scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)


def source_fields(scene,amps):
    values=json.loads(scene['optical_sources'])
    if len(values)!=len(amps): raise ValueError('complete source state required')
    for source,amp in zip(values,amps): source['field_reim']=[amp.real,amp.imag]
    scene['optical_sources']=json.dumps(values)


def serialize(oracle):
    return {'fields':{p:[f.real,f.imag] for p,f in oracle['fields'].items()},'powers':oracle['powers'],
            'rays':oracle['rays'],'input_power':oracle['input_power'],
            'paths':[{'source_id':p['source_id'],'terminal':p['terminal'],
                      'length_BU':p['length_BU'],'reference_offset_BU':p['reference_offset_BU'],
                      'field_reim':[p['field'].real,p['field'].imag]} for p in oracle['paths']]}


def main():
    import bpy
    import gpu
    from exp005_blender_gpu import schedule_exit
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]); folder=args.evidence.resolve()
    if not args.authorized_by_user or args.report.exists() or folder.exists():
        raise ValueError('authorized fresh scenes and report required; never overwrite')
    folder.mkdir(); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    dependencies=[Path(__file__),SHADER,Path(__file__).with_name('exp005_chain_fixture.py'),
                  Path(__file__).with_name('exp005_frontier_runtime.py'),
                  Path(__file__).with_name('exp005_triangle_oracle.py'),
                  Path(__file__).with_name('exp005_scene_readback.py'),
                  Path(__file__).with_name('exp005_mode_gate.py')]
    dependencies += [Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/n
                     for n in ('frontier_gpu.py','frontier_inputs.py','gpu_geometry_probe.py')]
    report={'passed':False,'scope':'K3/K4 scalar coherent raw-scene GPU ALUs within Blender; NO RT/BVH',
            'host_scope':'construction/export/preflight/transfer/readback and independent CPU validation',
            'blender_version':bpy.app.version_string,'renderer':gpu.platform.renderer_get(),
            'backend':gpu.platform.backend_type_get(),'mode_cap':5,
            'thresholds':{'complex_ledger_sum_analytic':1e-4,'power_balance':2e-4,
                          'ledger_length_BU':1e-5,'causal_power_min':1e-3},
            'code_sha256':{str(p.relative_to(Path(__file__).parents[2])):sha(p) for p in dependencies},
            'cases':[],'scenes':[],'negative_controls':[]}
    def write(path,value): path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    shader=None
    try:
        if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA GPU required')
        shader=native_shader(gpu)
        for cells in (3,4):
            results={}
            for case in CASES:
                fixture=chain_fixture(cells,treatment=case); scene=build_scene(bpy,fixture,case)
                before=readback(bpy,scene); blend=folder/f'K{cells}_{case}.blend'
                if blend.exists(): raise ValueError('new blend required')
                bpy.ops.wm.save_as_mainfile(filepath=str(blend))
                digest=sha(blend); bpy.ops.wm.open_mainfile(filepath=str(blend)); scene=bpy.context.scene
                after=readback(bpy,scene); validate_roundtrip(fixture,before,after)
                write(folder/f'K{cells}_{case}_snapshot.json',after)
                report['scenes'].append({'cells':cells,'case':case,'file':blend.name,'sha256':digest,'evaluated_roundtrip_equal':True})
                records=[]
                for label,amps in inputs(cells+1):
                    source_fields(scene,amps); snapshot=readback(bpy,scene)
                    native,elapsed=dispatch(gpu,shader,snapshot,mode_cap=5)
                    metrics,oracle=parity(snapshot,native)
                    metrics['analytic_error']=analytic_check(cells,case,amps,native)
                    results[(case,label)]=native
                    report['cases'].append({'cells':cells,'case':case,'probe':label,'metrics':metrics,
                        'dispatch_sync_readback_ms':elapsed,'paths':sum(p['paths'] for p in native['ports'].values())})
                    records.append({'probe':label,'snapshot':snapshot,'gpu':native,'oracle':serialize(oracle)})
                    write(folder/f'K{cells}_{case}.json',records)
                if sha(blend)!=digest: raise ValueError('saved scene modified during inference')
                write(args.report,report)
            report.setdefault('power_effects',{})[str(cells)]=causal_check(results,cells+1)
            for case,expected in NEGATIVES.items():
                bpy.ops.wm.open_mainfile(filepath=str(folder/f'K{cells}_base.blend')); scene=bpy.context.scene
                source_fields(scene,[1+0j]+[0j]*cells); options={'mode_cap':5}; target=f'c{cells-1}.r1'
                if case=='missing_mirror':
                    bpy.data.objects.remove(scene.objects[target],do_unlink=True)
                    scene['optical_object_ids']=json.dumps([n for n in json.loads(scene['optical_object_ids']) if n!=target])
                if case=='overlap':
                    obj=scene.objects[target].copy(); obj.data=obj.data.copy(); obj.name='alias.r1'
                    scene.collection.objects.link(obj)
                    scene['optical_object_ids']=json.dumps(json.loads(scene['optical_object_ids'])+[obj.name])
                if case=='direction': scene.objects[f'c{cells-1}.Y']['mode_direction']=[0.,-1.,0.]
                if case=='step': options['max_steps']=1
                if case=='depth': options['max_depth']=1
                snapshot=readback(bpy,scene); native,elapsed=dispatch(gpu,shader,snapshot,**options)
                write(folder/f'K{cells}_negative_{case}.json',{'snapshot':snapshot,'options':options,'gpu':native})
                if native['valid'] or len(native['errors'])!=cells+1 or set(native['errors'].values())!={expected}:
                    raise ValueError('specific fail-closed GPU control absent: '+case+' '+str(native))
                report['negative_controls'].append({'cells':cells,'case':case,'errors':native['errors'],
                                                    'dispatch_sync_readback_ms':elapsed})
        if len(report['cases'])!=246 or len(report['negative_controls'])!=10 or len(report['scenes'])!=12:
            raise ValueError('frozen complete run counts required')
        for item in report['scenes']:
            if sha(folder/item['file'])!=item['sha256']: raise ValueError('scene hash changed')
        if any(sha(p)!=report['code_sha256'][str(p.relative_to(Path(__file__).parents[2]))] for p in dependencies):
            raise ValueError('code changed during run')
        report['passed']=True; print('EXP005_CHAIN_NATIVE_GPU_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: write(args.report,report)
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
