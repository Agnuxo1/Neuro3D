"""Recompute shared-frontier gates offline; no GPU/Blender or timing claims."""
import argparse
import hashlib
import json
from pathlib import Path
from exp005_shared_runtime import INPUT_REPORT_SHA,shared_parity
from exp005_chain_runtime import CASES,NEGATIVES,analytic_check,causal_check
from exp005_chain_fixture import inputs
from exp005_chain_audit import phase_locality


def audit(path):
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report=json.loads(path.read_text()); folder=path.with_suffix('')
    old=Path(report['input_directory'])
    if not report['passed'] or sha(old.with_suffix('.json'))!=INPUT_REPORT_SHA:
        raise ValueError('complete report and immutable original manifest required')
    root=Path(__file__).parents[2]
    for name,digest in report['code_sha256'].items():
        if sha(root/name)!=digest: raise ValueError('runtime dependency changed: '+name)
    for name,digest in report['input_scene_sha256'].items():
        if sha(old/name)!=digest: raise ValueError('input scene changed')
    metrics=[]; ledger=shared_casts=old_casts=0; effects={}; cone={}
    for cells in (3,4):
        results={}; references={}
        for case in CASES:
            rows=json.loads((folder/f'K{cells}_{case}.json').read_text())
            before=json.loads((old/f'K{cells}_{case}.json').read_text()); expected=list(inputs(cells+1))
            if len(rows)!=len(expected) or len(before)!=len(expected): raise ValueError('complete probes required')
            for row,previous,(label,amps) in zip(rows,before,expected):
                if row['probe']!=label or previous['probe']!=label or row['snapshot']!=previous['snapshot']:
                    raise ValueError('fresh shared scene probe mismatch')
                if [s['field_reim'] for s in row['snapshot']['sources']]!=[[a.real,a.imag] for a in amps]:
                    raise ValueError('scene inputs mismatch')
                native=row['gpu']; checked,oracle=shared_parity(row['snapshot'],native)
                checked['analytic_error']=analytic_check(cells,case,amps,native)
                error=max(abs(complex(*d['field_reim'])-complex(*previous['gpu']['ports'][p]['field_reim']))
                          for p,d in native['ports'].items())
                if error>1e-4: raise ValueError('previous GPU field gate failed')
                checked['previous_gpu_field_error']=error; metrics.append(checked)
                ledger+=sum(len(d['ledger']) for d in native['ports'].values())
                shared_casts+=native['work']['total_casts']
                old_casts+=sum(d['casts'] for d in previous['gpu']['ports'].values())
                results[(case,label)]=native
                if case=='base': references[label]=oracle
        effects[str(cells)]=causal_check(results,cells+1)
        local=[phase_locality(cells,results[('base',label)],results[('phase',label)],references[label]) for label,_ in inputs(cells+1)]
        cone[str(cells)]={k:sum(r[k] for r in local) for k in local[0]}
        for case,error in NEGATIVES.items():
            native=json.loads((folder/f'K{cells}_negative_{case}.json').read_text())['gpu']
            if native['valid'] or native['ports'] or len(native['errors'])!=cells+1 or set(native['errors'].values())!={error}:
                raise ValueError('all-output specific abort invalid')
            if native['work']['traversal_invocations']!=1 or native['work']['status']==0:
                raise ValueError('failed shared work metadata invalid')
    if len(metrics)!=246 or len(report['cases'])!=246 or len(report['negative_controls'])!=10:
        raise ValueError('complete frozen counts required')
    maxima={k:max(r[k] for r in metrics if r[k] is not None) for k in metrics[0]}
    return {'scope':'CPU re-audit of shared GPU readbacks; geometric work not a speed benchmark',
            'passed':True,'probes':246,'ledger_rows':ledger,'negative_controls':10,
            'max_errors':maxima,'power_effects':effects,'phase_causal_cone':cone,
            'old_repeated_geometric_casts':old_casts,'shared_geometric_casts':shared_casts,
            'logical_traversals_per_probe':1,'runtime_report_sha256':sha(path)}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--report',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists(): raise ValueError('new audit output required')
    result=audit(args.report); args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
