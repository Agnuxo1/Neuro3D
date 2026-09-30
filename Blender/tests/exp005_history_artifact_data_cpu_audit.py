"""Retain focused own artifact-data tests once, without writing blend files."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import unittest
import test_exp005_history_artifact_data as tests
from exp005_history_job_plan import verify_inputs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    outcome=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.ArtifactDataCPU))
    if not outcome.wasSuccessful():raise SystemExit(2)
    report=tests.ArtifactDataCPU.report
    report.update(executed_at_utc=datetime.now(timezone.utc).isoformat(),tests_run=outcome.testsRun)
    pins=verify_inputs()
    for p in (Path(__file__),Path(tests.__file__),Path(__file__).with_name('exp005_history_artifact_data.py'),
              Path(__file__).with_name('exp005_history_job_plan.py')):
        pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    report['code_sha256']=pins
    with args.output.open('x',encoding='utf-8') as file:file.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':3,'negatives':len(report['negatives']),'code_pins':len(pins),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
