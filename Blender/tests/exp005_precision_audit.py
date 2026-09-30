"""CPU re-audit of future retained precision V3 GPU results; no GPU imports."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from exp005_precision_runtime import probes, check_precision
from exp005_paired_cost import plan, check
from exp005_chain_runtime import serialize


def audit(report):
    if not report['passed']: raise ValueError('precision runtime did not pass')
    raw, old, real = report['raw_cases'], report['legacy_precision'], report['real_cases']
    if (len(raw), len(old), len(real)) != (29, 3, 4): raise ValueError('all 36 dispatches required')
    metrics = []
    for row, (label, snapshot, status) in zip(raw, probes()):
        if row['label'] != label or row['snapshot'] != json.loads(json.dumps(snapshot)):
            raise ValueError('raw fixture/order changed')
        if row['expected_status'] != status: raise ValueError('expected status changed')
        m, oracle = check_precision(row)
        if m is not None:
            if serialize(oracle) != row['oracle']: raise ValueError('retained raw oracle changed')
            metrics.append(m)
    expected_old = {'precision/direct_gap': 1, 'precision/reflected_gap': 1, 'precision/mode_mismatch': 0}
    if [r['label'] for r in old] != list(expected_old): raise ValueError('legacy precision order changed')
    for row in old:
        expected = expected_old[row['label']]
        if row['gpu']['work']['status'] != expected or row['gpu']['valid'] != (expected == 0):
            raise ValueError('legacy GPU precision failure missing')
    for row, (cells, label, amplitudes) in zip(real, plan()):
        if (row['cells'], row['input']) != (cells, label): raise ValueError('real probe order changed')
        m, oracle = check(row['snapshot'], row['gpu'], 'shared', cells, amplitudes)
        if serialize(oracle) != row['oracle']: raise ValueError('retained real oracle changed')
        metrics.append(m)
    return {'raw': 29, 'legacy': 3, 'real': 4, 'oracle_valid_probes': len(metrics),
            'max_metrics': {k: max(m.get(k, 0.) for m in metrics) for k in metrics[-1]},
            'scope': 'CPU re-audit of retained GPU readbacks; not a new GPU run'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new evidence path required')
    result = audit(json.loads(a.report.read_text(encoding='utf-8')))
    result['report_sha256'] = hashlib.sha256(a.report.read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__': main()
