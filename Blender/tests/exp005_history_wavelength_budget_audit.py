"""Tiny CPU audit of the opt-in wavelength-only many-path bound."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'benchmarks/capacity_audit'))
from test_exp005_history_wavelength_budget import run_case,upper,HistoryWavelengthBudget
from history_fields_cpu_v1 import ideal_fields
from history_trace_cpu_v1 import trace_scene


def audit():
    started=time.monotonic();stream=io.StringIO()
    tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(HistoryWavelengthBudget))
    if not tests.wasSuccessful():raise AssertionError(stream.getvalue())
    specifications=[('exact',{'field_budget':0.,'intensity_budget':0.}),
        ('inexact_single',{}),('inexact_coherent',{'sources':2}),
        ('inexact_independent',{'sources':2,'coherent':False}),
        ('inexact_opposition',{'sources':2,'opposite':True}),
        ('inexact_reference',{'shift':.03125}),
        ('inexact_zero',{'zero':True,'field_budget':0.,'intensity_budget':0.})]
    cases=[]
    for name,options in specifications:
        wavelength=.125 if name=='exact' else 1.00416693877201e-12
        scene,budget=run_case(wavelength,**options)
        candidate=deepcopy(scene);candidate['lambda_BU']=budget['wavelength_transport']['decoded_BU']
        fields=[]
        for snapshot in (scene,candidate):
            fields.append(ideal_fields(snapshot,trace_scene(snapshot)['records'],
                                      coherence_groups=budget['coherence_groups'])['ports'])
        field_errors={};intensity_errors={}
        for port,groups in budget['ports'].items():
            field_errors[port]={}
            for group,interval in groups['groups'].items():
                original=complex(*fields[0][port]['groups'][group]['field_reim'])
                encoded=complex(*fields[1][port]['groups'][group]['field_reim'])
                error=abs(original-encoded)
                # Diagnostic float64/libm comparison, NOT a certified native bound.
                if F(error)>upper(interval['field_error_upper'])+F(1e-13):
                    raise AssertionError('diagnostic field difference beyond bound plus explicit CPU slack')
                field_errors[port][group]=error
            error=abs(fields[0][port]['intensity']-fields[1][port]['intensity'])
            if F(error)>upper(groups['intensity_error_upper'])+F(1e-13):
                raise AssertionError('diagnostic intensity difference beyond bound plus explicit CPU slack')
            intensity_errors[port]=error
        cases.append({'name':name,'snapshot':scene,'budget':budget,
                      'original_cpu_fields':fields[0],'encoded_lambda_cpu_fields':fields[1],
                      'diagnostic_field_errors':field_errors,'diagnostic_intensity_errors':intensity_errors})
    names=['history_wavelength_field_budget_v1.py','history_trace_cpu_v1.py',
        'history_lengths_cpu_v1.py','history_lineage_cpu_v2.py','history_completeness_cpu_v1.py',
        'history_fields_cpu_v1.py','wavelength_transport_v1.py','phase_transport_budget_v1.py',
        'frontier_inputs.py','gpu_geometry_probe.py']
    paths=[ROOT/'benchmarks/capacity_audit'/n for n in names]
    paths += [Path(__file__),Path(__file__).with_name('test_exp005_history_wavelength_budget.py'),
              Path(__file__).with_name('exp005_history_mzi_audit.py'),
              Path(__file__).with_name('exp005_blender_gpu.py')]
    return {'timestamp_utc':datetime.now(timezone.utc).isoformat(),'cases':cases,
            'tests_run':tests.testsRun,'test_output':stream.getvalue(),
            'diagnostic_float64_slack':1e-13,
            'scope':'CPU synthetic ideal fixed geometry; wavelength-only bound, NOT total/native certification',
            'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'seconds':time.monotonic()-started,'no_jev_aval':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=audit()
    with args.output.open('x',encoding='utf-8') as handle:
        json.dump(result,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'tests':result['tests_run'],'cases':len(result['cases']),
        'accepted_wavelength_only':[c['name'] for c in result['cases'] if c['budget']['accepted_wavelength_only']],
        'seconds':result['seconds'],'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
