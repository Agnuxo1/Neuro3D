"""Prepared Blender GPU scalar probe; CPU ABI/decoder, no import-time GPU.

Exact uint words carry represented binary64 scalars. This does NOT validate
geometry hi-lo export, scene inference, physical optics or driver precision.
"""
from fractions import Fraction as F
import math
from pathlib import Path
import struct
from phase_circular_budget_cpu_v1 import scalar_circular_budget

SHADER = Path(__file__).resolve().parents[2]/'shaders/exp005_phase_compensated_probe.glsl'
KEYS = ('quotient_binary64','residual_binary64','correction_binary64',
        'reduced_cycles_binary64','angle_float32')
MAX_SAMPLES = 16


def words(value):
    if type(value) is not float: raise ValueError('binary64 float required')
    return struct.unpack('<2I',struct.pack('<d',value))


def scalar(pair):
    if len(pair)!=2 or any(type(x) is not int or not 0<=x<2**32 for x in pair):
        raise ValueError('two exact uint32 words required')
    return struct.unpack('<d',struct.pack('<2I',*pair))[0]


def pack_samples(samples):
    if type(samples) is not list or not 1<=len(samples)<=MAX_SAMPLES:
        raise ValueError('explicit 1..16 scalar pairs required')
    output=[]
    for pair in samples:
        if len(pair)!=2:raise ValueError('length/lambda pair required')
        output.extend((*words(pair[0]),*words(pair[1])))
    return output  # Includes intentional invalid scalars for status probes.


def require_statuses(samples, expected_statuses):
    if (type(expected_statuses) is not list or len(expected_statuses)!=len(samples)
            or any(type(s) is not int or s not in (0,1,2,3,4) for s in expected_statuses)):
        raise ValueError('explicit preregistered status per sample required')


def decode(samples, output, *, expected_statuses):
    pack_samples(samples);require_statuses(samples,expected_statuses)
    data=list(output)
    if len(data)!=len(samples)*28 or any(type(x) is not int or not 0<=x<2**32 for x in data):
        raise ValueError('exact uint32 readback shape required')
    result=[]
    for i,(length,wavelength) in enumerate(samples):
        row=data[i*28:(i+1)*28];status,identity,pad0,pad1=row[24:28]
        if identity!=i or status not in (0,1,2,3,4) or pad0 or pad1:
            raise ValueError('status/identity/padding mismatch')
        if status!=expected_statuses[i]:raise ValueError('unexpected abort or success')
        if status:
            if any(row[:24]):raise ValueError('aborted probe emitted partial trace/field')
            result.append({'id':i,'status':status,'field_emitted':False});continue
        if any(row[4*j+2] or row[4*j+3] for j in range(5)):
            raise ValueError('scalar trace padding mismatch')
        trace={key:scalar(row[4*j:4*j+2]) for j,key in enumerate(KEYS)}
        bound=scalar_circular_budget(length,wavelength,trace,field_budget=1e-4)
        real,imag=scalar(row[20:22]),scalar(row[22:24])
        if not all(math.isfinite(x) for x in (real,imag)):
            raise ValueError('nonfinite shader sin/cos readback')
        cycles=F(length)/F(wavelength);cycles-=(cycles+F(1,2))//1
        angle=math.tau*float(cycles)
        error=abs(complex(real,imag)-complex(math.cos(angle),math.sin(angle)))
        if error>1e-4 or not bound['field_budget_satisfied_arithmetic_only']:
            raise ValueError('scalar field/phase gate failed')
        result.append({'id':i,'status':0,'trace':trace,'point_arithmetic_bound':bound,
                       'observed_unit_field_error_vs_CPU_reference':error})
    return {'cases':result,'native_promotion_allowed':False,
            'geometry_or_scene_inference':False,'runtime_execution_authenticated':False,
            'scope':'scalar readback consistency only; CPU libm reference not driver certificate'}


def flatten(value):
    return [x for v in value for x in flatten(v)] if isinstance(value,(list,tuple)) else [value]


def dispatch_probe(gpu, samples, expected_statuses, check_deadline):
    """Caller MUST own exclusive guarded Blender child and fresh deadline.

    No CLI/launcher, authorization flag, reservation bypass or CPU fallback.
    check_deadline is mandatory before compile/alloc/dispatch/readback.
    Outputs expose compiler/RN errors rather than relaxing a threshold.
    """
    if not callable(check_deadline):raise ValueError('external deadline check required')
    check_deadline();data=pack_samples(samples);require_statuses(samples,expected_statuses)
    info=gpu.types.GPUShaderCreateInfo()
    info.sampler(0,'UINT_2D','samples_in')
    info.image(0,'RGBA32UI','UINT_2D','trace_out',qualifiers={'WRITE'})
    info.push_constant('INT','sample_count');info.local_group_size(8,1,1)
    info.compute_source(SHADER.read_text(encoding='utf-8'))
    shader=gpu.shader.create_from_info(info);check_deadline()
    source=gpu.types.GPUTexture((len(samples),1),format='RGBA32UI',
        data=gpu.types.Buffer('UINT',len(data),data))
    target=gpu.types.GPUTexture((7,len(samples)),format='RGBA32UI')
    shader.uniform_sampler('samples_in',source);shader.image('trace_out',target)
    shader.uniform_int('sample_count',len(samples));check_deadline()
    gpu.compute.dispatch(shader,math.ceil(len(samples)/8),1,1)
    check_deadline()
    output=flatten(target.read().to_list());check_deadline()
    return decode(samples,output,expected_statuses=expected_statuses)
