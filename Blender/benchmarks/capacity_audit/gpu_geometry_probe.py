"""Raw geometry/ray ABI and native Blender GPU nearest-hit probe, not RT.

No optical field, expected intersection, CPU traversal or Blender import here.
Reference ray inputs may originate from prior CPU traces: a component audit only.
"""
from dataclasses import dataclass
import math
from numbers import Real
from pathlib import Path

MAX_TRIANGLES=256
MAX_QUERIES=256
BIAS=1e-6
SHADER=Path(__file__).parents[2]/'shaders'/'exp005_intersections.glsl'


def vector(value):
    if len(value)!=3 or any(isinstance(x,bool) or not isinstance(x,Real) or not math.isfinite(x) or abs(x)>1e6 for x in value):
        raise ValueError('bounded finite three-vector required')
    return tuple(float(x) for x in value)


@dataclass(frozen=True)
class GeometryBatch:
    object_ids: tuple
    triangles: tuple
    rays: tuple

    @property
    def triangle_count(self): return len(self.triangles)//12

    @property
    def query_count(self): return len(self.rays)//8


def pack_geometry(snapshot,queries):
    if snapshot['schema'] not in ('exp005-readback-v1','exp005-readback-v2') or snapshot['undeclared_meshes']:
        raise ValueError('explicit complete geometry readback required')
    if not 1<=len(queries)<=MAX_QUERIES or not snapshot['objects']:
        raise ValueError('bounded nonempty ray/geometry batch required')
    names=tuple(snapshot['objects']); triangles=[]; rays=[]
    for index,(name,obj) in enumerate(snapshot['objects'].items()):
        if obj['kind'] not in ('bs','mirror','det','escape'): raise ValueError('unknown optical geometry')
        vertices=[vector(v) for v in obj['vertices_world_BU']]
        if not obj['faces']: raise ValueError('nonempty triangles required')
        for face in obj['faces']:
            if (len(face)!=3 or len(set(face))!=3 or any(isinstance(i,bool) or not isinstance(i,int) or not 0<=i<len(vertices) for i in face)):
                raise ValueError('valid triangulated geometry required')
            a,b,c=(vertices[i] for i in face)
            u,v=[tuple(p-q for p,q in zip(end,a)) for end in (b,c)]
            cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            if math.hypot(*cross)==0: raise ValueError('degenerate triangle')
            triangles.extend((*a,float(index),*b,0.,*c,0.))
            if len(triangles)//12>MAX_TRIANGLES: raise ValueError('triangle bound exceeded')
    for ray in queries:
        origin,direction=vector(ray['origin_BU']),vector(ray['direction'])
        if math.hypot(*direction)==0: raise ValueError('nonzero ray direction required')
        rays.extend((*origin,BIAS,*direction,0.))  # Normalization/intersections happen GPU.
    return GeometryBatch(names,tuple(triangles),tuple(rays))


def decode_hits(batch,hits,normals):
    if len(hits)!=4*batch.query_count or len(normals)!=len(hits) or any(not math.isfinite(v) for v in (*hits,*normals)):
        raise ValueError('complete finite GPU hit readback required')
    results=[]
    for i in range(batch.query_count):
        distance,obj,primitive,status=hits[4*i:4*i+4]
        normal=normals[4*i:4*i+3]
        if status not in (0.,1.,2.): raise ValueError('unknown GPU hit status')
        if status==0:
            if (distance,obj,primitive)!=(-1.,-1.,-1.): raise ValueError('explicit miss sentinel required')
            results.append({'status':'miss'}); continue
        if obj!=int(obj) or primitive!=int(primitive) or not 0<=obj<len(batch.object_ids) or not 0<=primitive<batch.triangle_count or distance<=0:
            raise ValueError('malformed nearest-hit indices/distance')
        if abs(math.hypot(*normal)-1)>1e-6: raise ValueError('unit GPU normal required')
        results.append({'status':'hit' if status==1 else 'ambiguous','object_id':batch.object_ids[int(obj)],
                        'distance_BU':distance,'normal':normal,'primitive_index':int(primitive)})
    return results


def require_unambiguous(results):
    if any(r['status']=='ambiguous' for r in results):
        raise ValueError('ambiguous coincident geometry: no inference permitted')


def native_geometry_shader(gpu):
    info=gpu.types.GPUShaderCreateInfo()
    for slot,name in enumerate(('geometry_hi','geometry_lo','rays_hi','rays_lo')):
        info.sampler(slot,'FLOAT_2D',name)
    for slot,name in enumerate(('hits_out','normals_out')):
        info.image(slot,'RGBA32F','FLOAT_2D',name,qualifiers={'WRITE'})
    info.push_constant('INT','triangle_count'); info.push_constant('INT','query_count')
    info.local_group_size(8,1,1); info.compute_source(SHADER.read_text(encoding='utf-8'))
    return gpu.shader.create_from_info(info)


def dispatch_geometry(gpu,shader,batch):
    from exp005_blender_gpu import texture_data,flatten
    import time
    textures=[]
    for raw in (batch.triangles,batch.rays):
        height,hi,lo=texture_data(raw)
        for values in (hi,lo):
            textures.append(gpu.types.GPUTexture((64,height),format='RGBA32F',
                data=gpu.types.Buffer('FLOAT',len(values),values)))
    outputs=[gpu.types.GPUTexture((batch.query_count,1),format='RGBA32F') for _ in range(2)]
    for name,texture in zip(('geometry_hi','geometry_lo','rays_hi','rays_lo'),textures): shader.uniform_sampler(name,texture)
    for name,texture in zip(('hits_out','normals_out'),outputs): shader.image(name,texture)
    shader.uniform_int('triangle_count',batch.triangle_count); shader.uniform_int('query_count',batch.query_count)
    start=time.perf_counter(); gpu.compute.dispatch(shader,math.ceil(batch.query_count/8),1,1)
    hits,normals=[flatten(t.read().to_list()) for t in outputs]
    elapsed=(time.perf_counter()-start)*1000
    return decode_hits(batch,hits,normals),elapsed
