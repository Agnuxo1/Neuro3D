"""Resource-guarded native Blender save/reopen and geometry inference trial."""
import argparse,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile(path):
    p,pin=read_json(path,65536)
    need(p['schema']=='optic_neuro_blender.blender_reproduction_profile.v1','frozen Blender reproduction profile required')
    need(p['worker']=='Tools/restore_trained_geometry_in_blender_v1.py','declared worker required')
    need(p['limits']=={'worker_seconds':180,'free_ram_before_mib':4000,'free_ram_floor_mib':2500,'owned_rss_mib':1500,'evidence_mib':64,'cpu_cores':1,'gpu':False},'fixed native Blender trial resource limits required')
    for name,h in p['pins'].items():
        file=(ROOT/name).resolve();need(file.is_relative_to(ROOT) and file.is_file() and sha(file)==h,'profile pin mismatch:'+name)
    need({p['original_blend'],p['worker'],p['training_result'],p['virtual_scene'],p['training_profile'],p['network'],p['semantics'],p['contract'],p['fields'],'Tools/run_frozen_blender_reproduction_v1.py'}<=set(p['pins']),'all critical artifacts must be pinned')
    executable=Path(p['blender_executable']);need(executable.is_file() and sha(executable)==p['blender_executable_sha256'],'Blender executable identity mismatch')
    return p,pin


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--registration',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out=args.out.resolve();args.out.mkdir(exist_ok=False)
    process=None;report={'schema':'optic_neuro_blender.blender_reproduction_supervision.v1','status':'NOT_EXECUTED','worker_started':False,'result_collected':False,'primary_metric':None,'gpu_requested':False};code=3
    try:
        import psutil
        p,pin=validate_profile(args.profile);registration,rpin=read_json(args.registration,65536);check_registration(registration,p,pin)
        report.update(profile_sha256=pin,registration_sha256=rpin,preflight_free_ram_mib=psutil.virtual_memory().available/2**20)
        need(report['preflight_free_ram_mib']>=4000,'fixed host RAM preflight guard')
        for name in p['pins']:
            target=args.out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copyfile(args.profile,args.out/'profile.json');shutil.copyfile(args.registration,args.out/'registration.json')
        command=[p['blender_executable'],'-b','--factory-startup','--disable-autoexec','-t','1','-noaudio',str(ROOT/p['original_blend']),
                 '--python-exit-code','3','--python',str(ROOT/p['worker']),'--',str(args.profile.resolve()),str(args.out/'worker')]
        report['command']=command;start=time.monotonic();peak=0;stop=None
        with (args.out/'blender.log').open('xb') as stream:
            process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report['worker_started']=True;owned=psutil.Process(process.pid);owned.cpu_affinity([psutil.Process().cpu_affinity()[0]])
            while process.poll() is None:
                try:peak=max(peak,owned.memory_info().rss)
                except psutil.NoSuchProcess:break
                if time.monotonic()-start>180:stop='WORKER_DEADLINE'
                elif peak>1500*2**20:stop='OWNED_RSS_LIMIT'
                elif psutil.virtual_memory().available<2500*2**20:stop='HOST_RAM_FLOOR'
                elif sum(f.stat().st_size for f in (args.out/'worker').rglob('*') if f.is_file())>64*2**20:stop='RESULT_SIZE_LIMIT'
                if stop:process.kill();break
                time.sleep(.2)
            process.wait(timeout=5)
        report.update(worker_exit_code=process.returncode,worker_seconds=time.monotonic()-start,peak_owned_rss_mib=peak/2**20,stopped=stop)
        need(stop is None and process.returncode==0,'native execution did not complete')
        _,afterpin=validate_profile(args.profile);need(afterpin==pin and sha(args.registration)==rpin,'profile or registration changed')
        result,rhash=read_json(args.out/'worker/result.json',64*2**20)
        need(result['status']=='PASS' and result['profile_sha256']==pin and result['all150_predictions_match'] is True,'native reproduction outcome mismatch')
        report.update(status='VALID_NATIVE_BLENDER_REPRODUCTION',result_collected=True,result_sha256=rhash,primary_metric=1);code=0
    except Exception as exc:
        report['failure_type']=type(exc).__name__
        if isinstance(exc,ValueError):report['reason']=str(exc)
        if report['worker_started']:report['status']='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT'
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait(timeout=5)
        report['owned_worker_cleaned_up']=process is None or process.poll() is not None
        report['raw_file_sha256']={f.relative_to(args.out).as_posix():sha(f) for f in args.out.rglob('*') if f.is_file()}
        (args.out/'supervisor.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
        print(json.dumps({k:report.get(k) for k in ('status','worker_started','result_collected','primary_metric','worker_seconds','peak_owned_rss_mib','reason')}),flush=True)
    return code


if __name__=='__main__':raise SystemExit(main())
