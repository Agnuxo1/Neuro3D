"""Own CPU doubles of evaluated Blender scene export; NOT a Blender run."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
from types import SimpleNamespace as NS
from exp005_history_mzi_export import fixture,CASES,evaluated_readback,validate_export
from test_exp005_scene_readback import Object,Objects,OffsetMatrix


def doubles(expected):
    scene=type('FakeScene',(dict,),{})(coherence_groups=json.dumps({'s':'g'}),
         optical_contract=expected['schema'],lambda_BU=expected['lambda_BU'],
         optical_object_ids=json.dumps(list(expected['objects'])),optical_sources=json.dumps(expected['sources']))
    scene.objects=Objects()
    f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
    for name,record in expected['objects'].items():
        obj=Object(name,record['kind']);obj.update({k:v for k,v in record.items() if k not in ('vertices_world_BU','faces')})
        obj.data=NS(vertices=[NS(co=tuple(f32(x) for x in v)) for v in record['vertices_world_BU']],
                    polygons=[NS(vertices=tuple(f)) for f in record['faces']])
        obj.matrix_world=OffsetMatrix();obj.original=obj;obj.update_tag=lambda:None
        scene.objects[name]=obj
    graph=NS(mode='VIEWPORT',objects=list(scene.objects.values()))
    bpy=NS(context=NS(view_layer=NS(update=lambda:None),evaluated_depsgraph_get=lambda:graph))
    return bpy,scene


def audit():
    controls=[];negatives=[]
    for label,phase,shift in CASES:
        expected,rows=fixture(phase,shift);bpy,scene=doubles(expected);before=evaluated_readback(bpy,scene)
        after=copy.deepcopy(before);checked=validate_export(expected,before,after,rows,phase,shift)
        controls.append({'case':label,'expected':expected,'fake_evaluated_readback':after,'checks':checked})
    expected,rows=fixture();bpy,scene=doubles(expected);base=evaluated_readback(bpy,scene)
    for label in ('unchecked','reopen_change','world_vertex_change','source_change','missing_property','order_change','extra_mesh','coherence_change'):
        before=copy.deepcopy(base);after=copy.deepcopy(base)
        if label=='unchecked':before['evaluated_optics_checked']=False
        elif label=='reopen_change':after['objects']['MA']['phase_rad']=.2
        elif label=='world_vertex_change':
            before['objects']['MA']['vertices_world_BU'][0][0]+=2.**-23;after=copy.deepcopy(before)
        elif label=='source_change':before['sources'][0]['field_reim']=[.5,0.];after=copy.deepcopy(before)
        elif label=='missing_property':del before['objects']['MA']['phase_rad'];after=copy.deepcopy(before)
        elif label=='order_change':before['objects']=dict(reversed(list(before['objects'].items())));after=copy.deepcopy(before)
        elif label=='extra_mesh':before['undeclared_meshes']=['blocker'];after=copy.deepcopy(before)
        else:before['coherence_groups']={'s':'another'};after=copy.deepcopy(before)
        try:validate_export(expected,before,after,rows,0.,0.)
        except ValueError as e:negatives.append({'case':label,'reason':str(e)})
        else:raise ValueError('invalid export accepted: '+label)
    return {'scope':'CPU doubles and float32 roundtrip emulation only, NOT actual Blender/save/reopen/GPU',
            'controls':controls,'negatives':negatives,'no_jev_aval':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=audit()
    b=Path(__file__).parents[1]
    files=[Path(__file__),Path(__file__).with_name('test_exp005_history_mzi_export.py')]
    files += [b/'tests'/n for n in ('exp005_history_mzi_export.py','exp005_history_mzi_audit.py',
                                   'exp005_scene_readback.py','exp005_scene_properties.py','test_exp005_scene_readback.py')]
    files += [b/'benchmarks/capacity_audit'/n for n in ('history_fields_cpu_v1.py','history_lengths_cpu_v1.py',
                                                      'history_completeness_cpu_v1.py','history_lineage_cpu_v2.py',
                                                      'frontier_inputs.py','gpu_geometry_probe.py')]
    out['code_sha256']={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x',encoding='utf-8') as f:f.write(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'CPU_double_controls':len(out['controls']),'negative_checks':len(out['negatives']),
                      'report_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
