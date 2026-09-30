"""Preregistered paired hot-inference cost of two immutable ALU backends.

No comparison with conventional networks, RT or optical hardware. A complete
hot call includes input update, evaluated export, preflight/packing, transfers,
GPU dispatch/sync/readback and decoder. Lifecycle and validation are separate.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
import frontier_gpu as repeated
import shared_frontier_gpu as shared
from exp005_chain_runtime import readback,source_fields,analytic_check,serialize
from exp005_chain_fixture import set_fields
from exp005_frontier_runtime import parity
from exp005_shared_runtime import INPUT_REPORT_SHA,shared_parity

SHARED_REPORT_SHA='ca23f606478b3c5897c141ab80f877af5ba47aacd572bc527825ac7047c7d5b3'
WARMUPS=3
PAIRS=20


def plan():
    for cells in (3,4):
        yield cells,'basis0',[1+0j]+[0j]*cells
        yield cells,'all1',[1+0j]*(cells+1)


def order(index):
    if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<PAIRS:
        raise ValueError('bounded preregistered pair index required')
    return ('repeated','shared') if index%2==0 else ('shared','repeated')


def percentile(values,fraction):
    if not values or not 0<=fraction<=1 or any(not math.isfinite(v) or v<=0 for v in values):
        raise ValueError('finite positive measured times required')
    sorted_values=sorted(values); position=fraction*(len(values)-1); lower=math.floor(position)
    return sorted_values[lower]+(sorted_values[math.ceil(position)]-sorted_values[lower])*(position-lower)


def summarize(samples):
    if len(samples)!=PAIRS*2: raise ValueError('all paired samples required, no selection')
    ratios=[]; result={}
    for index in range(PAIRS):
        pair=samples[index*2:index*2+2]
        if [r['backend'] for r in pair]!=list(order(index)) or any(r['pair']!=index for r in pair):
            raise ValueError('preregistered AB/BA order mismatch')
        times={r['backend']:r['hot_inference_ms'] for r in pair}
        # Validate individual times even when later reporting only paired ratios.
        for value in times.values(): percentile([value],.5)
        ratios.append(times['repeated']/times['shared'])
    for name in ('repeated','shared'):
        rows=[r for r in samples if r['backend']==name]
        hot=[r['hot_inference_ms'] for r in rows]; gpu=[r['dispatch_sync_readback_ms'] for r in rows]
        result[name]={'n':len(rows),'hot_median_ms':percentile(hot,.5),'hot_p95_ms':percentile(hot,.95),
                      'dispatch_sync_readback_median_ms':percentile(gpu,.5),
                      'dispatch_sync_readback_p95_ms':percentile(gpu,.95)}
    result['paired_repeated_over_shared']={'median':statistics.median(ratios),
                 'p95':percentile(ratios,.95),'raw_ratios':ratios,
                 'meaning':'>1 favors shared for this hot-call boundary only; not end-to-end deployment'}
    return result


def check(snapshot,native,name,cells,amps):
    metrics,oracle=(shared_parity if name=='shared' else parity)(snapshot,native)
    metrics['analytic_error']=analytic_check(cells,'base',amps,native)
    return metrics,oracle


def main():
    import bpy
    import gpu
    from exp005_blender_gpu import schedule_exit
    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True); parser.add_argument('--authorized-by-user',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]); folder=args.report.with_suffix('')
    if not args.authorized_by_user or args.report.exists() or folder.exists(): raise ValueError('authorized new artifacts required')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); root=Path(__file__).parents[2]
    manifest=args.evidence.with_suffix('.json'); shared_manifest=args.evidence.parent/'exp005_shared_native_20260930_0337.json'
    if sha(manifest)!=INPUT_REPORT_SHA or sha(shared_manifest)!=SHARED_REPORT_SHA: raise ValueError('frozen manifests changed')
    previous=json.loads(manifest.read_text()); previous_shared=json.loads(shared_manifest.read_text())
    for module,prior in ((repeated,previous),(shared,previous_shared)):
        for path in (Path(module.__file__),module.SHADER):
            if sha(path)!=prior['code_sha256'][str(path.relative_to(root))]: raise ValueError('backend changed since correctness gate')
    hashes={r['file']:r['sha256'] for r in previous['scenes']}
    if len(hashes)!=12 or any(sha(args.evidence/n)!=digest for n,digest in hashes.items()): raise ValueError('frozen scenes changed')
    folder.mkdir(); report={'passed':False,'scope':'paired local hot inference of two ALU scene backends, NO RT/baseline superiority',
        'host_boundary':'source update/export/preflight/packing/transfer/dispatch/sync/readback/decoder; excludes lifecycle and oracle',
        'blender_version':bpy.app.version_string,'renderer':gpu.platform.renderer_get(),'backend':gpu.platform.backend_type_get(),
        'input_directory':str(args.evidence.resolve()),'input_scene_sha256':hashes,'pairs_per_input':PAIRS,'warmups_per_backend':WARMUPS,
        'lifecycle':{'compile_api_ms':{},'reopen_ms':{}},'cases':[],'code_sha256':{}}
    dependencies=[Path(__file__),Path(repeated.__file__),Path(shared.__file__),repeated.SHADER,shared.SHADER]
    dependencies += [Path(__file__).with_name(n) for n in ('exp005_chain_runtime.py','exp005_chain_fixture.py',
                         'exp005_frontier_runtime.py','exp005_shared_runtime.py','exp005_triangle_oracle.py','exp005_scene_readback.py','exp005_mode_gate.py')]
    dependencies += [Path(repeated.__file__).with_name(n) for n in ('frontier_inputs.py','gpu_geometry_probe.py')]
    report['code_sha256']={str(p.relative_to(root)):sha(p) for p in dependencies}
    def write(path,value): path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    shaders={}; modules={'repeated':repeated,'shared':shared}
    try:
        if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA GPU context required')
        for name,module in modules.items():
            start=time.perf_counter(); shaders[name]=module.native_shader(gpu)
            report['lifecycle']['compile_api_ms'][name]=(time.perf_counter()-start)*1000
        for cells,label,amps in plan():
            start=time.perf_counter(); bpy.ops.wm.open_mainfile(filepath=str(args.evidence/f'K{cells}_base.blend'))
            scene=bpy.context.scene; report['lifecycle']['reopen_ms'][f'K{cells}_{label}']=(time.perf_counter()-start)*1000
            expected=readback(bpy,scene); set_fields(expected,amps)
            rows=[]; info={'cells':cells,'input':label,'warmups':[],'samples':[],'summary':None}
            report['cases'].append(info)
            def once(name,phase,index):
                # The independent oracle and all artifact I/O are AFTER the clock.
                start=time.perf_counter(); source_fields(scene,amps); snapshot=readback(bpy,scene)
                native,gpu_ms=modules[name].dispatch(gpu,shaders[name],snapshot,mode_cap=5)
                hot_ms=(time.perf_counter()-start)*1000
                validation_start=time.perf_counter()
                if snapshot!=expected: raise ValueError('fresh timed readback differs from expected source/optical state')
                metrics,oracle=check(snapshot,native,name,cells,amps)
                validation_ms=(time.perf_counter()-validation_start)*1000
                item={'backend':name,'phase':phase,'pair':index,'hot_inference_ms':hot_ms,
                      'dispatch_sync_readback_ms':gpu_ms,'independent_validation_ms':validation_ms,'metrics':metrics,
                      'geometric_casts_executed':native['work']['total_casts'] if name=='shared' else sum(p['casts'] for p in native['ports'].values())}
                rows.append({'sample':item,'snapshot':snapshot,'gpu':native,'oracle':serialize(oracle)})
                return item
            for index in range(WARMUPS):
                for name in order(index): info['warmups'].append(once(name,'warmup',index))
            for index in range(PAIRS):
                for name in order(index): info['samples'].append(once(name,'measured',index))
                write(folder/f'K{cells}_{label}.json',rows); write(args.report,report)
            info['summary']=summarize(info['samples']); write(args.report,report)
        if len(report['cases'])!=4 or sum(len(r['samples']) for r in report['cases'])!=160 or sum(len(r['warmups']) for r in report['cases'])!=24:
            raise ValueError('complete preregistered counts required')
        if sha(manifest)!=INPUT_REPORT_SHA or sha(shared_manifest)!=SHARED_REPORT_SHA or any(sha(args.evidence/n)!=digest for n,digest in hashes.items()):
            raise ValueError('frozen inputs changed')
        if any(sha(p)!=report['code_sha256'][str(p.relative_to(root))] for p in dependencies): raise ValueError('code changed during measurements')
        report['passed']=True; print('EXP005_PAIRED_COST_PASS',flush=True)
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'; raise
    finally: write(args.report,report)
    shaders.clear()
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__=='__main__': main()
