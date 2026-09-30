"""Bounded saved/reopened connected cascade: bpy paths, CPU complex fields.

No rendering, GPU propagation or RT claim. Frozen thresholds and new artifacts.
"""
import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

FIELD_TOL=2e-3
POWER_TOL=1e-4
PATH_TOL=1e-5
CAUSAL_MIN=1e-3
CASES=('base','phase_a','phase_b','sham','roof','lambda')
PORTS=('a.Y','b.X','b.Y')


def probes():
    result=[]
    for i in range(3):
        amps=[0j]*3; amps[i]=1+0j; result.append((f'basis{i}',amps))
    for i,j in itertools.combinations(range(3),2):
        for phase in (1+0j,1j):
            amps=[0j]*3; amps[i]=1+0j; amps[j]=phase
            result.append((f'pair{i}{j}_{phase.imag:g}',amps))
    return result


def main():
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from exp005_cascade_fixture import cascade_fixture,closed_form_columns
    from exp005_scene_readback import export_snapshot
    from exp005_triangle_oracle import trace_scene
    from exp005_scene_properties import decode_scene,sum_declared_channels
    from exp005_runtime_smoke import key,write_json
    from exp005_cascade_bpy_paths import raycast_paths

    parser=argparse.ArgumentParser(); parser.add_argument('--evidence',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    folder=Path(args.evidence).resolve(); folder.mkdir(parents=True,exist_ok=True)
    if any(folder.glob('*.blend')) or (folder/'cascade_runtime.json').exists():
        raise ValueError('fresh evidence folder required; no overwrite')
    result={'scope':'connected two-cell hybrid: bpy geometry, Python CPU fields, not RT',
            'passed':False,'blender_version':bpy.app.version_string,
            'thresholds':{'complex':FIELD_TOL,'power':POWER_TOL,'distance_BU':PATH_TOL,
                          'causal_min':CAUSAL_MIN},'cases':{}}
    result['dependencies_sha256']={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
        for name in ('exp005_cascade_fixture.py','exp005_runtime_smoke.py','exp005_scene_readback.py',
                     'exp005_triangle_oracle.py','exp005_scene_properties.py',
                     'exp005_cascade_bpy_paths.py','exp005_reflection.py')}
    for case in CASES:
        phases=(.6,.37) if case=='phase_a' else (.2,.8) if case=='phase_b' else (.2,.37)
        fixture=cascade_fixture(*phases,wavelength=.101 if case=='lambda' else .1)
        bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
        scene['lambda_BU']=fixture['lambda_BU']
        scene['optical_object_ids']=json.dumps(list(fixture['objects']))
        scene['optical_sources']=json.dumps(fixture['sources'])
        for name,record in fixture['objects'].items():
            mesh=bpy.data.meshes.new(name)
            mesh.from_pydata(record['vertices_world_BU'],[],record['faces']); mesh.update()
            obj=bpy.data.objects.new(name,mesh); scene.collection.objects.link(obj)
            for prop in ('kind','phase_rad','mode_origin_BU','mode_direction'):
                if prop in record: obj[prop]=record[prop]
            if case=='sham': obj.color=(.3,.8,.1,1.)
            if case=='roof' and name in ('a.r1','a.r2'): obj.location.x+=.0125
        def readback():
            bpy.context.view_layer.update()
            return export_snapshot(bpy.context.scene,depsgraph=bpy.context.evaluated_depsgraph_get(),
                                   view_layer=bpy.context.view_layer)
        before=readback(); blend=folder/f'{case}.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.wm.open_mainfile(filepath=str(blend))
        snapshot=readback(); scene=bpy.context.scene
        if before!=snapshot: raise ValueError('save/reopen snapshot mismatch')
        write_json(folder/f'{case}_snapshot.json',snapshot)
        reports=[]
        for label,amps in probes():
            supplied=copy.deepcopy(snapshot)
            for source,amp in zip(supplied['sources'],amps): source['field_reim']=[amp.real,amp.imag]
            scene['optical_sources']=json.dumps(supplied['sources'])
            oracle=trace_scene(supplied)
            paths,rays=raycast_paths(scene)
            reference={key(path):path for path in oracle['paths']}
            actual={key(path):path for path in paths}
            if len(reference)!=len(oracle['paths']) or len(actual)!=len(paths) or set(reference)!=set(actual):
                raise ValueError('path identities or multiplicities mismatch')
            distance_error=max(abs(hit['distance_BU']-ref['distance_BU'])
                for path_key,path in actual.items()
                for hit,ref in zip(path['hits'],reference[path_key]['hits']))
            ledger=sum_declared_channels(decode_scene(supplied),paths)
            if set(ledger['fields'])!=set(PORTS) or set(oracle['fields'])!=set(PORTS):
                raise ValueError('complete complex output set required')
            error=max(abs(ledger['fields'][port]-oracle['fields'][port]) for port in PORTS)
            balance=abs(sum(ledger['powers'].values())-sum(abs(amp)**2 for amp in amps))
            analytic_error=None
            if case!='lambda':
                effective=(phases[0]+math.pi/2,phases[1]) if case=='roof' else phases
                columns=closed_form_columns(*effective)
                expected=[sum(amp*column[j] for amp,column in zip(amps,columns)) for j in range(3)]
                analytic_error=max(abs(ledger['fields'][port]-field) for port,field in zip(PORTS,expected))
            report={'probe':label,'input_fields':amps,'fields':ledger['fields'],'powers':ledger['powers'],
                    'complex_error':error,'closed_form_error':analytic_error,
                    'distance_error_BU':distance_error,'balance_error':balance,'rays':rays,'paths':len(paths)}
            reports.append(report)
            write_json(folder/f'{case}_{label}_paths.json',{'bpy':paths,'oracle':oracle,'report':report})
            if (error>FIELD_TOL or distance_error>PATH_TOL or balance>POWER_TOL or
                    (analytic_error is not None and analytic_error>FIELD_TOL)):
                write_json(folder/'failure.json',{'case':case,'report':report})
                raise ValueError('frozen connected-cascade numerical gate failed')
        result['cases'][case]={'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
                               'readback_equal':True,'probes':reports}
        write_json(folder/'cascade_runtime.json',result)
    base=result['cases']['base']['probes']
    sham=result['cases']['sham']['probes']
    sham_error=max(abs(a['fields'][p]-b['fields'][p]) for a,b in zip(base,sham) for p in PORTS)
    effects={case:max(abs(result['cases'][case]['probes'][0]['powers'][p]-base[0]['powers'][p])
                     for p in PORTS) for case in ('phase_a','phase_b','roof','lambda')}
    result.update(sham_complex_error=sham_error,causal_power_effects=effects,
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    result['passed']=sham_error<=1e-12 and all(v>CAUSAL_MIN for v in effects.values())
    write_json(folder/'cascade_runtime.json',result)
    if not result['passed']: raise ValueError('frozen sham/causality gate failed')
    print('EXP005_CASCADE_RUNTIME_PASS',flush=True)


if __name__=='__main__': main()
