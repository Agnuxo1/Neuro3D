"""Independent secondary interval validation of already recorded CUDA outputs."""
import argparse,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode,need
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.state_graph_enclosure_v1 import observed_certificate
from Blender.blender_lab.coherent_state_graph_v1 import propagate_graph
from Tools.trace_indexed_scene_v1 import wire


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',type=Path,required=True);parser.add_argument('--result',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();p=json.loads(args.profile.read_text());r=json.loads(args.result.read_text())
    need(r['status']=='PASS' and r['profile_sha256']==hashlib.sha256(args.profile.read_bytes()).hexdigest(),'recorded frozen CUDA result identity required')
    scene_wire=json.loads((ROOT/p['scene']).read_text());scene=decode(scene_wire);graph=decode(json.loads((ROOT/p['graph']).read_text()))
    estimates=propagate_graph(graph,{s['id']:s['field_reim'] for s in scene['sources']})
    audit=audit_graph_neighborhood(scene_wire,wire({'graph':graph,**estimates}));need(audit['primary_metric']==1,'independent represented geometry audit required')
    need(r['source_ids']==[root['source_id'] for root in graph['roots']] and r['ports']==graph['ports'],'source/detector order mismatch')
    start=time.perf_counter();certificates=[]
    for i,(real,imag) in enumerate(p['coherent_probes']):
        fields={sid:[real[j],imag[j]] for j,sid in enumerate(r['source_ids'])}
        observed={port:{'real':r['actual_cuda_fields_reim'][0][i][j],'imag':r['actual_cuda_fields_reim'][1][i][j]} for j,port in enumerate(r['ports'])}
        powers={port:r['actual_cuda_powers'][i][j] for j,port in enumerate(r['ports'])}
        certificate=observed_certificate(graph,fields,observed,powers,detector_ports=['det.R0','det.R1','det.R2'])
        certificates.append(dict(certificate,probe_index=i))
    sources=['Tools/certify_cuda_coherent_probes_v1.py','Blender/blender_lab/state_graph_enclosure_v1.py','Blender/benchmarks/capacity_audit/rational_interval_v1.py','Tools/audit_graph_neighborhood_v1.py','Tools/audit_coherent_state_graph_v1.py','Tools/audit_captured_pilot_result_v1.py']
    report={'schema':'optic_neuro_blender.observed_cuda_probe_interval_certificate.v1','status':'CERTIFIED_OBSERVED_REPRESENTED_CUDA_OUTPUTS' if all(c['status']=='CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS' for c in certificates) else 'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET',
        'result_sha256':hashlib.sha256(args.result.read_bytes()).hexdigest(),'profile_sha256':r['profile_sha256'],'probe_count':len(certificates),
        'max_field_L1_error_upward':max(v['observed_field_error_L1_upward_float'] for c in certificates for v in c['ports'].values()),
        'max_power_error_upward':max(v['observed_power_error_upward_float'] for c in certificates for v in c['ports'].values()),
        'certified_argmax_count':sum(c['decision']['status']=='CERTIFIED_REPRESENTED_ARGMAX' for c in certificates),
        'unknown_decision_count':sum(c['decision']['status']=='UNKNOWN_OVERLAPPING_INTERVALS' for c in certificates),
        'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources},'certificates':certificates,
        'analysis_seconds_excluding_geometry_audit':time.perf_counter()-start,'independent_geometry_audit':audit,
        'scope':'Secondary deterministic proof of already recorded NVIDIA fields/powers versus exact represented scalar geometry and frozen coherent inputs; defaultunchanged1e-11budgets; not a generalGPUerrorbound, gradientcertificate, physicalfidelity or a newconfirmatorytrial'}
    with args.out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('status','probe_count','max_field_L1_error_upward','max_power_error_upward','certified_argmax_count','unknown_decision_count','analysis_seconds_excluding_geometry_audit')}),flush=True)


if __name__=='__main__':main()
