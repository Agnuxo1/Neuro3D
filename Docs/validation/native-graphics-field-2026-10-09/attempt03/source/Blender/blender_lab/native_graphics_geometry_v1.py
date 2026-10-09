"""Nearest-surface candidates from Blender's native instanced raster pipeline.

Actual triangle vertices feed a vertex buffer; depth testing selects surfaces.
No matrix weights or expected hits feed the shader. Float32 candidates require
separate exact geometry validation before coherent propagation. This is raster
graphics, not an assertion that RT cores or OptiX were executed.
"""
import math,time

VERTEX=r'''
void main() {
  int lane=gl_InstanceID;
  vec4 origin=texelFetch(ray_origins,ivec2(lane,0),0);
  vec3 direction=normalize(texelFetch(ray_directions,ivec2(lane,0),0).xyz);
  vec3 up=abs(direction.z)<0.9 ? vec3(0,0,1) : vec3(0,1,0);
  vec3 u=normalize(cross(up,direction));
  vec3 v=cross(direction,u);
  vec3 relative=position-origin.xyz;
  float distance=dot(relative,direction);
  ray_lane=lane; object_index=int(object_id); triangle_index=int(primitive_id);
  distance_BU=distance;
  gl_Position=vec4((float(lane)+0.5+dot(relative,u)/pixel_BU)*2.0/float(query_count)-1.0,
                   dot(relative,v)*2.0/pixel_BU,distance*2.0/far_BU-1.0,1.0);
  // The caller proves that the previous planar object is exactly at t=0.
  // No positive-distance epsilon, energy pruning or hidden CPU hit is used.
  if (int(origin.w)==int(object_id)) gl_Position=vec4(2,2,2,1);
}
'''
FRAGMENT=r'''
void main() {
  if (int(floor(gl_FragCoord.x))!=ray_lane || distance_BU<=0.0) discard;
  out_color=vec4(float(object_index),distance_BU,float(triangle_index),1.0);
}
'''


def pack_geometry(scene):
    names=list(scene['objects']);positions=[];objects=[];primitives=[];primitive=0
    if not names:raise ValueError('nonempty captured triangle geometry required')
    for index,name in enumerate(names):
        obj=scene['objects'][name]
        for face in obj['faces']:
            if len(face)!=3 or len(set(face))!=3:raise ValueError('explicit nondegenerate triangle indices required')
            for k in face:
                value=tuple(float(v) for v in obj['vertices_world_BU'][k])
                if len(value)!=3 or not all(math.isfinite(v) for v in value):raise ValueError('finite evaluated world vertices required')
                positions.append(value);objects.append(float(index));primitives.append(float(primitive))
            primitive+=1
    if not 1<=primitive<=100000:raise ValueError('bounded explicit triangle count required')
    return names,{'position':positions,'object_id':objects,'primitive_id':primitives},primitive


def pack_queries(queries,names):
    if not 1<=len(queries)<=4096:raise ValueError('bounded native graphics batch required')
    origins=[];directions=[]
    for q in queries:
        if set(q)!={'origin','direction','previous_name'}:raise ValueError('only geometric query inputs allowed; no expected-hit feedback')
        o=[float(v) for v in q['origin']];d=[float(v) for v in q['direction']];previous=q['previous_name']
        if len(o)!=3 or len(d)!=3 or not all(math.isfinite(v) for v in o+d) or not any(d):raise ValueError('finite nonzero geometric ray required')
        if previous is not None and previous not in names:raise ValueError('declared previous object required')
        origins.extend(o+[float(names.index(previous)) if previous is not None else -1.0]);directions.extend(d+[0.0])
    return origins,directions


class NativeGraphicsCandidates:
    def __init__(self,gpu,scene,*,pixel_BU,far_BU):
        from gpu_extras.batch import batch_for_shader
        self.gpu=gpu;self.pixel_BU=pixel_BU;self.far_BU=far_BU;start=time.perf_counter()
        self.names,data,self.triangle_count=pack_geometry(scene)
        interface=gpu.types.GPUStageInterfaceInfo('geometry_views')
        interface.flat('INT','ray_lane');interface.flat('INT','object_index');interface.flat('INT','triangle_index');interface.smooth('FLOAT','distance_BU')
        info=gpu.types.GPUShaderCreateInfo();info.vertex_in(0,'VEC3','position');info.vertex_in(1,'FLOAT','object_id');info.vertex_in(2,'FLOAT','primitive_id')
        info.vertex_out(interface);info.fragment_out(0,'VEC4','out_color')
        info.sampler(0,'FLOAT_2D','ray_origins');info.sampler(1,'FLOAT_2D','ray_directions')
        info.push_constant('INT','query_count');info.push_constant('FLOAT','pixel_BU');info.push_constant('FLOAT','far_BU')
        info.vertex_source(VERTEX);info.fragment_source(FRAGMENT)
        self.shader=gpu.shader.create_from_info(info);self.batch=batch_for_shader(self.shader,'TRIS',data)
        self.compile_pack_upload_seconds=time.perf_counter()-start

    def query(self,queries):
        gpu=self.gpu;n=len(queries);start=time.perf_counter();origins,directions=pack_queries(queries,self.names)
        rays=[gpu.types.GPUTexture((n,1),format='RGBA32F',data=gpu.types.Buffer('FLOAT',len(values),values)) for values in (origins,directions)]
        color=gpu.types.GPUTexture((n,1),format='RGBA32F');depth=gpu.types.GPUTexture((n,1),format='DEPTH_COMPONENT32F');framebuffer=gpu.types.GPUFrameBuffer(depth_slot=depth,color_slots=(color,))
        setup=time.perf_counter()-start;render_start=time.perf_counter()
        with framebuffer.bind():
            framebuffer.clear(color=(-1,-1,-1,0),depth=1.0);gpu.state.viewport_set(0,0,n,1);gpu.state.depth_test_set('LESS');gpu.state.depth_mask_set(True);gpu.state.blend_set('NONE');gpu.state.face_culling_set('NONE')
            try:
                self.shader.bind();self.shader.uniform_sampler('ray_origins',rays[0]);self.shader.uniform_sampler('ray_directions',rays[1]);self.shader.uniform_int('query_count',n);self.shader.uniform_float('pixel_BU',self.pixel_BU);self.shader.uniform_float('far_BU',self.far_BU)
                self.batch.draw_instanced(self.shader,instance_count=n)
                values=list(color.read().to_list())
            finally:gpu.state.depth_test_set('NONE');gpu.state.depth_mask_set(False)
        def flatten(v):return [x for child in v for x in flatten(child)] if isinstance(v,(list,tuple)) else [v]
        values=flatten(values);render_seconds=time.perf_counter()-render_start
        if len(values)!=4*n or not all(math.isfinite(x) for x in values):raise ValueError('complete finite native framebuffer readback required')
        rows=[]
        for j in range(n):
            obj,distance,primitive,valid=values[4*j:4*j+4]
            if valid==0:rows.append({'status':'MISS','raw_rgba':[obj,distance,primitive,valid]});continue
            if valid!=1 or obj!=int(obj) or primitive!=int(primitive) or not 0<=obj<len(self.names) or not 0<=primitive<self.triangle_count or distance<=0:raise ValueError('malformed depth-selected graphics candidate')
            rows.append({'status':'GRAPHICS_SURFACE_CANDIDATE','object':self.names[int(obj)],'distance_BU':distance,'primitive_id':int(primitive),'raw_rgba':[obj,distance,primitive,valid]})
        return {'rows':rows,'setup_seconds':setup,'draw_sync_readback_seconds':render_seconds,'total_query_seconds':time.perf_counter()-start,'vertex_instances':3*self.triangle_count*n}
