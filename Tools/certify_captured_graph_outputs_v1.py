"""Secondary deterministic validation of already frozen observed outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.audit_captured_pilot_result_v1 import decode
from Tools.audit_coherent_state_graph_v1 import audit_graph_result
from Blender.blender_lab.state_graph_enclosure_v1 import observed_certificate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',type=Path,required=True)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    scene,scene_pin=read_json(args.scene,8*2**20)
    result,result_pin=read_json(args.result,64*2**20)
    audit=audit_graph_result(scene,result)
    if audit['primary_metric']!=1:
        raise ValueError('completed independent graph audit required')
    scene,result=decode(scene),decode(result)
    detectors=[d['object'] for d in scene['blender_lab_ingress']['network_bindings']['detectors']]
    certificate=observed_certificate(result['graph'],{s['id']:s['field_reim'] for s in scene['sources']},
        result['fields'],result['powers'],detector_ports=detectors)
    certificate.update(scene_raw_sha256=scene_pin,result_raw_sha256=result_pin,geometric_audit=audit,
                       analysis_scope='Secondary deterministic validation of previously collected frozen graph result; not a newly registered confirmatory H1 trial')
    sources=[Path(__file__),ROOT/'Blender/blender_lab/state_graph_enclosure_v1.py',
             ROOT/'Blender/benchmarks/capacity_audit/rational_interval_v1.py',ROOT/'Tools/audit_coherent_state_graph_v1.py']
    certificate['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(certificate,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':certificate['status'],'max_field_error':max(p['observed_field_error_L1_upward_float'] for p in certificate['ports'].values()),
                      'max_power_error':max(p['observed_power_error_upward_float'] for p in certificate['ports'].values()),'decision':certificate['decision']}))


if __name__=='__main__':
    main()
