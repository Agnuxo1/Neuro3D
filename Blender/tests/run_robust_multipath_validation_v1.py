"""Run point-3 preregistered gates, preserve failure and exact full-path ledger."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import test_robust_multipath_v1 as tests
from robust_multipath_v1 import trace_scene
from exp005_chain_fixture import chain_fixture, inputs, set_fields, analytic_fields


def wire(value):
    if isinstance(value, Fraction): return {'numerator': value.numerator, 'denominator': value.denominator}
    if isinstance(value, complex): return [value.real, value.imag]
    if isinstance(value, dict): return {k: wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [wire(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): raise ValueError('fresh evidence directory required')
    args.out.mkdir(parents=True)
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    report = {'schema': 'neuro3d-complete-multipath-validation-v1', 'time_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS' if result.wasSuccessful() else 'FAIL', 'tests': result.testsRun,
              'failure_count': len(result.failures), 'error_count': len(result.errors), 'test_output': output.getvalue(),
              'scope': 'CPU exact represented geometry, approximate scalar phase/fields; no full GPU/physical claim'}
    rows, max_error, max_balance = [], 0., 0.
    if result.wasSuccessful():
        for cells in (3, 4):
            snapshot = chain_fixture(cells)
            for label, amplitudes in inputs(cells+1):
                set_fields(snapshot, amplitudes)
                traced = trace_scene(snapshot); expected = analytic_fields(cells, amplitudes)
                error = max(abs(traced['fields'][p]-expected[p]) for p in expected)
                balance = abs(traced['input_power']-traced['output_power'])
                max_error, max_balance = max(max_error, error), max(max_balance, balance)
                rows.append({'cells': cells, 'probe': label, 'field_error': error, 'balance_error': balance, 'trace': traced})
        report.update(analytic_probes=len(rows), max_field_error=max_error, max_balance_error=max_balance)
        (args.out/'exact_paths.json').write_text(json.dumps(wire(rows), indent=2, allow_nan=False)+'\n', encoding='utf-8')
    dependencies = [Path(__file__), Path(tests.__file__), ROOT/'Blender/benchmarks/capacity_audit/robust_multipath_v1.py',
                    ROOT/'Blender/tests/exp005_chain_fixture.py', ROOT/'Blender/tests/exp005_cascade_fixture.py',
                    ROOT/'Blender/tests/exp005_escape_fixture.py', ROOT/'Docs/MULTIPATH_EXACT_PREREGISTRATION_2026-10-08.md']
    report['source_sha256'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
    report['evidence_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.out.iterdir() if p.is_file()}
    (args.out/'receipt.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'tests', 'failure_count', 'error_count')}))
    if not result.wasSuccessful():
        print(output.getvalue()[-12000:]); return 1
    return 0


if __name__ == '__main__': raise SystemExit(main())
