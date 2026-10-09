"""Actual Blender native graphics geometry candidate audit; no GPU field claim."""
import argparse,gc,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need,dot,vec
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.audit_coherent_state_graph_v1 import planar_objects,independent_nearest
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.native_graphics_geometry_v1 import NativeGraphicsCandidates

def put(path,value):path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())

def square(x):
    return {'vertices_world_BU':[(x,-1,-1),(x,1,-1),(x,1,1),(x,-1,1)],'faces':[(0,1,2),(0,2,3)]}

def main():
    import bpy,gpu
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(exist_ok=False);start=time.perf_counter()
    profile=json.loads(args.profile.read_bytes());report={'schema':'optic_neuro_blender.native_graphics_geometry_audit.v1','status':'NOT_EXECUTED','primary_metric':None,'native_gpu_executed':False,'gpu_geometry_readback':False,'gpu_fields_executed':False,'hardware_RT_executed':False};backend=None;failure=None
    try:
        for name,pin in profile['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen graphics source mismatch:'+name)
        need(not bpy.app.background and list(bpy.app.version)==[4,5,14],'Actual native windowed Blender4.5.14 required')
        report.update(blender_version=bpy.app.version_string,blender_build_hash=bpy.app.build_hash.decode(),backend=gpu.platform.backend_type_get(),vendor=gpu.platform.vendor_get(),renderer=gpu.platform.renderer_get(),driver=gpu.platform.version_get())
        need(report['backend']=='OPENGL' and 'NVIDIA' in report['vendor'] and 'RTX 3090' in report['renderer'],'Actual frozen NVIDIA native graphics context required')
        bpy.context.preferences.use_preferences_save=False;bpy.context.preferences.view.use_save_prompt=False;bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
        bpy.ops.preferences.addon_install(filepath=str(ROOT/profile['archive_relative']),overwrite=False)
        import addon_utils
        addon_utils.enable('optic_neuro_blender',default_set=False,persistent=True)
        from optic_neuro_blender.model import capture_current,prepare
        from optic_neuro_blender.bootstrap import verify_bundle
        verify_bundle();bpy.ops.wm.open_mainfile(filepath=str(ROOT/profile['blend']),use_scripts=False)
        t=time.perf_counter();capture=capture_current();scene=prepare(capture,{sid:[1,0] for sid in ('r0','r1','c0','c1','c2')});capture_seconds=time.perf_counter()-t
        expected=decode(json.loads((ROOT/profile['scene']).read_bytes()));result_wire=json.loads((ROOT/profile['graph_result']).read_bytes());graph=decode(result_wire)['graph']
        put(args.out/'actual_capture.json',capture);put(args.out/'actual_scene.json',wire(scene))
        need(wire(scene['objects'])==wire(expected['objects']) and scene['lambda_BU']==expected['lambda_BU'],'Actual evaluated optical meshes/materials must match fixed native scene')
        need(wire([(s['id'],s['position_BU'],s['direction']) for s in scene['sources']])==wire([(s['id'],s['position_BU'],s['direction']) for s in expected['sources']]),'Actual evaluated source geometry identity required')
        put(args.out/'actual_capture.json',capture);put(args.out/'actual_scene.json',wire(scene))
        t=time.perf_counter();audit=audit_graph_neighborhood(json.loads((ROOT/profile['scene']).read_bytes()),result_wire);need(audit['primary_metric']==1,'Independent exact geometry/neighborhood reference required');audit_seconds=time.perf_counter()-t
        objects=planar_objects(expected);byname={o[0]:o for o in objects};queries=[]
        for node in graph['nodes']:
            previous=node['previous_plane'];name=previous[0] if previous else None
            if name is not None:
                plane=byname[name][2];need(dot(plane[1],vec(node['origin']))==plane[2] and dot(plane[1],vec(node['direction']))!=0,'Previous mask requires exact zero transverse contact')
            queries.append({'origin':node['origin'],'direction':node['direction'],'previous_name':name})
        need(len(queries)==133,'Complete fixed component query set required');put(args.out/'shader_queries_no_expected_hits.json',wire(queries))
        t=time.perf_counter()
        for node in graph['nodes']:independent_nearest(node,objects)
        cpu_query_seconds=time.perf_counter()-t
        backend=NativeGraphicsCandidates(gpu,scene,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU']);records=[]
        for count in profile['batch_sizes']:
            batch=[queries[j%133] for j in range(count)];runs=[]
            for repetition in range(profile['repetitions']):
                observed=backend.query(batch);report['native_gpu_executed']=True;report['gpu_geometry_readback']=True
                matched=0;maximum=0;checks=[]
                for j,row in enumerate(observed['rows']):
                    node=graph['nodes'][j%133];norm=math_norm(node['direction']);distance=float(node['segment_parameter'])*norm
                    error=abs(row.get('distance_BU',-1)-distance);same=row.get('object')==node['hit_object'];matched+=int(same and error<=profile['distance_absolute_tolerance_BU']);maximum=max(maximum,error)
                    checks.append({'query':j,'reference_node':j%133,'object_agreement':same,'distance_absolute_error_BU':error})
                observed.update(repetition=repetition,matched_queries=matched,max_distance_absolute_error_BU=maximum,comparison=checks);runs.append(observed)
            records.append({'batch_size':count,'runs':runs})
        # Explicit controls; these shader inputs contain vertices/rays only.
        controls=[]
        fixture={'objects':{'near':square(F(1)),'far':square(F(2))}};small=NativeGraphicsCandidates(gpu,fixture,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU'])
        inputs=[{'origin':[0,0,0],'direction':[1,0,0],'previous_name':None},{'origin':[1,0,0],'direction':[1,0,0],'previous_name':'near'},{'origin':[0,2,0],'direction':[1,0,0],'previous_name':None}]
        observed=small.query(inputs);rows=observed['rows'];controls.extend([{'name':'nearest_of_two_surfaces','pass':rows[0].get('object')=='near' and abs(rows[0].get('distance_BU',-1)-1)<=5e-5},{'name':'exact_previous_zero_contact_mask','pass':rows[1].get('object')=='far' and abs(rows[1].get('distance_BU',-1)-1)<=5e-5},{'name':'closed_surface_miss','pass':rows[2]['status']=='MISS'}]);put(args.out/'geometric_controls.json',{'controls':controls,'readback':observed})
        del small
        close={'objects':{'far':square(F(1)+F(1,2**25)),'near':square(F(1))}};small=NativeGraphicsCandidates(gpu,close,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU']);close_result=small.query(inputs[:1]);put(args.out/'float32_close_surface_diagnostic.json',{'exact_nearest_object':'near','exact_separation_BU':[1,2**25],'readback':close_result,'exact_nearest_agreement':close_result['rows'][0].get('object')=='near','scope':'Diagnostic precision challenge; not a universal candidate certificate. A wrong candidate requires exact refinement, never physical zero.'});del small
        complete=all(run['matched_queries']==case['batch_size'] for case in records for run in case['runs']) and all(c['pass'] for c in controls)
        report.update(status='VALID_NATIVE_GRAPHICS_COMPONENT_AUDIT',primary_metric=int(complete),profile_sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),triangles=backend.triangle_count,objects=len(backend.names),queries=133,independent_reference_audit=audit,
                      cost_seconds={'actual_bpy_capture_and_admission':capture_seconds,'independent_reference_geometry_audit':audit_seconds,'fresh_independent_cpu133_nearest_queries':cpu_query_seconds,'graphics_geometry_pack_compile_upload':backend.compile_pack_upload_seconds},batches=records,geometric_controls=controls,
                      scope='Actual Blender vertex/fragment instancing+raster/depth geometry candidate selection on evaluated meshes.133queries originate from independent CPU reference graph: component audit, not GPU-driven full frontier. CPU exact optical phase/field path remains separate. FP32 graphics not globally certified; close-surface diagnostic retained. No hardware RT/OptiX, matrix-neuron, physical fidelity, GPU training or speed superiority claim.')
    except Exception as exc:
        failure=exc;report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT',failure_type=type(exc).__name__)
        if isinstance(exc,(ValueError,RuntimeError)):report['reason']=str(exc)
    finally:
        report['seconds']=time.perf_counter()-start;put(args.out/'result.json',report)
        backend=None;gc.collect()
    if failure is not None:raise failure
    print(json.dumps({'status':report['status'],'primary_metric':report['primary_metric'],'seconds':report['seconds']}),flush=True)
    def finish():
        window=list(bpy.context.window_manager.windows)[0]
        with bpy.context.temp_override(window=window):bpy.ops.wm.quit_blender()
        return None
    bpy.app.timers.register(finish,first_interval=.1)

def math_norm(direction):
    import math
    return math.sqrt(sum(float(v)**2 for v in direction))

if __name__=='__main__':main()
