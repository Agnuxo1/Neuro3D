"""Four new pair probes against Claude's retained independent CPU tracer.

Reads peer code without modifying it. This is numerical cross-check, not
validation of that tracer's lost-ray handling, defaults or GPU runtime.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

CASES=((3,'lambda','pair02_1'),(4,'base','pair04_1'),
       (4,'phase','pair03_1'),(4,'T','pair14_1'))


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--peer',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise ValueError('new retained peer-check output required')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    spec=importlib.util.spec_from_file_location('neuro3d_peer_retained',args.peer)
    peer=importlib.util.module_from_spec(spec); spec.loader.exec_module(peer)
    report={'scope':'four pair probes against retained Claude CPU tracer; no GPU/Blender/new peer audit certification',
            'peer_code_sha256':sha(args.peer),'runtime_report_sha256':sha(args.evidence.with_suffix('.json')),
            'limits':'peer drops lost/depth rays and has optical defaults; fail-closed/paths/modality not certified',
            'checks':[],'passed':False}
    for cells,case,label in CASES:
        rows=json.loads((args.evidence/f'K{cells}_{case}.json').read_text())
        row=next(r for r in rows if r['probe']==label); snapshot=row['snapshot']; expected={p:0j for p in row['gpu']['ports']}
        for source in snapshot['sources']:
            if source['field_reim']==[0,0]: continue
            traced=peer.trace(snapshot,source)
            if not set(traced)<=set(expected): raise ValueError('peer emitted unknown port')
            for port,field in traced.items(): expected[port]+=field
        error=max(abs(complex(*row['gpu']['ports'][p]['field_reim'])-f) for p,f in expected.items())
        report['checks'].append({'cells':cells,'case':case,'probe':label,'complex_error':error,
                                'peer_fields':{p:[f.real,f.imag] for p,f in expected.items()}})
        if error>1e-4: raise ValueError('independent peer pair complex gate failed')
    report['passed']=True
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'pairs':len(report['checks']),
                      'max_error':max(r['complex_error'] for r in report['checks']),
                      'peer_code_sha256':report['peer_code_sha256']}))


if __name__=='__main__': main()
