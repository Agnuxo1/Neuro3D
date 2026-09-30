"""Retain only own CPU plan checks; never launch the prepared command."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from test_exp005_history_job_plan import audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit()
    report['executed_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['preparation_sha256'] = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (Path(__file__), Path(__file__).with_name('exp005_history_job_plan.py'),
                  Path(__file__).with_name('test_exp005_history_job_plan.py'))}
    with args.output.open('x', encoding='utf-8') as file:
        file.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'pins': len(report['control']['code_sha256']),
                      'negatives': len(report['negatives']), 'launched': False,
                      'report_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__':main()
