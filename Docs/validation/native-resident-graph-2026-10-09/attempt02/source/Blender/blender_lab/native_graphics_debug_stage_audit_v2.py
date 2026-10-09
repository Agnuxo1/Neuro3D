"""Owned-context synchronous driver diagnostics, with unchanged strict GL gates."""
import ctypes
from Blender.blender_lab.native_graphics_stage_audit_v1 import GraphicsStageAudit as StrictAudit


class GraphicsStageAudit(StrictAudit):
    def __init__(self,path):
        super().__init__(path)
        self.record['driver_messages']=[]
        callback_type=ctypes.WINFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p,ctypes.c_void_p)
        def receive(source,kind,identifier,severity,length,message,user):
            if len(self.record['driver_messages'])<256:
                self.record['driver_messages'].append({'source':source,'type':kind,'id':identifier,'severity':severity,'message':ctypes.string_at(message,length).decode('utf-8',errors='replace')})
        self.callback=callback_type(receive)
        self.install=self.sync._resolve('glDebugMessageCallback',None,ctypes.c_void_p,ctypes.c_void_p)
        self.install(ctypes.cast(self.callback,ctypes.c_void_p),None)
        enable=self.sync._dll.glEnable;enable.argtypes=[ctypes.c_uint32];enable.restype=None
        enable(0x92E0);enable(0x8242)
        self.after('owned_synchronous_debug_callback_install')
        self.save()
