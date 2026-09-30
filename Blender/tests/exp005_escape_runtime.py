"""New Blender/native-GPU escape-mode experiment; CPU intersections, not RT."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

FIELD_TOL=1e-4
POWER_TOL=2e-4
REFERENCE_TOL=2e-5


def main():
    import bpy
    import gpu
    sys.path.insert(0,str(Path(__file__).parent))
    from exp005_escape_fixture import escape_fixture,CASES,ESCAPE
    from exp005_cascade_runtime import probes
    from exp005_cascade_bpy_paths import raycast_paths
    from exp005_scene_readback import export_snapshot
    from exp005_triangle_oracle import trace_scene
    from exp005_gpu_pack import pack_paths
    from exp005_blender_gpu import native_shader,dispatch,schedule_exit
    from exp005_runtime_smoke import write_json,key
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_by_user or args.report.exists(): raise ValueError('authorization and fresh report required')
    folder=args.evidence; folder.mkdir(parents=True,exist_ok=False)
    report={'passed':False,'scope':'native GPU coherent escape ledger; CPU bpy intersections, not RT',
            'thresholds':{'complex':FIELD_TOL,'power_balance':POWER_TOL,'reference':REFERENCE_TOL},
            'blender_version':bpy.app.version_string,'backend':gpu.platform.backend_type_get(),
            'renderer':gpu.platform.renderer_get(),'cases':[],'scenes':{}}
    if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA GPU required')
    shader=None
    try:
        shader=native_shader(gpu); results={}
        for case in CASES:
            fixture=escape_fixture(case)
            bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
            scene['lambda_BU']=fixture['lambda_BU']
            scene['optical_object_ids']=json.dumps(list(fixture['objects']))
            scene['optical_sources']=json.dumps(fixture['sources'])
            for name,record in fixture['objects'].items():
                mesh=bpy.data.meshes.new(name); mesh.from_pydata(record['vertices_world_BU'],[],record['faces']); mesh.update()
                obj=bpy.data.objects.new(name,mesh); scene.collection.objects.link(obj)
                for prop in ('kind','phase_rad','mode_origin_BU','mode_direction'):
                    if prop in record: obj[prop]=record[prop]
                if case=='sham': obj.color=(.9,.1,.5,1.)
            def readback():
                bpy.context.view_layer.update()
                return export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
            before=readback(); blend=folder/f'{case}.blend'
            bpy.ops.wm.save_as_mainfile(filepath=str(blend)); bpy.ops.wm.open_mainfile(filepath=str(blend))
            snapshot=readback(); scene=bpy.context.scene
            if snapshot!=before: raise ValueError('save/reopen readback mismatch')
            write_json(folder/f'{case}_snapshot.json',snapshot)
            report['scenes'][case]={'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'readback_equal':True}
            for label,amps in probes():
                sources=json.loads(scene['optical_sources'])
                for source,amp in zip(sources,amps): source['field_reim']=[amp.real,amp.imag]
                scene['optical_sources']=json.dumps(sources)
                supplied=readback(); oracle=trace_scene(supplied)
                paths,rays=raycast_paths(scene)
                expected={key(p):p for p in oracle['paths']}; actual={key(p):p for p in paths}
                if len(expected)!=len(oracle['paths']) or len(actual)!=len(paths) or set(expected)!=set(actual):
                    raise ValueError('path identity/multiplicity mismatch')
                distance=max(abs(a['distance_BU']-b['distance_BU']) for k,p in actual.items()
                             for a,b in zip(p['hits'],expected[k]['hits']))
                packed=pack_paths(supplied,paths); values,elapsed=dispatch(gpu,shader,packed)
                fields={p:complex(values[4*i],values[4*i+1]) for i,p in enumerate(packed.ports)}
                powers={p:values[4*i+2] for i,p in enumerate(packed.ports)}
                if set(fields)!=set(oracle['fields']) or supplied['objects'][ESCAPE]['kind']!='escape':
                    raise ValueError('complete declared escape/detector channels required')
                error=max(abs(fields[p]-oracle['fields'][p]) for p in fields)
                power_error=max(abs(powers[p]-abs(oracle['fields'][p])**2) for p in fields)
                balance=abs(sum(powers.values())-sum(abs(a)**2 for a in amps))
                incoherent=sum(abs(p['field'])**2 for p in oracle['paths'] if p['terminal']==ESCAPE)
                record={'case':case,'probe':label,'fields':fields,'powers':powers,'input_fields':amps,
                        'complex_error':error,'power_error':power_error,'balance_error':balance,
                        'distance_error_BU':distance,'paths':len(paths),'rays':rays,
                        'escape_power':powers[ESCAPE],'detected_power':sum(v for p,v in powers.items() if p!=ESCAPE),
                        'incoherent_escape_negative_control':incoherent,'dispatch_sync_readback_ms':elapsed}
                report['cases'].append(record); results[(case,label)]=fields,powers
                write_json(folder/f'{case}_{label}_paths.json',{'bpy':paths,'oracle':oracle,'report':record})
                if error>FIELD_TOL or max(power_error,balance)>POWER_TOL or distance>1e-5:
                    raise ValueError('frozen escape GPU numerical gate failed')
        report['sham_error']=max(abs(results[('base',label)][0][p]-results[('sham',label)][0][p])
            for label,_ in probes() for p in results[('base',label)][0])
        report['boundary_fixed_reference_error']=max(abs(results[('base',label)][0][p]-results[('boundary_shift',label)][0][p])
            for label,_ in probes() for p in results[('base',label)][0])
        report['reference_quarterwave_error']=max(abs(results[('reference_shift',label)][0][p]-results[('base',label)][0][p]*(1j if p==ESCAPE else 1))
            for label,_ in probes() for p in results[('base',label)][0])
        report['phase_power_effect']=abs(results[('phase','basis0')][1][ESCAPE]-results[('base','basis0')][1][ESCAPE])
        report['lambda_power_effect']=abs(results[('lambda','basis0')][1][ESCAPE]-results[('base','basis0')][1][ESCAPE])
        base=report['cases'][0]
        report['incoherent_control_gap']=abs(base['incoherent_escape_negative_control']-base['escape_power'])
        # Negative geometry: remove boundary transiently, never save it over fixture.
        bpy.ops.wm.open_mainfile(filepath=str(folder/'base.blend'))
        invalid=readback()
        x,y,z=invalid['objects'][ESCAPE]['mode_origin_BU']
        invalid['objects'][ESCAPE]['mode_origin_BU']=[x+.03125,y,z]
        try: trace_scene(invalid)
        except ValueError as exc:
            if 'planar phase-reference surface' not in str(exc): raise
            report['offplane_reference_rejection']=str(exc)
        else: raise ValueError('offplane reference silently accepted')
        bpy.data.objects.remove(bpy.data.objects[ESCAPE],do_unlink=True)
        try: raycast_paths(bpy.context.scene)
        except ValueError as exc: report['missing_boundary_rejection']=str(exc)
        else: raise ValueError('lost ray silently accepted')
        if (report['sham_error']>1e-12 or max(report['boundary_fixed_reference_error'],report['reference_quarterwave_error'])>REFERENCE_TOL
                or min(report['phase_power_effect'],report['lambda_power_effect'])<=1e-3 or report['incoherent_control_gap']<=.1):
            raise ValueError('frozen escape causality/reference/negative-control gate failed')
        report['code_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (Path(__file__),Path(__file__).with_name('exp005_escape_fixture.py'),Path(__file__).with_name('exp005_blender_gpu.py'),
             Path(__file__).parents[1]/'shaders'/'exp005_blender_fields.glsl')}
        report['passed']=True; print('EXP005_ESCAPE_NATIVE_GPU_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        write_json(args.report,report)
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
