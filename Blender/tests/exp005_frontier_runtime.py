"""Actual raw-scene GPU pilot vs independent CPU oracles; no RT claim."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_gpu import native_shader,dispatch,SHADER
from exp005_triangle_oracle import trace_scene

CASES=('base','sham','phase','lambda','shift','T02','T1')


def parity(snapshot,native):
    if not native['valid']: raise ValueError('GPU aborted valid fixture: '+str(native['errors']))
    oracle=trace_scene(snapshot); field_error=power_error=ledger_error=length_error=ledger_sum_error=0.
    if set(native['ports'])!=set(oracle['fields']): raise ValueError('missing GPU port')
    for port,data in native['ports'].items():
        field=complex(*data['field_reim']); field_error=max(field_error,abs(field-oracle['fields'][port]))
        power_error=max(power_error,abs(data['power']-oracle['powers'][port]))
        expected=[p for p in oracle['paths'] if p['terminal']==port]
        if len(data['ledger'])!=len(expected) or data['casts']!=oracle['rays']: raise ValueError('GPU traversal/path count mismatch')
        ledger_sum_error=max(ledger_sum_error,abs(sum((complex(*r['field_reim']) for r in data['ledger']),0j)-field))
        remaining=expected.copy()
        for row in data['ledger']:
            candidates=[p for p in remaining if p['source_id']==row['source_id'] and
                        abs(p['length_BU']+p['reference_offset_BU']-row['effective_length_BU'])<=1e-5]
            if not candidates: raise ValueError('no independent path ledger correspondence')
            reference=min(candidates,key=lambda p:abs(p['field']-complex(*row['field_reim'])))
            ledger_error=max(ledger_error,abs(reference['field']-complex(*row['field_reim'])))
            length_error=max(length_error,abs(reference['length_BU']+reference['reference_offset_BU']-row['effective_length_BU']))
            remaining.remove(reference)
    balance=abs(sum(d['power'] for d in native['ports'].values())-oracle['input_power'])
    if max(field_error,ledger_error,ledger_sum_error)>1e-4 or max(power_error,balance)>2e-4 or length_error>1e-5:
        raise ValueError('frozen raw-scene GPU numerical gate failed')
    return {'complex_error':field_error,'power_error':power_error,'balance_error':balance,
            'ledger_complex_error':ledger_error,'ledger_length_error_BU':length_error,'ledger_sum_error':ledger_sum_error},oracle


def main():
    import bpy
    import gpu
    from exp005_scene_readback import export_snapshot
    from exp005_cascade_runtime import probes
    from exp005_cascade_bpy_paths import raycast_paths
    from exp005_mode_gate import validate_native_modes
    from exp005_scene_properties import decode_scene,field_for_path
    from exp005_blender_gpu import schedule_exit
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]); artifacts=args.report.with_suffix('')
    if not args.authorized_by_user or args.report.exists() or artifacts.exists(): raise ValueError('authorization/fresh artifacts required')
    artifacts.mkdir(); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    blend=args.evidence/'base.blend'; input_sha=sha(blend)
    report={'passed':False,'scope':'raw-scene scalar traversal/reflection/phase/reduction/intensity native GPU ALUs in Blender; no RT/BVH',
            'cpu_scope':'readback/transport/preflight and independent validation only; no CPU ray inputs to GPU',
            'blender_version':bpy.app.version_string,'renderer':gpu.platform.renderer_get(),'backend':gpu.platform.backend_type_get(),
            'input_sha256':input_sha,'thresholds':{'complex':1e-4,'ledger_complex':1e-4,'power_balance':2e-4,
            'ledger_length_BU':1e-5,'causal_power_min':1e-3},'cases':[],'negative_controls':[]}
    if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA GPU context required')
    shader=None
    def reopen():
        bpy.ops.wm.open_mainfile(filepath=str(blend)); scene=bpy.context.scene; scene['optical_contract']='exp005-readback-v2'
        for obj in scene.objects:
            if obj.get('kind')=='bs': obj['power_transmittance']=.5; obj.update_tag()
        bpy.context.view_layer.update(); return scene
    def readback(scene):
        for obj in scene.objects:
            if obj.get('kind') in ('bs','mirror','det','escape'): obj.update_tag()
        bpy.context.view_layer.update()
        return export_snapshot(scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
    def sources(scene,amps):
        values=json.loads(scene['optical_sources'])
        for source,amp in zip(values,amps): source['field_reim']=[amp.real,amp.imag]
        scene['optical_sources']=json.dumps(values)
    def serialize(oracle):
        return {'fields':{p:[f.real,f.imag] for p,f in oracle['fields'].items()},'powers':oracle['powers'],
                'rays':oracle['rays'],'input_power':oracle['input_power'],'paths':[
                {'source_id':p['source_id'],'terminal':p['terminal'],'length_BU':p['length_BU'],
                 'reference_offset_BU':p['reference_offset_BU'],'field_reim':[p['field'].real,p['field'].imag]} for p in oracle['paths']]}
    try:
        shader=native_shader(gpu); results={}
        for case in CASES:
            scene=reopen()
            if case=='sham': scene.objects['a.r1'].color=(.1,.3,.7,1.)
            if case=='phase': scene.objects['a.r1']['phase_rad']+=.1
            if case=='lambda': scene['lambda_BU']=.126
            if case=='shift':
                for name in ('a.r1','a.r2'):
                    obj=scene.objects[name]
                    for vertex in obj.data.vertices: vertex.co.x+=.03125
                    obj.data.update()
            if case in ('T02','T1'): scene.objects['b.bs2']['power_transmittance']=.2 if case=='T02' else 1.
            records=[]
            for label,amps in probes():
                sources(scene,amps); snapshot=readback(scene)
                native,elapsed=dispatch(gpu,shader,snapshot)  # No paths/CPU expected values passed.
                metrics,oracle=parity(snapshot,native)
                if case=='base':
                    paths,_=raycast_paths(scene); validate_native_modes(snapshot,paths); optics=decode_scene(snapshot)
                    bpy_fields={p:0j for p in native['ports']}
                    for path in paths:
                        value=field_for_path(optics,path['hits'],path['initial_field'],
                                             reference_offset_BU=path['reference_offset_BU'])['field']
                        bpy_fields[path['hits'][-1]['object_id']]+=value
                    bpy_error=max(abs(complex(*native['ports'][p]['field_reim'])-f) for p,f in bpy_fields.items())
                    if bpy_error>1e-4: raise ValueError('independent bpy/hybrid gate failed')
                    metrics['bpy_cpu_field_error']=bpy_error
                results[(case,label)]=native
                report['cases'].append({'case':case,'probe':label,'metrics':metrics,
                    'dispatch_sync_readback_ms':elapsed,'paths':sum(v['paths'] for v in native['ports'].values())})
                records.append({'probe':label,'snapshot':snapshot,'gpu':native,'oracle':serialize(oracle)})
            (artifacts/f'{case}.json').write_text(json.dumps(records,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        portnames=results[('base','basis0')]['ports']
        report['power_effects']={c:max(abs(results[(c,'basis0')]['ports'][p]['power']-results[('base','basis0')]['ports'][p]['power'])
                                    for p in portnames) for c in CASES if c not in ('base','sham')}
        if any(v<=1e-3 for v in report['power_effects'].values()): raise ValueError('causal GPU power control failed')
        for label,_ in probes():
            if results[('base',label)]!=results[('sham',label)]: raise ValueError('exact native sham control failed')
        controls=(('missing_mirror','lost ray'),('overlap','ambiguous geometry'),('direction','terminal direction mismatch'),
                  ('step','step limit'),('depth','depth limit'),('lost_source','lost ray'))
        for case,expected in controls:
            scene=reopen(); sources(scene,[1+0j,0j,0j]); options={}
            if case=='missing_mirror':
                bpy.data.objects.remove(scene.objects['a.r1'],do_unlink=True)
                scene['optical_object_ids']=json.dumps([n for n in json.loads(scene['optical_object_ids']) if n!='a.r1'])
            if case=='overlap':
                obj=scene.objects['a.r1'].copy(); obj.data=obj.data.copy(); obj.name='alias.r1'
                scene.collection.objects.link(obj)
                scene['optical_object_ids']=json.dumps(json.loads(scene['optical_object_ids'])+[obj.name])
            if case=='direction': scene.objects['a.Y']['mode_direction']=[0.,-1.,0.]
            if case=='step': options['max_steps']=1
            if case=='depth': options['max_depth']=1
            if case=='lost_source':
                values=json.loads(scene['optical_sources']); values[0]['direction']=[0.,0.,1.]; scene['optical_sources']=json.dumps(values)
            snapshot=readback(scene); native,elapsed=dispatch(gpu,shader,snapshot,**options)
            if native['valid'] or len(native['errors'])!=3 or set(native['errors'].values())!={expected}:
                raise ValueError('expected GPU fail-closed control absent: '+case+' '+str(native))
            report['negative_controls'].append({'case':case,'errors':native['errors'],'dispatch_sync_readback_ms':elapsed})
            (artifacts/f'negative_{case}.json').write_text(json.dumps({'snapshot':snapshot,'options':options,'gpu':native},indent=2,allow_nan=False)+'\n',encoding='utf-8')
        if len(report['cases'])!=63 or len(report['negative_controls'])!=6 or sha(blend)!=input_sha: raise ValueError('frozen run count/input hash failed')
        dependencies=[Path(__file__),SHADER,Path(__file__).with_name('exp005_triangle_oracle.py'),
            Path(__file__).with_name('exp005_scene_readback.py'),Path(__file__).with_name('exp005_mode_gate.py')]
        dependencies += [Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/n for n in ('frontier_gpu.py','frontier_inputs.py','gpu_geometry_probe.py')]
        report['code_sha256']={p.name:sha(p) for p in dependencies}; report['passed']=True
        print('EXP005_RAW_SCENE_NATIVE_GPU_PILOT_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
