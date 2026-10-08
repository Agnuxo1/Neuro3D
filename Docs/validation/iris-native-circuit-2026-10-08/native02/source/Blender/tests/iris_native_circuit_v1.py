"""Full frozen Iris circuit GPU worker. No CPU inference, labels or global U."""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import traceback
import uuid

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from Blender.benchmarks.capacity_audit import iris_native_packet_v1 as packet
from Blender.benchmarks.capacity_audit.iris_native_readback_v1 import validate_result
from Blender.benchmarks.capacity_audit import scene_hilo_gpu_v1 as device
from Blender.tests.native_gl_compile_v1 import compile_source
from Blender.tests.exp005_blender_gpu import schedule_exit

SHADER=ROOT/'Blender/shaders/iris_lattice_native_circuit_v1.glsl'


def read(path):
    raw=Path(path).read_bytes();packet.need(len(raw)<=16*2**20,'bounded worker input')
    def pairs(items):
        result={}
        for key,value in items:
            packet.need(key not in result,'duplicate input key');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))


def validate_manifest(job):
    packet.need(set(job)=={'schema','expected_backend','expected_renderer_contains','limits','assets','cases'},'closed circuit manifest')
    packet.need(job['schema']==packet.SCHEMA and job['expected_backend']=='OPENGL' and job['expected_renderer_contains']=='RTX 3090','fixed circuit profile')
    packet.need(job['limits']=={'samples':150,'cells':16,'modes':8,'dispatches':3,'output_row_words':128},'complete frozen network limits')
    packet.need([c['case_id'] for c in job['cases']]==['baseline','phase','sham'],'complete intervention coverage')
    for case in job['cases']:
        packet.need(set(case)=={'case_id','packet_path','packet_sha256'},'closed case record')
        packet.admit(read(packet.packet_path(case)))
    for key in ('trained','dataset'):
        path=ROOT/job['assets'][key+'_path'];packet.need(packet.sha(path)==job['assets'][key+'_sha256'],'frozen asset hash')
    return job


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-manifest',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True);parser.add_argument('--job-id',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);packet.need(str(uuid.UUID(args.job_id))==args.job_id,'canonical job UUID')
    report={'schema':'neuro3d.iris_lattice.native_report.v1','status':'FAIL','verification_passed':False,
            'job_id':args.job_id,'input_manifest_sha256':packet.sha(args.input_manifest),
            'native_gpu_executed':False,'native_gpu_execution_attempted':False,'gpu_dispatch_count':0,
            'completed_readbacks':0,'gpu_readback_records':[],'gpu_readback_sha256':None,
            'scope':{'full_scalar_circuit':True,'all_cells':16,'all_modes':8,'samples':150,
                     'GPU_input_encoding':True,'GPU_fields_powers_logits_decision':True,
                     'GPU_geometric_traversal':False,'physical_optics':False,'speed_advantage_claimed':False,
                     'cpu_inference_fallback':False},'shader_api_used':'RAW_OPENGL_CORE_IN_BLENDER_WGL','cases':[]}
    started=time.perf_counter();program=None;failure=None;hasher=hashlib.sha256()
    try:
        import bpy
        import gpu
        packet.need(not bpy.app.background,'private windowed OpenGL context required')
        report.update(device.device_profile(gpu));report.update(background=False,blender_version=bpy.app.version_string,
                                                               blender_build_hash=bpy.app.build_hash.decode('ascii'))
        bpy.context.preferences.use_preferences_save=False;bpy.context.preferences.view.use_save_prompt=False
        bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
        job=validate_manifest(read(args.input_manifest))
        dependencies=[Path(__file__),SHADER,ROOT/'Blender/tests/native_gl_compile_v1.py',
                      ROOT/'Blender/tests/robust_first_hit_raw_gl_v1.py',Path(packet.__file__),
                      ROOT/'Blender/benchmarks/capacity_audit/iris_native_readback_v1.py',Path(device.__file__),
                      ROOT/'Blender/benchmarks/capacity_audit/scene_hilo_transport_v1.py',
                      ROOT/'Blender/benchmarks/capacity_audit/oblique_exact_scalar_hilo32_CPU_v1.py',
                      ROOT/'Blender/tests/exp005_blender_gpu.py']
        report['code_sha256']={p.relative_to(ROOT).as_posix():packet.sha(p) for p in dependencies}
        report['compilation']={};program=compile_source(SHADER.read_text(encoding='utf-8'),report['compilation'])
        for case in job['cases']:
            value=read(packet.packet_path(case));wire=packet.admit(value)
            nonce=int.from_bytes(hashlib.sha256((args.job_id+'/'+case['case_id']).encode()).digest()[:4],'little')&0x7fffffff
            packet.need(nonce!=0,'nonzero fresh nonce')
            report['gpu_dispatch_count']+=1;report['native_gpu_execution_attempted']=True
            result=program.dispatch(wire,{'nonce':nonce},output_words=packet.SAMPLES*packet.ROW_WORDS)
            report['native_gpu_executed']=True
            echo=struct.pack('<%dI'%len(result['echo']),*result['echo']);raw=struct.pack('<%dI'%len(result['result']),*result['result'])
            record={'case_id':case['case_id'],'nonce':nonce,'input_echo_hex':echo.hex(),'result_hex':raw.hex()}
            report['gpu_readback_records'].append(record);report['completed_readbacks']=len(report['gpu_readback_records'])
            hasher.update(echo);hasher.update(raw);report['gpu_readback_sha256']=hasher.hexdigest()
            # Raw bytes are retained before typed/numeric evaluation, including failures.
            packet.need(echo==wire+bytes(len(echo)-len(wire)),'native exact input echo')
            rows=validate_result(raw,nonce)
            report['cases'].append({'case_id':case['case_id'],'rows':rows,'synchronization':result['synchronization'],
                'allocation_upload_bind_ms':result['allocation_upload_bind_ms'],
                'dispatch_sync_readback_host_validation_ms':result['dispatch_sync_readback_host_validation_ms'],
                'resource_payload_bytes':result['resource_payload_bytes']})
        packet.need(report['gpu_dispatch_count']==report['completed_readbacks']==3,'complete native cases')
        packet.need(packet.sha(args.input_manifest)==report['input_manifest_sha256'] and all(packet.sha(ROOT/k)==v for k,v in report['code_sha256'].items()),'immutable worker inputs/code')
        validate_manifest(read(args.input_manifest));report.update(status='PASS',verification_passed=True)
    except BaseException as error:
        failure=error;report.update(error=type(error).__name__+': '+str(error),traceback=traceback.format_exc())
    finally:
        if program is not None: program.close()
        gc.collect();report['total_seconds']=time.perf_counter()-started
        packet.need(not args.report.exists() and args.report.parent.is_dir(),'fresh worker output')
        with args.report.open('xb') as stream: stream.write((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    if failure is not None: raise failure
    print('IRIS_FULL_NATIVE_CIRCUIT_READBACK_PASS',report['gpu_readback_sha256'],flush=True);schedule_exit(bpy)


if __name__=='__main__': main()
