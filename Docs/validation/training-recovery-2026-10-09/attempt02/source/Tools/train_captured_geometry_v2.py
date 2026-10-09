"""Own training with one continuous topology proof and exact membership checks."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import argparse,csv,hashlib,json,sys,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.affine_box_audit_v1 import IndependentAffineBox
from Blender.blender_lab.affine_family_identity_v1 import certify_affine_identity,require_box_membership
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph


def parameters_and_bases(scene):
    bindings=scene['blender_lab_ingress']['network_bindings']['parameters']
    expected={f'c{i}{j}.{mirror}' for i in range(4) for j in range(4) for mirror in ('r1','r2')}
    need({b['object'] for b in bindings}==expected and len(bindings)==32,'actual32Iristranslationbindings required')
    byname={b['object']:b for b in bindings};parameters=[];bases=[]
    for i in range(4):
        for j in range(4):
            pair=[f'c{i}{j}.{mirror}' for mirror in ('r1','r2')]
            values=[]
            for name in pair:
                b=byname[name];need(b['path']==['matrix_world',0,3] and b['unit']=='BU','declaredworldx binding required')
                values.append(F(float.fromhex(b['represented_value_hex'])))
            need(values[0]==values[1],'native paired mirror base coordinates differ')
            parameters.append({'id':f'c{i}{j}.paired_world_x','objects':{name:(1,0,0) for name in pair}});bases.append(values[0])
    return parameters,bases


def quantize(values,bases):
    return np.asarray([float(F(float(np.float32(float(b)+float(d))))-b) for b,d in zip(bases,values)])


def load_data(path,train_indices,source_ids):
    rows=list(csv.DictReader(path.open(encoding='utf-8')))
    raw=np.asarray([[float(row[k]) for k in ('sepal_length','sepal_width','petal_length','petal_width')] for row in rows])
    labels=np.asarray([['setosa','versicolor','virginica'].index(row['species']) for row in rows],dtype=np.int64)
    low,high=raw[train_indices].min(axis=0),raw[train_indices].max(axis=0)
    need(np.all(high>low),'training feature range must be positive')
    scaled=(raw-low)/(high-low)
    encoded=np.zeros((len(raw),len(source_ids)),dtype=np.complex128)
    for column,sid in enumerate(('r0','r1','c0','c1')):encoded[:,source_ids.index(sid)]=scaled[:,column]
    encoded[:,source_ids.index('c2')]=1
    encoded/=np.sqrt((np.abs(encoded)**2).sum(axis=1,keepdims=True))
    return encoded,labels,{'fit_rows':list(train_indices),'lo':low.tolist(),'hi':high.tolist(),'test_clipping':False,'reference_amplitude':1,'encoding':'REAL_COMMON_COHERENCE_UNIT_INPUT_POWER'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();outer=json.loads(args.profile.read_bytes());args.out.mkdir(exist_ok=False)
    for name,pin in outer['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen reuse source mismatch:'+name)
    profile=json.loads((ROOT/outer['training_profile']).read_bytes())
    scene=decode(json.loads((ROOT/profile['scene']).read_text()));result=decode(json.loads((ROOT/profile['graph_result']).read_text()))
    parameters,bases=parameters_and_bases(scene)
    start=time.perf_counter();net=AffineGeometryNetwork(scene,result['graph'],parameters);compile_seconds=time.perf_counter()-start
    t=time.perf_counter()
    base_audit=audit_graph_neighborhood(wire(scene),wire(result));need(base_audit['primary_metric']==1,'Independent base audit required')
    independent=IndependentAffineBox(scene,result['graph'],parameters);identity=certify_affine_identity(independent,net)
    initial=quantize(profile['initial_deltas_BU'],bases);h=F(profile['gradient_difference_step_BU']);radius=F(profile['translation_bound_BU'])+F(profile['native_quantization_allowance_BU'])
    box=[(min(F(c)-radius,F(float(d))-h),max(F(c)+radius,F(float(d))+h)) for c,d in zip(profile['untrained_center_deltas_BU'],initial)]
    continuous=independent.prove_box(box);need(continuous['status']=='PROVED_CONTINUOUS_AFFINE_BOX_TOPOLOGY','Whole original training family must be proved')
    family={'base_geometry_audit':base_audit,'exact_expression_identity':identity,'continuous_topology_proof':continuous,'box_relative_bounds':[[[a.numerator,a.denominator],[b.numerator,b.denominator]] for a,b in box]}
    (args.out/'continuous_family_proof.json').write_bytes((json.dumps(family,indent=2)+'\n').encode())
    family_seconds=time.perf_counter()-t
    train,test=profile['train_indices'],profile['test_indices']
    need(len(train)==120 and len(test)==30 and set(train).isdisjoint(test) and set(train)|set(test)==set(range(150)),'complete frozen split required')
    x,y,scaler=load_data(ROOT/profile['dataset'],train,net.source_ids)
    center=np.asarray(profile['untrained_center_deltas_BU'])
    d=quantize(profile['initial_deltas_BU'],bases);detectors=profile['detectors'];temperature=profile['loss_temperature']
    loss,gradient,_=net.cross_entropy(x[train],y[train],d,detectors,temperature)
    initial_loss=loss;h=profile['gradient_difference_step_BU'];errors=[]
    for j in range(len(d)):
        delta=np.eye(len(d))[j]*h
        require_box_membership(box,d+delta);require_box_membership(box,d-delta)
        a=net.cross_entropy(x[train],y[train],d+delta,detectors,temperature)[0]
        b=net.cross_entropy(x[train],y[train],d-delta,detectors,temperature)[0]
        errors.append(abs((a-b)/(2*h)-gradient[j]))
    need(max(errors)<=profile['gradient_absolute_tolerance'],'captured training gradient difference gate')
    history=[];m=np.zeros(len(d));v=np.zeros(len(d));audit_seconds=0;train_seconds=0
    with (args.out/'progress.jsonl').open('x',encoding='utf-8') as stream:
        for step in range(profile['steps']+1):
            t=time.perf_counter();audit=require_box_membership(box,d);audit_seconds+=time.perf_counter()-t
            t=time.perf_counter();loss,gradient,_=net.cross_entropy(x[train],y[train],d,detectors,temperature);train_seconds+=time.perf_counter()-t
            row={'step':step,'train_loss':loss,'gradient_max_abs':float(np.max(np.abs(gradient))), 'deltas_BU':d.tolist(),'continuous_family_membership':audit}
            history.append(row);stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
            print(json.dumps({'step':step,'train_loss':loss,'continuous_family_membership':audit['status']}),flush=True)
            if step==profile['steps']:break
            m=.9*m+.1*gradient;v=.999*v+.001*gradient**2
            update=profile['learning_rate_BU']*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
            proposed=center+np.clip(d-update-center,-profile['translation_bound_BU'],profile['translation_bound_BU'])
            d=quantize(proposed,bases)
            need(np.max(np.abs(d-center))<=profile['translation_bound_BU']+profile['native_quantization_allowance_BU'],'quantized translation bound')
    final=net.forward(x,d,gradients=False);columns=[net.ports.index(p) for p in detectors]
    predictions=np.argmax(final['powers'][:,columns],axis=1)
    scene_final,materialized=net.materialize(d)
    t=time.perf_counter();rebuilt=build_graph(scene_final);rebuild_seconds=time.perf_counter()-t
    need(rebuilt['status']=='COMPLETE','final fresh geometric rebuild must be complete')
    fresh_columns=[]
    for basis in np.eye(len(net.source_ids),dtype=complex):
        outputs=propagate_graph(rebuilt,{s:[a.real,a.imag] for s,a in zip(net.source_ids,basis)})['fields']
        fresh_columns.append([outputs[p] for p in net.ports])
    fresh=np.asarray(fresh_columns).T@x.T
    reconstruction_error=float(np.max(np.abs(final['fields']-fresh.T)))
    need(reconstruction_error<=profile['field_rebuild_tolerance'],'final fresh geometric field reconstruction gate')
    trial={'schema':'optic_neuro_blender.continuous_family_training.v1','status':'PASS' if initial_loss-loss>=profile['minimum_training_loss_drop'] else 'FAIL_LOSS_DROP',
        'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'initial_train_loss':initial_loss,'final_train_loss':loss,
        'train_accuracy':float(np.mean(predictions[train]==y[train])),'heldout_accuracy':float(np.mean(predictions[test]==y[test])),
        'train_correct':int(np.sum(predictions[train]==y[train])),'test_correct':int(np.sum(predictions[test]==y[test])),
        'heldout_labels_used_for_scoring_only_after_final_update':True,'dataset_previously_used_in_project':True,
        'gradient_difference_max_absolute_error':max(errors),'field_rebuild_max_absolute_error':reconstruction_error,
        'parameter_ids':net.parameter_ids,'native_base_world_x_hex':[float(b).hex() for b in bases],
        'final_deltas_BU':d.tolist(),'final_native_world_x_hex':[float(float(b)+float(v)).hex() for b,v in zip(bases,d)],
        'parameters':parameters,'source_ids':net.source_ids,'ports':net.ports,'detectors':detectors,'scaler':scaler,
        'initialization_policy':profile['initialization_policy'],'untrained_center_deltas_BU':center.tolist(),
        'predictions':predictions.tolist(),'observed_powers':final['powers'].tolist(),
        'cost_seconds':{'continuous_independent_proof':family_seconds,'affine_compile':compile_seconds,'own_loss_and_gradient_updates':train_seconds,'exact_family_membership_checks':audit_seconds,'fresh_final_geometric_rebuild':rebuild_seconds},
        'geometry_audited_states':0,'geometry_membership_states':len(history),'continuous_family_proved_states':continuous['states'],'exact_affine_expression_identity':identity['status'],'own_analytic_transfer_matrix_used':False,'gpu_executed':False,
        'scope':'One independent proof of every point in original represented training region plus61exactparameter membership checks; not61separatepointaudits. Ownforward/Jacobian/CE/Adam/quantization unchanged. Proof overhead and fresh finalrebuild included; native Blender recapture and physical fidelity separate.'}
    (args.out/'result.json').write_bytes((json.dumps(trial,indent=2,allow_nan=False)+'\n').encode())
    (args.out/'final_virtual_scene.json').write_bytes((json.dumps(wire(scene_final),indent=2,allow_nan=False)+'\n').encode())
    (args.out/'final_virtual_graph.json').write_bytes((json.dumps(wire(rebuilt),indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:trial[k] for k in ('status','initial_train_loss','final_train_loss','train_accuracy','heldout_accuracy','gradient_difference_max_absolute_error','field_rebuild_max_absolute_error')}),flush=True)
    return 0 if trial['status']=='PASS' else 2


if __name__=='__main__':raise SystemExit(main())
