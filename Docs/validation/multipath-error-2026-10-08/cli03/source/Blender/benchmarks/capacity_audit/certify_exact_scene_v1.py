"""Public fresh-output JSON entry point for complete scalar-model certificates."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from multipath_error_certificate_v1 import certify_scene
from trace_exact_scene_v1 import decode_object


def read(path):
    raw=path.read_bytes()
    if len(raw)>8*1024*1024: raise ValueError('input size bound')
    return json.loads(raw,object_pairs_hook=decode_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',type=Path,required=True); parser.add_argument('--radii',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    snapshot=read(args.scene)
    result=certify_scene(snapshot) if args.radii is None else certify_scene(snapshot,radii=read(args.radii))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'reason':result.get('reason'),'path_count':result.get('path_count'),
                      'physical_input_bounds':result['physical_input_bounds']}))
    return 0 if result['status'].startswith('CERTIFIED_') else 2


if __name__=='__main__': raise SystemExit(main())
