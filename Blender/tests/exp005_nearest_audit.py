"""CPU re-audit of retained native nearest readbacks; never launches Blender/GPU."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from exp005_nearest_runtime import raw_cases, require_status
from exp005_paired_cost import plan, check
from exp005_shared_runtime import shared_parity
from exp005_chain_runtime import serialize


def audit(report):
    if not report['passed']: raise ValueError('runtime did not pass')
    raw = report['raw_cases']; historical = report['legacy_CE3']; real = report['real_cases']
    expected = list(raw_cases())
    if (len(raw), len(historical), len(real)) != (21, 6, 4):
        raise ValueError('all preregistered dispatches required')
    metrics = []
    for row, (label, snapshot, status) in zip(raw, expected):
        # JSON converts tuples to lists, without changing numeric raw geometry.
        if row['label'] != label or row['snapshot'] != json.loads(json.dumps(snapshot)):
            raise ValueError('raw fixture or order changed')
        if row['expected_status'] != status: raise ValueError('status contract changed')
        require_status(row['gpu'], status)
        if not status:
            m, oracle = shared_parity(row['snapshot'], row['gpu'])
            if serialize(oracle) != row['oracle']: raise ValueError('retained oracle changed')
            metrics.append(m)
    if [r['label'] for r in historical] != [r['label'] for r in raw[:6]]:
        raise ValueError('legacy order changed')
    if sum(r['gpu']['valid'] for r in historical) != 1:
        raise ValueError('legacy failure not reproduced')
    for row, (cells, label, amplitudes) in zip(real, plan()):
        if (row['cells'], row['input']) != (cells, label): raise ValueError('real probe order changed')
        m, oracle = check(row['snapshot'], row['gpu'], 'shared', cells, amplitudes)
        if serialize(oracle) != row['oracle']: raise ValueError('real retained oracle changed')
        metrics.append(m)
    return {'raw': 21, 'legacy': 6, 'real': 4, 'oracle_valid_probes': len(metrics),
            'ambiguous_rejected': 12, 'miss_rejected': 1,
            'max_metrics': {k: max(m.get(k, 0.) for m in metrics) for k in metrics[-1]},
            'scope': 'retained GPU fields/ledger/counters against CPU scene oracle; no new runtime'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new evidence path required')
    result = audit(json.loads(a.report.read_text(encoding='utf-8')))
    result['report_sha256'] = hashlib.sha256(a.report.read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__': main()
