"""Opt-in HOST input transport only: no kernel, upload, inference or admission.

Geometry uses frozen hi-lo32 words; original source fields use binary64 bits.
Future source encoding must be explicit and charged; it is NOT done here.
No cached units, products, gates or expected port outputs enter these buffers.
"""
import base64
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-native-input-transport-le32-v1'
PREVIOUS = 'coordinacion/respuestas/AXIAL-NATIVE-EVIDENCE-CONTRACT-001-CODEX.json'
PREVIOUS_SHA = 'c01575b67e5a097df08d1254247c192d91d737af2c17a727f85f9ef3d8df2948'
PLAN_SHA = '472ac95b0a30c1bd1674223fc3ab563323cd14590bc4091af494d1d1e412fdb1'
GEOMETRY = 'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
BUFFER_NAMES = ('triangles', 'sources', 'wavelength', 'reference',
                'original_scene_json', 'input_metadata_json')
STRIDES = {'triangles': 35, 'sources': 32, 'wavelength': 18}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return sha(canonical(value))


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def payload(report):
    run = report['test_run']
    require(type(run['rc']) is int and run['rc'] == 0, 'retained status')
    raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
    require(len(raw) == run['stdout_bytes'] and sha(raw) == run['stdout_sha256'],
            'retained stdout fingerprint')
    return parse(raw)


def load_inputs():
    raw = (ROOT / PREVIOUS).read_bytes()
    require(sha(raw) == PREVIOUS_SHA, 'previous contract fingerprint')
    report = parse(raw)
    pins = dict(report['code_doc_sha256'])
    pins[PREVIOUS] = PREVIOUS_SHA
    for name, h in pins.items():
        require(sha((ROOT / name).read_bytes()) == h, 'changed frozen input ' + name)
    plan = payload(report)['plan']
    require(digest(plan) == PLAN_SHA, 'whole frozen contract')
    geometry = payload(parse((ROOT / GEOMETRY).read_bytes()))['cases']
    require(set(geometry) == set(plan['cases']), 'exact case coverage')
    snapshots = {name: c['scene_snapshot'] for name, c in geometry.items()}
    for name, snapshot in snapshots.items():
        require(digest(snapshot) == plan['cases'][name]['original_snapshot_sha256'],
                'original snapshot fingerprint')
    return plan, snapshots, pins


def u32(value):
    require(type(value) is int and 0 <= value < 2**32, 'uint32 type/range')
    return value


def radius_words(value):
    require(type(value) is int and 0 <= value < 2**511, 'nonnegative signed512 radius')
    return [(value >> (32 * i)) & 0xffffffff for i in range(16)]


def float64_words(value):
    require(type(value) in (int, float) and math.isfinite(value), 'original binary64 type/finite')
    return list(struct.unpack('<II', struct.pack('<d', value)))


def vector_words(vector):
    require(type(vector) is list and len(vector) == 3, 'three hi-lo coordinates')
    result = []
    for pair in vector:
        require(type(pair) is list and len(pair) == 2, 'hi-lo pair')
        result.extend(map(u32, pair))
    return result


def word_bytes(words):
    return struct.pack('<' + 'I' * len(words), *map(u32, words))


def pack_case(plan, name, snapshot):
    require(digest(plan) == PLAN_SHA, 'whole frozen contract; no caller swaps')
    require(type(name) is str and name in plan['cases'], 'case name')
    case = plan['cases'][name]
    require(digest(snapshot) == case['original_snapshot_sha256'], 'original scene binding')
    abi = case['effective_geometry_word_ABI']
    require(digest(abi) == case['word_ABI_sha256'], 'word ABI fingerprint')
    source_ids = case['source_order']
    require(source_ids == abi['source_order'] ==
            [s['source_id'] for s in abi['sources']] ==
            [s['id'] for s in snapshot['sources']], 'ordered source identity')
    triangles = []
    for triangle in abi['triangles']:
        owner = u32(triangle['owner'])
        require(owner < len(abi['object_ids']), 'owner range')
        require(len(triangle['vertices_uint32_hilo']) == 3, 'triangle shape')
        triangles.append(owner)
        for vertex in triangle['vertices_uint32_hilo']:
            triangles.extend(vector_words(vertex))
        triangles.extend(radius_words(triangle['X_radius_scaled']))
    sources = []
    for encoded, original in zip(abi['sources'], snapshot['sources']):
        sources.extend(vector_words(encoded['origin_uint32_hilo']))
        sources.extend(vector_words(encoded['direction_uint32_hilo']))
        sources.extend(radius_words(encoded['X_radius_scaled']))
        field = original['field_reim']
        require(type(field) is list and len(field) == 2, 'original complex field')
        for component in field:
            sources.extend(float64_words(component))
    wavelength = list(map(u32, abi['wavelength_uint32_hilo']))
    require(len(wavelength) == 2, 'wavelength hi-lo')
    wavelength.extend(radius_words(abi['wavelength_radius_scaled']))
    ref = case['effective_reference']
    original_ref = snapshot['objects']['D']
    encoded_ref = ref['HOST_reference_ABI']
    reference = [int(encoded_ref is not None)]
    for key in ('mode_origin_BU', 'mode_direction'):
        require(len(original_ref[key]) == 3, 'original reference vector')
        for value in original_ref[key]:
            reference.extend(float64_words(value))
    if encoded_ref is not None:
        reference.extend(map(u32, encoded_ref['uint32_hilo']))
        require(len(encoded_ref['uint32_hilo']) == 2, 'reference hi-lo')
        numerator, denominator = encoded_ref['outward_radius_BU']
        require(type(numerator) is int and type(denominator) is int and
                numerator >= 0 and denominator > 0, 'reference radius rational')
        scaled, remainder = divmod(numerator * 2**149, denominator)
        require(remainder == 0, 'reference radius must already be exact scaled integer')
        reference.extend(radius_words(scaled))
    # Explicit whitelist: the full plan (including expected answers) is never serialized.
    metadata = {
        'schema': MODEL, 'plan_sha256': PLAN_SHA, 'case_name': name,
        'scene_binding_sha256': case['scene_binding_sha256'],
        'word_ABI_sha256': case['word_ABI_sha256'],
        'original_snapshot_sha256': case['original_snapshot_sha256'],
        'source_order': source_ids, 'object_ids': abi['object_ids'], 'kinds': abi['kinds'],
        'extra_radius_HOST_BU_rational': abi['extra_radius_HOST_BU_rational'],
        'extra_radius_HOST_outward_inflation_BU_rational':
            abi['extra_radius_HOST_outward_inflation_BU_rational'],
        'reference': ref,
        'original_path_phase_caps': case['original_path_phase_caps'],
        'explicit_group_contract': case['explicit_group_contract'],
        'source_field_format': 'original binary64 bits; HOST hi-lo encoder NOT implemented',
        'radius_format': 'nonnegative signed512 little-endian limbs, BU*2^149',
        'scope': 'HOST transport only, input bytes are not native evidence or GPU admission'}
    buffers = {'triangles': word_bytes(triangles), 'sources': word_bytes(sources),
               'wavelength': word_bytes(wavelength), 'reference': word_bytes(reference),
               'original_scene_json': canonical(snapshot),
               'input_metadata_json': canonical(metadata)}
    counts = {'triangles': len(abi['triangles']), 'sources': len(source_ids),
              'wavelength': 1}
    layouts = {key: {'records': counts[key], 'stride_words': stride,
                    'bytes': counts[key] * stride * 4}
               for key, stride in STRIDES.items()}
    layouts['reference'] = {'words': 31 if encoded_ref is not None else 13,
                            'HOST_encoding_available': encoded_ref is not None}
    manifest = {'schema': MODEL, 'plan_sha256': PLAN_SHA, 'case_name': name,
                'endianness': 'little', 'layout': layouts,
                'buffers': {k: {'bytes': len(buffers[k]), 'sha256': sha(buffers[k])}
                            for k in BUFFER_NAMES}}
    return manifest, buffers


def verify_packet(plan, name, snapshot, manifest, buffers):
    """Read-only exact input receipt; not an upload/dispatch or admission."""
    expected_manifest, expected = pack_case(plan, name, snapshot)
    require(digest(manifest) == digest(expected_manifest), 'exact input manifest')
    require(type(buffers) is dict and set(buffers) == set(BUFFER_NAMES), 'input-only buffers')
    for key in BUFFER_NAMES:
        require(type(buffers[key]) is bytes and buffers[key] == expected[key],
                'input buffer differs: ' + key)
    return {'input_transport_verified': True, 'GPU_executed': False,
            'source_HOST_encoder_implemented': False, 'native_kernel_implemented': False,
            'GPU_job_admission': False}
