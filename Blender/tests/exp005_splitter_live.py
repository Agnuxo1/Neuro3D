"""Dynamic object-property updates, bounded native GPU parity, no render/RT."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    import bpy
    import gpu
    sys.path.insert(0,str(Path(__file__).parent))
    from exp005_cascade_runtime import probes
    from exp005_cascade_bpy_paths import raycast_paths
    from exp005_scene_readback import export_snapshot
    from exp005_triangle_oracle import trace_scene
    from exp005_mode_gate import validate_native_modes
    from exp005_gpu_pack import pack_paths
    from exp005_blender_gpu import native_shader,dispatch,schedule_exit
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_by_user or args.report.exists(): raise ValueError('authorization and fresh report required')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    blend=args.evidence/'T05.blend'; shader_file=Path(__file__).parents[1]/'shaders'/'exp005_variable_splitter.glsl'
    report={'passed':False,'scope':'live scene-owned T with explicit depsgraph refresh; CPU geometry/native GPU fields, not RT',
            'input_sha256':sha(blend),'cases':[],'negative_controls':[], 'backend':gpu.platform.backend_type_get(),
            'blender_version':bpy.app.version_string,'renderer':gpu.platform.renderer_get(),'thresholds':{'complex':1e-4,'power_balance':2e-4}}
    if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA context required')
    shader=None
    try:
        bpy.ops.wm.open_mainfile(filepath=str(blend)); scene=bpy.context.scene; obj=scene.objects['b.bs2']
        def readback():
            obj.update_tag()
            bpy.context.view_layer.update()
            return export_snapshot(scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
        before=readback(); shader=native_shader(gpu,shader_file); results={}
        for tau in (.2,.8,.5):
            obj['power_transmittance']=tau
            for label,amps in probes():
                sources=json.loads(scene['optical_sources'])
                for source,amp in zip(sources,amps): source['field_reim']=[amp.real,amp.imag]
                scene['optical_sources']=json.dumps(sources); actual=readback()
                if actual['objects']['b.bs2']['power_transmittance']!=tau: raise ValueError('live property readback incorrect')
                paths,_=raycast_paths(scene); validate_native_modes(actual,paths)
                oracle=trace_scene(actual); packed=pack_paths(actual,paths)
                values,elapsed=dispatch(gpu,shader,packed,supports_variable_splitter=True)
                fields={p:complex(values[4*i],values[4*i+1]) for i,p in enumerate(packed.ports)}
                powers={p:values[4*i+2] for i,p in enumerate(packed.ports)}
                error=max(abs(fields[p]-oracle['fields'][p]) for p in fields)
                power_error=max(abs(powers[p]-abs(oracle['fields'][p])**2) for p in fields)
                balance=abs(sum(powers.values())-sum(abs(a)**2 for a in amps))
                report['cases'].append({'T':tau,'probe':label,'fields':{p:[v.real,v.imag] for p,v in fields.items()},
                    'powers':powers,'complex_error':error,'power_error':power_error,'balance_error':balance,'dispatch_sync_readback_ms':elapsed})
                results[(tau,label)]=fields,powers
                if error>1e-4 or max(power_error,balance)>2e-4: raise ValueError('frozen live numerical gate failed')
        for label,value in (('missing',None),('bool',True),('negative',-.01),('above_one',1.01),('nonfinite',float('nan'))):
            if value is None: del obj['power_transmittance']
            else: obj['power_transmittance']=value
            try: readback()
            except (KeyError,ValueError) as exc:
                if label=='missing' and not isinstance(exc,KeyError): raise
                if label in ('bool','negative','above_one') and 'evaluated' in str(exc): raise
                report['negative_controls'].append({'case':label,'rejection':f'{type(exc).__name__}: {exc}'})
            else: raise ValueError('live invalid property accepted: '+label)
            obj['power_transmittance']=.5
        ports=results[(.2,'basis0')][0]
        report['T_power_effect']=max(abs(results[(.2,'basis0')][1][p]-results[(.5,'basis0')][1][p]) for p in ports)
        report['complementary_power_difference']=max(abs(results[(.2,'basis0')][1][p]-results[(.8,'basis0')][1][p]) for p in ports)
        report['complementary_field_difference']=max(abs(results[(.2,'basis0')][0][p]-results[(.8,'basis0')][0][p]) for p in ports)
        if (len(report['cases'])!=27 or len(report['negative_controls'])!=5 or report['T_power_effect']<=1e-3 or
                report['complementary_power_difference']>2e-4 or report['complementary_field_difference']<=1e-3):
            raise ValueError('frozen live update control failed')
        if sha(blend)!=report['input_sha256']: raise ValueError('frozen blend modified')
        report['code_sha256']={p.name:sha(p) for p in (Path(__file__),shader_file,Path(__file__).with_name('exp005_scene_readback.py'))}
        report['passed']=True; print('EXP005_VARIABLE_SPLITTER_LIVE_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
