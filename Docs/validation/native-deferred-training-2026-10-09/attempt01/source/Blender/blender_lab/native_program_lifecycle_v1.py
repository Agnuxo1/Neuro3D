"""Release a bound owned program before destruction in this disposable WGL context."""
import ctypes
from Blender.benchmarks.capacity_audit.scene_hilo_gpu_v1 import OpenGLReadbackSync


def unbind_owned_program(gpu):
    sync=OpenGLReadbackSync();sync.assert_context();sync.require_no_error('before owned program release')
    value=ctypes.c_int32();sync._get_integer(0x8B8D,ctypes.byref(value));previous=value.value
    gpu.shader.unbind()
    # Blender 4.5.14 GLShader::unbind calls glUseProgram(0) only in debug builds.
    use_program=sync._resolve('glUseProgram',None,ctypes.c_uint32)
    use_program(0);sync.require_no_error('owned documented glUseProgram zero')
    sync._get_integer(0x8B8D,ctypes.byref(value));sync.require_no_error('owned unbound program check')
    if value.value!=0:raise ValueError('Actual owned GL_CURRENT_PROGRAM zero required before destruction')
    return {'schema':'optic_neuro_blender.native_program_release.v1','previous_owned_program':previous,'current_program_after_release':value.value,'same_context_verified':True,'gl_errors':[]}
