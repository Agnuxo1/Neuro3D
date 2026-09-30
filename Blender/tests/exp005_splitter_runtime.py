"""Seven NEW v2 scenes: variable splitter property -> native GPU fields, not RT."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys


def main():
    import bpy
    import gpu
    sys.path.insert(0,str(Path(__file__).parent))
    from exp005_splitter_fixture import splitter_fixture,CASES
    from exp005_cascade_runtime import probes
    from exp005_cascade_bpy_paths import raycast_paths
    from exp005_scene_readback import export_snapshot
    from exp005_triangle_oracle import trace_scene
    from exp005_gpu_pack import pack_paths
    from exp005_mode_gate import validate_native_modes
    from exp005_blender_gpu import native_shader,dispatch,schedule_exit
    from exp005_runtime_smoke import write_json,key
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_by_user or args.report.exists(): raise ValueError('authorization and fresh report required')
    folder=args.evidence; folder.mkdir(parents=True,exist_ok=False)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    shader_file=Path(__file__).parents[1]/'shaders'/'exp005_variable_splitter.glsl'
    report={'passed':False,'scope':'scene-owned variable lossless splitter; CPU intersections, native GPU fields, not RT',
            'blender_version':bpy.app.version_string,'backend':gpu.platform.backend_type_get(),
            'renderer':gpu.platform.renderer_get(),'thresholds':{'complex':1e-4,'power_balance':2e-4,
            'distance_BU':1e-5,'sham':1e-12,'effect_min':1e-3},'cases':[],'scenes':{},'invalid_properties':[]}
    if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA context required')
    shader=None
    try:
        shader=native_shader(gpu,shader_file); results={}
        for case in CASES:
            fixture=splitter_fixture(case)
            bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
            scene['lambda_BU']=fixture['lambda_BU']; scene['optical_contract']=fixture['schema']
            scene['optical_object_ids']=json.dumps(list(fixture['objects'])); scene['optical_sources']=json.dumps(fixture['sources'])
            for name,record in fixture['objects'].items():
                mesh=bpy.data.meshes.new(name); mesh.from_pydata(record['vertices_world_BU'],[],record['faces']); mesh.update()
                obj=bpy.data.objects.new(name,mesh); scene.collection.objects.link(obj)
                for prop in ('kind','phase_rad','mode_origin_BU','mode_direction','power_transmittance'):
                    if prop in record: obj[prop]=record[prop]
                if case=='sham': obj.color=(.8,.2,.3,1.)
            def readback():
                bpy.context.view_layer.update()
                return export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
            before=readback(); blend=folder/f'{case}.blend'
            bpy.ops.wm.save_as_mainfile(filepath=str(blend)); bpy.ops.wm.open_mainfile(filepath=str(blend))
            supplied=readback(); scene=bpy.context.scene
            if supplied!=before: raise ValueError('save/reopen property readback differs')
            write_json(folder/f'{case}_snapshot.json',supplied)
            report['scenes'][case]={'blend_sha256':sha(blend),'readback_equal':True,
                                   'b.bs2_T':supplied['objects']['b.bs2']['power_transmittance']}
            for label,amps in probes():
                sources=json.loads(scene['optical_sources'])
                for source,amp in zip(sources,amps): source['field_reim']=[amp.real,amp.imag]
                scene['optical_sources']=json.dumps(sources); supplied=readback()
                paths,rays=raycast_paths(scene); mode=validate_native_modes(supplied,paths)
                oracle=trace_scene(supplied)
                expected={key(p):p for p in oracle['paths']}; actual={key(p):p for p in paths}
                if len(expected)!=len(oracle['paths']) or len(actual)!=len(paths) or set(expected)!=set(actual):
                    raise ValueError('full path identity/multiplicity differs')
                distance=max(abs(a['distance_BU']-b['distance_BU']) for k,p in actual.items()
                             for a,b in zip(p['hits'],expected[k]['hits']))
                packed=pack_paths(supplied,paths)
                # Selecting the v2 shader is explicit; v1 consumers fail closed on codes4/5.
                values,elapsed=dispatch(gpu,shader,packed,supports_variable_splitter=True)
                fields={p:complex(values[4*i],values[4*i+1]) for i,p in enumerate(packed.ports)}
                powers={p:values[4*i+2] for i,p in enumerate(packed.ports)}
                error=max(abs(fields[p]-oracle['fields'][p]) for p in fields)
                power_error=max(abs(powers[p]-abs(oracle['fields'][p])**2) for p in fields)
                balance=abs(sum(powers.values())-sum(abs(a)**2 for a in amps))
                record={'case':case,'probe':label,'fields':fields,'powers':powers,'input_fields':amps,
                        'complex_error':error,'power_error':power_error,'balance_error':balance,
                        'distance_error_BU':distance,'mode_preflight':mode,'rays':rays,'dispatch_sync_readback_ms':elapsed}
                results[(case,label)]=fields,powers; report['cases'].append(record)
                write_json(folder/f'{case}_{label}_paths.json',{'bpy':paths,'oracle':oracle,'report':record})
                if error>1e-4 or max(power_error,balance)>2e-4 or distance>1e-5:
                    raise ValueError('frozen v2 splitter numerical gate failed')
        report['sham_error']=max(abs(results[('T05',label)][0][p]-results[('sham',label)][0][p])
                               for label,_ in probes() for p in results[('T05',label)][0])
        ports=results[('T02','basis0')][0]
        report['T_power_effect']=max(abs(results[('T02','basis0')][1][p]-results[('T05','basis0')][1][p]) for p in ports)
        report['phase_power_effect']=max(abs(results[('T02','basis0')][1][p]-results[('phase','basis0')][1][p]) for p in ports)
        report['complementary_power_difference']=max(abs(results[('T02','basis0')][1][p]-results[('T08','basis0')][1][p]) for p in ports)
        report['complementary_field_difference']=max(abs(results[('T02','basis0')][0][p]-results[('T08','basis0')][0][p]) for p in ports)
        # Actual bpy property/readback negatives, transient; never save altered fixture.
        bpy.ops.wm.open_mainfile(filepath=str(folder/'T05.blend')); obj=bpy.context.scene.objects['b.bs2']
        for label,value in (('missing',None),('bool',True),('negative',-.01),('above_one',1.01),('nonfinite',float('nan'))):
            if value is None: del obj['power_transmittance']
            else: obj['power_transmittance']=value
            try: readback()
            except (ValueError,KeyError) as exc:
                report['invalid_properties'].append({'case':label,'rejection':f'{type(exc).__name__}: {exc}'})
            else: raise ValueError('invalid actual Blender splitter property accepted: '+label)
            obj['power_transmittance']=.5
        if (len(report['cases'])!=63 or len(report['invalid_properties'])!=5 or report['sham_error']>1e-12 or
                min(report['T_power_effect'],report['phase_power_effect'],report['complementary_field_difference'])<=1e-3 or
                report['complementary_power_difference']>2e-4):
            raise ValueError('frozen amended splitter controls failed')
        report['code_sha256']={p.name:sha(p) for p in (Path(__file__),shader_file,
            *(Path(__file__).with_name(n) for n in ('exp005_scene_readback.py','exp005_scene_properties.py','exp005_triangle_oracle.py',
                'exp005_gpu_pack.py','exp005_blender_gpu.py','exp005_splitter_fixture.py','exp005_mode_gate.py')))}
        report['passed']=True; print('EXP005_VARIABLE_SPLITTER_NATIVE_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: write_json(args.report,report)
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
