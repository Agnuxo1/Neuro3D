"""Tests only the new strict selected-word CPU reader; no frozen producer imports."""
import importlib.util
import json
import struct
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'Blender/benchmarks/capacity_audit/axial_scene_SOURCE_selected_word_reader_CPU_v1.py'
spec=importlib.util.spec_from_file_location('own_selected_reader',P)
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
DATA={}
class ReaderTests(unittest.TestCase):
    def test_01_scene_and_missing(self):
        req=reader.make_synthetic_request()
        actual=reader.audit_scene_SOURCE_reader_CPU(req,model=reader.MODEL)
        with patch.object(reader,'interpret_SELECTED_CPU',side_effect=AssertionError('missing must not read')) as mocked:
            missing=reader.audit_scene_SOURCE_reader_CPU(None,model=reader.MODEL)
            self.assertEqual(mocked.call_count,0)
        self.assertEqual((actual['source_count'],actual['new_word_reinterpretations'],actual['group_admissions']),(4,8,0))
        self.assertTrue(actual[reader.FLAG])
        self.assertEqual(sum(r['retained_whole_box_guard_admission_disproved'] is True for r in actual['sources']),2)
        self.assertTrue(all(r['frozen_guard_admission_for_entire_box_proved'] is False and r['status']=='STOP' for r in actual['sources']))
        self.assertEqual((missing['retained_missing_cases'],missing['retained_missing_sources'],missing['new_word_reinterpretations']),(17,19,0))
        self.assertFalse(missing[reader.FLAG])
        for result in (actual,missing):
            self.assertEqual(result['status'],'STOP')
            self.assertIsNone(result['uniform_executed_SOURCE_error_L1'])
            self.assertEqual(len(result['proof_scope']),38)
            self.assertTrue(all(v is False for v in result['proof_scope'].values()))
        DATA.update(request=req,scene=actual,missing=missing)
    def test_02_primitive_types_and_classes(self):
        valid=[];rejected=[]
        for width,mb,eb in ((32,23,8),(64,52,11)):
            sign=1<<(width-1);one=((1<<(eb-1))-1)<<mb;maximum=(((1<<eb)-2)<<mb)|((1<<mb)-1)
            for name,word in (('positive_zero',0),('negative_zero',sign),('positive_one',one),('negative_one',sign|one),
                              ('positive_min_normal',1<<mb),('negative_min_normal',sign|(1<<mb)),
                              ('positive_max_finite',maximum),('negative_max_finite',sign|maximum)):
                row=reader.interpret_SELECTED_CPU(word,width)
                self.assertEqual(row['roundtrip_uint'],word);self.assertEqual(row['new_arithmetic_or_RN_casts'],0)
                valid.append({'name':name,**row})
            inf=((1<<eb)-1)<<mb
            for name,word in (('bool_true',True),('bool_false',False),('float',1.0),('none',None),('negative',-1),
                              ('overflow',1<<width),('min_subnormal',1),('negative_subnormal',sign|1),
                              ('max_subnormal',(1<<mb)-1),('inf',inf),('negative_inf',sign|inf),('nan',inf|1)):
                with patch.object(reader.struct,'pack',side_effect=AssertionError('invalid must not pack')) as mocked:
                    with self.assertRaises(ValueError) as caught:reader.interpret_SELECTED_CPU(word,width)
                    self.assertEqual(mocked.call_count,0)
                rejected.append({'name':name,'width':width,'word':word,'reason':str(caught.exception),'pack_calls':0})
        for width in (True,False,32.0,64.0,'64',None,16,128):
            with patch.object(reader.struct,'pack',side_effect=AssertionError('invalid width must not pack')) as mocked:
                with self.assertRaises(ValueError) as caught:reader.interpret_SELECTED_CPU(0,width)
                self.assertEqual(mocked.call_count,0)
            rejected.append({'name':'invalid_width','width':width,'word':0,'reason':str(caught.exception),'pack_calls':0})
        self.assertEqual((len(valid),len(rejected)),(16,32))
        DATA.update(primitive_valid=valid,primitive_rejections=rejected)
    def test_03_all_before_any(self):
        base=reader.make_synthetic_request();last=base['case_order'][-1]
        # Late-case corruptions ensure earlier valid SOURCE entries are NOT interpreted.
        mutations=[
            ('context_cap',lambda r:r['cases'][last]['context'].__setitem__('phase_cap',123)),
            ('grid_snapshot',lambda r:r['cases'][last]['GRID_INPUT'].__setitem__('original_snapshot_sha256','0'*64)),
            ('grid_domain',lambda r:r['cases'][last]['GRID_INPUT'].__setitem__('domain_sha256','0'*64)),
            ('source_gauge',lambda r:r['cases'][last]['SOURCE_read_requests'][-1].__setitem__('terminal_reference_id','changed')),
            ('source_domain',lambda r:r['cases'][last]['SOURCE_read_requests'][-1].__setitem__('domain_source_sha256','0'*64)),
            ('source_id',lambda r:r['cases'][last]['SOURCE_read_requests'][-1].__setitem__('source_id','changed')),
            ('word_bool',lambda r:r['cases'][last]['SOURCE_read_requests'][-1]['words'].__setitem__(1,False)),
            ('word_signedzero',lambda r:r['cases'][last]['SOURCE_read_requests'][-1]['words'].__setitem__(1,1<<63)),
            ('word_changed',lambda r:r['cases'][last]['SOURCE_read_requests'][-1]['words'].__setitem__(0,0)),
            ('width_float',lambda r:r['cases'][last]['SOURCE_read_requests'][-1].__setitem__('width',64.0)),
            ('missing_source',lambda r:r['cases'][last]['SOURCE_read_requests'].pop()),
            ('missing_case',lambda r:r['cases'].pop(last)),
            ('fitted_output',lambda r:r.__setitem__('output_fitted',True)),
            ('request_model',lambda r:r.__setitem__('model','wrong')),
            ('duplicate_case_order',lambda r:r['case_order'].__setitem__(-1,r['case_order'][0])),
            ('reordered_source',lambda r:r['cases']['two_sources']['SOURCE_read_requests'].reverse()),
        ]
        rejected=[]
        for name,mutate in mutations:
            req=deepcopy(base);mutate(req)
            with patch.object(reader,'interpret_SELECTED_CPU',side_effect=AssertionError('ALL before ANY')) as mocked:
                with self.assertRaises(ValueError) as caught:reader.audit_scene_SOURCE_reader_CPU(req,model=reader.MODEL)
                self.assertEqual(mocked.call_count,0)
            rejected.append({'name':name,'request':req,'reason':str(caught.exception),'reader_calls':0})
        DATA['batch_rejections']=rejected
    def test_04_roundtrip_and_optin_failure(self):
        # Corrupt only the float unpack of our new primitive, not any frozen writer.
        real_unpack=struct.unpack
        def wrong(fmt,raw):return (0.0,) if fmt=='<d' else real_unpack(fmt,raw)
        with patch.object(reader.struct,'unpack',side_effect=wrong):
            with self.assertRaises(ValueError) as caught:reader.interpret_SELECTED_CPU(1<<63,64)
        DATA['roundtrip_failure']={'word':1<<63,'width':64,'reason':str(caught.exception)}
        rejected=[]
        for model in (None,True,reader.MODEL+'-implicit'):
            with patch.object(reader,'load_retained',side_effect=AssertionError('optin before INPUT')) as mocked:
                with self.assertRaises(ValueError) as caught:reader.audit_scene_SOURCE_reader_CPU(None,model=model)
                self.assertEqual(mocked.call_count,0)
            rejected.append({'model':model,'reason':str(caught.exception),'loader_calls':0})
        DATA['optin_rejections']=rejected
if __name__=='__main__':
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReaderTests))
    print(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'data':DATA},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
