"""Shared-FIFO hidden native Blender graphics trial with owned resource guards."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need
LIMITS={'worker_seconds':300,'free_ram_before_mib':4000,'free_ram_floor_mib':2500,'owned_rss_mib':2000,'evidence_mib':128,'gpu_used_mib':2048,'gpu_temperature_c':80,'cpu_cores':1,'gpu':True}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def gpu_sample():
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,memory.used,temperature.gpu,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();rows=raw.splitlines();need(len(rows)==1,'Fixed single GPU required');uuid,name,used,temp,util=[v.strip() for v in rows[0].split(',')];return {'uuid':uuid,'name':name,'memory_used_mib':int(used),'temperature_c':int(temp),'utilization_percent':int(util)}

def validate(path,registration):
    profile,pin=read_json(path,262144);need(profile['schema']=='optic_neuro_blender.native_graphics_frontier_profile.v1' and profile['limits']==LIMITS,'Fixed native graphics envelope required')
    need(profile['repetitions']==3 and profile['max_states']==4096 and profile['field_tolerance']==1e-11 and profile['pixel_BU']==.25 and profile['far_BU']==64 and profile['distance_absolute_tolerance_BU']==5e-5,'Fixed graphics trials/geometry budget required')
    for name,expected in profile['pins'].items():
        source=(ROOT/name).resolve();need(source.is_relative_to(ROOT) and source.is_file() and sha(source)==expected,'Graphics pin mismatch:'+name)
    need(sha(Path(profile['blender_executable']))==profile['blender_executable_sha256'],'Actual frozen Blender executable required')
    record,rpin=read_json(registration,65536);check_registration(record,profile,pin);return profile,pin,rpin

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--registration',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();out=args.out.resolve();out.mkdir(exist_ok=False)
    process=None;peak=0;report={'schema':'optic_neuro_blender.native_graphics_frontier_supervision.v1','status':'NOT_EXECUTED','primary_metric':None,'worker_started':False,'result_collected':False,'gpu_requested':True};code=3
    try:
        import psutil
        profile,pin,rpin=validate(args.profile,args.registration);need(os.environ.get('GPUQ_HOLDER')=='1' and os.environ.get('GPUQ_NAME')==profile['queue_job_name'],'Actual shared FIFO admission required')
        report.update(profile_sha256=pin,registration_sha256=rpin,preflight_free_ram_mib=psutil.virtual_memory().available/2**20,shared_fifo_job_name=os.environ['GPUQ_NAME']);need(report['preflight_free_ram_mib']>=4000,'Fixed RAM preflight')
        sample=gpu_sample();need(sample['uuid']==profile['gpu_uuid'] and sample['name']=='NVIDIA GeForce RTX 3090','Actual frozen GPU required');report['gpu_telemetry']=[sample]
        for name in profile['pins']:
            target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copyfile(args.profile,out/'profile.json');shutil.copyfile(args.registration,out/'registration.json')
        scripts=out/'isolated_scripts';config=out/'isolated_config';scripts.mkdir();config.mkdir()
        temporary=out/'temporary';temporary.mkdir()
        env=dict(os.environ,TEMP=str(temporary),TMP=str(temporary),BLENDER_USER_SCRIPTS=str(scripts),BLENDER_USER_CONFIG=str(config),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        startup=None
        if os.name=='nt':startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=subprocess.SW_HIDE
        command=[profile['blender_executable'],'--factory-startup','--disable-autoexec','--threads','1','-noaudio','--python-exit-code','3','--python',str(ROOT/profile['worker']),'--','--profile',str(args.profile.resolve()),'--out',str(out/'worker')]
        start=time.monotonic();stop=None;next_gpu=start
        with (out/'worker.stdout').open('xb') as stream:
            process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env=env,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name=='nt' else 0)
            owned=psutil.Process(process.pid);owned.cpu_affinity([psutil.Process().cpu_affinity()[0]]);report['worker_started']=True
            while process.poll() is None:
                try:peak=max(peak,owned.memory_info().rss)
                except psutil.NoSuchProcess:break
                if time.monotonic()-start>300:stop='WORKER_DEADLINE'
                elif peak>2000*2**20:stop='OWNED_RSS_LIMIT'
                elif psutil.virtual_memory().available<2500*2**20:stop='HOST_RAM_FLOOR'
                elif sum(x.stat().st_size for x in out.rglob('*') if x.is_file())>128*2**20:stop='EVIDENCE_LIMIT'
                if time.monotonic()>=next_gpu:
                    sample=gpu_sample();report['gpu_telemetry'].append(sample);next_gpu=time.monotonic()+1
                    if sample['uuid']!=profile['gpu_uuid']:stop='GPU_IDENTITY_CHANGED'
                    elif sample['memory_used_mib']>2048:stop='GPU_TOTAL_MEMORY_LIMIT'
                    elif sample['temperature_c']>80:stop='GPU_TEMPERATURE_LIMIT'
                if stop:process.kill();break
                time.sleep(.2)
            process.wait(timeout=5)
        report.update(worker_exit_code=process.returncode,worker_seconds=time.monotonic()-start,peak_owned_rss_mib=peak/2**20,stopped=stop)
        need(stop is None,'Incomplete native graphics trial');validate(args.profile,args.registration)
        result,rpin=read_json(out/'worker/result.json',64*2**20)
        need(process.returncode==0 and result['status']=='VALID_NATIVE_GRAPHICS_FRONTIER_AUDIT' and result['profile_sha256']==pin and result['native_gpu_executed'] is True and result['gpu_geometry_readback'] is True,'Actual complete graphics geometry execution/readback required')
        need(result['source_driven_frontier'] is True and len(result['cpu_runs'])==len(result['graphics_runs'])==3,'Complete autonomous graphics and equivalent CPU construction required')
        if result['primary_metric']==1:need(result['all150_predictions_same'] is True and result['represented_terminal_paths']==17060 and all(r['states']==133 for r in result['graphics_runs']),'Complete coherent inference and paths required')
        report.update(status='VALID_FROZEN_NATIVE_GRAPHICS_FRONTIER_AUDIT',primary_metric=result['primary_metric'],result_collected=True,result_sha256=rpin);code=0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT' if report['worker_started'] else 'NOT_EXECUTED',failure_type=type(exc).__name__)
        if isinstance(exc,ValueError):report['reason']=str(exc)
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait(timeout=5)
        report['owned_worker_cleaned_up']=process is None or process.poll() is not None
        report['raw_file_sha256']={x.relative_to(out).as_posix():sha(x) for x in out.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
        (out/'supervisor.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps({k:report.get(k) for k in ('status','primary_metric','worker_seconds','peak_owned_rss_mib','reason')}),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
