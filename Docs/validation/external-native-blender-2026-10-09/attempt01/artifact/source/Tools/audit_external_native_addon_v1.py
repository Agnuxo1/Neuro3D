"""Unchanged nine native controls plus measured external Blender runtime."""
import json
from pathlib import Path
import platform
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_installed_own_blender_addon_v3 import main as native_main


if __name__ == '__main__':
    native_main()
    args = sys.argv[sys.argv.index('--') + 1:]
    path = Path(args[1]) / 'result.json'
    result = json.loads(path.read_bytes())
    result['external_runtime'] = {'python': sys.version, 'numpy': np.__version__,
                                  'platform': platform.platform(), 'machine': platform.machine(),
                                  'blender_version': bpy.app.version_string,
                                  'blender_version_numeric': list(bpy.app.version),
                                  'build_hash': bpy.app.build_hash.decode(),
                                  'binary_path': bpy.app.binary_path}
    result['independent_human_replication'] = False
    result['scope'] = 'Actual GitHub-hosted Linux Blender nine-control standalone addon repetition with unchanged scientific worker. External environment, not independent specialist interpretation, GPU execution or physical fidelity.'
    path.write_bytes((json.dumps(result, indent=2, allow_nan=False) + '\n').encode())
