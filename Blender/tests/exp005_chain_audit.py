"""Offline CPU re-audit of retained K3/K4 evidence after Blender has exited.

Recomputes oracles/gates; never trusts status=passed or stored oracle values.
Does not dispatch GPU, open Blender, alter inputs or publish anything.
"""
import argparse
import hashlib
import json
from pathlib import Path
from exp005_chain_runtime import CASES,NEGATIVES,parity,analytic_check,causal_check,validate_roundtrip
from exp005_chain_fixture import chain_fixture,inputs


def phase_locality(cells,base,phase,oracle):
    """Any terminal untouched by the edited mirror must remain exactly equal.

    Uses retraced whole-scene path histories, not assumed topology/port names.
    Dark unreachable ports also count, explicitly distinguished in the result.
    """
    target=f'c{cells-1}.r1'; checked=dark=0
    for port,original in base['ports'].items():
        paths=[p for p in oracle['paths'] if p['terminal']==port]
        if any(any(h['object_id']==target for h in p['hits']) for p in paths): continue
        checked+=1; dark+=not bool(paths)
        if phase['ports'][port]!=original: raise ValueError('phase escaped its geometric causal cone')
    return {'untouched_port_probes':checked,'dark_unreachable_port_probes':dark}


def audit(path):
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report=json.loads(path.read_text()); folder=path.with_suffix('')
    if not report['passed'] or report['mode_cap']!=5 or len(report['scenes'])!=12:
        raise ValueError('complete successful runtime report required')
    root=Path(__file__).parents[2]
    for name,digest in report['code_sha256'].items():
        if sha(root/name)!=digest: raise ValueError('runtime dependency changed: '+name)
    metrics=[]; ledger=0; times=[]; effects={}; blends={}; locality={}
    for item in report['scenes']:
        p=folder/item['file']
        if sha(p)!=item['sha256']: raise ValueError('retained blend changed')
        blends[item['file']]=item['sha256']
    for cells in (3,4):
        results={}; references={}
        for case in CASES:
            snapshot=json.loads((folder/f'K{cells}_{case}_snapshot.json').read_text())
            validate_roundtrip(chain_fixture(cells,treatment=case),snapshot,snapshot)
            rows=json.loads((folder/f'K{cells}_{case}.json').read_text())
            expected=list(inputs(cells+1))
            if len(rows)!=len(expected): raise ValueError('complete retained input probes required')
            for row,(label,amps) in zip(rows,expected):
                if row['probe']!=label: raise ValueError('retained probe order mismatch')
                value=row['snapshot']
                for source,amp in zip(value['sources'],amps):
                    if source['field_reim']!=[amp.real,amp.imag]: raise ValueError('scene-owned input mismatch')
                before=dict(snapshot); before['sources']=value['sources']
                if value!=before: raise ValueError('optical state changed between retained probes')
                native=row['gpu']; checked,oracle=parity(value,native)
                checked['analytic_error']=analytic_check(cells,case,amps,native)
                metrics.append(checked); results[(case,label)]=native
                if case=='base': references[label]=oracle
                ledger+=sum(len(p['ledger']) for p in native['ports'].values())
        effects[str(cells)]=causal_check(results,cells+1)
        counts=[phase_locality(cells,results[('base',label)],results[('phase',label)],references[label])
                for label,_ in inputs(cells+1)]
        locality[str(cells)]={key:sum(row[key] for row in counts) for key in counts[0]}
        for case,error in NEGATIVES.items():
            negative=json.loads((folder/f'K{cells}_negative_{case}.json').read_text())['gpu']
            if negative['valid'] or negative['ports'] or len(negative['errors'])!=cells+1 or set(negative['errors'].values())!={error}:
                raise ValueError('retained fail-closed control invalid')
    if len(metrics)!=246 or len(report['cases'])!=246 or len(report['negative_controls'])!=10:
        raise ValueError('runtime counts differ from contract')
    maxima={name:max(m[name] for m in metrics if m[name] is not None) for name in metrics[0]}
    times=[r['dispatch_sync_readback_ms'] for r in report['cases']]
    return {'scope':'offline CPU re-audit of all246 native GPU readbacks; no new GPU run',
            'passed':True,'readbacks':len(metrics),'ledger_rows':ledger,'max_errors':maxima,
            'power_effects':effects,'phase_causal_cone':locality,'sham_exact_equal':True,'negative_controls':10,
            'dispatch_sync_readback_ms_range':[min(times),max(times)],
            'runtime_report_sha256':sha(path),'blend_sha256':blends}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True); args=parser.parse_args()
    if args.output.exists(): raise ValueError('new audit artifact required')
    result=audit(args.report)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='blend_sha256'},indent=2))


if __name__=='__main__': main()
