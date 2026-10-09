"""Bounded all-channel operator analysis; normalization failures are valid outcomes."""
import argparse,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile(path):
    profile,pin=read_json(path,65536)
    need(profile['schema']=='optic_neuro_blender.global_training_family_profile.v1','declared training profile required')
    need(profile['worker']=='Tools/certify_global_training_family_v1.py' and profile['box_algorithm']=='original_center_bound_plus_native_allowance_union_initial_FD_offsets','fixed worker/steps required')
    need(profile['limits']=={'worker_seconds':120,'free_ram_before_mib':4000,'free_ram_floor_mib':2500,'owned_rss_mib':1500,'evidence_mib':64,'cpu_cores':1,'gpu':False},'fixed new profile resource limits required')
    for name,expected in profile['pins'].items():
        source=(ROOT/name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source)==expected,'profile pin mismatch:'+name)
    need({profile['training_profile'],profile['worker'],'Tools/run_frozen_global_training_family_v1.py','Blender/blender_lab/affine_family_identity_v1.py','Blender/blender_lab/affine_box_audit_v1.py','Blender/blender_lab/affine_geometry_network_v1.py'}<=set(profile['pins']),'critical sources must be pinned')
    return profile,pin


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--registration',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out=args.out.resolve();args.out.mkdir(exist_ok=False)
    process=None;report={'schema':'optic_neuro_blender.global_training_family_supervision.v1','status':'NOT_EXECUTED','worker_started':False,'result_collected':False,'primary_metric':None,'gpu_requested':False};code=3
    try:
        import psutil
        profile,pin=validate_profile(args.profile);registration,rpin=read_json(args.registration,65536);check_registration(registration,profile,pin)
        report.update(profile_sha256=pin,registration_sha256=rpin,preflight_free_ram_mib=psutil.virtual_memory().available/2**20)
        need(report['preflight_free_ram_mib']>=4000,'fixed host RAM preflight guard')
        for name in profile['pins']:
            target=args.out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copyfile(args.profile,args.out/'profile.json');shutil.copyfile(args.registration,args.out/'registration.json')
        flags=(subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS) if sys.platform=='win32' else 0
        command=[sys.executable,'-X','utf8',str(ROOT/profile['worker']),'--profile',str(args.profile.resolve()),'--out',str(args.out/'worker')]
        start=time.monotonic();peak=0;stop=None
        with (args.out/'worker.stdout').open('xb') as stream:
            process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags)
            report['worker_started']=True;owned=psutil.Process(process.pid);owned.cpu_affinity([psutil.Process().cpu_affinity()[0]])
            while process.poll() is None:
                try:peak=max(peak,owned.memory_info().rss)
                except psutil.NoSuchProcess:break
                if time.monotonic()-start>120:stop='WORKER_DEADLINE'
                elif peak>1500*2**20:stop='OWNED_RSS_LIMIT'
                elif psutil.virtual_memory().available<2500*2**20:stop='HOST_RAM_FLOOR'
                elif sum(p.stat().st_size for p in (args.out/'worker').rglob('*') if p.is_file())>64*2**20:stop='RESULT_SIZE_LIMIT'
                if stop:process.kill();break
                time.sleep(.2)
            process.wait(timeout=5)
        report.update(worker_exit_code=process.returncode,worker_seconds=time.monotonic()-start,peak_owned_rss_mib=peak/2**20,stopped=stop)
        need(stop is None,'environment interrupted trial')
        _,afterpin=validate_profile(args.profile);need(afterpin==pin and sha(args.registration)==rpin,'profile/registration changed')
        result,resultpin=read_json(args.out/'worker/certificate.json',32*2**20)
        need(result['profile_sha256']==pin and result['schema']=='optic_neuro_blender.global_training_family_certificate.v1' and result['training_profile_sha256']==profile['pins'][profile['training_profile']],'declared protocol outcome mismatch')
        metric=result['primary_metric'];need(metric in (0,1) and result['status'] in ('CERTIFIED_WHOLE_DECLARED_TRAINING_FAMILY','VALID_UNKNOWN_WHOLE_TRAINING_FAMILY'),'valid bounded outcome required')
        need(process.returncode==0,'complete secondary analysis required')
        report.update(status='VALID_FROZEN_GLOBAL_TRAINING_FAMILY_ANALYSIS',result_collected=True,result_sha256=resultpin,primary_metric=metric);code=0
    except Exception as exc:
        report['failure_type']=type(exc).__name__
        if isinstance(exc,ValueError):report['reason']=str(exc)
        if report['worker_started']:report['status']='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT'
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait(timeout=5)
        report['owned_worker_cleaned_up']=process is None or process.poll() is not None
        report['raw_file_sha256']={p.relative_to(args.out).as_posix():sha(p) for p in args.out.rglob('*') if p.is_file()}
        (args.out/'supervisor.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps({k:report.get(k) for k in ['status','primary_metric','worker_seconds','peak_owned_rss_mib','reason']}),flush=True)
    return code


if __name__=='__main__':raise SystemExit(main())
