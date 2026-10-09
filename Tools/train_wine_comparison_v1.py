"""Frozen three-seed Wine experiment with every geometry state audited."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.trace_indexed_scene_v1 import wire
from Tools.train_captured_geometry_v1 import parameters_and_bases,quantize,audit_state
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Blender.blender_lab.classifier_comparison_v1 import encode_real_features,fit_baseline,baseline_scores,classification_metrics,paired_comparison,equivalent_real_quadratic


def load_wine(path):
    raw=np.loadtxt(path,delimiter=',')
    need(raw.shape==(178,14) and np.isfinite(raw).all(),'original UCI178x14Wine data required')
    labels=raw[:,0].astype(np.int64)-1
    need(np.array_equal(labels+1,raw[:,0]) and np.array_equal(np.bincount(labels),[59,71,48]),'fixed Wine label counts required')
    return raw[:,1:5],labels


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();profile=json.loads(args.profile.read_bytes());args.out.mkdir(exist_ok=False)
    start=time.perf_counter()
    scene=decode(json.loads((ROOT/profile['scene']).read_bytes()));original=decode(json.loads((ROOT/profile['graph_result']).read_bytes()))
    params,bases=parameters_and_bases(scene);net=AffineGeometryNetwork(scene,original['graph'],params)
    train,test=profile['train_indices'],profile['test_indices']
    need(len(train)==141 and len(test)==37 and set(train).isdisjoint(test) and set(train)|set(test)==set(range(178)),'fixed141/37split required')
    raw,y=load_wine(ROOT/profile['dataset']);x,scaler=encode_real_features(raw,train,net.source_ids)
    # Holdout labels are loaded to verify stratification, not used in any fit/update/selection.
    need(np.array_equal(np.bincount(y[train]),[47,56,38]) and np.array_equal(np.bincount(y[test]),[12,15,10]),'frozen stratification required')
    baselines=[fit_baseline(x[train],y[train],kind,profile['baseline_optimizer']) for kind in ('linear','quadratic')]
    majority=int(np.argmax(np.bincount(y[train])))
    columns=[net.ports.index(p) for p in profile['detectors']];center=np.asarray(profile['untrained_center_deltas_BU'])
    final_runs=[]
    for initialization in profile['initializations']:
        seed=initialization['seed'];output=args.out/('seed'+str(seed));output.mkdir()
        d=quantize(initialization['deltas_BU'],bases);m=np.zeros(16);v=np.zeros(16);audit_seconds=0.;update_seconds=0.;history=[]
        first,gradient,_=net.cross_entropy(x[train],y[train],d,profile['detectors'],profile['loss_temperature'])
        h=profile['gradient_difference_step_BU'];errors=[]
        for j in range(16):
            delta=np.eye(16)[j]*h
            a=net.cross_entropy(x[train],y[train],d+delta,profile['detectors'],profile['loss_temperature'])[0]
            b=net.cross_entropy(x[train],y[train],d-delta,profile['detectors'],profile['loss_temperature'])[0]
            errors.append(abs((a-b)/(2*h)-gradient[j]))
        need(max(errors)<=profile['gradient_absolute_tolerance'],'all16initiallossgradientFD gate')
        run_start=time.perf_counter()
        with (output/'progress.jsonl').open('x',encoding='utf-8') as stream:
            for step in range(profile['steps']+1):
                tick=time.perf_counter();audit=audit_state(net,d,step);audit_seconds+=time.perf_counter()-tick
                tick=time.perf_counter();loss,gradient,_=net.cross_entropy(x[train],y[train],d,profile['detectors'],profile['loss_temperature']);update_seconds+=time.perf_counter()-tick
                row={'seed':seed,'step':step,'train_loss':loss,'gradient_max_abs':float(np.max(np.abs(gradient))),'deltas_BU':d.tolist(),'geometry_audit':audit}
                history.append(row);stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush()
                print(json.dumps({'seed':seed,'step':step,'train_loss':loss,'geometry_audit':audit['primary_metric']}),flush=True)
                if step==profile['steps']:break
                m=.9*m+.1*gradient;v=.999*v+.001*gradient**2
                change=profile['learning_rate_BU']*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
                d=quantize(center+np.clip(d-change-center,-profile['translation_bound_BU'],profile['translation_bound_BU']),bases)
                need(np.max(np.abs(d-center))<=profile['translation_bound_BU']+profile['native_quantization_allowance_BU'],'boundedquantizedtranslation gate')
        # No holdout accuracy is computed until all fixed updates of this run have finished.
        final=net.forward(x,d,gradients=False);prediction=np.argmax(final['powers'][:,columns],axis=1)
        final_scene,materialized=net.materialize(d)
        tick=time.perf_counter();rebuilt=build_graph(final_scene);rebuild_seconds=time.perf_counter()-tick
        need(rebuilt['status']=='COMPLETE','fresh final geometric trace must complete')
        transfer=np.asarray([[propagate_graph(rebuilt,{sid:[value.real,value.imag] for sid,value in zip(net.source_ids,basis)})['fields'][port]
                              for port in net.ports] for basis in np.eye(5,dtype=complex)]).T
        fresh_error=float(np.max(np.abs(final['fields']-(transfer@x.T).T)))
        need(fresh_error<=profile['field_rebuild_tolerance'],'freshgeometryall178fields gate')
        run={'seed':seed,'status':'PASS' if first-loss>=profile['minimum_training_loss_drop'] else 'FAIL_LOSS_DROP',
             'initial_train_loss':first,'final_train_loss':loss,'gradient_difference_max_absolute_error':max(errors),
             'geometry_audited_states':len(history),'field_rebuild_max_absolute_error':fresh_error,'final_deltas_BU':d.tolist(),
             'final_native_world_x_hex':[float(float(b)+float(v)).hex() for b,v in zip(bases,d)],
             'predictions':prediction.tolist(),'train':classification_metrics(prediction[train],y[train]),'heldout':classification_metrics(prediction[test],y[test]),
             'equivalent_dense_quadratic':equivalent_real_quadratic(net,d,x),'cost_seconds':{'all_geometry_audits':audit_seconds,'own_loss_and_gradient':update_seconds,'fresh_geometric_rebuild':rebuild_seconds,'seed_training_plus_rebuild':time.perf_counter()-run_start},
             'nominal_geometric_parameters':16,'native_base_world_x_hex':[float(b).hex() for b in bases]}
        (output/'result.json').write_bytes((json.dumps(run,indent=2,allow_nan=False)+'\n').encode())
        for filename,item in [('final_virtual_scene.json',final_scene),('final_virtual_graph.json',rebuilt)]:
            (output/filename).write_bytes((json.dumps(wire(item),indent=2,allow_nan=False)+'\n').encode())
        final_runs.append(run)
    # Baseline holdout scoring and all paired reports occur after every optical run, no feedback into fits.
    for baseline in baselines:
        tick=time.perf_counter();pred=np.argmax(baseline_scores(baseline,x),axis=1);baseline['score_seconds']=time.perf_counter()-tick
        baseline.update(predictions=pred.tolist(),train=classification_metrics(pred[train],y[train]),heldout=classification_metrics(pred[test],y[test]))
        for run in final_runs:
            run.setdefault('paired_baselines',{})[baseline['kind']]=paired_comparison(np.asarray(run['predictions'])[test],pred[test],y[test])
    result={'schema':'optic_neuro_blender.wine_comparison.v1','status':'PASS' if all(run['status']=='PASS' for run in final_runs) else 'FAIL_ONE_OR_MORE_TRAINING_LOSS_GATES',
            'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'features':['alcohol','malic_acid','ash','alcalinity_of_ash'],
            'train_indices':train,'test_indices':test,'labels':y.tolist(),'source_ids':net.source_ids,'scaler':scaler,'runs':final_runs,'baselines':baselines,
            'majority':{'selected_from_train':majority,'train':classification_metrics(np.full(len(train),majority),y[train]),'heldout':classification_metrics(np.full(len(test),majority),y[test])},
            'all_seeds_reported_without_selection':True,'heldout_labels_used_for_updates_or_model_selection':False,
            'dataset_scope':'Public UCI Wine, newly evaluated in this sequence, fixed first4of13features; retraining and within-dataset holdout, not zero-shot transfer, external blinded data, or independent reproduction',
            'no_claim_of_optical_superiority':True,'gpu_executed':False,'worker_compute_seconds':time.perf_counter()-start}
    (args.out/'result.json').write_bytes((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':result['status'],'own_heldout_correct':[r['heldout']['correct'] for r in final_runs],'baseline_heldout_correct':{r['kind']:r['heldout']['correct'] for r in baselines}}),flush=True)
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':raise SystemExit(main())
