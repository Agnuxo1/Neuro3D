"""Read-only saved scenes -> native shared GPU frontier -> independent gates."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from shared_frontier_gpu import dispatch,native_shader,SHADER
from exp005_chain_runtime import CASES,NEGATIVES,readback,source_fields,analytic_check,causal_check,serialize,validate_roundtrip
from exp005_chain_fixture import inputs,chain_fixture
from exp005_frontier_runtime import parity
from exp005_chain_audit import phase_locality

INPUT_REPORT_SHA='c101286137e59ceb47918e0913f112c3ca1a0e9733610b662be7d2d63dd961f4'


def shared_parity(snapshot,native):
    metrics,oracle=parity(snapshot,native)
    work=native['work']
    if (work['traversal_invocations']!=1 or work['status']!=0 or
            work['total_casts']!=oracle['rays'] or work['total_terminal_paths']!=len(oracle['paths'])):
        raise ValueError('shared traversal count differs from independent full-scene trace')
    return metrics,oracle


def main():
    import bpy
    import gpu
    from exp005_blender_gpu import schedule_exit
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]); folder=args.report.with_suffix('')
    if not args.authorized_by_user or args.report.exists() or folder.exists(): raise ValueError('fresh authorized output required')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    previous_report=args.evidence.with_suffix('.json')
    if sha(previous_report)!=INPUT_REPORT_SHA: raise ValueError('frozen scene manifest changed')
    previous=json.loads(previous_report.read_text()); folder.mkdir()
    hashes={item['file']:item['sha256'] for item in previous['scenes']}
    if len(hashes)!=12 or any(sha(args.evidence/name)!=digest for name,digest in hashes.items()):
        raise ValueError('twelve frozen scene hashes required')
    dependencies=[Path(__file__),SHADER,Path(__file__).with_name('exp005_chain_runtime.py'),
                  Path(__file__).with_name('exp005_chain_audit.py'),Path(__file__).with_name('exp005_chain_fixture.py'),
                  Path(__file__).with_name('exp005_frontier_runtime.py'),Path(__file__).with_name('exp005_triangle_oracle.py'),
                  Path(__file__).with_name('exp005_scene_readback.py'),Path(__file__).with_name('exp005_mode_gate.py')]
    dependencies += [Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/name
                     for name in ('shared_frontier_gpu.py','frontier_gpu.py','frontier_inputs.py','gpu_geometry_probe.py')]
    report={'passed':False,'scope':'one shared scalar GPU ALU traversal for all ports inside Blender; not RT/BVH',
            'host_scope':'export/preflight/transfer/readback/validation remain CPU',
            'input_report_sha256':INPUT_REPORT_SHA,'input_scene_sha256':hashes,'input_directory':str(args.evidence.resolve()),
            'blender_version':bpy.app.version_string,'renderer':gpu.platform.renderer_get(),'backend':gpu.platform.backend_type_get(),
            'cases':[],'negative_controls':[],'phase_causal_cone':{},'power_effects':{},
            'thresholds':{'field_ledger_analytic_previous':1e-4,'power_balance':2e-4,'length_BU':1e-5,'causal_min':1e-3},
            'code_sha256':{str(p.relative_to(Path(__file__).parents[2])):sha(p) for p in dependencies}}
    def write(path,value): path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    shader=None
    try:
        if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA GPU context required')
        shader=native_shader(gpu)
        for cells in (3,4):
            results={}; references={}
            for case in CASES:
                bpy.ops.wm.open_mainfile(filepath=str(args.evidence/f'K{cells}_{case}.blend')); scene=bpy.context.scene
                snapshot=readback(bpy,scene)
                retained=json.loads((args.evidence/f'K{cells}_{case}_snapshot.json').read_text())
                validate_roundtrip(chain_fixture(cells,treatment=case),retained,snapshot)
                prior=json.loads((args.evidence/f'K{cells}_{case}.json').read_text()); rows=[]
                for index,(label,amps) in enumerate(inputs(cells+1)):
                    source_fields(scene,amps); snapshot=readback(bpy,scene)
                    if prior[index]['probe']!=label or snapshot!=prior[index]['snapshot']:
                        raise ValueError('fresh readback differs from frozen previous probe')
                    native,elapsed=dispatch(gpu,shader,snapshot,mode_cap=5)
                    metrics,oracle=shared_parity(snapshot,native)
                    metrics['analytic_error']=analytic_check(cells,case,amps,native)
                    metrics['previous_gpu_field_error']=max(abs(complex(*data['field_reim'])-
                           complex(*prior[index]['gpu']['ports'][p]['field_reim'])) for p,data in native['ports'].items())
                    if metrics['previous_gpu_field_error']>1e-4: raise ValueError('previous GPU field parity failed')
                    results[(case,label)]=native
                    if case=='base': references[label]=oracle
                    report['cases'].append({'cells':cells,'case':case,'probe':label,'metrics':metrics,
                                             'work':native['work'],'dispatch_sync_readback_ms':elapsed})
                    rows.append({'probe':label,'snapshot':snapshot,'gpu':native,'oracle':serialize(oracle)})
                    write(folder/f'K{cells}_{case}.json',rows)
                write(args.report,report)
            report['power_effects'][str(cells)]=causal_check(results,cells+1)
            local=[phase_locality(cells,results[('base',label)],results[('phase',label)],references[label]) for label,_ in inputs(cells+1)]
            report['phase_causal_cone'][str(cells)]={k:sum(row[k] for row in local) for k in local[0]}
            for case,expected in NEGATIVES.items():
                bpy.ops.wm.open_mainfile(filepath=str(args.evidence/f'K{cells}_base.blend')); scene=bpy.context.scene
                source_fields(scene,[1+0j]+[0j]*cells); target=f'c{cells-1}.r1'; options={'mode_cap':5}
                if case=='missing_mirror':
                    bpy.data.objects.remove(scene.objects[target],do_unlink=True)
                    scene['optical_object_ids']=json.dumps([n for n in json.loads(scene['optical_object_ids']) if n!=target])
                if case=='overlap':
                    obj=scene.objects[target].copy(); obj.data=obj.data.copy(); obj.name='alias.r1'; scene.collection.objects.link(obj)
                    scene['optical_object_ids']=json.dumps(json.loads(scene['optical_object_ids'])+[obj.name])
                if case=='direction': scene.objects[f'c{cells-1}.Y']['mode_direction']=[0.,-1.,0.]
                if case=='step': options['max_steps']=1
                if case=='depth': options['max_depth']=1
                snapshot=readback(bpy,scene); native,elapsed=dispatch(gpu,shader,snapshot,**options)
                write(folder/f'K{cells}_negative_{case}.json',{'snapshot':snapshot,'options':options,'gpu':native})
                if native['valid'] or len(native['errors'])!=cells+1 or set(native['errors'].values())!={expected}:
                    raise ValueError('all-port specific shared GPU abort absent: '+case)
                report['negative_controls'].append({'cells':cells,'case':case,'errors':native['errors'],'work':native['work']})
        if len(report['cases'])!=246 or len(report['negative_controls'])!=10: raise ValueError('complete frozen counts required')
        if sha(previous_report)!=INPUT_REPORT_SHA or any(sha(args.evidence/name)!=digest for name,digest in hashes.items()):
            raise ValueError('frozen input modified')
        if any(sha(p)!=report['code_sha256'][str(p.relative_to(Path(__file__).parents[2]))] for p in dependencies):
            raise ValueError('runtime code changed')
        report['passed']=True; print('EXP005_SHARED_NATIVE_GPU_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: write(args.report,report)
    del shader
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
