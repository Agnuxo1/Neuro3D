"""Opt-in CPU linkage: evaluated snapshot -> generated histories -> fields.

No bpy/GPU launch or writer. Existing export CLI and frozen validators stay
unchanged. Callers must distinguish CPU doubles from actual bpy readback.
"""
from exp005_history_mzi_export import validate_export
from history_trace_cpu_v1 import trace_scene


def validate_generated_export(expected,before,after,phase,shift):
    if not before.get('evaluated_optics_checked') or not after.get('evaluated_optics_checked'):
        raise ValueError('evaluated readback required before tracing')
    if before!=after:raise ValueError('save/reopen readback mismatch before tracing')
    # Only actual supplied readback goes into traversal, not expected fixture
    # geometry or its precomputed paths. Frozen export equality gate follows.
    trace=trace_scene(after)
    checked=validate_export(expected,before,after,trace['records'],phase,shift)
    return {'generated_history':trace,'export_checks':checked,
            'scope':'CPU reference generated from supplied evaluated snapshot; no GPU inference',
            'bpy_execution_certified':False,'native_backend_received_paths':False}
