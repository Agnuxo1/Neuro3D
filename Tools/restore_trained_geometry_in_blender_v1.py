"""Apply frozen native coordinates, save/reopen, recapture and rebuild inference."""
import copy,hashlib,json,sys,time
from pathlib import Path
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.train_captured_geometry_v1 import parameters_and_bases,load_data
from Blender.blender_lab.scene_capture_v1 import capture_scene,canonical_bytes
from Blender.blender_lab.coherent_contract_v1 import prepare_coherent_scene
from Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire
from Blender.blender_lab.coherent_state_graph_v1 import build_graph
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork


def main():
    args=sys.argv[sys.argv.index('--')+1:];profile_path,out=Path(args[0]),Path(args[1]);out.mkdir(exist_ok=False)
    profile=json.loads(profile_path.read_text());training_path=ROOT/profile['training_result'];training=json.loads(training_path.read_text())
    need(training['status']=='PASS','successful frozen training receipt required')
    original_path=Path(bpy.data.filepath);original_pin=hashlib.sha256(original_path.read_bytes()).hexdigest()
    for parameter,position in zip(training['parameters'],training['final_native_world_x_hex']):
        value=float.fromhex(position)
        for name in parameter['objects']:
            obj=bpy.data.objects.get(name);need(obj is not None and obj.animation_data is None,'static unique saved translation target required')
            matrix=obj.matrix_world.copy();matrix[0][3]=value;obj.matrix_world=matrix
    bpy.context.view_layer.update()
    bpy.context.scene['optic_neuro_blender_active_model']='AFFINE_CAPTURED_GEOMETRY_TRAINING_V1'
    bpy.context.scene['optic_neuro_blender_training_result_sha256']=hashlib.sha256(training_path.read_bytes()).hexdigest()
    bpy.context.scene['optic_neuro_blender_trained_positions_hex']=json.dumps(dict(zip(training['parameter_ids'],training['final_native_world_x_hex'])),sort_keys=True)
    network=json.loads((ROOT/profile['network']).read_text())
    before=capture_scene(network=network)
    (out/'capture_before_save.json').write_bytes(canonical_bytes(before))
    saved=out/'trained_geometry.blend';bpy.ops.wm.save_as_mainfile(filepath=str(saved))
    bpy.ops.wm.open_mainfile(filepath=str(saved),load_ui=False,use_scripts=False)
    after=capture_scene(network=network)
    (out/'capture_after_reopen.json').write_bytes(canonical_bytes(after))
    need(before['state_sha256']==after['state_sha256'],'saved/reopened capture identity mismatch')
    semantics=json.loads((ROOT/profile['semantics']).read_text());contract=json.loads((ROOT/profile['contract']).read_text())
    semantics['capture_state_sha256']=contract['capture_state_sha256']=after['state_sha256']
    fields=json.loads((ROOT/profile['fields']).read_text())
    packet=prepare_coherent_scene(after,semantics,fields,contract)
    virtual=decode(json.loads((ROOT/profile['virtual_scene']).read_text()))
    need(rational_wire(packet['objects'])==rational_wire(virtual['objects']) and packet['lambda_BU']==virtual['lambda_BU'],'native Blender recapture differs from trained represented optical geometry')
    need(rational_wire(packet['sources'])==rational_wire(virtual['sources']),'native Blender source geometry/coherent fields changed')
    (out/'semantics.json').write_bytes(canonical_bytes(semantics));(out/'contract.json').write_bytes(canonical_bytes(contract))
    (out/'scene.json').write_bytes(canonical_bytes(rational_wire(packet)))
    t=time.perf_counter();graph=build_graph(packet);rebuild_seconds=time.perf_counter()-t
    need(graph['status']=='COMPLETE','recaptured geometric graph must complete')
    parameters,bases=parameters_and_bases(packet);net=AffineGeometryNetwork(packet,graph,parameters)
    training_profile=json.loads((ROOT/profile['training_profile']).read_text())
    x,y,scaler=load_data(ROOT/training_profile['dataset'],training_profile['train_indices'],net.source_ids)
    output=net.forward(x,np.zeros(16),gradients=False)
    need(net.ports==training['ports'] and net.source_ids==training['source_ids'] and scaler==training['scaler'],'readout/input/scaler identity changed after reopening')
    difference=float(np.max(np.abs(output['powers']-np.asarray(training['observed_powers']))))
    columns=[net.ports.index(p) for p in training['detectors']];predictions=np.argmax(output['powers'][:,columns],axis=1)
    need(difference<=profile['power_tolerance'] and predictions.tolist()==training['predictions'],'saved/reopened inference mismatch')
    need(hashlib.sha256(original_path.read_bytes()).hexdigest()==original_pin,'original blend changed')
    report={'schema':'optic_neuro_blender.native_saved_geometry_training_reproduction.v1','status':'PASS',
        'profile_sha256':hashlib.sha256(profile_path.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'blender_build_hash':bpy.app.build_hash.decode(),
        'original_scene_sha256':original_pin,'saved_scene_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),
        'capture_state_sha256':after['state_sha256'],'before_after_identity_equal':True,'native_recapture_matches_trained_represented_geometry':True,
        'fresh_rebuilt_states':len(graph['nodes']),'fresh_rebuild_seconds':rebuild_seconds,'all150_predictions_match':True,
        'max_observed_power_difference':difference,'source_ids':net.source_ids,'ports':net.ports,'powers':output['powers'].tolist(),'predictions':predictions.tolist(),
        'scope':'Actual Blender native transform update, save/reopen, capture and own geometry inference; local reproduction, not external replication or physical optics',
        'gpu_executed':False,'physical_calibration_verified':False}
    (out/'graph.json').write_bytes(canonical_bytes(rational_wire(graph)))
    (out/'result.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:report[k] for k in ('status','blender_version','fresh_rebuilt_states','all150_predictions_match','max_observed_power_difference')}),flush=True)


if __name__=='__main__':main()
