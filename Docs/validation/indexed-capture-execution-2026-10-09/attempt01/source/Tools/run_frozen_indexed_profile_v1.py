"""Run a separately frozen profile only with an actual verified registration.

Operator must verify human authorization or external receipt. Parser validation
does not authenticate its origin. No registration or IPFS ID is issued here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.audit_captured_pilot_result_v1 import audit_result,need


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_profile(path):
    profile,pin=read_json(path,65536)
    need(profile['schema']=='optic_neuro_blender.indexed_traversal_profile.v1','unknown profile schema')
    need(profile['max_rays']==4096 and profile['max_depth']==64,'declared fixed traversal limits required')
    need(profile['worker']=='Tools/trace_indexed_scene_v1.py','declared worker required')
    for name,expected in profile['pins'].items():
        source=(ROOT/name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source)==expected,'profile pin mismatch: '+name)
    need(profile['scene'] in profile['pins'] and profile['worker'] in profile['pins']
         and 'Tools/run_frozen_indexed_profile_v1.py' in profile['pins'],'missing critical pins')
    return profile,pin


def check_registration(record,profile,pin):
    need(record.get('schema')=='optic_neuro_blender.profile_registration.v1' and record.get('approved') is True,
         'actual approved registration required')
    need(record.get('profile_sha256')==pin and record.get('profile_id')==profile['profile_id'],
         'registration/profile identity mismatch')
    need(isinstance(record.get('evidence_reference'),str) and record['evidence_reference']
         and not any(s in record['evidence_reference'].upper() for s in ('SYNTHETIC','TEST_ONLY')),
         'actual evidence reference required')
    if record.get('kind')=='HUMAN_GITHUB_EXCEPTION':
        need(record.get('evidence_origin')=='DIRECT_HUMAN_USER_MESSAGE_VERIFIED_BY_OPERATOR'
             and record.get('preregId') is None and record.get('ipfsCid') is None,'human exception must disclose absent external IDs')
    elif record.get('kind')=='EXTERNAL_REGISTRATION':
        need(record.get('evidence_origin')=='EXTERNAL_REGISTRY_RECEIPT_VERIFIED_BY_OPERATOR'
             and all(isinstance(record.get(k),str) and record[k] for k in ('preregId','ipfsCid')),'external verified IDs required')
    else:
        raise ValueError('unsupported registration kind')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--registration',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args(argv)
    args.out=args.out.resolve()
    args.profile=args.profile.resolve()
    if args.registration:
        args.registration=args.registration.resolve()
    args.out.mkdir(exist_ok=False)
    report={'schema':'optic_neuro_blender.indexed_profile_supervision.v1','status':'NOT_EXECUTED',
            'worker_started':False,'result_collected':False,'primary_metric':None,'gpu_requested':False,
            'field_certified':False,'physical_optics_certified':False}
    process=None
    code=3
    try:
        import psutil
        profile,pin=check_profile(args.profile)
        report.update(profile_id=profile['profile_id'],profile_sha256=pin,
                      preflight_free_ram_mib=psutil.virtual_memory().available/2**20)
        if args.registration:
            registration,registration_pin=read_json(args.registration,65536)
            check_registration(registration,profile,pin)
            report['registration_sha256']=registration_pin
        report['registration_accepted']=args.registration is not None
        if args.preflight_only:
            report['status']='SOFTWARE_PREFLIGHT_ONLY'
            return 0
        need(args.registration is not None,'new profile registration still pending')
        need(report['preflight_free_ram_mib']>=4000,'host RAM preflight guard')
        for name in profile['pins']:
            target=args.out/'source'/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)
        shutil.copyfile(args.profile,args.out/'profile.json')
        shutil.copyfile(args.registration,args.out/'registration.json')
        command=[sys.executable,'-X','utf8',str(ROOT/profile['worker']),
                 '--scene',str(ROOT/profile['scene']),'--out',str(args.out/'result.json'),
                 '--max-rays','4096','--max-depth','64']
        report['command']=command
        start=time.monotonic()
        peak=0
        stopped=None
        flags=(subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS) if sys.platform=='win32' else 0
        with (args.out/'worker.stdout').open('xb') as log:
            process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
            report['worker_started']=True
            owned=psutil.Process(process.pid)
            owned.cpu_affinity([psutil.Process().cpu_affinity()[0]])
            while process.poll() is None:
                try:
                    peak=max(peak,owned.memory_info().rss)
                except psutil.NoSuchProcess:
                    break
                if peak>1500*2**20:
                    stopped='OWNED_PROCESS_RSS_LIMIT'
                elif psutil.virtual_memory().available<2500*2**20:
                    stopped='HOST_FREE_RAM_FLOOR'
                elif time.monotonic()-start>90:
                    stopped='WORKER_DEADLINE'
                elif (args.out/'result.json').exists() and (args.out/'result.json').stat().st_size>64*2**20:
                    stopped='RESULT_SIZE_LIMIT'
                if stopped:
                    process.kill()
                    break
                time.sleep(.1)
            process.wait(timeout=5)
        report.update(worker_seconds=time.monotonic()-start,peak_owned_rss_mib=peak/2**20,
                      worker_exit_code=process.returncode,stopped=stopped)
        need(stopped is None,'environment interrupted worker')
        _,after_pin=check_profile(args.profile)
        need(after_pin==pin and sha(args.registration)==registration_pin,'profile or registration changed')
        result,result_pin=read_json(args.out/'result.json',64*2**20)
        scene,_=read_json(ROOT/profile['scene'],8*2**20)
        report.update(result_collected=True,result_sha256=result_pin)
        need(type(result.get('rays')) is int and 0<=result['rays']<=4096 and len(result.get('paths',[]))<=4096
             and all(len(p['hits'])<=64 for p in result['paths']),'fixed output bounds exceeded')
        audit=audit_result(scene,result)
        need(process.returncode==(0 if audit['primary_metric']==1 else 2),'exit/result mismatch')
        report.update(status='VALID_SEPARATE_PROFILE_RESULT',audit=audit,primary_metric=audit['primary_metric'])
        code=0
    except Exception as exc:
        report['failure_type']=type(exc).__name__
        if isinstance(exc,ValueError):
            report['reason']=str(exc)
        if report['worker_started']:
            report['status']='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT'
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        report['owned_worker_cleaned_up']=process is None or process.poll() is not None
        report['raw_file_sha256']={p.relative_to(args.out).as_posix():sha(p) for p in args.out.rglob('*') if p.is_file()}
        (args.out/'supervisor.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        print(json.dumps({k:report.get(k) for k in ('status','worker_started','result_collected','primary_metric','reason')}))
    return code


if __name__=='__main__':
    raise SystemExit(main())
