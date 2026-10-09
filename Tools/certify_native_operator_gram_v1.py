"""Frozen independent all-channel operator analysis of the native trained graph."""
import argparse,hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.state_graph_enclosure_v1 import enclose_fields
from Blender.blender_lab.operator_gram_enclosure_v1 import gram_enclosure,positive_ldl,normalization

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();args.out.mkdir(exist_ok=False);start=time.perf_counter()
    profile=json.loads(args.profile.read_bytes())
    for name,pin in profile['pins'].items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,'Frozen operator source mismatch:'+name)
    scene=json.loads((ROOT/profile['scene']).read_bytes());wire=json.loads((ROOT/profile['graph_result']).read_bytes())
    audit=audit_graph_neighborhood(scene,wire);need(audit['primary_metric']==1,'Independent geometry/neighborhood audit required')
    graph=decode(wire)['graph'];ids=[r['source_id'] for r in graph['roots']];ports=graph['ports'];need(len(ids)==5 and len(ports)==8,'Fixed five input/eight output channels required')
    columns=[enclose_fields(graph,{s:[int(s==basis),0] for s in ids}) for basis in ids]
    matrix=[[col[port] for col in columns] for port in ports];gram=gram_enclosure(matrix)
    midpoint=np.array([[complex(float((r.lo+r.hi)/2),float((im.lo+im.hi)/2)) for r,im in row] for row in gram],dtype=np.complex128)
    eigenvalues,eigenvectors=np.linalg.eigh(midpoint);v=eigenvectors[:,-1];vector=[[float(z.real),float(z.imag)] for z in v]
    report={'schema':'optic_neuro_blender.operator_gram_certificate.v1','status':'VALID_INDEPENDENT_OPERATOR_ANALYSIS','primary_metric':1,
            'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'source_ids':ids,'ports':ports,'independent_geometry_audit':audit,
            'transfer_matrix_enclosure':[[{'real':r.wire(),'imag':im.wire()} for r,im in row] for row in matrix],
            'gram_enclosure':[[{'real':r.wire(),'imag':im.wire()} for r,im in row] for row in gram],
            'rank_certificate':positive_ldl(gram),'normalization_certificate':normalization(gram,vector,F(*profile['contractivity_tolerance'])),
            'diagnostic_midpoint_eigenvalues_not_proof':eigenvalues.tolist(),'seconds':time.perf_counter()-start,
            'scope':{'all_complex_represented_input_vectors':True,'full_five_column_rank_requires_positive_interval_LDL':True,
                     'euclidean_channel_norm_equals_physical_flux_verified':False,'noncontractive_witness_does_not_demonstrate_physical_gain':True,
                     'physical_passivity':'UNKNOWN_NOT_ZERO','native_pipeline_error_bounded':False,'novelty':'NOT_ESTABLISHED'}}
    (args.out/'certificate.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':report['status'],'rank':report['rank_certificate'],'normalization':report['normalization_certificate'],'seconds':report['seconds']}),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
