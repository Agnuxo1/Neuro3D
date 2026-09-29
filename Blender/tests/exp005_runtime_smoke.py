"""Prebounded real Blender CPU smoke; NOT the frozen multicell EXP-005 gate.

Creates new tiny fixtures only, reopens every file, compares actual Blender
raycasts against a separate triangle oracle and supplied-path consumer. No render.
Run through gpuq using run_exp005_smoke.py; thresholds fixed before measurement.
"""
import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_exp005_triangle_oracle import mz
from exp005_scene_readback import export_snapshot
from exp005_triangle_oracle import trace_scene
from exp005_scene_properties import decode_scene, sum_declared_channels

FIELD_TOL = 2e-3
POWER_TOL = 1e-4
PATH_TOL = 5e-6


def json_value(value):
    if isinstance(value,complex): return [value.real,value.imag]
    raise TypeError(type(value).__name__)


def write_json(path,value):
    path.write_text(json.dumps(value,default=json_value,indent=2)+'\n',encoding='utf-8')


def raycast_paths(scene):
    """Independent bpy traversal: does NOT ask triangle oracle for hits/paths."""
    scene.view_layers[0].update()
    dg = bpy.context.evaluated_depsgraph_get()
    paths = []; rays = 0
    for source in json.loads(scene['optical_sources']):
        initial = complex(*source['field_reim'])
        if initial == 0: continue
        stack = [(Vector(source['position_BU']),Vector(source['direction']).normalized(),[])]
        while stack:
            origin,direction,history = stack.pop(); rays += 1
            if rays>4096 or len(history)>=64: raise ValueError('bounded smoke exceeded')
            # Small ray-origin displacement avoids self-hit; length uses ORIGINAL origin.
            found,point,normal,face,obj,_ = scene.ray_cast(dg,origin+direction*1e-6,direction)
            if not found: raise ValueError('lost Blender ray')
            distance = (point-origin).length
            kind = obj['kind']
            hit = {'object_id':obj.name,'distance_BU':distance,'face_index':face}
            if kind in ('det','escape'):
                axis = Vector(obj['mode_direction']).normalized()
                if direction.dot(axis)<1-1e-6: raise ValueError('terminal mode mismatch')
                hit['event'] = 'detect' if kind=='det' else 'escape'
                paths.append({'source_id':source['id'],'initial_field':initial,
                              'hits':history+[hit], 'reference_offset_BU':
                              direction.dot(Vector(obj['mode_origin_BU'])-point)})
                continue
            reflected = (direction-2*direction.dot(normal)*normal).normalized()
            events = [('mirror',reflected)] if kind=='mirror' else [('t',direction),('r',reflected)]
            for event,ray in events:
                stack.append((point,ray,history+[dict(hit,event=event)]))
    return paths,rays


def build(case):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fixture = mz()
    sc = bpy.context.scene
    sc['lambda_BU'] = .101 if case=='lambda' else .1
    sc['optical_object_ids'] = json.dumps(list(fixture['objects']))
    sc['optical_sources'] = json.dumps(fixture['sources'])
    for name,record in fixture['objects'].items():
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(record['vertices_world_BU'],[],record['faces']); mesh.update()
        obj = bpy.data.objects.new(name,mesh); sc.collection.objects.link(obj)
        obj['kind'] = record['kind']
        if record['kind']=='mirror': obj['phase_rad'] = .1 if case=='phase' and name=='r1' else 0.
        if record['kind']=='det':
            obj['mode_origin_BU'] = record['mode_origin_BU']; obj['mode_direction'] = record['mode_direction']
        if case=='sham': obj.color = (.7,.1,.2,1)
        if case=='roof' and name in ('r1','r2'): obj.location.x += .0125


def key(path):
    return (path['source_id'],tuple((h['object_id'],h['event']) for h in path['hits']))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--evidence',required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    folder = Path(args.evidence).resolve(); folder.mkdir(parents=True,exist_ok=True)
    reports = {}
    for case in ('base','phase','lambda','sham','roof'):
        build(case)
        blend = folder/f'{case}.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.wm.open_mainfile(filepath=str(blend))
        snapshot = export_snapshot(bpy.context.scene)
        write_json(folder/f'{case}_snapshot.json',snapshot)
        oracle = trace_scene(snapshot)
        supplied,rays = raycast_paths(bpy.context.scene)
        ledger = sum_declared_channels(decode_scene(snapshot),supplied)
        oracle_paths = {key(p):p for p in oracle['paths']}
        assert len(oracle_paths)==len(oracle['paths'])==len(supplied)
        path_error = 0.
        for path in supplied:
            ref = oracle_paths[key(path)]
            path_error = max(path_error,max(abs(a['distance_BU']-b['distance_BU'])
                             for a,b in zip(path['hits'],ref['hits'])))
        error = max(abs(ledger['fields'].get(n,0j)-f) for n,f in oracle['fields'].items())
        y_expected = math.sin(.05)**2 if case=='phase' else .5 if case=='roof' else None
        if case in ('base','sham'): y_expected = 0.
        if case=='lambda':
            y_expected = abs(.5*(cmath.exp(2j*math.pi*7/.101)-cmath.exp(2j*math.pi*5/.101)))**2
        power_error = abs(sum(ledger['powers'].values())-1)
        law_error = abs(ledger['powers']['Y']-y_expected)
        assert error<=FIELD_TOL and path_error<=PATH_TOL
        assert power_error<=POWER_TOL and law_error<=POWER_TOL
        reports[case] = {'fields':ledger['fields'],'powers':ledger['powers'],
                         'max_complex_error':error,'max_distance_error_BU':path_error,
                         'power_balance_error':power_error,'closed_form_power_error':law_error,
                         'paths':len(supplied),'raycasts':rays,
                         'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest()}
        write_json(folder/f'{case}_paths.json',{'bpy':supplied,'oracle':oracle})
    sham = max(abs(reports['base']['fields'][n]-reports['sham']['fields'][n])
               for n in reports['base']['fields'])
    assert sham<=FIELD_TOL
    result = {'passed':True,'scope':'single-cell real bpy raycast + Python fields; not full EXP-005',
              'blender_version':bpy.app.version_string,'thresholds':{
              'complex':FIELD_TOL,'power':POWER_TOL,'distance_BU':PATH_TOL},
              'sham_complex_error':sham,'cases':reports,
              'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_json(folder/'runtime_smoke.json',result)
    print('EXP005_RUNTIME_SMOKE_PASS',flush=True)


if __name__=='__main__': main()
