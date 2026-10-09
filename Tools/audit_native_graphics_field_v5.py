"""Source-driven native Blender graphics frontier and coherent inference audit."""
import argparse,gc,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need,dot,vec
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.audit_coherent_state_graph_v1 import planar_objects,independent_nearest
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.native_graphics_field_v5 import NativeGraphicsFieldTransport
from Blender.blender_lab.native_graphics_coherent_network_v1 import transport_batch
from Blender.blender_lab.native_geometry_frontier_v3 import build_graphics_graph,DeclaredNativeGraphicsCandidates as NativeGraphicsCandidates
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
        t=time.perf_counter();backend=NativeGraphicsCandidates(gpu,scene,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU'])
        own=build_graphics_graph(scene,backend,max_states=4096,distance_tolerance_BU=profile['distance_absolute_tolerance_BU']);geometry_seconds=time.perf_counter()-t
        report['native_gpu_executed']=True;report['gpu_geometry_readback']=True
        put(args.out/'actual_gpu_geometry_graph.json',wire(own));need(own['status']=='COMPLETE' and wire(own['nodes'])==wire(graph['nodes']),'Actual exact-verified GPU geometry identity required')
        t=time.perf_counter();single=propagate_graph(own,{sid:[1,0] for sid in ('r0','r1','c0','c1','c2')});audit=audit_graph_result(wire(scene),wire({'graph':own,**single}));audit_seconds=time.perf_counter()-t
        need(audit['primary_metric']==1 and single['represented_terminal_paths']==17060,'Independent complete optical branch/path audit required')
        native=json.loads((ROOT/profile['native_result']).read_bytes());ports=native['ports'];detectors=native['detectors'];source_ids=native['source_ids']
        inputs=[dict(zip(source_ids,row)) for row in native['all150_encoded_inputs_reim']]
        phase_input={sid:[-v[1],v[0]] for sid,v in inputs[0].items()}
        first={sid:[int(sid=='r0'),0] for sid in source_ids};second={sid:[int(sid=='r1'),0] for sid in source_ids};cancel={sid:[int(sid=='r0')-int(sid=='r1'),0] for sid in source_ids}
        controls=[phase_input,cancel,first,second]
        cpu_runs=[];graphics_runs=[];max_field=max_power=max_local=0.;backend=None;gc.collect()
        t=time.perf_counter();transport=NativeGraphicsFieldTransport(gpu,scene,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU']);prepare_seconds=time.perf_counter()-t
        transport.diagnostic_path=args.out/'native_binary64_diagnostic.json'
        put(args.out/'uploaded_captured_optical_planes.json',{'names':transport.names,'plane_material_reference_kind_scalars':transport.object_scalars,'layout':['nx','ny','nz','offset_BU','tau','mirror_phase_rad','reference_x_BU','reference_y_BU','reference_z_BU','kind'],'precomputed_transfer_matrix_used':False})
        for repetition in range(profile['repetitions']):
            t=time.perf_counter();cpu_fields=[propagate_graph(own,row) for row in inputs];cpu_runs.append({'repetition':repetition,'phase_only_graph_reuse_seconds':time.perf_counter()-t})
            actual=transport_batch(own,transport,inputs,distance_tolerance_BU=profile['distance_absolute_tolerance_BU']);report['gpu_fields_executed']=True
            put(args.out/('native_gpu_transport_'+str(repetition)+'.json'),wire(actual))
            predictions=[]
            for observed,expected_fields,expected_powers in zip(actual['fields_reim'],native['all150_native_fields_reim'],native['all150_native_powers']):
                max_field=max(max_field,max(abs(complex(*observed[p])-complex(*z)) for p,z in zip(ports,expected_fields)))
            for powers,expected_powers in zip(actual['powers'],native['all150_native_powers']):
                max_power=max(max_power,max(abs(powers[p]-v) for p,v in zip(ports,expected_powers)));predictions.append(max(range(len(detectors)),key=lambda j:powers[detectors[j]]))
            max_local=max(max_local,actual['transport_local_max_difference']);need(len(predictions)==150 and predictions==native['all150_predictions'] and max_field<=1e-11 and max_power<=1e-11 and max_local<=1e-11,'Unchanged150complex/power/decision/localtransport gates required')
            graphics_runs.append({'repetition':repetition,'transport_seconds':actual['seconds'],'states':actual['states'],'samples':actual['samples'],'actual_geometric_ray_queries':actual['actual_geometric_ray_queries'],'frontier_batches':len(actual['batches']),'field_max_difference':max_field,'power_max_difference':max_power,'transport_local_max_difference':max_local})
        actual_controls=transport_batch(own,transport,controls,distance_tolerance_BU=profile['distance_absolute_tolerance_BU']);put(args.out/'native_gpu_coherence_controls.json',wire(actual_controls))
        control_difference=0.;interference_difference=0.;common_phase_difference=0.;common_phase_power_difference=0.
        for j,row in enumerate(controls):
            reference=propagate_graph(own,row)
            for p in ports:control_difference=max(control_difference,abs(complex(*actual_controls['fields_reim'][j][p])-reference['fields'][p]))
        for p,z in zip(ports,native['all150_native_fields_reim'][0]):
            common_phase_difference=max(common_phase_difference,abs(complex(*actual_controls['fields_reim'][0][p])-1j*complex(*z)))
            common_phase_power_difference=max(common_phase_power_difference,abs(actual_controls['powers'][0][p]-native['all150_native_powers'][0][ports.index(p)]))
            summed=complex(*actual_controls['fields_reim'][2][p])-complex(*actual_controls['fields_reim'][3][p]);interference_difference=max(interference_difference,abs(abs(summed)**2-(actual_controls['powers'][2][p]+actual_controls['powers'][3][p])))
            need(abs(summed-complex(*actual_controls['fields_reim'][1][p]))<=1e-11,'Phase-aware destructive-superposition control required')
        need(control_difference<=1e-11 and common_phase_difference<=1e-11 and common_phase_power_difference<=1e-11 and interference_difference>1e-4,'Native coherent controls must agree with independent CPU and distinguish coherent from intensity sums')
        report.update(status='VALID_NATIVE_GRAPHICS_FIELD_AUDIT',primary_metric=1,profile_sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),source_driven_frontier=True,cpu_runs=cpu_runs,graphics_runs=graphics_runs,represented_terminal_paths=single['represented_terminal_paths'],edges=sum(len(n['edges']) for n in own['nodes']),independent_audit=audit,all150_predictions_same=True,field_max_difference=max_field,power_max_difference=max_power,transport_local_max_difference=max_local,
                      coherence_controls={'max_complex_difference':control_difference,'global_phase_complex_difference':common_phase_difference,'global_phase_power_difference':common_phase_power_difference,'coherent_vs_intensity_sum_difference':interference_difference,'destructive_superposition_pass':True},
                      cost_seconds={'capture_and_admission':capture_seconds,'fresh_exact_verified_gpu_geometry':geometry_seconds,'independent_full_graph_audit':audit_seconds,'native_field_shader_geometry_pack_compile_upload':prepare_seconds},
                      cpu_compensated_coherent_merging=True,precomputed_transfer_matrix_used=False,native_rounding_certified=False,
                      scope='Actual captured triangle raster/depth selects each transport surface. FP64 fragment shader derives intersection distance, wavelength phase, splitter/mirror branch fields and terminal reference phase from captured planes/materials and current rays/inputs. Exact CPU topology/admission and compensated coherent merging explicit. Geometry reselected for each of150inputs rather than precomputed transfer-matrix multiplication. Native binary64 fields/parity observed, not rigorous GPU rounding or physical-wave certification. CPU timing is phase-only graph reuse, GPU timing includes re-selection; no equivalent speed claim.')
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
