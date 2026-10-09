"""Bounded separate path-growth diagnostic, not a repeat of the frozen pilot."""
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
from Blender.benchmarks.capacity_audit.robust_multipath_v1 import trace_scene
from Blender.benchmarks.capacity_audit.exact_object_index_v1 import ExactObjectIndex


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--max-rays',required=True,type=int)
    parser.add_argument('--max-depth',required=True,type=int)
    args=parser.parse_args()
    start=time.monotonic()
    indices=[]
    class ObservedIndex(ExactObjectIndex):
        def __call__(self,origin,direction,triangles,previous=None):
            scalars=(*origin,*direction)
            row={'query':self.stats['queries']+1,'elapsed_seconds':time.monotonic()-start,
                 'origin_direction_max_numerator_bits':max(v.numerator.bit_length() for v in scalars),
                 'origin_direction_max_denominator_bits':max(v.denominator.bit_length() for v in scalars)}
            print(json.dumps(dict(row,stage='before_selection')),flush=True)
            hit=super().__call__(origin,direction,triangles,previous)
            print(json.dumps(dict(row,stage='after_selection',status=hit['status'],
                                  selected_object=hit.get('selected',{}).get('object_id'),
                                  candidates=len(hit['candidates']),statistics=self.stats)),flush=True)
            return hit
    def factory(triangles):
        index=ObservedIndex(triangles)
        indices.append(index)
        return index
    scene,_=read_json(args.scene,8*2**20)
    result=trace_scene(decode(scene),max_rays=args.max_rays,max_depth=args.max_depth,_selection_factory=factory)
    result.update(selection_backend='EXACT_OBJECT_AABB_CPU_DIAGNOSTIC',selection_statistics=indices[0].stats,
                  diagnostic_only=True)
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(wire(result),indent=2,allow_nan=False)+'\n')
    return 0 if result['status']=='COMPLETE' else 2


if __name__=='__main__':
    raise SystemExit(main())
