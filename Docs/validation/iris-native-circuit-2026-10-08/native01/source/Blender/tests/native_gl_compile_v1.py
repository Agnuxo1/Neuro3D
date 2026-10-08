"""Compile/link raw GL450 compute source in a verified private Blender WGL context."""
import ctypes as c
import hashlib
from Blender.tests.robust_first_hit_raw_gl_v1 import RawProgram


def compile_source(source,report):
    raw=source.encode('utf-8'); report['shader_source_sha256']=hashlib.sha256(raw).hexdigest()
    api=RawProgram(0); U,I=c.c_uint32,c.c_int32
    create=api.entry('glCreateShader',U,U); shader=create(0x91b9)
    program=0
    def log(handle,program_log=False):
        getter=api.entry('glGetProgramiv' if program_log else 'glGetShaderiv',None,U,U,c.POINTER(I))
        length=I(); getter(handle,0x8b84,c.byref(length)); limit=min(max(length.value,1),2**20)
        buffer=c.create_string_buffer(limit); written=I()
        api.entry('glGetProgramInfoLog' if program_log else 'glGetShaderInfoLog',None,U,I,c.POINTER(I),c.c_void_p)(handle,limit,c.byref(written),buffer)
        return buffer.raw[:max(written.value,0)].decode('utf-8',errors='replace')
    try:
        string=c.c_char_p(raw); length=I(len(raw))
        api.entry('glShaderSource',None,U,I,c.POINTER(c.c_char_p),c.POINTER(I))(shader,1,c.byref(string),c.byref(length))
        api.entry('glCompileShader',None,U)(shader)
        compiled=I(); api.entry('glGetShaderiv',None,U,U,c.POINTER(I))(shader,0x8b81,c.byref(compiled))
        report['compile_log']=log(shader); report['compiled']=compiled.value==1
        if compiled.value!=1: raise ValueError('native GL compute compilation failed')
        program=api.entry('glCreateProgram',U)()
        api.entry('glAttachShader',None,U,U)(program,shader); api.entry('glLinkProgram',None,U)(program)
        linked=I(); api.entry('glGetProgramiv',None,U,U,c.POINTER(I))(program,0x8b82,c.byref(linked))
        report['link_log']=log(program,True); report['linked']=linked.value==1
        if linked.value!=1: raise ValueError('native GL compute linking failed')
        result=RawProgram(program); program=0
        api.sync.require_no_error('compute compile/link')
        return result
    finally:
        if shader: api.entry('glDeleteShader',None,U)(shader)
        if program: api.entry('glDeleteProgram',None,U)(program)
