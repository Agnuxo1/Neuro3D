"""Deferred native3D optical transport: actual raster G-buffer then FP64 shading.

Geometry candidates come exclusively from this process's captured-triangle GPU
raster readbacks, never expected graph hit IDs. Cache key uses exact represented
rays and previous-plane exclusion. Every actual geometry update clears the cache.
The second shader derives plane distance, phase and tangents from current actual
planes/materials/rays/incoming fields; no transfer/phase/Jacobian matrix is supplied.
CPU exact topology and coherent merges remain explicit.
"""
import hashlib,json,math,struct,time
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit import robust_multipath_v1 as base
from Blender.blender_lab.native_graphics_geometry_v1 import pack_queries
from Blender.blender_lab.native_graphics_gradient_v2 import (NativeGraphicsGradientTransport as ForwardTransport,FRAGMENT as FORWARD_FRAGMENT,exact_double,uniform_bytes,flatten,unpack_complex)

FRAGMENT=FORWARD_FRAGMENT.replace(
    "  if(int(floor(gl_FragCoord.x))!=ray_lane || distance_BU<=0.0)discard;\n  int q=ray_lane,o=object_index;",
    "  int q=int(floor(gl_FragCoord.x)); if(q<0 || q>=query_count)discard;\n  vec4 selected=texelFetch(actual_candidates,ivec2(q,0),0);\n  if(selected.w!=1.0 || selected.y<=0.0)discard;\n  int object_index=int(selected.x),triangle_index=int(selected.z); float distance_BU=selected.y;\n  int o=object_index;")

def ray_key(query):
    return (tuple(exact_double(v).hex() for v in query['origin']),tuple(exact_double(v).hex() for v in query['direction']),query.get('previous_name'))

class NativeDeferredGraphicsGradientTransport(ForwardTransport):
    def __init__(self,gpu,scene,*,pixel_BU,far_BU,stage_audit_path):
        from gpu_extras.batch import batch_for_shader
        super().__init__(gpu,scene,pixel_BU=pixel_BU,far_BU=far_BU,stage_audit_path=stage_audit_path)
        self.selector_shader,self.selector_batch=self.shader,self.batch
        self.candidate_cache={};self.geometry_generation=0;self.native_triangle_surface_queries=0;self.optical_fragment_queries=0;self.candidate_receipts=[]
        info=gpu.types.GPUShaderCreateInfo();info.vertex_in(0,'VEC2','position')
        for slot,typ,name in [(0,'VEC4','out_color'),(1,'UVEC4','out_propagated'),(2,'UVEC4','out_first'),(3,'UVEC4','out_second'),(4,'UVEC4','out_input_echo'),(5,'UVEC4','out_raw_echo')]:info.fragment_out(slot,typ,name)
        info.sampler(0,'FLOAT_2D','actual_candidates');info.typedef_source('struct RayPacket { uvec4 words[2048]; }; struct ObjectPacket { uvec4 words[2048]; };');info.uniform_buf(0,'RayPacket','ray_packet');info.uniform_buf(1,'ObjectPacket','object_packet')
        info.push_constant('INT','query_count');info.push_constant('INT','echo_mode')
        info.vertex_source('void main(){gl_Position=vec4(position,0.0,1.0);}')
        info.fragment_source(FRAGMENT);self.shader=gpu.shader.create_from_info(info);self.stage_audit.after('deferred_FP64_optical_shader_creation')
        self.batch=batch_for_shader(self.shader,'TRIS',{'position':[(-1,-1),(3,-1),(-1,3)]});self.stage_audit.after('deferred_fullscreen_triangle_creation')

    def update_geometry(self,scene):
        optical_shader,optical_batch=self.shader,self.batch
        try:
            self.shader,self.batch=self.selector_shader,self.selector_batch
            super().update_geometry(scene)
            self.selector_batch=self.batch
        finally:self.shader,self.batch=optical_shader,optical_batch
        self.candidate_cache={};self.geometry_generation+=1
        self.stage_audit.after('deferred_actual_geometry_cache_invalidation')

    def selected_candidates(self,queries):
        unique={}
        for q in queries:
            key=ray_key(q)
            if key not in self.candidate_cache:unique.setdefault(key,q)
        if unique:
            keys=list(unique);qs=list(unique.values());optical_shader,optical_batch=self.shader,self.batch
            try:
                self.shader,self.batch=self.selector_shader,self.selector_batch
                # <=133 distinct rays in the declared captured family: no recursion.
                if len(qs)>256:raise ValueError('Bounded native candidate cache fill required')
                raw=ForwardTransport.query(self,qs,[0j]*len(qs),[0j]*len(qs),[(F(0),F(0),F(0))]*len(qs))
            finally:self.shader,self.batch=optical_shader,optical_batch
            if len(raw['rows'])!=len(keys):raise ValueError('Complete actual raster G-buffer readback required')
            for key,row in zip(keys,raw['rows']):self.candidate_cache[key]=row
            self.native_triangle_surface_queries+=len(keys)
            self.candidate_receipts.append({'generation':self.geometry_generation,'exact_ray_keys':keys,'actual_gpu_readback':raw})
        return [self.candidate_cache[ray_key(q)] for q in queries]

    def surface_receipt(self):
        return {'schema':'optic_neuro_blender.deferred_actual_surface_provenance.v1','native_triangle_surface_queries':self.native_triangle_surface_queries,'optical_fragment_queries_including_echo':self.optical_fragment_queries,'geometry_generations':self.geometry_generation,'fills':self.candidate_receipts,'scope':'Every candidate originated in actual captured-triangle raster/depth draw. Exact-ray key and generation reset; second shader independently derives phase/tangent from selected-surface current planes/materials and incoming fields. CPU exact admission and coherent merges explicit.'}

    def query(self,queries,fields,jacobians,origin_jets):
        if not len(queries)==len(fields)==len(jacobians)==len(origin_jets):raise ValueError('One geometric tangent and field derivative per ray required')
        if len(queries)>256:
            start=time.perf_counter();blocks=[self.query(queries[i:i+256],fields[i:i+256],jacobians[i:i+256],origin_jets[i:i+256]) for i in range(0,len(queries),256)]
            return {'rows':[row for block in blocks for row in block['rows']],'setup_seconds':sum(b['setup_seconds'] for b in blocks),'draw_and_readback_seconds':sum(b['draw_and_readback_seconds'] for b in blocks),'full_seconds':time.perf_counter()-start,'native_fp64_fragment_transport':True,'uniform_buffer_draw_batches':len(blocks),'native_integer_readback_transactions':[b['native_integer_readback'] for b in blocks]}
        fields_input=fields
        candidates=self.selected_candidates(queries)
        gpu=self.gpu;n=len(queries);start=time.perf_counter();origins,directions=pack_queries(queries,self.names)
        scalars=[]
        for q,z,j,origin_j in zip(queries,fields,jacobians,origin_jets):
            z=complex(z);j=complex(j);scalars.append([*[exact_double(v) for v in q['origin']],*[exact_double(v) for v in q['direction']],z.real,z.imag,self.wavelength,*[exact_double(v) for v in origin_j],j.real,j.imag])
        bits=gpu.types.GPUUniformBuf(uniform_bytes(scalars,14));self.stage_audit.after('ray_UBO_creation')
        candidate_values=[v for row in candidates for v in (self.names.index(row['object']),row['distance_BU'],row['primitive_id'],1.0)]
        candidate_texture=gpu.types.GPUTexture((n,1),format='RGBA32F',data=gpu.types.Buffer('FLOAT',len(candidate_values),candidate_values))
        color=gpu.types.GPUTexture((n,1),format='RGBA32F');outputs=[gpu.types.GPUTexture((n,1),format='RGBA32UI') for _ in range(5)];depth=gpu.types.GPUTexture((n,1),format='DEPTH_COMPONENT32F');fb=gpu.types.GPUFrameBuffer(depth_slot=depth,color_slots=(color,*outputs));setup=time.perf_counter()-start;self.stage_audit.after('ray_textures_and_framebuffer_creation')
        t=time.perf_counter()
        with fb.bind():
            self.stage_audit.after('framebuffer_bind');color.clear(format="FLOAT",value=(0,0,0,0));self.stage_audit.after('float_geometry_texture_clear');fb.clear(depth=1.0);self.stage_audit.after('depth_only_clear');gpu.state.viewport_set(0,0,n,1);gpu.state.depth_test_set('NONE');gpu.state.depth_mask_set(True);gpu.state.blend_set('NONE');gpu.state.face_culling_set('NONE');self.stage_audit.after('graphics_draw_state')
            try:
                self.shader.bind();self.stage_audit.after('field_shader_bind');self.shader.uniform_sampler('actual_candidates',candidate_texture);self.shader.uniform_block('ray_packet',bits);self.shader.uniform_block('object_packet',self.objects);self.stage_audit.after('sampler_and_UBO_binding')
                self.shader.uniform_int('query_count',n);self.shader.uniform_int('echo_mode',0);self.stage_audit.after('scalar_uniform_binding');self.batch.draw(self.shader);self.stage_audit.after('instanced_triangle_draw')
                from Blender.blender_lab.native_integer_framebuffer_read_v1 import read_uint_slots
                raw,readback_identity=read_uint_slots(n,(1,2,3,4,5));geometry=flatten(color.read().to_list());self.stage_audit.after('exact_integer_and_float_readback')
                self.shader.uniform_int('echo_mode',1);fb.clear(depth=1.0);self.stage_audit.after('derivative_echo_depth_reset')
                self.batch.draw(self.shader);self.stage_audit.after('derivative_echo_triangle_draw')
                echo_j,echo_identity=read_uint_slots(n,(5,));geometry_j=flatten(color.read().to_list());self.stage_audit.after('derivative_echo_exact_readback')
                if geometry_j!=geometry or geometry!=candidate_values:raise ValueError('Both deferred optical draws must echo the exact actual GPU selected-surface payload')
                self.stage_audit.finish()
            finally:gpu.state.depth_test_set('NONE');gpu.state.depth_mask_set(False)
        draw_readback=time.perf_counter()-t
        if len(geometry)!=4*n or any(len(row)!=4*n for row in raw):raise ValueError('Complete geometry and FP64 field readbacks required')
        if getattr(self,'diagnostic_path',None) is not None and not self.diagnostic_path.exists():
            import json
            diagnostics={'schema':'optic_neuro_blender.native_graphics_word_diagnostic.v1','queries':n,'input_fields_hex':[[complex(z).real.hex(),complex(z).imag.hex()] for z in fields_input[:8]],'geometry_rgba':geometry[:32],'readback_slots_uint_words':[a[:32] for a in raw],'uploaded_ubo_first_160_bytes_hex':uniform_bytes(scalars,14)[:160].hex(),'slot_layout':['propagated','first','second','double_input_echo','raw_ubo_input_echo'],'field_shader_compiled_and_draw_readback_reached':True}
            self.diagnostic_path.write_bytes((json.dumps(diagnostics,indent=2)+'\n').encode())
        rows=[]
        for j in range(n):
            obj,distance,primitive,valid=geometry[4*j:4*j+4]
            if valid!=1 or obj!=int(obj) or primitive!=int(primitive) or not 0<=obj<len(self.names) or not 0<=primitive<self.triangle_count or distance<=0:raise ValueError('Every coherent transport ray requires actual depth-selected surface')
            fields=[unpack_complex(values[4*j:4*j+4]) for values in raw]
            if struct.pack('<dd',fields[4].real,fields[4].imag)!=struct.pack('<dd',complex(fields_input[j]).real,complex(fields_input[j]).imag):raise ValueError('Native GPU incoming binary64 echo differs from exact uploaded field')
            actual_j=unpack_complex(echo_j[0][4*j:4*j+4]);expected_j=complex(jacobians[j])
            if struct.pack('<dd',actual_j.real,actual_j.imag)!=struct.pack('<dd',expected_j.real,expected_j.imag):raise ValueError('Exact incoming derivative binary64 echo required')
            rows.append({'object':self.names[int(obj)],'primitive_id':int(primitive),'distance_BU':distance,'first_jacobian_reim':[fields[0].real,fields[0].imag],'first_reim':[fields[1].real,fields[1].imag],'second_reim':[fields[2].real,fields[2].imag],'second_jacobian_reim':[fields[3].real,fields[3].imag],'input_echo_reim':[fields[4].real,fields[4].imag],'jacobian_echo_reim':[actual_j.real,actual_j.imag],'native_input_bit_echo_verified':True,'native_jacobian_bit_echo_verified':True})
        self.optical_fragment_queries+=2*n
        return {'rows':rows,'deferred_actual_gpu_surface_cache':True,'geometry_generation':self.geometry_generation,'setup_seconds':setup,'draw_and_readback_seconds':draw_readback,'full_seconds':time.perf_counter()-start,'native_fp64_fragment_transport':True,'native_integer_readback':readback_identity,'native_jacobian_echo_readback':echo_identity,'actual_triangle_draws':2}
