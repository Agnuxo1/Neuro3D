"""Native raw-scene scalar GPU pilot; no CPU ray tracing or field arithmetic.

CPU serialization/validation/readback are host work, not claimed GPU work.
Calls need a real Blender GPU context and exclusive guarded reservation.
"""
import math
from pathlib import Path
from frontier_inputs import pack_frontier

SHADER=Path(__file__).parents[2]/'shaders'/'exp005_frontier.glsl'
ERRORS={1:'lost ray',2:'ambiguous geometry',3:'terminal direction mismatch',
        4:'stack overflow',5:'step limit',6:'depth limit',7:'unknown optical role',8:'ledger overflow'}


def limits(max_steps,max_depth):
    if (any(isinstance(n,bool) or not isinstance(n,int) for n in (max_steps,max_depth)) or
            not 1<=max_steps<=4096 or not 1<=max_depth<=32):
        raise ValueError('bounded integer GPU traversal limits required')


def decode(batch,fields,stats,ledger):
    count=len(batch.ports)
    if len(fields)!=4*count or len(stats)!=4*count or len(ledger)!=128*4*count:
        raise ValueError('complete final GPU readback required')
    if any(not math.isfinite(v) for v in (*fields,*stats)):
        raise ValueError('finite final GPU readback required')
    result={}; errors={}
    for i,port in enumerate(batch.ports):
        re,im,power,status=fields[i*4:i*4+4]
        casts,paths,depth,flag=stats[i*4:i*4+4]
        if status!=flag or status!=int(status) or (status!=0 and status not in ERRORS):
            raise ValueError('inconsistent GPU status')
        if any(v!=int(v) or v<0 for v in (casts,paths,depth)) or paths>128 or depth>32 or casts>4096*len(batch.source_ids):
            raise ValueError('invalid GPU traversal statistics')
        if status:
            if (re,im,power)!=(0.,0.,0.): raise ValueError('invalid partial fields must be cleared')
            errors[port]=ERRORS[status]; continue
        if power<0 or abs(power-(re*re+im*im))>2e-6*max(1.,power):
            raise ValueError('invalid GPU intensity readback')
        rows=[ledger[i*512+j*4:i*512+j*4+4] for j in range(int(paths))]
        if any(not math.isfinite(v) for row in rows for v in row): raise ValueError('finite retained path ledger required')
        if any(row[3]!=int(row[3]) or not 0<=row[3]<len(batch.source_ids) for row in rows):
            raise ValueError('source-owned path ledger required')
        result[port]={'field_reim':[re,im],'power':power,'casts':int(casts),'paths':int(paths),
                      'max_depth':int(depth),'ledger':[{'field_reim':row[:2],'effective_length_BU':row[2],
                      'source_id':batch.source_ids[int(row[3])]} for row in rows]}
    return {'valid':not errors,'ports':result,'errors':errors}


def native_shader(gpu):
    info=gpu.types.GPUShaderCreateInfo()
    for slot,name in enumerate(('geometry_hi','geometry_lo','sources_hi','sources_lo','optics_hi','optics_lo')):
        info.sampler(slot,'FLOAT_2D',name)
    for slot,name in enumerate(('fields_out','stats_out','ledger_out')):
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
             gpu.types.GPUTexture((128,count),format='RGBA32F')]
    for name,texture in zip(('geometry_hi','geometry_lo','sources_hi','sources_lo','optics_hi','optics_lo'),textures):
        shader.uniform_sampler(name,texture)
    for name,texture in zip(('fields_out','stats_out','ledger_out'),outputs): shader.image(name,texture)
    for name,value in (('triangle_count',batch.geometry.triangle_count),('source_count',len(batch.source_ids)),
                       ('port_count',count),('max_steps',max_steps),('max_depth',max_depth)): shader.uniform_int(name,value)
    hi,lo=split_double(batch.wavelength_BU)
    shader.uniform_float('wavelength_hi',hi); shader.uniform_float('wavelength_lo',lo)
    start=time.perf_counter(); gpu.compute.dispatch(shader,count,1,1)
    raw=[flatten(t.read().to_list()) for t in outputs]
    elapsed=(time.perf_counter()-start)*1000
    return decode(batch,*raw),elapsed
