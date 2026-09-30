"""Versioned shared traversal; no CPU tracing/phase/sums, no RT/BVH."""
import math
from pathlib import Path
from frontier_inputs import pack_frontier
from frontier_gpu import decode as decode_ports,limits,ERRORS

SHADER=Path(__file__).parents[2]/'shaders'/'exp005_shared_frontier.glsl'


def decode(batch,fields,stats,ledger,work):
    result=decode_ports(batch,fields,stats,ledger)
    if len(work)!=4 or any(not math.isfinite(v) or v!=int(v) or v<0 for v in work):
        raise ValueError('finite complete integer shared work readback required')
    casts,paths,invocations,status=map(int,work)
    if invocations!=1 or casts>4096*len(batch.source_ids) or paths>128*len(batch.ports):
        raise ValueError('bounded single shared traversal required')
    if status!=0 and status not in ERRORS: raise ValueError('unknown shared GPU status')
    if any(stats[i]!=casts for i in range(0,len(stats),4)) or sum(stats[1::4])!=paths:
        raise ValueError('shared counter copies/path totals inconsistent')
    if any(stats[i]!=status for i in range(3,len(stats),4)):
        raise ValueError('all ports must share fail-closed status')
    result['work']={'traversal_invocations':invocations,'total_casts':casts,
                    'total_terminal_paths':paths,'status':status,
                    'port_casts_semantics':'copies of shared total; do not sum as work'}
    return result


def native_shader(gpu):
    info=gpu.types.GPUShaderCreateInfo()
    for slot,name in enumerate(('geometry_hi','geometry_lo','sources_hi','sources_lo','optics_hi','optics_lo')):
        info.sampler(slot,'FLOAT_2D',name)
    for slot,name in enumerate(('fields_out','stats_out','ledger_out','work_out')):
        info.image(slot,'RGBA32F','FLOAT_2D',name,qualifiers={'WRITE'})
    for name in ('triangle_count','source_count','port_count','max_steps','max_depth'): info.push_constant('INT',name)
    for name in ('wavelength_hi','wavelength_lo'): info.push_constant('FLOAT',name)
    info.local_group_size(1,1,1); info.compute_source(SHADER.read_text(encoding='utf-8'))
    return gpu.shader.create_from_info(info)


def dispatch(gpu,shader,snapshot,*,max_steps=4096,max_depth=32,mode_cap=3):
    from exp005_blender_gpu import texture_data,split_double,flatten
    from exp005_mode_gate import mode_geometry
    import time
    limits(max_steps,max_depth); mode_geometry(snapshot); batch=pack_frontier(snapshot,mode_cap=mode_cap)
    textures=[]
    for raw in (batch.geometry.triangles,batch.sources,batch.optics):
        height,hi,lo=texture_data(raw)
        for values in (hi,lo): textures.append(gpu.types.GPUTexture((64,height),format='RGBA32F',
                       data=gpu.types.Buffer('FLOAT',len(values),values)))
    count=len(batch.ports)
    outputs=[gpu.types.GPUTexture((count,1),format='RGBA32F'),gpu.types.GPUTexture((count,1),format='RGBA32F'),
             gpu.types.GPUTexture((128,count),format='RGBA32F'),gpu.types.GPUTexture((1,1),format='RGBA32F')]
    for name,texture in zip(('geometry_hi','geometry_lo','sources_hi','sources_lo','optics_hi','optics_lo'),textures):
        shader.uniform_sampler(name,texture)
    for name,texture in zip(('fields_out','stats_out','ledger_out','work_out'),outputs): shader.image(name,texture)
    for name,value in (('triangle_count',batch.geometry.triangle_count),('source_count',len(batch.source_ids)),
                       ('port_count',count),('max_steps',max_steps),('max_depth',max_depth)): shader.uniform_int(name,value)
    hi,lo=split_double(batch.wavelength_BU)
    shader.uniform_float('wavelength_hi',hi); shader.uniform_float('wavelength_lo',lo)
    start=time.perf_counter(); gpu.compute.dispatch(shader,1,1,1)
    raw=[flatten(t.read().to_list()) for t in outputs]
    elapsed=(time.perf_counter()-start)*1000
    return decode(batch,*raw),elapsed
