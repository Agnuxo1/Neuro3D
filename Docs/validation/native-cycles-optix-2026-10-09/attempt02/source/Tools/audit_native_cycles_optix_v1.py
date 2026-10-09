"""Bounded captured-scene OptiX surface component and identical-proof CPU BVH."""
import argparse,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.trace_indexed_scene_v1 import wire
from Tools.audit_coherent_state_graph_v1 import audit_graph_result
from Blender.blender_lab.native_geometry_frontier_v4 import build_graphics_graph
from Blender.blender_lab.native_cycles_optix_geometry_v1 import NativeCyclesOptixCandidates
from Blender.blender_lab.native_bvh_geometry_v1 import NativeBVHCandidates
from Blender.blender_lab.coherent_state_graph_v1 import propagate_graph

def put(path,value):path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())

def main():
    import bpy
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(exist_ok=False)
    profile=json.loads(args.profile.read_bytes());start=time.perf_counter();failure=None
    report={'schema':'optic_neuro_blender.native_cycles_optix_audit.v1','status':'NOT_EXECUTED','primary_metric':None,'native_optix_render_executed':False,'hardware_RT_kernel_counters_measured':False,'gpu_fields_executed':False}
    try:
        for name,pin in profile['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen source mismatch:'+name)
        need(list(bpy.app.version)==[4,5,14],'Frozen native Blender4.5.14 required')
        report.update(blender_version=bpy.app.version_string,blender_build_hash=bpy.app.build_hash.decode())
        bpy.context.preferences.use_preferences_save=False;bpy.context.preferences.view.use_save_prompt=False;bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
        bpy.ops.preferences.addon_install(filepath=str(ROOT/profile['archive_relative']),overwrite=False)
        import addon_utils
        addon_utils.enable('optic_neuro_blender',default_set=False,persistent=True)
        from optic_neuro_blender.model import capture_current,prepare
        from optic_neuro_blender.bootstrap import verify_bundle
        verify_bundle();bpy.ops.wm.open_mainfile(filepath=str(ROOT/profile['blend']),use_scripts=False)
        t=time.perf_counter();capture=capture_current();scene=prepare(capture,{sid:[1,0] for sid in ('r0','r1','c0','c1','c2')});capture_seconds=time.perf_counter()-t
        expected=decode(json.loads((ROOT/profile['scene']).read_bytes()));reference=decode(json.loads((ROOT/profile['graph_result']).read_bytes()))['graph']
        need(wire(scene['objects'])==wire(expected['objects']) and scene['lambda_BU']==expected['lambda_BU'],'Evaluated captured optical scene identity required')
        need(wire([(s['id'],s['position_BU'],s['direction']) for s in scene['sources']])==wire([(s['id'],s['position_BU'],s['direction']) for s in expected['sources']]),'Actual source geometry identity required')
        put(args.out/'actual_capture.json',capture);put(args.out/'actual_scene.json',wire(scene))
        t=time.perf_counter();backend=NativeCyclesOptixCandidates(scene,out=args.out/'lossless_candidate_pixels',pixel_BU=profile['candidate_pixel_BU'],far_BU=profile['far_BU'])
        report.update(optix_selected_device=backend.selected_device,cycles_device_inventory=backend.device_inventory,candidate_geometry_pack_seconds=backend.compile_pack_upload_seconds)
        own=build_graphics_graph(scene,backend,max_states=4096,distance_tolerance_BU=profile['distance_absolute_tolerance_BU']);optix_seconds=time.perf_counter()-t
        report.update(native_optix_render_executed=backend.query_index>0,actual_optix_render_queries=backend.query_index)
        put(args.out/'actual_optix_geometry_graph.json',wire(own))
        need(own['status']=='COMPLETE' and wire(own['nodes'])==wire(reference['nodes']),'All requested represented rays require exact independent OptiX admission; no fallback')
        t=time.perf_counter();single=propagate_graph(own,{sid:[1,0] for sid in ('r0','r1','c0','c1','c2')});audit=audit_graph_result(wire(scene),wire({'graph':own,**single}));audit_seconds=time.perf_counter()-t
        put(args.out/'independent_optix_graph_audit.json',audit);need(audit['primary_metric']==1 and single['represented_terminal_paths']==17060,'Independent full topology/branch/path audit required')
        t=time.perf_counter();cpu=NativeBVHCandidates(scene,far_BU=profile['far_BU']);cpu_graph=build_graphics_graph(scene,cpu,max_states=4096,distance_tolerance_BU=profile['distance_absolute_tolerance_BU']);cpu_seconds=time.perf_counter()-t
        put(args.out/'actual_cpu_bvh_geometry_graph.json',wire(cpu_graph));need(cpu_graph['status']=='COMPLETE' and wire(cpu_graph['nodes'])==wire(own['nodes']),'Identical-proof CPU BVH candidate baseline required')
        native=json.loads((ROOT/profile['native_result']).read_bytes());powers=[];field_max=power_max=0.;t=time.perf_counter()
        for encoded,expected_fields,expected_powers in zip(native['all150_encoded_inputs_reim'],native['all150_native_fields_reim'],native['all150_native_powers']):
            actual=propagate_graph(own,dict(zip(native['source_ids'],encoded)));powers.append([actual['powers'][port] for port in native['ports']])
            field_max=max(field_max,max(abs(actual['fields'][port]-complex(*z)) for port,z in zip(native['ports'],expected_fields)))
            power_max=max(power_max,max(abs(actual['powers'][port]-z) for port,z in zip(native['ports'],expected_powers)))
        columns=[native['ports'].index(port) for port in native['detectors']];predictions=[max(range(3),key=lambda k:row[columns[k]]) for row in powers]
        need(predictions==native['all150_predictions'] and max(field_max,power_max)<=profile['field_tolerance'],'Coherent CPU fields from exact-verified OptiX geometry preserve all150 outputs')
        report.update(status='VALID_NATIVE_CYCLES_OPTIX_AUDIT',primary_metric=1,profile_sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),source_driven_frontier=True,states=len(own['nodes']),edges=sum(len(n['edges']) for n in own['nodes']),represented_terminal_paths=17060,actual_optix_render_queries=backend.query_index,all150_predictions_equal=True,field_max_difference=field_max,power_max_difference=power_max,all150_powers=powers,
            cost_seconds={'capture':capture_seconds,'optix_candidate_and_identical_exact_proof':optix_seconds,'cpu_bvh_candidate_and_identical_exact_proof':cpu_seconds,'independent_full_graph_audit':audit_seconds,'cpu_coherent_all150':time.perf_counter()-t},
            scope='Actual installed Cycles OPTIX RTX3090 GPU renders captured triangles with a1e-7BU orthographic pixel footprint; lossless float32 emitted object/primitive/projected-position candidates enter independent exact represented-ray admission. Source-driven complete133state/186edge/17060path graph. CPU coherent fields and equivalent exact-proof BVH baseline explicit. No measured RT kernel counters, GPU optical fields/learning, physical fidelity or general speed advantage.')
    except Exception as exc:
        failure=exc;report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT',failure_type=type(exc).__name__)
        if isinstance(exc,(ValueError,RuntimeError,TypeError)):report['reason']=str(exc)
    finally:report['seconds']=time.perf_counter()-start;put(args.out/'result.json',report)
    if failure is not None:raise failure
    print(json.dumps({k:report[k] for k in ('status','primary_metric','actual_optix_render_queries','seconds')}),flush=True)
    def finish():
        window=list(bpy.context.window_manager.windows)[0]
        with bpy.context.temp_override(window=window):bpy.ops.wm.quit_blender()
        return None
    bpy.app.timers.register(finish,first_interval=.1)

if __name__=='__main__':main()
