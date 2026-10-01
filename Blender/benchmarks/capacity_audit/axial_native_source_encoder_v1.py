"""Opt-in exact HOST source encoder from pinned ORIGINAL input bytes.

Not a GPU operation model or inference. Residual subtraction is exact HOST
rational arithmetic, explicitly charged, not an uncharged native subtraction.
"""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-HOST-original-binary64-to-normal-hilo32-input-v1'
INGRESS = 'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
INGRESS_SHA = 'c20ddf4f856b8932c9394d1d60c6c4e44b3170bac72e4a3922a673c778dfb855'
PACKET_SHA = {
    "boundary_FAIL": "b4f362b8be7a397818963b3d2ebda0346184345ec21f8a6bfb71bdfc7f479242",
    "declared_contact_FAIL": "f6728a0de88c7590e9d3e0d9acc7227b31939a1b1b9e8b9a30447d24336e42d8",
    "declared_radius_PASS": "33531c266922d9d293ddd8deeb30994bbdefff18299da39ff5bddcf88e827e6f",
    "lambda_transport_FAIL": "bdf5f55c33fe0175a0c4c8fcc5a5ac9b6810654aee845f6cc6a9357a179b014b",
    "negative": "5e00c20768609b9dd3bc725c6c136dbe9d104432de6c0fcc0ea2a240b9309d23",
    "nonexact_geometry_phase_FAIL": "d3263794d356d8558d1baa0045b2a81fb5c2e5a774905f342946069da4d8ff28",
    "nonexact_geometry_phase_PASS": "920487b2eb7427a2bde64c08899be66e26def118535cc7afa9e1f9936b5d2dcc",
    "otherowner_contact_FAIL": "11238c3799695b77e08413168b96d5f1d33832a7a50b63bcf0868398ffd92bf3",
    "positive": "c98c33e2f272748bb36ed9a55f716327ad0c09130ba8d69e3316ad327313bcfe",
    "source_contact_FAIL": "21df0614ce1fb0565c769d9c894241d5a954d77dad7337d718269d163fa4e101",
    "thin_collapsed_FAIL": "6dfa48f6d2abdaa3f68917ce51cab2c0c4ef8af385ea2246b9d29e1aa7133eb3",
    "thin_resolved": "c5fb9c96b5231b6c61a31872b67121073a696cf5444930bb09290491c70e56c6",
    "two_sources": "9a5a12f985b053786688604a9f617c753e33b4486765264c82903be20b4b37a1"
}


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
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def payload(report):
    t = report['test_run']
    require(type(t['rc']) is int and t['rc'] == 0, 'retained run status')
    raw = zlib.decompress(base64.b64decode(t['stdout_zlib_base64'], validate=True))
    require(len(raw) == t['stdout_bytes'] and sha(raw) == t['stdout_sha256'], 'retained stdout SHA')
    return parse(raw)


def load_packets():
    raw = (ROOT / INGRESS).read_bytes()
    require(sha(raw) == INGRESS_SHA, 'frozen ingress report')
    report = parse(raw)
    pins = dict(report['code_doc_sha256'])
    pins[INGRESS] = INGRESS_SHA
    for name, h in pins.items():
        require(sha((ROOT / name).read_bytes()) == h, 'changed frozen input ' + name)
    packets = payload(report)['packets']
    require(set(packets) == set(PACKET_SHA), 'frozen full case coverage')
    for name, packet in packets.items():
        require(digest(packet) == PACKET_SHA[name], 'input-only packet identity')
    return packets, pins


def pair(q):
    return [q.numerator, q.denominator]


def decode(word, bits):
    require(type(word) is int and type(bits) is int and bits in (32, 64) and
            0 <= word < 2**bits, 'word type/range')
    mantissa_bits, exponent_bits, bias = (23, 8, 127) if bits == 32 else (52, 11, 1023)
    exponent = (word >> mantissa_bits) & (2**exponent_bits-1)
    fraction = word & (2**mantissa_bits-1)
    require(exponent != 2**exponent_bits-1, 'finite original/limb required')
    significand = fraction if exponent == 0 else fraction + 2**mantissa_bits
    power = (1 if exponent == 0 else exponent) - bias - mantissa_bits
    q = F(significand * 2**power) if power >= 0 else F(significand, 2**(-power))
    return -q if word >> (bits-1) else q


def ties_even(n, d):
    whole, remainder = divmod(n, d)
    return whole + int(2*remainder > d or (2*remainder == d and whole & 1))


def rn32(q):
    """Integer RN ties-even. Chosen subnormals/overflow rejected, never FTZ/clamp.

    Canonical +0 for an exact or rounded zero matches frozen Fraction encoder.
    Original signed zero is retained separately in input binary64 words.
    """
    require(type(q) is F, 'exact HOST rational required')
    if q == 0:
        return 0
    sign = int(q < 0) << 31
    n, d = abs(q.numerator), q.denominator
    exponent = n.bit_length() - d.bit_length()
    below_power = n < d << exponent if exponent >= 0 else n << -exponent < d
    if below_power:
        exponent -= 1
    require(exponent <= 127, 'binary32 overflow, no saturation')
    grid = max(exponent, -126) - 23
    m = ties_even(n, d << grid) if grid >= 0 else ties_even(n << -grid, d)
    if m == 0:
        return 0
    if exponent < -126:
        require(m >= 2**23, 'chosen binary32 subnormal, no FTZ assumption')
        exponent = -126
    if m == 2**24:
        m >>= 1
        exponent += 1
    require(-126 <= exponent <= 127 and 2**23 <= m < 2**24, 'finite normal binary32 required')
    return sign | ((exponent+127) << 23) | (m-2**23)


def encode_complex(original_words):
    require(type(original_words) is list and len(original_words) == 2, 'two ORIGINAL uint64 components')
    original = [decode(w, 64) for w in original_words]
    words, represented, errors, trace = [], [], [], []
    for q in original:
        hi = rn32(q)
        high = decode(hi, 32)
        residual = q - high  # exact HOST subtraction, NOT RN64 or native
        lo = rn32(residual)
        value = high + decode(lo, 32)
        words.extend((hi, lo))
        represented.append(value)
        errors.append(abs(q-value))
        trace.append({'original': pair(q), 'high_uint32': hi, 'high': pair(high),
                      'HOST_exact_residual': pair(residual), 'low_uint32': lo,
                      'represented': pair(value), 'encoding_error': pair(abs(q-value))})
    raw = struct.pack('<4I', *words)
    return {'model': MODEL, 'original_source_uint64': list(original_words),
            'source_limb_uint32': words, 'source_exact_limb_sum_rational': list(map(pair, represented)),
            'source_encoding_error_L1': pair(sum(errors, F(0))),
            'source_norm_L1': pair(sum(map(abs, original), F(0))),
            'HOST_trace': trace, 'source_hilo_le_base64': base64.b64encode(raw).decode(),
            'source_hilo_le_sha256': sha(raw),
            'costs': {'new_HOST_RN32': 4, 'new_HOST_exact_residual_subtractions': 2,
                      'cached_encoding_operations_NOT_executed': 0},
            'GPU_executed': False, 'native_promotion_allowed': False}


def encode_packet(name, packet):
    """Consumes input buffers, never cached unit/product/output/gates."""
    require(type(name) is str and name in PACKET_SHA and digest(packet) == PACKET_SHA[name],
            'pinned input packet; reject even rehashed substitution')
    manifest = packet['manifest']
    buffers = {key: base64.b64decode(value, validate=True)
               for key, value in packet['buffers_base64'].items()}
    for key, raw in buffers.items():
        require(manifest['buffers'][key] == {'bytes': len(raw), 'sha256': sha(raw)}, 'input byte receipt')
    metadata = parse(buffers['input_metadata_json'])
    original = parse(buffers['original_scene_json'])
    ids = metadata['source_order']
    require(ids == [s['id'] for s in original['sources']], 'source ID/order')
    require(len(buffers['sources']) == 128*len(ids), 'ingress source record stride')
    fields = []
    for i, sid in enumerate(ids):
        raw = buffers['sources'][128*i+112:128*i+128]
        require(raw == struct.pack('<dd', *original['sources'][i]['field_reim']), 'ORIGINAL source bits')
        encoded = encode_complex(list(struct.unpack('<QQ', raw)))
        encoded['source_id'] = sid
        encoded['source_phase_reference_id'] = 'original-source-zero:' + metadata['scene_binding_sha256'] + ':' + sid
        fields.append(encoded)
    hilo = b''.join(base64.b64decode(v['source_hilo_le_base64']) for v in fields)
    return {'model': MODEL, 'case_name': name, 'input_packet_sha256': PACKET_SHA[name],
            'scene_binding_sha256': metadata['scene_binding_sha256'],
            'word_ABI_sha256': metadata['word_ABI_sha256'],
            'original_snapshot_sha256': metadata['original_snapshot_sha256'],
            'source_order': ids, 'fields': fields,
            'input_receipts_UNCHANGED': manifest['buffers'],
            'original_path_phase_caps_UNCHANGED': metadata['original_path_phase_caps'],
            'group_contract_UNCHANGED': metadata['explicit_group_contract'],
            'source_hilo_buffer_base64': base64.b64encode(hilo).decode(),
            'source_hilo_buffer_sha256': sha(hilo), 'source_stride_words': 4,
            'costs': {'new_HOST_RN32': 4*len(ids), 'new_HOST_exact_residual_subtractions': 2*len(ids),
                      'cached_encoding_operations_NOT_executed': 0},
            'encoding_error_not_yet_propagated_through_unit_or_detector': True,
            'accepted_full_field_pipeline': False, 'native_kernel_implemented': False,
            'GPU_executed': False, 'GPU_job_admission': False,
            'coherence_authenticated': False, 'execution_authenticated': False}
