"""Source-driven native Blender graphics frontier and coherent inference audit."""
import argparse,gc,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need,dot,vec
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.audit_coherent_state_graph_v1 import planar_objects,independent_nearest
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.native_program_lifecycle_v1 import unbind_owned_program
from Blender.blender_lab.native_graphics_gradient_v1 import NativeGraphicsGradientTransport
from Blender.blender_lab.native_graphics_gradient_network_v1 import transport_parameter_tangent
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Tools.train_captured_geometry_v1 import parameters_and_bases
import numpy as np
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
        parameters,bases=parameters_and_bases(scene)
        net=AffineGeometryNetwork(scene,own,parameters)
        inputs=[inputs[i] for i in profile['native_probe_indices']]+profile['additional_complex_probes']
        need(len(inputs)==5 and net.count==16,'Five fixed probes and16 geometric parameters required')
        x=np.array([[complex(*row[sid]) for sid in source_ids] for row in inputs])
        zero=[0.0]*16;cpu=net.forward(x,zero)
        labels=np.asarray(profile['probe_labels']);temperature=profile['loss_temperature']
        cpu_loss,cpu_loss_gradient,_=net.cross_entropy(x,labels,zero,detectors,temperature)
        report['owned_program_release']=unbind_owned_program(gpu);backend=None;gc.collect()
        t=time.perf_counter();transport=NativeGraphicsGradientTransport(gpu,scene,pixel_BU=profile['pixel_BU'],far_BU=profile['far_BU'],stage_audit_path=args.out/'native_gradient_GL_stage_audit.json');prepare_seconds=time.perf_counter()-t
        values=[];derivatives=[];power_derivatives=[];runs=[]
        for j in range(16):
            transport.set_parameter({name:[net.shifts[name][k][j] for k in range(3)] for name in net.shifts})
            tangent=transport_parameter_tangent(own,transport,inputs,[tuple(v[j] for v in origin) for origin in net.origin_jets],distance_tolerance_BU=profile['distance_absolute_tolerance_BU'])
            put(args.out/('native_graphics_parameter_'+str(j)+'.json'),wire(tangent))
            values.append(np.array([[complex(*row[p]) for p in ports] for row in tangent['fields_reim']]))
            derivatives.append(np.array([[complex(*row[p]) for p in ports] for row in tangent['field_parameter_derivative_reim']]))
            power_derivatives.append(np.array([[row[p] for p in ports] for row in tangent['power_parameter_derivative']]))
            runs.append({'parameter_index':j,'seconds':tangent['seconds'],'samples':5,'states':133,'actual_geometric_queries_including_echo_draw':tangent['actual_geometric_queries_including_echo_draw']})
            print(json.dumps({'native_parameter':j,'seconds':tangent['seconds']}),flush=True)
        field_jac=np.stack(derivatives,axis=2);power_jac=np.stack(power_derivatives,axis=2);observed=values[0];powers=np.abs(observed)**2
        field_difference=max(float(np.max(np.abs(v-cpu['fields']))) for v in values)
        parameter_field_difference=max(float(np.max(np.abs(v-observed))) for v in values)
        field_jac_difference=float(np.max(np.abs(field_jac-cpu['field_jacobian'])))
        power_jac_difference=float(np.max(np.abs(power_jac-cpu['power_jacobian'])))
        columns=[ports.index(p) for p in detectors];scores=powers[:,columns]/temperature;shifted=scores-scores.max(axis=1,keepdims=True);exponents=np.exp(shifted);prob=exponents/exponents.sum(axis=1,keepdims=True)
        loss=float(np.mean(np.log(exponents.sum(axis=1))-shifted[np.arange(5),labels]));weights=prob.copy();weights[np.arange(5),labels]-=1
        loss_gradient=np.einsum('nc,ncp->p',weights/(5*temperature),power_jac[:,columns,:])
        loss_gradient_difference=float(np.max(np.abs(loss_gradient-cpu_loss_gradient)))
        need(field_difference<=profile['field_tolerance'] and parameter_field_difference<=profile['field_tolerance'],'Native tangent execution preserves coherent fields')
        need(field_jac_difference<=profile['jacobian_absolute_tolerance'] and power_jac_difference<=profile['jacobian_absolute_tolerance'] and loss_gradient_difference<=profile['loss_gradient_absolute_tolerance'],'Frozen field/power/loss gradient agreement required')
        step=F(profile['finite_difference_step_BU']);fd_reports=[];fd_field_max=fd_power_max=fd_loss_max=0.;t=time.perf_counter()
        for j in range(16):
            offsets=[]
            for sign in (-1,1):
                delta=[0.0]*16;delta[j]=float(sign*step);shifted_scene,shifted_graph=net.materialize(delta)
                shifted_result=propagate_graph(shifted_graph,{sid:[1,0] for sid in source_ids})
                checked=audit_graph_neighborhood(wire(shifted_scene),wire({'graph':shifted_graph,**shifted_result}))
                need(checked['primary_metric']==1,'Independent complete finite-difference geometry audit required')
                finite_fields=[propagate_graph(shifted_graph,row)['fields'] for row in inputs]
                f=np.array([[row[p] for p in ports] for row in finite_fields]);p=np.abs(f)**2
                scores_fd=p[:,columns]/temperature;shifted_fd=scores_fd-scores_fd.max(axis=1,keepdims=True);exp_fd=np.exp(shifted_fd)
                loss_fd=float(np.mean(np.log(exp_fd.sum(axis=1))-shifted_fd[np.arange(5),labels]))
                offsets.append((f,p,loss_fd));fd_reports.append({'parameter_index':j,'sign':sign,'complete_independent_geometry_audit':checked})
            denominator=2*float(step);fd_field=(offsets[1][0]-offsets[0][0])/denominator;fd_power=(offsets[1][1]-offsets[0][1])/denominator;fd_loss=(offsets[1][2]-offsets[0][2])/denominator
            fd_field_max=max(fd_field_max,float(np.max(np.abs(fd_field-field_jac[:,:,j])/np.maximum(1,np.maximum(np.abs(fd_field),np.abs(field_jac[:,:,j]))))))
            fd_power_max=max(fd_power_max,float(np.max(np.abs(fd_power-power_jac[:,:,j])/np.maximum(1,np.maximum(np.abs(fd_power),np.abs(power_jac[:,:,j]))))))
            fd_loss_max=max(fd_loss_max,abs(fd_loss-loss_gradient[j])/max(1,abs(fd_loss),abs(loss_gradient[j])))
        fd_seconds=time.perf_counter()-t;put(args.out/'independent_finite_difference_geometry_audits.json',fd_reports)
        need(max(fd_field_max,fd_power_max,fd_loss_max)<=profile['finite_difference_scaled_tolerance'],'Independent central-difference numerical control required')
        need(np.max(np.abs(field_jac[-1]))==0 and np.max(np.abs(power_jac[-1]))==0,'Zero input must have zero field/power geometry gradients')
        report.update(status='VALID_NATIVE_GRAPHICS_GRADIENT_AUDIT',primary_metric=1,profile_sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),gpu_fields_executed=True,gpu_geometry_gradients_executed=True,source_driven_frontier=True,represented_terminal_paths=17060,edges=186,parameter_count=16,probe_count=5,graphics_runs=runs,
            field_max_difference=field_difference,parameter_field_max_difference=parameter_field_difference,field_jacobian_max_difference=field_jac_difference,power_jacobian_max_difference=power_jac_difference,loss_gradient_max_difference=loss_gradient_difference,
            loss=loss,reference_loss=cpu_loss,loss_gradient=loss_gradient.tolist(),reference_loss_gradient=cpu_loss_gradient.tolist(),input_probes=inputs,field_jacobian_reim=[[[[z.real,z.imag] for z in row] for row in sample] for sample in field_jac],power_jacobian=power_jac.tolist(),
            finite_difference={'step_BU':profile['finite_difference_step_BU'],'full_geometry_audits':32,'field_scaled_max_difference':fd_field_max,'power_scaled_max_difference':fd_power_max,'loss_scaled_max_difference':fd_loss_max,'seconds':fd_seconds},zero_input_zero_gradient=True,
            cost_seconds={'capture':capture_seconds,'fresh_exact_verified_gpu_geometry':geometry_seconds,'independent_full_graph_audit':audit_seconds,'gradient_shader_pack_compile_upload':prepare_seconds},
            precomputed_transfer_matrix_used=False,precomputed_optical_jacobian_matrix_used=False,cpu_affine_origin_tangents=True,cpu_compensated_field_and_tangent_merging=True,cpu_power_and_loss_chain_rule=True,
            scope='Actual GPU raster/depth selected captured surfaces; FP64 fragment shader derives ray-plane distance tangent and complex optical tangent from captured normals/materials, displacement/origin tangents and current field/tangent. CPU exact topology and affine origin/displacement tangents, compensated merges, power/loss readout explicit. Finite differences use32 independently audited materialized geometries. Five probes/all16parameters only, not universal derivative enclosure, native GPU training or physical optics.')
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
