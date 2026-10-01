"""Focused HOST source encoder tests, no frozen arithmetic producer imported."""
import base64
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import struct
import sys
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks/capacity_audit'))
import axial_native_source_encoder_v1 as encoder


def word64(value):
    return struct.unpack('<Q', struct.pack('<d', value))[0]


class EncoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets, cls.pins = encoder.load_packets()
        cls.cases = {n: encoder.encode_packet(n,p) for n,p in cls.packets.items()}

    def test_all_original_sources_including_rejected_cases(self):
        ids = 0
        for name, case in self.cases.items():
            self.assertEqual(case['source_order'], [s['source_id'] for s in case['fields']])
            for source in case['fields']:
                ids += 1
                self.assertEqual(source['original_source_uint64'], [word64(.1),word64(0.)])
                self.assertEqual(source['source_limb_uint32'], [1036831949,2966211789,0,0])
                self.assertEqual(source['source_encoding_error_L1'], [1,2**55])
                self.assertEqual(source['costs']['new_HOST_RN32'], 4)
                self.assertEqual(source['costs']['new_HOST_exact_residual_subtractions'], 2)
                self.assertEqual(source['source_phase_reference_id'],
                                 'original-source-zero:'+case['scene_binding_sha256']+':'+source['source_id'])
            self.assertFalse(case['GPU_job_admission'])
            self.assertFalse(case['accepted_full_field_pipeline'])
            self.assertTrue(case['encoding_error_not_yet_propagated_through_unit_or_detector'])
        self.assertEqual(ids,14)

    def test_matches_available_frozen_source_inputs_not_outputs(self):
        r=json.loads((encoder.ROOT/'coordinacion/respuestas/AXIAL-NATIVE-EVIDENCE-CONTRACT-001-CODEX.json').read_bytes())
        plan=json.loads(zlib.decompress(base64.b64decode(r['test_run']['stdout_zlib_base64'])))['plan']
        matched=0
        for name, c in plan['cases'].items():
            self.assertEqual(self.cases[name]['group_contract_UNCHANGED'],c['explicit_group_contract'])
            self.assertEqual(self.cases[name]['original_path_phase_caps_UNCHANGED'],c['original_path_phase_caps'])
            sources={s['source_id']:s for s in self.cases[name]['fields']}
            for prior in c['expected_source_outputs']:
                if prior['source_limb_uint32'] is not None:
                    self.assertEqual(sources[prior['source_id']]['source_limb_uint32'],prior['source_limb_uint32'])
                    matched+=1
        self.assertEqual(matched,6)

    def test_ties_even_both_signs_and_binade(self):
        for q,expected in ((F(1)+F(1,2**24),0x3f800000),
                           (F(1)+F(3,2**24),0x3f800002),
                           (F(1)-F(1,2**25),0x3f800000)):
            self.assertEqual(encoder.rn32(q),expected)
            self.assertEqual(encoder.rn32(-q),expected|2**31)

    def test_subnormal_choice_rejected_but_rounded_zero_charged(self):
        self.assertEqual(encoder.rn32(F(1,2**150)),0)
        self.assertEqual(encoder.rn32(-F(1,2**150)),0)
        self.assertEqual(encoder.rn32(F(1,2**126)-F(1,2**150)),0x00800000)
        for q in (F(1,2**149),F(1,2**150)+F(1,2**200),F(1,2**126)-F(3,2**150)):
            with self.assertRaises(ValueError):
                encoder.rn32(q)
        tiny=encoder.encode_complex([1,0]) # smallest positive binary64, not zero input
        self.assertEqual(tiny['source_limb_uint32'],[0,0,0,0])
        self.assertEqual(tiny['source_encoding_error_L1'],[1,2**1074])

    def test_overflow_nonfinite_bool_and_no_saturation(self):
        for q in (F(2**128),F(2**128-2**103),-F(2**128-2**103)):
            with self.assertRaises(ValueError):
                encoder.rn32(q)
        self.assertEqual(encoder.rn32(F(2**128-2**104)),0x7f7fffff)
        for bits in (32.0,True,16):
            with self.assertRaises(ValueError):
                encoder.decode(0,bits)
        for words in ([True,0],[-1,0],[2**64,0],[0x7ff0000000000000,0],[0x7ff8000000000001,0]):
            with self.assertRaises(ValueError):
                encoder.encode_complex(words)

    def test_original_signed_zero_preserved_separately_canonical_limb_zero(self):
        inputs=[2**63,0]
        out=encoder.encode_complex(inputs)
        inputs[0]=0
        self.assertEqual(out['original_source_uint64'],[2**63,0])
        self.assertEqual(out['source_limb_uint32'],[0,0,0,0])
        self.assertEqual(out['source_encoding_error_L1'],[0,1])

    def test_complex_distinct_amplitudes_and_exact_residual_trace(self):
        for re,im in ((.1,-.3),(1+2**-30,2**-80),(-2**20,3.25),(0.,0.)):
            out=encoder.encode_complex([word64(re),word64(im)])
            self.assertEqual(len(base64.b64decode(out['source_hilo_le_base64'])),16)
            for trace,value in zip(out['HOST_trace'],(re,im)):
                q=F(value)
                self.assertEqual(F(*trace['original']),q)
                self.assertEqual(F(*trace['HOST_exact_residual']),q-F(*trace['high']))
                self.assertEqual(F(*trace['encoding_error']),abs(q-F(*trace['represented'])))

    def test_rehashed_source_swap_and_foreign_case_reject(self):
        packet=copy.deepcopy(self.packets['positive'])
        raw=bytearray(base64.b64decode(packet['buffers_base64']['sources']))
        raw[112]^=1
        packet['buffers_base64']['sources']=base64.b64encode(raw).decode()
        packet['manifest']['buffers']['sources']['sha256']=encoder.sha(raw)
        with self.assertRaises(ValueError):
            encoder.encode_packet('positive',packet)
        with self.assertRaises(ValueError):
            encoder.encode_packet('negative',self.packets['positive'])
        packet=copy.deepcopy(self.packets['two_sources'])
        packet['manifest']['case_name']='positive'
        with self.assertRaises(ValueError):
            encoder.encode_packet('two_sources',packet)

    def test_error_is_reported_not_a_new_field_budget_gate(self):
        for name,case in self.cases.items():
            self.assertFalse(case['native_kernel_implemented'])
            self.assertFalse(case['coherence_authenticated'])
            self.assertEqual(case['input_receipts_UNCHANGED'], self.packets[name]['manifest']['buffers'])
            self.assertEqual(len(base64.b64decode(case['source_hilo_buffer_base64'])),
                             16*len(case['source_order']))
        with self.assertRaises(ValueError):
            encoder.parse(b'{"x":1,"x":2}')


if __name__=='__main__':
    # Instrument only this own new encoder, not any frozen producer.
    original_rn32=encoder.rn32
    original_encode_complex=encoder.encode_complex
    rn_trace=[]
    encoded_success=[]
    def measured_rn32(q):
        row={'input_rational':encoder.pair(q)}
        try:
            result_word=original_rn32(q)
        except ValueError as error:
            row.update(rejected=True,reason=str(error))
            rn_trace.append(row)
            raise
        row.update(rejected=False,output_uint32=result_word)
        rn_trace.append(row)
        return result_word
    def measured_encode_complex(words):
        result_source=original_encode_complex(words)
        encoded_success.append(result_source)
        return result_source
    encoder.rn32=measured_rn32
    encoder.encode_complex=measured_encode_complex
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(EncoderTests))
    controls={}
    if result.wasSuccessful():
        for name,words in {
            'complex':[word64(.1),word64(-.3)],
            'exact':[word64(1+2**-30),word64(2**-80)],
            'signedzero':[2**63,0],
            'tiny64':[1,0],
            'maxfinite32':[word64(2**128-2**104),0],
        }.items():
            controls[name]=encoder.encode_complex(words)
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,
        'model':encoder.MODEL,'pins':getattr(EncoderTests,'pins',{}),
        'cases':getattr(EncoderTests,'cases',{}) if result.wasSuccessful() else {},
        'controls':controls,'GPU_executed':False,'new_HOST_RN32_main':56,
        'new_HOST_exact_residual_subtractions_main':28,
        'new_HOST_RN32_controls':20,'new_HOST_exact_residual_subtractions_controls':10,
        'all_new_RN32_calls_including_tests_and_controls':rn_trace,
        'all_new_successful_encodings_including_tests_and_controls':encoded_success,
        'all_new_HOST_exact_residual_subtractions_including_tests_and_controls':2*len(encoded_success)},
        sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
