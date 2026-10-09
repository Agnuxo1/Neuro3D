"""Experimental GPU fragment graph using actual GPU-derived local coefficients.

CPU supplies admitted topology and coherent input fields. GPU local phases are
obtained solely by querying current captured surfaces with unit incoming field.
No global transfer matrix is supplied. Native equivalence requires a new trial.
"""
import math, struct, time
from fractions import Fraction as F
from Blender.blender_lab.native_graphics_gradient_v2 import exact_double, unpack_complex
from Blender.blender_lab.native_program_lifecycle_v1 import unbind_owned_program
from Blender.blender_lab.native_integer_framebuffer_read_v2 import read_uint_slots

FRAGMENT = r'''
double value(int q,int k){
    uvec2 b=uvec2(input_packet.words[8*q+k/2][2*(k%2)],input_packet.words[8*q+k/2][2*(k%2)+1]);
    return packDouble2x32(b);
}
dvec2 mul(dvec2 a,dvec2 b){return dvec2(a.x*b.x-a.y*b.y,a.x*b.y+a.y*b.x);}
dvec2 coefficient(int n,int branch){
    uvec4 w=graph_packet.words[4*n+branch];
    return dvec2(packDouble2x32(w.xy),packDouble2x32(w.zw));
}
uvec4 bits(dvec2 v){return uvec4(unpackDouble2x32(v.x),unpackDouble2x32(v.y));}
void add(inout dvec2 sum,inout dvec2 error,dvec2 v){
    dvec2 y=v-error,t=sum+y;error=(t-sum)-y;sum=t;
}
void main(){
    int q=int(floor(gl_FragCoord.x));if(q>=query_count)discard;
    if(echo_mode!=0){
        out0=bits(dvec2(value(q,0),value(q,1)));out1=bits(dvec2(value(q,2),value(q,3)));
        out2=bits(dvec2(value(q,4),value(q,5)));out3=bits(dvec2(value(q,6),value(q,7)));
        out4=bits(dvec2(value(q,8),value(q,9)));out5=uvec4(0u);out6=uvec4(0u);out7=uvec4(0u);return;
    }
    dvec2 states[133],correction[133],ports[8],porterror[8];
    for(int n=0;n<133;n++){states[n]=dvec2(0.0LF);correction[n]=dvec2(0.0LF);}
    for(int n=0;n<8;n++){ports[n]=dvec2(0.0LF);porterror[n]=dvec2(0.0LF);}
    for(int r=0;r<5;r++){
        int node=int(root_packet.words[r].x);
        add(states[node],correction[node],dvec2(value(q,2*r),value(q,2*r+1)));
    }
    for(int order=0;order<133;order++){
        int n=int(order_packet.words[order].x);
        uvec4 route=graph_packet.words[4*n+2];
        dvec2 first=mul(coefficient(n,0),states[n]);
        dvec2 second=mul(coefficient(n,1),states[n]);
        if(route.x<133u)add(states[route.x],correction[route.x],first);
        if(route.y<133u)add(states[route.y],correction[route.y],second);
        if(route.z<8u)add(ports[route.z],porterror[route.z],first);
    }
    out0=bits(ports[0]);out1=bits(ports[1]);out2=bits(ports[2]);out3=bits(ports[3]);
    out4=bits(ports[4]);out5=bits(ports[5]);out6=bits(ports[6]);out7=bits(ports[7]);
}
'''


class NativeResidentOpticalGraph:
    def __init__(self, gpu, scene, graph, backend, source_ids):
        from gpu_extras.batch import batch_for_shader
        if len(graph['nodes']) != 133 or len(graph['ports']) != 8 or len(source_ids) != 5 or graph['status'] != 'COMPLETE':
            raise ValueError('Fixed complete captured optical graph required')
        self.gpu, self.graph, self.backend, self.source_ids = gpu, graph, backend, list(source_ids)
        self.generation = backend.geometry_generation
        self.wavelength = exact_double(scene['lambda_BU'])
        nodes = graph['nodes']
        queries = [{'origin': n['origin'], 'direction': n['direction'], 'previous_name': n['previous_plane'][0] if n['previous_plane'] else None} for n in nodes]
        start = time.perf_counter()
        local = backend.query(queries, [1+0j] * 133, [0j] * 133, [(F(0), F(0), F(0))] * 133)
        self.local_coefficient_seconds = time.perf_counter() - start
        if len(local['rows']) != 133:
            raise ValueError('Every coefficient must originate in an actual GPU query')
        packets = []
        for node, row in zip(nodes, local['rows']):
            if row['object'] != node['hit_object'] or row['primitive_id'] not in node['coincident_primitives'] or not row['native_input_bit_echo_verified'] or not row['native_jacobian_bit_echo_verified']:
                raise ValueError('Actual selected-surface and exact input echo required')
            expected = exact_double(node['segment_parameter']) * math.sqrt(sum(exact_double(v)**2 for v in node['direction']))
            if abs(row['distance_BU'] - expected) > 5e-5:
                raise ValueError('Fixed actual surface distance budget required')
            route = [0xffffffff] * 4
            for edge in node['edges']:
                lane = 1 if edge['event'] == 'r' else 0
                if route[lane] != 0xffffffff:
                    raise ValueError('At most one output per local optical branch required')
                route[lane] = edge['target']
            if 'terminal' in node:
                route[2] = graph['ports'].index(node['terminal'])
            packets.append(struct.pack('<4d4I16x', *row['first_reim'], *row['second_reim'], *route))
        self.local_receipt = local
        graph_data = b''.join(packets)
        root_data = b''.join(struct.pack('<4I', next(r['node'] for r in graph['roots'] if r['source_id'] == sid), 0, 0, 0) for sid in source_ids)
        order_data = b''.join(struct.pack('<4I', n, 0, 0, 0) for n in graph['topological_order'])
        # State identity, material/optical properties and topology are fixed by the
        # producer. A geometry generation or wavelength change invalidates use.
        self.scene_identity = repr(scene)
        info = gpu.types.GPUShaderCreateInfo()
        info.vertex_in(0, 'VEC2', 'position')
        for slot in range(8):
            info.fragment_out(slot, 'UVEC4', 'out'+str(slot))
        info.typedef_source('struct InputPacket { uvec4 words[2048]; }; struct GraphPacket { uvec4 words[532]; }; struct RootPacket { uvec4 words[5]; }; struct OrderPacket { uvec4 words[133]; };')
        for binding, typ, name in ((0, 'InputPacket', 'input_packet'), (1, 'GraphPacket', 'graph_packet'), (2, 'RootPacket', 'root_packet'), (3, 'OrderPacket', 'order_packet')):
            info.uniform_buf(binding, typ, name)
        info.push_constant('INT', 'query_count')
        info.push_constant('INT', 'echo_mode')
        info.vertex_source('void main(){gl_Position=vec4(position,0.0,1.0);}')
        info.fragment_source(FRAGMENT)
        unbind_owned_program(gpu)
        self.shader = gpu.shader.create_from_info(info)
        backend.stage_audit.after('resident_optical_graph_shader_creation')
        self.batch = batch_for_shader(self.shader, 'TRIS', {'position': [(-1, -1), (3, -1), (-1, 3)]})
        self.graph_buffer = gpu.types.GPUUniformBuf(graph_data)
        self.root_buffer = gpu.types.GPUUniformBuf(root_data)
        self.order_buffer = gpu.types.GPUUniformBuf(order_data)
        backend.stage_audit.after('resident_actual_coefficient_and_topology_buffers')
        self.draws = 0

    def query(self, inputs, scene):
        if self.generation != self.backend.geometry_generation or self.scene_identity != repr(scene) or self.wavelength != exact_double(scene['lambda_BU']):
            raise ValueError('Actual geometry/material/wavelength cache invalidation required')
        if not 0 < len(inputs) <= 256 or any(len(row) != 5 for row in inputs):
            raise ValueError('Complete coherent five-channel input tile required')
        rows = [[v for z in row for v in (complex(z).real, complex(z).imag)] for row in inputs]
        if not all(math.isfinite(v) for row in rows for v in row):
            raise ValueError('Finite binary64 coherent inputs required')
        data = b''.join(struct.pack('<10d48x', *row) for row in rows)
        input_buffer = self.gpu.types.GPUUniformBuf(data + bytes(32768 - len(data)))
        outputs = [self.gpu.types.GPUTexture((len(inputs), 1), format='RGBA32UI') for _ in range(8)]
        fb = self.gpu.types.GPUFrameBuffer(color_slots=tuple(outputs))
        with fb.bind():
            gpu = self.gpu
            gpu.state.viewport_set(0, 0, len(inputs), 1)
            gpu.state.depth_test_set('NONE');gpu.state.depth_mask_set(False)
            gpu.state.blend_set('NONE');gpu.state.face_culling_set('NONE')
            self.shader.bind()
            for name, value in (('input_packet', input_buffer), ('graph_packet', self.graph_buffer), ('root_packet', self.root_buffer), ('order_packet', self.order_buffer)):
                self.shader.uniform_block(name, value)
            self.shader.uniform_int('query_count', len(inputs))
            self.shader.uniform_int('echo_mode', 0)
            self.backend.stage_audit.after('resident_graph_draw_state_and_binding')
            self.batch.draw(self.shader)
            self.backend.stage_audit.after('resident_graph_all_optical_states_fragment_draw')
            raw, receipt = read_uint_slots(len(inputs), tuple(range(8)))
            self.backend.stage_audit.after('resident_graph_all_eight_modal_integer_readback')
            self.shader.uniform_int('echo_mode', 1)
            self.batch.draw(self.shader)
            self.backend.stage_audit.after('resident_all_five_coherent_input_echo_draw')
            echo, echo_receipt = read_uint_slots(len(inputs), tuple(range(5)))
            self.backend.stage_audit.after('resident_all_five_coherent_input_echo_readback')
        for i, row in enumerate(inputs):
            for source, z in enumerate(row):
                actual = unpack_complex(echo[source][4*i:4*i+4])
                if struct.pack('<dd', actual.real, actual.imag) != struct.pack('<dd', complex(z).real, complex(z).imag):
                    raise ValueError('Every resident coherent input requires exact native binary64 bit echo')
        receipt['all_five_input_bit_echo_verified'] = True
        receipt['input_echo_readback'] = echo_receipt
        self.draws += 2
        return [[unpack_complex(raw[port][4*i:4*i+4]) for port in range(8)] for i in range(len(inputs))], receipt
