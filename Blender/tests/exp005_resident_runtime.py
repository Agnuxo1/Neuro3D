"""Frozen resident-vs-fresh comparison: immutable shared shader, raw scene GPU.

Each timed hot call still includes evaluated scene export and final readback.
No RT, batch, GPU event timings or fully GPU-resident inputs claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
import resident_frontier_gpu as resident
import shared_frontier_gpu as fresh
from exp005_chain_runtime import readback,source_fields,serialize
from exp005_chain_fixture import inputs,set_fields
from exp005_paired_cost import plan,order,check,percentile,PAIRS,WARMUPS,SHARED_REPORT_SHA
from exp005_shared_runtime import INPUT_REPORT_SHA


def resident_order(index):
    return tuple('fresh' if n=='repeated' else 'resident' for n in order(index))


def summary(rows):
    if len(rows)!=PAIRS*2: raise ValueError('complete resident paired measurements required')
    ratios=[]; result={}
    for index in range(PAIRS):
        pair=rows[index*2:index*2+2]
        if [s['backend'] for s in pair]!=list(resident_order(index)) or any(s['pair']!=index for s in pair):
            raise ValueError('resident paired order mismatch')
        values={r['backend']:r['hot_ms'] for r in pair}
        for value in values.values(): percentile([value],.5)
        ratios.append(values['fresh']/values['resident'])
    for name in ('fresh','resident'):
        values=[s['hot_ms'] for s in rows if s['backend']==name]
        result[name]={'median_ms':percentile(values,.5),'p95_ms':percentile(values,.95),'n':len(values)}
    result['paired_fresh_over_resident']={'median':statistics.median(ratios),'raw':ratios,
        'meaning':'>1 favors residency only for this hot-call boundary; lifecycle separate'}
    return result


def main():
    import bpy
    import gpu
    from exp005_blender_gpu import schedule_exit
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--authorized-by-user',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);folder=args.report.with_suffix('')
    if not args.authorized_by_user or args.report.exists() or folder.exists(): raise ValueError('new authorized artifacts required')
    sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();root=Path(__file__).parents[2]
    manifest=args.evidence.with_suffix('.json'); shared_manifest=args.evidence.parent/'exp005_shared_native_20260930_0337.json'
    if sha(manifest)!=INPUT_REPORT_SHA or sha(shared_manifest)!=SHARED_REPORT_SHA: raise ValueError('immutable manifests changed')
    previous=json.loads(manifest.read_text());prior=json.loads(shared_manifest.read_text())
    hashes={s['file']:s['sha256'] for s in previous['scenes']}
    if len(hashes)!=12 or any(sha(args.evidence/n)!=h for n,h in hashes.items()): raise ValueError('immutable scenes changed')
    for path in (Path(fresh.__file__),fresh.SHADER):
        if sha(path)!=prior['code_sha256'][str(path.relative_to(root))]: raise ValueError('shared kernel/backend changed')
    dependencies=[Path(__file__),Path(resident.__file__),Path(fresh.__file__),fresh.SHADER,
        Path(fresh.__file__).with_name('frontier_gpu.py'),Path(fresh.__file__).with_name('frontier_inputs.py'),
        Path(fresh.__file__).with_name('gpu_geometry_probe.py')]
    dependencies += [Path(__file__).with_name(n) for n in ('exp005_blender_gpu.py','exp005_chain_runtime.py',
        'exp005_chain_fixture.py','exp005_paired_cost.py','exp005_shared_runtime.py','exp005_frontier_runtime.py',
        'exp005_scene_readback.py','exp005_triangle_oracle.py','exp005_mode_gate.py')]
    folder.mkdir();report={'passed':False,'scope':'resident raw-scene GPU ALU, NO RT/CPU tracing/matrix/result cache',
        'host_boundary':'source update/evaluated export/input checks/transfers/dispatch/sync/readback/decode; setup and oracle separate',
        'input_directory':str(args.evidence.resolve()),'input_scene_sha256':hashes,
        'code_sha256':{str(x.relative_to(root)):sha(x) for x in dependencies},'cases':[],
        'renderer':gpu.platform.renderer_get(),'backend':gpu.platform.backend_type_get(),'blender_version':bpy.app.version_string}
    def write(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    shader=None;session=None
    try:
        if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA GPU context required')
        start=time.perf_counter();shader=fresh.native_shader(gpu);report['compile_api_ms']=(time.perf_counter()-start)*1000
        for cells,label,amps in plan():
            start=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(args.evidence/f'K{cells}_base.blend'))
            reopen=(time.perf_counter()-start)*1000;scene=bpy.context.scene
            source_fields(scene,amps);expected=readback(bpy,scene)
            start=time.perf_counter();session=resident.ResidentSession(gpu,shader,expected,mode_cap=5)
            setup=(time.perf_counter()-start)*1000
            info={'cells':cells,'input':label,'reopen_ms':reopen,'resident_setup_ms':setup,
                  'warmups':[],'samples':[],'correctness_sequence':[],'invalidation':None}
            report['cases'].append(info);rows=[]
            def once(name,phase,index):
                start=time.perf_counter();source_fields(scene,amps);snapshot=readback(bpy,scene)
                if name=='fresh':
                    native,inner=fresh.dispatch(gpu,shader,snapshot,mode_cap=5);detail={'dispatch_sync_readback_ms':inner}
                else:native,detail=session.run(snapshot)
                elapsed=(time.perf_counter()-start)*1000
                start=time.perf_counter()
                if snapshot!=expected: raise ValueError('timed evaluated state differs from expected')
                metrics,oracle=check(snapshot,native,'shared',cells,amps)
                item={'backend':name,'phase':phase,'pair':index,'hot_ms':elapsed,'stages':detail,'metrics':metrics,
                      'independent_validation_ms':(time.perf_counter()-start)*1000}
                rows.append({'sample':item,'snapshot':snapshot,'gpu':native,'oracle':serialize(oracle)})
                return item
            for index in range(WARMUPS):
                for name in resident_order(index):info['warmups'].append(once(name,'warmup',index))
            for index in range(PAIRS):
                for name in resident_order(index):info['samples'].append(once(name,'measured',index))
                write(folder/f'K{cells}_{label}.json',rows);write(args.report,report)
            info['summary']=summary(info['samples'])
            # Reuse the same buffers with all independent basis and complex pair
            # inputs, plus zero: tests overwriting/stale ledger and output hazards.
            for input_label,values in list(inputs(cells+1))+[('zero',[0j]*(cells+1))]:
                source_fields(scene,values);snapshot=readback(bpy,scene);native,detail=session.run(snapshot)
                metrics,oracle=check(snapshot,native,'shared',cells,values)
                info['correctness_sequence'].append({'input':input_label,'snapshot':snapshot,'gpu':native,
                    'metrics':metrics,'stages':detail,'oracle':serialize(oracle)})
            calls=session.calls;allocations=session.allocations
            # Actual Blender property change -> evaluated readback -> reject before GPU.
            bpy.data.objects[f'c{cells-1}.r1']['phase_rad']+=.1
            changed=readback(bpy,scene)
            try:session.run(changed)
            except ValueError as exc:
                if 'scene changed' not in str(exc): raise
            else: raise ValueError('edited scene accepted by stale resident resources')
            if not session.closed or session.calls!=calls or session.allocations!=allocations or session.static or session.outputs:
                raise ValueError('invalidation must precede GPU and release retained references')
            try:session.run(expected)
            except ValueError as exc:
                if 'session is closed' not in str(exc): raise
            else: raise ValueError('invalidated session resumed silently')
            info['invalidation']={'changed_snapshot':changed,'closed':True,'no_new_dispatch':True,'calls':calls,
                                  'texture_allocations':allocations,'formula':'8 setup + 2 per resident call'}
            if allocations!=8+2*calls: raise ValueError('resident allocation bound failed')
            session=None;write(folder/f'K{cells}_{label}.json',rows);write(args.report,report)
        if any(sha(args.evidence/n)!=h for n,h in hashes.items()) or sha(manifest)!=INPUT_REPORT_SHA or sha(shared_manifest)!=SHARED_REPORT_SHA:
            raise ValueError('frozen inputs changed')
        if any(sha(root/n)!=h for n,h in report['code_sha256'].items()): raise ValueError('code changed during measurement')
        report['passed']=True;print('EXP005_RESIDENT_PASS',flush=True)
    except Exception as exc:report['error']=f'{type(exc).__name__}: {exc}';raise
    finally:
        if session is not None:session.close()
        write(args.report,report)
    shader=None
    import gc
    gc.collect();schedule_exit(bpy)


if __name__=='__main__':main()
