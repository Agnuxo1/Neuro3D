"""Freeze a fresh bounded full-Iris job and acquire exclusive gpuq ownership."""
import argparse
from datetime import datetime,timedelta,timezone
from pathlib import Path
import json
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from Blender.benchmarks.capacity_audit import iris_native_gpu_guard_v1 as adapter
from Blender.tests import iris_native_circuit_v1 as native
base=adapter.base


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out-dir',type=Path,required=True)
    parser.add_argument('--input-manifest',type=Path,required=True);args=parser.parse_args()
    manifest=args.input_manifest.resolve();inputs=native.validate_manifest(native.read(manifest))
    out=args.out_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),Path(native.__file__),native.SHADER,manifest,
           ROOT/'Docs/IRIS_NATIVE_CIRCUIT_PROTOCOL_2026-10-08.md',
           ROOT/'Blender/tests/native_gl_compile_v1.py',ROOT/'Blender/tests/robust_first_hit_raw_gl_v1.py',
           ROOT/'Blender/tests/exp005_blender_gpu.py',
           *(ROOT/'Blender/benchmarks/capacity_audit'/p for p in (
               'iris_native_packet_v1.py','iris_native_readback_v1.py','scene_hilo_gpu_v1.py',
               'scene_hilo_transport_v1.py','oblique_exact_scalar_hilo32_CPU_v1.py')),
           ROOT/'Blender/shaders/scene_hilo_transport_v1.glsl',
           *(native.packet.packet_path(case) for case in inputs['cases']),
           *(ROOT/inputs['assets'][key+'_path'] for key in ('trained','dataset')),
           *adapter.critical_paths()]
    files=sorted(set(p.resolve() for p in files),key=base.key)
    gpu=subprocess.run([str(base.SMI),'--query-gpu=uuid','--format=csv,noheader'],check=True,capture_output=True,text=True).stdout.strip().splitlines()
    native.packet.need(len(gpu)==1,'single declared GPU')
    for path in files:
        if path.is_relative_to(ROOT):
            target=out/'source'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(path.read_bytes())
    now=datetime.now(timezone.utc);job_id=str(uuid.uuid4())
    job={'schema':'scene-hilo-gpu-job-v1','job_id':job_id,
         'authorization_context':'User 2026-10-08 authorizes sequential Neuro3D closure and GPU; execute the frozen complete Iris algebraic circuit on all 150 raw samples with phase/sham controls. No GPU triangle/physical claim.',
         'gpu_uuid':gpu[0],'issued_utc':now.isoformat(),'deadline_utc':(now+timedelta(seconds=590)).isoformat(),
         'worker':str(Path(native.__file__).resolve()),'input_manifest':str(manifest),
         'input_manifest_sha256':base.sha_file(manifest),'worker_report':str(out/'worker.json'),
         'pins':{str(p):base.sha_file(p) for p in files},'host_budget_bytes':base.GIB,
         'device_budget_bytes':2*base.GIB,'timeout_seconds':100,'cleanup_seconds':10}
    job_path=out/'job.json';base.atomic_json(job_path,job)
    command=[sys.executable,str(base.QUEUE),'run','--name',job_id,'--vram','2','--ram','6',
             '--max-wait','4','--cwd',str(ROOT),'--',sys.executable,'-I','-B',str(Path(adapter.__file__).resolve()),
             '--manifest',str(job_path),'--receipt',str(out/'guard.json')]
    result=subprocess.run(command,capture_output=True)
    (out/'guard_stdout.txt').write_bytes(result.stdout);(out/'guard_stderr.txt').write_bytes(result.stderr)
    base.atomic_json(out/'launch.json',{'schema':'neuro3d.iris_lattice.guarded_launch.v1','returncode':result.returncode,
                                      'job_id':job_id,'pin_count':len(job['pins']),'manifest_sha256':job['input_manifest_sha256']})
    print(json.dumps({'returncode':result.returncode,'out':str(out),'job_id':job_id}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
