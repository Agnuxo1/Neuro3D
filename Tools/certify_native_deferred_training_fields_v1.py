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
    need(receipt['status']=='VALID_FROZEN_NATIVE_DEFERRED_GRAPHICS_GEOMETRY_TRAINING' and receipt['primary_metric']==1 and receipt['worker_exit_code']==0 and receipt['result_sha256']==profile['pins'][profile['native_result']],'Recorded complete native graphics learning provenance required')
    need(result['status']=='VALID_NATIVE_GRAPHICS_GEOMETRY_TRAINING' and result['gpu_geometry_fields_and_gradients_executed'] is True and result['all61_actual_native_states_captured'] is True and result['optimizer_updates']==60 and result['geometry_membership_states']==61 and result['actual_geometry_cache_generations']==62,'All61 actual native captured states and60 graphical updates required')
    producer_pin=profile['pins'][profile['producer_profile']];need(result['profile_sha256']==producer_pin and receipt['profile_sha256']==producer_pin,'Immutable producer-profile identity required')
    ids=result['source_ids'];ports=result['ports'];detectors=profile['detectors']
    x=result['all150_inputs_reim'];fields=result['all150_fields_reim'];powers=result['all150_powers'];predictions=result['all150_predictions']
    need(len(fields)==len(powers)==150 and len(fields[0])==len(powers[0])==8,'Complete final recorded outputs required')
    wrapped={'graph':graph_wire,'fields':{p:{'real':fields[0][j][0],'imag':fields[0][j][1]} for j,p in enumerate(ports)},'powers':dict(zip(ports,powers[0]))}
    audit=audit_graph_neighborhood(scene_wire,wrapped);need(audit['primary_metric']==1 and audit['boundary_neighborhood_independently_verified'],'Independent complete final native geometry audit required')
    graph=decode(graph_wire)
    need(ids==[r['source_id'] for r in graph['roots']] and ports==graph['ports'] and detectors==result['detectors'],'Recorded source/mode order mismatch')
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
    passed=encoding_error<=input_budget and all(s['all_field_power_budgets_passed'] for s in summaries.values())
    report={'schema':'optic_neuro_blender.native_deferred_training_field_certificate.v1','status':'CERTIFIED_OBSERVED_NATIVE_BATCH_AND_ENCODER' if passed else 'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET',
            'primary_metric':int(passed),'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'native_result_sha256':profile['pins'][profile['native_result']],
            'summaries':summaries,'input_encoding_error_max_upward_float':upward_float(encoding_error),'input_budget_passed':encoding_error<=input_budget,
            'train_correct':sum(predictions[i]==labels[i] for i in train),'test_correct':sum(predictions[i]==labels[i] for i in test),
            'independent_native_geometry_audit':audit,'certificates':observed_rows,'seconds':time.perf_counter()-start,
            'scope':{'secondary_analysis_of_previous_observations':True,'own_independent_interval_composition':True,'all150_final_observed_deferred_graphics_fields_powers_decisions_bounded':True,'all_training_gradient_errors_interval_certified':False,'GPU_transform_quantizer_preimages_certified':False,'graphics_fragment_and_CPU_merge_observation_error_bounded':True,
                     'trainonly_scaler_arithmetic_error_bounded':True,'raw_feature_domain':'Exact parsed binary64 CSVvalues, not measurement or parsing preimage uncertainty',
                     'intended_geometry_error_bounded':False,'blender_transform_rounding_error_bounded':False,'unobserved_gpu_error_bounded':False,'physical_model_error':'UNKNOWN_NOT_ZERO','class_correctness_distinct_from_certified_argmax':True}}
    (args.out/'certificate.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:report[k] for k in ('status','primary_metric','summaries','input_encoding_error_max_upward_float','train_correct','test_correct','seconds')}),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
