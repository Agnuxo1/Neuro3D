"""Bounded CPU diagnostic; no changes to frozen absolute complex-field gates."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'benchmarks/capacity_audit'))
from test_exp005_relative_power_budget import make_scene,evaluate,RelativePowerBudget
from history_relative_power_budget_v1 import upper
from history_wavelength_field_budget_v1 import scene_wavelength_field_budget
from history_trace_cpu_v1 import trace_scene
from history_fields_cpu_v1 import ideal_fields
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

BASELINE=NEURO3D_COGNITION / 'neuro3d/exp005_history_wavelength_budget_20260930_1541.json'
BASELINE_SHA='a6e49baefa5196c2c3740fed3de3eb28cd7ba3fd62a1adb0fa4c30e0d7d3103f'


def verify_baseline():
    if hashlib.sha256(BASELINE.read_bytes()).hexdigest()!=BASELINE_SHA:
        raise ValueError('retained baseline changed')
    previous=json.loads(BASELINE.read_text())
    for file,sha in previous['code_sha256'].items():
        if hashlib.sha256(Path(file).read_bytes()).hexdigest()!=sha:
            raise ValueError('frozen baseline input changed: '+file)
    return previous


def audit():
    started=time.monotonic();previous=verify_baseline()
    stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RelativePowerBudget))
    if not tests.wasSuccessful():raise AssertionError(stream.getvalue())
    specs=[('same_lengths_coherent',dict(two=True),True),
           ('distinct_lengths_coherent',dict(two=True,offset=.03125),True),
           ('distinct_lengths_independent',dict(two=True,offset=.03125),False),
           ('reference_shift',dict(reference=.03125),True),
           ('exact_wavelength',dict(two=True,offset=.03125,wavelength=.125),True)]
    cases=[]
    for name,options,coherent in specs:
        scene=make_scene(**options);before=deepcopy(scene)
        candidate=evaluate(scene,coherent=coherent)
        groups=candidate['coherence_groups']
        absolute=scene_wavelength_field_budget(scene,coherence_groups=groups,
            field_budget=1e-4,intensity_budget=2e-4,relative_budget=1e-12)
        if scene!=before or candidate['ledger']!=absolute['ledger']:
            raise AssertionError('scene or complete absolute ledger changed')
        for port,value in candidate['ports'].items():
            if upper(value['intensity_error_upper'])>upper(absolute['ports'][port]['intensity_error_upper']):
                raise AssertionError('candidate worsened bound')
            for group,entry in value['groups'].items():
                for key in ('field_error_upper','field_budget_satisfied','path_count','amplitude_sum_upper'):
                    if entry[key]!=absolute['ports'][port]['groups'][group][key]:
                        raise AssertionError('absolute complex-field gate modified')
        snapshots=[scene,deepcopy(scene)]
        snapshots[1]['lambda_BU']=candidate['wavelength_transport']['decoded_BU']
        fields=[ideal_fields(s,trace_scene(s)['records'],coherence_groups=groups)['ports'] for s in snapshots]
        observed={}
        for port,value in candidate['ports'].items():
            difference=abs(fields[0][port]['intensity']-fields[1][port]['intensity'])
            if F(difference)>upper(value['intensity_error_upper'])+F(1e-13):
                raise AssertionError('CPU diagnostic beyond relative bound plus explicit float64 slack')
            observed[port]=difference
        cases.append({'name':name,'snapshot':scene,'absolute':absolute,'relative':candidate,
                      'diagnostic_original_fields':fields[0],'diagnostic_encoded_fields':fields[1],
                      'diagnostic_intensity_error':observed})
    verify_baseline()
    files=[Path(__file__),Path(__file__).with_name('test_exp005_relative_power_budget.py'),
           ROOT/'benchmarks/capacity_audit/history_relative_power_budget_v1.py']
    return {'timestamp_utc':datetime.now(timezone.utc).isoformat(),'tests_run':tests.testsRun,
            'test_output':stream.getvalue(),'cases':cases,'seconds':time.monotonic()-started,
            'unchanged_baseline_sha256':BASELINE_SHA,'verified_baseline_pins':previous['code_sha256'],
            'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'diagnostic_float64_slack':1e-13,
            'scope':'CPU ideal fixed-scene wavelength-only intensity bound; absolute fields unchanged; NOT GPU/RT',
            'no_jev_aval':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=audit()
    with args.output.open('x',encoding='utf-8') as handle:
        json.dump(out,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'cases':len(out['cases']),'tests':out['tests_run'],'seconds':out['seconds'],
        'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'Dx_power_bounds':[{'case':c['name'],
            'absolute':float(upper(c['absolute']['ports']['Dx']['intensity_error_upper'])),
            'relative':float(upper(c['relative']['ports']['Dx']['intensity_error_upper'])),
            'observed':c['diagnostic_intensity_error']['Dx']} for c in out['cases']]}))


if __name__=='__main__':main()
