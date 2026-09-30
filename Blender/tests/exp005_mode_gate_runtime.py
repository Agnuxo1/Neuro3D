"""Pre-dispatch modal adversaries + nine native GPU probes, not RT optics."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys


def adverse_cases(scene, paths):
    changes = []
    for label in ('alias', 'longitudinal_alias', 'inactive_zero_direction', 'offplane',
                  'output_alias', 'arrival_direction', 'offset', 'missing_hit_position'):
        s, p = copy.deepcopy(scene), copy.deepcopy(paths)
        if label in ('alias', 'longitudinal_alias'):
            s['sources'][1] = dict(s['sources'][0], id='alias', field_reim=[0, 0])
            if label == 'longitudinal_alias':
                s['sources'][1]['position_BU'] = [-2, 0, 0]
        if label == 'inactive_zero_direction': s['sources'][1]['direction'] = [0,0,0]
        if label == 'offplane': s['objects']['b.escape']['mode_origin_BU'] = [6.03125,4,0]
        if label == 'output_alias': s['objects']['alias'] = copy.deepcopy(s['objects']['b.escape'])
        if label == 'arrival_direction': p[0]['hits'][-1]['incoming_direction'] = [0,0,1]
        if label == 'offset': p[0]['reference_offset_BU'] += .03125
        if label == 'missing_hit_position': del p[0]['hits'][-1]['point_BU']
        changes.append((label, s, p))
    return changes


def main():
    import bpy
    import gpu
    sys.path.insert(0,str(Path(__file__).parent))
    from exp005_mode_gate import validate_native_modes
    from exp005_scene_readback import export_snapshot
    from exp005_cascade_bpy_paths import raycast_paths
    from exp005_cascade_runtime import probes
    from exp005_triangle_oracle import trace_scene
    from exp005_gpu_pack import pack_paths
    from exp005_blender_gpu import native_shader,dispatch,schedule_exit,SHADER
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_by_user or args.report.exists(): raise ValueError('authorization and fresh report required')
    blend=args.evidence/'base.blend'; snapshot_file=args.evidence/'base_snapshot.json'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report={'passed':False,'scope':'conservative mode preflight; fresh CPU raycasts + native GPU fields, not RT',
            'blender_version':bpy.app.version_string,'backend':gpu.platform.backend_type_get(),
            'renderer':gpu.platform.renderer_get(),'input_sha256':{p.name:sha(p) for p in (blend,snapshot_file)},
            'thresholds':{'complex':1e-4,'power_balance':2e-4},'negative_controls':[],
            'gpu_dispatches':0,'cases':[],'geometry_gate_passed':False}
    if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA context required')
    shader=None
    try:
        bpy.ops.wm.open_mainfile(filepath=str(blend))
        def readback():
            bpy.context.view_layer.update()
            return export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
        actual=readback(); frozen=json.loads(snapshot_file.read_text(encoding='utf-8'))
        if actual!=frozen: raise ValueError('frozen scene readback differs')
        paths,_=raycast_paths(bpy.context.scene)
        validate_native_modes(actual,paths)
        # Adversaries are COPIES of actual readback/hits, not saved scene mutations.
        # Neither pack nor shader compilation/dispatch happens in this loop.
        for label,s,p in adverse_cases(actual,paths):
            try: validate_native_modes(s,p)
            except (ValueError,KeyError) as exc:
                report['negative_controls'].append({'case':label,'rejection':f'{type(exc).__name__}: {exc}',
                                                    'gpu_dispatches_at_rejection':report['gpu_dispatches']})
            else: raise ValueError('adversary accepted: '+label)
        shader=native_shader(gpu)
        for label,amps in probes():
            sources=json.loads(bpy.context.scene['optical_sources'])
            for source,amp in zip(sources,amps): source['field_reim']=[amp.real,amp.imag]
            bpy.context.scene['optical_sources']=json.dumps(sources)
            supplied=readback(); paths,rays=raycast_paths(bpy.context.scene)
            mode=validate_native_modes(supplied,paths)
            oracle=trace_scene(supplied)
            packed=pack_paths(supplied,paths); values,elapsed=dispatch(gpu,shader,packed)
            report['gpu_dispatches']+=1
            fields={p:complex(values[4*i],values[4*i+1]) for i,p in enumerate(packed.ports)}
            powers={p:values[4*i+2] for i,p in enumerate(packed.ports)}
            error=max(abs(fields[p]-oracle['fields'][p]) for p in fields)
            power_error=max(abs(powers[p]-abs(oracle['fields'][p])**2) for p in fields)
            balance=abs(sum(powers.values())-sum(abs(a)**2 for a in amps))
            report['cases'].append({'probe':label,'fields':{p:[v.real,v.imag] for p,v in fields.items()},
                'powers':powers,'oracle_fields':{p:[v.real,v.imag] for p,v in oracle['fields'].items()},
                'complex_error':error,'power_error':power_error,'balance_error':balance,
                'mode_preflight':mode,'rays':rays,'dispatch_sync_readback_ms':elapsed})
            if error>1e-4 or max(power_error,balance)>2e-4: raise ValueError('frozen native numerical gate failed')
        if len(report['negative_controls'])!=8 or report['gpu_dispatches']!=9:
            raise ValueError('incomplete modal experiment')
        if any(sha(args.evidence/name)!=digest for name,digest in report['input_sha256'].items()):
            raise ValueError('frozen artifacts changed')
        report['code_sha256']={p.name:sha(p) for p in (Path(__file__),Path(__file__).with_name('exp005_mode_gate.py'),
            Path(__file__).with_name('exp005_blender_gpu.py'),Path(__file__).with_name('exp005_gpu_pack.py'),SHADER)}
        report['passed']=True; print('EXP005_MODE_PREFLIGHT_NATIVE_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally:
        args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
