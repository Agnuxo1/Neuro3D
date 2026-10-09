"""Secondary independent certificates of recorded native Blender outputs.

No producer propagation or training kernel is imported. Numerical correctness
and correct botanical class labels are separate quantities.
"""
import argparse,csv,hashlib,json,math,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.state_graph_enclosure_v1 import enclose_fields
from Blender.blender_lab.encoded_input_enclosure_v1 import encode_feature_row,enclose_interval_inputs
from Blender.benchmarks.capacity_audit.rational_interval_v1 import error_upper,upward_float


def certificate_from_reference(reference,observed,powers,detectors,field_budget,power_budget):
    need(set(reference)==set(observed)==set(powers),'Complete finite recorded native output required')
    ports={};intervals={};field_ok=power_ok=True
    for port,(real,imag) in reference.items():
        value=observed[port];need(set(value)=={'real','imag'} and all(math.isfinite(x) for x in [value['real'],value['imag'],powers[port]]) and powers[port]>=0,'Finite native observations required')
        power=real.square()+imag.square();intervals[port]=power
        fe=error_upper(value['real'],real)+error_upper(value['imag'],imag);pe=error_upper(powers[port],power)
        field_ok=field_ok and fe<=field_budget;power_ok=power_ok and pe<=power_budget
        ports[port]={'field_real':real.wire(),'field_imag':imag.wire(),'power':power.wire(),
                     'observed_field_error_L1_upper':[fe.numerator,fe.denominator],'observed_power_error_upper':[pe.numerator,pe.denominator],
                     'field_error_L1_upward_float':upward_float(fe),'power_error_upward_float':upward_float(pe)}
    need(len(detectors)==3 and len(set(detectors))==3 and set(detectors)<=set(reference),'Three distinct class detector modes required')
    winner=max(detectors,key=lambda p:powers[p]);margin=intervals[winner].lo-max(intervals[p].hi for p in detectors if p!=winner)
    lower=float(margin)
    if F(lower)>margin:lower=math.nextafter(lower,-math.inf)
    decision={'status':'CERTIFIED_REPRESENTED_ARGMAX' if margin>0 else 'UNKNOWN_OVERLAPPING_INTERVALS',
              'winner':winner if margin>0 else None,'observed_native_winner':winner,'margin_lower':[margin.numerator,margin.denominator],
              'margin_lower_downward_float':lower}
    return {'status':'CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS' if field_ok and power_ok else 'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET',
            'ports':ports,'decision':decision,'field_budget_passed':field_ok,'power_budget_passed':power_ok}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    profile=json.loads(args.profile.read_bytes());args.out.mkdir(exist_ok=False);start=time.perf_counter()
    for name,pin in profile['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen secondary source/input mismatch:'+name)
    result=json.loads((ROOT/profile['native_result']).read_bytes());scene_wire=json.loads((ROOT/profile['scene']).read_bytes());graph_wire=json.loads((ROOT/profile['graph_result']).read_bytes())
    receipt=json.loads((ROOT/profile['native_completion_receipt']).read_bytes())
    need(receipt['state']=='COMPLETED' and receipt['result_collected'] is True and receipt['exit_code']==0 and receipt['result_sha256']==profile['pins'][profile['native_result']], 'Recorded native completion/result provenance required')
    need(result['request_sha256']==profile['pins'][profile['native_request']], 'Recorded native request/result provenance required')
    need(result['status']=='PASS' and result['action']=='TRAIN' and result['legacy_analytic_matrix_used'] is False,'Recorded own native training result required')
    audit=audit_graph_neighborhood(scene_wire,graph_wire);need(audit['primary_metric']==1 and audit['boundary_neighborhood_independently_verified'],'Independent complete native geometry audit required')
    graph=decode(graph_wire)['graph'];ids=result['source_ids'];ports=result['ports'];detectors=profile['detectors']
    need(ids==[r['source_id'] for r in graph['roots']] and ports==graph['ports'] and detectors==result['detectors'],'Recorded source/mode order mismatch')
    gpu_supervisor=json.loads((ROOT/profile['graphics_supervisor']).read_bytes())
    gpu_result=json.loads((ROOT/profile['graphics_result']).read_bytes())
    need(gpu_supervisor['status']=='VALID_FROZEN_NATIVE_GRAPHICS_FIELD_AUDIT' and gpu_supervisor['primary_metric']==1 and gpu_supervisor['worker_exit_code']==0 and gpu_supervisor['result_sha256']==profile['pins'][profile['graphics_result']], 'Actual complete frozen GPU field provenance required')
    need(gpu_result['gpu_fields_executed'] is True and gpu_result['all150_predictions_same'] is True and gpu_result['precomputed_transfer_matrix_used'] is False, 'Actual captured-surface graphics field result required')
    actual_graph=decode(json.loads((ROOT/profile['graphics_graph']).read_bytes()))
    need(actual_graph['nodes']==graph['nodes'] and actual_graph['roots']==graph['roots'] and actual_graph['ports']==ports,'Recorded GPU field graph must equal independently audited native geometry')
    graphics=[json.loads((ROOT/n).read_bytes()) for n in profile['graphics_transports']]
    need(len(graphics)==3 and all(g['samples']==150 and g['states']==133 and g['actual_geometric_ray_queries']==19950 for g in graphics),'Three complete captured-surface GPU repetitions required')
    for repeated in graphics[1:]:
        need(repeated['fields_reim']==graphics[0]['fields_reim'] and repeated['powers']==graphics[0]['powers'],'Certificate reuse requires identical recorded binary64 outputs in all repetitions')
    x=result['all150_encoded_inputs_reim'];fields=[[g[p] for p in ports] for g in graphics[0]['fields_reim']];powers=[[g[p] for p in ports] for g in graphics[0]['powers']];predictions=result['all150_predictions']
    need(len(x)==len(fields)==len(powers)==len(predictions)==150,'All150 recorded rows required')
    rows=list(csv.DictReader((ROOT/profile['dataset']).open(encoding='utf-8')));need(len(rows)==150,'All150 Iris CSVrows required')
    raw=[[float(row[name]) for name in ('sepal_length','sepal_width','petal_length','petal_width')] for row in rows]
    labels=[['setosa','versicolor','virginica'].index(row['species']) for row in rows]
    original=json.loads((ROOT/profile['training_profile']).read_bytes());train=original['train_indices'];test=original['test_indices']
    need(len(train)==120 and len(test)==30 and set(train).isdisjoint(test) and set(train)|set(test)==set(range(150)),'Frozen complete split required')
    low=[min(raw[i][j] for i in train) for j in range(4)];high=[max(raw[i][j] for i in train) for j in range(4)]
    need(result['scaler']['fit_rows']==train and result['scaler']['lo']==low and result['scaler']['hi']==high and result['scaler']['test_clipping'] is False,'Frozen train-only scaler semantics required')
    observed_rows=[];encoding_error=F(0);input_budget=F(profile['input_error_budget']);field_budget=F(profile['field_error_budget']);power_budget=F(profile['power_error_budget'])
    for i in range(150):
        need(len(x[i])==5 and len(fields[i])==len(powers[i])==8,'Complete native scalar input/output shape required')
        need(all(len(pair)==2 and all(math.isfinite(v) for v in pair) for pair in x[i]+fields[i]),'Finite complex native pair observations required')
        native={p:{'real':fields[i][j][0],'imag':fields[i][j][1]} for j,p in enumerate(ports)};native_power=dict(zip(ports,powers[i]))
        supplied=dict(zip(ids,x[i]));ideal=encode_feature_row(raw[i],low,high,ids)
        input_errors={sid:error_upper(supplied[sid][0],ideal[sid][0])+error_upper(supplied[sid][1],ideal[sid][1]) for sid in ids}
        encoding_error=max(encoding_error,*input_errors.values())
        exact=certificate_from_reference(enclose_fields(graph,supplied),native,native_power,detectors,field_budget,power_budget)
        encoded=certificate_from_reference(enclose_interval_inputs(graph,ideal),native,native_power,detectors,field_budget,power_budget)
        winner=max(range(3),key=lambda j:native_power[detectors[j]])
        need(winner==predictions[i],'Recorded prediction/readout inconsistency')
        observed_rows.append({'row_index':i,'partition':'train' if i in train else 'test','label':labels[i],'native_prediction':winner,
                              'native_prediction_correct':winner==labels[i],'input_error_max_upward_float':upward_float(max(input_errors.values())),
                              'recorded_encoded_inputs':exact,'ideal_trainonly_encoder':encoded})
        print(json.dumps({'row':i,'exact_status':exact['status'],'encoder_status':encoded['status']}),flush=True)
    summaries={}
    for name in ('recorded_encoded_inputs','ideal_trainonly_encoder'):
        cs=[r[name] for r in observed_rows];certified=[r for r in observed_rows if r[name]['decision']['status']=='CERTIFIED_REPRESENTED_ARGMAX']
        summaries[name]={'all_field_power_budgets_passed':all(c['status']=='CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS' for c in cs),
                         'max_field_error_L1_upward_float':max(p['field_error_L1_upward_float'] for c in cs for p in c['ports'].values()),
                         'max_power_error_upward_float':max(p['power_error_upward_float'] for c in cs for p in c['ports'].values()),
                         'certified_argmax_count':len(certified),'unknown_decision_count':150-len(certified),
                         'certified_correct_count':sum(r['native_prediction_correct'] for r in certified),
                         'certified_wrong_count':sum(not r['native_prediction_correct'] for r in certified),
                         'minimum_margin_lower_downward_float':min(c['decision']['margin_lower_downward_float'] for c in cs)}
    recorded_controls=json.loads((ROOT/profile['graphics_controls']).read_bytes())
    need(recorded_controls['samples']==4,'Four recorded coherent controls required')
    supplied0=dict(zip(ids,x[0]));phase_input={sid:[-v[1],v[0]] for sid,v in supplied0.items()}
    control_inputs=[phase_input,{sid:[int(sid=='r0')-int(sid=='r1'),0] for sid in ids},{sid:[int(sid=='r0'),0] for sid in ids},{sid:[int(sid=='r1'),0] for sid in ids}]
    control_certificates=[]
    for supplied,observed,observed_power in zip(control_inputs,recorded_controls['fields_reim'],recorded_controls['powers']):
        control_certificates.append(certificate_from_reference(enclose_fields(graph,supplied),{p:{'real':observed[p][0],'imag':observed[p][1]} for p in ports},observed_power,detectors,field_budget,power_budget))
    need(len(control_certificates)==4,'Complete coherent control certificate coverage required')
    passed=encoding_error<=input_budget and all(s['all_field_power_budgets_passed'] for s in summaries.values()) and all(c['field_budget_passed'] and c['power_budget_passed'] for c in control_certificates)
    report={'schema':'optic_neuro_blender.native_graphics_field_certificate.v1','status':'CERTIFIED_OBSERVED_NATIVE_BATCH_AND_ENCODER' if passed else 'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET',
            'primary_metric':int(passed),'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'native_result_sha256':profile['pins'][profile['native_result']],'graphics_result_sha256':profile['pins'][profile['graphics_result']],'recorded_gpu_repetitions':3,'recorded_gpu_observation_count':450,'repeated_outputs_verified_identical':True,'coherence_control_certificates':control_certificates,
            'summaries':summaries,'input_encoding_error_max_upward_float':upward_float(encoding_error),'input_budget_passed':encoding_error<=input_budget,
            'train_correct':sum(predictions[i]==labels[i] for i in train),'test_correct':sum(predictions[i]==labels[i] for i in test),
            'independent_native_geometry_audit':audit,'certificates':observed_rows,'seconds':time.perf_counter()-start,
            'scope':{'observed_GPU_fragment_transport_and_CPU_merge_error_bounded':True,'GPU_transform_quantizer_preimages_certified':False,'secondary_analysis_of_previous_observations':True,'own_independent_interval_composition':True,'all450_observed_graphics_fields_powers_decisions_bounded':True,
                     'trainonly_scaler_arithmetic_error_bounded':True,'raw_feature_domain':'Exact parsed binary64 CSVvalues, not measurement or parsing preimage uncertainty',
                     'intended_geometry_error_bounded':False,'blender_transform_rounding_error_bounded':False,'unobserved_gpu_error_bounded':False,'physical_model_error':'UNKNOWN_NOT_ZERO','class_correctness_distinct_from_certified_argmax':True}}
    (args.out/'certificate.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:report[k] for k in ('status','primary_metric','summaries','input_encoding_error_max_upward_float','train_correct','test_correct','seconds')}),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
