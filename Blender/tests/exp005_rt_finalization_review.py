"""Pinned RT-CAP-005 control-flow replay with ONLY own in-memory doubles.

Never imports peer modules or executes their writers, subprocesses, telemetry,
main, core or test suite. This is not a sandbox for arbitrary peer code.
"""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT=Path(__file__).parents[2]
PEER=NEURO3D_COGNITION / 'neuro3d/rt_cap002'
PINS={ROOT/'coordinacion/respuestas/RT-CAP-005-CLAUDE.json':'51f94861ed9b9d1f2e09bf9a2a77345e62fde1e1b7ac981ddb708ced8f1f6d13',
      ROOT/'coordinacion/tareas/RT-CAP-005-CLAUDE.md':'6ea6175332c1a9fb0dd713255eec9a49fb60fc581bce1d024e05faf76659684b',
      PEER/'guard_v4.py':'cf097276e040230d4d470e4648098b507aa4bc5f03b70c0a599d5ff2c591d820',
      PEER/'test_v4.py':'108cb8ced78c131ba9593a19bad9fede033d6119688a094b3fffcd9ca8e71343',
      PEER/'test_v4_inherited.py':'955d1501eb96049623a793b6c3347a26137b3dffe2ca7c66b72512fb170dcc6b',
      PEER/'guard_v3.py':'82e9ea1b33c7a48d90bb83faa109eb2af30cf441e08a6cdd8651655a94d1a743',
      PEER/'guard_v2.py':'1786cf75803e22bf11306f6b468851f7705f2c3cdee5bc84e4e8304c1276f8b0'}


def pinned():
    hashes={};sources={}
    for p,expected in PINS.items():
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha!=expected:raise ValueError('input changed: '+str(p))
        hashes[str(p)]=sha;sources[p]=raw.decode('utf-8')
    return sources,hashes


def function(tree,name):
    found=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
    if len(found)!=1:raise ValueError('function ABI changed')
    return found[0]


def isolated_case(node,label,*,probe_bad=False,write_bad=False,status='OK',code=0):
    node=copy.deepcopy(node)
    allowed={'_envelope_probe','_fallback','_run_core','_write_envelope','repr','print','env.get'}
    if node.decorator_list:raise ValueError('unreviewed decorators')
    for n in ast.walk(node):
        if isinstance(n,(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,ast.With,ast.Lambda)):
            raise ValueError('unreviewed side effect in finalization flow')
        if isinstance(n,ast.Call) and ast.unparse(n.func) not in allowed:raise ValueError('unreviewed call')
    events=[];saved=[];fallback=[]
    def probe(path):
        events.append('probe')
        if probe_bad:raise OSError('own simulated unwritable path')
    def core(cmd,**kw):
        events.append('core_double');kw['env_out']['env']={'status':status,'child_terminated_verified':True}
        return code
    def writer(env,path):
        events.append('writer_double')
        if write_bad:raise OSError('own simulated persistence/readback failure')
        saved.append(copy.deepcopy(env))
    def recover(env):events.append('fallback_double');fallback.append(copy.deepcopy(env))
    ns={'__builtins__':{'Exception':Exception,'repr':repr},'sys':SimpleNamespace(stderr=None),
        'print':lambda *a,**k:None,'_envelope_probe':probe,'_run_core':core,'_write_envelope':writer,'_fallback':recover}
    node.name='isolated_finalization_flow'
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<reviewed pinned in-memory flow>','exec'),ns)
    rc=ns['isolated_finalization_flow'](['NO_EXECUTION'],ram_gib=1,vram_gib=1,timeout=10,
                                        deadline='NOT_A_REAL_DEADLINE',envelope_path='NO_FILE_WRITTEN')
    return {'case':label,'code':rc,'events':events,'saved_in_memory':saved,'fallback_in_memory':fallback}


def audit():
    sources,hashes=pinned();new=ast.parse(sources[PEER/'guard_v4.py']);old=ast.parse(sources[PEER/'guard_v3.py'])
    flow=function(new,'run')
    cases=[isolated_case(flow,'success'),isolated_case(flow,'unwritable_probe',probe_bad=True),
           isolated_case(flow,'successful_child_persistence_failure',write_bad=True),
           isolated_case(flow,'failed_child_saved',status='FAILED',code=4),
           isolated_case(flow,'failed_child_persistence_failure',status='FAILED',code=4,write_bad=True),
           isolated_case(flow,'timeout_saved',status='TIMEOUT',code=5),
           isolated_case(flow,'timeout_persistence_failure',status='TIMEOUT',code=5,write_bad=True),
           isolated_case(flow,'interrupt_saved',status='INTERRUPTED',code=130)]
    if [c['code'] for c in cases]!=[0,3,7,4,7,5,5,130]:raise ValueError('finalization gate mismatch')
    if cases[1]['events']!=['probe','fallback_double']:raise ValueError('blocked probe must not reach core')
    if cases[2]['fallback_in_memory'][0]['status']!='CLOSE_FAILED':raise ValueError('missing close failure')
    core_new=function(new,'_run_core');core_old=function(old,'run')
    loop_new=[n for n in ast.walk(core_new) if isinstance(n,ast.While)]
    loop_old=[n for n in ast.walk(core_old) if isinstance(n,ast.While)]
    unchanged={n:ast.dump(function(new,n))==ast.dump(function(old,n)) for n in ('bounded','_kill_own')}
    unchanged['watchdog_loop']=len(loop_new)==len(loop_old)==1 and ast.dump(loop_new[0])==ast.dump(loop_old[0])
    if not all(unchanged.values()):raise ValueError('reviewed core preservation changed')
    return {'scope':'pinned finalization decisions with own in-memory doubles; NOT disk/watchdog/child/GPU runtime',
            'input_sha256':hashes,'cases':cases,'preserved_ast':unchanged,
            'peer_writers_imports_core_and_tests_executed':False,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();r=audit()
    files=[Path(__file__),Path(__file__).with_name('test_exp005_rt_finalization.py')]
    r['own_code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'finalization_cases':len(r['cases']),'core_ast_checks':len(r['preserved_ast']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
