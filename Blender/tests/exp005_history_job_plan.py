"""CPU-only job preparation; does NOT reserve, launch or certify a process.

Frozen night guard is not an executor for this pilot. Its pure policy function
is reusable with an explicit NEW deadline; the actual job needs a new wrapper.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Blender/benchmarks/capacity_audit'))
from guarded_job import violations

GIB = 2**30
BASELINE = Path('D:/PROJECTS/.cognition/neuro3d/exp005_history_runtime_cpu_20260930_1414.json')
BASELINE_SHA = 'b49a22bb0afae6907117eb720f96a29161281837f642193e55455f572a30df8c'
RUNNER = ROOT / 'Blender/tests/exp005_history_generated_runtime.py'
POLICY = ROOT / 'Blender/benchmarks/capacity_audit/guarded_job.py'
POLICY_SHA = '958163c3bba7f16d619c9788893771eaf7fc6a17b1e295eae8cf84b15bfcd818'
HOST_BUDGET = 2*GIB + 3*1024  # fixed startup/temporary margin + three MZI cells
DEVICE_BUDGET = 2*GIB


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs():
    if sha(BASELINE) != BASELINE_SHA:
        raise ValueError('changed baseline report')
    pins = json.loads(BASELINE.read_text(encoding='utf-8'))['code_sha256']
    if len(pins) != 17 or str(RUNNER) not in pins:
        raise ValueError('incomplete frozen dependency pins')
    for name, digest in pins.items():
        path = Path(name).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != digest:
            raise ValueError('changed or foreign dependency: '+name)
    if sha(POLICY) != POLICY_SHA:
        raise ValueError('changed frozen policy')
    return dict(pins, **{str(POLICY): POLICY_SHA})


def prepare(blender, evidence, allowed_parent, deadline, sample, *, now=None):
    """Return an unadmitted manifest, using caller-supplied fresh telemetry.

    Caller must refresh telemetry/revalidate pins inside a future exclusive job.
    No queue token/telemetry authenticity/monotonic lifecycle is inferred here.
    """
    now = now or datetime.now(timezone.utc)
    for value in (now, deadline):
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset().total_seconds() != 0:
            raise ValueError('explicit UTC clocks required')
    remaining = (deadline-now).total_seconds()
    if not 115 <= remaining <= 120:
        raise ValueError('new deadline must leave 110s child plus >=5s close margin within 120s')
    # Explicit deadline, not guarded_job.DEADLINE (historical night, preserved).
    if set(sample) != {'ram_available_bytes', 'device_used_bytes', 'temperature_c'}:
        raise ValueError('missing or unexpected telemetry fields')
    reasons = violations(sample, now=now, deadline=deadline, elapsed=0, timeout=110,
                         host_estimate=HOST_BUDGET, device_estimate=DEVICE_BUDGET)
    if reasons:
        raise ValueError('resource preflight rejected: '+','.join(reasons))
    for value in sample.values():
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('nonfinite or nonnumeric telemetry')
    blender, evidence, allowed_parent = map(Path, (blender, evidence, allowed_parent))
    if not all(p.is_absolute() for p in (blender, evidence, allowed_parent)):
        raise ValueError('absolute executable and evidence paths required')
    blender, evidence, allowed_parent = (p.resolve() for p in (blender, evidence, allowed_parent))
    if blender.name.lower() != 'blender.exe' or not blender.is_file():
        raise ValueError('existing explicit Blender executable required')
    if not allowed_parent.is_dir() or evidence.parent != allowed_parent or evidence.exists():
        raise ValueError('fresh direct child evidence folder required; no overwrite')
    pins = verify_inputs()
    iso = deadline.isoformat()
    command = [str(blender), '--background', '--factory-startup', '--threads', '1',
               '--python-exit-code', '1', '--python', str(RUNNER), '--',
               '--evidence', str(evidence), '--job-deadline-utc', iso,
               '--authorized-private-child']
    return {'schema': 'exp005.generated-history-job-plan.v1',
            'scope': 'preparation only; candidate Blender persistence and CPU tracing/fields, NOT GPU inference',
            'admitted_for_launch': False, 'job_deadline_utc': iso,
            'child_timeout_s': 110, 'close_margin_s': remaining-110,
            'host_budget_bytes': HOST_BUDGET, 'device_budget_bytes': DEVICE_BUDGET,
            'policy': {'ram_floor_after_budget_bytes': 4*GIB, 'device_total_cap_bytes': 18*GIB,
                       'temperature_cap_c': 80, 'geometry_bytes_per_cell': 1024, 'cells': 3},
            'sample_supplied_not_authenticated': dict(sample), 'command': command,
            'executable_sha256': sha(blender), 'baseline_sha256': BASELINE_SHA,
            'code_sha256': pins, 'evidence': str(evidence),
            'pending': ['exclusive gpuq job and fresh process/resource check',
                        'new operational wrapper, monotonic watchdog and late-exit rejection',
                        'joint rc/envelope/owned-child closure plus actual readback and file hashes'],
            'no_jev_aval': True}
