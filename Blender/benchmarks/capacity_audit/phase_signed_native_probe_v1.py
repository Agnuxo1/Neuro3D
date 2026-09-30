"""Signed exact-word ABI/decoder and uncompiled guarded GPU callable.

Never a launcher/admission certificate. Raw output must be retained before
numeric gating. Frozen nonnegative pilot unchanged; no CPU runtime fallback.
"""
from fractions import Fraction as F
import math
from pathlib import Path
from phase_native_probe_v1 import words, scalar, pack_samples, require_statuses, flatten, KEYS
from history_signed_phase_budget_cpu_v1 import signed_scalar_budget

SHADER = Path(__file__).resolve().parents[2]/'shaders/exp005_signed_phase_probe.glsl'


def pilot_cases():
    pairs = [(-1e-9, .125), (-.5, 1.), (-1000.0625, 1.00416693877201e-12),
             (-1000001.8750002384, 3*2.**-20), (-3.03125, .1),
             (4.03125, .125), (0., .125), (math.nextafter(-.5, -math.inf), 1.),
             (-float(2**52), 1.), (-1., 0.), (-2.**-1074, 1.), (math.nan, 1.)]
    statuses = [0]*8+[2, 1, 1, 1]
    return [{'id': i, 'input_uint32': list((*words(l), *words(w))), 'expected_status': s}
            for i, ((l, w), s) in enumerate(zip(pairs, statuses))]


def decode(samples, output, *, expected_statuses):
    pack_samples(samples); require_statuses(samples, expected_statuses)
    data = list(output)
    if len(data) != len(samples)*28 or any(type(x) is not int or not 0 <= x < 2**32 for x in data):
        raise ValueError('exact signed uint32 readback shape required')
    results = []
    for i, (length, wavelength) in enumerate(samples):
        row = data[i*28:(i+1)*28]
        status, identity, p0, p1 = row[24:28]
        if identity != i or status != expected_statuses[i] or p0 or p1:
            raise ValueError('signed status/identity/padding mismatch')
        if status:
            if any(row[:24]): raise ValueError('aborted signed probe emitted partial field')
            results.append({'id': i, 'status': status, 'field_emitted': False})
            continue
        if any(row[4*j+2] or row[4*j+3] for j in range(5)):
            raise ValueError('signed scalar trace padding mismatch')
        decoded = {key: scalar(row[4*j:4*j+2]) for j, key in enumerate(KEYS)}
        sign = -1 if length < 0 else 1
        magnitude = {**decoded, 'angle_float32': sign*decoded['angle_float32']}
        trace = {'effective_length_BU': length, 'phase_sign': sign, 'magnitude_trace': magnitude,
                 'angle_float32': decoded['angle_float32']}
        bound = signed_scalar_budget(length, wavelength, trace, field_budget=1e-4)
        real, imag = scalar(row[20:22]), scalar(row[22:24])
        if not all(math.isfinite(x) for x in (real, imag)):
            raise ValueError('nonfinite signed sin/cos readback')
        cycles = F(length)/F(wavelength); cycles -= (cycles+F(1, 2))//1
        reference = math.tau*float(cycles)
        error = abs(complex(real, imag)-complex(math.cos(reference), math.sin(reference)))
        if error > 1e-4 or not bound['field_budget_satisfied_arithmetic_only']:
            raise ValueError('signed scalar field/phase gate failed')
        results.append({'id': i, 'status': 0, 'signed_trace': trace,
                        'point_arithmetic_bound': bound, 'unit_field_error_vs_CPU_libm': error})
    return {'cases': results, 'native_promotion_allowed': False,
            'runtime_execution_authenticated': False, 'geometry_or_scene_inference': False,
            'scope': 'signed scalar consistency only; CPU libm is not a driver certificate'}


def dispatch_signed_probe(gpu, samples, statuses, check_deadline, retain_raw):
    if not callable(check_deadline) or not callable(retain_raw):
        raise ValueError('mandatory external deadline and raw-retention adapters')
    check_deadline(); data = pack_samples(samples); require_statuses(samples, statuses)
    info = gpu.types.GPUShaderCreateInfo()
    info.sampler(0, 'UINT_2D', 'samples_in')
    info.image(0, 'RGBA32UI', 'UINT_2D', 'trace_out', qualifiers={'WRITE'})
    info.push_constant('INT', 'sample_count'); info.local_group_size(8, 1, 1)
    info.compute_source(SHADER.read_text(encoding='utf-8'))
    shader = gpu.shader.create_from_info(info); check_deadline()
    source = gpu.types.GPUTexture((len(samples), 1), format='RGBA32UI',
                                 data=gpu.types.Buffer('UINT', len(data), data))
    target = gpu.types.GPUTexture((7, len(samples)), format='RGBA32UI')
    shader.uniform_sampler('samples_in', source); shader.image('trace_out', target)
    shader.uniform_int('sample_count', len(samples)); check_deadline()
    gpu.compute.dispatch(shader, math.ceil(len(samples)/8), 1, 1); check_deadline()
    output = flatten(target.read().to_list())
    retain_raw(output)  # Mandatory before post-readback deadline/numerical gate.
    check_deadline()
    return decode(samples, output, expected_statuses=statuses)
