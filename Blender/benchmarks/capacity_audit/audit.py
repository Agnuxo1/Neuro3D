"""Read-only capacity evidence checker. No GPU imports or benchmark execution.

Process exit/status is separate from numerical accuracy, hardware evidence and
compute placement. Missing evidence is NOT success. Frozen v1 error limit applies
to future intensity smoke cases; historical v0 rows are provisional diagnostics.
"""
import argparse
import hashlib
import json
import math
from numbers import Real
from pathlib import Path

REL_ERROR_LIMIT = .001


def finite(value, *, positive=False):
    return (not isinstance(value,bool) and isinstance(value,Real)
            and math.isfinite(value) and (value>0 if positive else value>=0))


def audit_record(record):
    reasons = []
    execution_ok = record.get('status')=='ok'
    if not execution_ok: reasons.append('execution_not_ok')
    numerical_ok = finite(record.get('rel_error')) and record['rel_error']<=REL_ERROR_LIMIT
    if not numerical_ok: reasons.append('accuracy_failed_or_missing')
    dimensions_ok = all(isinstance(record.get(k),int) and not isinstance(record[k],bool)
                        and record[k]>0 for k in ('N','M'))
    if not dimensions_ok: reasons.append('dimensions_invalid')
    elif record.get('params')!=record['N']*record['M']: reasons.append('parameter_count_invalid')
    timings_ok = finite(record.get('render_s'),positive=True) and finite(record.get('total_s'),positive=True)
    if not timings_ok: reasons.append('timings_missing_or_invalid')
    elif record['total_s']<record['render_s']: reasons.append('total_time_less_than_render')
    peak = record.get('vram_peak_mb')  # legacy producer records nvidia-smi MiB, not bytes
    if not finite(peak) or peak<=0: reasons.append('device_memory_peak_missing')
    elif peak>18*1024: reasons.append('device_vram_cap_exceeded')
    if record.get('mode')=='cells':
        category = 'incoherent_render_partial_cpu_row_sum'
        full_gpu = False
    elif record.get('mode')=='integrate':
        category = 'incoherent_render_integrator_unverified'
        full_gpu = record.get('gpu_reduction_verified') is True
    else:
        category = 'unknown'; full_gpu = False; reasons.append('unknown_compute_placement')
    backend_ok = (record.get('backend')=='OPTIX' and record.get('device')=='NVIDIA GeForce RTX 3090'
                  and isinstance(record.get('blender_version'),str)
                  and bool(record.get('backend_log_sha256')))
    if not backend_ok: reasons.append('rt_backend_evidence_missing')
    evidence_ok = (bool(record.get('input_artifact_sha256')) and bool(record.get('readback_artifact_sha256'))
                   and bool(record.get('code_sha256')))
    if not evidence_ok: reasons.append('independent_readback_evidence_missing')
    if not full_gpu: reasons.append('full_gpu_reduction_not_demonstrated')
    safe = (finite(record.get('ram_free_min_gib')) and record['ram_free_min_gib']>=4
            and finite(record.get('gpu_temp_max_c')) and record['gpu_temp_max_c']<=80)
    if not safe: reasons.append('resource_guard_evidence_missing_or_failed')
    return {'N':record.get('N'),'M':record.get('M'),'mode':record.get('mode'),
            'geometry':record.get('geometry'),'spp':record.get('spp'),
            'execution_ok':execution_ok,'producer_accuracy_within_v1_limit':numerical_ok,
            'category':category,'gpu_reduction_claimed':full_gpu,
            'full_gpu_verified':False,'rt_backend_metadata_complete':backend_ok,
            'rt_backend_verified':False,
            'candidate_incoherent_case_for_review':not reasons,
            'verified_incoherent_capacity':False,  # metadata is NOT independent proof
            'eligible_coherent_rt_capacity':False,  # this producer has NO wave phase
            'relative_error_limit_v1':REL_ERROR_LIMIT,'reasons':reasons}


def audit_linear_arrays(x,weights,observed):
    """Independent float64 reference; CPU only. Weights shape [input,output]."""
    import numpy as np
    x = np.asarray(x,dtype=np.float64); weights = np.asarray(weights,dtype=np.float64)
    observed = np.asarray(observed,dtype=np.float64)
    if x.ndim!=1 or weights.ndim!=2 or observed.ndim!=1:
        raise ValueError('vector/matrix/vector required')
    if weights.shape!=(x.size,observed.size) or not x.size or not observed.size:
        raise ValueError('input/output dimensions mismatch')
    if not all(np.isfinite(a).all() for a in (x,weights,observed)):
        raise ValueError('nonfinite artifact')
    reference = x@weights
    error = observed-reference
    norm = float(np.linalg.norm(reference)); max_abs = float(np.max(np.abs(error)))
    relative = float(np.linalg.norm(error)/norm) if norm else None
    # A zero reference cannot be accepted by a meaningless relative denominator.
    return {'relative_error':relative,'max_abs_error':max_abs,
            'reference_norm':norm,'zero_reference_exact':bool(norm==0 and max_abs==0),
            'reference':reference.tolist()}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True); args = parser.parse_args()
    source = Path(args.input).resolve(); data = source.read_bytes()
    records = [json.loads(line) for line in data.decode('utf-8').splitlines() if line.strip()]
    result = {'input_sha256':hashlib.sha256(data).hexdigest(),
              'scope':'provisional producer-metric audit; independent raw readback still required',
              'records':[audit_record(r) for r in records]}
    Path(args.output).resolve().write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'records':len(records),'reported_accuracy_failures':sum(
        not r['producer_accuracy_within_v1_limit'] for r in result['records']),
        'eligible_coherent_rt':0}))


if __name__=='__main__': main()
