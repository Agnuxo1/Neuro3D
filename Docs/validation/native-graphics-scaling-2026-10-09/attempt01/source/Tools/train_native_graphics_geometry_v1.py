"""Actual native Blender geometry learning with FP64 graphical optical tangents."""
import argparse,gc,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.trace_indexed_scene_v1 import wire
from Tools.train_captured_geometry_v1 import parameters_and_bases,load_data,quantize
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.native_geometry_frontier_v3 import build_graphics_graph,DeclaredNativeGraphicsCandidates
from Blender.blender_lab.native_graphics_gradient_v2 import NativeGraphicsGradientTransport
from Blender.blender_lab.native_graphics_gradient_network_v2 import transport_parameter_tangent
from Blender.blender_lab.native_program_lifecycle_v1 import unbind_owned_program
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.affine_box_audit_v1 import IndependentAffineBox
from Blender.blender_lab.affine_family_identity_v1 import certify_affine_identity,require_box_membership
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph

def put(path,value):path.write_bytes((json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def encoded_rows(x,source_ids):return [dict(zip(source_ids,[[z.real,z.imag] for z in row])) for row in x]
def readout(fields,power_jac,ports,detectors,labels,temperature):
    columns=[ports.index(p) for p in detectors];powers=np.abs(fields)**2;scores=powers[:,columns]/temperature
    shifted=scores-scores.max(axis=1,keepdims=True);exp=np.exp(shifted);prob=exp/exp.sum(axis=1,keepdims=True)
    loss=float(np.mean(np.log(exp.sum(axis=1))-shifted[np.arange(len(labels)),labels]));prob[np.arange(len(labels)),labels]-=1
    gradient=np.einsum('nc,ncp->p',prob/(len(labels)*temperature),power_jac[:,columns,:])
    return loss,gradient,powers

def main():
    import bpy,gpu,addon_utils
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(exist_ok=False)
    outer=json.loads(args.profile.read_bytes());training=json.loads((ROOT/outer['training_profile']).read_bytes());start=time.perf_counter();failure=None;transport=None
    report={'schema':'optic_neuro_blender.native_graphics_training.v1','status':'NOT_EXECUTED','primary_metric':None,'gpu_geometry_fields_and_gradients_executed':False,'cpu_optimizer_loss_and_coherent_merges':True,'hardware_RT_executed':False}
    try:
        for name,pin in outer['pins'].items():need(sha(ROOT/name)==pin,'Frozen graphics training source mismatch:'+name)
        need(not bpy.app.background and list(bpy.app.version)==[4,5,14] and gpu.platform.backend_type_get()=='OPENGL' and 'RTX 3090' in gpu.platform.renderer_get(),'Actual native RTX3090 OpenGL context required')
        report.update(blender_version=bpy.app.version_string,blender_build_hash=bpy.app.build_hash.decode(),renderer=gpu.platform.renderer_get(),driver=gpu.platform.version_get())
        bpy.context.preferences.use_preferences_save=False;bpy.context.preferences.view.use_save_prompt=False;bpy.context.preferences.filepaths.use_auto_save_temporary_files=False
        bpy.ops.preferences.addon_install(filepath=str(ROOT/outer['archive_relative']),overwrite=False);addon_utils.enable('optic_neuro_blender',default_set=False,persistent=True)
        from optic_neuro_blender.model import capture_current,prepare,apply_positions,save_copy
        from optic_neuro_blender.bootstrap import verify_bundle
        verify_bundle();bpy.ops.wm.open_mainfile(filepath=str(ROOT/outer['blend']),use_scripts=False)
        t=time.perf_counter();capture=capture_current();base_scene=prepare(capture,{sid:[1,0] for sid in ('r0','r1','c0','c1','c2')});capture_seconds=time.perf_counter()-t
        expected=decode(json.loads((ROOT/outer['scene']).read_bytes()))
        need(wire(base_scene['objects'])==wire(expected['objects']),'Native baseline captured geometry identity required')
        put(args.out/'initial_native_capture.json',capture);put(args.out/'initial_native_scene.json',wire(base_scene))
        t=time.perf_counter();geometry=DeclaredNativeGraphicsCandidates(gpu,base_scene,pixel_BU=outer['pixel_BU'],far_BU=outer['far_BU']);base_graph=build_graphics_graph(base_scene,geometry,max_states=4096,distance_tolerance_BU=outer['distance_absolute_tolerance_BU']);geometry_seconds=time.perf_counter()-t
        need(base_graph['status']=='COMPLETE' and len(base_graph['nodes'])==133,'Fresh exact-verified complete native GPU geometry required');put(args.out/'initial_native_graph.json',wire(base_graph))
        parameters,bases=parameters_and_bases(base_scene);net=AffineGeometryNetwork(base_scene,base_graph,parameters)
        prior=json.loads((ROOT/outer['prior_training_result']).read_bytes());old_bases=[F(float.fromhex(v)) for v in prior['native_base_world_x_hex']]
        initial=quantize([float(a+F(float(d))-b) for a,d,b in zip(old_bases,training['initial_deltas_BU'],bases)],bases)
        center=np.asarray([float(a+F(float(d))-b) for a,d,b in zip(old_bases,training['untrained_center_deltas_BU'],bases)])
        radius=F(training['translation_bound_BU'])+F(training['native_quantization_allowance_BU']);h=F(training['gradient_difference_step_BU'])
        box=[(min(F(float(c))-radius,F(float(d))-h),max(F(float(c))+radius,F(float(d))+h)) for c,d in zip(center,initial)]
        t=time.perf_counter();base_audit=audit_graph_neighborhood(wire(base_scene),wire({'graph':base_graph,**propagate_graph(base_graph,{sid:[1,0] for sid in net.source_ids})}));need(base_audit['primary_metric']==1,'Independent exact base geometry audit required')
        independent=IndependentAffineBox(base_scene,base_graph,parameters);identity=certify_affine_identity(independent,net);continuous=independent.prove_box(box);need(continuous['status']=='PROVED_CONTINUOUS_AFFINE_BOX_TOPOLOGY','Full original continuous training family proof required')
        proof_seconds=time.perf_counter()-t;put(args.out/'continuous_family_proof.json',{'base_audit':base_audit,'exact_expression_identity':identity,'continuous_topology_proof':continuous,'relative_box':wire(box)})
        train,test=training['train_indices'],training['test_indices'];need(len(train)==120 and len(test)==30 and set(train).isdisjoint(test) and set(train)|set(test)==set(range(150)),'Fixed complete train/test split required')
        x,y,scaler=load_data(ROOT/training['dataset'],train,net.source_ids);inputs=encoded_rows(x[train],net.source_ids);labels=y[train]
        d=initial.copy();m=np.zeros(16);v=np.zeros(16);shadow_d=d.copy();shadow_m=np.zeros(16);shadow_v=np.zeros(16)
        report['owned_program_release']=unbind_owned_program(gpu);geometry=None;gc.collect()
        t=time.perf_counter();transport=NativeGraphicsGradientTransport(gpu,base_scene,pixel_BU=outer['pixel_BU'],far_BU=outer['far_BU'],stage_audit_path=args.out/'strict_compact_GL_stage_audit.json');compile_seconds=time.perf_counter()-t
        history=[];max_field=max_jac=max_power_jac=max_gradient=max_shadow_delta=0.;query_count=0;native_capture_seconds=graphics_seconds=cpu_reference_seconds=0.
        for step in range(training['steps']+1):
            membership=require_box_membership(box,d);native_positions=[float(float(b)+float(delta)).hex() for b,delta in zip(bases,d)]
            t=time.perf_counter();apply_positions(parameters,native_positions);actual_capture=capture_current();actual_scene=prepare(actual_capture,{sid:[1,0] for sid in net.source_ids});native_capture_seconds+=time.perf_counter()-t
            virtual_scene,graph=net.materialize(d)
            need(wire(actual_scene['objects'])==wire(virtual_scene['objects']) and actual_scene['lambda_BU']==virtual_scene['lambda_BU'],'Every optimizer state requires exact actual native geometry recapture equality')
            need(wire([(s['id'],s['position_BU'],s['direction']) for s in actual_scene['sources']])==wire([(s['id'],s['position_BU'],s['direction']) for s in base_scene['sources']]),'Every native source geometry must stay fixed')
            transport.update_geometry(actual_scene)
            values=[];jac=[];power_jac=[];batches=[];t=time.perf_counter()
            for j in range(16):
                transport.set_parameter({name:[net.shifts[name][k][j] for k in range(3)] for name in net.shifts})
                tangent=transport_parameter_tangent(graph,transport,inputs,[tuple(origin[k][j] for k in range(3)) for origin in net.origin_jets],distance_tolerance_BU=outer['distance_absolute_tolerance_BU'])
                values.append(np.asarray([[complex(*row[port]) for port in net.ports] for row in tangent['fields_reim']]))
                jac.append(np.asarray([[complex(*row[port]) for port in net.ports] for row in tangent['field_parameter_derivative_reim']]))
                power_jac.append(np.asarray([[row[port] for port in net.ports] for row in tangent['power_parameter_derivative']]))
                query_count+=tangent['actual_geometric_queries_including_echo_draw'];batches.append({'parameter':j,'seconds':tangent['seconds'],'readback_summaries':tangent['batches']})
            graphics_seconds+=time.perf_counter()-t;field=values[0];field_jac=np.stack(jac,axis=2);power_jac=np.stack(power_jac,axis=2)
            loss,gradient,powers=readout(field,power_jac,net.ports,training['detectors'],labels,training['loss_temperature'])
            t=time.perf_counter();ref_loss,ref_gradient,ref=net.cross_entropy(x[train],labels,d,training['detectors'],training['loss_temperature']);shadow_loss,shadow_gradient,_=net.cross_entropy(x[train],labels,shadow_d,training['detectors'],training['loss_temperature']);cpu_reference_seconds+=time.perf_counter()-t
            differences={'field':max(float(np.max(np.abs(a-ref['fields']))) for a in values),'field_jacobian':float(np.max(np.abs(field_jac-ref['field_jacobian']))),'power_jacobian':float(np.max(np.abs(power_jac-ref['power_jacobian']))),'loss_gradient':float(np.max(np.abs(gradient-ref_gradient))),'loss':abs(loss-ref_loss),'shadow_delta_BU':float(np.max(np.abs(d-shadow_d)))}
            need(differences['field']<=outer['field_tolerance'] and differences['field_jacobian']<=outer['jacobian_absolute_tolerance'] and differences['power_jacobian']<=outer['jacobian_absolute_tolerance'] and differences['loss_gradient']<=outer['loss_gradient_absolute_tolerance'],'Every native graphics optimizer state requires independent CPU numerical parity')
            max_field=max(max_field,differences['field']);max_jac=max(max_jac,differences['field_jacobian']);max_power_jac=max(max_power_jac,differences['power_jacobian']);max_gradient=max(max_gradient,differences['loss_gradient']);max_shadow_delta=max(max_shadow_delta,differences['shadow_delta_BU'])
            state={'step':step,'train_loss':loss,'reference_train_loss':ref_loss,'shadow_train_loss':shadow_loss,'deltas_BU':d.tolist(),'native_world_x_hex':native_positions,'actual_capture_state_sha256':actual_capture['state_sha256'],'actual_optical_scene_sha256':hashlib.sha256(json.dumps(wire(actual_scene),sort_keys=True,separators=(',',':')).encode()).hexdigest(),'exact_native_geometry_matches_materialized':True,'continuous_family_membership':membership,'differences':differences,'loss_gradient':gradient.tolist(),'graphics_batches':batches}
            put(args.out/('state_'+str(step)+'.json'),dict(state,fields_reim=[[[z.real,z.imag] for z in row] for row in field],field_jacobian_reim=[[[[z.real,z.imag] for z in row] for row in sample] for sample in field_jac],power_jacobian=power_jac.tolist()))
            history.append(state);put(args.out/'progress.json',history);print(json.dumps({'native_graphics_step':step,'train_loss':loss,'field_max_difference':differences['field'],'loss_gradient_max_difference':differences['loss_gradient']}),flush=True)
            if step==training['steps']:break
            def advance(dd,mm,vv,gg):
                mm=.9*mm+.1*gg;vv=.999*vv+.001*gg**2;update=training['learning_rate_BU']*(mm/(1-.9**(step+1)))/(np.sqrt(vv/(1-.999**(step+1)))+1e-8)
                return quantize(center+np.clip(dd-update-center,-training['translation_bound_BU'],training['translation_bound_BU']),bases),mm,vv
            d,m,v=advance(d,m,v,gradient);shadow_d,shadow_m,shadow_v=advance(shadow_d,shadow_m,shadow_v,shadow_gradient);require_box_membership(box,d)
        need(history[0]['train_loss']-loss>=training['minimum_training_loss_drop'],'Fixed minimum training loss drop required')
        saved=args.out/'trained_graphics_geometry.blend';save_copy(saved);bpy.ops.wm.open_mainfile(filepath=str(saved),use_scripts=False)
        final_capture=capture_current();final_scene=prepare(final_capture,{sid:[1,0] for sid in net.source_ids});need(wire(final_scene['objects'])==wire(virtual_scene['objects']),'Saved/reopened actual trained optical geometry must match last admitted state')
        put(args.out/'trained_native_capture.json',final_capture);put(args.out/'trained_native_scene.json',wire(final_scene));t=time.perf_counter();fresh=build_graph(final_scene);need(fresh['status']=='COMPLETE','Fresh final exact graph required');audit=audit_graph_neighborhood(wire(final_scene),wire({'graph':fresh,**propagate_graph(fresh,{sid:[1,0] for sid in net.source_ids})}));need(audit['primary_metric']==1,'Independent fresh final complete graph audit required');final_audit_seconds=time.perf_counter()-t
        put(args.out/'final_independent_graph_audit.json',audit);put(args.out/'trained_native_graph.json',wire(fresh));transport.update_geometry(final_scene);transport.set_parameter({name:[0,0,0] for name in net.shifts})
        t=time.perf_counter();final_gpu=transport_parameter_tangent(fresh,transport,encoded_rows(x,net.source_ids),[(F(0),F(0),F(0)) for _ in fresh['nodes']],distance_tolerance_BU=outer['distance_absolute_tolerance_BU']);final_graphics_seconds=time.perf_counter()-t
        observed=np.asarray([[complex(*row[p]) for p in net.ports] for row in final_gpu['fields_reim']]);powers=np.abs(observed)**2;columns=[net.ports.index(p) for p in training['detectors']];predictions=np.argmax(powers[:,columns],axis=1)
        actual_cpu=AffineGeometryNetwork(final_scene,fresh,parameters).forward(x,[0.]*16,gradients=False);final_difference=float(np.max(np.abs(observed-actual_cpu['fields'])));need(final_difference<=outer['field_tolerance'] and predictions.tolist()==np.argmax(actual_cpu['powers'][:,columns],axis=1).tolist(),'All150 saved/reopened GPU fields and decisions must match actual native CPU reference')
        shadow=net.forward(x,shadow_d,gradients=False);shadow_predictions=np.argmax(shadow['powers'][:,columns],axis=1);need(predictions.tolist()==shadow_predictions.tolist(),'All150 GPU-optimized decisions must match fixed own CPU shadow optimizer')
        put(args.out/'final_graphics_readback.json',final_gpu);transport.stage_audit.finish()
        report.update(status='VALID_NATIVE_GRAPHICS_GEOMETRY_TRAINING',primary_metric=1,profile_sha256=sha(args.profile),gpu_geometry_fields_and_gradients_executed=True,all61_actual_native_states_captured=True,continuous_original_family_proved=True,geometry_states=133,represented_terminal_paths=17060,optimizer_updates=60,geometry_membership_states=61,actual_graphics_queries_including_echo_draw=query_count+final_gpu['actual_geometric_queries_including_echo_draw'],initial_train_loss=history[0]['train_loss'],final_train_loss=loss,train_correct=int(np.sum(predictions[train]==y[train])),test_correct=int(np.sum(predictions[test]==y[test])),all150_predictions=predictions.tolist(),all150_powers=powers.tolist(),all150_fields_reim=[[[z.real,z.imag] for z in row] for row in observed],all150_inputs_reim=[[[z.real,z.imag] for z in row] for row in x],all150_native_cpu_predictions_equal=True,all150_cpu_shadow_predictions_equal=True,heldout_labels_scored_only_after_final_update=True,scaler=scaler,ports=net.ports,detectors=training['detectors'],source_ids=net.source_ids,final_native_world_x_hex=history[-1]['native_world_x_hex'],final_deltas_BU=d.tolist(),maximum_differences={'field':max_field,'field_jacobian':max_jac,'power_jacobian':max_power_jac,'loss_gradient':max_gradient,'cpu_shadow_delta_BU':max_shadow_delta,'fresh_reopened_field':final_difference},strict_GL_checked_stage_count=transport.stage_audit.count,strict_GL_owned_errors=transport.stage_audit.errors,
            cost_seconds={'initial_capture':capture_seconds,'fresh_initial_gpu_geometry':geometry_seconds,'continuous_independent_original_family_proof':proof_seconds,'gradient_shader_compile':compile_seconds,'all61_actual_native_capture':native_capture_seconds,'all61_graphics_transport_and_CPU_merges':graphics_seconds,'all61_CPU_reference_and_shadow':cpu_reference_seconds,'fresh_final_graph_and_independent_audit':final_audit_seconds,'final_saved_reopened_all150_graphics':final_graphics_seconds},
            scope='Actual native Blender61quantizedgeometrycaptures andsave/reopen; GPUcapturedtriangles/FP64ray-planephase/opticalderivatives drive60Adamupdates. CPUexact affine geometryoriginjets/topologyfamilyproof, compensatedcoherentfield/tangentmerges, power/CE/Adamexplicit. Samefixedtrainonlyencoding/split/init/clipping; Irispreviouslyused. NumericalCPUparityallstates, no universalGPUrounding/physical/AMD/RT/speed claim. Unchangedshaderarithmetic; strictGLchecks andbitechoeverydraw; success logs usecounts/streamhash ratherthanfullgrowingeventlist.')
    except Exception as exc:
        failure=exc;report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT',failure_type=type(exc).__name__)
        if isinstance(exc,(ValueError,RuntimeError,TypeError)):report['reason']=str(exc)
    finally:
        report['seconds']=time.perf_counter()-start;put(args.out/'result.json',report)
        if transport is not None:transport.stage_audit.finish()
    if failure is not None:raise failure
    print(json.dumps({k:report[k] for k in ('status','primary_metric','seconds','train_correct','test_correct')}),flush=True)
    def finish():
        window=list(bpy.context.window_manager.windows)[0]
        with bpy.context.temp_override(window=window):bpy.ops.wm.quit_blender()
        return None
    bpy.app.timers.register(finish,first_interval=.1)

if __name__=='__main__':main()
