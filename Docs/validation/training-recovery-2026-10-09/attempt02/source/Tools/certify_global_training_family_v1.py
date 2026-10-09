"""Prospective whole unchanged training-family proof before audit reuse."""
import argparse,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.train_captured_geometry_v1 import parameters_and_bases,quantize
from Blender.blender_lab.affine_box_audit_v1 import IndependentAffineBox
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Blender.blender_lab.affine_family_identity_v1 import certify_affine_identity,require_box_membership

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();args.out.mkdir(exist_ok=False);start=time.perf_counter()
    profile=json.loads(args.profile.read_bytes())
    for name,pin in profile['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen family source mismatch:'+name)
    training=json.loads((ROOT/profile['training_profile']).read_bytes());scene_wire=json.loads((ROOT/training['scene']).read_bytes());graph_wire=json.loads((ROOT/training['graph_result']).read_bytes())
    audit=audit_graph_neighborhood(scene_wire,graph_wire);need(audit['primary_metric']==1,'Independent base geometry/neighborhood required')
    scene=decode(scene_wire);graph=decode(graph_wire)['graph'];parameters,bases=parameters_and_bases(scene)
    independent=IndependentAffineBox(scene,graph,parameters);producer=AffineGeometryNetwork(scene,graph,parameters);identity=certify_affine_identity(independent,producer)
    initial=quantize(training['initial_deltas_BU'],bases);h=F(training['gradient_difference_step_BU']);radius=F(training['translation_bound_BU'])+F(training['native_quantization_allowance_BU'])
    box=[(min(F(c)-radius,F(float(d))-h),max(F(c)+radius,F(float(d))+h)) for c,d in zip(training['untrained_center_deltas_BU'],initial)]
    require_box_membership(box,initial);proof=independent.prove_box(box);proved=proof['status']=='PROVED_CONTINUOUS_AFFINE_BOX_TOPOLOGY'
    report={'schema':'optic_neuro_blender.global_training_family_certificate.v1','status':'CERTIFIED_WHOLE_DECLARED_TRAINING_FAMILY' if proved else 'VALID_UNKNOWN_WHOLE_TRAINING_FAMILY',
            'primary_metric':int(proved),'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'training_profile_sha256':profile['pins'][profile['training_profile']],
            'independent_base_geometry_audit':audit,'exact_expression_identity':identity,'continuous_topology_proof':proof,
            'parameter_ids':[p['id'] for p in parameters],'box_relative_bounds':[[[a.numerator,a.denominator],[b.numerator,b.denominator]] for a,b in box],
            'initial_quantized_deltas_BU':initial.tolist(),'seconds':time.perf_counter()-start,
            'scope':{'whole_original_projected_training_family_included':True,'all_initial_finite_difference_offsets_included':True,'audit_reuse_authorized_only_if_proved':proved,
                     'conditional_represented_geometry':True,'native_blender_transform_preimage_verified':False,'physical_error':'UNKNOWN_NOT_ZERO'}}
    (args.out/'certificate.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps({'status':report['status'],'primary_metric':report['primary_metric'],'issues':len(proof['issues']),'seconds':report['seconds']}),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
