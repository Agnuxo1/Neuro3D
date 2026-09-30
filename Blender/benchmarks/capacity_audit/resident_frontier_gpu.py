"""Resident resources for the immutable shared ALU shader, NOT RT.

Cache raw scene geometry/optics and output allocations, never fields or paths.
Every call dispatches GPU traversal anew. Source fields remain host inputs.
CPU evaluated export, invalidation, transfer, decode and oracle are explicit.
"""
import copy
from dataclasses import replace
import json
import time
from frontier_inputs import pack_frontier,scalar
from frontier_gpu import limits
from shared_frontier_gpu import decode,native_shader,SHADER


def static_key(snapshot):
    """Strict state token: only source field values may vary within a session."""
    frozen=copy.deepcopy(snapshot)
    for source in frozen['sources']:
        pair=source['field_reim']
        if len(pair)!=2: raise ValueError('complete complex source field required')
        tuple(map(scalar,pair))
        source['field_reim']=[0.,0.]
    # Preserve object order: GPU optical IDs refer to that order.
    return json.dumps(frozen,separators=(',',':'),allow_nan=False)


class SceneBinding:
    """Pure CPU ABI/invalidation, no tracing, interference or GPU at import."""
    def __init__(self,snapshot,mode_cap=3):
        from exp005_mode_gate import mode_geometry
        mode_geometry(snapshot)
        self.batch=pack_frontier(snapshot,mode_cap=mode_cap)
        self.key=static_key(snapshot)

    def inputs(self,snapshot):
        if static_key(snapshot)!=self.key:
            raise ValueError('scene changed: explicit resident rebuild required')
        raw=list(self.batch.sources)
        for index,source in enumerate(snapshot['sources']):
            real,imag=map(scalar,source['field_reim'])
            raw[index*8+3]=real; raw[index*8+7]=imag
        return replace(self.batch,sources=tuple(raw))


class ResidentSession:
    """Bounded resources owned by one caller in one live Blender GPU context.

No concurrent callers. A changed state or any exception poisons the session;
caller must rebuild explicitly, not fall back to stale geometry or output.
"""
    def __init__(self,gpu,shader,snapshot,*,mode_cap=3,max_steps=4096,max_depth=32):
        limits(max_steps,max_depth)
        self.gpu=gpu; self.shader=shader; self.closed=False
        self.static=[]; self.outputs=[]; self.calls=0; self.allocations=0
        self.max_steps=max_steps; self.max_depth=max_depth
        try:
            self.binding=SceneBinding(snapshot,mode_cap)
            for raw in (self.binding.batch.geometry.triangles,self.binding.batch.optics):
                self.static.extend(self._textures(raw))
            count=len(self.binding.batch.ports)
            for size in ((count,1),(count,1),(128,count),(1,1)):
                self.outputs.append(gpu.types.GPUTexture(size,format='RGBA32F'))
                self.allocations+=1
        except Exception:
            self.close(); raise

    def _textures(self,raw):
        from exp005_blender_gpu import texture_data
        height,hi,lo=texture_data(raw); result=[]
        for values in (hi,lo):
            result.append(self.gpu.types.GPUTexture((64,height),format='RGBA32F',
                data=self.gpu.types.Buffer('FLOAT',len(values),values)))
            self.allocations+=1
        return result

    def run(self,snapshot):
        if self.closed: raise ValueError('resident session is closed; rebuild required')
        from exp005_blender_gpu import split_double,flatten
        try:
            start=time.perf_counter(); batch=self.binding.inputs(snapshot)
            dynamic=self._textures(batch.sources)
            textures=self.static[:2]+dynamic+self.static[2:]
            for name,texture in zip(('geometry_hi','geometry_lo','sources_hi','sources_lo','optics_hi','optics_lo'),textures):
                self.shader.uniform_sampler(name,texture)
            for name,texture in zip(('fields_out','stats_out','ledger_out','work_out'),self.outputs):
                self.shader.image(name,texture)
            for name,value in (('triangle_count',batch.geometry.triangle_count),('source_count',len(batch.source_ids)),
                ('port_count',len(batch.ports)),('max_steps',self.max_steps),('max_depth',self.max_depth)):
                self.shader.uniform_int(name,value)
            hi,lo=split_double(batch.wavelength_BU)
            self.shader.uniform_float('wavelength_hi',hi); self.shader.uniform_float('wavelength_lo',lo)
            transfer_ms=(time.perf_counter()-start)*1000
            start=time.perf_counter(); self.gpu.compute.dispatch(self.shader,1,1,1)
            raw=[flatten(t.read().to_list()) for t in self.outputs]
            dispatch_ms=(time.perf_counter()-start)*1000
            start=time.perf_counter(); result=decode(batch,*raw)
            if not result['valid']: raise ValueError('resident GPU traversal aborted')
            decode_ms=(time.perf_counter()-start)*1000
            self.calls+=1
            del textures,dynamic  # no host cache of source textures or computed results
            return result,{'input_check_transfer_ms':transfer_ms,'dispatch_sync_readback_ms':dispatch_ms,
                           'decode_ms':decode_ms,'gpu_dispatches':self.calls,
                           'texture_allocations':self.allocations}
        except Exception:
            self.close(); raise

    def close(self):
        self.closed=True
        self.static.clear(); self.outputs.clear()
