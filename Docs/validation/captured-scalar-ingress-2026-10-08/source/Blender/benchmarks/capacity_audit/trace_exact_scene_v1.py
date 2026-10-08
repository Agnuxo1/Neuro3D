"""Public JSON entry point for the versioned complete CPU multipath engine."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from robust_multipath_v1 import trace_scene


def encode(value):
    if isinstance(value, Fraction): return {'numerator': value.numerator, 'denominator': value.denominator}
    if isinstance(value, complex): return {'real': value.real, 'imag': value.imag}
    if isinstance(value, dict): return {key: encode(v) for key, v in value.items()}
    if isinstance(value, (list, tuple)): return [encode(v) for v in value]
    return value


def decode_object(pairs):
    row = {}
    for key, value in pairs:
        if key in row: raise ValueError('duplicate JSON key')
        row[key] = value
    if set(row) == {'numerator', 'denominator'}:
        if type(row['numerator']) is not int or type(row['denominator']) is not int or row['denominator'] <= 0:
            raise ValueError('invalid rational wire')
        return Fraction(row['numerator'], row['denominator'])
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--max-rays', type=int, default=4096); parser.add_argument('--max-depth', type=int, default=64)
    args = parser.parse_args()
    raw = args.scene.read_bytes()
    if len(raw) > 8*1024*1024: raise ValueError('scene size bound')
    snapshot = json.loads(raw, object_pairs_hook=decode_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
    result = trace_scene(snapshot, max_rays=args.max_rays, max_depth=args.max_depth)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(encode(result), indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': result['status'], 'backend': result['backend'], 'paths': len(result['paths']),
                      'unresolved': len(result['unresolved']), 'field_certified': result['field_certified']}))
    return 0 if result['status'] == 'COMPLETE' else 2


if __name__ == '__main__': raise SystemExit(main())
