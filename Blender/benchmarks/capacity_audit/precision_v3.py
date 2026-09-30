"""Opt-in unshifted nearest V2 + strict scalar terminal-mode candidate.

CPU routines below are bounded contract specifications, not GPU execution.
No Blender dispatch or existing benchmark switches to this variant implicitly.
"""
import hashlib
import math
import nearest_hit_v2 as nearest

PART_SHA = '5310320c1255b2f8470e78b0a93e3c7cd5dec08f4886f3713b2f98d4a67a3206'
T_MIN_BU = 1e-9
TERMINAL_DOT_TOL = 1e-9


def shader_source():
    if hashlib.sha256(nearest.PART.read_bytes()).hexdigest() != PART_SHA:
        raise ValueError('frozen nearest V2 snippet changed')
    source = nearest.shader_source()
    replacements = (
        ('const double BIAS=1.0e-6lf;', 'const double BIAS=0.0lf;'),
        ('if(dot(ray.d,axis)<1.0lf-1.0e-6lf)',
         'if(dot(ray.d,axis)<1.0lf-1.0e-9lf)'),
    )
    for old, new in replacements:
        if source.count(old) != 1: raise ValueError('unexpected frozen precision boundary')
        source = source.replace(old, new)
    return source


def native_shader(gpu):
    info = gpu.types.GPUShaderCreateInfo()
    for slot, name in enumerate(('geometry_hi', 'geometry_lo', 'sources_hi',
                                 'sources_lo', 'optics_hi', 'optics_lo')):
        info.sampler(slot, 'FLOAT_2D', name)
    for slot, name in enumerate(('fields_out', 'stats_out', 'ledger_out', 'work_out')):
        info.image(slot, 'RGBA32F', 'FLOAT_2D', name, qualifiers={'WRITE'})
    for name in ('triangle_count', 'source_count', 'port_count', 'max_steps', 'max_depth'):
        info.push_constant('INT', name)
    for name in ('wavelength_hi', 'wavelength_lo'): info.push_constant('FLOAT', name)
    info.local_group_size(1, 1, 1)
    info.compute_source(shader_source())
    return gpu.shader.create_from_info(info)


def terminal_accept(direction, axis, *, dot_tolerance=TERMINAL_DOT_TOL):
    if (isinstance(dot_tolerance, bool) or not isinstance(dot_tolerance, (int, float))
            or not math.isfinite(dot_tolerance) or not 0 <= dot_tolerance < 1):
        raise ValueError('finite dot-product tolerance in [0,1) required')
    def unit(value):
        if len(value) != 3 or any(isinstance(x, bool) or not isinstance(x, (int, float))
                                 or not math.isfinite(x) for x in value):
            raise ValueError('finite direction required')
        n = math.hypot(*value)
        if n == 0: raise ValueError('nonzero direction required')
        return tuple(x/n for x in value)
    d, a = unit(direction), unit(axis)
    return sum(x*y for x, y in zip(d, a)) >= 1-dot_tolerance
