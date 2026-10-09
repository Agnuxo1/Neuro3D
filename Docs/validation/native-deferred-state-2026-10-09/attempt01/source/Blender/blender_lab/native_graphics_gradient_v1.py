"""FP64 coherent fields and translation tangents on captured triangle surfaces.

The shader receives captured planes/materials, current geometric rays and
incoming complex fields. It derives distance, phase and optical branches;
no expected hits or precomputed transfer coefficients enter the shader.
CPU exact admission and compensated coherent merging remain explicit.
"""
import math,struct,time
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit import robust_multipath_v1 as base
from Blender.blender_lab.native_graphics_geometry_v1 import VERTEX,pack_geometry,pack_queries


FRAGMENT=r'''
const double PI=3.141592653589793238462643383279502884LF;
uint rayword(int q,int k){return ray_packet.words[8*q+k/4][k%4];}
uint objectword(int q,int k){return object_packet.words[8*q+k/4][k%4];}
double raynumber(int q,int k){return packDouble2x32(uvec2(rayword(q,2*k),rayword(q,2*k+1)));}
double objectnumber(int q,int k){return packDouble2x32(uvec2(objectword(q,2*k),objectword(q,2*k+1)));}
dvec2 multiply(dvec2 a,dvec2 b){return dvec2(a.x*b.x-a.y*b.y,a.x*b.y+a.y*b.x);}
dvec2 phase(double angle){
  double x=angle-floor(angle/(2.0LF*PI)+0.5LF)*(2.0LF*PI);
  double square=x*x,sine=x,cosine=1.0LF,st=x,ct=1.0LF;
  for(int k=1;k<32;++k){
    st*=-square/(double(2*k)*double(2*k+1));
    ct*=-square/(double(2*k-1)*double(2*k));
    sine+=st;cosine+=ct;
  }
  return dvec2(cosine,sine);
}
dvec2 segment(double parameter,dvec3 direction,double wavelength){
  double cycles=parameter*sqrt(dot(direction,direction))/wavelength;
  cycles-=floor(cycles);
  return phase(2.0LF*PI*cycles);
}
uvec4 words(dvec2 value){return uvec4(unpackDouble2x32(value.x),unpackDouble2x32(value.y));}
void main(){
  if(int(floor(gl_FragCoord.x))!=ray_lane || distance_BU<=0.0)discard;
  int q=ray_lane,o=object_index;
  dvec3 origin=dvec3(raynumber(q,0),raynumber(q,1),raynumber(q,2));
  dvec3 direction=dvec3(raynumber(q,3),raynumber(q,4),raynumber(q,5));
  dvec2 incoming=dvec2(raynumber(q,6),raynumber(q,7));
  double wavelength=raynumber(q,8);
  dvec3 origin_j=dvec3(raynumber(q,9),raynumber(q,10),raynumber(q,11));
  dvec2 incoming_j=dvec2(raynumber(q,12),raynumber(q,13));
  dvec3 normal=dvec3(objectnumber(o,0),objectnumber(o,1),objectnumber(o,2));
  double parameter=(objectnumber(o,3)-dot(normal,origin))/dot(normal,direction);
  double parameter_j=(objectnumber(o,10)-dot(normal,origin_j))/dot(normal,direction);
  dvec2 coefficient=segment(parameter,direction,wavelength);
  dvec2 propagated=multiply(incoming,coefficient);
  double angle_j=2.0LF*PI*parameter_j*sqrt(dot(direction,direction))/wavelength;
  dvec2 propagated_j=multiply(incoming_j,coefficient)+angle_j*dvec2(-propagated.y,propagated.x);
  int kind=int(objectnumber(o,9));dvec2 first,second=dvec2(0.0LF),first_j,second_j=dvec2(0.0LF);
  if(kind==0){
    double tau=objectnumber(o,4);
    first=sqrt(tau)*propagated;first_j=sqrt(tau)*propagated_j;
    second=sqrt(1.0LF-tau)*dvec2(-propagated.y,propagated.x);
    second_j=sqrt(1.0LF-tau)*dvec2(-propagated_j.y,propagated_j.x);
  }else if(kind==1){first=-multiply(propagated,phase(objectnumber(o,5)));first_j=-multiply(propagated_j,phase(objectnumber(o,5)));}
  else{
    dvec3 reference=dvec3(objectnumber(o,6),objectnumber(o,7),objectnumber(o,8));
    dvec3 point=origin+parameter*direction;
    double reference_parameter=dot(direction,reference-point)/dot(direction,direction);
    dvec3 reference_j=dvec3(objectnumber(o,11),objectnumber(o,12),objectnumber(o,13));
    dvec3 point_j=origin_j+parameter_j*direction;
    double reference_parameter_j=dot(direction,reference_j-point_j)/dot(direction,direction);
    dvec2 reference_coefficient=segment(reference_parameter,direction,wavelength);
    first=multiply(propagated,reference_coefficient);
    double reference_angle_j=2.0LF*PI*reference_parameter_j*sqrt(dot(direction,direction))/wavelength;
    first_j=multiply(propagated_j,reference_coefficient)+reference_angle_j*dvec2(-first.y,first.x);
  }
  out_color=vec4(float(object_index),distance_BU,float(triangle_index),1.0);
  out_propagated=words(first_j);out_first=words(first);out_second=words(second);out_input_echo=words(second_j);out_raw_echo=words(echo_mode==0?incoming:incoming_j);
}
'''


def exact_double(value):
    v=F(value);f=float(v)
    if not math.isfinite(f) or F(f)!=v:raise ValueError('Exactly representable binary64 geometry/material required')
    return f


def texture_words(rows,count):
    """Little-endian binary64 word transport, row-major RGBA32UI storage."""
    if not rows or any(len(r)!=count for r in rows):raise ValueError('Fixed nonempty scalar extent required')
    packed=[]
    for row in rows:
        if not all(math.isfinite(float(v)) for v in row):raise ValueError('Finite binary64 inputs required')
        words=[]
        for v in row:words.extend(struct.unpack('<II',struct.pack('<d',float(v))))
        words.extend([0]*((-len(words))%4));packed.append(words)
    height=(2*count+3)//4
    return [word for y in range(height) for row in packed for word in row[4*y:4*y+4]],height


def unpack_complex(words):
    if len(words)!=4 or any(type(v)!=int or not 0<=v<2**32 for v in words):raise ValueError('Four unsigned binary64 words required')
    value=complex(struct.unpack('<d',struct.pack('<II',*words[:2]))[0],struct.unpack('<d',struct.pack('<II',*words[2:]))[0])
    if not math.isfinite(value.real) or not math.isfinite(value.imag):raise ValueError('Finite native complex readback required')
    return value


def captured_object_scalars(scene,names):
    _,objects,triangles=base.geometry(scene);first={}
    for tri in triangles:first.setdefault(tri['object_id'],tri)
    result=[]
    for name in names:
        tri=first[name];a,b,c=tri['vertices'];n=base.cross(base.sub(b,a),base.sub(c,a));pivot=next(v for v in n if v);n=tuple(v/pivot for v in n);offset=base.dot(n,a)
        if any(base.dot(n,base.vector(v))!=offset for v in scene['objects'][name]['vertices_world_BU']):raise ValueError('Exactly planar captured object required')
        obj=objects[name];kind=0 if obj['kind']=='bs' else 1 if obj['kind']=='mirror' else 2
        values=[*n,offset,obj.get('tau',0),obj.get('phase',0),*obj.get('reference',(0,0,0)),kind]
        result.append([exact_double(v) for v in values])
    return result


def flatten(v):return [x for child in v for x in flatten(child)] if isinstance(v,(list,tuple)) else [v]


class NativeGraphicsGradientTransport:
    def __init__(self,gpu,scene,*,pixel_BU,far_BU,stage_audit_path):
        from gpu_extras.batch import batch_for_shader
        from Blender.blender_lab.native_graphics_debug_stage_audit_v2 import GraphicsStageAudit
        self.stage_audit=GraphicsStageAudit(stage_audit_path)
        self.gpu=gpu;self.pixel_BU=pixel_BU;self.far_BU=far_BU;start=time.perf_counter();self.wavelength=exact_double(base.rational(scene['lambda_BU']))
        self.names,data,self.triangle_count=pack_geometry(scene)
        self.object_scalars=[row+[0.0]*4 for row in captured_object_scalars(scene,self.names)]
        self.objects=gpu.types.GPUUniformBuf(uniform_bytes(self.object_scalars,14));self.stage_audit.after('object_UBO_creation')
        interface=gpu.types.GPUStageInterfaceInfo('field_geometry_views')
        interface.flat('INT','ray_lane');interface.flat('INT','object_index');interface.flat('INT','triangle_index');interface.smooth('FLOAT','distance_BU')
        info=gpu.types.GPUShaderCreateInfo();info.vertex_in(0,'VEC3','position');info.vertex_in(1,'FLOAT','object_id');info.vertex_in(2,'FLOAT','primitive_id');info.vertex_out(interface)
        info.fragment_out(0,'VEC4','out_color');info.fragment_out(1,'UVEC4','out_propagated');info.fragment_out(2,'UVEC4','out_first');info.fragment_out(3,'UVEC4','out_second');info.fragment_out(4,'UVEC4','out_input_echo');info.fragment_out(5,'UVEC4','out_raw_echo')
        info.sampler(0,'FLOAT_2D','ray_origins');info.sampler(1,'FLOAT_2D','ray_directions');info.typedef_source('struct RayPacket { uvec4 words[2048]; }; struct ObjectPacket { uvec4 words[2048]; };');info.uniform_buf(0,'RayPacket','ray_packet');info.uniform_buf(1,'ObjectPacket','object_packet')
        info.push_constant('INT','query_count');info.push_constant('INT','echo_mode');info.push_constant('FLOAT','pixel_BU');info.push_constant('FLOAT','far_BU');info.vertex_source(VERTEX);info.fragment_source(FRAGMENT)
        self.shader=gpu.shader.create_from_info(info);self.stage_audit.after('shader_creation');self.batch=batch_for_shader(self.shader,'TRIS',data);self.stage_audit.after('captured_triangle_VBO_creation')
        self.compile_pack_upload_seconds=time.perf_counter()-start

    def set_parameter(self,shifts):
        rows=[]
        for name,original in zip(self.names,self.object_scalars):
            row=list(original);shift=shifts[name]
            row[10]=exact_double(sum((F(row[k])*F(shift[k]) for k in range(3)),F(0)))
            row[11:14]=[exact_double(v) for v in shift]
            rows.append(row)
        self.objects=self.gpu.types.GPUUniformBuf(uniform_bytes(rows,14))
        self.stage_audit.after('parameter_displacement_object_UBO_creation')

    def query(self,queries,fields,jacobians,origin_jets):
        if not len(queries)==len(fields)==len(jacobians)==len(origin_jets):raise ValueError('One geometric tangent and field derivative per ray required')
        if len(queries)>256:
            start=time.perf_counter();blocks=[self.query(queries[i:i+256],fields[i:i+256],jacobians[i:i+256],origin_jets[i:i+256]) for i in range(0,len(queries),256)]
            return {'rows':[row for block in blocks for row in block['rows']],'setup_seconds':sum(b['setup_seconds'] for b in blocks),'draw_and_readback_seconds':sum(b['draw_and_readback_seconds'] for b in blocks),'full_seconds':time.perf_counter()-start,'native_fp64_fragment_transport':True,'uniform_buffer_draw_batches':len(blocks),'native_integer_readback_transactions':[b['native_integer_readback'] for b in blocks]}
        fields_input=fields
        gpu=self.gpu;n=len(queries);start=time.perf_counter();origins,directions=pack_queries(queries,self.names)
        scalars=[]
        for q,z,j,origin_j in zip(queries,fields,jacobians,origin_jets):
            z=complex(z);j=complex(j);scalars.append([*[exact_double(v) for v in q['origin']],*[exact_double(v) for v in q['direction']],z.real,z.imag,self.wavelength,*[exact_double(v) for v in origin_j],j.real,j.imag])
        bits=gpu.types.GPUUniformBuf(uniform_bytes(scalars,14));self.stage_audit.after('ray_UBO_creation')
        rays=[gpu.types.GPUTexture((n,1),format='RGBA32F',data=gpu.types.Buffer('FLOAT',len(values),values)) for values in (origins,directions)]
        color=gpu.types.GPUTexture((n,1),format='RGBA32F');outputs=[gpu.types.GPUTexture((n,1),format='RGBA32UI') for _ in range(5)];depth=gpu.types.GPUTexture((n,1),format='DEPTH_COMPONENT32F');fb=gpu.types.GPUFrameBuffer(depth_slot=depth,color_slots=(color,*outputs));setup=time.perf_counter()-start;self.stage_audit.after('ray_textures_and_framebuffer_creation')
        t=time.perf_counter()
        with fb.bind():
            self.stage_audit.after('framebuffer_bind');color.clear(format="FLOAT",value=(0,0,0,0));self.stage_audit.after('float_geometry_texture_clear');fb.clear(depth=1.0);self.stage_audit.after('depth_only_clear');gpu.state.viewport_set(0,0,n,1);gpu.state.depth_test_set('LESS');gpu.state.depth_mask_set(True);gpu.state.blend_set('NONE');gpu.state.face_culling_set('NONE');self.stage_audit.after('graphics_draw_state')
            try:
                self.shader.bind();self.stage_audit.after('field_shader_bind');self.shader.uniform_sampler('ray_origins',rays[0]);self.shader.uniform_sampler('ray_directions',rays[1]);self.shader.uniform_block('ray_packet',bits);self.shader.uniform_block('object_packet',self.objects);self.stage_audit.after('sampler_and_UBO_binding')
                self.shader.uniform_int('query_count',n);self.shader.uniform_int('echo_mode',0);self.shader.uniform_float('pixel_BU',self.pixel_BU);self.shader.uniform_float('far_BU',self.far_BU);self.stage_audit.after('scalar_uniform_binding');self.batch.draw_instanced(self.shader,instance_count=n);self.stage_audit.after('instanced_triangle_draw')
                from Blender.blender_lab.native_integer_framebuffer_read_v1 import read_uint_slots
                raw,readback_identity=read_uint_slots(n,(1,2,3,4,5));geometry=flatten(color.read().to_list());self.stage_audit.after('exact_integer_and_float_readback')
                self.shader.uniform_int('echo_mode',1);fb.clear(depth=1.0);self.stage_audit.after('derivative_echo_depth_reset')
                self.batch.draw_instanced(self.shader,instance_count=n);self.stage_audit.after('derivative_echo_triangle_draw')
                echo_j,echo_identity=read_uint_slots(n,(5,));geometry_j=flatten(color.read().to_list());self.stage_audit.after('derivative_echo_exact_readback')
                if geometry_j!=geometry:raise ValueError('Derivative echo requires identical selected surfaces')
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
        return {'rows':rows,'setup_seconds':setup,'draw_and_readback_seconds':draw_readback,'full_seconds':time.perf_counter()-start,'native_fp64_fragment_transport':True,'native_integer_readback':readback_identity,'native_jacobian_echo_readback':echo_identity,'actual_triangle_draws':2}


def uniform_bytes(rows,count):
    if not 0<len(rows)<=256 or count!=14 or any(len(row)!=count for row in rows):raise ValueError('Bounded fixed UBO extent required')
    if not all(math.isfinite(float(v)) for row in rows for v in row):raise ValueError('Finite UBO binary64 required')
    data=b''.join(struct.pack('<'+'d'*count,*row)+bytes((16-count)*8) for row in rows)
    return data+bytes(256*128-len(data))
