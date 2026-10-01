"""Own CPU transport tests; no retained arithmetic producer is imported."""
import base64
import copy
import json
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks/capacity_audit'))
import axial_native_ingress_v1 as transport


class IngressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.snapshots, cls.pins = transport.load_inputs()

    def pack(self, name='positive'):
        return transport.pack_case(self.plan, name, self.snapshots[name])

    def test_all_cases_exact_roundtrip_and_original_fields(self):
        for name, case in self.plan['cases'].items():
            manifest, buffers = self.pack(name)
            result = transport.verify_packet(self.plan, name, self.snapshots[name], manifest, buffers)
            self.assertTrue(result['input_transport_verified'])
            self.assertFalse(result['GPU_job_admission'])
            self.assertFalse(result['native_kernel_implemented'])
            words = struct.unpack('<' + 'I' * (len(buffers['sources']) // 4), buffers['sources'])
            for i, original in enumerate(self.snapshots[name]['sources']):
                self.assertEqual(buffers['sources'][i*128+112:i*128+128],
                                 struct.pack('<dd', *original['field_reim']))
                self.assertEqual(words[i*32:i*32+6], tuple(
                    v for pair in case['effective_geometry_word_ABI']['sources'][i]['origin_uint32_hilo']
                    for v in pair))
            self.assertEqual(json.loads(buffers['original_scene_json']), self.snapshots[name])

    def test_no_expected_outputs_or_gate_or_lookup_in_input_metadata(self):
        forbidden = {'expected_stage_gates', 'expected_original_phase_gate', 'legacy_gates_UNCHANGED',
                     'expected_source_outputs', 'expected_port_outputs', 'restricted_tree_certificate_sha256',
                     'unit_uint64', 'field_uint64', 'source_limb_uint32', 'port_power_uint64',
                     'group_field_uint64', 'group_power_uint64', 'case_dependency_sha256'}
        def walk(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)
        for name in self.snapshots:
            _, buffers = self.pack(name)
            walk(json.loads(buffers['input_metadata_json']))
            walk(json.loads(buffers['original_scene_json']))
            self.assertNotIn('U/GEMM', buffers['input_metadata_json'].decode())

    def test_missing_reference_is_not_encoded_zero_or_success(self):
        count = 0
        for name, case in self.plan['cases'].items():
            manifest, buffers = self.pack(name)
            available = case['effective_reference']['HOST_reference_ABI'] is not None
            self.assertEqual(struct.unpack('<I', buffers['reference'][:4])[0], int(available))
            self.assertEqual(len(buffers['reference']), 124 if available else 52)
            self.assertIs(manifest['layout']['reference']['HOST_encoding_available'], available)
            if not available:
                count += 1
        self.assertEqual(count, 5)

    def test_declared_radius_not_erased_when_original_binding_same(self):
        a, ba = self.pack('positive')
        b, bb = self.pack('declared_radius_PASS')
        self.assertEqual(self.plan['cases']['positive']['scene_binding_sha256'],
                         self.plan['cases']['declared_radius_PASS']['scene_binding_sha256'])
        self.assertNotEqual(a['buffers']['sources']['sha256'], b['buffers']['sources']['sha256'])
        limbs = struct.unpack('<16I', bb['sources'][48:112])
        self.assertEqual(sum(v << (32*i) for i, v in enumerate(limbs)), 2**142)
        self.assertEqual(ba['sources'][48:112], bytes(64))

    def test_corrupted_rehashed_bytes_and_foreign_buffer_reject(self):
        manifest, buffers = self.pack()
        for key in transport.BUFFER_NAMES:
            damaged = dict(buffers)
            value = bytearray(damaged[key])
            value[0] ^= 1
            damaged[key] = bytes(value)
            changed = copy.deepcopy(manifest)
            changed['buffers'][key]['sha256'] = transport.sha(damaged[key])
            with self.assertRaises(ValueError):
                transport.verify_packet(self.plan, 'positive', self.snapshots['positive'], changed, damaged)
        damaged = dict(buffers, answers=b'cached output')
        with self.assertRaises(ValueError):
            transport.verify_packet(self.plan, 'positive', self.snapshots['positive'], manifest, damaged)

    def test_plan_source_reference_order_and_expected_gate_swaps_reject(self):
        changed = copy.deepcopy(self.plan)
        changed['cases']['two_sources']['source_order'].reverse()
        with self.assertRaises(ValueError):
            transport.pack_case(changed, 'two_sources', self.snapshots['two_sources'])
        for mutate in (
            lambda p: p['cases']['positive']['source_order'].append('other'),
            lambda p: p['cases']['positive']['expected_stage_gates'].clear(),
            lambda p: p['cases']['positive']['effective_reference'].clear(),
        ):
            changed = copy.deepcopy(self.plan)
            mutate(changed)
            with self.assertRaises(ValueError):
                transport.pack_case(changed, 'positive', self.snapshots['positive'])
        changed = copy.deepcopy(self.snapshots['positive'])
        changed['sources'][0]['field_reim'][0] = 0.0
        with self.assertRaises(ValueError):
            transport.pack_case(self.plan, 'positive', changed)
        a, ba = self.pack('positive')
        with self.assertRaises(ValueError):
            transport.verify_packet(self.plan, 'negative', self.snapshots['negative'], a, ba)

    def test_word_overflow_bool_negative_and_signed_zero(self):
        for value in (True, -1, 2**32, 1.0):
            with self.assertRaises(ValueError):
                transport.u32(value)
        for value in (True, -1, 2**511, 0.0):
            with self.assertRaises(ValueError):
                transport.radius_words(value)
        for value in (True, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                transport.float64_words(value)
        self.assertEqual(transport.float64_words(-0.0), [0, 0x80000000])
        limbs = transport.radius_words(2**511-1)
        self.assertEqual(limbs, [0xffffffff]*15 + [0x7fffffff])

    def test_manifest_endian_counts_stride_and_availability_reject(self):
        manifest, buffers = self.pack()
        for mutate in (
            lambda m: m.update(endianness='big'),
            lambda m: m['layout']['sources'].update(stride_words=28),
            lambda m: m['layout']['sources'].update(records=0),
            lambda m: m['layout']['reference'].update(HOST_encoding_available=False),
        ):
            changed = copy.deepcopy(manifest)
            mutate(changed)
            with self.assertRaises(ValueError):
                transport.verify_packet(self.plan, 'positive', self.snapshots['positive'], changed, buffers)

    def test_json_duplicate_nonfinite_reject(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}'):
            with self.assertRaises(ValueError):
                transport.parse(raw)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IngressTests)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    packets = {}
    if result.wasSuccessful():
        for name in IngressTests.snapshots:
            manifest, buffers = transport.pack_case(IngressTests.plan, name, IngressTests.snapshots[name])
            packets[name] = {'manifest': manifest,
                             'buffers_base64': {k: base64.b64encode(v).decode() for k,v in buffers.items()}}
    print(json.dumps({'PASS': result.wasSuccessful(), 'tests': result.testsRun,
                      'model': transport.MODEL, 'pins': getattr(IngressTests, 'pins', {}),
                      'packets': packets, 'GPU_executed': False,
                      'source_HOST_encoder_implemented': False, 'native_kernel_implemented': False},
                     sort_keys=True, separators=(',', ':'), allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
