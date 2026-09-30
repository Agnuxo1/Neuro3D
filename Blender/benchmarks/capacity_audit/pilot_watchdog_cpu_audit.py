"""Run focused CPU lifecycle tests once and retain the same cases."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import unittest
import test_pilot_watchdog_v1 as tests


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.PilotWatchdogCPU))
    if not result.wasSuccessful():raise SystemExit(2)
    report=tests.PilotWatchdogCPU.report
    report.update(executed_at_utc=datetime.now(timezone.utc).isoformat(),tests_run=result.testsRun,
                  no_jev_aval=True)
    files=[Path(__file__),Path(tests.__file__),Path(__file__).with_name('pilot_watchdog_v1.py'),
           Path(__file__).with_name('guarded_job.py')]
    report['code_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x',encoding='utf-8') as file:
        file.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':len(report['cases']), 'tests':result.testsRun,
        'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
