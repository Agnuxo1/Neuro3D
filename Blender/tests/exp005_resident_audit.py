"""Offline re-audit of retained resident readbacks, invalidation and paired costs."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from exp005_resident_runtime import summary,resident_order,plan,check,PAIRS,WARMUPS
from exp005_chain_fixture import inputs
from resident_frontier_gpu import static_key


def audit(path):
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report=json.loads(path.read_text());root=Path(__file__).parents[2];folder=path.with_suffix('')
    if not report['passed'] or len(report['cases'])!=4:raise ValueError('complete successful resident report required')
    if any(sha(root/n)!=h for n,h in report['code_sha256'].items()):raise ValueError('resident dependency changed')
    old=Path(report['input_directory'])
    if any(sha(old/n)!=h for n,h in report['input_scene_sha256'].items()):raise ValueError('input blend changed')
    checked_rows=0;metrics=[];output=[];dispatches=0
    for info,(cells,label,amps) in zip(report['cases'],plan()):
        if (info['cells'],info['input'])!=(cells,label):raise ValueError('resident input ordering mismatch')
        rows=json.loads((folder/f'K{cells}_{label}.json').read_text())
        if len(rows)!=46 or len(info['warmups'])!=6 or len(info['samples'])!=40:raise ValueError('complete paired counts required')
        calls=0;key=None
        def verify(snapshot,native,item,values):
            nonlocal checked_rows,key
            if [s['field_reim'] for s in snapshot['sources']]!=[[a.real,a.imag] for a in values]:raise ValueError('source fields mismatch')
            current=static_key(snapshot)
            if key is None:key=current
            if current!=key:raise ValueError('static scene changed during resident session')
            checked,oracle=check(snapshot,native,'shared',cells,values)
            if checked!=item['metrics']:raise ValueError('resident stored metrics differ from independent oracles')
            if native['work']['total_casts']!=oracle['rays']:raise ValueError('resident GPU work count mismatch')
            metrics.append(checked);checked_rows+=1
        for index,row in enumerate(rows):
            item=row['sample'];phase='warmup' if index<6 else 'measured'
            pair=index//2 if index<6 else (index-6)//2
            expected=info['warmups'][index] if index<6 else info['samples'][index-6]
            if item!=expected or item['phase']!=phase or item['pair']!=pair or item['backend']!=resident_order(pair)[index%2]:
                raise ValueError('retained resident sample order mismatch')
            verify(row['snapshot'],row['gpu'],item,amps)
            stages=item['stages']
            if stages['dispatch_sync_readback_ms']>item['hot_ms'] or item['hot_ms']<=0 or item['independent_validation_ms']<0:
                raise ValueError('resident timing boundaries inconsistent')
            if item['backend']=='resident':
                calls+=1
                if (stages['gpu_dispatches'],stages['texture_allocations'])!=(calls,8+2*calls):raise ValueError('resident counter/allocations invalid')
            dispatches+=1
        sequence=list(inputs(cells+1))+[('zero',[0j]*(cells+1))]
        if len(info['correctness_sequence'])!=len(sequence):raise ValueError('complete mutable-input sequence required')
        for row,(input_label,values) in zip(info['correctness_sequence'],sequence):
            if row['input']!=input_label:raise ValueError('basis/pair/zero order mismatch')
            verify(row['snapshot'],row['gpu'],row,values);calls+=1;dispatches+=1
            if (row['stages']['gpu_dispatches'],row['stages']['texture_allocations'])!=(calls,8+2*calls):raise ValueError('reused output dispatch/allocations invalid')
        invalid=info['invalidation'];expected=copy.deepcopy(info['correctness_sequence'][-1]['snapshot'])
        expected['objects'][f'c{cells-1}.r1']['phase_rad']+=.1
        if invalid['changed_snapshot']!=expected or static_key(expected)==key:raise ValueError('actual evaluated phase edit missing')
        if not invalid['closed'] or not invalid['no_new_dispatch'] or (invalid['calls'],invalid['texture_allocations'])!=(calls,8+2*calls):
            raise ValueError('invalidated session accepted stale state')
        statistics=summary(info['samples'])
        if statistics!=info['summary']:raise ValueError('resident paired statistics differ')
        output.append({'cells':cells,'input':label,'summary':statistics,'resident_calls':calls,
                       'resident_setup_ms':info['resident_setup_ms']})
    if (checked_rows,dispatches)!=(270,270):raise ValueError('complete 184+86 GPU readbacks required')
    return {'passed':True,'scope':'offline field/ledger/path/energy/hash/order/270readbacks; host clocks NOT independent GPU events',
        'readbacks':checked_rows,'measured_calls':160,'warmups':24,'mutable_input_calls':86,'invalidations':4,
        'max_errors':{k:max(m[k] for m in metrics if m[k] is not None) for k in metrics[0]},
        'runtime_report_sha256':sha(path),'cases':output}


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise ValueError('new audit output required')
    result=audit(args.report);args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    for case in result['cases']:print(json.dumps(case))


if __name__=='__main__':main()
