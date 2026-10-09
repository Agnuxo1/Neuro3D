"""Actual owned-process interruption and fresh deterministic training restart."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need

LIMITS={'stage_seconds':300,'total_seconds':1000,'free_ram_before_mib':4000,'free_ram_floor_mib':2500,'owned_rss_mib':1500,'evidence_mib':128,'cpu_cores':1,'gpu':False}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(path,registration):
    profile,pin=read_json(path,262144);need(profile['schema']=='optic_neuro_blender.training_recovery_profile.v1' and profile['limits']==LIMITS and profile['crash_next_step']==12,'Fixed process recovery profile/envelope required')
    need(profile['worker']=='Tools/train_captured_geometry_v3.py' and profile['parity_tolerances']=={'geometry_BU':0,'loss':0,'power':1e-11},'Fixed own recovery/numeric controls required')
    for name,expected in profile['pins'].items():
        source=(ROOT/name).resolve();need(source.is_relative_to(ROOT) and source.is_file() and sha(source)==expected,'Recovery source mismatch:'+name)
    need({profile['worker'],profile['training_profile'],'Tools/run_frozen_training_recovery_v1.py','Blender/blender_lab/optimizer_checkpoint_v1.py','Blender/blender_lab/affine_family_identity_v1.py'}<=set(profile['pins']),'Critical checkpoint/proof sources required')
    record,rpin=read_json(registration,65536);check_registration(record,profile,pin)
    return profile,pin,rpin

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--registration',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();out=args.out.resolve();out.mkdir(exist_ok=False)
    report={'schema':'optic_neuro_blender.training_process_recovery_supervision.v1','status':'NOT_EXECUTED','primary_metric':None,'worker_started':False,'result_collected':False,'gpu_requested':False,'stages':[]};process=None;peak=0;begin=time.monotonic();code=3
    try:
        import psutil
        profile,pin,rpin=validate(args.profile,args.registration);report.update(profile_sha256=pin,registration_sha256=rpin,preflight_free_ram_mib=psutil.virtual_memory().available/2**20)
        need(report['preflight_free_ram_mib']>=4000,'Fixed RAM preflight guard')
        for name in profile['pins']:
            target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copyfile(args.profile,out/'profile.json');shutil.copyfile(args.registration,out/'registration.json')
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');checkpoint=out/'interrupted/optimizer_checkpoint.json';source_checkpoint_sha=None
        stages=[('uninterrupted',[]),('interrupted',['--pause-after-checkpoint-step','12']),('resumed',['--resume-checkpoint',str(checkpoint)])]
        for name,extra in stages:
            command=[sys.executable,'-X','utf8',str(ROOT/profile['worker']),'--profile',str(args.profile.resolve()),'--out',str(out/name),*extra]
            started=time.monotonic();stop=None;intentional=False
            with (out/(name+'.stdout')).open('xb') as stream:
                process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env=env,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name=='nt' else 0)
                owned=psutil.Process(process.pid);cpu_core=psutil.Process().cpu_affinity()[-1];owned.cpu_affinity([cpu_core]);report['worker_started']=True
                while process.poll() is None:
                    try:peak=max(peak,owned.memory_info().rss)
                    except psutil.NoSuchProcess:break
                    if time.monotonic()-started>300 or time.monotonic()-begin>1000:stop='DEADLINE'
                    elif peak>1500*2**20:stop='OWNED_RSS_LIMIT'
                    elif psutil.virtual_memory().available<2500*2**20:stop='RAM_FLOOR'
                    elif sum(x.stat().st_size for x in out.rglob('*') if x.is_file())>128*2**20:stop='EVIDENCE_LIMIT'
                    if stop:process.kill();break
                    ready=out/name/'crash_point_ready.json'
                    if name=='interrupted' and ready.exists():
                        signal,_=read_json(ready,65536);need(signal['next_step']==12,'Fixed crash point required')
                        doc,_=read_json(checkpoint,16*2**20);need(doc['payload']['next_step']==12 and doc['payload_sha256']==signal['checkpoint_payload_sha256'],'Committed checkpoint must precede process interruption')
                        source_checkpoint_sha=sha(checkpoint);process.kill();intentional=True;break
                    time.sleep(.2)
                process.wait(timeout=5)
            stage={'name':name,'seconds':time.monotonic()-started,'exit_code':process.returncode,'stopped':stop,'intentional_owned_process_kill':intentional,'owned_pid':process.pid,'cpu_core':cpu_core,'result_collected':name!='interrupted' and (out/name/'result.json').exists()};report['stages'].append(stage)
            need(stop is None,'Incomplete recovery stage:'+name)
            if name=='interrupted':need(intentional and process.returncode!=0 and not (out/name/'result.json').exists(),'Actual fixed own process crash/no finished scientific result required')
            else:need(process.returncode in (0,2),'Recovery worker did not finish:'+name)
        import numpy as np
        baseline,bpin=read_json(out/'uninterrupted/result.json',64*2**20);resumed,cpin=read_json(out/'resumed/result.json',64*2**20)
        need(sha(checkpoint)==source_checkpoint_sha==resumed['recovery']['checkpoint_source_sha256'],'Original crash checkpoint preserved and identified')
        need(baseline['recovery']['resume_step']==0 and resumed['recovery']['resume_step']==12 and resumed['recovery']['prefix_replay_verified'] is True,'Actual prefix replay/restoration required')
        need(len(resumed['recovery']['adversarial_controls'])==4 and all(c['rejected'] for c in resumed['recovery']['adversarial_controls']),'All four actual checkpoint adversaries required')
        histories=[[json.loads(row) for row in (out/name/'progress.jsonl').read_text().splitlines()] for name in ('uninterrupted','resumed')];need(all(len(rows)==61 for rows in histories),'All61 optimizer states required')
        delta=max(float(np.max(np.abs(np.asarray(a['deltas_BU'])-np.asarray(b['deltas_BU'])))) for a,b in zip(*histories));loss=max(abs(a['train_loss']-b['train_loss']) for a,b in zip(*histories));power=float(np.max(np.abs(np.array(baseline['observed_powers'])-np.array(resumed['observed_powers']))));predictions=int(np.sum(np.array(baseline['predictions'])==np.array(resumed['predictions'])))
        need(delta==loss==0 and power<=1e-11 and predictions==150,'Complete uninterrupted/resumed trajectory equivalence gate')
        need(baseline['status'] in ('PASS','FAIL_LOSS_DROP') and resumed['status'] in ('PASS','FAIL_LOSS_DROP'),'Complete valid training outcomes required')
        validate(args.profile,args.registration)
        report.update(status='VALID_ACTUAL_PROCESS_TRAINING_RECOVERY',primary_metric=int(baseline['status']==resumed['status']=='PASS'),result_collected=True,uninterrupted_result_sha256=bpin,resumed_result_sha256=cpin,
                      crash_checkpoint_sha256=source_checkpoint_sha,all61_geometry_delta_max_difference_BU=delta,all61_loss_max_difference=loss,final_power_max_difference=power,prediction_agreement=predictions,
                      uninterrupted_test_correct=baseline['test_correct'],resumed_test_correct=resumed['test_correct'],peak_owned_rss_mib=peak/2**20,
                      scope='Actual termination of only a newly spawned own research worker after atomic checkpoint12; fresh process repeats whole family proof and exact prefix replay, then finishes60updates. Not whole OS/power-loss/filesystem-durability or installed Blender host crash closure; all costs and invalid checkpoints retained.')
        code=0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT' if report['worker_started'] else 'NOT_EXECUTED',failure_type=type(exc).__name__)
        if isinstance(exc,ValueError):report['reason']=str(exc)
    finally:
        if process is not None and process.poll() is None:process.kill();process.wait(timeout=5)
        report['seconds']=time.monotonic()-begin;report['owned_worker_cleaned_up']=process is None or process.poll() is not None
        report['raw_file_sha256']={x.relative_to(out).as_posix():sha(x) for x in out.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
        (out/'supervisor.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps({k:report.get(k) for k in ('status','primary_metric','seconds','resumed_test_correct','reason')}),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
