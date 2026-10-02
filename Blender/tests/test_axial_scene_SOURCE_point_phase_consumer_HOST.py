"""Point-bound consumer tests only; no frozen encoders or floating RN calls."""
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('own_point_phase',ROOT/'Blender/benchmarks/capacity_audit/axial_scene_SOURCE_point_phase_consumer_HOST_v1.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
DATA={};ONE=0x3ff0000000000000;NINE_EIGHTHS=0x3ff2000000000000
class PhaseTests(unittest.TestCase):
    def test_01_bound_and_missing(self):
        req=c.make_synthetic_request();a=c.audit_point_phase_HOST(req,model=c.MODEL)
        with patch.object(c,'bound_POINT_phase',side_effect=AssertionError('missing must not bound')) as mocked:
            m=c.audit_point_phase_HOST(None,model=c.MODEL);self.assertEqual(mocked.call_count,0)
        self.assertTrue(a[c.FLAG]);self.assertEqual((a['point_phase_computations'],a['point_phase_enclosed_count'],a['inherited_pins_verified']),(4,4,513))
        self.assertFalse(m[c.FLAG]);self.assertEqual((m['missing_cases'],m['missing_sources'],m['point_phase_computations']),(17,19,0))
        for out in (a,m):
            self.assertEqual(out['group_admissions'],0);self.assertIsNone(out['uniform_phase_bound_rad']);self.assertIsNone(out['phase_quota_fits'])
            self.assertEqual(len(out['proof_scope']),38);self.assertTrue(all(v is False for v in out['proof_scope'].values()))
        self.assertEqual(sum(x['retained_whole_box_guard_admission_disproved'] is True for x in a['sources']),2)
        DATA.update(request=req,audit=a,missing=m)
    def test_02_new_rational_controls(self):
        args=[('exact_axis',[ONE,0],[ONE,0],[0,1],True),
              ('nonzero_complex_disk',[ONE,ONE],[NINE_EIGHTHS,ONE],[1,8],True),
              ('origin',[0,0],[0,0],[0,1],True),
              ('touch_margin',[ONE,0],[ONE,0],[1,1],True),
              ('retained_negative_zero',[ONE,1<<63],[ONE,0],[0,1],False)]
        rows=[]
        for name,a,b,eps,zs in args:
            proof=c.bound_POINT_phase(a,b,eps,original_zero_signs_preserved=zs);rows.append({'name':name,'proof':proof})
        self.assertEqual(rows[0]['proof']['point_principal_phase_bound_rad'],[0,1])
        self.assertEqual(rows[1]['proof']['point_principal_phase_bound_rad'],[1,7])
        for row in rows[2:]:self.assertFalse(row['proof']['point_phase_enclosed']);self.assertIsNone(row['proof']['point_principal_phase_bound_rad'])
        self.assertEqual(rows[-1]['proof']['measured_point_error_L1'],[0,1])
        DATA['rational_controls']=rows
    def test_03_batch_before_any_bound(self):
        req=c.make_synthetic_request();last=req['SCENE_INPUT']['case_order'][-1]
        mutations=[
            ('input_cap',lambda r:r['SCENE_INPUT']['cases'][last]['context'].__setitem__('phase_cap',123)),
            ('original_word',lambda r:r['SOURCE_point_records'][-1]['scalars'][-1].__setitem__('original_uint64',1<<63)),
            ('point_error',lambda r:r['SOURCE_point_records'][-1]['scalars'][0].__setitem__('point_error_bound_abs',[0,1])),
            ('zero_flag',lambda r:r['SOURCE_point_records'][-1]['scalars'][-1].__setitem__('ORIGINAL_zero_sign_preserved',0)),
            ('record_order',lambda r:r['SOURCE_point_records'].reverse()),
            ('missing_record',lambda r:r['SOURCE_point_records'].pop()),
            ('fitted_cap',lambda r:r.__setitem__('phase_cap_fitted',[1,10**9])),
            ('wrong_parent',lambda r:r.__setitem__('encoder_receipt_sha256','0'*64))]
        badrows=[]
        for name,mutate in mutations:
            bad=deepcopy(req);mutate(bad)
            with patch.object(c,'bound_POINT_phase',side_effect=AssertionError('ALL before ANY phase')) as mocked:
                with self.assertRaises(ValueError) as caught:c.audit_point_phase_HOST(bad,model=c.MODEL)
                self.assertEqual(mocked.call_count,0)
            badrows.append({'name':name,'request':bad,'reason':str(caught.exception),'bound_calls':0})
        DATA['batch_stops']=badrows
    def test_04_typed_radii_and_optin(self):
        bads=[('bool_rational',[ONE,0],[ONE,0],[False,1],True),
              ('noncanonical',[ONE,0],[ONE,0],[0,2],True),
              ('denominator_zero',[ONE,0],[ONE,0],[1,0],True),
              ('negative_radius',[ONE,0],[ONE,0],[-1,8],True),
              ('radius_does_not_enclose',[ONE,0],[NINE_EIGHTHS,0],[0,1],True),
              ('lying_zero_sign',[ONE,1<<63],[ONE,0],[0,1],True),
              ('bool_word',[True,0],[0,0],[0,1],True),
              ('bool_sign_gate',[ONE,0],[ONE,0],[0,1],1)]
        rows=[]
        for name,a,b,eps,zs in bads:
            with self.assertRaises(ValueError) as caught:c.bound_POINT_phase(a,b,eps,original_zero_signs_preserved=zs)
            rows.append({'name':name,'original_words':a,'decoded_words':b,'error_L1':eps,'sign_gate':zs,'reason':str(caught.exception)})
        opts=[]
        for model in (None,True,c.MODEL+'-implicit'):
            with patch.object(c,'load_retained',side_effect=AssertionError('optin before INPUT')) as mocked:
                with self.assertRaises(ValueError) as caught:c.audit_point_phase_HOST(None,model=model)
                self.assertEqual(mocked.call_count,0)
            opts.append({'model':model,'reason':str(caught.exception),'loader_calls':0})
        DATA.update(type_stops=rows,optin_stops=opts)
if __name__=='__main__':
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseTests))
    print(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'data':DATA},sort_keys=True,allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
