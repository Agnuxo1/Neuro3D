"""Own point SOURCE bounds from sealed transport; no native producer imports."""
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('own_point_bound',ROOT/'Blender/benchmarks/capacity_audit/axial_tagged_SOURCE_ORIGINAL_point_bound_HOST_v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sealed=m.load_retained()
        cls.patcher=patch.object(m,'load_retained',return_value=cls.sealed);cls.patcher.start()
    @classmethod
    def tearDownClass(cls):cls.patcher.stop()
    def test_1_tagged_point_and_missing(self):
        req=m.make_synthetic_request();a=m.audit_POINT_HOST(req,model=m.MODEL)
        self.assertEqual(a['point_bound_calls'],4);self.assertEqual(a['native_RN_nodes'],0)
        self.assertTrue(all(r['proof']['point_relative_L1_bound'] is not None and
                            r['proof']['point_principal_phase_bound_rad'] is not None for r in a['sources']))
        self.assertEqual([r['retained_whole_box_guard_admission_disproved'] for r in a['sources']],[True,True,None,None])
        self.assertTrue(all(v is False for v in a['proof_scope'].values()))
        with patch.object(m,'bound_POINT') as mock:missing=m.audit_POINT_HOST(None,model=m.MODEL);self.assertEqual(mock.call_count,0)
        self.assertEqual((missing['missing_cases'],missing['missing_sources']),(17,19))
        DATA.update(request=req,audit=a,missing=missing)
    def test_2_new_reference_zero_controls(self):
        one=0x3ff0000000000000;negzero=1<<63;tiny=1<<52
        controls=[]
        def add(label,a,b,eps,signs,relative,phase):
            out=m.bound_POINT(a,b,m.pair(eps))
            self.assertIs(out['ORIGINAL_zero_components_and_signs_preserved'],signs)
            self.assertEqual(out['point_relative_L1_bound'] is not None,relative)
            self.assertEqual(out['point_principal_phase_bound_rad'] is not None,phase)
            controls.append({'label':label,'proof':out})
        add('nonzero absolute relative principal phase',[one,0],[one+1,0],F(2)**-52,True,True,True)
        add('origin +0 no relative or phase',[0,0],[0,0],F(0),True,False,False)
        add('origin restored -0 still no relative or phase',[negzero,0],[negzero,0],F(0),True,False,False)
        add('zero sign lost even epsilon0',[negzero,one],[0,one],F(0),False,True,False)
        add('same sign but zero became nonzero is not preserved',[0,one],[tiny,one],F(2)**-1022,False,True,False)
        add('disk touches origin',[one,0],[one,0],F(1),True,True,False)
        add('disk crosses origin',[one,0],[one,0],F(2),True,True,False)
        add('principal crossing cut not unwrapped',[one|(1<<63),tiny],[one|(1<<63),tiny|(1<<63)],
            2*F(2)**-1022,True,True,True)
        DATA['new_POINT_controls']=controls
    def test_3_atomic_wire_reference_and_output(self):
        req=m.make_synthetic_request();bad=[]
        def stop(label,edit):
            q=deepcopy(req);edit(q)
            with patch.object(m,'bound_POINT') as mock:
                with self.assertRaises(ValueError):m.audit_POINT_HOST(q,model=m.MODEL)
                self.assertEqual(mock.call_count,0)
            bad.append(label)
        stop('last SOURCE decoded ORIGINAL word alias',lambda q:q['transport_OUTPUT']['sources'][-1]['decoded_SOURCE_uint64'].__setitem__(1,True))
        stop('last SOURCE scalar decoded changed',lambda q:q['transport_OUTPUT']['sources'][-1]['decoded_scalars'][-1].update(decoded_uint64=1<<63))
        stop('last SOURCE frame digest stale',lambda q:q['transport_OUTPUT']['sources'][-1].update(frame_sha256='0'*64))
        stop('last SOURCE error laundering',lambda q:q['transport_OUTPUT']['sources'][-1]['decoded_scalars'][0].update(decode_error_abs=[1,1]))
        stop('last original zero changed',lambda q:q['transport_INPUT']['decoder_INPUT']['SOURCE_limb_records'][-1]['scalars'][-1].update(original_uint64=1<<63))
        stop('last frame modified',lambda q:q['transport_INPUT']['frames'][-1].update(frame_base64='AAAA'))
        stop('decoder selection changed',lambda q:q['transport_INPUT']['program_INPUT']['decoder_selection'].update(model='legacy'))
        stop('scope full reflected SOURCE alias',lambda q:q.update(reference_scope='fixed-ORIGINAL-A-exp-i-theta-times-ideal-minus-one'))
        stop('UNIT scope alias',lambda q:q.update(reference_scope='UNIT-principal-phase'))
        stop('domain variable SOURCE alias',lambda q:q.update(reference_scope='variable-domain-ORIGINAL-A'))
        stop('legacy phase INPUT quota inserted',lambda q:q.update(phase_INPUT={'cap_rad':[1,1]}))
        stop('new default quota inserted',lambda q:q.update(cap_rad=[0,1]))
        stop('OUTPUT reordered',lambda q:q['transport_OUTPUT']['sources'].reverse())
        stop('SOURCE omitted',lambda q:q['transport_INPUT']['frames'].pop())
        stop('receipt SHA stale',lambda q:q.update(transport_receipt_sha256='0'*64))
        stop('broad promotion',lambda q:q['transport_OUTPUT'].update(actual_scene_authenticated=True))
        DATA['batch_rejections']=bad
    def test_4_types_and_radius_coverage(self):
        one=0x3ff0000000000000;checks=[]
        for w in (True,-1,1<<64,1,0x7ff0000000000000,0x7ff8000000000000,0.0,'0'):
            with self.assertRaises(ValueError):m.bound_POINT([w,one],[0,one],[0,1])
            checks.append('typed selected word')
        for radius in ([True,1],[1,True],[0,0],[0,2],[-1,1],[0.0,1],[1<<4096,1],None):
            with self.assertRaises(ValueError):m.bound_POINT([one,0],[one,0],radius)
            checks.append('typed canonical bounded radius')
        with self.assertRaises(ValueError):m.bound_POINT([one,0],[one+1,0],[0,1])
        checks.append('radius undercovers observed ORIGINAL error')
        with self.assertRaises(ValueError):m.audit_POINT_HOST(None,model=True)
        DATA['typed_rejections']=checks;DATA['model_rejections']=['bool']
if __name__=='__main__':
    r=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests_run':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'data':DATA},sort_keys=True,allow_nan=False))
    sys.exit(not r.wasSuccessful())
