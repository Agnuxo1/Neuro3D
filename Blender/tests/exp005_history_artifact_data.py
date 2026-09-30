"""Read-only data audit: recompute CPU histories/fields, paths and hashes.

This is NOT provenance authentication, .blend parsing or job admission.
Synthetic snapshots and arbitrary bytes can pass data consistency checks.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
from exp005_history_mzi_export import CASES, fixture
from exp005_history_generated_export import validate_generated_export

SCOPE = 'candidate bpy evaluated export/save/reopen plus CPU Python tracing/fields; NOT GPU inference'
REPORT_KEYS = {'scope', 'cases', 'blender_version', 'job_deadline_utc'}
CASE_KEYS = {'case', 'before', 'after', 'result', 'blend_path', 'blend_sha256'}


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))


def validate_data(report, folder, deadline, *, read_blob=lambda p:p.read_bytes()):
    """Compare reported results with NEW traversal of supplied after snapshots.

    read_blob is an explicit test seam. Real file hashes alone cannot prove
    Blender generated those files; outer executable/job/log evidence is needed.
    """
    canonical(report)  # Nonfinite values are never accepted or cached.
    if not isinstance(deadline, datetime) or deadline.tzinfo is None or deadline.utcoffset().total_seconds()!=0:
        raise ValueError('explicit common UTC deadline required')
    if not isinstance(report, dict) or set(report) != REPORT_KEYS or report['scope'] != SCOPE:
        raise ValueError('frozen runtime report schema/scope required')
    if report['job_deadline_utc'] != deadline.isoformat():
        raise ValueError('report and job deadline mismatch')
    if not isinstance(report['blender_version'], str) or not report['blender_version']:
        raise ValueError('reported version missing; version text is not authentication')
    folder=Path(folder)
    if not folder.is_absolute():raise ValueError('absolute evidence folder required')
    folder=folder.resolve()
    cases=report['cases']
    if not isinstance(cases,list) or len(cases)!=len(CASES):
        raise ValueError('exact three-case coverage required')
    checked=[]
    for supplied,(label,phase,shift) in zip(cases,CASES):
        if not isinstance(supplied,dict) or set(supplied)!=CASE_KEYS or supplied['case']!=label:
            raise ValueError('case schema/order/coverage mismatch')
        if not all(isinstance(supplied[k],dict) for k in ('before','after','result')):
            raise ValueError('snapshot/result dictionaries required')
        if list(supplied['before'].get('objects',{})) != list(supplied['after'].get('objects',{})):
            raise ValueError('save/reopen global object order mismatch')
        blend=folder/(label+'.blend')
        declared=Path(supplied['blend_path'])
        if not declared.is_absolute() or declared.resolve()!=blend:
            raise ValueError('blend must be exact direct child of evidence folder')
        digest=hashlib.sha256(read_blob(blend)).hexdigest()
        if supplied['blend_sha256']!=digest:raise ValueError('blend hash mismatch')
        expected,_=fixture(phase,shift)  # Do not use fixture histories.
        recomputed=validate_generated_export(expected,supplied['before'],supplied['after'],phase,shift)
        if canonical(recomputed)!=canonical(supplied['result']):
            raise ValueError('reported history/fields/metadata differ from fresh scene traversal')
        checked.append({'case':label,'blend_sha256':digest,
                        'records':len(recomputed['generated_history']['records']),
                        'analytic_field_error':recomputed['export_checks']['analytic_field_error']})
    # Bind the result to the bytes observed throughout the audit, not a changed file.
    for item in checked:
        if hashlib.sha256(read_blob(folder/(item['case']+'.blend'))).hexdigest()!=item['blend_sha256']:
            raise ValueError('blend changed during audit')
    return {'scope':'data consistency plus fresh CPU scene traversal; NOT Bpy/job/GPU provenance',
            'artifact_data_consistent':True,'cases':checked,'job_deadline_utc':deadline.isoformat(),
            'report_data_sha256':hashlib.sha256(json.dumps(report,allow_nan=False,separators=(',',':')).encode('utf-8')).hexdigest(),
            'bpy_execution_certified':False,'operational_gate_passed':False,
            'blend_format_checked':False,'no_jev_aval':True}


def audit_folder(folder, deadline):
    """Read actual bytes only. Never launch, modify or repair an artifact."""
    folder=Path(folder);path=folder/'export.json';raw=path.read_bytes()
    report=json.loads(raw)
    result=validate_data(report,folder,deadline)
    if path.read_bytes()!=raw:raise ValueError('export report changed during audit')
    result['export_file_sha256']=hashlib.sha256(raw).hexdigest()
    return result
