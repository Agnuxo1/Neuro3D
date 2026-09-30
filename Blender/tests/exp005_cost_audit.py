"""Offline recomputation of all paired-cost readbacks and statistics."""
import argparse
import hashlib
import json
from pathlib import Path
from exp005_paired_cost import plan,order,check,summarize,WARMUPS,PAIRS


def audit(path):
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report=json.loads(path.read_text()); folder=path.with_suffix(''); root=Path(__file__).parents[2]
    if not report['passed'] or len(report['cases'])!=4: raise ValueError('complete successful preregistered report required')
    for name,digest in report['code_sha256'].items():
        if sha(root/name)!=digest: raise ValueError('runtime dependency changed')
    old=Path(report['input_directory'])
    if any(sha(old/n)!=digest for n,digest in report['input_scene_sha256'].items()): raise ValueError('input blend changed')
    output=[]; metrics=[]; readbacks=0; total_work={'repeated':0,'shared':0}
    for info,(cells,label,amps) in zip(report['cases'],plan()):
        if (info['cells'],info['input'])!=(cells,label): raise ValueError('four inputs order mismatch')
        rows=json.loads((folder/f'K{cells}_{label}.json').read_text())
        if len(rows)!=(WARMUPS+PAIRS)*2: raise ValueError('complete warmup and measured readbacks required')
        warmups=info['warmups']; samples=info['samples']
        if len(warmups)!=WARMUPS*2 or len(samples)!=PAIRS*2: raise ValueError('invalid summary counts')
        for index,row in enumerate(rows):
            item=row['sample']; expected=warmups[index] if index<WARMUPS*2 else samples[index-WARMUPS*2]
            if item!=expected: raise ValueError('report sample differs from retained readback')
            phase='warmup' if index<WARMUPS*2 else 'measured'
            pair=index//2 if phase=='warmup' else (index-WARMUPS*2)//2
            if item['phase']!=phase or item['pair']!=pair or item['backend']!=order(pair)[index%2]:
                raise ValueError('warmup/paired execution order differs')
            snapshot=row['snapshot']
            if [s['field_reim'] for s in snapshot['sources']]!=[[a.real,a.imag] for a in amps]: raise ValueError('all scene sources required')
            checked,oracle=check(snapshot,row['gpu'],item['backend'],cells,amps)
            if checked!=item['metrics']: raise ValueError('stored numerical metrics differ from independent recomputation')
            actual=oracle['rays'] if item['backend']=='shared' else oracle['rays']*(cells+1)
            if actual!=item['geometric_casts_executed']: raise ValueError('work counter mismatch')
            if item['dispatch_sync_readback_ms']>item['hot_inference_ms'] or item['independent_validation_ms']<0:
                raise ValueError('timing boundary mismatch')
            if phase=='measured': total_work[item['backend']]+=actual
            readbacks+=1; metrics.append(checked)
        summary=summarize(samples)
        if summary!=info['summary']: raise ValueError('recorded percentile/ratio summary differs')
        output.append({'cells':cells,'input':label,'summary':summary})
    return {'passed':True,'scope':'all184 readbacks and paired stats re-audited CPU; timings are host clocks, not independently measured GPU events',
            'readbacks':readbacks,'measured_calls':160,'warmups':24,
            'max_errors':{k:max(r[k] for r in metrics if r[k] is not None) for k in metrics[0]},
            'measured_work':total_work,'cases':output,'runtime_report_sha256':sha(path)}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--report',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists(): raise ValueError('new audit artifact required')
    result=audit(args.report); args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    for case in result['cases']:
        stats=case['summary']; print(json.dumps({'cells':case['cells'],'input':case['input'],
              'repeated_hot_ms':stats['repeated']['hot_median_ms'],'shared_hot_ms':stats['shared']['hot_median_ms'],
              'paired_ratio':stats['paired_repeated_over_shared']['median']}))


if __name__=='__main__': main()
