"""Separate exact-index worker, never the original frozen pilot worker."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from optic_neuro_blender._vendor.Tools.bind_network_capture_v1 import read_json
from optic_neuro_blender._vendor.Tools.audit_captured_pilot_result_v1 import decode
from optic_neuro_blender._vendor.Blender.benchmarks.capacity_audit.exact_object_index_v1 import trace_scene_indexed
from optic_neuro_blender._vendor.Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire


def wire(value):
    if isinstance(value,complex):
        return {'real':value.real,'imag':value.imag}
    if isinstance(value,dict):
        return {k:wire(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [wire(v) for v in value]
    return rational_wire(value)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--max-rays',type=int,required=True)
    parser.add_argument('--max-depth',type=int,required=True)
    args=parser.parse_args()
    scene,_=read_json(args.scene,8*2**20)
    result=trace_scene_indexed(decode(scene),max_rays=args.max_rays,max_depth=args.max_depth)
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(wire(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'paths':len(result['paths']),
                      'rays':result['rays'],'unresolved':len(result['unresolved']),
                      'selection_statistics':result['selection_statistics']}))
    return 0 if result['status']=='COMPLETE' else 2


if __name__=='__main__':
    raise SystemExit(main())
