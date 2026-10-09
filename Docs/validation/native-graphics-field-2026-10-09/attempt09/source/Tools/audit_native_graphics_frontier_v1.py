"""Source-driven native Blender graphics frontier and coherent inference audit."""
import argparse,gc,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need,dot,vec
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.audit_coherent_state_graph_v1 import planar_objects,independent_nearest
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.native_graphics_geometry_v1 import NativeGraphicsCandidates
from Blender.blender_lab.native_graphics_frontier_v1 import build_graphics_graph
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Tools.audit_coherent_state_graph_v1 import audit_graph_result

def put(path,value):path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())

def square(x):
    return {'vertices_world_BU':[(x,-1,-1),(x,1,-1),(x,1,1),(x,-1,1)],'faces':[(0,1,2),(0,2,3)]}

def main():
    import bpy,gpu
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(exist_ok=False);start=time.perf_counter()
    profile=json.loads(args.profile.read_bytes());report={'schema':'optic_neuro_blender.native_graphics_frontier_audit.v1','status':'NOT_EXECUTED','primary_metric':None,'native_gpu_executed':False,'gpu_geometry_readback':False,'gpu_fields_executed':False,'hardware_RT_executed':False};backend=None;failure=None
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
        cpu_runs=[];graphics_runs=[];graphs=[]
        for repetition in range(profile['repetitions']):
            t=time.perf_counter();cpu=build_graph(scene);elapsed=time.perf_counter()-t
            need(cpu['status']=='COMPLETE','Complete equivalent CPU graph required')
            cpu_runs.append({'repetition':repetition,'build_seconds':elapsed,'selection_statistics':cpu['selection_statistics']})
        for repetition in range(profile['repetitions']):
            t=time.perf_counter();backend=NativeGraphicsCandidates(gpu,scene,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU']);packing=backend.compile_pack_upload_seconds
            own=build_graphics_graph(scene,backend,max_states=4096,distance_tolerance_BU=profile['distance_absolute_tolerance_BU']);elapsed=time.perf_counter()-t
            report['native_gpu_executed']=True;report['gpu_geometry_readback']=True
            put(args.out/('graphics_graph_'+str(repetition)+'.json'),wire(own))
            record={'repetition':repetition,'pack_compile_upload_and_build_seconds':elapsed,'pack_compile_upload_seconds':packing,'status':own['status'],'states':len(own['nodes']),'frontier_batches':len(own['graphics_frontier_batches']),'selection_statistics':own['selection_statistics'],'candidate_fallback':own['graphics_candidate_fallback']}
            graphics_runs.append(record);graphs.append(own);backend=None;gc.collect()
        complete=all(g['status']=='COMPLETE' for g in graphs)
        if complete:
            own=graphs[-1]
            for g in graphs:
                need(wire(g['nodes'])==wire(cpu['nodes'])==wire(graph['nodes']) and g['roots']==cpu['roots'] and g['topological_order']==cpu['topological_order'],'Exact autonomous frontier geometry/topology must equal CPU and historical native references')
                need(g['selection_statistics']['verified_candidates']==133 and g['selection_statistics']['rejected_candidates']==0,'All133actual GPU candidates require exact verification')
            t=time.perf_counter();fields={s['id']:[1,0] for s in scene['sources']};single=propagate_graph(own,fields);audit=audit_graph_result(wire(scene),wire({'graph':own,**single}));audit_seconds=time.perf_counter()-t
            need(audit['primary_metric']==1 and single['represented_terminal_paths']==17060,'Independent complete optical branch/path audit required')
            native=json.loads((ROOT/profile['native_result']).read_bytes());max_field=0;max_power=0;outputs=[];predictions=[];ports=native['ports'];detectors=native['detectors'];source_ids=native['source_ids']
            t=time.perf_counter()
            for row,expected_fields,expected_powers in zip(native['all150_encoded_inputs_reim'],native['all150_native_fields_reim'],native['all150_native_powers']):
                result=propagate_graph(own,dict(zip(source_ids,row)));observed_fields=[result['fields'][p] for p in ports];powers=[result['powers'][p] for p in ports]
                max_field=max(max_field,max(abs(z-complex(*pair)) for z,pair in zip(observed_fields,expected_fields)));max_power=max(max_power,max(abs(v-u) for v,u in zip(powers,expected_powers)))
                predictions.append(max(range(len(detectors)),key=lambda j:powers[ports.index(detectors[j])]))
                outputs.append({'fields_reim':[[z.real,z.imag] for z in observed_fields],'powers':powers})
            inference_seconds=time.perf_counter()-t
            need(len(outputs)==150 and predictions==native['all150_predictions'] and max_field<=1e-11 and max_power<=1e-11,'All150 own coherent inference predictions and phase-aware fields must match native reference')
            put(args.out/'all150_coherent_inference.json',{'outputs':outputs,'predictions':predictions,'field_max_difference':max_field,'power_max_difference':max_power,'gpu_geometry':True,'gpu_field_arithmetic':False})
            report.update(independent_audit=audit,represented_terminal_paths=single['represented_terminal_paths'],edges=sum(len(n['edges']) for n in own['nodes']),field_max_difference=max_field,power_max_difference=max_power,all150_predictions_same=True,cost_seconds={'capture_and_admission':capture_seconds,'independent_full_graph_and_field_audit':audit_seconds,'all150_coherent_inference':inference_seconds})
        report.update(status='VALID_NATIVE_GRAPHICS_FRONTIER_AUDIT',primary_metric=int(complete),profile_sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),triangles=6656,source_driven_frontier=True,cpu_runs=cpu_runs,graphics_runs=graphics_runs,
                      scope='Actual GPU vertex/fragment raster/depth candidates generate own frontier from source rays and optical branches. Each candidate independently verified by CPU exact predicates before phase; no CPU candidate replacement. All paths retained, coherent arithmetic CPU, graph reuse for150inputs. Paired CPU exact builders and GPU+exact verification include their full construction costs. Three repetitions on shared host are exploratory; no physical/RTcore/AMD/energy claim.')
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
