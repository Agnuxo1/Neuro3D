# Remedial larger-window v2 with explicit increased memory envelope.
"""Freeze/receipt and resource guards for the declared Gaussian wave family."""
import argparse,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need
LIMITS={'worker_seconds':240,'free_ram_before_mib':6144,'free_ram_floor_mib':3500,'owned_rss_mib':3000,'evidence_mib':64,'cpu_cores':1,'gpu':False}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(path):
    p,pin=read_json(path,65536)
    need(p['schema']=='optic_neuro_blender.gaussian_wave_profile.v2' and p['limits']==LIMITS,'fixed wave profile/limits required')
    need(p['worker']=='Tools/run_gaussian_wave_reference_v2.py' and p['grids']==[[1024,32],[2048,32],[4096,32],[4096,64]],'fixed wave worker/gridfamily required')
    for name,expected in p['pins'].items():
        target=(ROOT/name).resolve();need(target.is_relative_to(ROOT) and target.is_file() and sha(target)==expected,'wave sourcepin mismatch:'+name)
    need({p['worker'],'Tools/run_frozen_wave_reference_v2.py','Blender/blender_lab/wave_optics_v1.py','Tools/independent_gaussian_hankel_v1.py'}<=set(p['pins']),'critical wave sourcepins required')
    return p,pin

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--registration',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out=args.out.resolve();args.out.mkdir(exist_ok=False);process=None;code=3
    report={'schema':'optic_neuro_blender.wave_supervision.v2','status':'NOT_EXECUTED','primary_metric':None,'worker_started':False,'result_collected':False}
    try:
        import psutil
        p,pin=validate(args.profile);receipt,rpin=read_json(args.registration,65536);check_registration(receipt,p,pin)
        free=psutil.virtual_memory().available/2**20;report.update(profile_sha256=pin,registration_sha256=rpin,preflight_free_ram_mib=free)
        need(free>=LIMITS['free_ram_before_mib'],'fixed wave RAM guard')
        for name in p['pins']:
            target=args.out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copyfile(args.profile,args.out/'profile.json');shutil.copyfile(args.registration,args.out/'registration.json')
        flags=(subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS) if sys.platform=='win32' else 0
        command=[sys.executable,'-X','utf8',str(ROOT/p['worker']),'--profile',str(args.profile.resolve()),'--out',str(args.out/'worker')]
        start=time.monotonic();peak=0;stop=None
        with (args.out/'worker.stdout').open('xb') as stream:
            process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags);report['worker_started']=True
            owned=psutil.Process(process.pid);owned.cpu_affinity([psutil.Process().cpu_affinity()[0]])
            while process.poll() is None:
                try:peak=max(peak,owned.memory_info().rss)
                except psutil.NoSuchProcess:break
                if time.monotonic()-start>LIMITS['worker_seconds']:stop='WORKER_DEADLINE'
                elif peak>LIMITS['owned_rss_mib']*2**20:stop='OWNED_RSS_LIMIT'
                elif psutil.virtual_memory().available<LIMITS['free_ram_floor_mib']*2**20:stop='HOST_RAM_FLOOR'
                elif sum(f.stat().st_size for f in (args.out/'worker').rglob('*') if f.is_file())>LIMITS['evidence_mib']*2**20:stop='RESULT_SIZE_LIMIT'
                if stop:process.kill();break
                time.sleep(.2)
            process.wait(timeout=5)
        report.update(worker_seconds=time.monotonic()-start,worker_exit_code=process.returncode,peak_owned_rss_mib=peak/2**20,stopped=stop)
        need(stop is None,'wave environmental interruption')
        _,after=validate(args.profile);need(after==pin and sha(args.registration)==rpin,'wave profile/receipt changed')
        result,resultpin=read_json(args.out/'worker/result.json',64*2**20)
        need(result['schema']=='optic_neuro_blender.gaussian_wave_reference.v2' and result['status'] in ('PASS','FAIL_ONE_OR_MORE_FROZEN_GATES') and result['profile_sha256']==pin and len(result['rows'])==36 and len(result['gates'])==9,'wave frozen outcome mismatch')
        metric=1 if result['status']=='PASS' else 0;need(process.returncode==(0 if metric else 2),'wave result/exit mismatch')
        report.update(status='VALID_FROZEN_WAVE_REFERENCE_RESULT',primary_metric=metric,result_collected=True,result_sha256=resultpin);code=0
    except Exception as exc:
        report['failure_type']=type(exc).__name__
        if isinstance(exc,ValueError):report['reason']=str(exc)
        if report['worker_started']:report['status']='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT'
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait(timeout=5)
        report['owned_worker_cleaned_up']=process is None or process.poll() is not None
        report['raw_file_sha256']={f.relative_to(args.out).as_posix():sha(f) for f in args.out.rglob('*') if f.is_file()}
        (args.out/'supervisor.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
