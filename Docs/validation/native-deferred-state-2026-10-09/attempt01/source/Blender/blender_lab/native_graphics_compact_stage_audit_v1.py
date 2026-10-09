"""Strict GL/context gates with bounded event-count and SHA256 stream evidence.

Every stage still checks the current context and glGetError synchronously.
Successful events are represented by per-stage counts and a chained stream
hash, avoiding repeated serialization of the entire growing history.
"""
import hashlib,json
from Blender.blender_lab.native_graphics_debug_stage_audit_v2 import GraphicsStageAudit as DebugAudit

class GraphicsStageAudit(DebugAudit):
    def __init__(self,path):
        self.count=0;self.counts={};self.stream=hashlib.sha256();self.errors=[]
        super().__init__(path)
    def save(self):
        self.record.update(schema='optic_neuro_blender.native_graphics_compact_stage_audit.v1',checked_stage_count=self.count,per_stage_counts=self.counts,ordered_stage_stream_sha256=self.stream.hexdigest(),owned_stage_errors=self.errors,all_owned_stages_checked_synchronously=True)
        self.path.write_bytes((json.dumps(self.record,indent=2,allow_nan=False)+'\n').encode())
    def after(self,name):
        self.sync.assert_context();value=self.sync._get_error();event={'stage':name,'gl_error':hex(value)}
        self.count+=1;self.counts[name]=self.counts.get(name,0)+1
        self.stream.update((json.dumps(event,sort_keys=True,separators=(',',':'))+'\n').encode())
        if value:self.errors.append(event);self.save();raise ValueError('Owned native graphics stage '+name+' OpenGL error '+hex(value))
    def finish(self):self.save()
