"""Private scalar capture adapter, NOT a launcher or GPU admission authority.

Frozen shader/decoder unchanged. Retain raw uint readback BEFORE any numeric
gate, including failed gates. Real exclusive admission, telemetry and hard
timeout must be supplied by an outer supervisor; no CLI or CPU fallback.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

from phase_native_probe_v1 import SHADER, decode, flatten, pack_samples, scalar, words

ROOT = Path(__file__).resolve().parents[3]
PREP = ROOT/'coordinacion/respuestas/PHASE-NATIVE-PREP-001-CODEX.json'
PREP_SHA = '2119d9e5e86cd4930184d8eac806c6aa473df9b1cd682c113f3667f38e498b43'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest():
    if sha(PREP) != PREP_SHA:
        raise ValueError('preregistered preparation changed')
    preparation = json.loads(PREP.read_text(encoding='utf-8'))
    pins = {str(Path(p)): value for p, value in preparation['code_sha256'].items()}
    if any(sha(p) != value for p, value in pins.items()):
        raise ValueError('frozen input changed')
    pins[str(PREP)] = PREP_SHA
    pins[str(Path(__file__).resolve())] = sha(__file__)
    cases = [{'name': 'valid_'+str(i),
              'input_uint32': list((*words(float(pair[0])), *words(float(pair[1])))),
              'expected_status': 0}
             for i, pair in enumerate(preparation['valid_scalar_controls'])]
    cases.extend(preparation['pilot_contract']['negative_samples'])
    if len(cases) != 12:
        raise ValueError('exact preregistered twelve cases required')
    return {'version': 'phase-native-capture-v1', 'code_sha256': pins,
            'cases': cases, 'policy': preparation['pilot_contract'],
            'operational_admission_granted': False, 'native_promotion_allowed': False}


def validate_manifest(value):
    # Canonical JSON distinguishes bool/int and admits no NaN or extra fields.
    if json.dumps(value, sort_keys=True, allow_nan=False) != json.dumps(
            manifest(), sort_keys=True, allow_nan=False):
        raise ValueError('manifest differs from frozen preregistration or current pins')
    return [(scalar(c['input_uint32'][:2]), scalar(c['input_uint32'][2:]))
            for c in value['cases']], [c['expected_status'] for c in value['cases']]


def fresh_deadline(deadline, *, now=lambda: datetime.now(timezone.utc),
                   monotonic=time.monotonic):
    clock = now()
    if any(not isinstance(v, datetime) or v.tzinfo is None or
           v.utcoffset().total_seconds() != 0 for v in (deadline, clock)):
        raise ValueError('explicit UTC deadline and clock required')
    remaining = (deadline-clock).total_seconds()
    if not 0 < remaining <= 90:
        raise ValueError('new scalar child deadline must be within ninety seconds')
    start = monotonic()

    def check():
        elapsed = monotonic()-start
        if not math.isfinite(elapsed) or not 0 <= elapsed < remaining or now() >= deadline:
            raise ValueError('scalar child deadline exhausted')
    return check


def reject_admission():
    raise ValueError('outer exclusive guarded job admission required')


def raw_dispatch(gpu, samples, statuses, check, retain):
    """New capture variant; same frozen shader and exact ABI, no numerical fallback."""
    check()
    data = pack_samples(samples)
    info = gpu.types.GPUShaderCreateInfo()
    info.sampler(0, 'UINT_2D', 'samples_in')
    info.image(0, 'RGBA32UI', 'UINT_2D', 'trace_out', qualifiers={'WRITE'})
    info.push_constant('INT', 'sample_count'); info.local_group_size(8, 1, 1)
    info.compute_source(SHADER.read_text(encoding='utf-8'))
    shader = gpu.shader.create_from_info(info); check()
    source = gpu.types.GPUTexture((len(samples), 1), format='RGBA32UI',
                                 data=gpu.types.Buffer('UINT', len(data), data))
    target = gpu.types.GPUTexture((7, len(samples)), format='RGBA32UI')
    shader.uniform_sampler('samples_in', source); shader.image('trace_out', target)
    shader.uniform_int('sample_count', len(samples)); check()
    gpu.compute.dispatch(shader, math.ceil(len(samples)/8), 1, 1); check()
    output = flatten(target.read().to_list())
    retain(output)  # Persist before post-readback deadline or numeric validation.
    check()
    return decode(samples, output, expected_statuses=statuses)


def run_private_capture(gpu, plan, evidence, check, *, admit=reject_admission):
    """Callable inside an already supervised private child. No process launch.

    Fake adapters exercise this in CPU tests, NOT authentic native evidence.
    Persistence/compile/decode/deadline failures propagate to a nonzero caller.
    """
    if not callable(check) or not callable(admit):
        raise ValueError('explicit deadline/admission adapters required')
    check(); samples, statuses = validate_manifest(plan)
    folder = Path(evidence)
    folder.mkdir(exist_ok=False)  # Never reuse/overwrite a previous result.
    with (folder/'manifest.json').open('x', encoding='utf-8') as out:
        out.write(json.dumps(plan, indent=2, allow_nan=False)+'\n')
    result = {'status': 'failed', 'readback_retained': False,
              'runtime_execution_authenticated': False, 'native_promotion_allowed': False,
              'operational_gate_passed': False, 'geometry_or_scene_inference': False,
              'scope': 'private scalar capture; outer guard and runtime authentication separate',
              'no_jev_aval': True}
    # Reserve mandatory result BEFORE touching GPU; exactly one finalization.
    with (folder/'result.json').open('x', encoding='utf-8') as report:
        try:
            check(); admit(); validate_manifest(plan); check()

            def retain(output):
                with (folder/'raw_uint32.json').open('x', encoding='utf-8') as raw:
                    raw.write(json.dumps(output, allow_nan=False)+'\n')
                result['readback_retained'] = True
                result['raw_sha256'] = sha(folder/'raw_uint32.json')

            result['decoded'] = raw_dispatch(gpu, samples, statuses, check, retain)
            check(); validate_manifest(plan)
            result['status'] = 'scalar_gates_passed_pending_outer_authentication'
            return result
        except Exception as error:
            result['error_type'] = type(error).__name__
            raise
        finally:
            report.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
            report.flush()
