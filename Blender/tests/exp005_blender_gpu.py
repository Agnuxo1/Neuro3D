"""Native Blender shader integration, CPU raycasts + GPU fields, not RT.

No import-time Blender/GPU dispatch. Use bounded hidden launcher via gpuq/guard.
"""
import argparse
import json
import math
from pathlib import Path
import struct
import sys
import time

FIELD_TOL=1e-4
POWER_TOL=2e-4
SHADER=Path(__file__).parents[1]/'shaders'/'exp005_blender_fields.glsl'


def split_double(value):
    hi=struct.unpack('<f',struct.pack('<f',value))[0]
    lo=struct.unpack('<f',struct.pack('<f',value-hi))[0]
    if not all(math.isfinite(v) for v in (hi,lo)):
        raise ValueError('finite split representation required')
    return hi,lo


def texture_data(values):
    """Split numerical representation only; no phase/coefficient/field arithmetic."""
    height=max(1,math.ceil(len(values)/256))
    hi,lo=[],[]
    for value in values:
        a,b=split_double(value); hi.append(a); lo.append(b)
    pad=height*256-len(values)
    return height,hi+[0.]*pad,lo+[0.]*pad


def flatten(value):
    if isinstance(value,(list,tuple)):
        return [x for v in value for x in flatten(v)]
    return [value]


def schedule_exit(bpy):
    """Quit only once GUI event-loop/window context exists, not during CLI setup."""
    def close():
        windows=list(bpy.context.window_manager.windows)
        if not windows:
            raise RuntimeError('No Blender window for clean shutdown')
        with bpy.context.temp_override(window=windows[0]):
            bpy.ops.wm.quit_blender()
        return None
    bpy.app.timers.register(close,first_interval=.1)


def native_shader(gpu,shader_path=SHADER):
    info=gpu.types.GPUShaderCreateInfo()
    for slot,name in enumerate(('paths_hi','paths_lo','hits_hi','hits_lo')):
        info.sampler(slot,'FLOAT_2D',name)
    info.image(0,'RGBA32F','FLOAT_2D','fields_out',qualifiers={'WRITE'})
    info.push_constant('INT','path_count'); info.push_constant('INT','port_count')
    info.push_constant('FLOAT','wavelength_hi'); info.push_constant('FLOAT','wavelength_lo')
    info.local_group_size(8,1,1)
    info.compute_source(shader_path.read_text(encoding='utf-8'))
    return gpu.shader.create_from_info(info)


def dispatch(gpu,shader,packed,*,supports_variable_splitter=False):
    allowed={0,1,2,3,4,5} if supports_variable_splitter else {0,1,2,3}
    if any(code not in allowed for code in packed.hits[2::4]):
        raise ValueError('unsupported hit code for selected native shader')
    textures=[]
    for values in (packed.paths,packed.hits):
        height,hi,lo=texture_data(values)
        for data in (hi,lo):
            textures.append(gpu.types.GPUTexture((64,height),format='RGBA32F',
                            data=gpu.types.Buffer('FLOAT',len(data),data)))
    target=gpu.types.GPUTexture((len(packed.ports),1),format='RGBA32F')
    for name,texture in zip(('paths_hi','paths_lo','hits_hi','hits_lo'),textures):
        shader.uniform_sampler(name,texture)
    shader.image('fields_out',target)
    shader.uniform_int('path_count',packed.path_count)
    shader.uniform_int('port_count',len(packed.ports))
    hi,lo=split_double(packed.wavelength)
    shader.uniform_float('wavelength_hi',hi); shader.uniform_float('wavelength_lo',lo)
    start=time.perf_counter()
    gpu.compute.dispatch(shader,math.ceil(len(packed.ports)/8),1,1)
    values=flatten(target.read().to_list())
    elapsed=(time.perf_counter()-start)*1000
    if len(values)!=4*len(packed.ports) or not all(math.isfinite(v) for v in values):
        raise ValueError('malformed/nonfinite GPU texture readback')
    return values,elapsed


def main():
    import bpy
    import gpu
    sys.path.insert(0,str(Path(__file__).parent))
    from exp005_gpu_consumer import prepare,sha
    from exp005_gpu_pack import pack_paths
    from exp005_mode_gate import validate_native_modes
    from exp005_cascade_bpy_paths import raycast_paths
    from exp005_scene_readback import export_snapshot
    from exp005_cascade_runtime import probes
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not args.authorized_by_user or args.report.exists() or not args.report.parent.is_dir():
        raise ValueError('authorization and fresh report required')
    report={'passed':False,'scope':'native Blender GPU field consumer; fresh CPU scene.ray_cast, not RT',
            'blender_version':bpy.app.version_string,'background':bpy.app.background,
            'thresholds':{'complex':FIELD_TOL,'power_balance':POWER_TOL,'sham':1e-12},'cases':[]}
    try:
        report['backend']=gpu.platform.backend_type_get()
        report['vendor']=gpu.platform.vendor_get(); report['renderer']=gpu.platform.renderer_get()
        report['driver_version']=gpu.platform.version_get()
        if 'NVIDIA' not in (report['vendor']+report['renderer']).upper():
            raise ValueError('NVIDIA context required')
        jobs,hashes=prepare(args.evidence)
        report['input_sha256']=hashes
        report['code_sha256']={p.name:sha(p) for p in (Path(__file__),SHADER,
            Path(__file__).with_name('exp005_gpu_pack.py'),Path(__file__).with_name('exp005_cascade_bpy_paths.py'),
            Path(__file__).with_name('exp005_mode_gate.py'))}
        shader=native_shader(gpu)
        previous=None; results={}
        for case,label,amps,_,oracle,retained in jobs:
            if case!=previous:
                bpy.ops.wm.open_mainfile(filepath=str(args.evidence/f'{case}.blend'))
                bpy.context.view_layer.update()
                snapshot=export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
                frozen=json.loads((args.evidence/f'{case}_snapshot.json').read_text())
                if snapshot!=frozen: raise ValueError('reopened scene differs from frozen snapshot')
                previous=case
            # Input changes are transient, never saved to the frozen .blend files.
            sources=json.loads(bpy.context.scene['optical_sources'])
            for source,amp in zip(sources,amps): source['field_reim']=[amp.real,amp.imag]
            bpy.context.scene['optical_sources']=json.dumps(sources)
            actual=export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),view_layer=bpy.context.view_layer)
            paths,rays=raycast_paths(bpy.context.scene)
            validate_native_modes(actual,paths)
            packed=pack_paths(actual,paths)
            values,elapsed=dispatch(gpu,shader,packed)
            fields={p:complex(values[4*i],values[4*i+1]) for i,p in enumerate(packed.ports)}
            powers={p:values[4*i+2] for i,p in enumerate(packed.ports)}
            error=max(abs(fields[p]-oracle[p]) for p in fields)
            retained_error=max(abs(fields[p]-retained[p]) for p in fields)
            power_error=max(abs(powers[p]-abs(oracle[p])**2) for p in fields)
            balance=abs(sum(powers.values())-sum(abs(a)**2 for a in amps))
            internal=max(abs(powers[p]-abs(fields[p])**2) for p in fields)
            report['cases'].append({'case':case,'probe':label,'paths':len(paths),'rays':rays,
                'fields':{p:[v.real,v.imag] for p,v in fields.items()},'powers':powers,
                'oracle_complex_error':error,'retained_cpu_complex_error':retained_error,
                'oracle_power_error':power_error,'balance_error':balance,
                'internal_power_error':internal,'dispatch_sync_readback_ms':elapsed})
            results[(case,label)]=fields,powers
            if max(error,retained_error)>FIELD_TOL or max(power_error,balance)>POWER_TOL or internal>1e-6:
                raise ValueError('frozen native GPU numerical gate failed')
        report['sham_complex_error']=max(abs(results[('base',label)][0][p]-results[('sham',label)][0][p])
            for label,_ in probes() for p in results[('base',label)][0])
        report['causal_power_effects']={case:max(abs(results[(case,'basis0')][1][p]-results[('base','basis0')][1][p])
            for p in results[('base','basis0')][1]) for case in ('phase_a','phase_b','roof','lambda')}
        if report['sham_complex_error']>1e-12 or any(v<=1e-3 for v in report['causal_power_effects'].values()):
            raise ValueError('frozen native GPU causal gate failed')
        if any(sha(args.evidence/name)!=digest for name,digest in hashes.items()):
            raise ValueError('frozen input artifact modified')
        report['passed']=True
        print('EXP005_NATIVE_BLENDER_GPU_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    # Destroy Python GPU owners while Blender's graphics context still exists.
    # Keeping the shader alive across quit risks teardown after GPU shutdown.
    del shader
    import gc
    gc.collect()
    schedule_exit(bpy)


if __name__=='__main__': main()
