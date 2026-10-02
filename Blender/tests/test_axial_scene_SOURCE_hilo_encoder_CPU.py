"""New encoder conformance only; no frozen numeric producer imports or sweeps."""
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('own_new_encoder',ROOT/'Blender/benchmarks/capacity_audit/axial_scene_SOURCE_hilo_encoder_CPU_v1.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
DATA={}
class EncoderTests(unittest.TestCase):
    def test_01_scene_and_missing(self):
        req=e.reader.make_synthetic_request()
        audit=e.audit_scene_encoder_CPU(req,model=e.MODEL)
        with patch.object(e,'encode_scalar',side_effect=AssertionError('missing must not encode')) as mocked:
            missing=e.audit_scene_encoder_CPU(None,model=e.MODEL);self.assertEqual(mocked.call_count,0)
        self.assertTrue(audit[e.FLAG]);self.assertFalse(missing[e.FLAG])
        self.assertEqual((audit['source_count'],audit['new_RN32_casts'],audit['new_RN64_subtractions'],audit['new_RN64_decode_adds']),(4,16,8,8))
        self.assertEqual((missing['missing_cases'],missing['missing_sources']),(17,19))
        for row in audit['sources']:
            self.assertEqual(len(row['scalars']),2)
            self.assertFalse(row['frozen_guard_admission_for_entire_box_proved'])
            for x in row['scalars']:
                self.assertEqual([n['label'] for n in x['nodes']],['high_RN32','residual_RN64','low_RN32','decode_RN64'])
                self.assertLessEqual(F(*x['decoded_error_abs']),F(*x['point_error_bound_abs']))
        for result in (audit,missing):
            self.assertEqual(result['group_admissions'],0);self.assertIsNone(result['uniform_executed_SOURCE_error_L1'])
            self.assertIsNone(result['phase_bound_rad']);self.assertEqual(result['status'],'STOP')
            self.assertEqual(len(result['proof_scope']),38);self.assertTrue(all(v is False for v in result['proof_scope'].values()))
        DATA.update(request=req,audit=audit,missing=missing)
    def test_02_new_primitive_and_stop(self):
        tie_word=e.as_word(1.0+2.0**-24,64)
        tie=e.encode_scalar(tie_word);self.assertEqual(tie['high_uint32'],0x3f800000)
        negzero=e.encode_scalar(1<<63)
        self.assertEqual((negzero['high_uint32'],negzero['residual_uint64'],negzero['low_uint32'],negzero['decoded_uint64']),(1<<31,0,0,0))
        self.assertFalse(negzero['ORIGINAL_zero_sign_preserved']);self.assertFalse(negzero['ORIGINAL_bitwise_roundtrip'])
        self.assertEqual(negzero['decoded_error_abs'],[0,1]);self.assertEqual(negzero['status'],'ORIGINAL_ZERO_SIGN_FAIL_STOP')
        failures=[]
        for name,word,reason in (('selected_subnormal_high',e.as_word(2.0**-127,64),'normal-or-zero selected output'),
                                 ('high_overflow',e.as_word(2.0**128,64),'native high_RN32 overflow STOP')):
            with patch.object(e,'native_subtract',side_effect=AssertionError('bad high before residual')) as mocked:
                with self.assertRaises(ValueError) as caught:e.encode_scalar(word)
                self.assertEqual(mocked.call_count,0)
            self.assertEqual(str(caught.exception),reason)
            failures.append({'name':name,'original_uint64':word,'reason':reason,'residual_calls':0,'native_high_attempts':1})
        with patch.object(e,'native_cast32',return_value=0x3f800001),patch.object(e,'native_subtract',side_effect=AssertionError('poison before residual')) as mocked:
            with self.assertRaises(ValueError) as caught:e.encode_scalar(tie_word)
            self.assertEqual(mocked.call_count,0)
        failures.append({'name':'wrong_tie_cast','original_uint64':tie_word,'reason':str(caught.exception),'residual_calls':0,'native_high_attempts':0,'mock_high_calls':1})
        for word in (True,64.0,None,-1,1<<64):
            with patch.object(e,'native_cast32',side_effect=AssertionError('typed INPUT before cast')) as mocked:
                with self.assertRaises(ValueError) as caught:e.encode_scalar(word)
                self.assertEqual(mocked.call_count,0)
            failures.append({'name':'invalid_original','original_uint64':word,'reason':str(caught.exception),'cast_calls':0})
        DATA.update(primitive_valid=[tie,negzero],primitive_stops=failures)
    def test_03_all_INPUT_before_any(self):
        req=e.reader.make_synthetic_request();last=req['case_order'][-1]
        mutations=[
            ('context_cap',lambda r:r['cases'][last]['context'].__setitem__('phase_cap',123)),
            ('grid_program',lambda r:r['cases'][last]['GRID_INPUT'].__setitem__('encoder_program_sha256','0'*64)),
            ('source_gauge',lambda r:r['cases'][last]['SOURCE_read_requests'][-1].__setitem__('source_phase_reference_id','other')),
            ('word_change',lambda r:r['cases'][last]['SOURCE_read_requests'][-1]['words'].__setitem__(0,0)),
            ('width_float',lambda r:r['cases'][last]['SOURCE_read_requests'][-1].__setitem__('width',64.0)),
            ('reordered_SOURCE',lambda r:r['cases']['two_sources']['SOURCE_read_requests'].reverse()),
            ('missing_case',lambda r:r['cases'].pop(last)),
            ('fitted_output',lambda r:r.__setitem__('output_fitted',True)),
        ]
        stops=[]
        for name,mutate in mutations:
            bad=deepcopy(req);mutate(bad)
            with patch.object(e,'encode_scalar',side_effect=AssertionError('ALL before ANY')) as mocked:
                with self.assertRaises(ValueError) as caught:e.audit_scene_encoder_CPU(bad,model=e.MODEL)
                self.assertEqual(mocked.call_count,0)
            stops.append({'name':name,'request':bad,'reason':str(caught.exception),'encoder_calls':0})
        opts=[]
        for model in (None,True,e.MODEL+'-implicit'):
            with patch.object(e,'load_retained',side_effect=AssertionError('opt-in before INPUT')) as mocked:
                with self.assertRaises(ValueError) as caught:e.audit_scene_encoder_CPU(None,model=model)
                self.assertEqual(mocked.call_count,0)
            opts.append({'model':model,'reason':str(caught.exception),'loader_calls':0})
        DATA.update(batch_stops=stops,optin_stops=opts)
    def test_04_exact_guard_adversaries(self):
        tie=F(1)+F(1,1<<24)
        negatives=[('tie_odd',tie,0x3f800001,32,0),
                   ('wrong_sign',F(1),0xbf800000,32,0),
                   ('zero_sign',F(0),0,32,1),
                   ('selected_subnormal',F(1),1,32,0),
                   ('bool_width',F(1),0x3f800000,True,0),
                   ('bool_word',F(0),False,32,0)]
        rows=[]
        for name,exact,w,width,zs in negatives:
            with self.assertRaises(ValueError) as caught:e.check_RN(exact,w,width,zs)
            rows.append({'name':name,'exact':e.pair(exact),'word':w,'width':width,'zero_sign':zs,'reason':str(caught.exception)})
        DATA['guard_stops']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EncoderTests))
    print(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'data':DATA},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
