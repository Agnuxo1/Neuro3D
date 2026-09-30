"""RES-001 V2 lifecycle wrapper; V1 numerical code/limits remain immutable.

Only private --factory-startup preferences change. Never save user preferences.
Unsaved optical edits are intentional controls; no quit confirmation dialog.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import exp005_resident_runtime as numerical


def configure_private_exit(bpy):
    prefs=bpy.context.preferences
    # Disable saving BEFORE any other preference mutation in this owned child.
    prefs.use_preferences_save=False
    prefs.view.use_save_prompt=False
    prefs.filepaths.use_auto_save_temporary_files=False
    if prefs.use_preferences_save or prefs.view.use_save_prompt or prefs.filepaths.use_auto_save_temporary_files:
        raise ValueError('private non-persistent no-dialog shutdown required')
    return {'save_user_preferences':False,'save_prompt':False,'temporary_autosave':False,
            'scope':'owned factory-startup child only; numerical kernels and watchdog unchanged'}


def main():
    import bpy
    settings=configure_private_exit(bpy);start=time.perf_counter()
    numerical.main()
    values=sys.argv[sys.argv.index('--')+1:]
    report=Path(values[values.index('--report')+1])
    path=report.with_name(report.stem+'_lifecycle.json')
    if path.exists():raise ValueError('new lifecycle envelope required')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    envelope={'settings':settings,'wrapper_sha256':sha(Path(__file__)),
        'numerical_runner_sha256':sha(Path(numerical.__file__)),
        'report_sha256':sha(report),'main_body_ms':(time.perf_counter()-start)*1000,
        'warning':'numerical body completed; clean process exit requires separate guard rc0'}
    path.write_text(json.dumps(envelope,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('RESIDENT_V2_PRIVATE_EXIT_CONFIGURED',flush=True)


if __name__=='__main__':main()
