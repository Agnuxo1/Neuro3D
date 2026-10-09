"""Bounded actual installed Blender host-kill and UI optimizer recovery audit."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need
LIMITS={'worker_seconds':1500,'free_ram_before_mib':4000,'free_ram_floor_mib':2500,'owned_rss_mib':2500,'evidence_mib':256,'cpu_cores':1,'gpu':False}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_bytes((json.dumps(v,indent=2,allow_nan=False)+'\n').encode())
def validate(path,registration):
    p,h=read_json(path,262144);need(p['schema']=='optic_neuro_blender.installed_resume_profile.v2' and p['limits']==LIMITS and p['power_tolerance']==1e-11 and p['checkpoint_step']==12,'Frozen installed recovery envelope required')
    for n,pin in p['pins'].items():
        source=(ROOT/n).resolve();need(source.is_relative_to(ROOT) and source.is_file() and sha(source)==pin,'Frozen installed recovery pin mismatch:'+n)
    need(sha(Path(p['blender_executable']))==p['blender_executable_sha256'],'Frozen actual Blender executable required')
    r,rh=read_json(registration,65536)
    parent,ph=read_json(ROOT/p['frozen_parent_profile'],262144);check_registration(r,parent,ph)
    need(parent['schema']=='optic_neuro_blender.external_installed_resume_profile.v1' and p['limits']==parent['native_limits'],'Actual frozen external parent required')
    excluded={'schema','limits','blender_executable','blender_executable_sha256','frozen_parent_profile'}
    need(all(p[k]==v for k,v in parent.items() if k not in excluded) and set(p)==set(parent)|{'blender_executable','blender_executable_sha256','frozen_parent_profile'},'Only prepared executable/runtime mapping may differ from frozen parent')
    need(p['blender_executable_sha256']==parent['official_blender']['binary_sha256'],'Actual prepared Linux binary identity required')
    return p,h,rh
def main():
    import psutil,numpy as np,ctypes
    need(sys.platform.startswith('linux'),'Actual Linux subreaper controller required')
    libc=ctypes.CDLL(None,use_errno=True);libc.prctl.argtypes=[ctypes.c_int,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong];libc.prctl.restype=ctypes.c_int
    need(libc.prctl(36,1,0,0,0)==0,'Controller-owned child subreaper required to observe orphan worker exit9')
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--registration',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(exist_ok=False);started=time.monotonic();owned={};peak=0.;report={'schema':'optic_neuro_blender.installed_resume_supervision.v1','status':'NOT_EXECUTED','primary_metric':None,'worker_started':False};process=None;code=3
    try:
        profile,pin,rpin=validate(a.profile,a.registration);need(psutil.virtual_memory().available/2**20>=4000,'RAM preflight rejected')
        report.update(profile_sha256=pin,registration_sha256=rpin,stages=[])
        for name in profile['pins']:
            target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copyfile(a.profile,out/'profile.json');shutil.copyfile(a.registration,out/'registration.json')
        runtime=dict(profile,archive=str((ROOT/profile['archive_relative']).resolve()));runtime_path=out/'runtime_profile.json';put(runtime_path,runtime)
        scripts=out/'isolated_scripts';config=out/'isolated_config';temporary=out/'temporary'
        for d in (scripts,config,temporary):d.mkdir()
        env=dict(os.environ,BLENDER_USER_SCRIPTS=str(scripts),BLENDER_USER_CONFIG=str(config),TEMP=str(temporary),TMP=str(temporary),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        original=None
        for mode in ('BASELINE','PAUSE','RESUME'):
            folder=out/mode.lower();command=[profile['blender_executable'],'--background','--factory-startup','--disable-autoexec','--threads','1','-noaudio','--python-exit-code','3','--python',str(ROOT/profile['worker']),'--','--profile',str(runtime_path),'--out',str(folder),'--mode',mode]
            if original is not None and mode=='RESUME':command+=['--original',str(original)]
            t=time.monotonic();host_killed=False;ready=None;child=None
            with (out/(mode.lower()+'.stdout')).open('xb') as stream:
                process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name=='nt' else 0)
                host=psutil.Process(process.pid);host.cpu_affinity([psutil.Process().cpu_affinity()[0]]);owned[host.pid]=host;report['worker_started']=True
                while process.poll() is None:
                    try:
                        for c in host.children(recursive=True):owned[c.pid]=c
                    except psutil.NoSuchProcess:
                        break
                    total=0
                    for c in list(owned.values()):
                        try:total+=c.memory_info().rss if c.is_running() else 0
                        except psutil.NoSuchProcess:pass
                    peak=max(peak,total/2**20)
                    need(time.monotonic()-started<=1500,'Installed recovery overall deadline')
                    need(total/2**20<=2500 and psutil.virtual_memory().available/2**20>=2500,'Owned/host RAM envelope')
                    need(sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<=256*2**20,'Evidence envelope')
                    if mode=='PAUSE' and (folder/'host_kill_ready.json').exists():
                        ready=json.loads((folder/'host_kill_ready.json').read_bytes());need(ready['host_identity']['pid']==host.pid and ready['next_step']==12,'Actual owned host/checkpoint identity required')
                        original=Path(ready['job_folder']);need(original.is_relative_to(out/'jobs') and sha(original/'training/optimizer_checkpoint.json')==ready['checkpoint_sha256'] and not (original/'result.json').exists(),'Original interrupted evidence identity required')
                        child=owned.get(ready['child_identity']['pid']);need(child is not None and child.is_running(),'Actual tracked owned descendant required')
                        process.kill();process.wait(timeout=5);host_killed=True
                        # Do not kill the child: its installed owner-loss guard must stop it.
                        until=time.monotonic()+10
                        while child.is_running() and time.monotonic()<until:
                            try:child.wait(timeout=.2)
                            except psutil.TimeoutExpired:pass
                        try:child_exit=child.wait(timeout=.2)
                        except psutil.TimeoutExpired:raise ValueError('Owned child remained orphaned after actual host kill')
                        need(child_exit==9,'Installed child must self-stop with owner-loss exit9')
                        need(sha(original/'training/optimizer_checkpoint.json')==ready['checkpoint_sha256'] and not (original/'result.json').exists(),'Atomic interrupted checkpoint preserved/no complete result')
                        break
                    time.sleep(.2)
                process.wait(timeout=5)
            stage={'mode':mode,'seconds':time.monotonic()-t,'host_exit_code':process.returncode,'owned_host_killed':host_killed}
            if mode=='PAUSE':stage.update(child_self_exit_code=child_exit,original_interrupted_folder=str(original),checkpoint_sha256=ready['checkpoint_sha256']);need(host_killed,'Actual host interruption required')
            else:
                need(process.returncode==0,'Installed owner did not complete:'+mode);stage['result']=json.loads((folder/'result.json').read_bytes());need(stage['result']['status']=='PASS','Installed owner result gate')
            report['stages'].append(stage);put(out/'progress.json',report)
        baseline=Path(report['stages'][0]['result']['job_folder']);resumed=Path(report['stages'][2]['result']['job_folder'])
        before=json.loads((baseline/'result.json').read_bytes());after=json.loads((resumed/'result.json').read_bytes())
        b=[json.loads(line) for line in (baseline/'training/progress.jsonl').read_text().splitlines()];r=[json.loads(line) for line in (resumed/'training/progress.jsonl').read_text().splitlines()]
        need(len(b)==len(r)==61 and all(x['step']==y['step'] and x['deltas_BU']==y['deltas_BU'] and float(x['train_loss']).hex()==float(y['train_loss']).hex() for x,y in zip(b,r)),'All61 resumed optimizer coordinates/loss exactly equal baseline')
        difference=float(np.max(np.abs(np.asarray(before['all150_native_powers'])-np.asarray(after['all150_native_powers']))));need(difference==0 and before['all150_predictions']==after['all150_predictions'],'All150 resumed native outputs exactly equal baseline')
        need(after['training']['test_correct']==27 and after['training']['recovery']['resume_step']==12,'Declared fixed inference/recovery result')
        need(len(report['stages'][2]['result']['checks'])==5 and all(x['pass'] for x in report['stages'][2]['result']['checks']),'All installed stale/corrupt/replay/apply/save controls required')
        validate(a.profile,a.registration)
        report.update(status='VALID_INSTALLED_BLENDER_HOST_RECOVERY',primary_metric=1,result_collected=True,all61_optimizer_states_exact=True,all150_native_predictions_exact=True,all150_native_power_difference=difference,test_correct=27,owned_host_killed_at_step=12,owned_child_self_exit_code=9,full_host_power_loss_durability_verified=False,scope='Actual installed0.1.3 background Blender owner killed atatomiccheckpoint12; owned child self-stops, fresh host installed Resumeoperator provesoriginalfamily/replaysprefix/restoresAdam,all61coordinates/loss and150nativepowers/predictions exact,stale/truncated/fourforgedcontrols andapply/save/reopen. CPUworkflow, notphysicaldevice/graphicsGPUtraining/fullmachinepowerloss orhumanusability.');code=0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT' if report['worker_started'] else 'NOT_EXECUTED',failure_type=type(exc).__name__)
        if isinstance(exc,(ValueError,RuntimeError)):report['reason']=str(exc)
    finally:
        for c in reversed(list(owned.values())):
            try:
                if c.is_running():c.kill();c.wait(timeout=5)
            except (psutil.NoSuchProcess,psutil.TimeoutExpired):pass
        report.update(worker_seconds=time.monotonic()-started,peak_owned_aggregate_rss_mib=peak,owned_pids=list(owned),raw_file_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and '__pycache__' not in p.parts})
        put(out/'supervisor.json',report);print(json.dumps({k:report.get(k) for k in ('status','primary_metric','worker_seconds','peak_owned_aggregate_rss_mib','reason')}),flush=True)
    return code
if __name__=='__main__':raise SystemExit(main())
