"""Prospectively bounded scaling of actual native graphical optical inference."""
import argparse,gc,hashlib,json,math,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.trace_indexed_scene_v1 import wire
from Tools.train_captured_geometry_v1 import parameters_and_bases
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.native_geometry_frontier_v3 import build_graphics_graph,DeclaredNativeGraphicsCandidates
from Blender.blender_lab.native_deferred_graphics_gradient_v2 import NativeDeferredGraphicsGradientTransport
from Blender.blender_lab.native_graphics_gradient_network_v2 import transport_parameter_tangent
from Blender.blender_lab.native_program_lifecycle_v1 import unbind_owned_program
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.coherent_state_graph_v1 import propagate_graph

def put(p,v):p.write_bytes((json.dumps(v,indent=2,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    import bpy,gpu,addon_utils
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(exist_ok=False);p=json.loads(args.profile.read_bytes());start=time.perf_counter();failure=None;backend=None
    report={'schema':'optic_neuro_blender.native_graphics_scaling.v1','status':'NOT_EXECUTED','primary_metric':None}
    try:
        for name,pin in p['pins'].items():need(sha(ROOT/name)==pin,'Immutable scaling source mismatch:'+name)
        prior=json.loads((ROOT/p['producer_result']).read_bytes());need(prior['status']=='VALID_NATIVE_GRAPHICS_GEOMETRY_TRAINING' and prior['optimizer_updates']==60,'Completed published native graphics training required')
        need(not bpy.app.background and list(bpy.app.version)==[4,5,14] and gpu.platform.backend_type_get()=='OPENGL' and 'RTX 3090' in gpu.platform.renderer_get(),'Actual fixed native graphics context required')
        bpy.context.preferences.use_preferences_save=False;bpy.context.preferences.view.use_save_prompt=False;bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
        bpy.ops.preferences.addon_install(filepath=str(ROOT/p['archive_relative']),overwrite=False);addon_utils.enable('optic_neuro_blender',default_set=False,persistent=True)
        from optic_neuro_blender.model import capture_current,prepare
        from optic_neuro_blender.bootstrap import verify_bundle
        verify_bundle();bpy.ops.wm.open_mainfile(filepath=str(ROOT/p['blend']),use_scripts=False)
        t=time.perf_counter();capture=capture_current();scene=prepare(capture,{sid:[1,0] for sid in prior['source_ids']});capture_seconds=time.perf_counter()-t
        expected=decode(json.loads((ROOT/p['scene']).read_bytes()));need(wire(scene['objects'])==wire(expected['objects']),'Actual saved trained scene geometry equality required')
        put(args.out/'actual_capture.json',capture);put(args.out/'actual_scene.json',wire(scene))
        t=time.perf_counter();selector=DeclaredNativeGraphicsCandidates(gpu,scene,pixel_BU=p['pixel_BU'],far_BU=p['far_BU']);graph=build_graphics_graph(scene,selector,max_states=4096,distance_tolerance_BU=p['distance_absolute_tolerance_BU']);gpu_graph_seconds=time.perf_counter()-t
        need(graph['status']=='COMPLETE' and len(graph['nodes'])==133,'Fresh complete actual native GPU graph required')
        t=time.perf_counter();audit=audit_graph_neighborhood(wire(scene),wire({'graph':graph,**propagate_graph(graph,{sid:[1,0] for sid in prior['source_ids']})}));need(audit['primary_metric']==1,'Independent full nearest/closed-fan graph audit required');audit_seconds=time.perf_counter()-t
        put(args.out/'actual_graph.json',wire(graph));put(args.out/'independent_graph_audit.json',audit)
        t=time.perf_counter();parameters,_=parameters_and_bases(scene);net=AffineGeometryNetwork(scene,graph,parameters);cpu_setup_seconds=time.perf_counter()-t
        need(net.source_ids==prior['source_ids'] and net.ports==prior['ports'],'Fixed complete modal order required')
        unbind_owned_program(gpu);selector=None;gc.collect();t=time.perf_counter()
        backend=NativeDeferredGraphicsGradientTransport(gpu,scene,pixel_BU=p['pixel_BU'],far_BU=p['far_BU'],stage_audit_path=args.out/'strict_GL_audit.json');backend.set_parameter({name:[0,0,0] for name in net.shifts});compile_seconds=time.perf_counter()-t
        original=np.asarray(prior['all150_inputs_reim']);original=original[:,:,0]+1j*original[:,:,1]
        columns=[net.ports.index(d) for d in prior['detectors']];results=[];max_field=max_power=0.
        for size in p['batch_sizes']:
            backend.update_geometry(scene)
            indices=np.arange(size)%150;phases=np.asarray([1,1j,-1,-1j])[np.arange(size)%4];x=original[indices]*phases[:,None]
            assert np.isfinite(x).all()
            def cpu():
                t=time.perf_counter();value=net.forward(x,[0.]*16,gradients=False);return value['fields'],time.perf_counter()-t,None
            def graphics():
                t=time.perf_counter();out=[];receipts=[]
                for offset in range(0,size,150):
                    inputs=[dict(zip(net.source_ids,[[z.real,z.imag] for z in row])) for row in x[offset:offset+150]]
                    value=transport_parameter_tangent(graph,backend,inputs,[(F(0),F(0),F(0)) for _ in graph['nodes']],distance_tolerance_BU=p['distance_absolute_tolerance_BU'])
                    out.extend([[complex(*row[port]) for port in net.ports] for row in value['fields_reim']]);receipts.append({'tile_start':offset,'samples':len(inputs),'batches':value['batches'],'zero_derivative_echo_enforced':True})
                return np.asarray(out),time.perf_counter()-t,receipts
            for repetition in range(2):
                order=['CPU_GEOMETRY_DAG','GPU_DEFERRED_GRAPHICS'] if repetition==0 else ['GPU_DEFERRED_GRAPHICS','CPU_GEOMETRY_DAG'];outputs={};cost={};receipts=None
                for arm in order:
                    outputs[arm],cost[arm],details=cpu() if arm=='CPU_GEOMETRY_DAG' else graphics()
                    if details is not None:receipts=details
                observed=outputs['GPU_DEFERRED_GRAPHICS'];reference=outputs['CPU_GEOMETRY_DAG'];field_error=float(np.max(np.abs(observed-reference)));power=np.abs(observed)**2;ref_power=np.abs(reference)**2;power_error=float(np.max(np.abs(power-ref_power)));pred=np.argmax(power[:,columns],axis=1)
                need(field_error<=p['field_tolerance'] and power_error<=p['power_tolerance'],'Equivalent-output numerical budgets required')
                need(pred.tolist()==np.argmax(ref_power[:,columns],axis=1).tolist()==np.asarray(prior['all150_predictions'])[indices].tolist(),'Fixed repeated-row decisions must match both own CPU and original learned output')
                need(float(np.max(np.abs(power-np.asarray(prior['all150_powers'])[indices])))<=p['power_tolerance'],'Global coherent quarter-turn preserves recorded learned powers')
                max_field=max(max_field,field_error);max_power=max(max_power,power_error)
                record={'batch_size':size,'repetition':repetition,'execution_order':order,'monotonic_seconds_end':time.monotonic(),'geometry_cache_cold_for_first_gpu_arm':repetition==0,'seconds':cost,'field_max_difference':field_error,'power_max_difference':power_error,'all_decisions_equal':True,'gpu_fields_reim':[[[z.real,z.imag] for z in row] for row in observed],'cpu_fields_reim':[[[z.real,z.imag] for z in row] for row in reference],'gpu_powers':power.tolist(),'predictions':pred.tolist(),'gpu_readback_receipts':receipts}
                put(args.out/f'batch_{size}_repeat_{repetition}.json',record);results.append({k:v for k,v in record.items() if k not in ('gpu_fields_reim','cpu_fields_reim','gpu_powers','predictions','gpu_readback_receipts')});put(args.out/'progress.json',results)
                print(json.dumps(results[-1]),flush=True)
        surface=backend.surface_receipt();put(args.out/'actual_surface_provenance.json',surface);backend.stage_audit.finish()
        report.update(status='VALID_NATIVE_GRAPHICS_SCALING',primary_metric=1,profile_sha256=sha(args.profile),renderer=gpu.platform.renderer_get(),driver=gpu.platform.version_get(),blender_version=bpy.app.version_string,geometry_states=133,represented_terminal_paths=17060,all_modal_outputs_and_decisions_equivalent=True,max_field_difference=max_field,max_power_difference=max_power,results=results,setup_cost_seconds={'actual_capture':capture_seconds,'fresh_GPU_graph':gpu_graph_seconds,'independent_exact_graph_audit':audit_seconds,'CPU_geometry_network_setup':cpu_setup_seconds,'GPU_shader_compile':compile_seconds},native_triangle_surface_queries_actual=surface['native_triangle_surface_queries'],deferred_optical_fragment_queries_including_echo=surface['optical_fragment_queries_including_echo'],strict_GL_checked_stage_count=backend.stage_audit.count,strict_GL_owned_errors=backend.stage_audit.errors,
            scope='Actual captured3D selection andFP64opticalshader. Batch1/150/4096 uses fixed previouslyobservedIris rows with commonexactquarterturn, notnewgeneralization. GPU tiles<=150 and existingzero-tangent/bit-echo draws remainincluded, coherentCPUmerges explicit. CPU own geometryDAG computesgeometry-derivedphases, no cachedtransfermatrix. Shared capture/fullindependenttopologyaudit/setup measured separately; twofixedalternatingorders notstatisticalthroughputproof. GPUcandidatecache cold first arm per size; warm second. WholeGPU telemetry notisolatedopticaldeviceenergy. No physical/AMD/RT/exceptionalnovelty claim.')
    except Exception as exc:
        failure=exc;report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT',failure_type=type(exc).__name__)
        if isinstance(exc,(ValueError,RuntimeError,TypeError)):report['reason']=str(exc)
    finally:
        report['seconds']=time.perf_counter()-start;put(args.out/'result.json',report)
        if backend is not None:backend.stage_audit.finish()
    if failure is not None:raise failure
    print(json.dumps({'status':report['status'],'primary_metric':report['primary_metric'],'seconds':report['seconds']}),flush=True)
    def finish():
        window=list(bpy.context.window_manager.windows)[0]
        with bpy.context.temp_override(window=window):bpy.ops.wm.quit_blender()
        return None
    bpy.app.timers.register(finish,first_interval=.1)

if __name__=='__main__':main()
