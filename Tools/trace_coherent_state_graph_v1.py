"""Own captured-geometry DAG worker; fields from roots/edges, no circuit input."""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.audit_captured_pilot_result_v1 import decode
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--max-states',type=int,required=True)
    args=parser.parse_args()
    scene,raw_sha=read_json(args.scene,8*2**20)
    scene=decode(scene)
    started=time.monotonic()
    graph=build_graph(scene,max_states=args.max_states)
    graph_seconds=time.monotonic()-started
    print(json.dumps({'graph_status':graph['status'],'states':len(graph['nodes']),'graph_seconds':graph_seconds}),flush=True)
    result={'graph':graph,'fields':None,'powers':None,'raw_scene_sha256':raw_sha,
            'graph_seconds':graph_seconds,'field_certified':False,'physical_optics_certified':False}
    if graph['status']=='COMPLETE':
        result.update(propagate_graph(graph,{s['id']:s['field_reim'] for s in scene['sources']}))
    result['worker_compute_seconds']=time.monotonic()-started
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(wire(result),indent=2,allow_nan=False)+'\n')
    return 0 if graph['status']=='COMPLETE' else 2


if __name__=='__main__':
    raise SystemExit(main())
