"""Own bounded new decoder tests; frozen encoder/producers are never imported."""
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('own_zero_decoder',ROOT/'Blender/benchmarks/capacity_audit/axial_SOURCE_hilo_zero_aware_decoder_CPU_v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA={}
class Tests(unittest.TestCase):
    def test_1_scene_and_missing(self):
        req=m.make_synthetic_request();out=m.audit_decoder_CPU(req,model=m.MODEL)
        DATA['request']=req;DATA['audit']=out
        self.assertEqual((out['new_native_RN64_adds'],out['new_zero_branch_selections']),(4,4))
        self.assertEqual(len(out['sources']),4)
        self.assertTrue(all(s['ORIGINAL_zero_sign_preserved'] for r in out['sources'] for s in r['scalars']))
        self.assertEqual([r['retained_whole_box_guard_admission_disproved'] for r in out['sources']],[True,True,None,None])
        self.assertTrue(all(v is False for v in out['proof_scope'].values()))
        with patch.object(m,'decode_scalar',side_effect=AssertionError('missing INPUT must not decode')):
            missing=m.audit_decoder_CPU(None,model=m.MODEL)
        self.assertEqual((missing['missing_cases'],missing['missing_sources']),(17,19))
        self.assertEqual(missing['new_native_RN64_adds'],0);DATA['missing']=missing
    def test_2_new_branch_controls_and_retained_failure(self):
        controls=[]
        for high in (0,1<<31):
            for low in (0,1<<31):
                with patch.object(m,'native_add64',side_effect=AssertionError('both-zero branch is not native sum')):
                    r=m.decode_scalar(high,low)
                self.assertEqual(r['decoded_uint64'],(high>>31)<<63)
                controls.append(r)
        for high,low in ((0x3f800000,0xbf800000),(0xbf800000,0x3f800000),
                         (0x3f800000,74<<23),(0xbf800000,(1<<31)|(74<<23))):
            controls.append(m.decode_scalar(high,low))
        self.assertEqual([v['decoded_uint64'] for v in controls[4:]],[0,0,0x3ff0000000000000,0xbff0000000000000])
        DATA['controls']=controls
        retained,_,_=m.load_retained();old=retained['primitive_valid'][1]
        self.assertEqual(old['original_uint64'],1<<63)
        self.assertFalse(old['ORIGINAL_zero_sign_preserved']);self.assertEqual(old['decoded_uint64'],0)
        self.assertEqual(old['status'],'ORIGINAL_ZERO_SIGN_FAIL_STOP')
        new=m.decode_scalar(old['high_uint32'],old['low_uint32'])
        self.assertEqual(new['decoded_uint64'],old['original_uint64'])
        self.assertEqual(new['hilo_le_sha256'],old['hilo_le_sha256'])
        self.assertFalse(new['old_RN_add_graph_equivalence_proved'])
        DATA['retained_negative_zero']={'old':old,'new':new,'point_original_bitwise_restored':True,
                                        'old_failure_preserved':True,'phase_at_origin':None,'status':'POINT_ONLY_BOX_STOP'}
    def test_3_atomic_batch_and_optin(self):
        req=m.make_synthetic_request();bad=[]
        def stop(label,fn):
            q=deepcopy(req);fn(q)
            with patch.object(m,'decode_scalar') as mock:
                with self.assertRaises((ValueError,TypeError)):m.audit_decoder_CPU(q,model=m.MODEL)
                self.assertEqual(mock.call_count,0)
            bad.append(label)
        stop('last SOURCE high bool',lambda q:q['SOURCE_limb_records'][-1]['scalars'][-1].update(high_uint32=True))
        stop('last SOURCE low changed',lambda q:q['SOURCE_limb_records'][-1]['scalars'][-1].update(low_uint32=1))
        stop('last SOURCE bytes',lambda q:q['SOURCE_limb_records'][-1].update(hilo_le_sha256='0'*64))
        stop('last SOURCE ORIGINAL zero sign',lambda q:q['SOURCE_limb_records'][-1]['scalars'][-1].update(original_uint64=1<<63))
        stop('last SOURCE stale scope flag',lambda q:q['SOURCE_limb_records'][-1].update(frozen_guard_admission_for_entire_box_proved=True))
        stop('scene context changed',lambda q:q['SCENE_INPUT']['cases'][q['SOURCE_limb_records'][-1]['case_name']]['context'].update(extra=True))
        stop('order changed',lambda q:q['SOURCE_limb_records'].reverse())
        stop('missing SOURCE',lambda q:q['SOURCE_limb_records'].pop())
        stop('old model alias',lambda q:q.update(model='axial-retained-synthetic-scene-SOURCE-hilo-point-encoder-CPU-v1'))
        stop('scope changed',lambda q:q.update(scope='equivalent frozen RN sum'))
        stop('encoder SHA changed',lambda q:q.update(encoder_receipt_sha256='0'*64))
        stop('extra authority',lambda q:q.update(admitted=True))
        with self.assertRaises(ValueError):m.audit_decoder_CPU(None,model=True)
        DATA['batch_rejections']=bad;DATA['model_rejections']=['bool']
    def test_4_inputs_and_failclosed_RN(self):
        labels=[]
        for index in (0,1):
            for word in (True,-1,1<<32,1,0x7f800000,0x7fc00000,-0.0,'0',None):
                limbs=[0x3f800000,0];limbs[index]=word
                with patch.object(m,'native_add64') as mock:
                    with self.assertRaises(ValueError):m.decode_scalar(*limbs)
                    self.assertEqual(mock.call_count,0)
                labels.append([index,str(word)])
        failures=[]
        for wrong in (0x3ff0000000000001,1,0x7ff0000000000000,True):
            with patch.object(m,'native_add64',return_value=wrong) as mock:
                with self.assertRaises(ValueError):m.decode_scalar(0x3f800000,74<<23)
                self.assertEqual(mock.call_count,1)
            failures.append(str(wrong))
        DATA['primitive_rejections']=labels;DATA['mock_output_rejections']=failures
if __name__=='__main__':
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'data':DATA},sort_keys=True,allow_nan=False))
    sys.exit(not result.wasSuccessful())
