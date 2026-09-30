"""Scene-bound CPU arithmetic proxy for frozen GLSL phase expressions.

Not GPU execution or a compiler/libm certificate. The quotient-first
alternative is a diagnostic only, NOT a general fix or shader patch.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys
import time
import unittest

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'benchmarks/capacity_audit'))
from exp005_history_mzi_audit import fixture
from exp005_blender_gpu import split_double,texture_data
from frontier_inputs import pack_frontier
from history_trace_cpu_v1 import trace_scene
from history_lengths_cpu_v1 import reconstruct_lengths

FIELD_TOL=1e-4
SHADER=ROOT/'shaders/exp005_shared_frontier.glsl'


def float32(value):
    return struct.unpack('<f',struct.pack('<f',value))[0]


def phase_proxy(length,wavelength):
    turns=F(length)/F(wavelength)
    reduced=turns-((turns+F(1,2))//1)
    exact_angle=math.tau*float(reduced)
    phase=math.tau*length/wavelength
    phase_first=float32(phase-math.tau*math.floor(phase/math.tau+.5))
    quotient=length/wavelength
    cycles_first=float32(math.tau*(quotient-math.floor(quotient+.5)))
    target=complex(math.cos(exact_angle),math.sin(exact_angle))
    def difference(angle):
        return abs(complex(math.cos(angle),math.sin(angle))-target)
    return {'exact_reduced_turns':[reduced.numerator,reduced.denominator],
            'rational_reference_angle':exact_angle,
            'phase_first_CPU_angle_float32':phase_first,
            'cycles_first_CPU_angle_float32':cycles_first,
            'phase_first_CPU_unit_field_error':difference(phase_first),
            'cycles_first_CPU_unit_field_error':difference(cycles_first),
            'cpu_cos_sin_only':True}


def case(name,wavelength,reference):
    scene,_=fixture();scene['lambda_BU']=wavelength
    scene['objects']['Dx']['mode_origin_BU'][0]=reference
    batch=pack_frontier(scene)
    unchanged={}
    for label,raw in (('geometry',batch.geometry.triangles),('sources',batch.sources),('optics',batch.optics)):
        _height,hi,lo=texture_data(raw)
        unchanged[label]=sum(float(a)+float(b)!=v for v,a,b in zip(raw,hi,lo))
    if any(unchanged.values()):raise ValueError('this pilot requires exact non-wavelength raw ABI transport')
    rows=trace_scene(scene)['records'];lengths=reconstruct_lengths(scene,rows)
    values=[r['effective_length'] for r in lengths['terminals'] if r['port']=='Dx']
    if not values or any(r!=values[0] for r in values):
        raise ValueError('same effective length on the two Dx arms required')
    effective=values[0]
    lo,hi=F(*effective['rational_lower']),F(*effective['rational_upper'])
    if lo!=hi or F(float(lo))!=lo:raise ValueError('exact binary64 effective length required')
    high,low=split_double(wavelength);decoded=float(high)+float(low)
    result=phase_proxy(float(lo),decoded)
    return {'name':name,'snapshot':scene,'generated_records':len(rows),
            'non_wavelength_raw_transport_changes':unchanged,
            'effective_length':effective,'lambda_hi_lo':[high,low],'lambda_decoded_BU':decoded,
            'lambda_transport_exact':decoded==wavelength,
            'reference_uses_decoded_lambda_not_original':True,**result}


def cases():
    return [case('integer_control',.125,2.),case('quarter_control',.125,2.03125),
            case('exact_lambda_large_quarter_20',2**-20,999999.875+2**-22),
            case('exact_lambda_large_quarter_30',2**-30,999999.875+2**-32),
            case('cycles_first_still_fails',1.00416693877201e-12,999999.875+2**-22)]


def audit():
    started=time.monotonic();source=SHADER.read_text()
    required=('float angle=float(phase-TAU*floor(phase/TAU+0.5));',
              'TAU*effective/(double(wavelength_hi)+double(wavelength_lo))')
    if any(token not in source for token in required):raise ValueError('frozen source expression changed')
    before=hashlib.sha256(SHADER.read_bytes()).hexdigest()
    from test_exp005_phase_reduction_cpu import PhaseReductionCPU
    stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PhaseReductionCPU))
    if not tests.wasSuccessful():raise AssertionError(stream.getvalue())
    rows=cases()
    if hashlib.sha256(SHADER.read_bytes()).hexdigest()!=before:
        raise ValueError('shader changed during CPU audit')
    names=['history_trace_cpu_v1.py','history_lengths_cpu_v1.py','history_lineage_cpu_v2.py',
           'history_completeness_cpu_v1.py','frontier_inputs.py','gpu_geometry_probe.py']
    paths=[ROOT/'benchmarks/capacity_audit'/name for name in names]
    paths += [Path(__file__),Path(__file__).with_name('test_exp005_phase_reduction_cpu.py'),
              Path(__file__).with_name('exp005_history_mzi_audit.py'),
              Path(__file__).with_name('exp005_blender_gpu.py'),SHADER]
    return {'timestamp_utc':datetime.now(timezone.utc).isoformat(),'tests_run':tests.testsRun,
            'test_output':stream.getvalue(),'cases':rows,'field_threshold_unchanged':FIELD_TOL,
            'seconds':time.monotonic()-started,'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'synthetic complete CPU scene plus actual ABI encoder and CPU phase arithmetic proxy; NOT GPU/RT/Bpy',
            'quotient_first_shader_implemented':False,'native_promotion_allowed':False,
            'no_jev_aval':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=audit()
    with args.output.open('x',encoding='utf-8') as handle:
        json.dump(out,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'cases':len(out['cases']),'tests':out['tests_run'],'seconds':out['seconds'],
        'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'errors':[{'case':r['name'],'exact_lambda':r['lambda_transport_exact'],
            'phase_first':r['phase_first_CPU_unit_field_error'],
            'cycles_first':r['cycles_first_CPU_unit_field_error']} for r in out['cases']]}))


if __name__=='__main__':main()
