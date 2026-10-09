"""Conditional continuous parameter boxes; no claim of full native/physical error."""
import argparse,csv,hashlib,json,math,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.affine_box_audit_v1 import IndependentAffineBox
from Blender.blender_lab.encoded_input_enclosure_v1 import encode_feature_row
from Blender.benchmarks.capacity_audit.rational_interval_v1 import error_upper,upward_float


def describe(reference,native_fields,native_powers,detectors):
    ports={};powers={}
    for port,(real,imag) in reference.items():
        power=real.square()+imag.square();powers[port]=power
        fe=error_upper(native_fields[port][0],real)+error_upper(native_fields[port][1],imag);pe=error_upper(native_powers[port],power)
        ports[port]={'field_real':real.wire(),'field_imag':imag.wire(),'power':power.wire(),
                     'native_center_to_any_box_field_L1_bound_upward_float':upward_float(fe),'native_center_to_any_box_power_bound_upward_float':upward_float(pe)}
    winner=max(detectors,key=lambda p:native_powers[p]);margin=powers[winner].lo-max(powers[p].hi for p in detectors if p!=winner)
    lower=float(margin)
    if F(lower)>margin:lower=math.nextafter(lower,-math.inf)
    return {'ports':ports,'decision':{'status':'CERTIFIED_SAME_ARGMAX_OVER_ENTIRE_BOX' if margin>0 else 'UNKNOWN_OVERLAPPING_BOX_POWER_INTERVALS',
                                    'winner':winner if margin>0 else None,'native_center_winner':winner,'margin_lower':[margin.numerator,margin.denominator],
                                    'margin_lower_downward_float':lower}}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();args.out.mkdir(exist_ok=False);start=time.perf_counter()
    profile=json.loads(args.profile.read_bytes())
    for name,pin in profile['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen box analysis source mismatch:'+name)
    result=json.loads((ROOT/profile['native_result']).read_bytes());previous=json.loads((ROOT/profile['native_batch_certificate']).read_bytes())
    need(previous['status']=='CERTIFIED_OBSERVED_NATIVE_BATCH_AND_ENCODER' and previous['native_result_sha256']==profile['pins'][profile['native_result']],'Prior native arithmetic certificate identity required')
    scene_wire=json.loads((ROOT/profile['scene']).read_bytes());graph_wire=json.loads((ROOT/profile['graph_result']).read_bytes())
    audit=audit_graph_neighborhood(scene_wire,graph_wire);need(audit['primary_metric']==1,'Independent base geometry/neighborhood audit required')
    scene=decode(scene_wire);graph=decode(graph_wire)['graph'];parameters=result['training']['parameters'];ids=result['source_ids'];ports=result['ports'];detectors=profile['detectors']
    need(ids==[r['source_id'] for r in graph['roots']] and ports==graph['ports'] and detectors==result['detectors'],'Complete frozen source/port identity required')
    expected=[{'id':f'c{i}{j}.paired_world_x','objects':{f'c{i}{j}.r1':[1,0,0],f'c{i}{j}.r2':[1,0,0]}} for i in range(4) for j in range(4)]
    need(parameters==expected,'Fixed16 paired worldXtranslation parameters required')
    bindings={b['object']:b for b in scene['blender_lab_ingress']['network_bindings']['parameters']};cells=[];base_box=[]
    for j,parameter in enumerate(parameters):
        values=[float.fromhex(bindings[name]['represented_value_hex']) for name in parameter['objects']]
        need(len(values)==2 and values[0]==values[1] and values[0].hex()==result['training']['final_native_world_x_hex'][j],'Actual paired coordinate identity required')
        value=values[0];binary=np.float32(value);need(float(binary)==value and math.isfinite(value),'Exact finite represented binary32 coordinate required')
        before=F(float(np.nextafter(binary,np.float32(-np.inf))));after=F(float(np.nextafter(binary,np.float32(np.inf))));center=F(value)
        low=(before-center)/2;high=(after-center)/2;need(low<0<high,'Strict adjacent coordinate spacing required')
        cells.append({'parameter':parameter['id'],'world_x_hex':value.hex(),'lower_relative_half_spacing':[low.numerator,low.denominator],'upper_relative_half_spacing':[high.numerator,high.denominator]});base_box.append((low,high))
    rows=list(csv.DictReader((ROOT/profile['dataset']).open(encoding='utf-8')));need(len(rows)==150,'Complete fixed Iris rows required')
    raw=[[float(row[name]) for name in ('sepal_length','sepal_width','petal_length','petal_width')] for row in rows];labels=[['setosa','versicolor','virginica'].index(row['species']) for row in rows]
    training=json.loads((ROOT/profile['training_profile']).read_bytes());train=training['train_indices'];test=training['test_indices'];low=[min(raw[i][j] for i in train) for j in range(4)];high=[max(raw[i][j] for i in train) for j in range(4)]
    need(low==result['scaler']['lo'] and high==result['scaler']['hi'] and train==result['scaler']['fit_rows'],'Independent train-only scaler identity required')
    inputs=[encode_feature_row(row,low,high,ids) for row in raw];net=IndependentAffineBox(scene,graph,parameters);cases=[]
    for scale in profile['half_spacing_multipliers']:
        t=time.perf_counter();box=[(a*scale,b*scale) for a,b in base_box];proof=net.prove_box(box)
        case={'multiplier':scale,'box_relative_bounds':[[[a.numerator,a.denominator],[b.numerator,b.denominator]] for a,b in box],
              'max_absolute_shift_BU_upward_float':upward_float(max(max(abs(a),abs(b)) for a,b in box)), 'topology_proof':proof}
        if proof['status']=='PROVED_CONTINUOUS_AFFINE_BOX_TOPOLOGY':
            certified=[]
            for i,values in enumerate(inputs):
                reference=net.enclose_fields(box,values);native_fields=dict(zip(ports,result['all150_native_fields_reim'][i]));native_powers=dict(zip(ports,result['all150_native_powers'][i]))
                row=describe(reference,native_fields,native_powers,detectors);row.update(row_index=i,label=labels[i],native_prediction=result['all150_predictions'][i],native_center_prediction_correct=result['all150_predictions'][i]==labels[i],partition='train' if i in train else 'test');certified.append(row)
            separated=[r for r in certified if r['decision']['status']=='CERTIFIED_SAME_ARGMAX_OVER_ENTIRE_BOX']
            case.update(status='VALID_PROVED_PARAMETER_BOX_WITH_ALL150_ROWS',rows=certified,summary={'same_argmax_certified':len(separated),'unknown_decisions':150-len(separated),
                        'certified_correct':sum(r['native_center_prediction_correct'] for r in separated),'certified_wrong':sum(not r['native_center_prediction_correct'] for r in separated),
                        'minimum_margin_lower_downward_float':min(r['decision']['margin_lower_downward_float'] for r in certified),
                        'max_native_center_to_any_box_field_L1_bound_upward_float':max(v['native_center_to_any_box_field_L1_bound_upward_float'] for r in certified for v in r['ports'].values()),
                        'max_native_center_to_any_box_power_bound_upward_float':max(v['native_center_to_any_box_power_bound_upward_float'] for r in certified for v in r['ports'].values())})
        else:case.update(status='VALID_UNKNOWN_PARAMETER_BOX_TOPOLOGY',rows=None,summary={'same_argmax_certified':0,'unknown_decisions':150,'reason':'Unproved geometry must not produce output fields'})
        case['seconds']=time.perf_counter()-t;cases.append(case);print(json.dumps({'multiplier':scale,'status':case['status'],'summary':case['summary'],'seconds':case['seconds']}),flush=True)
    report={'schema':'optic_neuro_blender.conditional_parameter_box_certificate.v1','status':'VALID_CONDITIONAL_PARAMETER_BOX_ANALYSIS','primary_metric':1,'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),
            'native_result_sha256':profile['pins'][profile['native_result']],'conditional_coordinate_cells':cells,'independent_base_geometry_audit':audit,'cases':cases,'seconds':time.perf_counter()-start,
            'scope':{'entire_continuous_declared_parameter_boxes_analyzed':True,'same_paired_translation_applies_to_both_mirrors':True,'half_adjacent_binary32_spacing_is_conditional_box_definition_not_verified_native_pipeline_preimage':True,
                     'intended_mesh_and_transform_preimages_bounded':False,'blender_native_transform_arithmetic_bounded':False,'unobserved_perturbed_native_execution_error_bounded':False,
                     'physical_model_error':'UNKNOWN_NOT_ZERO','input_measurement_uncertainty':'UNKNOWN_NOT_ZERO','unknown_does_not_mean_demonstrated_instability':True}}
    (args.out/'certificate.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode());print(json.dumps({'status':report['status'],'seconds':report['seconds']}),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
