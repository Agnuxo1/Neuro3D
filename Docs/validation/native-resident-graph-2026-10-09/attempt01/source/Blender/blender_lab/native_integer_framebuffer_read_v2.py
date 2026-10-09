"""Exact eight-attachment RGBA integer readback in the existing verified native WGL context.

Khronos requires GL_RGBA_INTEGER for integer attachments. This bounded reader
uses documented GL calls, owns no context/resource, and restores read/pack state.
"""
import ctypes
from Blender.benchmarks.capacity_audit.scene_hilo_gpu_v1 import OpenGLReadbackSync


def read_uint_slots(width,slots):
    if type(width)!=int or not 1<=width<=256 or not slots or any(type(s)!=int or not 0<=s<8 for s in slots):raise ValueError('Bounded native integer framebuffer read required')
    sync=OpenGLReadbackSync();sync.assert_context()
    def integer(name):
        value=ctypes.c_int32();sync._get_integer(name,ctypes.byref(value));return value.value
    state={k:integer(k) for k in (0x8CA6,0x8CAA,0x88ED,0x0C02,0x0D05,0x0D02,0x0D03,0x0D04)}
    if not state[0x8CA6] or state[0x8CA6]!=state[0x8CAA] or state[0x88ED]!=0:raise ValueError('Existing owned draw/read framebuffer and no pixel-pack-buffer required')
    sync.require_no_error('before exact integer framebuffer read')
    read_buffer=sync._dll.glReadBuffer;read_buffer.restype=None;read_buffer.argtypes=[ctypes.c_uint32]
    pixel_store=sync._dll.glPixelStorei;pixel_store.restype=None;pixel_store.argtypes=[ctypes.c_uint32,ctypes.c_int32]
    read_pixels=sync._dll.glReadPixels;read_pixels.restype=None
    read_pixels.argtypes=[ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)]
    rows=[]
    try:
        for pname,value in ((0x0D05,4),(0x0D02,0),(0x0D03,0),(0x0D04,0)):pixel_store(pname,value)
        sync.require_no_error('controlled exact integer pixel-pack state')
        for slot in slots:
            sync.assert_context();read_buffer(0x8CE0+slot);sync.require_no_error('selected integer framebuffer attachment')
            data=(ctypes.c_uint32*(4*width))()
            read_pixels(0,0,width,1,0x8D99,0x1405,data)
            sync.require_no_error('GL_RGBA_INTEGER GL_UNSIGNED_INT readback');rows.append(list(data))
    finally:
        sync.assert_context();read_buffer(state[0x0C02])
        for pname in (0x0D05,0x0D02,0x0D03,0x0D04):pixel_store(pname,state[pname])
        sync.require_no_error('restored framebuffer integer readback state')
    return rows,{'schema':'optic_neuro_blender.native_integer_readback.v1','same_context_verified':True,'format':'GL_RGBA_INTEGER','type':'GL_UNSIGNED_INT','pack_read_state_restored':True,'word_count_per_slot':4*width,'slots':list(slots),'gl_errors':[]}
