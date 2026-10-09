"""Record pre-existing errors and reject new errors at each owned graphics stage."""
import json
from Blender.benchmarks.capacity_audit.scene_hilo_gpu_v1 import OpenGLReadbackSync


class GraphicsStageAudit:
    def __init__(self,path):
        self.path=path;self.sync=OpenGLReadbackSync();prior=[]
        for _ in range(16):
            value=self.sync._get_error()
            if value==0:break
            prior.append(hex(value))
        else:raise ValueError('Bounded pre-existing native GL error log exhausted')
        self.record={'schema':'optic_neuro_blender.native_graphics_stage_audit.v1','preexisting_errors_before_owned_field_kernel':prior,'stages':[],'same_context_verified':True}
        self.save()
    def save(self):self.path.write_bytes((json.dumps(self.record,indent=2)+'\n').encode())
    def after(self,name):
        self.sync.assert_context();value=self.sync._get_error();self.record['stages'].append({'stage':name,'gl_error':hex(value)})
        if value:self.save();raise ValueError('Owned native field graphics stage '+name+' OpenGL error '+hex(value))
    def finish(self):self.save()
