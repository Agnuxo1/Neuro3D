"""Versioned Blender --python entrypoint with explicit sibling-module path.

Preserves V2 and its failed import evidence. Numerical V1, private preferences,
shader and gates unchanged; own guard enforces <=110s for this child.
"""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from exp005_resident_v2 import main as run_v2


def main():
    run_v2()
    values = sys.argv[sys.argv.index('--')+1:]
    report = Path(values[values.index('--report')+1])
    path = report.with_name(report.stem + '_entrypoint.json')
    if path.exists():
        raise ValueError('new entrypoint envelope required')
    lifecycle = report.with_name(report.stem + '_lifecycle.json')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    path.write_text(json.dumps({'entrypoint_sha256': sha(Path(__file__)),
        'lifecycle_sha256': sha(lifecycle), 'report_sha256': sha(report),
        'module_path': str(Path(__file__).parent),
        'scope': 'explicit Blender script import path; V2 settings and V1 numerical code unchanged'},
        indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print('RESIDENT_V3_ENTRYPOINT_COMPLETED', flush=True)


if __name__ == '__main__': main()
